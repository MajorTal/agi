"""AWS access for the bot: the SSO profile `private` and its Parameter Store secrets.

Run `aws sso login --profile private` first. No static AWS keys are used.
"""
import os
from functools import cache

import boto3

SESSION = boto3.Session(profile_name=os.getenv("AWS_PROFILE", "private"),
                        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))


@cache
def secret(env_name: str, parameter: str) -> str:
    """The env var `env_name` when set, else the SecureString /secrets/agi/<parameter>."""
    value = os.getenv(env_name)
    if value:
        return value
    response = SESSION.client("ssm").get_parameter(Name=f"/secrets/agi/{parameter}", WithDecryption=True)
    return response["Parameter"]["Value"]
