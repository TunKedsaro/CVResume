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
        self.weight_config          = self.load_yaml("src/config/weight.yaml")         # config

    def aggregate(self,llm_output:dict):
        '''
        Convert, reshape, transform output format that we got from llm
        '''
        self.llm_output   = llm_output               # Op
        self.section_name = llm_output["section"]    # Get section name such as Profile, Summary, ..., Skills
        self.section_config_scores   = self.weight_config["weights"][self.section_name]   # Get max score in weight.yaml config
        scaled_criteria_scores  = {}            # Output dictionary
        total_section_raw_score = 0.0           # Accumulate raw score from every criteria
        total_section_max_score = 0.0           # Accumulate maximum score from every criteria that posible
        scores_copy  = copy.deepcopy(llm_output["scores"])         # Protect multiple mutation when we run more than one time
        for criteria,body in scores_copy.items():  # Loop with op...
            raw_llm_score = body["score"]       # raw score for every criteria each section
            if raw_llm_score == 0:              # If LLM detect empty value then max_score should be 0 (don't calcualte it)
                max_score_from_config = 0       # score = 0 instead maximum score
            else:
                max_score_from_config = self.section_config_scores[criteria] # Max score in weight.yaml (default=10)
            scaled_score = (raw_llm_score / 5) * max_score_from_config  # raw_score/max scale score(5) x max score in weight.yaml(10)
            body["score"] = scaled_score            # Replace new scaled score in body
            scaled_criteria_scores[criteria] = body # Create new dict (Op -> S)
            total_section_raw_score = total_section_raw_score + scaled_score # Accumulate scaled raw score from each criteria in each seciton
            total_section_max_score = total_section_max_score + max_score_from_config # Accumulate full score from config file that Llm not detect 0
        return {
                "section": self.section_name,
                "total_section_raw_score":total_section_raw_score,
                "total_section_max_score":total_section_max_score,
                "scores":scaled_criteria_scores,
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

    def normalize_score_to_grade(self, total_raw_score, total_max_score):
        # print(f"total_raw_score -> {total_raw_score}")
        # print(f"total_max_score -> {total_max_score}")
        if total_max_score == 0:
            return "-"
        normalize_score = (total_raw_score / total_max_score) * 100
        # print(f"normalize_score -> {normalize_score}/100")
        score = round(normalize_score)
        if score == 0:
            return "-"
        elif score == 100:
            return "S"
        elif 95 <= score <= 99:
            return "A+"
        elif 90 <= score <= 94:
            return "A"
        elif 85 <= score <= 89:
            return "A-"
        elif 80 <= score <= 84:
            return "B+"
        elif 75 <= score <= 79:
            return "B"
        elif 70 <= score <= 74:
            return "B-"
        elif 65 <= score <= 69:
            return "C+"
        elif 60 <= score <= 64:
            return "C"
        elif 55 <= score <= 59:
            return "C-"
        elif 50 <= score <= 54:
            return "D+"
        elif 45 <= score <= 49:
            return "D"
        elif 40 <= score <= 44:
            return "D-"
        elif 1 <= score <= 39:
            return "F"
        else:
            return "Grading error"
        
    def aggregate_weighted_section_scores(self):         # def fn1(self):
        weights      = self.weight_config["weights"]
        contribution = {}                    # Keep stat of score and detail
        total_section_weighted   = 0.0       # Accumulate section weight for every section (normally It's should be 1.0)
        total_weighted_raw_score = 0.0       # Accumulate raw score after time by weight
        total_weighted_max_score = 0.0       # Accumulate max score after time by weight
        for section_data in self.section_outputs: # Loop with section_output (Ss)
            section_name            = section_data["section"]   # Get section name
            total_section_raw_score = section_data["total_section_raw_score"]    # Get raw section score from each section
            total_section_max_score = section_data["total_section_max_score"]    # Get max section score from each section
            section_weight          = weights[section_name]["section_weight"]    # Get section_weight from weight.yaml e.g. 0.1,0.2
            
            total_section_raw_score_x_weight = total_section_raw_score*section_weight   # raw_score x weight
            total_section_max_score_x_weight = total_section_max_score*section_weight   # max_score x weight

            contribution[section_name] = {
                "session_grade":self.normalize_score_to_grade(total_section_raw_score_x_weight,total_section_max_score_x_weight), # Grading CVResume with (total_section_raw_score_x_weight/total_section_max_score_x_weight)*100 -> if else 
                "total_section_raw_score":total_section_raw_score,
                "total_section_max_score":total_section_max_score,
                "section_weight":section_weight,
                "total_section_raw_score_x_weight":total_section_raw_score_x_weight,
                "total_section_max_score_x_weight":total_section_max_score_x_weight
            }
            total_section_weighted    = total_section_weighted   + section_weight
            total_weighted_raw_score  = total_weighted_raw_score + total_section_raw_score_x_weight   # E(raw_score x weight)
            total_weighted_max_score  = total_weighted_max_score + total_section_max_score_x_weight   # E(max_score x weight)
            
        return {
            "global_grade":self.normalize_score_to_grade(total_weighted_raw_score,total_weighted_max_score), # Grading CVResume with (total_weighted_raw_score/total_weighted_max_score)*100 -> if else 
            "total_weighted_raw_score":total_weighted_raw_score, # E(raw_score x weight) Summation of raw score for every section every criteria
            "total_weighted_max_score":total_weighted_max_score, # E(max_score x weight) Summation of max score for every section every criteria
            "total_section_weight":total_section_weighted,
            "section_contribution":contribution,                 # Details
            "globalfeedback":self.parse_global_feedback
        }
    
    def generate_global_feedback(self):    # def fn2(self)
        details = {}
        for section_data in self.section_outputs:
            # print(f"section_data->\n{section_data}")
            details[section_data["section"]] = {
                'total_section_raw_score':section_data['total_section_raw_score'],
                'total_section_max_score':section_data['total_section_max_score'],
                'scores':section_data['scores'],
                'section_feedbak':section_data['session_feedback']
            }
        # prompt = self.prompt_config['feedback']['globalfeedback']
        prompt = f'''
            You are an expert CV and Resume reviewer.

            Your task is to generate a SINGLE, GLOBAL feedback summary based on the full resume evaluation results below.

            IMPORTANT:
            - You MUST read and consider feedback from ALL resume sections.
            - Do NOT repeat section-by-section feedback.
            - Synthesize insights into an overall assessment.
            - Assume the user will NOT read individual section details.
            - Limit the session_feedback to one short paragraph with 20 words.

            Focus on:
            1. Overall strengths of the resume
            2. Key weaknesses or gaps
            3. High-impact, actionable improvement advice

            Guidelines:
            - Be professional, constructive, and specific
            - Avoid generic statements
            - Do NOT assume missing information
            - Base your feedback ONLY on the evaluation data provided
            {self.config_lang}

            INPUT (section-level evaluation results):
            {json.dumps(details, indent=2)}

            STRICT OUTPUT RULES:
            - Return JSON ONLY
            - No markdown
            - No explanation
            - No extra text

            Output schema:
            {
                {
                "response": "Concise but insightful global feedback covering strengths, weaknesses, and improvement suggestions."
                }
            }
        '''
        # print(f"prompt->\n{prompt}")
        self.parse_global_feedback,_ = self._call_raw(prompt)
        # print(self.parse)
        return details
    
    def build_metadata(self):    # def fn3(self):
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
    
    def build_final_evaluation(self):
        """
        Assemble the final evaluation response.
        Combines the final resume score, detailed section results,
        and evaluation metadata into a single response payload.
        Returns:
            dict:
                Final aggregated resume evaluation result.
        """
        detail_part     = self.generate_global_feedback()
        conclution_part = self.aggregate_weighted_section_scores()
        metadata_part   = self.build_metadata()
        
        return {
            "Conclution":conclution_part,
            "Section_detail":detail_part,
            "Metadata":metadata_part
        }