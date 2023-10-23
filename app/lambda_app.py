import json
from main import *

# Define your authentication key
AUTHENTICATION_KEY = 'your-auth-key'

import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    if 'headers' in event and 'x-api-key' in event['headers'] and event['headers']['x-api-key'] == AUTHENTICATION_KEY:
        # Authentication key is valid
        if event['httpMethod'] == 'POST':
            if event['resource'] == '/':
                incoming_msg = event['Body']
                incoming_number = event['From']
                return parse_incoming_text(incoming_number,incoming_msg)
            elif event['resource'] == '/startvoting':
                if true_if_members_list_zero():
                    response = {
                        'error': 'Internal Server Error',
                        'message': 'Member list is zero',
                    }
                    return json.dumps(response), 500 
                title = event['title']
                api_start_voting(title=title)
                return get_ok()
            elif event['resource'] == '/stopvoting':
                return api_stop_voting()
        elif event['httpMethod'] == 'GET':
            if event['resource'] == '/results':
                return api_get_results()
            elif event['resource'] == '/webresults':
                return get_html_page()
            elif event['resource'] == '/testing':
                return api_testing()
            elif event['resource'] == '/isvotingstarted':
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
