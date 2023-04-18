import boto3
import json
from . import env


_client = boto3.client("secretsmanager")
_get_secret_value_response = _client.get_secret_value(
    SecretId=env.secrets_manager_secret_id)
print(_get_secret_value_response)
print(_get_secret_value_response["SecretString"])
_secrets = json.loads(_get_secret_value_response["SecretString"])

# export secret values
openai_api_key = _secrets[env.openai_api_key_secret_name]
slack_signing_key = _secrets[env.slack_signing_key_secret_name]
slack_bot_token = _secrets[env.slack_bot_token_secret_name]
