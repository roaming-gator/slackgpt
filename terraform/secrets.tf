
resource "aws_secretsmanager_secret" "this" {
  name = var.secret_mgr_path
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id
  # these secrets need to be set manually after the stack is deployed
  secret_string = <<EOF
    {
        "${var.openai_api_key_secret_name}": "${var.openai_api_key}"
        "${var.slack_signing_key_secret_name}": "${var.slack_signing_key}"
        "${var.slack_bot_token_secret_name}": "${var.slack_bot_token}"
    }
  EOF 
}
