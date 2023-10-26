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

    file_path = '../members.csv'  # TODO this is just for the first launch, remove this

    def __init__(self):
        super().__init__()
        self.s3_resource = boto3.resource('s3')
        self.s3 =  boto3.client('s3')
        self.bucket_name = 'cb-dashboard-data-store'
        self.vote_log_key = 'vote_log.json'
        self.current_vote_name_key = 'current_vote_name.json'
        self.currently_in_a_voting_session_key = 'currently_in_a_voting_session.json'
        self.members_key = 'members.json'
        self.vote_log_folder = 'vote_log'

    def get_vote_log(self) -> Dict[str, Vote]:
        vote_logs = {}

        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.vote_log_folder+'/+')
        for obj in response.get('Contents', []):
            # Get the object key (file path)
            object_key = obj['Key']

            # Fetch the object's data
            response = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
            object_data = response['Body'].read().decode('utf-8')
            # Load the object data as JSON
            try:
                data = json.loads(object_data)
            except json.JSONDecodeError:
                print(f"Error loading JSON for object: {object_key}")
                continue

            # Extract data and create the desired object structure
            sms_number = object_key.split('/')[1]
            name_to_set = data['voter']
            vote_data = data['votes_vote']
            if vote_data:
                vote_logs[sms_number] = Vote(voter=Voter(name=name_to_set,sms_number=sms_number), voters_vote=VoteOptions(vote_data))
        
        return vote_logs
        
    def add_to_vote_log(self,key,value):
        try:
            obj = self.s3_resource.Object(self.bucket_name, self.vote_log_folder+'/'+value.voter.sms_number)
            to_save = value.toJSON()
            obj.put(Body=json.dumps(to_save))
        except Exception as e:
            # Handle any exceptions
            pass

    def clear_vote_log(self):
        # List all objects with the specified prefix
        objects = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.vote_log_folder)

        # Check if the bucket has any objects
        if 'Contents' in objects:
            # Extract the object keys to be deleted
            keys = [{'Key': obj['Key']} for obj in objects['Contents']]

            # Delete the objects in batches for efficiency
            chunk_size = 1000  # You can adjust the chunk size as needed
            for i in range(0, len(keys), chunk_size):
                response = self.s3.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': keys[i:i + chunk_size]}
                )

                # Check if any objects failed to delete
                if 'Errors' in response:
                    for error in response['Errors']:
                        print(f"Error deleting object: {error['Key']} - {error['Message']}")

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