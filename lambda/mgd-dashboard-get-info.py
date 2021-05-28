import json
import boto3
import os
from boto3.dynamodb.conditions import Attr 
dynamodb = boto3.resource('dynamodb')
table_wf = dynamodb.Table(os.environ['dashboard_table'])

def info(event, context):
    items = []
    id = event['pathParameters']['id']
    try:
        response = table_wf.scan(
                FilterExpression = Attr('id').eq(id)
        )
        items = response['Items']
    except Exception as e:
        return {
                'statusCode': 404,
                'body': json.dumps({"Message":'dataset id not found!'})
            }

    if len(items) == 0:
        return {
                'statusCode': 404,
                'body': json.dumps({"Message":'dataset id not found!'})
            }


    return {
        'statusCode': 200,
        'body': json.dumps(items),
        "headers": {
                "Access-Control-Allow-Origin": '*'
        }
    }