import unittest
from unittest.mock import MagicMock, patch
import json

# Before importing main, set up mocks for its global persister and votelogger
# This is one way to ensure main.py uses our mocks when its functions are called
mock_persister_instance = MagicMock()
mock_votelogger_instance = MagicMock()

# Apply patches to the main module where persister and votelogger are defined
# Adjust 'app.main.persister' and 'app.main.votelogger' if their definition location is different
# For example, if they are PersisterS3() directly in main.py, you patch that class.
# If main.py is `from app.PersisterClass import PersisterS3` and then `persister = PersisterS3()`,
# you'd patch 'app.main.PersisterS3' to return your mock_persister_instance.

# Assuming main.py has:
# from PersisterClass import PersisterS3
# persister = PersisterS3()
# from VoteLoggingClass import S3VoteLoggingClass
# votelogger = S3VoteLoggingClass()

# We will patch the instances directly in the main module after import,
# or patch the classes if instantiation happens inside functions we test.
# For global instances, it's often easier to patch them after the module is loaded.

# Import main after setting up the stage for patching, or use inline patching in test methods.
# For simplicity with module-level instances, we often patch *before* import or use a more
# sophisticated loading mechanism if the module initializes these on import.
# A common pattern is to use @patch decorators on test methods or classes.

# Let's try patching the module's global variables directly within tests or setUp.
# For now, we prepare the mocks. The actual patching will occur in test methods or setUp.

from app import main  # Import the module to be tested
from app.VoteOptionsEnum import VoteOptions
from app.VoteClass import Vote
from app.VoterClass import Voter
from twilio.twiml.messaging_response import MessagingResponse # For checking response types


class TestMainApiStartVoting(unittest.TestCase):
    @patch('app.main.persister', new=mock_persister_instance) # Patch the global persister in main.py
    def test_api_start_voting_resolution(self):
        mock_persister_instance.reset_mock() # Reset mock for this test
        title = "Test Resolution Vote"
        community_board = "cb1"

        main.api_start_voting(title=title, community_board=community_board, vote_type="RESOLUTION")

        mock_persister_instance.set_current_vote_name.assert_called_once_with(title, community_board)
        mock_persister_instance.set_vote_type.assert_called_once_with("RESOLUTION", community_board)
        mock_persister_instance.set_election_candidates.assert_called_once_with([], community_board)
        mock_persister_instance.set_currently_in_a_voting_session.assert_called_once_with(True, community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    def test_api_start_voting_election(self):
        mock_persister_instance.reset_mock()
        title = "Test Election Vote"
        community_board = "cb2"
        candidates = ["Alice", "Bob"]

        main.api_start_voting(title=title, community_board=community_board, vote_type="ELECTION", candidates=candidates)

        mock_persister_instance.set_current_vote_name.assert_called_once_with(title, community_board)
        mock_persister_instance.set_vote_type.assert_called_once_with("ELECTION", community_board)
        mock_persister_instance.set_election_candidates.assert_called_once_with(candidates, community_board)
        mock_persister_instance.set_currently_in_a_voting_session.assert_called_once_with(True, community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    def test_api_start_voting_election_no_candidates_uses_default_none(self):
        # This test ensures that if vote_type is ELECTION but candidates is None (e.g. not provided by flask app if logic error),
        # it still passes None to set_election_candidates, relying on Persister's logic (though our main.py adds specific handling)
        # The main.api_start_voting function *itself* ensures candidates becomes [] if vote_type is RESOLUTION.
        # If vote_type is ELECTION and candidates is None, it passes None along.
        mock_persister_instance.reset_mock()
        title = "Test Election Vote No Cands"
        community_board = "cb3"

        main.api_start_voting(title=title, community_board=community_board, vote_type="ELECTION", candidates=None)

        mock_persister_instance.set_current_vote_name.assert_called_once_with(title, community_board)
        mock_persister_instance.set_vote_type.assert_called_once_with("ELECTION", community_board)
        # main.py's api_start_voting: if vote_type == "ELECTION" and candidates: ...
        # So if candidates is None, set_election_candidates is called with None.
        mock_persister_instance.set_election_candidates.assert_called_once_with(None, community_board)
        mock_persister_instance.set_currently_in_a_voting_session.assert_called_once_with(True, community_board)


class TestMainGetVoteFromString(unittest.TestCase):
    @patch('app.main.persister', new=mock_persister_instance)
    def test_get_vote_from_string_resolution(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_res_test"
        mock_persister_instance.get_vote_type.return_value = "RESOLUTION"

        self.assertEqual(main.get_vote_from_string("yes", community_board), VoteOptions.YES)
        self.assertEqual(main.get_vote_from_string("YES", community_board), VoteOptions.YES)
        self.assertEqual(main.get_vote_from_string("no", community_board), VoteOptions.NO)
        self.assertEqual(main.get_vote_from_string("No ", community_board), VoteOptions.NO) # Test trimming/cleaning if any
        self.assertEqual(main.get_vote_from_string("abstain", community_board), VoteOptions.ABSTAIN)
        self.assertEqual(main.get_vote_from_string("Abstain", community_board), VoteOptions.ABSTAIN)
        self.assertEqual(main.get_vote_from_string("cause", community_board), VoteOptions.CAUSE)
        self.assertEqual(main.get_vote_from_string("Cause", community_board), VoteOptions.CAUSE)
        self.assertIsNone(main.get_vote_from_string("invalid", community_board))
        self.assertIsNone(main.get_vote_from_string("yess", community_board))

        mock_persister_instance.get_vote_type.assert_called_with(community_board) # Called each time

    @patch('app.main.persister', new=mock_persister_instance)
    def test_get_vote_from_string_election(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_elec_test"
        candidates = ["Alice Smith", "Bob Johnson", "Charlie Brown"]

        mock_persister_instance.get_vote_type.return_value = "ELECTION"
        mock_persister_instance.get_election_candidates.return_value = candidates

        self.assertEqual(main.get_vote_from_string("Alice Smith", community_board), "Alice Smith")
        self.assertEqual(main.get_vote_from_string("alice smith", community_board), "Alice Smith") # Case-insensitive match
        self.assertEqual(main.get_vote_from_string("Bob Johnson", community_board), "Bob Johnson")
        self.assertEqual(main.get_vote_from_string("Charlie Brown ", community_board), "Charlie Brown") # Test with trailing space
        self.assertIsNone(main.get_vote_from_string("David", community_board)) # Non-candidate
        self.assertIsNone(main.get_vote_from_string("Alice", community_board)) # Partial match not enough

        # Verify get_vote_type and get_election_candidates were called
        mock_persister_instance.get_vote_type.assert_called_with(community_board)
        mock_persister_instance.get_election_candidates.assert_called_with(community_board)


class TestMainSummarizeVotes(unittest.TestCase):
    @patch('app.main.persister', new=mock_persister_instance)
    def test_summarize_votes_resolution(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_sum_res"
        mock_persister_instance.get_vote_type.return_value = "RESOLUTION"

        voter1 = Voter("Voter1", "1")
        voter2 = Voter("Voter2", "2")
        voter3 = Voter("Voter3", "3")

        vote_log_data = {
            "1": Vote(voter1, VoteOptions.YES),
            "2": Vote(voter2, VoteOptions.NO),
            "3": Vote(voter3, VoteOptions.YES),
        }
        mock_persister_instance.get_vote_log.return_value = vote_log_data

        summary = main.summarize_votes(community_board)

        self.assertIn(VoteOptions.YES, summary)
        self.assertIn(VoteOptions.NO, summary)
        self.assertIn(VoteOptions.ABSTAIN, summary)
        self.assertIn(VoteOptions.CAUSE, summary)

        self.assertEqual(len(summary[VoteOptions.YES]), 2)
        self.assertEqual(len(summary[VoteOptions.NO]), 1)
        self.assertEqual(len(summary[VoteOptions.ABSTAIN]), 0)

        # Check if voter details are correctly placed (based on toJSON output)
        self.assertTrue(any(v['voter'] == "Voter1" for v in summary[VoteOptions.YES]))
        self.assertTrue(any(v['voter'] == "Voter3" for v in summary[VoteOptions.YES]))
        self.assertTrue(any(v['voter'] == "Voter2" for v in summary[VoteOptions.NO]))

        mock_persister_instance.get_vote_type.assert_called_once_with(community_board)
        mock_persister_instance.get_vote_log.assert_called_once_with(community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    def test_summarize_votes_election(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_sum_elec"
        candidates = ["CandidateX", "CandidateY"]

        mock_persister_instance.get_vote_type.return_value = "ELECTION"
        mock_persister_instance.get_election_candidates.return_value = candidates

        voter_alice = Voter("Alice", "sms_alice")
        voter_bob = Voter("Bob", "sms_bob")
        voter_charlie = Voter("Charlie", "sms_charlie")

        vote_log_data = {
            "sms_alice": Vote(voter_alice, "CandidateX"),
            "sms_bob": Vote(voter_bob, "CandidateY"),
            "sms_charlie": Vote(voter_charlie, "CandidateX"),
        }
        mock_persister_instance.get_vote_log.return_value = vote_log_data

        summary = main.summarize_votes(community_board)

        self.assertIn("CandidateX", summary)
        self.assertIn("CandidateY", summary)
        self.assertEqual(len(summary["CandidateX"]), 2)
        self.assertEqual(len(summary["CandidateY"]), 1)

        self.assertTrue(any(v['voter'] == "Alice" for v in summary["CandidateX"]))
        self.assertTrue(any(v['voter'] == "Charlie" for v in summary["CandidateX"]))
        self.assertTrue(any(v['voter'] == "Bob" for v in summary["CandidateY"]))

        mock_persister_instance.get_vote_type.assert_called_once_with(community_board)
        mock_persister_instance.get_election_candidates.assert_called_once_with(community_board)
        mock_persister_instance.get_vote_log.assert_called_once_with(community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    def test_summarize_votes_election_no_votes_for_candidate(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_sum_elec_novote"
        candidates = ["CandidateA", "CandidateB", "CandidateC"]

        mock_persister_instance.get_vote_type.return_value = "ELECTION"
        mock_persister_instance.get_election_candidates.return_value = candidates

        voter_dave = Voter("Dave", "sms_dave")
        vote_log_data = {
            "sms_dave": Vote(voter_dave, "CandidateA"),
        }
        mock_persister_instance.get_vote_log.return_value = vote_log_data
        summary = main.summarize_votes(community_board)

        self.assertEqual(len(summary["CandidateA"]), 1)
        self.assertEqual(len(summary["CandidateB"]), 0) # Should exist as a key with empty list
        self.assertEqual(len(summary["CandidateC"]), 0) # Should exist as a key with empty list


class TestMainGetSummary(unittest.TestCase):
    @patch('app.main.persister', new=mock_persister_instance)
    @patch('app.main.summarize_votes') # Mock the internal call to summarize_votes
    def test_get_summary_resolution(self, mock_summarize_votes):
        mock_persister_instance.reset_mock()
        community_board = "cb_getsum_res"
        vote_title = "Resolution XYZ"

        mock_persister_instance.get_vote_type.return_value = "RESOLUTION"
        mock_persister_instance.get_current_vote_name.return_value = vote_title

        # Mock the output of summarize_votes directly
        mock_summary_data = {
            VoteOptions.YES: [{'voter': 'Voter1'}, {'voter': 'Voter3'}],
            VoteOptions.NO: [{'voter': 'Voter2'}],
            VoteOptions.ABSTAIN: [],
            VoteOptions.CAUSE: [],
        }
        mock_summarize_votes.return_value = mock_summary_data

        summary_text = main.get_summary(community_board)

        self.assertIn(f'Vote Summary for {vote_title}', summary_text)
        self.assertIn('2 yes votes', summary_text)
        self.assertIn('1 no votes', summary_text)
        self.assertIn('0 abstain votes', summary_text)
        self.assertIn('Voter1 voted Yes', summary_text)
        self.assertIn('Voter2 voted No', summary_text)
        self.assertIn('Voter3 voted Yes', summary_text)

        mock_persister_instance.get_vote_type.assert_called_once_with(community_board)
        mock_persister_instance.get_current_vote_name.assert_called_once_with(community_board)
        mock_summarize_votes.assert_called_once_with(community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    @patch('app.main.summarize_votes')
    def test_get_summary_election(self, mock_summarize_votes):
        mock_persister_instance.reset_mock()
        community_board = "cb_getsum_elec"
        vote_title = "Election ABC"
        candidates = ["CandidateX", "CandidateY"]

        mock_persister_instance.get_vote_type.return_value = "ELECTION"
        mock_persister_instance.get_election_candidates.return_value = candidates
        mock_persister_instance.get_current_vote_name.return_value = vote_title

        mock_summary_data = {
            "CandidateX": [{'voter': 'Alice'}, {'voter': 'Charlie'}],
            "CandidateY": [{'voter': 'Bob'}],
        }
        mock_summarize_votes.return_value = mock_summary_data

        summary_text = main.get_summary(community_board)

        self.assertIn(f'Vote Summary for {vote_title}', summary_text)
        self.assertIn('2 votes for CandidateX', summary_text)
        self.assertIn('1 votes for CandidateY', summary_text)
        self.assertIn('Alice voted for CandidateX', summary_text)
        self.assertIn('Bob voted for CandidateY', summary_text)
        self.assertIn('Charlie voted for CandidateX', summary_text)

        mock_persister_instance.get_vote_type.assert_called_once_with(community_board)
        mock_persister_instance.get_election_candidates.assert_called_once_with(community_board)
        mock_persister_instance.get_current_vote_name.assert_called_once_with(community_board)
        mock_summarize_votes.assert_called_once_with(community_board)


class TestMainParseIncomingText(unittest.TestCase):

    def setUp(self):
        # Reset mocks before each test in this class
        mock_persister_instance.reset_mock()
        mock_votelogger_instance.reset_mock()

        # Default mock behaviors good for most tests
        mock_persister_instance.get_members.return_value = {"+1112223333": Voter("Test User", "+1112223333")}
        mock_persister_instance.get_currently_in_a_voting_session.return_value = True
        mock_persister_instance.get_current_vote_name.return_value = "Current Vote Name"

    @patch('app.main.persister', new=mock_persister_instance)
    @patch('app.main.votelogger', new=mock_votelogger_instance)
    @patch('app.main.get_vote_from_string') # Mock this helper function too
    def test_parse_incoming_text_resolution_vote(self, mock_get_vote_from_string):
        community_board = "cb_parse_res"
        incoming_number = "+1112223333"
        incoming_msg = "yes"

        mock_persister_instance.get_vote_type.return_value = "RESOLUTION"
        mock_get_vote_from_string.return_value = VoteOptions.YES # Simulate successful vote parsing

        response_str = main.parse_incoming_text(incoming_number, incoming_msg, community_board)

        # Check TwiML response
        self.assertIn('<Message>', response_str)
        self.assertIn('Your vote has been recorded, you voted Yes for resolution Current Vote Name', response_str)

        # Check that persister.add_to_vote_log was called correctly
        mock_persister_instance.add_to_vote_log.assert_called_once()
        args, kwargs = mock_persister_instance.add_to_vote_log.call_args
        self.assertEqual(kwargs['key'], incoming_number)
        self.assertEqual(kwargs['community_board'], community_board)
        logged_vote_object = kwargs['value']
        self.assertIsInstance(logged_vote_object, Vote)
        self.assertEqual(logged_vote_object.voter.sms_number, incoming_number)
        self.assertEqual(logged_vote_object.voters_vote, VoteOptions.YES)

        mock_votelogger_instance.log_raw_vote_to_file.assert_called_once()
        mock_get_vote_from_string.assert_called_once_with(incoming_msg, community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    @patch('app.main.votelogger', new=mock_votelogger_instance)
    @patch('app.main.get_vote_from_string')
    def test_parse_incoming_text_election_vote_success(self, mock_get_vote_from_string):
        community_board = "cb_parse_elec"
        incoming_number = "+1112223333"
        candidate_name = "Alice Candidate"
        incoming_msg = candidate_name # User texts candidate name

        mock_persister_instance.get_vote_type.return_value = "ELECTION"
        # mock_persister_instance.get_election_candidates.return_value = [candidate_name, "Bob Candidate"] # Not directly used by parse_incoming_text if get_vote_from_string handles it
        mock_get_vote_from_string.return_value = candidate_name # Simulate successful vote parsing

        response_str = main.parse_incoming_text(incoming_number, incoming_msg, community_board)

        self.assertIn('<Message>', response_str)
        self.assertIn(f'Your vote has been recorded, you voted for {candidate_name} for election Current Vote Name', response_str)

        mock_persister_instance.add_to_vote_log.assert_called_once()
        args, kwargs = mock_persister_instance.add_to_vote_log.call_args
        logged_vote_object = kwargs['value']
        self.assertEqual(logged_vote_object.voters_vote, candidate_name)
        self.assertIsInstance(logged_vote_object.voters_vote, str)

        mock_votelogger_instance.log_raw_vote_to_file.assert_called_once()
        mock_get_vote_from_string.assert_called_once_with(incoming_msg, community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    @patch('app.main.votelogger', new=mock_votelogger_instance)
    @patch('app.main.get_vote_from_string')
    def test_parse_incoming_text_election_vote_invalid_candidate(self, mock_get_vote_from_string):
        community_board = "cb_parse_elec_invalid"
        incoming_number = "+1112223333"
        incoming_msg = "NonExistent Candidate"

        mock_persister_instance.get_vote_type.return_value = "ELECTION"
        # mock_persister_instance.get_election_candidates.return_value = ["Alice", "Bob"] # For get_vote_from_string's internal logic
        mock_get_vote_from_string.return_value = None # Simulate candidate not found

        response_str = main.parse_incoming_text(incoming_number, incoming_msg, community_board)

        self.assertIn(main.INVALID_INPUT_MESSAGE, response_str)
        mock_persister_instance.add_to_vote_log.assert_not_called() # Vote should not be logged
        mock_votelogger_instance.log_raw_vote_to_file.assert_called_once() # Raw attempt is logged

    def test_parse_incoming_text_not_in_voting_session(self):
        mock_persister_instance.get_currently_in_a_voting_session.return_value = False
        response_str = main.parse_incoming_text("+1112223333", "yes", "cb_parse_notin")
        self.assertIn(main.NOT_VOTING_MESSAGE, response_str)

    def test_parse_incoming_text_invalid_number(self):
        mock_persister_instance.get_members.return_value = {} # No members registered
        response_str = main.parse_incoming_text("+4445556666", "yes", "cb_parse_invalidnum")
        self.assertIn(main.NOT_VALID_NUMBER_MESSAGE, response_str)

    def test_parse_incoming_text_instructions_message(self):
        response_str = main.parse_incoming_text("+1112223333", "instructions", "cb_parse_instr")
        self.assertIn(main.INSTRUCTIONS_MESSAGE, response_str)
        mock_persister_instance.add_to_vote_log.assert_not_called()


class TestMainApiIsVotingStarted(unittest.TestCase):
    @patch('app.main.persister', new=mock_persister_instance)
    def test_api_is_voting_started_resolution_type(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_isvoting_res"
        vote_name = "Resolution Vote Test"

        mock_persister_instance.get_currently_in_a_voting_session.return_value = True
        mock_persister_instance.get_current_vote_name.return_value = vote_name
        mock_persister_instance.get_vote_type.return_value = "RESOLUTION"
        # get_election_candidates should not be strictly necessary to mock if vote_type is RESOLUTION,
        # as the code logic might short-circuit, but good to be explicit.
        mock_persister_instance.get_election_candidates.return_value = []

        response = main.api_is_voting_started(community_board)

        self.assertIn("statusCode", response)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("body", response)

        body_data = json.loads(response["body"])
        self.assertTrue(body_data["isVotingStarted"])
        self.assertEqual(body_data["currentVoteName"], vote_name)
        self.assertEqual(body_data["voteType"], "RESOLUTION")
        self.assertEqual(body_data["electionCandidates"], [])

        mock_persister_instance.get_currently_in_a_voting_session.assert_called_once_with(community_board)
        mock_persister_instance.get_current_vote_name.assert_called_once_with(community_board)
        mock_persister_instance.get_vote_type.assert_called_once_with(community_board)
        # Depending on exact logic in api_is_voting_started, get_election_candidates might not be called
        # if vote_type is RESOLUTION. If it is, the call needs to be asserted.
        # Based on the provided implementation: `candidates if vote_type == "ELECTION" else []`
        # This means get_election_candidates IS called before this conditional.
        mock_persister_instance.get_election_candidates.assert_called_once_with(community_board)


    @patch('app.main.persister', new=mock_persister_instance)
    def test_api_is_voting_started_election_type(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_isvoting_elec"
        vote_name = "Election Vote Test"
        candidates = ["Candidate A", "Candidate B"]

        mock_persister_instance.get_currently_in_a_voting_session.return_value = True
        mock_persister_instance.get_current_vote_name.return_value = vote_name
        mock_persister_instance.get_vote_type.return_value = "ELECTION"
        mock_persister_instance.get_election_candidates.return_value = candidates

        response = main.api_is_voting_started(community_board)
        body_data = json.loads(response["body"])

        self.assertTrue(body_data["isVotingStarted"])
        self.assertEqual(body_data["currentVoteName"], vote_name)
        self.assertEqual(body_data["voteType"], "ELECTION")
        self.assertEqual(body_data["electionCandidates"], candidates)

        mock_persister_instance.get_election_candidates.assert_called_once_with(community_board)

    @patch('app.main.persister', new=mock_persister_instance)
    def test_api_is_voting_not_started(self):
        mock_persister_instance.reset_mock()
        community_board = "cb_isvoting_not"

        mock_persister_instance.get_currently_in_a_voting_session.return_value = False
        mock_persister_instance.get_current_vote_name.return_value = "" # Usually empty if not started
        mock_persister_instance.get_vote_type.return_value = "RESOLUTION" # Default or last state
        mock_persister_instance.get_election_candidates.return_value = []

        response = main.api_is_voting_started(community_board)
        body_data = json.loads(response["body"])

        self.assertFalse(body_data["isVotingStarted"])
        self.assertEqual(body_data["voteType"], "RESOLUTION") # Should still report type
        self.assertEqual(body_data["electionCandidates"], [])


class TestMainApiStopVoting(unittest.TestCase):
    @patch('app.main.persister', new=mock_persister_instance)
    @patch('app.main.votelogger', new=mock_votelogger_instance)
    @patch('app.main.get_summary') # Mock this helper function call
    def test_api_stop_voting(self, mock_get_summary):
        mock_persister_instance.reset_mock()
        mock_votelogger_instance.reset_mock()
        mock_get_summary.reset_mock() # Ensure this is also reset

        community_board = "cb_stop_vote"
        current_vote_name = "Vote To Be Stopped"
        summary_text_output = "This is the vote summary."

        mock_persister_instance.get_current_vote_name.return_value = current_vote_name
        mock_get_summary.return_value = summary_text_output

        main.api_stop_voting(community_board)

        # Verify votelogger was called
        mock_votelogger_instance.log_vote_summary_to_file.assert_called_once_with(
            current_vote_name=current_vote_name,
            summary=summary_text_output,
            community_board=community_board
        )

        # Verify persister state changes
        mock_persister_instance.set_current_vote_name.assert_called_once_with('', community_board)
        mock_persister_instance.set_currently_in_a_voting_session.assert_called_once_with(False, community_board)
        mock_persister_instance.clear_vote_log.assert_called_once_with(community_board)

        # Verify new calls for resetting vote type and candidates
        mock_persister_instance.set_vote_type.assert_called_once_with("RESOLUTION", community_board)
        mock_persister_instance.set_election_candidates.assert_called_once_with([], community_board)

        mock_get_summary.assert_called_once_with(community_board)


if __name__ == '__main__':
    # This allows running tests directly from this file
    unittest.main()
