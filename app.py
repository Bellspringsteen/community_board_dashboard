import json
from flask import Flask, request, render_template,jsonify
from twilio.twiml.messaging_response import MessagingResponse

app = Flask('Voting')

class Voter:
  def __init__(self, name, sms_number):
    self.name = name
    self.sms_number = sms_number

  def __str__(self):
    return f"{self.name})"
  
  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__)

class Vote:
  def __init__(self, voter:Voter, voters_vote):
    self.voter:Voter = voter
    self.voters_vote = voters_vote

  def __str__(self):
    return f"{self.voter.vote})"
  
  def toJSON(self):
    return {
        'voter': self.voter.name,
        'votes_vote': self.voters_vote
    }
      
VOTE_YES = 'Yes'
VOTE_NO = 'No'
VOTE_ABSTAIN = 'Abstain'
VOTE_CAUSE = 'Abstaining for Cause'
VOTE_OPTIONS = [VOTE_YES,VOTE_NO,VOTE_ABSTAIN,VOTE_CAUSE]

NUMBER_ALEX_BELL = '+19178418243'
NUMBER_BARBARA_ADLER = '+19179407979'
NUMBER_BEVERLY = '+19175739898'
NUMBER_MAX = '+13479783985'
NUMBER_JESSIE = '+16467406450'

members = {
    NUMBER_ALEX_BELL: Voter('Alex Bell',NUMBER_ALEX_BELL),
    NUMBER_BARBARA_ADLER: Voter('Barbara Adler',NUMBER_BARBARA_ADLER),
    NUMBER_BEVERLY: Voter('Beverly',NUMBER_BEVERLY),
    NUMBER_MAX: Voter('Max',NUMBER_MAX),
    NUMBER_JESSIE: Voter('Jessie',NUMBER_JESSIE),
}

vote_log = {}

current_vote_name =''
currently_in_a_voting_session = False

INSTRUCTIONS_MESSAGE = ' Welcome to CB7 text message voting. Text yes to vote yes, no to vote no, abstain to vote abstain, cause to vote cause. '
INVALID_INPUT_MESSAGE = 'Your vote was NOT RECORDED, your message was invalid. '
NOT_VOTING_MESSAGE = 'Not currently open for voting'

def get_vote_from_string(incoming_message):
    if 'cause' in incoming_message or 'Cause' in incoming_message:
        return VOTE_CAUSE
    elif 'abstain' in incoming_message or 'Abstain' in incoming_message:
        return VOTE_ABSTAIN
    elif 'yes'in incoming_message or 'Yes' in incoming_message:
        return VOTE_YES
    elif 'no' in incoming_message or 'No' in incoming_message:
        return VOTE_NO
    else:
        return None 

def summarize_votes():

    vote_summary = {
       VOTE_YES:[],
       VOTE_NO:[],
       VOTE_ABSTAIN:[],
       VOTE_CAUSE:[]
    }
    for voter_number in vote_log:
        vote_summary[vote_log[voter_number].voters_vote].append(vote_log[voter_number].toJSON())

    return vote_summary
    

def get_summary():
    vote_summary = summarize_votes()
    pre_amble = 'Here is the voting summary \n'
    results = ('Voting Summary:\n' +str(len(vote_summary[VOTE_YES]))+' yes votes \n' +str(len(vote_summary[VOTE_NO]))+' no votes \n' +str(len(vote_summary[VOTE_ABSTAIN]))+' abstain votes \n' +str(len(vote_summary[VOTE_CAUSE]))+' abstaining for cause votes \n')
    log = '----------------------- \n'
    for voted_option in VOTE_OPTIONS:
        for voted_option_results in vote_summary[voted_option]:
            log += voted_option_results['name']+" voted "+ voted_option +' \n'

    return pre_amble+results+log

def check_if_instructions(incoming_msg):
    if 'instructions' in incoming_msg or 'Instructions' in incoming_msg:
        return True

def create_response_msg(text_to_send):
    r = MessagingResponse()
    r.message(text_to_send)
    return str(r)

def write_to_file():

    f = open("/home/regolith/voting.txt", "w")
    f.write(get_summary())
    f.close()

def parse_incoming_text(incoming_number,incoming_msg):
    if not currently_in_a_voting_session:
        return create_response_msg(NOT_VOTING_MESSAGE)
    voting_member:Voter = members[incoming_number]
    #TODO check if number is in list, otherwise respond with "You are not in the list, here is your number, this is only available for board members"
    if check_if_instructions(incoming_msg):
        return create_response_msg(INSTRUCTIONS_MESSAGE)
    vote_cast = get_vote_from_string(incoming_msg)
    if vote_cast == None:
        return create_response_msg(INVALID_INPUT_MESSAGE)
    
    vote_log[voting_member.sms_number] = Vote(voting_member,vote_cast)
    #print(get_summary())
    #write_to_file()
    r = MessagingResponse()
    r.message('Your vote has been recorded, you voted '+vote_cast+' for resolution '+current_vote_name)
    return str(r)


@app.route('/', methods=['POST'])
def incoming_text():
    incoming_msg = request.values['Body']
    incoming_number = request.values['From']
    return parse_incoming_text(incoming_number,incoming_msg)
    

@app.route('/results', methods=['GET'])
def results():
    return json.dumps(summarize_votes())

@app.route('/webresults', methods=['GET'])
def webresults():
   return render_template('./index.html')

@app.route('/testing', methods=['GET'])
def testing():
   parse_incoming_text(NUMBER_ALEX_BELL,'Yes')
   parse_incoming_text(NUMBER_BARBARA_ADLER,'Yes')
   parse_incoming_text(NUMBER_BEVERLY,'abstain')
   parse_incoming_text(NUMBER_JESSIE, 'no')
   parse_incoming_text(NUMBER_MAX,'Cause')
   return 'OK'

@app.route('/startvoting', methods=['POST'])
def startvoting():
    global current_vote_name,currently_in_a_voting_session,title
    try:
        data = request.get_json()
        title = data.get('title')
        current_vote_name = title
        currently_in_a_voting_session = True

        return 'OK'  
    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': 'Couldnt start voting',
        }
        return jsonify(response), 500

@app.route('/stopvoting', methods=['POST'])
def stopvoting():
    global current_vote_name,currently_in_a_voting_session,vote_log
    try:
        current_vote_name = ''
        currently_in_a_voting_session = False
        vote_log = {}
        return 'OK'  
    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': 'Couldnt stop voting',
        }
        return jsonify(response), 500


# TODO, log every vote that comes in to a log file with the date, append mode
# TODO, on stop voting, log to a seperate file for each resolution with summary
# TODO, the fetch should stop when voting is not in progress
# TODO, make everything a nice python class and make the options ENUM
# TODO, get rid of global variables
# TODO, change so that front end polls for is currently in Voting Session, i.e. source of truth is backend
# TODO, change to REACT to make fluid
# TODO, deploy somewhere