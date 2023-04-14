resource "aws_dynamodb_table" "this" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "chatid"

  attribute {
    name = "chatid"
    type = "S"
  }
}

resource "aws_secretsmanager_secret" "this" {
  name = var.secret_mgr_path
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id
  # these secrets need to be set manually after the stack is deployed
  secret_string = <<EOF
    {
        "openai_api_key": ""
        "slack_signing_key": ""
        "slack_bot_token": ""
    }
  EOF 
}

resource "aws_iam_role" "lambda_execution" {
  name = var.lambda_execution_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_execution_policy" {
  role   = aws_iam_role.lambda_execution.id
  policy = data.aws_iam_policy_document.lambda_policy_document.json
}

data "aws_iam_policy_document" "lambda_policy_document" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [aws_dynamodb_table.this.arn]
  }

  statement {
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [aws_secretsmanager_secret.this.arn]
  }
}

resource "aws_lambda_function" "this" {

  function_name    = var.lambda_function_name
  filename         = "package.zip"
  source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
  role             = aws_iam_role.lambda_execution.arn
  runtime          = "python3.9"
  handler          = "lambda.main.lambda_handler"
  timeout          = 60
  # enable enhanced monitoring
  # https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html#monitoring-metrics-enhanced
  # enable tracing


  environment {
    variables = {
      DYNAMODB_TABLE_NAME        = aws_dynamodb_table.this.name
      SECRETS_MANAGER_SECRET_ARN = aws_secretsmanager_secret.this.arn
    }
  }
}

resource "aws_api_gateway_rest_api" "this" {
  name        = var.api_gateway_name
  description = "Slack GPT API Gateway"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "slackgpt"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.this.invoke_arn
}

resource "aws_api_gateway_deployment" "this" {
  depends_on = [aws_api_gateway_integration.lambda]

  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = var.environment
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}

output "api_gateway_url" {
  value = "https://${aws_api_gateway_rest_api.this.id}.execute-api.${var.region}.amazonaws.com/${var.environment}/slackgpt"
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.this.name
}

output "secrets_manager_secret_arn" {
  value = aws_secretsmanager_secret.this.arn
}
