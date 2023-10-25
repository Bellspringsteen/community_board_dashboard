import json
from main import *
import base64
from urllib.parse import parse_qs

import os
import boto3

s3 = boto3.client('s3')
API_KEY = os.environ.get('API_KEY')
TWILIO_API_KEY = os.environ.get('TWILIO_API_KEY')

def lambda_handler(event, context):
    if event['rawPath'] == '/default/incomingtext' and event['rawQueryString'] == 'auth='+TWILIO_API_KEY:
                body = event['body']
                decoded_body = base64.b64decode(body).decode('utf-8')
                query_params = parse_qs(decoded_body)
                incoming_msg = query_params.get('Body', [''])[0]
                incoming_number = query_params.get('From', [''])[0]
                return {
                   'body': str(parse_incoming_text(incoming_number,incoming_msg)),
                   'statusCode': 200,
                   'headers': {
                       'Content-Type': 'application/xml'
                   }
                }
    if 'headers' in event and 'x-api-key' in event['headers'] and event['headers']['x-api-key'] == API_KEY:
        # Authentication key is valid
        if event['requestContext']['http']['method'] == 'POST':
            if event['rawPath'] == '/default/startvoting':
                if true_if_members_list_zero():
                    response = {
                        'error': 'Internal Server Error',
                        'message': 'Member list is zero',
                    }
                    return json.dumps(response), 500 
                body = event['body']
                data = json.loads(body)
                title = data.get('title', None)
                api_start_voting(title=title)
                return get_ok()
            elif event['rawPath'] == '/default/stopvoting':
                return api_stop_voting()
        elif event['requestContext']['http']['method']== 'GET':
            if event['rawPath'] == '/default/results':
                return api_get_results()
            elif event['rawPath'] == '/default/webresults':
                return get_html_page()
            elif event['rawPath'] == '/default/testing':
                return api_testing()
            elif event['rawPath'] == '/default/isvotingstarted':
                return json.dumps(api_is_voting_started())
        else:
            return {
                'statusCode': 405,
                'body': json.dumps('Method not allowed')
            }
    else:
        # Invalid authentication key
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized')
        }
    
def get_ok():
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin": "*" # TODO Remove this
        },
        'body': json.dumps('OK')
    }
    return response
    
def get_html_page():
    bucket_name = 'cb-dashboard-data-store'
    html_file_key = 'index.html'

    # Retrieve the HTML content from S3
    response = s3.get_object(Bucket=bucket_name, Key=html_file_key)
    html_content = response['Body'].read().decode('utf-8')

    # Construct an HTTP response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': html_content
    }

    return response
