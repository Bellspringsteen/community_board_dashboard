from flask import Flask, request, render_template,jsonify

from main import * 
app = Flask('Voting')

@app.route('/incomingtext', methods=['POST'])
def incoming_text():
    #incoming_msg = request.values['Body']
    #incoming_number = request.values['From']
    test = create_response_msg('TEST')
    print(test)
    return create_response_msg('TEST')
    return parse_incoming_text(incoming_number,incoming_msg)
    

@app.route('/results', methods=['GET'])
def results():
    return api_get_results()

@app.route('/webresults', methods=['GET'])
def webresults():
   return render_template('./index.html')

@app.route('/testing', methods=['GET'])
def testing():
    api_testing()
    return 'OK'

@app.route('/startvoting', methods=['POST'])
def startvoting():
    try:
        if true_if_members_list_zero():
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
        response = {
            'error': 'Internal Server Error',
            'message': 'Couldnt start voting',
        }
        return jsonify(response), 500

@app.route('/stopvoting', methods=['POST'])
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
def is_voting_started():
    return json.dumps(api_is_voting_started())