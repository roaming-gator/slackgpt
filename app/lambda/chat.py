import os
import boto3
import openai
from dotenv import load_dotenv


class Chat:
    def __init__(self, chatid, api_key, model="gpt-3.5-turbo"):
        openai.api_key = api_key
        self.model = model
        dynamodb = boto3.resource("dynamodb")
        self.state_table = dynamodb.Table(os.environ["DYNAMODB_TABLE_NAME"])
        self.chatid = chatid

    def get_messages(self):
        # Get item from DynamoDB table
        response = self.state_table.get_item(Key={"chatid": self.chatid})
        return response.get("Item", {}).get("messages", [])

    def update_messages(self, messages):
        self.state_table.update_item(
            Key={"chatid": self.chatid},
            AttributeUpdates={
                "messages": {"Value": messages},
            },
        )

    def message(self, content):
        messages = self.get_messages()
        messages.append({"role": "system", "content": content})
        chat = openai.ChatCompletion.create(model=self.model, messages=messages)
        response = chat["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": response})
        self.update_messages(messages)
        return response
