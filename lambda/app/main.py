from . import slack, worker
import logging
from aws_xray_sdk.core import patch_all
import logging

logging.getLogger().setLevel(logging.INFO)

# instrument the code using aws xray for tracing
patch_all()


def event_consumer(event, context):
    # this lambda function consumes slack events that come in through api gateway
    logging.info(f"Received event:\n{event}\nWith context:\n{context}")
    return slack.lambda_request_handler.handle(event, context)


def job_worker(event, context):
    # this lambda function processes jobs from the worker queue
    logging.info(f"Received event:\n{event}\nWith context:\n{context}")
    records = event['Records']
    result = worker.process_records(records)
    return {
        "statusCode": result.status_code,
        "body": result.message
    }
