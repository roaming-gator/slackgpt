import logging
import json
import boto3
import dataclasses
from . import env, slack
from .chat import Chat


@dataclasses.dataclass
class QueueItem:
    # this gets pushed on the sqs worker queue
    channel: str
    text: str

    @classmethod
    def from_json(cls, json_string):
        return cls(**json.loads(json_string))

    def to_json(self):
        return json.dumps(dataclasses.asdict(self))


def push_queue(queue_item):
    queue_message = queue_item.to_json()
    logging.debug(f"Queue message: {queue_message}")
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=env.sqs_queue_url,
        MessageBody=queue_message
    )


def process_records(records):
    # siphoned-off synchronous processing of records from sqs queue
    logging.info(f"Received records from the queue: {records}")
    for record in records:
        logging.info(f"Processing record: {record}")
        queue_message = record['body']
        queue_item = QueueItem.from_json(queue_message)
        channel = queue_item.channel
        query = queue_item.text
        # per-channel chat contexts
        chat = Chat(channel)
        response = chat.send_message(query)
        logging.info(f"got a response: {response}")
        slack.post_message(channel, response)
