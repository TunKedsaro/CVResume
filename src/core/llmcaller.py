from google import genai
import json
import re
from core.helper import Helper
import os

# class LlmCaller(Helper):
#     def __init__(self):
#         # self.global_cfg = self.load_yaml("src/config/global.yaml")
#         # api_key         = self.global_cfg["setting"]["GOOGLE_API_KEY"]
#         api_key         = os.getenv("GOOGLE_API_KEY")
#         self.model_cfg  = self.load_yaml("src/config/model.yaml")
#         self.client     = genai.Client(api_key=api_key)
#         self.model      = self.model_cfg["model"]["generation_model"]
#     def _parse(self,resp):
#         text = resp.text.strip()
#         text = re.sub(r"^```json|```$", "", text).strip()
#         return json.loads(text)
#     def call(self,prompt:str):
#         resp = self.client.models.generate_content(
#             model    = self.model,
#             contents = prompt 
#         )
#         return self._parse(resp)

# x = LlmCaller()
# resp = x.call("Hello,This is Gemini conection testing if you here me return {'status': 'connected'} as a json format")
# print(resp)

# class LlmCaller(Helper):
#     def __init__(self):
#         api_key         = os.getenv("GOOGLE_API_KEY")
#         self.model_cfg  = self.load_yaml("src/config/model.yaml")
#         self.client     = genai.Client(api_key=api_key)
#         self.model      = self.model_cfg["model"]["generation_model"]
#     def _parse(self,resp):
#         text = resp.text.strip()
#         text = re.sub(r"^```json|```$", "", text).strip()
#         return json.loads(text)
#     def call(self,prompt:str):
#         resp = self.client.models.generate_content(
#             model    = self.model,
#             contents = prompt 
#         )
#         parsed = self._parse(resp)
#         return parsed, resp

# x = LlmCaller()
# parsed,resp = x.call("Hello,This is Gemini conection testing if you here me return {'status': 'connected'} as a json format")
# print(parsed)

# import asyncio
# from time import time
# from core.logcost import estimate_gemini_cost
# from core.llm_excel_logger import log_llm_usage
# from core.helper import Helper


# from core.aggregator import SectionScoreAggregator

# agg = SectionScoreAggregator()



# from pydantic import BaseModel, Field, ValidationError
# from typing import Dict, Literal

# class CriterionScore(BaseModel):
#     score: int = Field(ge=0, le=5)
#     feedback: str

# class SectionEvaluation(BaseModel):
#     section: Literal["Skills"]
#     scores: Dict[str, CriterionScore]

# class LlmCaller(Helper):
#     def __init__(self):
#         api_key        = os.getenv("GOOGLE_API_KEY")
#         self.model_cfg = self.load_yaml("src/config/model.yaml")
#         self.client    = genai.Client(api_key=api_key)
#         self.model     = self.model_cfg["model"]["generation_model"]
#         self.usd2bath  = Helper.load_yaml("src/config/global.yaml")['currency']['USD_to_THB']
#         self.log_digit = Helper.load_yaml("src/config/global.yaml")['logging']['logging_round_digit']

#     def _parse(self, resp):
#         text = resp.text.strip()
#         text = re.sub(r"^```json|```$", "", text).strip()
#         return json.loads(text)

#     def call(self, prompt: str):
#         resp = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
#         parsed = self._parse(resp)
#         return parsed, resp

#     async def call_async(self, prompt: str):
#         return await asyncio.to_thread(self.call, prompt)
    
#     def run_llm(self,prompt:str,api_id:str,Oplang:str):
#         start = time()
#         op, raw = self.call(prompt)
#         s = agg.aggregate(op)
#         usage_time = time() - start
#         cost = estimate_gemini_cost(raw)
#         log_llm_usage({
#             "id": api_id,
#             "output_lange": Oplang,
#             "prompt_length_chars": len(prompt),
#             "input_tokens": cost["prompt_tokens"],
#             "output_tokens": cost["output_tokens"],
#             "total_tokens": cost["prompt_tokens"] + cost["output_tokens"],
#             "estimated_cost_usd": cost["total_cost"],
#             "estimated_cost_thd": cost["total_cost"] * self.usd2bath,
#             "response_time_sec": round(usage_time, self.log_digit)
#         })
#         return s, {
#             "usage_time":usage_time, 
#             "total_cost":cost["total_cost"] * self.usd2bath
#             }
    
#     def validate_llm_output(raw_output: dict) -> SectionEvaluation:
#         return SectionEvaluation.model_validate(raw_output)
    



import asyncio

from pydantic import BaseModel, Field, ValidationError
from typing import Dict

class CriterionScore(BaseModel):
    """
    Represents a single evaluation score for one criterion.
    Attributes:
        score (int): Integer score between 0 and 5.
        feedback (str): Textual feedback explaining the score.
    """
    score: int = Field(ge=0, le=5)
    feedback: str

class SectionEvaluation(BaseModel):
    """
    Validated LLM evaluation output for a resume section.
    Attributes:
        section (str): Name of the resume section.
        scores (Dict[str, CriterionScore]): Mapping of criteria to scores.
    """
    section: str
    scores: Dict[str, CriterionScore]

class LlmCaller(Helper):
    def __init__(self):
        """
        Handles interaction with the LLM for section-level resume evaluation.
        Responsibilities:
        - Send prompts to the LLM
        - Parse and validate structured JSON responses
        - Retry with a repair prompt if validation fails
        - Return validated output along with raw LLM response
        """
        api_key        = os.getenv("GOOGLE_API_KEY")
        self.model_cfg = self.load_yaml("src/config/model.yaml")
        self.client    = genai.Client(api_key=api_key)
        self.model     = self.model_cfg["model"]["generation_model"]
        self.usd2bath  = Helper.load_yaml("src/config/global.yaml")['currency']['USD_to_THB']
        self.log_digit = Helper.load_yaml("src/config/global.yaml")['logging']['logging_round_digit']

    def _parse(self, resp):
        """
        Parse raw LLM response text into a JSON object.
        Removes markdown code fences and converts the result to a dictionary.
        Args:
            resp: Raw response object from the LLM client.
        Returns:
            dict: Parsed JSON output.
        """
        text = resp.text.strip()
        text = re.sub(r"^```json|```$", "", text).strip()
        return json.loads(text)
    
    def _call_raw(self, prompt: str):
        """
        Send a prompt to the LLM without validation.
        Args:
            prompt (str): Prompt text to send.
        Returns:
            tuple:
                - Parsed JSON output (dict)
                - Raw LLM response object
        """
        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        parsed = self._parse(resp)
        return parsed, resp
    
    def _validate(self, raw_output:dict)->SectionEvaluation:
        """
        Validate LLM output against the expected schema.
        Args:
            raw_output (dict): Parsed LLM output.
        Returns:
            SectionEvaluation: Validated evaluation object.
        Raises:
            ValidationError: If the output does not match the schema.
        """
        return SectionEvaluation.model_validate(raw_output)
    
    def _repair_prompt(self, error_msg: str) -> str:
        """
        Generate a corrective prompt when LLM output validation fails.
        Instructs the LLM to strictly follow the expected JSON schema.
        Args:
            error_msg (str): Validation error message.
        Returns:
            str: Repair prompt to prepend to the original prompt.
        """
        return f"""
                Your previous response was INVALID.
                Validation error:
                {error_msg}
                STRICT RULES:
                - Return JSON only
                - No markdown
                - No explanation
                - Follow schema exactly
                - Section name must start with a capital letters (e.g. "Education")
                Expected format:
                {{
                    "section": "<section_name>",
                    "scores": {{
                        "<criterion>": {{ "score": 0-5, "feedback": "string" }}
                    }}
                }}
        """
    
    def call(self,prompt:str, max_retry:int = 3):
        """
        Call the LLM with validation and automatic retry.
        Attempts to validate the LLM response. If validation fails,
        retries using a repair prompt up to the specified limit.
        Args:
            prompt (str): Prompt text to send.
            max_retry (int): Maximum number of retry attempts.
        Returns:
            tuple:
                - Validated evaluation result (dict)
                - Raw LLM response object
        """
        last_error = None
        repair_prompt = "\n"
        for attemp in range(max_retry):
            final_prompt = repair_prompt + prompt
            # print(f"final_prompt attemp : {attemp} -> \n {final_prompt}")
            output, raw = self._call_raw(final_prompt)
            try:
                validated = self._validate(output)
                # print('Status : 1')
                return validated.model_dump(),raw
            except ValidationError as e:
                last_error = str(e)
                repair_prompt = self._repair_prompt(last_error)
                # print('Status : 0')
                print("Output error recall again ...")
            finally:
                print('='*100)
        return {
            "section":"UNKNOW",
            "scores":{}
        },raw

    async def call_async(self, prompt: str):
        """
        Asynchronous wrapper for `call`.
        Executes the blocking LLM call in a background thread.
        Args:
            prompt (str): Prompt text to send.
        Returns:
            tuple:
                - Validated evaluation result (dict)
                - Raw LLM response object
        """
        return await asyncio.to_thread(self.call, prompt)
