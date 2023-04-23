resource "null_resource" "python_scripts_setup" {
  # trigger whenever any file changes in the lambda directory
  triggers = {
    hash_of_hashes = sha1(jsonencode({
      for f in fileset("${path.module}/../lambda/", "**") :
      f => filesha1(f)
    }))
  }
  provisioner "local-exec" {
    command     = <<EOT
      set -e
      FOLDER_PATH="${path.module}/../lambda/"
      TEMP_DIR=$(mktemp -d)
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
  type = "zip"
  # package the app directory
  source_dir  = "${path.module}/../lambda/"
  output_path = "package.zip"
}