from datetime import datetime,timezone,timedelta
from core.helper import Helper
from core.llmcaller import LlmCaller
import copy
import json
class SectionScoreAggregator(Helper):
    """
    Aggregates raw LLM criterion scores for a single resume section
    into weighted scores and a section-level total score (0-5).
    Configuration:
        - src/config/weight.yaml
    Expected LLM Output Format (input):
        {
            "section": "<section_name>",
            "scores": {
                "<criterion>": {
                    "score": int,        # 0-5
                    "feedback": str
                }
            }
        }

    Output Format:
        {
            "section": "<section_name>",
            "total_score": float,
            "scores": {
                "<criterion>": {
                    "score": float,      # weighted score
                    "feedback": str
                }
            }
        }
    """
    def __init__(self):
        self.config          = self.load_yaml("src/config/weight.yaml")         # config
    def aggregate(self,llm_output:dict):
        # print(f"llm_output ->\n{llm_output}")
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
            "scores":ddict,
            "session_feedback":self.llm_output['session_feedback']
        }
    
class GlobalAggregator(LlmCaller,Helper):
    """
    Aggregates section-level evaluation results into a final resume score.
    Combines weighted section scores, detailed per-section breakdowns,
    and evaluation metadata (model, configuration versions, timestamp).
    Inputs:
        SectionScoreAggregator_output (list):
            Section-level aggregation results.
    Configurations:
        - model.yaml   : LLM model information
        - weight.yaml  : Section weights and version
        - prompt.yaml  : Prompt configuration version
    Input : 
    s1 = {
    'section': 'Experience',
    'total_score': 78.0,
    'scores': {
        'RoleRelevance':  {'score': 30.0, 'feedback': 'xxx'},
        'Length':         {'score': 8.0, 'feedback': 'yyy'},
        'Grammar':        {'score': 10.0, 'feedback': 'zzz'},
        'ContentQuality': {'score': 24.0, 'feedback': 'aaa'},
        'Completeness':   {'score': 6.0, 'feedback': 'bbb'}
            }
        }
    s2 = {
        'section': 'Profile',
        'total_score': 90.0,
        'scores': {
            'RoleRelevance':  {'score': 20.0, 'feedback': 'xxx'},
            'Length':         {'score': 10.0, 'feedback': 'yyy'},
            'Grammar':        {'score': 25.0, 'feedback': 'zzz'},
            'ContentQuality': {'score': 22.0, 'feedback': 'aaa'},
            'Completeness':   {'score': 13.0, 'feedback': 'bbb'}
                }
            }

    Output :
    Ss = {
        "conclution":{
            "final_resume_score": 82.4,
            "section_contribution":{
                "Profile":{
                    "section_total":78.0,
                    "section_weight":40,
                    "contribution":31.2
                },
                "Experience":{
                    "section_total":90.0,
                    "section_weight":10,
                    "contribution":9.0
                }
            }
        },
        "section_details":{
            "Profile":{
                "total_score":78.0,
                "scores":{
                        'RoleRelevance':  {'score': 30.0, 'feedback': 'xxx'},
                        'Length':         {'score': 8.0, 'feedback': 'yyy'},
                        'Grammar':        {'score': 10.0, 'feedback': 'zzz'},
                        'ContentQuality': {'score': 24.0, 'feedback': 'aaa'},
                        'Completeness':   {'score': 6.0, 'feedback': 'bbb'}
                }
            },
            "Experience":{
                "total_score":90.0,
                "scores":{
                        'RoleRelevance':  {'score': 20.0, 'feedback': 'xxx'},
                        'Length':         {'score': 10.0, 'feedback': 'yyy'},
                        'Grammar':        {'score': 25.0, 'feedback': 'zzz'},
                        'ContentQuality': {'score': 22.0, 'feedback': 'aaa'},
                        'Completeness':   {'score': 13.0, 'feedback': 'bbb'}
                }      
            }
        },
        "metadata":{
            "model_name":"gemini-2.5-flash",
            "timestamp": "2025-12-03T11:45:00+07:00",
            # "processing_time_ms":1234,
            # "input_tokens":1234,
            # "output_tokens":435,
            # "total_cost_usd":0.001234,
            "weights_version":"weights_v1",
            "prompt_version":"prompt_v1"
        }
    }                                                                                       

    """
    def __init__(self,SectionScoreAggregator_output:list,output_lang):
        super().__init__()    # Run Llmcaller class 
        self.section_outputs = SectionScoreAggregator_output
        self.timestamp       = str(datetime.now(tz=(timezone(timedelta(hours=7)))))
        self.model_config    = Helper.load_yaml("src/config/model.yaml")     # should include model name
        self.weight_config   = Helper.load_yaml("src/config/weight.yaml")    # includes weights + version
        self.prompt_config   = Helper.load_yaml("src/config/prompt.yaml")    # includes prompt version
        self.config_lang     = self.prompt_config['Language_output_style'][output_lang]
    def fn1(self):
        """
        Calculate the final resume score using section-level weights.
        Applies section weights to each section's total score and
        computes the overall composite resume score.
        Returns:
            dict:
                Final resume score and per-section contribution details.
        """
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
            "section_contribution":contribution,
            "globalfeedback":self.parse
        }
    def fn2(self):
        """
        Build detailed scoring results for each resume section.
        Returns:
            dict:
                Per-section total scores and criterion-level score breakdowns.
        """
        details = {}
        for section_data in self.section_outputs:
            # print(f"section_data->\n{section_data}")
            details[section_data["section"]] = {
                'total_score':section_data['total_score'],
                'scores':section_data['scores'],
                'session_feedback':section_data['session_feedback']
            }
        prompt = self.prompt_config['feedback']['globalfeedback']
        # print(f"prompt->\n{prompt}")
        self.parse,_ = self._call_raw(prompt)
        # print(self.parse)
        return details
    
    def fn3(self):
        """
        Generate metadata describing the evaluation context.
        Includes model information, configuration versions,
        and the evaluation timestamp.
        Returns:
            dict:
                Evaluation metadata.
        """
        return {
            "model_name": self.model_config['model']['generation_model'],
            "timestamp": self.timestamp,
            "weights_version": self.weight_config.get("version", "unknown"),
            "prompt_version": self.prompt_config.get("version", "unknown")
        }
    def fn0(self):
        """
        Assemble the final evaluation response.
        Combines the final resume score, detailed section results,
        and evaluation metadata into a single response payload.
        Returns:
            dict:
                Final aggregated resume evaluation result.
        """
        detail_part     = self.fn2()
        conclution_part = self.fn1()
        metadata_part   = self.fn3()

        return {
            "conclution":conclution_part,
            "section_detail":detail_part,
            "metadata":metadata_part
        }
    


