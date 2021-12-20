import json
import os
import uuid
import logging

import boto3

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event,context):

    LOG.info("EVENT: " + json.dumps(event))

    query_string_params = event["queryStringParameters"]
    if query_string_params is not None:
        target_url = query_string_params['targetUrl']
        if target_url is not None:
            return create_short_url(event)

    return {
        'statusCode': 200,
        'body': 'usage: ?targetUrl=URL'
    }

def create_short_url(event):
    # Pull out the DynamoDB table name from environment
    table_name = os.environ.get("TABLE_NAME")
    # Parse targetUrl
    target_url = event["queryStringParameters"]["targetUrl"]
    keys = event["queryStringParameters"].keys()
    
    if "id" in keys:
        id = event["queryStringParameters"]["id"]
        
    else:
        id = str(uuid.uuid4())[0:8]
    

    # Create item in DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item={
        'id': id,
        'target_url': target_url
    })

    # Create the redirect URL
    url = "https://" \
        + event["requestContext"]["domainName"] \
        + "/"+id

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': "Created URL: %s" % url
    }


