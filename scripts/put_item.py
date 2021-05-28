import boto3
import sys
import os
import json

dataset_items_path = './items/'
dynamodb = boto3.resource('dynamodb')

if __name__ == "__main__":
    cwd = os.getcwd()
    print(cwd)
    table_items = dynamodb.Table(sys.argv[1])

    for file in os.listdir(dataset_items_path):
        with open(dataset_items_path+file, 'r') as f:
            item = f.read()
            print(item)
            response = table_items.put_item(
                Item=json.loads(item))