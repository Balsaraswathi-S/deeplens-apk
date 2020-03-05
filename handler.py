import json
import boto3
import requests
import hashlib
import os
from urllib.parse import parse_qs

bucket_name = os.environ['lensapk']
slack_token = os.environ['xoxp-929407804161-941770225558-931346518001-c7e1d9ac7da10763c84094109931a528']
slack_channel_id = os.environ['CTPNN7N3G']
rekognition_collection_id = os.environ['deep-apk']

from doorman import guess
from doorman import train
from doorman import unknown


