import hmac
import hashlib
import time
import logging
import json
import requests
import boto3
from . import secrets, env
from .chat import Chat

sqs = boto3.client('sqs')


class PayloadProcessingResult():
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


def validate_request(headers, body):
    # make sure it's slack that's sending us the request
    # https://api.slack.com/authentication/verifying-requests-from-slack
    timestamp = int(headers.get("X-Slack-Request-Timestamp"))
    provided_signature = headers.get("X-Slack-Signature")
    if abs(time.time() - timestamp) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return False
    sig_basestring = f"v0:{timestamp}:{body}"
    slack_signing_key = secrets.slack_signing_key
    h = hmac.new(
        bytes(slack_signing_key, "latin-1"),
        msg=bytes(sig_basestring, "latin-1"),
        digestmod=hashlib.sha256,
    )
    calculated_signature = "v0=" + h.hexdigest()
    logging.debug(
        f"calculated = {calculated_signature}, passed = {provided_signature}")
    if calculated_signature != provided_signature:
        logging.warn("Signatures dont match")
        return False
    return True


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
            sqs.send_message(
                QueueUrl=env.sqs_queue_url,
                MessageBody=queue_message
            )
            return PayloadProcessingResult(200, "Message queued for processing")
    return PayloadProcessingResult(404, "Unrecognized request type")


def find_message_text(blocks):
    for block in blocks:
        if block.get("type") == "text":
            return block.get("text").strip()
        elif elements := block.get("elements")
            return find_message_text(elements)
    # couldnt find any text in these blocks
    return None


# siphoned-off synchronous processing of messages
def process_payload_sync(queue_event):
    logging.info(f"Received a message from the queue: {queue_event}")
    for record in queue_event['Records']:
        logging.info(f"Processing record: {record}")
        body = json.loads(record['body'])
        channel = body.get("channel")
        blocks = body.get("blocks")
        text = find_message_text(blocks)
        logging.info(f"got a message: {text}")
        # per-channel chat contexts
        chat = Chat(channel)
        response = chat.send_message(text)
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
