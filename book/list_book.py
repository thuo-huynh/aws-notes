import json
import boto3
from decimal import *
from boto3.dynamodb.types import TypeDeserializer

client = boto3.client('dynamodb') 
serializer = TypeDeserializer()

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
            
def deserialize(data):
    if isinstance(data, list):
        return [deserialize(v) for v in data]

    if isinstance(data, dict):
        try:
            return serializer.deserialize(data)
        except TypeError:
            return {k: deserialize(v) for k, v in data.items()}
    else:
        return data

def lambda_handler(event, context):
    data_books = client.scan(
        TableName='Books',
        IndexName='name-index'
    )
    format_data_books = deserialize(data_books["Items"])
    for book in format_data_books:
        data_comment = client.query(
            TableName="Books", 
            KeyConditionExpression="id = :id AND rv_id > :rv_id", 
            ExpressionAttributeValues={
                ":id": {"S": book['id']}, 
                ":rv_id": {"N": "0"}
            }
        )
        format_data_comment = deserialize(data_comment['Items'])
        print(data_comment['Items'])
        book["comments"] = format_data_comment
            
    print (format_data_books)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method,X-Access-Token,XKey,Authorization"
        },
        "body": json.dumps(format_data_books, cls=DecimalEncoder)
    }
