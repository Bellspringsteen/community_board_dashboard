import unittest
from app.VoteClass import Vote
from app.VoterClass import Voter
from app.VoteOptionsEnum import VoteOptions
from typing import Union

class TestVoteClass(unittest.TestCase):

    def test_vote_init_and_attributes(self):
        voter = Voter(name="Test Voter", sms_number="123")

        # Test with VoteOptions
        vote_option_instance = Vote(voter=voter, voters_vote=VoteOptions.YES)
        self.assertIsInstance(vote_option_instance.voter, Voter)
        self.assertEqual(vote_option_instance.voter.name, "Test Voter")
        self.assertEqual(vote_option_instance.voters_vote, VoteOptions.YES)

        # Test with string (candidate name)
        candidate_name = "Alice"
        vote_string_instance = Vote(voter=voter, voters_vote=candidate_name)
        self.assertIsInstance(vote_string_instance.voter, Voter)
        self.assertEqual(vote_string_instance.voter.name, "Test Voter")
        self.assertEqual(vote_string_instance.voters_vote, candidate_name)
        self.assertIsInstance(vote_string_instance.voters_vote, str)

    def test_vote_to_json(self):
        voter = Voter(name="Test Voter", sms_number="123")

        # Test with VoteOptions
        vote_option = VoteOptions.YES
        vote_instance_option = Vote(voter=voter, voters_vote=vote_option)
        expected_json_option = {
            'voter': "Test Voter",
            'votes_vote': "Yes"  # Enum .value
        }
        self.assertEqual(vote_instance_option.toJSON(), expected_json_option)

        # Test with string (candidate name)
        candidate_name = "Alice"
        vote_instance_string = Vote(voter=voter, voters_vote=candidate_name)
        expected_json_string = {
            'voter': "Test Voter",
            'votes_vote': "Alice" # Direct string
        }
        self.assertEqual(vote_instance_string.toJSON(), expected_json_string)

    def test_vote_type_hinting(self):
        # This test is more conceptual for static analysis,
        # but we can check instance types
        voter = Voter(name="Test Voter", sms_number="123")

        vote_with_enum = Vote(voter, VoteOptions.NO)
        self.assertTrue(isinstance(vote_with_enum.voters_vote, (VoteOptions, str)))
        self.assertIsInstance(vote_with_enum.voters_vote, VoteOptions)

        vote_with_str = Vote(voter, "Bob")
        self.assertTrue(isinstance(vote_with_str.voters_vote, (VoteOptions, str)))
        self.assertIsInstance(vote_with_str.voters_vote, str)

if __name__ == '__main__':
    unittest.main()
