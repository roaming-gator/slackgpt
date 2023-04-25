import logging
import json
import boto3
import dataclasses
from . import env
from .chat import Chat
from .slack import post_message as post_slack_message


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


@ dataclasses.dataclass
class PayloadProcessingResult:
    status_code: int
    message: str


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
    try:
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
            post_slack_message(channel, response)
        return PayloadProcessingResult(200, "Message sent")
    except Exception as e:
        logging.error(f"Error processing payload: {e}")
        return PayloadProcessingResult(500, "Error processing payload")
