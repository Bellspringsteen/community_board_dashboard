from flask import Flask, request, render_template,jsonify

from app import * 
app = Flask('Voting')


@app.route('/', methods=['POST'])
def incoming_text():
    incoming_msg = request.values['Body']
    incoming_number = request.values['From']
    return parse_incoming_text(incoming_number,incoming_msg)
    

@app.route('/results', methods=['GET'])
def results():
    from enum import Enum
    custom_encoder = lambda obj: obj.value if isinstance(obj, Enum) else obj #TODO , shouldnt this be apart of the class
    summary = summarize_votes()
    converted_summary = {custom_encoder(key): value for key, value in summary.items()}
    return json.dumps(converted_summary)

@app.route('/webresults', methods=['GET'])
def webresults():
   return render_template('./index.html')

@app.route('/testing', methods=['GET'])
def testing():
    members = persister.get_members()
    for voter in members.items():
        random_vote = random.choice([VoteOptions.YES.value, VoteOptions.NO.value, VoteOptions.CAUSE.value,VoteOptions.ABSTAIN.value])
        parse_incoming_text(voter[0], random_vote)
    return 'OK'

@app.route('/startvoting', methods=['POST'])
def startvoting():
    members = persister.get_members()
    try:
        if len(members) == 0:
            response = {
                'error': 'Internal Server Error',
                'message': 'Member list is zero',
            }
            return jsonify(response), 500 
        data = request.get_json()
        title = data.get('title')
        persister.set_current_vote_name(title)
        persister.set_currently_in_a_voting_session(True)
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
        log_vote_summary_to_file()
        persister.set_current_vote_name('')
        persister.set_currently_in_a_voting_session(False)
        persister.clear_vote_log()
        return 'OK'  
    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': 'Couldnt stop voting',
        }
        return jsonify(response), 500
    

@app.route('/isvotingstarted', methods=['GET'])
def is_voting_started():
    return jsonify({"isVotingStarted": persister.get_currently_in_a_voting_session(),"currentVoteName":persister.get_current_vote_name()})