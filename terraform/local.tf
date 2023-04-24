locals {
  # Openai api key secret name in AWS secret manager
  openai_api_key_secret_name = "openai_api_key"
  # Slack signing key secret name in AWS secret manager
  slack_signing_key_secret_name = "slack_signing_key"
  # Slack bot token secret name in AWS secret manager
  slack_bot_token_secret_name = "slack_bot_token"
  # temporary python package directory
  python_package_dir = "${path.module}/.terraform/tmp/package"
  # lambda package filename dependent on source code hash
  package_source_hash = sha1(jsonencode({
    for f in fileset("${path.module}/../lambda/", "**") :
    f => filesha1("${path.module}/../lambda/${f}")
  }))
  # lambda package filename
  package_file_name = "${local.package_source_hash}.zip"
}
