class Persister:
    '''
    Responsible for persisting vote, member, etc data.
    Will point to either a DynamoDB or a Global variable persisting
    '''

    def __init__(self, use_db=False):
        self.use_db = use_db
        self.currently_in_a_voting_session = False

    def get_vote_log(self):
        return vote_log

    def set_vote_log(self, value):
        global vote_log
        vote_log = value

    def get_current_vote_name(self):
        return current_vote_name

    def set_current_vote_name(self, value):
        global current_vote_name
        current_vote_name = value

    def get_currently_in_a_voting_session(self):
        return self.currently_in_a_voting_session

    def set_currently_in_a_voting_session(self, value):
        self.currently_in_a_voting_session = value

    def get_members(self):
        return members

    def set_members(self, value):
        global members
        members = value
