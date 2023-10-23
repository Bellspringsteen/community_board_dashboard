import json
import csv
import random
from PersisterClass import PersisterS3,PersisterGlobalVariables
from VoterClass import Voter
from VoteClass import Vote
from VoteOptionsEnum import VoteOptions
from twilio.twiml.messaging_response import MessagingResponse
from VoteLoggingClass import LocalVoteLoggingClass

INSTRUCTIONS_MESSAGE = ' Welcome to CB7 text message voting. text yes to vote yes, no to vote no, abstain to vote abstain, cause to vote cause. '
INVALID_INPUT_MESSAGE = 'Your vote was NOT RECORDED, your message was invalid. '
NOT_VOTING_MESSAGE = 'Not currently open for voting'
NOT_VALID_NUMBER_MESSAGE = 'We dont have a record of your number, tell Alex your name and this number'
JESSIE_MODE_BUT_FAILED = 'You are in Jessie mode, but the query failed'

JESSIE_MODE_NUMBER = '+1646740645011'

# S3 Persister
#persister = PersisterS3()

# Local Persister
persister= PersisterGlobalVariables()
persister.load_members() 


# Local Vote Logger
votelogger = LocalVoteLoggingClass()

def get_vote_from_string(incoming_message):
    if 'cause' in incoming_message or 'Cause' in incoming_message:
        return VoteOptions.CAUSE
    elif 'abstain' in incoming_message or 'Abstain' in incoming_message:
        return VoteOptions.ABSTAIN
    elif 'yes'in incoming_message or 'Yes' in incoming_message:
        return VoteOptions.YES
    elif 'no' in incoming_message or 'No' in incoming_message:
        return VoteOptions.NO
    else:
        return None 

def summarize_votes():

    vote_summary = {
       VoteOptions.YES:[],
       VoteOptions.NO:[],
       VoteOptions.ABSTAIN:[],
       VoteOptions.CAUSE:[]
    }
    vote_log = persister.get_vote_log()
    for voter_number in vote_log:
        vote_summary[vote_log[voter_number].voters_vote].append(vote_log[voter_number].toJSON())

    return vote_summary

def get_summary():
    vote_summary = summarize_votes()
    pre_amble = '------------------ \nVote Summary for '+persister.get_current_vote_name() + '\n'
    results = ('Voting Summary:\n' +str(len(vote_summary[VoteOptions.YES]))+' yes votes \n' +str(len(vote_summary[VoteOptions.NO]))+' no votes \n' +str(len(vote_summary[VoteOptions.ABSTAIN]))+' abstain votes \n' +str(len(vote_summary[VoteOptions.CAUSE]))+' abstaining for cause votes \n')
    log = '----Raw Log ----- \n'
    for voted_option in VoteOptions:
        for voted_option_results in vote_summary[voted_option]:
            log += voted_option_results['voter']+" voted "+ voted_option.value +' \n'

    return pre_amble+results+log

def check_if_instructions(incoming_msg):
    if 'instructions' in incoming_msg or 'Instructions' in incoming_msg:
        return True

def create_response_msg(text_to_send):
    r = MessagingResponse()
    r.message(text_to_send)
    return str(r)

def extract_name_and_vote(text):
    parts = text.split('-')
    if len(parts) == 2:
        name, vote = parts
        return name, vote
    else:
        return None, None
    
def search_for_number_for_name(name_to_query):
    members = persister.get_members()
    for voter in members.items():
        if name_to_query.lower_case() in voter[1].name.lower_case():
            return voter[0]
    return None

def parse_incoming_text(incoming_number,incoming_msg):
    votelogger.log_raw_vote_to_file(incoming_number,incoming_msg,persister.get_current_vote_name())

    if incoming_number is JESSIE_MODE_NUMBER:
        name_to_query,vote_to_send = extract_name_and_vote(incoming_msg)
        incoming_msg = vote_to_send
        incoming_number = search_for_number_for_name(name_to_query)

        if incoming_number is None or incoming_msg is None:
            return create_response_msg(JESSIE_MODE_BUT_FAILED) 

    members = persister.get_members()
    if incoming_number not in members.keys():
        return create_response_msg(NOT_VALID_NUMBER_MESSAGE+' '+incoming_number)

    voting_member:Voter = members[incoming_number] or None
    if not persister.get_currently_in_a_voting_session():
        return create_response_msg(NOT_VOTING_MESSAGE)
    if check_if_instructions(incoming_msg):
        return create_response_msg(INSTRUCTIONS_MESSAGE)
    vote_cast = get_vote_from_string(incoming_msg)
    if vote_cast == None:
        return create_response_msg(INVALID_INPUT_MESSAGE)
    

    persister.add_to_vote_log(key=voting_member.sms_number,value=Vote(voting_member,vote_cast))

    r = MessagingResponse()
    r.message('Your vote has been recorded, you voted '+vote_cast.value+' for resolution '+persister.get_current_vote_name())
    return str(r)

def true_if_members_list_zero():
    members = persister.get_members()
    return len(members) == 0

#### API SECTION ###

def api_get_results():
    from enum import Enum
    custom_encoder = lambda obj: obj.value if isinstance(obj, Enum) else obj #TODO , shouldnt this be apart of the class
    summary = summarize_votes()
    converted_summary = {custom_encoder(key): value for key, value in summary.items()}
    return json.dumps(converted_summary)


def api_testing():
    members = persister.get_members()
    for voter in members.items():
        random_vote = random.choice([VoteOptions.YES.value, VoteOptions.NO.value, VoteOptions.CAUSE.value,VoteOptions.ABSTAIN.value])
        parse_incoming_text(voter[0], random_vote)

def api_start_voting(title):
    persister.set_current_vote_name(title)
    persister.set_currently_in_a_voting_session(True)

def api_stop_voting():
    votelogger.log_vote_summary_to_file(get_summary())
    persister.set_current_vote_name('')
    persister.set_currently_in_a_voting_session(False)
    persister.clear_vote_log()

def api_is_voting_started():
    return {"isVotingStarted": persister.get_currently_in_a_voting_session(),"currentVoteName":persister.get_current_vote_name()}

# TODO refactor all the logging vote class, and then allow for logging to S3 or local
# TODO, dont just pass on exceptions, got to do something there
# TODO, some kind of simple password. Window.alert? Pass it in a header? For the twilio, i think your going to have to pass it in the url parameters
# TODO, put it on the custom domain you bought
# TODO, some kind of deployment scripts? put the html in a static bucket
# TODO, when the timer is over. Show a BIG STOP SIGN and start playing music louder and louder
# TODO, when reloading in a vote, the other ui elements come back
# TODO add type checking
# TODO, change to REACT to make fluid
# TODO, unit tests bro 
# TODO, admin tool? With Login? to change the list of users and numbers?