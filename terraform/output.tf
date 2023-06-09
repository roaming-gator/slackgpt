output "api_gateway_url" {
  value = "${aws_api_gateway_stage.this.invoke_url}/${var.api_gateway_resource_path}"
}

output "slack_app_manifest" {
  value = jsonencode({
    display_information = {
      name = var.slack_bot_display_name
    },
    oauth_config = {
      scopes = {
        bot = [
          "app_mentions:read",
          "chat:write"
        ]
      }
    },
    features = {
      bot_user = {
        display_name  = var.slack_bot_display_name
        always_online = true
      }
    },
    settings = {
      event_subscriptions = {
        request_url = "${aws_api_gateway_stage.this.invoke_url}/${var.api_gateway_resource_path}"
        bot_events = [
          "app_mention"
        ]
      },
      org_deploy_enabled     = false,
      socket_mode_enabled    = false,
      token_rotation_enabled = false
    }
  })
}
