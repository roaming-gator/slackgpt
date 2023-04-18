variable "dynamodb_table_name" {
  description = "Table to store app state."
  default     = "slackgpt"
}

variable "secret_mgr_path" {
  description = "Path to store secrets in AWS secret manager"
  default     = "slackgpt"
}

variable "openai_default_chat_model" {
  description = "Default chat model to use"
  default     = "davinci"
}

variable "openai_api_key_secret_name" {
  description = "Openai api key secret name in AWS secret manager"
  default     = "openai_api_key"
}

variable "openai_api_key" {
  description = "Openai api key"
  sensitive   = true
}

variable "slack_signing_key_secret_name" {
  description = "Slack signing key secret name in AWS secret manager"
  default     = "slack_signing_key"
}

variable "slack_signing_key" {
  description = "Slack signing key"
  sensitive   = true
}

variable "slack_bot_token_secret_name" {
  description = "Slack bot token secret name in AWS secret manager"
  default     = "slock_bot_token"
}

variable "slack_bot_token" {
  description = "Slack bot token"
  sensitive   = true
}

variable "lambda_function_name" {
  description = "Name of the lambda function that runs our app"
  default     = "slackgpt"
}

variable "lambda_execution_role_name" {
  description = "Name of the iam role that gets created for the lambda function"
  default     = "slackgpt-lambda-role"
}

variable "execution_timeout" {
  description = "Max amount of time that the lambda function can run before its terminated"
  default     = 60
}

variable "api_gateway_name" {
  description = "Name of the api gateway"
  default     = "SlackGPT"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}
