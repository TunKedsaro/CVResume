from datetime import datetime,timezone,timedelta
from core.helper import Helper
import copy

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
    
    
class GlobalAggregator(Helper):
    def __init__(self,SectionScoreAggregator_output:list):
        self.section_outputs = SectionScoreAggregator_output
        self.timestamp       = str(datetime.now(tz=(timezone(timedelta(hours=7)))))
        self.model_config    = Helper.load_yaml("src/config/model.yaml")     # should include model name
        self.weight_config   = Helper.load_yaml("src/config/weight.yaml")    # includes weights + version
        self.prompt_config   = Helper.load_yaml("src/config/prompt.yaml")    # includes prompt version
    def fn1(self):
        weights = self.weight_config["weights"]
        contribution = {}
        total = 0.0
        for section_data in self.section_outputs:
            section_name    = section_data["section"]
            total_score     = section_data["total_score"]
            section_weight  = weights[section_name]["section_weight"]
            section_contrib = total_score * section_weight
            contribution[section_name] = {
                "section_total": total_score,
                "section_weight": section_weight,
                "contribution": Helper.fop(section_contrib)
            }
            total = total + section_contrib
        return {
            "final_resume_score":Helper.fop(total),
            "section_contribution":contribution
        }
    def fn2(self):
        details = {}
        for section_data in self.section_outputs:
            details[section_data["section"]] = {
                'total_score':section_data['total_score'],
                'scores':section_data['scores']
            }
        return details
    def fn3(self):
        return {
            "model_name": self.model_config['model']['generation_model'],
            "timestamp": self.timestamp,
            "weights_version": self.weight_config.get("version", "unknown"),
            "prompt_version": self.prompt_config.get("version", "unknown")
        }
    def fn0(self):
        conclution_part = self.fn1()
        detail_part     = self.fn2()
        metadata_part   = self.fn3()
        # return {
        #     "conclution":conclution_part,
        #     "section_detail":detail_part,
        #     "metadata":metadata_part
        # }
        return {
            "conclution":conclution_part,
            "section_detail":detail_part,
            "metadata":metadata_part
        }
    


