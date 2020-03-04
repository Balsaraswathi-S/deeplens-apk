import json
import boto3
import requests
import hashlib
import os

bucket_name = os.environ['doorman-apk']
slack_token = os.environ['xoxp-929407804161-941770225558-931346518001-c7e1d9ac7da10763c84094109931a528']
slack_channel_id = os.environ['CTPNN7N3G']
rekognition_collection_id = os.environ['deeplensapk']


def guess(event, context):
    client = boto3.client('rekognition')  ##low level client representing the AWS Rekognition
    key = event['Records'][0]['s3']['object']['key'] ##getting the metadata from the s3 bucket
    event_bucket_name = event['Records'][0]['s3']['bucket']['name'] ##storing the metadata in the bucket name i.e) s3 bucket
    image = {
        'S3Object': {
            'Bucket': event_bucket_name, ##giving the bucket name 
            'Name': key
        }
    }
    # print(image)

    resp = client.search_faces_by_image(
        CollectionId=rekognition_collection_id, ##storing the rekognition-id in the collection_id
        Image=image,
        MaxFaces=1,
        FaceMatchThreshold=70)

    s3 = boto3.resource('s3') ##boto3-which allows users to make use of services like ec2 and s3

    if len(resp['FaceMatches']) == 0:
        # no known faces detected, let the users decide in slack
        print("No matches found, sending to unknown") ##message will be printed when no known faces are detected 
        new_key = 'unknown/%s.jpg' % hashlib.md5(key.encode('utf-8')).hexdigest() ##cyptographic hashes and encoding using md5 hash
        s3.Object(bucket_name, new_key).copy_from(CopySource='%s/%s' % (bucket_name, key)) ##renaming an object using copy_object
        s3.ObjectAcl(bucket_name, new_key).put(ACL='public-read') ##uploading a file to the s3 and make it public using boto3
        s3.Object(bucket_name, key).delete() ##deleting  the files from the s3 bucket
    else:
        print ("Face found") ##prints the message if the known faces are detected
        print (resp)
        # move image
        user_id = resp['FaceMatches'][0]['Face']['ExternalImageId']
        new_key = 'detected/%s/%s.jpg' % (user_id, hashlib.md5(key.encode('utf-8')).hexdigest())
        s3.Object(bucket_name, new_key).copy_from(CopySource='%s/%s' % (event_bucket_name, key))
        s3.ObjectAcl(bucket_name, new_key).put(ACL='public-read') ##uploading the file to the s3 and make it public using boto3
        s3.Object(bucket_name, key).delete() ##deleting the files from the s3 bucket

        # fetch the username for this user_id
        data = {
            "token": slack_token,
            "user": user_id
        }
        print(data)
        resp = requests.post("https://slack.com/api/users.info", data=data)
        print(resp.content)
        print(resp.json())
        username = resp.json()['user']['name']

        data = {
            "channel": slack_channel_id, ##data will be sent to the particular slack channel once the user enters
            "text": "Welcome @%s" % username, ##welcoming message with their name if the particular user was entered
            "link_names": True,
            "attachments": [
                {
                    "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, new_key),
                    "fallback": "Nope?",
                    "attachment_type": "default",
                }
            ]
        }
        resp = requests.post("https://slack.com/api/chat.postMessage", headers={'Content-Type':'application/json;charset=UTF-8', 'Authorization': 'Bearer %s' % slack_token}, json=data) ##posting the message in the slack channel with the name of the person
        return {} ##returns the result
