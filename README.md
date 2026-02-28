# Discord Count Bot

[![CI/CD](https://github.com/wildfan46/discord-count-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/wildfan46/discord-count-bot/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A serverless Discord counting bot implemented as an AWS Lambda function.

## Features

- Responds to counting messages in a Discord channel.
- Maintains count state using DynamoDB.
- Designed for low-cost, scalable operation on AWS Lambda.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- AWS account with Lambda permissions
- Discord account and bot token
- (Optional) AWS CLI configured for deployment

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/wildfan46/discord-count-bot.git
    cd discord-count-bot
    ```

2. **Install dependencies:**
    ```sh
    pip install -r src/requirements.txt
    ```

## Configuration

1. **Create a Discord Bot:**
    - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
    - Create a new application and add a bot.
    - Copy the bot token.

2. **Set Environment Variables:**
    - Required:
        - `DISCORD_TOKEN`: Your Discord bot token.
        - `CHANNEL_ID`: The Discord channel ID for counting.
        - `TABLE_NAME`: DynamoDB table name (default: `discord-counts`).
    - (For Lambda) Set these in the Lambda environment variables.

## Usage

### Running Locally

1. Set environment variables in your shell or a `.env` file.
2. Run the bot:
    ```sh
    python src/main.py
    ```

### Deploying to AWS Lambda

1. **Build and Deploy with AWS SAM:**
    ```sh
    sam build
    sam deploy --stack-name <stack-name> --s3-bucket <bucket-name> --capabilities CAPABILITY_IAM
    ```
    - Replace `<stack-name>` and `<bucket-name>` with your values.
    - Set environment variables in the Lambda configuration.

2. **GitHub Actions Deployment:**
    - On push to `main`, the workflow in `.github/workflows/deploy-lambda.yml` will:
        - Build and deploy the Lambda using AWS SAM.
        - Use OIDC for AWS credentials.

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.