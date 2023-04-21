import os

dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
secrets_manager_secret_id = os.environ['SECRETS_MANAGER_SECRET_ID']
openai_api_key_secret_name = os.environ['OPENAI_API_KEY_SECRET_NAME']
slack_signing_key_secret_name = os.environ['SLACK_SIGNING_KEY_SECRET_NAME']
slack_bot_token_secret_name = os.environ['SLACK_BOT_TOKEN_SECRET_NAME']
openai_default_chat_model = os.environ['OPENAI_DEFAULT_CHAT_MODEL']
sqs_queue_url = os.environ['SQS_QUEUE_URL']
