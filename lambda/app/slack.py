from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import logging
import re
from . import secrets, worker


# https://github.com/slackapi/bolt-python/blob/main/examples/aws_lambda/lazy_aws_lambda.py
app = App(token=secrets.slack_bot_token,
          signing_secret=secrets.slack_signing_key,
          process_before_response=True)
lambda_request_handler = SlackRequestHandler(app=app)


@app.middleware
def log_request(_, body, next):
    logging.debug(body)
    return next()


@app.event("app_mention")
def handle_app_mention(body, say, _):
    logging.info(f"Received an app mention: {body}")
    channel = body["event"]["channel"]
    original_text = body["event"]["text"]
    query = re.sub("<@.*>", "", original_text).strip()
    logging.info(f'User query is: {query}')
    queue_item = worker.QueueItem(channel, query)
    worker.push_queue(queue_item)


def post_message(channel, response):
    app.client.chat_postMessage(channel=channel, text=response)
