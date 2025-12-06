import copy
from core.helper import Helper

class SectionScoreAggregator(Helper):
    def __init__(self):
        self.config          = self.load_yaml("src/config/weight.yaml")         # config
    def aggregate(self,llm_output:dict):
        self.llm_output      = llm_output             # op
        self.section         = llm_output["section"]  # Get section
        self.section_weights = self.config["weights"][self.section]  # config["weights"][section_key][criteria]
        ddict = {}
        total = 0.0
        # Protect multiple mutation when we run more than one time
        scores_copy = copy.deepcopy(self.llm_output["scores"])
        for criteria, body in scores_copy.items():
            raw = body["score"]
            w   = self.section_weights[criteria]
            weighted = raw / 5 * w
            body["score"] = weighted
            ddict[criteria] = body
            total = total + weighted
        return {
            "section": self.section,
            "total_score":total,
            "scores":ddict
        }