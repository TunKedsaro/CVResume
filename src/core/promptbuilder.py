from google import genai
import json
import os
import yaml
from core.helper import Helper


class BasePromptBuilder(Helper):
    '''
    PromptBuilder v3 : PromptBuilder + Session,Global feedback + PromptSplit
    '''
    base_dir = "src/config/prompts"         # Prompts .yaml config file folder path
    def __init__(self, section, criteria, targetrole, cvresume, include_fewshot: bool = True, output_lang = "en"):
        self.section         = section
        self.criteria        = criteria[::-1]
        self.targetrole      = targetrole
        self.cvresume        = cvresume
        self.include_fewshot = include_fewshot
        self.output_lang     = output_lang

        self.global_config   = self.load_yaml("src/config/prompts/base.yaml")
        self.section_config  = self.load_yaml(f"{self.base_dir}/{self.section.lower()}.yaml")
        self.number_of_words = self.load_yaml("src/config/global.yaml")["output"]["number_of_words"]
        self.criteria_cfg    = self.section_config['criteria']
    def _build_response_template(self):
        return {
            "section": self.section,
            "scores": {
                c: {"score": 0, "feedback": ""} for c in self.criteria
            },
            "session_feedback":""
        }
    
    def _build_criteria_block(self) -> str:
        blocks = []
        for crit in self.criteria:
            block = f"- {crit}\n"
            for i in [5,3,1]:
                block += f"  score {i} :\n"
                x = f"score{i}"
                block += "\n".join(
                    "    " + line
                    for line in self.criteria_cfg[crit][x].splitlines()
                ) + "\n"
            blocks.append(block)
        return "".join(blocks)

    def build(self):
        config_role       = self.global_config['role']['role1']
        config_task       = self.section_config['task']['task1']
        config_lang       = self.global_config['Language_output_style'][self.output_lang]
        config_expected   = self.section_config['expected_content'][self.section]
        criteria_block    = self._build_criteria_block()
        config_example    = self.section_config['output_guidelines'][self.section]
        config_scale      = self.global_config['scale']['score1']
        config_feedback   = self.global_config['feedback']['globalfeedback']

        prompt_role       = f"Role :\n{config_role}\n\n"
        prompt_task       = f"Task :\n{config_task}\n"
        prompt_lang       = f"Output language instruction :\n{config_lang}\n"
        prompt_expected   = f"Expected :\n{config_expected}\n"
        prompt_criteria   = f"Criteria :\n{criteria_block}\n"
        prompt_scale      = f"Scale :\n{config_scale}\n"
        prompt_feedback   = f"Session feedback :\n{config_feedback}\n\n"
        prompt_Op_example = f"Output guideline :\n{config_example}\n\n"
        prompt_Op_format  = f"Output format :\n{json.dumps(self._build_response_template(), indent=2)}\n\n"
        prompt_cvresume   = f"CV/Resume :\n{self.cvresume}\n"

        prompt = (
            prompt_role + prompt_task + prompt_lang
            + prompt_expected + prompt_criteria + prompt_scale + prompt_feedback 
            + prompt_Op_example + prompt_Op_format + prompt_cvresume 
        )

        prompt = prompt.replace("<section_name>", self.section)
        prompt = prompt.replace("<targetrole>", self.targetrole)
        prompt = prompt.replace("<number_of_words>", str(self.number_of_words))

        return prompt

# p4 = BasePromptBuilder( 
#     section     = "Experience", 
#     criteria    = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
#     targetrole  = "data scientist",
#     cvresume    = 'test_payload["resume_json"]',
#     output_lang = "en"
# )
# prompt4 = p4.build()
# print(prompt4)


# class PromptBuilder(Helper):
#     """
#     PromptBuilder v1 : Original Promptbuilder
#     Builds a structured evaluation prompt for a specific resume section.
#     Uses YAML-driven configuration to assemble role instructions,
#     evaluation criteria, scoring scale, expected content, and
#     the candidate resume into a single LLM-ready prompt.
#     """

#     def __init__(self, section, criteria, targetrole, cvresume, include_fewshot: bool = True, output_lang = "en"):
#         """
#         Initialize the prompt builder for a resume section.
#         Args:
#             section (str): Resume section to evaluate (e.g. "Education").
#             criteria (list): Evaluation criteria for the section.
#             targetrole (str): Target role used for role relevance.
#             cvresume (str): Resume content to be evaluated.
#             include_fewshot (bool): Whether to include example scores.
#             output_lang (str): Output language code (e.g. "en", "th").
#         """
#         self.section        = section
#         self.criteria       = criteria[::-1]
#         self.cvresume       = cvresume
#         self.targetrole     = targetrole
#         self.include_fewshot= include_fewshot
#         self.output_lang    = output_lang
        
#         self.config         = self.load_yaml("src/config/prompt.yaml")
#         self.config_global  = self.load_yaml("src/config/global.yaml")
#         self.criteria_cfg   = self.config.get("criteria", {})

#     def build_response_template(self):
#         """
#         Build an empty JSON response template for the LLM.
#         Returns:
#             dict: Response skeleton with section name and criteria scores.
#         """
#         return {
#             "section": self.section,
#             "scores": {
#                 c: {"score": 0, "feedback": ""} for c in self.criteria
#             }
#         }
    
#     def _build_criteria_block(self) -> str:
#         """
#         Construct the criteria description block for the prompt.
#         Includes few-shot score examples if enabled and available
#         in the prompt configuration.
#         Returns:
#             str: Formatted criteria block text.
#         """
#         blocks = []
#         for crit in self.criteria:
#             block = f"- {crit}\n"
#             if self.include_fewshot and crit in self.criteria_cfg:
#                 few_cfg = self.criteria_cfg[crit]
#                 for score in [5, 3, 1]:
#                     key = f"score{score}"
#                     if key in few_cfg:
#                         text = few_cfg[key].strip()
#                         block += f"    score {score}: {text}\n"
#             blocks.append(block)
#         return "".join(blocks)
    
#     def build(self):
#         """
#         Assemble the full evaluation prompt.
#         Combines role instructions, evaluation objectives, section context,
#         criteria definitions, scoring scale, expected output format,
#         and resume content into a single prompt string.
#         Returns:
#             str: Final prompt ready to be sent to the LLM.
#         """
#         config_role      = self.config['role']['role1']
#         config_objective = self.config['objective']['objective1']
#         config_section   = self.config['section']['section1']
#         config_expected  = self.config['expected_content'][self.section]
#         config_scale     = self.config['scale']['score1']
#         criteria_block   = self._build_criteria_block()
#         config_lang      = self.config['Language_output_style'][self.output_lang]

#         prompt_role      = f"Role :\n{config_role}\n\n"
#         prompt_objective = f"Objectvie :\n{config_objective}\n"
#         promnt_lang      = f"Output Language Instruction::\n{config_lang}\n"
#         prompt_section   = f"Section :\n{config_section}\n\n"
#         prompt_expected  = f"Expected :\n{config_expected}\n"
#         prompt_criteria  = f"Criteria :\n{criteria_block}\n"
#         prompt_scale     = f"Scale :\n{config_scale}\n"
#         prompt_output    = f"Output :\n{json.dumps(self.build_response_template(), indent=2)}\n\n"
#         prompt_cvresume  = f"CV/Resume: \n{self.cvresume}\n"
#         prompt = (
#             prompt_role + prompt_objective + prompt_section + promnt_lang
#             + prompt_expected + prompt_criteria + prompt_scale
#             + prompt_output  + prompt_cvresume
#         )

#         prompt = prompt.replace("<section_name>", self.section)
#         prompt = prompt.replace("<targetrole>", self.targetrole)
#         # print(f"prompt -> \n{prompt}")
#         return prompt

# class PromptBuilder(Helper):
#     """
#     PromptBuilder v2 : PromptBuilder + Session,Global feedback
#     Builds a structured evaluation prompt for a specific resume section.
#     Uses YAML-driven configuration to assemble role instructions,
#     evaluation criteria, scoring scale, expected content, and
#     the candidate resume into a single LLM-ready prompt.
#     """

#     def __init__(self, section, criteria, targetrole, cvresume, include_fewshot: bool = True, output_lang = "en"):
#         """
#         Initialize the prompt builder for a resume section.
#         Args:
#             section (str): Resume section to evaluate (e.g. "Education").
#             criteria (list): Evaluation criteria for the section.
#             targetrole (str): Target role used for role relevance.
#             cvresume (str): Resume content to be evaluated.
#             include_fewshot (bool): Whether to include example scores.
#             output_lang (str): Output language code (e.g. "en", "th").
#         """
#         self.section        = section
#         self.criteria       = criteria[::-1]
#         self.cvresume       = cvresume
#         self.targetrole     = targetrole
#         self.include_fewshot= include_fewshot
#         self.output_lang    = output_lang
        
#         self.config         = self.load_yaml("src/config/prompt.yaml")
#         self.config_global  = self.load_yaml("src/config/global.yaml")
#         self.criteria_cfg   = self.config.get("criteria", {})

#     def build_response_template(self):
#         """
#         Build an empty JSON response template for the LLM.
#         Returns:
#             dict: Response skeleton with section name and criteria scores.
#         """
#         return {
#             "section": self.section,
#             "scores": {
#                 c: {"score": 0, "feedback": ""} for c in self.criteria
#             },
#             "session_feedback":""
#         }
    
#     def _build_criteria_block(self) -> str:
#         """
#         Construct the criteria description block for the prompt.
#         Includes few-shot score examples if enabled and available
#         in the prompt configuration.
#         Returns:
#             str: Formatted criteria block text.
#         """
#         blocks = []
#         for crit in self.criteria:
#             block = f"- {crit}\n"
#             if self.include_fewshot and crit in self.criteria_cfg:
#                 few_cfg = self.criteria_cfg[crit]
#                 for score in [5, 3, 1]:
#                     key = f"score{score}"
#                     if key in few_cfg:
#                         text = few_cfg[key].strip()
#                         block += f"    score {score}: {text}\n"
#             blocks.append(block)
#         return "".join(blocks)
    
#     def build(self):
#         """
#         Assemble the full evaluation prompt.
#         Combines role instructions, evaluation objectives, section context,
#         criteria definitions, scoring scale, expected output format,
#         and resume content into a single prompt string.
#         Returns:
#             str: Final prompt ready to be sent to the LLM.
#         """
#         config_role      = self.config['role']['role1']
#         config_objective = self.config['objective']['objective1']
#         config_section   = self.config['section']['section1']
#         config_expected  = self.config['expected_content'][self.section]
#         config_scale     = self.config['scale']['score1']
#         criteria_block   = self._build_criteria_block()
#         config_lang      = self.config['Language_output_style'][self.output_lang]
#         config_feedback  = self.config['feedback']['globalfeedback']

#         prompt_role      = f"Role :\n{config_role}\n\n"
#         prompt_objective = f"Objectvie :\n{config_objective}\n"
#         promnt_lang      = f"Output Language Instruction::\n{config_lang}\n"
#         prompt_section   = f"Section :\n{config_section}\n\n"
#         prompt_expected  = f"Expected :\n{config_expected}\n"
#         prompt_criteria  = f"Criteria :\n{criteria_block}\n"
#         prompt_scale     = f"Scale :\n{config_scale}\n"
#         prompt_feedback  = f'Session feedback :\n{config_feedback}\n'
#         prompt_output    = f"Output :\n{json.dumps(self.build_response_template(), indent=2)}\n\n"
#         prompt_cvresume  = f"CV/Resume: \n{self.cvresume}\n"
#         prompt = (
#             prompt_role + prompt_objective + prompt_section + promnt_lang
#             + prompt_expected + prompt_criteria + prompt_scale + prompt_feedback
#             + prompt_output  + prompt_cvresume
#         )

#         prompt = prompt.replace("<section_name>", self.section)
#         prompt = prompt.replace("<targetrole>", self.targetrole)
#         prompt = prompt.replace("<session_feedback-word>", str(self.config_global['feedback']['session_feedback_word']))
#         # print(f"prompt -> \n{prompt}
#         return prompt

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