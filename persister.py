class Persister:
    '''
    Responsible for persisting vote, member, etc data.
    Will point to either a DynamoDB or a Global variable persisting
    '''

    def __init__(self, use_db=False):
        self.use_db = use_db
        self.currently_in_a_voting_session = False
        self.current_vote_name = ''
        self.vote_log = {}

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

    def get_members(self):
        return members

    def set_members(self, value):
        global members
        members = value
