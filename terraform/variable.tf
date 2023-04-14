variable "region" {
  description = "The AWS region to deploy resources in."
  default     = "us-east-1"
}

variable "dynamodb_table_name" {
  description = "Table to store app state."
  default     = "slackgpt"
}

variable "secret_mgr_path" {
  description = "Path to store secrets in AWS secret manager"
  default     = "slackgpt-prod"
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

variable "environment" {
  description = "Deployment environment"
  default     = "prod"
}
