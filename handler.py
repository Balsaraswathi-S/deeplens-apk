import json
import boto3
import requests
import hashlib
import os 
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse


bucket_name = 'lensapk'
slack_token = 'xoxp-929407804161-941770225558-931346518001-c7e1d9ac7da10763c84094109931a528'
slack_channel_id = 'CTPNN7N3G'
rekognition_collection_id = 'deep-apk'

# from doorman import guess
# from doorman import train
# from doorman import unknown



