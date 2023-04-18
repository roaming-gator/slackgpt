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
  default     = "gpt-3.5-turbo"
}

variable "openai_api_key" {
  description = "Openai api key"
  sensitive   = true
}

variable "slack_signing_key" {
  description = "Slack signing key"
  sensitive   = true
}

variable "slack_bot_token" {
  description = "Slack bot token"
  sensitive   = true
}

variable "slack_bot_display_name" {
  description = "Slack bot display name"
  default     = "slackgpt"
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
  description = "Max amount of seconds that the lambda function can run before its terminated"
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

variable "api_gateway_stage_name" {
  description = "Name of the api gateway stage"
  default     = "main"
}

variable "api_gateway_resource_path" {
  description = "Last part of the api gateway endpoint path"
  default     = "slackgpt"
}
