import json

class ProposalStorage:
    def __init__(self):
        self.proposal = {}
        self.order = []
    
    def add_proposal(self, proposal_id: str, proposal: dict):
        self.proposal[proposal_id] = proposal

    def clear_proposals(self):
        self.proposal = {}
    
    def __str__(self):
        return json.dumps(self.proposal, indent=4)