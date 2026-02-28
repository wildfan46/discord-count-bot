import os
import boto3


ssm = boto3.client("ssm")


def get_param(name, decrypt=True):
    return ssm.get_parameter(
        Name=name, WithDecryption=decrypt
    )["Parameter"]["Value"]


def get_config():
    DISCORD_KEY = get_param(os.environ["DISCORD_KEY_PARAM"])
    return {
        "DISCORD_KEY": DISCORD_KEY,
    }
