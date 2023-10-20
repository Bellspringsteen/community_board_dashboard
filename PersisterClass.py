import csv 
from VoterClass import Voter

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

    def get_members(self):
        pass

class PersisterDynamoDB(Persister):
    '''
    Persister implementation using DynamoDB
    '''

    def __init__(self, dynamodb_resource):
        super().__init__()
        self.dynamodb_resource = dynamodb_resource

    def get_vote_log(self):
        # Implement DynamoDB-based getter for vote_log
        pass

    def set_vote_log(self, value):
        # Implement DynamoDB-based setter for vote_log
        pass

    def get_current_vote_name(self):
        # Implement DynamoDB-based getter for current_vote_name
        pass

    def set_current_vote_name(self, value):
        # Implement DynamoDB-based setter for current_vote_name
        pass

    def get_currently_in_a_voting_session(self):
        # Implement DynamoDB-based getter for currently_in_a_voting_session
        pass

    def set_currently_in_a_voting_session(self, value):
        # Implement DynamoDB-based setter for currently_in_a_voting_session
        pass

    def get_members(self):
        # Implement DynamoDB-based getter for members
        pass

    def set_members(self, value):
        # Implement DynamoDB-based setter for members
        pass


class PersisterGlobalVariables(Persister):
    '''
    Persister implementation using Global Variables
    '''

    file_path = './members.csv'

    def __init__(self, use_db=False):
        self.use_db = use_db
        self.currently_in_a_voting_session = False
        self.current_vote_name = ''
        self.vote_log = {}
        self.members = {}

    def get_vote_log(self):
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

    def get_members(self):
        return self.members