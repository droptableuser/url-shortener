#!/usr/bin/env python3

from aws_cdk import core
import json
import os

from urlshortener.urlshortener_stack import UrlshortenerStack

ACCOUNT=os.environ.get('SEC_ENGINEER_ACCOUNT', '742344209721')
REGION=os.environ.get('SEC_ENGINEER_REGION', 'eu-central-1')
env = core.Environment(account=ACCOUNT, region=REGION)

app = core.App()
env_file = open("env.json")
details = json.load(env_file)
UrlshortenerStack(app, "urlshortener",details["app"],env=env)

app.synth()
