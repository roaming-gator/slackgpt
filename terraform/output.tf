output "api_gateway_url" {
  value = "${aws_api_gateway_stage.this.invoke_url}/${var.api_gateway_resource_path}"
}

output "slack_app_manifest" {
  value = <<-EOF
    display_information:
      name: ${var.slack_bot_display_name}
    features:
      bot_user:
        display_name: ${var.slack_bot_display_name}
        always_online: true
    oauth_config:
      scopes:
        bot:
          - app_mentions:read
          - chat:write
    settings:
      event_subscriptions:
        request_url: "${aws_api_gateway_stage.this.invoke_url}/${var.api_gateway_resource_path}"
        bot_events:
          - app_mention
      org_deploy_enabled: false
      socket_mode_enabled: false
      token_rotation_enabled: false
    EOF
}

output "api_rest_api" {
  value = aws_api_gateway_rest_api.this.body
}
