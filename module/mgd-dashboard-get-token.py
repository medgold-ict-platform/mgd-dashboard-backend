from pycognito.aws_srp import AWSSRP
import boto3 
import sys
import json 
import os 

pool_id = os.environ['pool_id']
client_id = os.environ['client_id']

def authentication(event, context):
    print(event)
    username = event["queryStringParameters"]['username']
    password = event["queryStringParameters"]['password']
    print(username)
    print(password)
    try:
        client = boto3.client('cognito-idp')
        aws = AWSSRP(username=username, password=password, pool_id=pool_id,client_id=client_id, client=client)
        tokens = aws.authenticate_user()
        print(tokens['AuthenticationResult']['IdToken'])
        return {
            'statusCode': 200,
            'body': json.dumps({"token": tokens['AuthenticationResult']['IdToken']}),
            "headers": {
                "Access-Control-Allow-Origin": '*'
            }
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 404,
            'body': json.dumps({"message": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": '*'
            }
        }

    return {
        'statusCode': 404,
        'body': json.dumps({"message": "Incorrect username or password"}),
        "headers": {
            "Access-Control-Allow-Origin": '*'
        }
    }


