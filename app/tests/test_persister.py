import unittest
from app.PersisterClass import PersisterGlobalVariables
from app.VoteClass import Vote
from app.VoterClass import Voter
from app.VoteOptionsEnum import VoteOptions

class TestPersisterGlobalVariables(unittest.TestCase):

    def setUp(self):
        self.persister = PersisterGlobalVariables()
        self.community_board = "test_board"

    def test_set_and_get_vote_type(self):
        self.persister.set_vote_type("ELECTION", self.community_board)
        self.assertEqual(self.persister.get_vote_type(self.community_board), "ELECTION")

        self.persister.set_vote_type("RESOLUTION", self.community_board)
        self.assertEqual(self.persister.get_vote_type(self.community_board), "RESOLUTION")

    def test_set_and_get_election_candidates(self):
        candidates = ["Alice", "Bob", "Charlie"]
        self.persister.set_election_candidates(candidates, self.community_board)
        self.assertEqual(self.persister.get_election_candidates(self.community_board), candidates)

        self.persister.set_election_candidates([], self.community_board)
        self.assertEqual(self.persister.get_election_candidates(self.community_board), [])

    def test_get_vote_log_conceptual(self):
        # This test ensures that get_vote_log returns what was added,
        # which is important when votes can be strings (candidate names).
        voter1 = Voter("Voter One", "111")
        voter2 = Voter("Voter Two", "222")

        vote1_option = Vote(voter1, VoteOptions.YES)
        vote2_candidate = Vote(voter2, "CandidateX")

        self.persister.add_to_vote_log(voter1.sms_number, vote1_option, self.community_board)
        self.persister.add_to_vote_log(voter2.sms_number, vote2_candidate, self.community_board)

        vote_log = self.persister.get_vote_log(self.community_board)
        self.assertEqual(len(vote_log), 2)
        self.assertEqual(vote_log[voter1.sms_number].voters_vote, VoteOptions.YES)
        self.assertEqual(vote_log[voter2.sms_number].voters_vote, "CandidateX")
        self.assertIsInstance(vote_log[voter2.sms_number].voters_vote, str)

    def test_default_vote_type_and_candidates(self):
        # Test default values upon initialization if not explicitly set by other tests first
        # For PersisterGlobalVariables, these are set in __init__
        new_persister = PersisterGlobalVariables()
        self.assertEqual(new_persister.get_vote_type(self.community_board), "RESOLUTION")
        self.assertEqual(new_persister.get_election_candidates(self.community_board), [])

from unittest.mock import patch, MagicMock
import json
from app.PersisterClass import PersisterS3

class TestPersisterS3(unittest.TestCase):
    def setUp(self):
        self.community_board = "test_s3_board"
        # Patch boto3.resource and boto3.client for all tests in this class
        self.patcher_resource = patch('boto3.resource')
        self.patcher_client = patch('boto3.client')
        self.mock_s3_resource = self.patcher_resource.start()
        self.mock_s3_client = self.patcher_client.start()

        # Configure the mock S3 resource and client
        self.mock_s3_object = MagicMock()
        self.mock_s3_resource.return_value.Object.return_value = self.mock_s3_object
        self.mock_s3_client_instance = self.mock_s3_client.return_value

        self.persister = PersisterS3()
         # Override bucket name for tests if necessary, or ensure persister uses a test bucket
        self.persister.bucket_name = 'test-bucket'


    def tearDown(self):
        self.patcher_resource.stop()
        self.patcher_client.stop()

    def test_get_vote_type_s3(self):
        expected_vote_type = "ELECTION"
        s3_key = f'/{self.community_board}/{self.persister.vote_type_key}'

        # Simulate S3 get_object response
        self.mock_s3_object.get.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=json.dumps(expected_vote_type).encode('utf-8')))
        }

        vote_type = self.persister.get_vote_type(self.community_board)

        self.mock_s3_resource.return_value.Object.assert_called_with(self.persister.bucket_name, s3_key)
        self.mock_s3_object.get.assert_called_once()
        self.assertEqual(vote_type, expected_vote_type)

    def test_get_vote_type_s3_default_resolution(self):
        s3_key = f'/{self.community_board}/{self.persister.vote_type_key}'
        # Simulate an error (e.g., object not found)
        self.mock_s3_object.get.side_effect = Exception("S3 error")

        vote_type = self.persister.get_vote_type(self.community_board)

        self.mock_s3_resource.return_value.Object.assert_called_with(self.persister.bucket_name, s3_key)
        self.assertEqual(vote_type, "RESOLUTION") # Default value

    def test_set_vote_type_s3(self):
        vote_type_to_set = "ELECTION"
        s3_key = f'/{self.community_board}/{self.persister.vote_type_key}'

        self.persister.set_vote_type(vote_type_to_set, self.community_board)

        self.mock_s3_resource.return_value.Object.assert_called_with(self.persister.bucket_name, s3_key)
        self.mock_s3_object.put.assert_called_once_with(Body=json.dumps(vote_type_to_set))

    def test_get_election_candidates_s3(self):
        expected_candidates = ["CandidateA", "CandidateB"]
        s3_key = f'/{self.community_board}/{self.persister.election_candidates_key}'

        self.mock_s3_object.get.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=json.dumps(expected_candidates).encode('utf-8')))
        }

        candidates = self.persister.get_election_candidates(self.community_board)

        self.mock_s3_resource.return_value.Object.assert_called_with(self.persister.bucket_name, s3_key)
        self.assertEqual(candidates, expected_candidates)

    def test_get_election_candidates_s3_default_empty(self):
        s3_key = f'/{self.community_board}/{self.persister.election_candidates_key}'
        self.mock_s3_object.get.side_effect = Exception("S3 error")

        candidates = self.persister.get_election_candidates(self.community_board)

        self.mock_s3_resource.return_value.Object.assert_called_with(self.persister.bucket_name, s3_key)
        self.assertEqual(candidates, []) # Default value

    def test_set_election_candidates_s3(self):
        candidates_to_set = ["CandidateX", "CandidateY"]
        s3_key = f'/{self.community_board}/{self.persister.election_candidates_key}'

        self.persister.set_election_candidates(candidates_to_set, self.community_board)

        self.mock_s3_resource.return_value.Object.assert_called_with(self.persister.bucket_name, s3_key)
        self.mock_s3_object.put.assert_called_once_with(Body=json.dumps(candidates_to_set))

    def test_get_vote_log_s3_election_type(self):
        # Mock get_vote_type to return "ELECTION"
        self.persister.get_vote_type = MagicMock(return_value="ELECTION")

        mock_vote_data_candidate_a = {
            'voter': 'Voter A Name',
            'votes_vote': 'CandidateA' # String vote
        }
        mock_vote_data_candidate_b = {
            'voter': 'Voter B Name',
            'votes_vote': 'CandidateB' # String vote
        }

        # Simulate S3 list_objects_v2 response
        self.mock_s3_client_instance.list_objects_v2.return_value = {
            'Contents': [
                {'Key': f'{self.persister.vote_log_folder}/{self.community_board}/1234567890'},
                {'Key': f'{self.persister.vote_log_folder}/{self.community_board}/0987654321'},
            ]
        }
        # Simulate S3 get_object responses
        self.mock_s3_client_instance.get_object.side_effect = [
            {'Body': MagicMock(read=MagicMock(return_value=json.dumps(mock_vote_data_candidate_a).encode('utf-8')))},
            {'Body': MagicMock(read=MagicMock(return_value=json.dumps(mock_vote_data_candidate_b).encode('utf-8')))},
        ]

        vote_log = self.persister.get_vote_log(self.community_board)

        self.assertEqual(len(vote_log), 2)
        self.assertIn('1234567890', vote_log)
        self.assertEqual(vote_log['1234567890'].voters_vote, 'CandidateA') # Should be string
        self.assertIsInstance(vote_log['1234567890'].voters_vote, str)
        self.assertEqual(vote_log['1234567890'].voter.name, 'Voter A Name')

        self.assertIn('0987654321', vote_log)
        self.assertEqual(vote_log['0987654321'].voters_vote, 'CandidateB') # Should be string
        self.assertIsInstance(vote_log['0987654321'].voters_vote, str)
        self.assertEqual(vote_log['0987654321'].voter.name, 'Voter B Name')

        self.persister.get_vote_type.assert_called_with(self.community_board)


    def test_get_vote_log_s3_resolution_type(self):
        # Mock get_vote_type to return "RESOLUTION"
        self.persister.get_vote_type = MagicMock(return_value="RESOLUTION")

        mock_vote_data_yes = {
            'voter': 'Voter C Name',
            'votes_vote': 'Yes' # VoteOptions.YES.value
        }

        self.mock_s3_client_instance.list_objects_v2.return_value = {
            'Contents': [
                {'Key': f'{self.persister.vote_log_folder}/{self.community_board}/111222333'},
            ]
        }
        self.mock_s3_client_instance.get_object.return_value = \
            {'Body': MagicMock(read=MagicMock(return_value=json.dumps(mock_vote_data_yes).encode('utf-8')))}

        vote_log = self.persister.get_vote_log(self.community_board)

        self.assertEqual(len(vote_log), 1)
        self.assertIn('111222333', vote_log)
        self.assertEqual(vote_log['111222333'].voters_vote, VoteOptions.YES) # Should be Enum
        self.assertIsInstance(vote_log['111222333'].voters_vote, VoteOptions)
        self.assertEqual(vote_log['111222333'].voter.name, 'Voter C Name')

        self.persister.get_vote_type.assert_called_with(self.community_board)


if __name__ == '__main__':
    unittest.main()
