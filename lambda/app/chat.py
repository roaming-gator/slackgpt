import os
import boto3
import openai
from . import env


class Chat:
    def __init__(self, chatid, api_key, model=env.openai_default_chat_model):
        openai.api_key = api_key
        self.model = model
        dynamodb = boto3.resource("dynamodb")
        self.state_table = dynamodb.Table(env.dynamodb_table_name)
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
        chat = openai.ChatCompletion.create(
            model=self.model, messages=messages)
        response = chat["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": response})
        self.update_messages(messages)
        return response
