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
    print(str(event))
    # Extract HTTP method and path from the event
    http_method = event['requestContext']['http']['method']
    path = event['rawPath']

    if path == '/default/webresults':
        return get_html_page()
    if path == '/default/incomingtext' and 'auth=' + TWILIO_API_KEY in event['rawQueryString']:
        body = event['body']
        decoded_body = base64.b64decode(body).decode('utf-8')
        query_params = parse_qs(decoded_body)
        # Extract community_board from the query string
        query_string_params = parse_qs(event['rawQueryString'])
        community_board = query_string_params.get('cb', [''])[0]
        incoming_msg = query_params.get('Body', [''])[0]
        incoming_number = query_params.get('From', [''])[0]
        return {
            'body': str(parse_incoming_text(incoming_number, incoming_msg, community_board)),
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/xml'
            }
        }
    if 'headers' in event and 'x-api-key' in event['headers'] and event['headers']['x-api-key'] == API_KEY:
        # Authentication key is valid
        community_board = event['headers']['x-community-board']
        if http_method == 'POST':
            if path == '/default/startvoting':
                if true_if_members_list_zero(community_board):
                    response = {
                        'error': 'Internal Server Error',
                        'message': 'Member list is zero',
                    }
                    return json.dumps(response), 500 
                body = event['body']
                data = json.loads(body)
                title = data.get('title', None)
                api_start_voting(title=title,community_board=community_board)
                return get_ok()
            elif path == '/default/manualentry':
                print('ALEX'+str(event))
                body = event['body']
                data = json.loads(body)
                print(str(data))
                number_sms = data['number_sms']
                vote_to_send = data['vote_to_send']
                return api_testing(number_sms,vote_to_send,community_board)
            elif path == '/default/stopvoting':
                return api_stop_voting(community_board)
            elif path == '/members':
                body = json.loads(event['body']) if event.get('body') else {}
                return api_set_members(body,community_board)
        elif http_method == 'GET':
            if path == '/default/results':
                return api_get_results(community_board)
            elif path == '/default/export-votes':
                return handle_export_votes(event,community_board)
            elif path == '/default/isvotingstarted':
                return json.dumps(api_is_voting_started(community_board))
            elif path == '/members':
                return api_get_members(community_board)
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
# Define the path to the HTML file within your Lambda package
    html_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

    # Read the HTML content from the file
    with open(html_file_path, 'r') as html_file:
        html_content = html_file.read()

    # Construct an HTTP response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': html_content
    }

    return response

def handle_export_votes(event,community_board):
    try:
        body = json.loads(event['body'])
        date = body.get('date')
        
        if not date:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Date is required'})
            }

        # Convert YYYY-MM-DD to YYYYMMDD format
        formatted_date = date.replace('-', '')
        
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # Fetch summary votes for the date
        response = s3.list_objects_v2(
            Bucket='cb-dashboard-data-store',
            Prefix=f'summaryvotelog/{community_board}/{formatted_date}'
        )
        
        if 'Contents' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No data found for this date'})
            }
            
        # Combine all matching files
        combined_data = []
        for obj in response['Contents']:
            file_content = s3.get_object(
                Bucket='cb-dashboard-data-store',
                Prefix=f'summaryvotelog/{community_board}/{formatted_date}',
                Key=obj['Key']
            )['Body'].read().decode('utf-8')
            combined_data.append(file_content)
                
        return {
            'statusCode': 200,
            'body': '\n'.join(combined_data),
            'headers': {
                'Content-Type': 'text/plain'
            }
        }
        
    except Exception as e:
        print(f"Error in export_votes: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }



