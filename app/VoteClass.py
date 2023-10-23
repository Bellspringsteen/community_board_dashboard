from VoterClass import Voter

class Vote:
  def __init__(self, voter:Voter, voters_vote):
    self.voter:Voter = voter
    self.voters_vote = voters_vote

  def __str__(self):
    return f"{self.voter.vote})"
  
  def toJSON(self):
    return {
        'voter': self.voter.name,
        'votes_vote': self.voters_vote.value
    }