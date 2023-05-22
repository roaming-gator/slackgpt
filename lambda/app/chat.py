import boto3
import openai
import tiktoken
import logging
from time import sleep
from . import env, secrets

# set the api key
openai.api_key = secrets.openai_api_key


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    # from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logging.warning("model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        logging.warning(
            "gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        logging.warning(
            "gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_message = 4
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


class Chat:
    def __init__(self, chatid, model=env.openai_default_chat_model):
        self.model = model
        dynamodb = boto3.resource("dynamodb")
        self.state_table = dynamodb.Table(env.dynamodb_table_name)
        self.chatid = chatid

    @property
    def messages(self):
        # Get item from DynamoDB table
        response = self.state_table.get_item(Key={"chatid": self.chatid})
        return response.get("Item", {}).get("messages", [])

    def pop_message(self):
        # remove the first message from the history (fifo)
        self.state_table.update_item(
            Key={"chatid": self.chatid},
            UpdateExpression="REMOVE messages[0]",
            ConditionExpression="size(messages) > :zero",
            ExpressionAttributeValues={
                ":zero": 0,
            },
        )

    def push_messages(self, messages):
        # append messages to the end of the history
        self.state_table.update_item(
            Key={"chatid": self.chatid},
            UpdateExpression="SET messages = list_append(if_not_exists(messages, :empty_list), :messages)",
            ExpressionAttributeValues={
                ":messages": messages,
                ":empty_list": [],
            },
        )

    def prune_history(self, new_message):
        # remove messages from chat history until the number of tokens is less than the max
        # chat history specified, or until the new message is the only one left.
        max_tokens = env.chat_history_max_tokens
        logging.info(f"Pruning messages (max tokens: {max_tokens})")
        while (
            len(messages := self.messages) > 0
            and (token_count := num_tokens_from_messages(messages + [new_message],
                                                         model=self.model)) > max_tokens
        ):
            logging.info(
                f"Removing message (token count: {token_count}, max tokens: {max_tokens})")
            self.pop_message()
        logging.info("Remaining messages in history: {}".format(
            len(self.messages)))

    def send_message(self, content):
        # send a message to chatgpt, with previous chat history, and wait for a response
        user_message = {"role": "system", "content": content}
        self.prune_history(user_message)
        try:
            chat = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages + [user_message])
            response = chat["choices"][0]["message"]["content"]
            response_message = {"role": "assistant", "content": response}
            new_messages = [user_message, response_message]
            self.push_messages(new_messages)
        except openai.error.InvalidRequestError as e:
            if "reduce the length of the messages" in e.message:
                # chat is too long and the prune_history() function failed to prune enough messages
                response = "Error: User input is too long. Please try again."
            else:
                response = f"Unhandled openai exception: {e.message}"
        except Exception as e:
            response = "Could not generate response. Please try again later."
        return response
