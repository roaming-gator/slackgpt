from . import slack
import logging
from aws_xray_sdk.core import patch_all

patch_all()


# this lambda function consumes slack events that come in through api gateway
def event_consumer(event, context):
    logging.info(f"Received event:\n{event}\nWith context:\n{context}")
    headers = event["headers"]
    body = event["body"]
    logging.info(f"headers: {headers}")
    if slack.validate_request(headers, body):
        logging.info("Validation succeeded")
        result = slack.process_payload(body)
        logging.info("Sending %s" % ({
            "statusCode": result.status_code,
            "body": result.message
        }))
        return {
            "statusCode": result.status_code,
            "body": result.message
        }
    logging.info("Sending %s" % ({
        "statusCode": 403,
        "body": "You are not authorized to access this resource"
    }))
    return {
        "statusCode": 403,
        "body": "You are not authorized to access this resource"
    }


# this lambda function processes jobs from the worker queue
def job_worker(event, context):
    logging.info(f"Received event:\n{event}\nWith context:\n{context}")
    result = slack.process_payload_sync(event)
    return {
        "statusCode": result.status_code,
        "body": result.message
    }
