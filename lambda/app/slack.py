import hmac
import hashlib
import time
import logging
import json
import requests
from . import secrets
from .chat import Chat


class RequestResult():
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


def process_request(headers, body):
    if not validate_request(headers, body):
        logging.warn("Validation failed")
        return RequestResult(403, "Validation failed")
    body_obj = json.loads(body)
    request_type = body_obj.get("type")
    if request_type == "url_verification":
        logging.info("Url verification requested")
        # slack wants to validate this app
        challenge_answer = body_obj.get("challenge")
        return RequestResult(200, challenge_answer)
    elif request_type == "event_callback":
        event = body_obj.get("event", {})
        if event.get("type") == "app_mention":
            message = event.get("text")
            channel = event.get("channel")
            print(f"got a message: {message}")
            # per-channel chat contexts
            chat = Chat(channel)
            response = chat.send_message(message)
            print(f"got a response: {response}")
            requests.post(
                url="https://slack.com/api/chat.postMessage",
                data={
                    "token": secrets.slack_bot_token,
                    "channel": channel,
                    "text": response,
                },
            )
            return RequestResult(200, "Message sent")

    return RequestResult(404, "Unrecognized request type")
