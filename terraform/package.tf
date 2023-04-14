# preprocess and package the lambda function

resource "local_file" "envvars" {
  # fill out the environment file with terraform variables
  content = templatefile("${path.module}/../app/lambda/.env.tftpl", {
    DYNAMODB_TABLE_NAME        = var.dynamodb_table_name,
    SECRETS_MANAGER_SECRET_ARN = var.secret_mgr_path,
    REGION                     = var.region
  })
  filename = "${path.module}/../app/lambda/.env"
}

data "archive_file" "python_lambda_package" {
  type = "zip"
  # package the app directory
  source_dir  = "${path.module}/../app/"
  output_path = "package.zip"
  depends_on = [
    local_file.envvars
  ]
}
