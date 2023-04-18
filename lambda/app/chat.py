import boto3
import openai
from . import env, secrets

# set the api key
openai.api_key = secrets.openai_api_key


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

    @messages.setter
    def messages(self, value):
        # Update item in DynamoDB table
        self.state_table.update_item(
            Key={"chatid": self.chatid},
            AttributeUpdates={
                "messages": {"Value": value},
            },
        )

    def send_message(self, content):
        messages = self.messages
        messages.append({"role": "system", "content": content})
        chat = openai.ChatCompletion.create(
            model=self.model,
            messages=messages)
        response = chat["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": response})
        self.messages = messages
        return response
