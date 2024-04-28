import boto3
import json

s3 = boto3.client('s3')
client = boto3.resource('dynamodb')

def get_image_name(image_path):
    str_image = image_path.split("/")
    for image_path_item in str_image:
        image_name = image_path_item
        
    return image_name;
    
def lambda_handler(event, context):
    error = None
    status = 200
    delete_id = event['pathParameters']
    delete_id['rv_id'] = 0
    
    table = client.Table("Books")
    image_path = ""

    try:
        data = table.get_item(Key = delete_id)
        image_path = data['Item']['image']
        image_name = get_image_name(image_path)
    except Exception as e:
        error = e
    
    try:
        response = table.query(
            ProjectionExpression="rv_id", 
            KeyConditionExpression="id = :id", 
            ExpressionAttributeValues={":id": delete_id['id']})
            
        for item in response['Items']:
            delete_id['rv_id'] = item['rv_id']
            print(delete_id)
            table.delete_item(Key = delete_id)
        
        print(image_name)
        s3.delete_object(Bucket='book-image-resize-store-1', Key=image_name)
        
    except Exception as e:
        error = e
    
    if error is None:
        message = 'successfully deleted item!'
    else:
        message = 'delete item fail'
        status = 400

    return {
            'statusCode': status,
            'body': message,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }
