import subprocess
import sys
import time
import hmac
import hashlib
import json
import logging
import requests
from . import secrets, env
from .chat import Chat


# set default logging level to INFO and output to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def validate_request(event, slack_signing_key):
    slack_headers = event.get("headers")
    slack_body = event.get("body")
    timestamp = int(slack_headers.get("X-Slack-Request-Timestamp"))
    provided_signature = slack_headers.get("X-Slack-Signature")
    if abs(time.time() - timestamp) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return False
    sig_basestring = f"v0:{timestamp}:{slack_body}"
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


def lambda_handler(event, context):
    logging.info(f"Received event:\n{event}\nWith context:\n{context}")
    if not validate_request(event, secrets.slack_signing_key):
        logging.warn("Validation failed")
        return
    slack_body = event.get("body")
    slack_body_obj = json.loads(slack_body)
    request_type = slack_body_obj.get("type")
    if request_type == "url_verification":
        logging.info("Url verification requested")
        # slack wants to validate this app
        challenge_answer = slack_body_obj.get("challenge")
        return {"statusCode": 200, "body": challenge_answer}
    elif request_type == "event_callback":
        slack_event = slack_body_obj.get("event", {})
        if slack_event.get("type") == "app_mention":
            message = slack_event.get("text")
            channel = slack_event.get("channel")
            print(f"got a message: {message}")
            # per-channel chat contexts
            chat = Chat(channel, secrets.openai_api_key)
            response = chat.message(message)
            print(f"got a response: {response}")
            requests.post(
                url="https://slack.com/api/chat.postMessage",
                data={
                    "token": secrets.slack_bot_token,
                    "channel": channel,
                    "text": response,
                },
            )

    return {"statusCode": 200, "body": "Event type unrecognized"}
