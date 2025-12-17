from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from typing import Optional

from core.llmcaller import LlmCaller
from core.getmetadata import get_metadata      # 13
from core.globalupdate import update_global    # 14
from core.scoreaggregator import SectionScoreAggregator

from time import time
class AnalyseRequest(BaseModel):
    JSON: str | None = None

app = FastAPI(
    title="CV/Resume Evaluation API",
    version="0.1.1",
    description=(
        "Microservices for CV/Resume evaluation (In progress krub)"
        "<br>"
        f"Last time Update : {str(datetime.now(tz=(timezone(timedelta(hours=7)))))}"
    ),
    contact={
        "name": "Tun Kedsaro",
        "email": "tun.k@terradigitalventures.com"
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
### Health & Metadata #######################################################
### Health & Metadata.API:01 ################################################
@app.get("/", tags=["Health & Metadata"],
            description="Basic health check endpoint for uptime monitoring."
)
def health_fastapi():
    start_time = time()
    # for i in range(100000):
    #     print(i)
    finish_time   = time()
    process_time = finish_time - start_time
    return {
        "status": "ok", 
        "service": "FastAPI",
        "response_time" : f"{process_time:.5f} s"
        }

### Health & Metadata.API:02 ################################################
caller = LlmCaller()
agg = SectionScoreAggregator()

@app.get("/health/gemini", tags=["Health & Metadata"],
                description="Connectivity health check for Gemini LLM service. Verifies API availability and measures round-trip response latency."
)
def health_gemini():
    start_time = time()
    res = caller.call(
        "Return this as JSON: {'status': 'connected'}"
    )
    finish_time   = time()
    process_time = finish_time - start_time
    return {
        "response":res,
        "response_time" : f"{process_time:.5f} s"
        }

### Health & Metadata.API:03 ################################################
@app.get(
    "/health/metadata",
    tags=["Health & Metadata"],
    description="Metadata health check endpoint. Verifies metadata retrieval functionality and measures response latency."
)

def metadata():
    start_time = time()
    res = get_metadata()
    finish_time   = time()
    process_time = finish_time - start_time
    return {
        "message":get_metadata(),
        "response_time" : f"{process_time:.5f} s"
        }


#############################################################################
#############################################################################
    # start_time = time()
    # finish_time   = time()
    # "response_time" : f"{process_time:.5f} s"
### Debug & Lab #############################################################
from core.promptbuilder import PromptBuilder
from fastapi import Response

### Debug & Lab.API:04 ######################################################
from core.helper import Helper
mock_data = Helper.load_json("src/mock/resume3.json")
@app.get(
    "/evaluation/logexamplepayload",
    tags=["Debug & Lab"],
    description="Debug endpoint that returns a mock resume JSON payload as an example request body for evaluation APIs."
)

def show_example_of_payload_json_body():
    return {"response":mock_data}

### Debug & Lab.API:05 ######################################################
@app.get(
    "/evaluation/callexamplepayload",
    tags=["Debug & Lab"],
    description="Debug endpoint that builds a sample prompt from mock resume data and invokes the LLM to demonstrate an end-to-end evaluation flow with response latency."
)

def call_example_payload_json_body():
    test_payload = {"resume_json": mock_data}
    start_time = time()
    p1 = PromptBuilder(
        section  = "Profile",
        criteria = ["Completeness", "ContentQuality"],
        targetrole = "data scientist",
        cvresume = test_payload["resume_json"]
    )
    prompt = p1.build()
    res = caller.call(prompt)
    finish_time   = time()
    return {
        "response": res,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

### Debug & Lab.API:06 ######################################################
class PromptBuilderPayload(BaseModel):
        section    : str  | None = Field (default = "Summary")
        criteria   : list | None = Field (default = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"])
        targetrole : str  | None = Field (default = "Data scientist")

@app.post(
    "/test/prompt",
    tags=["Debug & Lab"],
    description="Debug endpoint for generating and inspecting a prompt using provided section, criteria, and target role parameters without invoking the LLM."
)

def prompt_lab(payload:PromptBuilderPayload):
    pl = payload.model_dump()
    pb = PromptBuilder(
        section    = pl["section"],
        criteria   = pl["criteria"],
        targetrole = pl["targetrole"],
        cvresume   = "resume_json"
        )
    prompt = pb.build()
    return Response(content=prompt, media_type="text/plain")

### Debug & Lab.API:07 ######################################################
# from core.promptupdate import update_prompt

# class PromptRole(BaseModel):
#     role1: Optional[str] = None
# class PromptObjective(BaseModel):
#     objective1: Optional[str] = None
# class PromptSectionName(BaseModel):
#     section1: Optional[str] = None
# class ExpectedContent(BaseModel):
#     Profile: Optional[str] = None
#     Summary: Optional[str] = None
#     Education: Optional[str] = None
#     Experience: Optional[str] = None
#     Activities: Optional[str] = None
#     Skills: Optional[str] = None
# class PromptScale(BaseModel):
#     score1: Optional[str] = None
#     score2: Optional[str] = None
# class OutputFormat(BaseModel):
#     format1: Optional[str] = None
#     format2: Optional[str] = None
#     format3: Optional[str] = None

# class PromptUpdatePayload(BaseModel):
#     version: Optional[str] = "prompt_v1"

#     role: Optional[PromptRole] = None
#     objective: Optional[PromptObjective] = None
#     section: Optional[PromptSectionName] = None
#     expected_content: Optional[ExpectedContent] = None
#     scale: Optional[PromptScale] = None
#     output: Optional[OutputFormat] = None

#     model_config = {
#         "json_schema_extra": {
#             "example": {
#                 "version": "prompt_v1",
#                 "role": {
#                     "role1": "You are the expert HR evaluator"
#                 },
#                 "objective": {
#                     "objective1": "Evaluate the <section_name> section from the resume using the scoring criteria"
#                 },
#                 "section": {
#                     "section1": "You are evaluating the <section_name> section."
#                 },
#                 "expected_content": {
#                     "Profile": 
#                         "- Candidate's basic professional identity\n"
#                         "- Clear positioning (e.g., \"Data Analyst\", \"ML Engineer\")\n"
#                         "- Career direction or headline\n"
#                         "- Avoid unnecessary personal details\n"
#                         "- Feedback word 20 words",
#                     "Summary": 
#                         "- 2-4 sentence summary of experience\n"
#                         "- Technical & domain strengths\n"
#                         "- Career focus & value proposition\n"
#                         "- Avoid buzzwords\n"
#                         "- Feedback word 20 words",
#                     "Education":
#                         "- Institution name\n"
#                         "- Degree & field of study\n"
#                         "- Dates attended\n"
#                         "- GPA, honors (optional)\n"
#                         "- Relevance to data career\n"
#                         "- Feedback word 20 words",
#                     "Experience":
#                         "- Job title, employer, dates\n"
#                         "- Clear bullet points\n"
#                         "- Action then method then impact structure\n"
#                         "- Technical tools used\n"
#                         "- Quantifiable metrics\n"
#                         "- Feedback word 20 words",
#                     "Activities":
#                         "- Competitions, hackathons, club activities\n"
#                         "- Project descriptions with responsibilities\n"
#                         "- Mention of tools/tech if applicable\n"
#                         "- Feedback word 20 words",
#                     "Skills":
#                         "- Technical skills (Python, SQL, ML, Cloud)\n"
#                         "- Tools (Power BI, Git, TensorFlow)\n"
#                         "- Soft skills\n"
#                         "- Language proficiency\n"
#                         "- Clear grouping/categorization\n"
#                         "- Feedback word 20 words"
#                 },
#                 "scale": {
#                     "score1":
#                         "0 = missing\n"
#                         "1 = poor\n"
#                         "2 = weak\n"
#                         "3 = sufficient\n"
#                         "4 = strong\n"
#                         "5 = excellent"
#                 }
#             }
#         }
#     }
# @app.put("/config/prompt", tags=["Debug & Lab"])
# def update_prompt_config(payload:PromptUpdatePayload):
#     payload_dict = payload.model_dump(exclude_none=True)
#     updated_yaml = update_prompt(payload_dict)
#     return {
#         "message":"prompt.yaml updated !!!",
#         "updated_keys":list(payload_dict.keys()),
#         "config":updated_yaml
#     }
#############################################################################
#############################################################################

### Evaluation ##############################################################
### Evaluation.API:08 #######################################################
# class ResumeSection(BaseModel):
#     text: str
#     word_count: int
#     matched_jd_skills: list[str]
#     confidence_score: float
# class ResumeSchema(BaseModel):
#     job_id: str
#     template_id: str
#     language: str
#     status: str
#     sections: dict[str, ResumeSection]
#     skills: list[dict]
class EvaluationPayload(BaseModel):
    # resume_json: ResumeSchema
    resume_json: dict | None = Field (default="resume_json")

@app.post(
    "/evaluation/profile",
    tags=["Evaluation"],
    description="Evaluates the Profile section of a resume using predefined criteria and role context, returning aggregated LLM-based scores with processing latency."
)
def evaluation_profile(payload: EvaluationPayload):
    start_time = time()
    resume_json = payload.resume_json
    p1 = PromptBuilder(
        section  = "Profile",
        criteria = ["Completeness", "ContentQuality"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt = p1.build()
    op1 = caller.call(prompt)
    s1 = agg.aggregate(op1)
    finish_time   = time()

    return {
        "response": s1,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

### Evaluation.API:09 #######################################################
@app.post(
    "/evaluation/summary",
    tags=["Evaluation"],
    description="Evaluates the Summary section of a resume against multiple quality and relevance criteria, returning aggregated LLM-based scores with processing latency."
)

def evaluate_summary(payload: EvaluationPayload):
    start_time = time()
    resume_json = payload.resume_json
    p2 = PromptBuilder( 
        section  = "Summary", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt = p2.build()
    op2 = caller.call(prompt)
    s2 = agg.aggregate(op2)
    finish_time   = time()
    return {
        "response": s2,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

### Evaluation.API:10 #######################################################
@app.post(
    "/evaluation/education",
    tags=["Evaluation"],
    description="Evaluates the Education section of a resume for completeness and role relevance, returning aggregated LLM-based scores with processing latency."
)

def evaluate_education(payload: EvaluationPayload):
    start_time = time()
    resume_json = payload.resume_json
    p3 = PromptBuilder( 
        section  = "Education", 
        criteria = ["Completeness","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt3 = p3.build()
    op3 = caller.call(prompt3)
    s3 = agg.aggregate(op3)
    finish_time   = time()
    return {
        "response": s3,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

### Evaluation.API:11 #######################################################
@app.post(
    "/evaluation/experience",
    tags=["Evaluation"],
    description="Evaluates the Experience section of a resume using content quality, completeness, grammar, length, and role relevance criteria, returning aggregated LLM-based scores with processing latency."
)

def evaluate_experience(payload: EvaluationPayload):
    start_time = time()
    resume_json = payload.resume_json
    p4 = PromptBuilder( 
        section  = "Experience", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt4 = p4.build()
    op4 = caller.call(prompt4)
    s4 = agg.aggregate(op4)
    finish_time   = time()
    return {
        "response": s4,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }


### Evaluation.API:12 #######################################################
@app.post(
    "/evaluation/activities",
    tags=["Evaluation"],
    description="Evaluates the Activities section of a resume based on completeness, content quality, grammar, and length criteria, returning aggregated LLM-based scores with processing latency."
)

def evaluate_activities(payload: EvaluationPayload):
    start_time = time()
    resume_json = payload.resume_json
    p5 = PromptBuilder( 
        section  = "Activities", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt5 = p5.build()
    op5 = caller.call(prompt5)
    s5 = agg.aggregate(op5)
    finish_time   = time()
    return {
        "response": s5,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }


### Evaluation.API:13 #######################################################
@app.post(
    "/evaluation/skills",
    tags=["Evaluation"],
    description="Evaluates the Skills section of a resume based on completeness, length, and role relevance criteria, returning aggregated LLM-based scores with processing latency."
)

def evaluate_skills(payload: EvaluationPayload):
    start_time = time()
    resume_json = payload.resume_json
    p6 = PromptBuilder( 
        section  = "Skills", 
        criteria = ["Completeness","Length","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt6 = p6.build()
    op6 = caller.call(prompt6)
    s6 = agg.aggregate(op6)
    finish_time   = time()
    return {
        "response": s6,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

#############################################################################
#############################################################################

### Composite evaluation ####################################################
### Composite evaluation.API:14 #############################################
from core.globalaggregator import GlobalAggregator

@app.post(
    "/evaluation/final-resume-score",
    tags=["Composite Evaluation"],
    description="Performs a full resume evaluation by scoring all major sections and aggregating them into a final composite resume score with overall processing latency."
)

def evaluate_resume(payload: EvaluationPayload):
    start_time = time()
    resume_json = payload.resume_json
    p1 = PromptBuilder(
        section  = "Profile",
        criteria = ["Completeness", "ContentQuality"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt1 = p1.build()
    
    p2 = PromptBuilder( 
        section  = "Summary", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt2 = p2.build()
    
    p3 = PromptBuilder( 
        section  = "Education", 
        criteria = ["Completeness","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt3 = p3.build()

    p4 = PromptBuilder( 
        section  = "Experience", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt4 = p4.build()
    
    p5 = PromptBuilder( 
        section  = "Activities", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt5 = p5.build()
    
    p6 = PromptBuilder( 
        section  = "Skills", 
        criteria = ["Completeness","Length","RoleRelevance"],
        targetrole = "Data science",
        cvresume = resume_json
    )
    prompt6 = p6.build()

    op1 = caller.call(prompt1)
    op2 = caller.call(prompt2)
    op3 = caller.call(prompt3)
    op4 = caller.call(prompt4)
    op5 = caller.call(prompt5)
    op6 = caller.call(prompt6)

    s1 = agg.aggregate(op1)
    s2 = agg.aggregate(op2)
    s3 = agg.aggregate(op3)
    s4 = agg.aggregate(op4)
    s5 = agg.aggregate(op5)
    s6 = agg.aggregate(op6)

    x = GlobalAggregator(SectionScoreAggregator_output = [s1,s2,s3,s4,s5,s6])

    output = x.fn0()

    finish_time   = time()
    return {
        "response": output,
        "response_time" : f"{finish_time - start_time:.5f} s"
    }

#############################################################################
#############################################################################


### Admin ####################################################################
### Admin.API:15 #############################################################
# class test(BaseModel):
#     provider         :str | None = Field (default="google")
#     embedding_model  :str | None = Field (default="text-embedding-004")
#     generation_model :str | None = Field (default="gemini-2.5-flash")

# from core.modelupdate import update_model
# @app.put("/config/model",tags=["Admin"])
# def update_model_config(payload:test):
#     update_model(payload.model_dump())
#     return {
#         "status":"updated",
#         "payload":payload
#     }
### Admin.API16 ##############################################################
# 14. Update global x
# class SettingConfig(BaseModel):
#     GOOGLE_API_KEY: Optional[str] = Field(default=None, example="AIza-xxxx")
# class PricingModel(BaseModel):
#     input_per_million: Optional[float] = Field(default=None, example=0.10)
#     output_per_million: Optional[float] = Field(default=None, example=0.40)
# class PricingConfig(BaseModel):
#     gemini_2_5_flash: Optional[PricingModel] = Field(
#         default=None,
#         example={
#             "input_per_million": 0.10,
#             "output_per_million": 0.40
#         }
#     )
# class ScoringConfig(BaseModel):
#     final_score_max: Optional[int] = Field(default=None, example=100)
#     normalize: Optional[bool] = Field(default=None, example=True)
#     round_digits: Optional[int] = Field(default=None, example=2)
#     aggregation_method: Optional[str] = Field(default=None, example="weighted_sum")
# class GlobalUpdatePayload(BaseModel):
#     version: Optional[str] = Field(default="global_v1", example="global_v1")
#     setting: Optional[SettingConfig] = Field(default=None)
#     pricing: Optional[PricingConfig] = Field(default=None)
#     scoring: Optional[ScoringConfig] = Field(default=None)

# @app.put("/config/global",tags=["Admin"])
# def update_global_config(payload:GlobalUpdatePayload):
#     updated = update_global(payload.model_dump())
#     return {
#         "status":"updated",
#         "config":updated
#     }

### Admin.API17 ##############################################################
# from core.weightupdate import update_weight
# class Criteria(BaseModel):
#     Completeness: Optional[int]   = Field(default=10)
#     ContentQuality: Optional[int] = Field(default=10)
#     Grammar: Optional[int]        = Field(default=10)
#     Length: Optional[int]         = Field(default=10)
#     RoleRelevance: Optional[int]  = Field(default=10)
#     section_weight: Optional[float] = Field(default=0.1)
# class ResumeParts(BaseModel):
#     Profile: Optional[Criteria]  = Field(
#         default = None,
#         example={
#             "Completeness": 10,
#             "ContentQuality": 10,
#             "Grammar": 0,
#             "Length": 0,
#             "RoleRelevance": 0,
#             "section_weight": 0.1
#         })
#     Summary: Optional[Criteria]  = Field(
#         default = None,
#         example={
#             "Completeness": 10,
#             "ContentQuality": 10,
#             "Grammar": 10,
#             "Length": 10,
#             "RoleRelevance": 10,
#             "section_weight": 0.1
#         })
#     Education: Optional[Criteria]  = Field(
#         default = None,
#         example={
#             "Completeness": 10,
#             "ContentQuality": 0,
#             "Grammar": 0,
#             "Length": 0,
#             "RoleRelevance": 10,
#             "section_weight": 0.2
#         })
#     Experience: Optional[Criteria]  = Field(
#         default = None,
#         example={
#             "Completeness": 10,
#             "ContentQuality": 10,
#             "Grammar": 10,
#             "Length": 10,
#             "RoleRelevance": 10,
#             "section_weight": 0.2
#         })
#     Activities: Optional[Criteria]  = Field(
#         default = None,
#         example={
#             "Completeness": 10,
#             "ContentQuality": 10,
#             "Grammar": 10,
#             "Length": 10,
#             "RoleRelevance": 10,
#             "section_weight": 0.2
#         })
#     Skills: Optional[Criteria]  = Field(
#         default = None,
#         example={
#             "Completeness": 10,
#             "ContentQuality": 0,
#             "Grammar": 0,
#             "Length": 10,
#             "RoleRelevance": 10,
#             "section_weight": 0.2
#         })
# class WeightUpdatePayload(BaseModel):
#     version: Optional[str] = Field(default="weights_v1")
#     weights: Optional[ResumeParts]   = Field(default=None)

# @app.put("/config/weight",tags=['Admin'])
# def update_global_config(payload:WeightUpdatePayload):
#     updated = update_weight(payload.model_dump())
#     return {
#         "status":"updated",
#         "config":updated
#     }



