output "api_gateway_url" {
  value = "${aws_api_gateway_stage.this.invoke_url}/${var.api_gateway_resource_path}"
}
