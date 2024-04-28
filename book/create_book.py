import boto3
import json
import base64
import io
import cgi
import os

s3 = boto3.client('s3')
client = boto3.resource('dynamodb')
runtime_region = os.environ['AWS_REGION']

def get_data_from_request_body(content_type, body):
    fp = io.BytesIO(base64.b64decode(body)) # decode
    environ = {"REQUEST_METHOD": "POST"}
    headers = {
        "content-type": content_type,
        "content-length": len(body),
    }

    fs = cgi.FieldStorage(fp=fp, environ=environ, headers=headers) 
    return [fs, None]
    
def lambda_handler(event, context):
    content_type = event['headers'].get('Content-Type', '') or event['headers'].get('content-type', '')
    
    if content_type == 'application/json':
        book_item = json.loads(event["body"])
    else:
        book_data, book_data_error = get_data_from_request_body(
            content_type=content_type, body=event["body"]
        )
    
        name = book_data['image'].filename
        image = book_data['image'].value
        s3.put_object(Bucket='book-image-store-1', Key=name, Body=image)
        image_path = "https://{}.s3.{}.amazonaws.com/{}".format("book-image-resize-store-1", runtime_region, name)
        
        book_item = {
            "id": book_data['id'].value,
            "rv_id": 0,
            "name": book_data['name'].value,
            "author": book_data['author'].value,
            "price" : book_data['price'].value,
            "category": book_data['category'].value,
            "description": book_data['description'].value,
            "image": image_path
        }
    
    table = client.Table('Books')
    table.put_item(Item = book_item)
    
    response = {
        'statusCode': 200,
        'body': 'successfully created item!',
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method,X-Access-Token, XKey, Authorization",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,OPTIONS"
        },
    }
  
    return response
