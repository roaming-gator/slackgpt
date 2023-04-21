locals {
  lambda_environment = {
    DYNAMODB_TABLE_NAME           = aws_dynamodb_table.this.name
    SECRETS_MANAGER_SECRET_ID     = aws_secretsmanager_secret.this.arn
    OPENAI_API_KEY_SECRET_NAME    = local.openai_api_key_secret_name
    SLACK_SIGNING_KEY_SECRET_NAME = local.slack_signing_key_secret_name
    SLACK_BOT_TOKEN_SECRET_NAME   = local.slack_bot_token_secret_name
    OPENAI_DEFAULT_CHAT_MODEL     = var.openai_default_chat_model
    SQS_QUEUE_URL                 = aws_sqs_queue.this.id
  }
}

resource "aws_lambda_function" "event_consumer" {
  function_name    = var.event_consumer_lambda_function_name
  filename         = "package.zip"
  source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
  role             = aws_iam_role.lambda_execution.arn
  runtime          = "python3.9"
  handler          = "app.main.event_consumer"
  timeout          = 60
  depends_on = [
    data.archive_file.python_lambda_package
  ]

  environment {
    variables = local.lambda_environment
  }
}

resource "aws_lambda_function" "job_worker" {
  function_name    = var.job_worker_lambda_function_name
  filename         = "package.zip"
  source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
  role             = aws_iam_role.lambda_execution.arn
  runtime          = "python3.9"
  handler          = "app.main.job_worker"
  timeout          = 60
  depends_on = [
    data.archive_file.python_lambda_package
  ]

  environment {
    variables = local.lambda_environment
  }
}

# connect the job worker to the queue
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.this.arn
  function_name    = aws_lambda_function.job_worker.arn
  batch_size       = 1
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.event_consumer.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}

data "archive_file" "python_lambda_package" {
  type = "zip"
  # package the app directory
  source_dir  = "${path.module}/../lambda/"
  output_path = "package.zip"
}
