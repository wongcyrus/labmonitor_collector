import boto3
import os
import sys
import uuid
import urllib.parse
import json

rekognition_client = boto3.client('rekognition', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    db = os.environ['ScreenshotMetaDataTable']
    table = dynamodb.Table(os.environ['ScreenshotMetaDataTable'])
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        download_path = '/tmp/{}.jpg'.format(uuid.uuid4())
        
        key = urllib.parse.unquote(key)
        s3_client.download_file(bucket, key, download_path)
        with open(download_path, 'rb') as image:
            response = rekognition_client.detect_text(Image={'Bytes': image.read()})
     
        detected_text = response['TextDetections']
        data ={"id": key, "DetectedText": json.dumps(detected_text)}
        db_response = table.put_item(
           Item=data
        )
        print("PutItem succeeded:")
                
       
