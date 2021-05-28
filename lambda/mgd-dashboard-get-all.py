import boto3
import os
import botocore
import json
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr 

##DYNAMO##
dynamodb = boto3.resource('dynamodb')
dashboard_table = dynamodb.Table(os.environ["dashboard_table"])

##_DATASET INFO_##
def all(event,context):
  items = []
  try:
    response = dashboard_table.scan()
    items = response['Items']
  except Exception as e:
      return {
            'statusCode': 404,
            'body': json.dumps({"Message":"table not found!"}),
            "headers": {
            "Access-Control-Allow-Origin": '*'
        }
      }

  if len(items) == 0:
     return {
            'statusCode': 404,
            'body': json.dumps({"Message":"items not found!"}),
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
