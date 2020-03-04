import json
import boto3
import requests
import hashlib
import os
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

bucket_name = os.environ['doorman-apk'] ##name of the bucket (S3)
slack_token = os.environ['xoxp-929407804161-941770225558-931346518001-c7e1d9ac7da10763c84094109931a528']
slack_channel_id = os.environ['CTPNN7N3G']
rekognition_collection_id = os.environ['deeplensapk']##name of the rekognition collection id

def train(event, context):
    # print(event['body'])
    data = parse_qs(event['body'])##creating the request object
    data = json.loads(data['payload'][0]) ##loading he data into the json
    print(data)
    key = data['callback_id']

    # if we got a discard action, send an update first, and then remove the referenced image
    if data['actions'][0]['name'] == 'discard':
        message = {
            "text": "Ok, I ignored this image",
            "attachments": [
                {
                    "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, key),
                    "fallback": "Nope?",
                    "attachment_type": "default",
                }
            ]
        }
        print(message)

        requests.post(  ##Requests will allow you to send HTTP/1.1 requests using Python
            data['response_url'],
            headers={
                'Content-Type':'application/json;charset=UTF-8',
                'Authorization': 'Bearer %s' % slack_token
            },
            json=message  ###message is stored to the json
        )
        s3 = boto3.resource('s3') ##getting the resources from the default session
        s3.Object(bucket_name, key).delete() ##deleting the file from the S3 bucket 


    if data['actions'][0]['name'] == 'username':
        user_id = data['actions'][0]['selected_options'][0]['value']
        new_key = 'trained/%s/%s.jpg' % (user_id, hashlib.md5(key.encode('utf-8')).hexdigest())

        message = {
            "text": "Trained as %s" % user_id,
            "attachments": [
                {
                    "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, new_key),
                    "fallback": "Nope?",
                    "attachment_type": "default",
                }
            ]
        }
        print(message)
        requests.post(data['response_url'], headers={'Content-Type':'application/json;charset=UTF-8', 'Authorization': 'Bearer %s' % slack_token}, json=message)

        # response is send, start training
        client = boto3.client('rekognition')
        resp = client.index_faces(
            CollectionId=rekognition_collection_id,
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': key,
                }
            },
            ExternalImageId=user_id,
            DetectionAttributes=['DEFAULT']
        )

        # move the s3 file to the 'trained' location
        s3 = boto3.resource('s3') ##getting the resouces from the default session
        s3.Object(bucket_name, new_key).copy_from(CopySource='%s/%s' % (bucket_name, key)) ##renaming the object
        s3.ObjectAcl(bucket_name, new_key).put(ACL='public-read') ##uploading a file to s3 and make it as public using boto3
        s3.Object(bucket_name, key).delete() ##deleting the files from the s3 bucket 

    return {
        "statusCode": 200 ##http response status code 
    }

