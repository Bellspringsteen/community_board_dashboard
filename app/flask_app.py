from flask import Flask, request, render_template,jsonify
from functools import wraps
import os
from main import * 
app = Flask('Voting')

def require_auth_key(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_key = os.environ.get('API_KEY')
        provided_auth_key = request.headers.get('x-api-key')
        
        if provided_auth_key != auth_key:
            return jsonify({'message': 'Unauthorized'}), 401

        return func(*args, **kwargs)

    return decorated_function

@app.route('/incomingtext', methods=['POST'])
def incoming_text():
    incoming_msg = request.values['Body']
    incoming_number = request.values['From']
    return parse_incoming_text(incoming_number,incoming_msg)
    
@app.route('/results', methods=['GET'])
@require_auth_key
def results():
    return api_get_results()

@app.route('/webresults', methods=['GET'])
def webresults():
   return render_template('./index.html')

@app.route('/manualentry', methods=['POST'])
def testing():
    data = request.get_json()
    number_sms = data['number_sms']
    vote_to_send = data['vote_to_send']
    return api_testing(number_sms,vote_to_send)
    
@app.route('/startvoting', methods=['POST'])
@require_auth_key
def startvoting():
    try:
        if true_if_members_list_zero():
            print('Member list is zero')
            response = {
                'error': 'Internal Server Error',
                'message': 'Member list is zero',
            }
            return jsonify(response), 500 
        data = request.get_json()
        title = data.get('title')
        api_start_voting(title=title)
        return 'OK'  
    except Exception as e:
        print(e)
        response = {
            'error': 'Internal Server Error',
            'message': 'Couldnt start voting',
        }
        return jsonify(response), 500

@app.route('/stopvoting', methods=['POST'])
@require_auth_key
def stopvoting():
    try:
        api_stop_voting()
        return 'OK'  
    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': 'Couldnt stop voting',
        }
        return jsonify(response), 500
    
@app.route('/isvotingstarted', methods=['GET'])
@require_auth_key
def is_voting_started():
    return json.dumps(api_is_voting_started())