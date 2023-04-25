# SlackGPT

This repository contains the source code for a serverless AI Slack Bot called SlackGPT, which allows users to interact with ChatGPT in their Slack channels. The bot is built using AWS Lambda and Terraform for infrastructure management.

At least half this project (code and README) was written by copilot/GPT.

## Repository Structure

The repository consists of two main directories:

- `terraform`: Contains all Terraform resources needed to deploy the SlackGPT application on AWS.
- `lambda`: Contains the Python application source code for the SlackGPT bot.

## Getting Started

Follow these steps to set up and deploy your SlackGPT bot.

### Prerequisites

1. Install [Terraform](https://www.terraform.io/downloads.html).
2. Install the [AWS CLI](https://aws.amazon.com/cli/) (v2 or higher) and [configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) your AWS credentials, or create a workspace on [Terraform Cloud](https://app.terraform.io/signup/account) which will interact with AWS.
3. Install [Python](https://www.python.org/downloads/) (v3.9 or higher).

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/roaming-gator/slackgpt.git
   cd slackgpt
   ```

2. Create an OpenAI API key that allows interaction with ChatGPT.

### Deploy

1. Navigate to the `terraform` directory:

   ```bash
   cd terraform
   ```

2. Apply the Terraform configuration with blank or dummy values for the two Slack variables:

   ```bash
   terraform apply -var "openai_api_key=<your_openai_api_key>" -var "slack_signing_key=<dummy_value>" -var "slack_bot_token=<dummy_value>"
   ```

   Review the changes and confirm by typing `yes` when prompted.

3. After the deployment is complete, a Slack App Manifest will be generated in the output. Copy the manifest to the Slack App wizard to automatically configure the application, including the AWS API Gateway invocation URL used for Slack events.

4. Retrieve the signing key and bot token from the app configuration webpage.

5. Re-apply the Terraform configuration with the actual Slack signing key and bot token:

   ```bash
   terraform apply -var "openai_api_key=<your_openai_api_key>" -var "slack_signing_key=<your_slack_signing_key>" -var "slack_bot_token=<your_slack_bot_token>"
   ```

   Review the changes and confirm by typing `yes` when prompted.

## Usage

To interact with the SlackGPT bot, simply mention it in a message within a Slack channel. Note that chat history is stored per-channel in a DynamoDB table.

## Technical Details

### Architecture

The SlackGPT application is designed to interact with users in Slack channels using ChatGPT. It is built using AWS Lambda and follows a serverless architecture, which ensures scalability and cost efficiency. The technical summary of how the application works is as follows:

1. **AWS Lambda Functions**: The application consists of two AWS Lambda functions that use the same Python code present in the `lambda` directory of the repository. The code has two different entrypoints, both located in the `main.py` file in the `lambda/app` subfolder.

2. **Event Reception**: The first Lambda function is responsible for receiving events from Slack through AWS API Gateway. When an event is received, this function pushes an item to AWS SQS (Simple Queue Service) and returns immediately.

3. **Event Processing**: The second Lambda function receives items from the SQS queue and processes them. It uses a DynamoDB table to store previous interactions and ChatGPT responses, which helps maintain the state of the conversation.

4. **State Management**: When a new request is received from the SQS queue, the Lambda function looks up the previous chat history from the DynamoDB table, appends the new message to the history, and sends it to ChatGPT for a response. Once the response is obtained, it is appended to the chat history, which is then updated in the DynamoDB table. The chat history state is preserved on a per-channel basis, with no expiration logic currently implemented.

5. **Slack Integration**: The response from ChatGPT is sent to the Slack `postMessage` API endpoint, which posts the response in the respective Slack channel.

6. **Secret Management**: The Slack and OpenAI secrets provided through Terraform are stored in AWS Secrets Manager. The Python application retrieves these secrets from Secrets Manager when needed for secure access to the Slack and OpenAI APIs.

This architecture allows the SlackGPT bot to interact seamlessly with users in Slack channels while maintaining conversation state, ensuring data security, and leveraging the benefits of serverless infrastructure.

### Configurable Variables

The following table lists the configurable variables in the `variables.tf` file:

| Variable Name                       | Description                                                                                      | Default Value             | Sensitive |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------- | --------- |
| dynamodb_table_name                 | Table to store app state                                                                         | "slackgpt"                | No        |
| secret_mgr_path                     | Path to store secrets in AWS secret manager                                                      | "slackgpt"                | No        |
| openai_default_chat_model           | Default chat model to use                                                                        | "gpt-3.5-turbo"           | No        |
| openai_model_max_tokens             | Max allowed tokens for the specified openai model (see https://platform.openai.com/docs/models). | 4096                      | No        |
| openai_api_key                      | OpenAI API key                                                                                   | N/A                       | Yes       |
| slack_signing_key                   | Slack signing key                                                                                | N/A                       | Yes       |
| slack_bot_token                     | Slack bot token                                                                                  | N/A                       | Yes       |
| slack_bot_display_name              | Slack bot display name                                                                           | "slackgpt"                | No        |
| event_consumer_lambda_function_name | Name of the lambda function that receives slack events and sends them to the background          | "slackgpt-event-consumer" | No        |
| job_worker_lambda_function_name     | Name of the lambda function that processes the jobs and sends the response back to slack         | "slackgpt-job-worker"     | No        |
| lambda_execution_role_name          | Name of the iam role that gets created for the lambda function                                   | "slackgpt-lambda-role"    | No        |
| execution_timeout                   | Max amount of seconds that the lambda function can run before its terminated                     | 60                        | No        |
| api_gateway_name                    | Name of the api gateway                                                                          | "SlackGPT"                | No        |
| aws_region                          | AWS region to deploy resources                                                                   | "us-east-1"               | No        |
| api_gateway_stage_name              | Name of the api gateway stage                                                                    | "main"                    | No        |
| api_gateway_resource_path           | Last part of the api gateway endpoint path                                                       | "slackgpt"                | No        |
| sqs_queue_name                      | Name of the sqs queue for sending the processing job to the background                           | "slackgpt"                | No        |

## Contributing

Contributions are welcome! Please feel free to send a pull request and I will review it as soon as I can.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
