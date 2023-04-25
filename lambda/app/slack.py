import logging
import json
import requests
import boto3
import re
import dataclasses
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from . import secrets, env
from .chat import Chat


@dataclasses.dataclass
class SlackEvent:
    channel: str
    text: str


@dataclasses.dataclass
class PayloadProcessingResult():
    status_code: int
    message: str


# https://github.com/slackapi/bolt-python/blob/main/examples/aws_lambda/lazy_aws_lambda.py
app = App(token=secrets.slack_bot_token,
          signing_secret=secrets.slack_signing_key,
          process_before_response=True)


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("app_mention")
def handle_app_mention(body, say, logger):


class PayloadProcessingResult():
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


def process_payload(body):
    body_obj = json.loads(body)
    request_type = body_obj.get("type")
    if request_type == "url_verification":
        logging.info("Url verification requested")
        # slack wants to validate this app
        challenge_answer = body_obj.get("challenge")
        return PayloadProcessingResult(200, challenge_answer)
    elif request_type == "event_callback":
        event = body_obj.get("event", {})
        if event.get("type") == "app_mention":
            logging.info("Got an app mention. Sending to sqs for processing")
            queue_message = json.dumps(event)
            sqs = boto3.client('sqs')
            sqs.send_message(
                QueueUrl=env.sqs_queue_url,
                MessageBody=queue_message
            )
            return PayloadProcessingResult(200, "Message queued for processing")
    return PayloadProcessingResult(404, "Unrecognized request type")


# siphoned-off synchronous processing of messages
def process_payload_sync(queue_event):
    logging.info(f"Received a message from the queue: {queue_event}")
    for record in queue_event['Records']:
        logging.info(f"Processing record: {record}")
        body = json.loads(record['body'])
        channel = body.get("channel")
        original_text = body.get("text")
        query = re.sub("<@.*>", "", original_text).strip()
        logging.debug(f"Original query was: {original_text}")
        logging.info(f'User query is: {query}')
        # per-channel chat contexts
        chat = Chat(channel)
        response = chat.send_message(query)
        logging.info(f"got a response: {response}")
        requests.post(
            url="https://slack.com/api/chat.postMessage",
            data={
                "token": secrets.slack_bot_token,
                "channel": channel,
                "text": response,
            },
        )
        return PayloadProcessingResult(200, "Message sent")
    return PayloadProcessingResult(500, "Could not process events")
