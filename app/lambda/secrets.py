import boto3
import os
import json
from dotenv import load_dotenv

secret_name = os.environ["SECRETS_MANAGER_SECRET_ARN"]
region_name = os.environ["REGION"]

client = boto3.client("secretsmanager", region_name=region_name)
get_secret_value_response = client.get_secret_value(SecretId=secret_name)
# Decrypts secret using the associated KMS key.
secrets = json.loads(get_secret_value_response["SecretString"])


@property
def openai_api_key():
    return secrets["openai_api_key"]


@property
def slack_signing_key():
    return secrets["slack_signing_key"]


@property
def slack_bot_token():
    return secrets["slack_bot_token"]
