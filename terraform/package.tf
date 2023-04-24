resource "local_file" "kick" {
  content  = local.package_source_hash
  filename = "${local.python_package_dir}/.kick"
}

resource "null_resource" "python_scripts_setup" {
  depends_on = [
    local_file.kick
  ]
  # trigger whenever any file changes in the lambda directory
  triggers = {
    redeployment = local.package_source_hash
  }
  provisioner "local-exec" {
    command     = <<EOT
      set -e
      FOLDER_PATH="${path.module}/../lambda/"
      TEMP_DIR="${local.python_package_dir}"
      echo "Temporary directory created: $TEMP_DIR"
      
      # Copy Python scripts to the temporary directory
      cp -R $FOLDER_PATH/* $TEMP_DIR/
      echo "Python scripts copied to $TEMP_DIR"

      # Check if 'requirements.txt' exists in the folder
      if [ -f "$TEMP_DIR/requirements.txt" ]; then
        # Install package dependencies to the temporary directory
        pip install -r $TEMP_DIR/requirements.txt --target $TEMP_DIR
        echo "Dependencies installed in $TEMP_DIR"
      else
        echo "No requirements.txt file found, skipping dependencies installation"
      fi
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

data "archive_file" "python_lambda_package" {
  depends_on = [
    null_resource.python_scripts_setup,
    local_file.kick
  ]
  excludes = [
    "__pycache__",
    "core/__pycache__",
    "tests"
  ]
  type = "zip"
  # package the app directory
  source_dir  = local.python_package_dir
  output_path = local.package_file_name
}
