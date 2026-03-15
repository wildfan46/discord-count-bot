import json

import boto3

import random

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

import dateparser

from datetime import datetime

from config import get_config

from boto3.dynamodb.conditions import Key, Attr

PUBLIC_KEY_HEX = get_config()['DISCORD_KEY']

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('discord-counts')  # This name must match template.yaml


def get_whimsical_response(count, user_name):
    # Responses based on the number of drinks logged for that day
    if count == 1:
        responses = [
            f"A fine start {user_name}, but those are rookie numbers.",
            f"The journey of a thousand drinks begins with one, {user_name}.",
            "Hydration is important. Wait, this isn't water.",
            "At least it isn't water I guess"
        ]
    elif 2 <= count <= 4:
        responses = [
            "Moving into the 'social butterfly' territory.",
            "I'm not saying you're a pro, but I'm impressed.",
            "Your liver has entered the chat."
        ]
    elif count >= 5:
        responses = [
            "Here is the link for the nearest AA meeting: [Google Maps](https://www.google.com/maps/search/aa+meetings+near+me)",
            "Do you want me to call a cab, or should I just call your mom?",
            "At this point, the DynamoDB table is just concerned for you.",
            "Please remember what a 'vegetable' looks like tomorrow."
        ]
    else:
        responses = [f"Logged it. Keep it classy, {user_name}"]

    return random.choice(responses)


def parse_user_date(user_input):
    settings = {
        'RELATIVE_BASE': datetime.now(),
        'TO_TIMEZONE': 'America/Chicago',
        'PREFER_DATES_FROM': 'past'
    }

    parsed = dateparser.parse(
        user_input,
        languages=['en'],
        settings=settings
    )

    if parsed:
        return parsed.strftime('%m-%d-%Y')
    return datetime.now().strftime('%m-%d-%Y')


def craft_response(amount, drink_subtype, drink_type, occurred_at, username, ytd_total):
    if drink_type == "wine":
        inner = f"Logged {amount} {drink_subtype} {drink_type}s for {occurred_at}"
    elif drink_subtype and not drink_subtype == 'Standard':
        inner = f"Logged {amount} {drink_subtype}s for {occurred_at}"
    else:
        inner = f"Logged {amount} {drink_type}s for {occurred_at}"
    return f"{inner}. {get_whimsical_response(amount, username)}.\nYour YTD count is now {ytd_total}"


def handle_log_command(data):
    options = {opt['name']: opt['value'] for opt in data['data'].get('options', [])}

    # Extract data
    guild_id = data['guild_id']
    user_id = data['member']['user']['id']
    username = data['member']['nick']

    amount = options.get('amount')
    drink_type = options.get('type')
    drink_subtype = options.get('subtype', 'Standard')
    print("Before parsing date")
    occurred_at = parse_user_date(options.get('date', "today"))

    # Generate a unique Sort Key (SK) using timestamp and a UUID to prevent collisions
    current_time = datetime.now()
    log_timestamp = current_time.isoformat()

    print("Before Dynamo write")
    # Put item into DynamoDB
    table.put_item(
        Item={
            'PK': f"SERVER#{guild_id}",
            'SK': f"USER#{user_id}#T{log_timestamp}",
            'user': user_id,
            'amount': amount,
            'drink_type': drink_type,
            'drink_subtype': drink_subtype,
            'occurred_at': occurred_at,
            'logged_at': log_timestamp
        }
    )
    print("After Dynamo Write")

    response = table.query(
        KeyConditionExpression=(
                Key('PK').eq(f"SERVER#{guild_id}") &
                Key('SK').begins_with(f"USER#{user_id}")
        ),
        FilterExpression=Attr('occurred_at').contains(str(current_time.year))
    )
    print("After Dynamo Query")

    items = response.get('Items', [])
    total_amount = sum(item.get('amount', 0) for item in items)

    response = craft_response(amount, drink_subtype, drink_type, occurred_at, username, total_amount)

    return response


def lambda_handler(event, context):
    print("Request Received")
    # Get Discord headers
    signature = event['headers'].get('x-signature-ed25519')
    timestamp = event['headers'].get('x-signature-timestamp')
    body = event['body']

    # 1. Verify Signature
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(PUBLIC_KEY_HEX))
        public_key.verify(bytes.fromhex(signature), f"{timestamp}{body}".encode())
    except (InvalidSignature, ValueError, TypeError):
        return {"statusCode": 401, "body": "invalid request signature"}
    print("Verified Signature")

    data = json.loads(body)

    # 2. Handle Discord Ping
    if data['type'] == 1:
        print("Handling Ping")
        return {"statusCode": 200, "body": json.dumps({"type": 1})}

    # 3. Handle Slash Command
    if data['type'] == 2:
        print("Handling Slash Command")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "type": 4,  # Type 4 = "Channel Message with Source"
                "data": {"content": handle_log_command(data)}
            })
        }

    return {"statusCode": 400, "body": "unknown interaction"}