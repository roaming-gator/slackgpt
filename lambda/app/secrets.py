import boto3
import json
import env


client = boto3.client("secretsmanager")
get_secret_value_response = client.get_secret_value(
    SecretId=env.secrets_manager_secret_id)
# Decrypts secret using the associated KMS key.
secrets = json.loads(get_secret_value_response["SecretString"])


@property
def openai_api_key():
    return secrets[env.openai_api_key_secret_name]


@property
def slack_signing_key():
    return secrets[env.slack_signing_key_secret_name]


@property
def slack_bot_token():
    return secrets[env.slack_bot_token_secret_name]
