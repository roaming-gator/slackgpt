locals {
  # Openai api key secret name in AWS secret manager
  openai_api_key_secret_name = "openai_api_key"
  # Slack signing key secret name in AWS secret manager
  slack_signing_key_secret_name = "slack_signing_key"
  # Slack bot token secret name in AWS secret manager
  slack_bot_token_secret_name = "slack_bot_token"
}
