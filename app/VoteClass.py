from VoterClass import Voter
from VoteOptionsEnum import VoteOptions # Make sure this is here
from typing import Union

class Vote:
  voters_vote: Union[VoteOptions, str]
  def __init__(self, voter:Voter, voters_vote: Union[VoteOptions, str]):
    self.voter:Voter = voter
    self.voters_vote = voters_vote

  def __str__(self):
    return f"{self.voter.name} voted {self.voters_vote})" # Corrected __str__ for clarity
  
  def toJSON(self):
    vote_value = ''
    if isinstance(self.voters_vote, VoteOptions):
        vote_value = self.voters_vote.value
    else:
        vote_value = self.voters_vote # It's a string (candidate name)
    return {
        'voter': self.voter.name,
        'votes_vote': vote_value
    }