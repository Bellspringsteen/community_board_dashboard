import csv 
from VoterClass import Voter
from VoteClass import Vote
from VoteOptionsEnum import VoteOptions
import boto3
import json
from typing import Dict
class Persister:
    '''
    Responsible for persisting vote, member, etc data.
    '''

    def __init__(self, use_db=False):
        pass

    def get_vote_log(self):
        pass

    def add_to_vote_log(self,key,value):
        pass

    def clear_vote_log(self):
        pass

    def get_current_vote_name(self):
        pass

    def set_current_vote_name(self, value):
        pass

    def get_currently_in_a_voting_session(self):
        pass

    def set_currently_in_a_voting_session(self, value):
        pass

    def load_members(self):
        pass

    def get_members(self)-> Dict[str, Voter]:
        pass

class PersisterS3(Persister):
    '''
    Persister implementation using Amazon S3
    '''

    file_path = './members.csv'  # TODO this is just for the first launch, remove this

    def __init__(self):
        super().__init__()
        self.s3_resource = boto3.resource('s3')
        self.bucket_name = 'cb-dashboard-data-store'
        self.vote_log_key = 'vote_log.json'
        self.current_vote_name_key = 'current_vote_name.json'
        self.currently_in_a_voting_session_key = 'currently_in_a_voting_session.json'
        self.members_key = 'members.json'

    def get_vote_log(self) -> Dict[str, Vote]:
    # Implement S3-based getter for vote_log
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.vote_log_key)
            vote_log_json = obj.get()['Body'].read().decode('utf-8')
            vote_log_data = json.loads(vote_log_json)

            # Deserialize vote_log_data into Dict[str, Vote]
            vote_log = {sms_number: Vote(voter=Voter(name=vote_data['voter'],sms_number=sms_number), voters_vote=VoteOptions(vote_data['votes_vote'])) for sms_number, vote_data in vote_log_data.items()}

            return vote_log
        except Exception as e:
            # Handle any exceptions
            return {}

    def set_vote_log(self, value):
        # Implement S3-based setter for vote_log
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.vote_log_key)
            value = {key: vote.toJSON() for key, vote in value.items()}
            obj.put(Body=json.dumps(value))
        except Exception as e:
            # Handle any exceptions
            pass

    def add_to_vote_log(self,key,value):
        vote_log = self.get_vote_log()
        vote_log[key] = value
        self.set_vote_log(vote_log)

    def clear_vote_log(self):
        vote_log = {}
        self.set_vote_log(vote_log)

    def get_current_vote_name(self):
        # Implement S3-based getter for current_vote_name
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.current_vote_name_key)
            current_vote_name_json = obj.get()['Body'].read().decode('utf-8')
            return json.loads(current_vote_name_json)
        except Exception as e:
            # Handle any exceptions
            return ''

    def set_current_vote_name(self, value):
        # Implement S3-based setter for current_vote_name
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.current_vote_name_key)
            obj.put(Body=json.dumps(value))
        except Exception as e:
            # Handle any exceptions
            pass

    def get_currently_in_a_voting_session(self):
        # Implement S3-based getter for currently_in_a_voting_session
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.currently_in_a_voting_session_key)
            currently_in_a_voting_session_json = obj.get()['Body'].read().decode('utf-8')
            return json.loads(currently_in_a_voting_session_json)
        except Exception as e:
            # Handle any exceptions
            return False

    def set_currently_in_a_voting_session(self, value):
        # Implement S3-based setter for currently_in_a_voting_session
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.currently_in_a_voting_session_key)
            obj.put(Body=json.dumps(value))
        except Exception as e:
            # Handle any exceptions
            pass

    def get_members(self)-> Dict[str, Voter]:
        # Implement S3-based getter for members
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.members_key)
            members_json = obj.get()['Body'].read().decode('utf-8')
            members_data = json.loads(members_json)
            # Deserialize members_data into a Dict[str, Voter]
            members = {key: Voter(name=voter['name'], sms_number=key) for key, voter in members_data.items()}
            return members
        except Exception as e:
            # Handle any exceptions
            return {}

    def set_members(self, value):
        # Implement S3-based setter for members
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.members_key)
            value = {key: voter.toJSON() for key, voter in value.items()}
            obj.put(Body=json.dumps(value))
        except Exception as e:
            # Handle any exceptions
            pass

    def load_members(self):
        self.members = {}
        with open(self.file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name']
                number = row['number']
                self.members[number] = Voter(name, number)
        self.set_members(self.members)

class PersisterGlobalVariables(Persister):
    '''
    Persister implementation using Global Variables
    '''

    file_path = '../members.csv'

    def __init__(self, use_db=False):
        self.use_db = use_db
        self.currently_in_a_voting_session = False
        self.current_vote_name = ''
        self.vote_log = {}
        self.members = {}

    def get_vote_log(self)-> Dict[str,Vote]:
        return self.vote_log

    def add_to_vote_log(self,key,value):
        self.vote_log[key] = value

    def clear_vote_log(self):
        self.vote_log = {}

    def get_current_vote_name(self):
        return self.current_vote_name

    def set_current_vote_name(self, value):
        self.current_vote_name = value

    def get_currently_in_a_voting_session(self):
        return self.currently_in_a_voting_session

    def set_currently_in_a_voting_session(self, value):
        self.currently_in_a_voting_session = value

    def load_members(self):
        self.members = {}
        with open(self.file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name']
                number = row['number']
                self.members[number] = Voter(name, number)
        return self.members

    def get_members(self)-> Dict[str, Voter]:
        return self.members