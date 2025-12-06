from google import genai
import json
import os
import yaml
from core.helper import Helper

class PromptBuilder(Helper):
    def __init__(self,section,criteria,cvresume):
        self.section  = section
        self.criteria = criteria[::-1]
        self.cvresume = cvresume
        self.config = Helper.load_yaml("src/config/prompt.yaml")
        # print(self.config)
    def build_response_template(self):
        return {
            "section": self.section,
            "scores": {
                c: {"score": 0, "feedback": ""} for c in self.criteria
            }
        }
    def build(self):
        config_role      = self.config['role']['role1']
        config_objective = self.config['objective']['objective1']
        config_section   = self.config['section']['section1']
        config_expected  = self.config['expected_content'][self.section]
        config_criteria  = ""
        for item in self.criteria:
            config_criteria = f"- {item}\n" + config_criteria
        config_scale     = self.config['scale']['score1']
        # config_output    = self.config['output']['format1']
        
        prompt_role      = f"Role :\n{config_role}"+"\n\n"
        prompt_objective = f"objectvie :\n{config_objective}"+"\n\n"
        prompt_section   = f"section :\n{config_section}"+"\n\n"
        prompt_expected  = f"expected :\n{config_expected}"+"\n"
        prompt_criteria  = f"Criteria :\n{config_criteria}"+"\n"
        prompt_scale     = f"Scale :\n{config_scale}"+"\n"
        prompt_output    = f"output :\n{json.dumps(self.build_response_template(), indent=2)}"+"\n\n"
        prompt_cvresume  = f"CV/Resume: \n{self.cvresume}"+"\n"

        prompt = prompt_role + prompt_objective + prompt_section \
            + prompt_expected + prompt_criteria + prompt_scale \
            + prompt_output + prompt_cvresume
        prompt = prompt.replace("<section_name>",self.section)
        return prompt