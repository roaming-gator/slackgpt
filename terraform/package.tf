resource "local_file" "kick" {
  # ensure the dynamically-generated temporary directory exists
  content  = local.package_source_hash
  filename = "${local.python_package_dir}/.kick"
}

resource "null_resource" "python_scripts_setup" {
  # install dependencies in a temp directory
  depends_on = [
    local_file.kick
  ]
  triggers = {
    redeployment = local.package_source_hash
  }
  lifecycle {
    replace_triggered_by = [
      # repackage these files whenever the local_file creates the temporary working directory.
      # this is a workaround for terraform cloud not allowing persistent file storage on the local_file kick resource.
      local_file.kick.id
    ]
  }
  provisioner "local-exec" {
    command     = <<EOT
      set -e
      FOLDER_PATH="${path.module}/../lambda/"
      TEMP_DIR="${local.python_package_dir}"
      mkdir -p "$TEMP_DIR"
      echo "Temporary directory created: $TEMP_DIR"
      
      # Copy Python scripts to the temporary directory
      cp -R $FOLDER_PATH/* $TEMP_DIR/
      echo "Python scripts copied to $TEMP_DIR"

      # Check if 'requirements.txt' exists in the folder
      if [ -f "$TEMP_DIR/requirements.txt" ]; then
        pip install --upgrade pip
        # Install package dependencies to the temporary directory
        pip install -r "$TEMP_DIR/requirements.txt" \
          --target "$TEMP_DIR" \
          --implementation cp \
          --only-binary=:all: \
          --platform manylinux2014_x86_64 \
          --upgrade \
          --python-version ${local.lambda_runtime_version}
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
