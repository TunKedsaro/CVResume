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

class LlmCaller(Helper):
    def __init__(self):
        api_key         = os.getenv("GOOGLE_API_KEY")
        self.model_cfg  = self.load_yaml("src/config/model.yaml")
        self.client     = genai.Client(api_key=api_key)
        self.model      = self.model_cfg["model"]["generation_model"]
    def _parse(self,resp):
        text = resp.text.strip()
        text = re.sub(r"^```json|```$", "", text).strip()
        return json.loads(text)
    def call(self,prompt:str):
        resp = self.client.models.generate_content(
            model    = self.model,
            contents = prompt 
        )
        parsed = self._parse(resp)
        return parsed, resp

# x = LlmCaller()
# parsed,resp = x.call("Hello,This is Gemini conection testing if you here me return {'status': 'connected'} as a json format")
# print(parsed)