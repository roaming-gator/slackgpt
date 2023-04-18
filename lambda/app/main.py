from . import slack
import logging


def lambda_handler(event, context):
    logging.info(f"Received event:\n{event}\nWith context:\n{context}")
    headers = event["headers"]
    body = event["body"]
    logging.info(f"headers: {headers}")
    result = slack.process_request(headers, body)
    return {
        "statusCode": result.status_code,
        "body": result.message
    }
