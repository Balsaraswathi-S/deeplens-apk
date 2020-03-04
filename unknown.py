import json
import boto3
import requests
import hashlib
import os
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

bucket_name = os.environ['doorman-apk']
slack_token = os.environ['xoxp-929407804161-941770225558-931346518001-c7e1d9ac7da10763c84094109931a528']
slack_channel_id = os.environ['CTPNN7N3G']
rekognition_collection_id = os.environ['deeplensapk']


def unknown(event, context): 
    key = event['Records'][0]['s3']['object']['key'] ##accessing the meta data from the AWS s3 with Lambda

    data = {
        "channel": slack_channel_id, ##giving the slack channel id where the message has to be sent
        "text": "I don't know who this is, can you tell me?", ##erroe message if the person is not recognised 
        "attachments": [
            {
                "image_url": "https://s3.amazonaws.com/%s/%s" % (bucket_name, key), ##creating and saving the image in s3 bucket
                "fallback": "Nope?",
                "callback_id": key,
                "attachment_type": "default",
                "actions": [{
                        "name": "username",
                        "text": "Select a username...",
                        "type": "select",
                        "data_source": "users"
                    },
                    {
                        "name": "discard",
                        "text": "Ignore",
                        "style": "danger",
                        "type": "button",
                        "value": "ignore",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Are you sure you want to ignore and delete this image?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            }
        ]
    }
    print(data)
    foo = requests.post("https://slack.com/api/chat.postMessage", headers={'Content-Type':'application/json;charset=UTF-8', 'Authorization': 'Bearer %s' % slack_token}, json=data) ##calling the slack API

    print(foo.json()) ## printing the JSON file

