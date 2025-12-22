from google import genai
import json
import os
import yaml
from core.helper import Helper

class PromptBuilder(Helper):
    def __init__(self, section, criteria, targetrole, cvresume, include_fewshot: bool = True, output_lang = "en"):
        self.section        = section
        self.criteria       = criteria[::-1]
        self.cvresume       = cvresume
        self.targetrole     = targetrole
        self.include_fewshot= include_fewshot
        self.output_lang    = output_lang
        
        self.config = self.load_yaml("src/config/prompt.yaml")
        self.criteria_cfg = self.config.get("criteria", {})

    def build_response_template(self):
        return {
            "section": self.section,
            "scores": {
                c: {"score": 0, "feedback": ""} for c in self.criteria
            }
        }
    
    def _build_criteria_block(self) -> str:
        blocks = []
        for crit in self.criteria:
            block = f"- {crit}\n"
            if self.include_fewshot and crit in self.criteria_cfg:
                few_cfg = self.criteria_cfg[crit]
                for score in [5, 3, 1]:
                    key = f"score{score}"
                    if key in few_cfg:
                        text = few_cfg[key].strip()
                        block += f"    score {score}: {text}\n"
            blocks.append(block)
        return "".join(blocks)
    
    def build(self):
        config_role      = self.config['role']['role1']
        config_objective = self.config['objective']['objective1']
        config_section   = self.config['section']['section1']
        config_expected  = self.config['expected_content'][self.section]
        config_scale     = self.config['scale']['score1']
        criteria_block   = self._build_criteria_block()
        config_lang      = self.config['Language_output_style'][self.output_lang]

        prompt_role      = f"Role :\n{config_role}\n\n"
        prompt_objective = f"Objectvie :\n{config_objective}\n"
        promnt_lang      = f"Output Language Instruction::\n{config_lang}\n"
        prompt_section   = f"Section :\n{config_section}\n\n"
        prompt_expected  = f"Expected :\n{config_expected}\n"
        prompt_criteria  = f"Criteria :\n{criteria_block}\n"
        prompt_scale     = f"Scale :\n{config_scale}\n"
        prompt_output    = f"Otput :\n{json.dumps(self.build_response_template(), indent=2)}\n\n"
        prompt_cvresume  = f"CV/Resume: \n{self.cvresume}\n"
        prompt = (
            prompt_role + prompt_objective + prompt_section + promnt_lang
            + prompt_expected + prompt_criteria + prompt_scale
            + prompt_output + prompt_cvresume 
        )
        # print(f"prompt -> \n{prompt}")
        prompt = prompt.replace("<section_name>", self.section)
        prompt = prompt.replace("<targetrole>", self.targetrole)
        return prompt


# class PromptBuilder(Helper):
#     def __init__(self,section,criteria,cvresume):
#         self.section  = section
#         self.criteria = criteria[::-1]
#         self.cvresume = cvresume
#         self.config = Helper.load_yaml("src/config/prompt.yaml")
#         # print(self.config)
#     def build_response_template(self):
#         return {
#             "section": self.section,
#             "scores": {
#                 c: {"score": 0, "feedback": ""} for c in self.criteria
#             }
#         }
#     def build(self):
#         config_role      = self.config['role']['role1']
#         config_objective = self.config['objective']['objective1']
#         config_section   = self.config['section']['section1']
#         config_expected  = self.config['expected_content'][self.section]
#         config_criteria  = ""
#         for item in self.criteria:
#             config_criteria = f"- {item}\n" + config_criteria
#         config_scale     = self.config['scale']['score1']
#         # config_output    = self.config['output']['format1']
        
#         prompt_role      = f"Role :\n{config_role}"+"\n\n"
#         prompt_objective = f"objectvie :\n{config_objective}"+"\n\n"
#         prompt_section   = f"section :\n{config_section}"+"\n\n"
#         prompt_expected  = f"expected :\n{config_expected}"+"\n"
#         prompt_criteria  = f"Criteria :\n{config_criteria}"+"\n"
#         prompt_scale     = f"Scale :\n{config_scale}"+"\n"
#         prompt_output    = f"output :\n{json.dumps(self.build_response_template(), indent=2)}"+"\n\n"
#         prompt_cvresume  = f"CV/Resume: \n{self.cvresume}"+"\n"

#         prompt = prompt_role + prompt_objective + prompt_section \
#             + prompt_expected + prompt_criteria + prompt_scale \
#             + prompt_output + prompt_cvresume
#         prompt = prompt.replace("<section_name>",self.section)
#         return prompt