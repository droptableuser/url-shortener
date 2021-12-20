import json
import os
import uuid
import logging

import boto3

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event,context):

    LOG.info("EVENT: " + json.dumps(event))

  
    return read_short_url(event)


def read_short_url(event):
    # Parse redirect ID from path
    id = event["requestContext"]["path"][1:]
    # Pull out the DynamoDB table name from the environment
    table_name = os.environ.get('TABLE_NAME')

    # Load redirect target from DynamoDB
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.get_item(Key={'id': id})
    LOG.debug("RESPONSE: " + json.dumps(response))

    item = response.get('Item', None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'No redirect found for ' + id
        }

    # Respond with a redirect
    return {
        'statusCode': 301,
        'headers': {
            'Location': item.get('target_url')
        }
    }