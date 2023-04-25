from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from .worker import push_queue as push_worker_queue, QueueItem
from . import secrets


# https://github.com/slackapi/bolt-python/blob/main/examples/aws_lambda/lazy_aws_lambda.py
app = App(token=secrets.slack_bot_token,
          signing_secret=secrets.slack_signing_key,
          process_before_response=True)
lambda_request_handler = SlackRequestHandler(app=app)


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("app_mention")
def handle_app_mention(body, say, logger):
    logger.info(f"Received an app mention: {body}")
    channel = body["event"]["channel"]
    text = body["event"]["text"]
    logger.info(f'User query is: {text}')
    queue_item = QueueItem(channel, text)
    push_worker_queue(queue_item)


def post_message(channel, response):
    app.client.chat_postMessage(channel=channel, text=response)
