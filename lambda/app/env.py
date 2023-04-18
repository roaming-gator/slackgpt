import os


@property
def dynamodb_table_name():
    return os.environ['DYNAMODB_TABLE_NAME']


@property
def secrets_manager_secret_id():
    return os.environ['SECRETS_MANAGER_SECRET_ID']


@property
def openai_api_key_secret_name():
    return os.environ['OPENAI_API_KEY_SECRET_NAME']


@property
def slack_signing_key_secret_name():
    return os.environ['SLACK_SIGNING_KEY_SECRET_NAME']


@property
def slack_bot_token_secret_name():
    return os.environ['SLACK_BOT_TOKEN_SECRET_NAME']


@property
def openai_default_chat_model():
    return os.environ['OPENAI_DEFAULT_CHAT_MODEL']
