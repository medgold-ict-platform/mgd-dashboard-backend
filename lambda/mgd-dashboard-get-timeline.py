import json
import boto3
import os
from boto3.dynamodb.conditions import Attr 
dynamodb = boto3.resource('dynamodb')
table_wf = dynamodb.Table(os.environ['dashboard_table'])


def timeline(event, context):
    items = []
    id = event['pathParameters']['id']
    resource_type = event['pathParameters']['resource']
    print(event['pathParameters'])
    try:
        response = table_wf.scan(
            FilterExpression = Attr('id').eq(id)
        )
        items = response['Items'][0][resource_type]['Timeline']
    except Exception as e:
        return {
                'statusCode': 404,
                'body': 'dataset id not found!'
            }

   

    print(items)

    if len(items) == 0:
        return {
                'statusCode': 404,
                'body': 'dataset id not found!',
                "headers": {
                    "Access-Control-Allow-Origin": '*'
                }
            }


    return {
        'statusCode': 200,
        'body': json.dumps(items),
        "headers": {
            "Access-Control-Allow-Origin": '*'
        }
    }