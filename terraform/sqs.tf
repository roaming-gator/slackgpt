# queue allows us to send the processing job to the background from the first lambda function and return 
# a response to slack immediately

resource "aws_sqs_queue" "this" {
  name_prefix                = var.sqs_queue_name
  visibility_timeout_seconds = var.execution_timeout
}
