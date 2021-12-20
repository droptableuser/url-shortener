#!/usr/bin/env python3

from aws_cdk import core

from urlshortener.urlshortener_stack import UrlshortenerStack


app = core.App()
UrlshortenerStack(app, "urlshortener")

app.synth()
