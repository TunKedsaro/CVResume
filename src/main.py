from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from typing import Optional

from core.llmcaller import LlmCaller
from core.getmetadata import get_metadata      # 13
from core.globalupdate import update_global    # 14
from core.scoreaggregator import SectionScoreAggregator
class AnalyseRequest(BaseModel):
    JSON: str | None = None

app = FastAPI(
    title="CV/Resume Evaluation API",
    version="0.1.5",
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
@app.get("/", tags=["Health & Metadata"])
def health_fastapi():
    return {"status": "ok", "service": "FastAPI"}

### Health & Metadata.API:02 ################################################
caller = LlmCaller()
agg = SectionScoreAggregator()

@app.get("/health/gemini", tags=["Health & Metadata"])
def health_gemini():
    res = caller.call(
        "Return this as JSON: {'status': 'connected'}"
    )
    return {"response":res}

### Health & Metadata.API:03 ################################################
@app.get("/health/metadata", tags=["Health & Metadata"])
def metadata():
    return {"message":get_metadata()}

#############################################################################
#############################################################################

### Debug & Lab #############################################################
from core.promptbuilder import PromptBuilder
from fastapi import Response

### Debug & Lab.API:04 ######################################################
class PromptBuilderPayload(BaseModel):
        section  : str  | None = Field (default = "Summary")
        criteria : list | None = Field (default = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"])

@app.post("/test/prompt", tags=["Debug & Lab"])
def prompt_lab(payload:PromptBuilderPayload):
    pl = payload.model_dump()
    pb = PromptBuilder(
        section  = pl["section"],
        criteria = pl["criteria"],
        cvresume = "resume_json"
        )
    prompt = pb.build()
    return Response(content=prompt, media_type="text/plain")

### Debug & Lab.API:05 ######################################################
from core.helper import Helper
mock_data = Helper.load_json("src/mock/resume1.json")
@app.get("/evaluation/logexamplepayload",tags=["Debug & Lab"])
def show_example_of_payload_json_body():
    return {"response":mock_data}

### Debug & Lab.API:06 ######################################################
@app.get("/evaluation/callexamplepayload",tags=["Debug & Lab"])
def call_example_payload_json_body():
    test_payload = {"resume_json": mock_data}
    p1 = PromptBuilder(
        section  = "Profile",
        criteria = ["Completeness", "ContentQuality"],
        cvresume = test_payload["resume_json"]
    )
    prompt = p1.build()
    res = caller.call(prompt)
    return {"response": res}

### Debug & Lab.API:07 ######################################################
@app.put("/config/prompt", tags=["Debug & Lab"])
def Xupdate_prompt():
    return {"message": "prompt.yaml updated"}
#############################################################################
#############################################################################

### Evaluation ##############################################################
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

### Evaluation.API:07 #######################################################
@app.post("/evaluation/profile", tags=["Evaluation"])
def evaluation_profile(payload: EvaluationPayload):
    resume_json = payload.resume_json
    p1 = PromptBuilder(
        section  = "Profile",
        criteria = ["Completeness", "ContentQuality"],
        cvresume = resume_json
    )
    prompt = p1.build()
    op1 = caller.call(prompt)
    s1 = agg.aggregate(op1)
    return {"response": s1}

### Evaluation.API:08 #######################################################
@app.post("/evaluation/summary", tags=["Evaluation"])
def evaluate_summary(payload: EvaluationPayload):
    resume_json = payload.resume_json
    p2 = PromptBuilder( 
        section  = "Summary", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        cvresume = resume_json
    )
    prompt = p2.build()
    op2 = caller.call(prompt)
    s2 = agg.aggregate(op2)
    return {"response": s2}

### Evaluation.API:09 #######################################################
@app.post("/evaluation/education", tags=["Evaluation"])
def evaluate_education(payload: EvaluationPayload):
    resume_json = payload.resume_json
    p3 = PromptBuilder( 
        section  = "Education", 
        criteria = ["Completeness","RoleRelevance"],
        cvresume = resume_json
    )
    prompt3 = p3.build()
    op3 = caller.call(prompt3)
    s3 = agg.aggregate(op3)
    return {"response": s3}

### Evaluation.API:10 #######################################################
@app.post("/evaluation/experience", tags=["Evaluation"])
def evaluate_experience(payload: EvaluationPayload):
    resume_json = payload.resume_json
    p4 = PromptBuilder( 
        section  = "Experience", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        cvresume = resume_json
    )
    prompt4 = p4.build()
    op4 = caller.call(prompt4)
    s4 = agg.aggregate(op4)
    return {"response": s4}


### Evaluation.API:11 #######################################################
@app.post("/evaluation/activities", tags=["Evaluation"])
def evaluate_activities(payload: EvaluationPayload):
    resume_json = payload.resume_json
    p5 = PromptBuilder( 
        section  = "Activities", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length"],
        cvresume = resume_json
    )
    prompt5 = p5.build()
    op5 = caller.call(prompt5)
    s5 = agg.aggregate(op5)
    return {"response": s5}


### Evaluation.API:12 #######################################################
@app.post("/evaluation/skills", tags=["Evaluation"])
def evaluate_skills(payload: EvaluationPayload):
    resume_json = payload.resume_json
    p6 = PromptBuilder( 
        section  = "Skills", 
        criteria = ["Completeness","Length","RoleRelevance"],
        cvresume = resume_json
    )
    prompt6 = p6.build()
    op6 = caller.call(prompt6)
    s6 = agg.aggregate(op6)
    return {"response": s6}

#############################################################################
#############################################################################

### Composite evaluation ####################################################
from core.globalaggregator import GlobalAggregator

@ app.post("/evaluation/final-resume-score", tags=["Composite Evaluation"])
def evaluate_resume(payload: EvaluationPayload):
    resume_json = payload.resume_json
    p1 = PromptBuilder(
        section  = "Profile",
        criteria = ["Completeness", "ContentQuality"],
        cvresume = resume_json
    )
    prompt1 = p1.build()
    
    p2 = PromptBuilder( 
        section  = "Summary", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        cvresume = resume_json
    )
    prompt2 = p2.build()
    
    p3 = PromptBuilder( 
        section  = "Education", 
        criteria = ["Completeness","RoleRelevance"],
        cvresume = resume_json
    )
    prompt3 = p3.build()

    p4 = PromptBuilder( 
        section  = "Experience", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        cvresume = resume_json
    )
    prompt4 = p4.build()
    
    p5 = PromptBuilder( 
        section  = "Activities", 
        criteria = ["Completeness", "ContentQuality","Grammar","Length"],
        cvresume = resume_json
    )
    prompt5 = p5.build()
    
    p6 = PromptBuilder( 
        section  = "Skills", 
        criteria = ["Completeness","Length","RoleRelevance"],
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

    return {"response": output}

#############################################################################
#############################################################################


### Admin ####################################################################
### Admin.API:13 #############################################################
# 13. Update models x
class test(BaseModel):
    provider         :str | None = Field (default="google")
    embedding_model  :str | None = Field (default="text-embedding-004")
    generation_model :str | None = Field (default="gemini-2.5-flash")

from core.modelupdate import update_model
@app.put("/config/model",tags=["Admin"])
def update_model_config(payload:test):
    update_model(payload.model_dump())
    return {
        "status":"updated",
        "payload":payload
    }
### Admin.API14 ##############################################################
# 14. Update global x
class SettingConfig(BaseModel):
    GOOGLE_API_KEY: Optional[str] = Field(default=None, example="AIza-xxxx")
class PricingModel(BaseModel):
    input_per_million: Optional[float] = Field(default=None, example=0.10)
    output_per_million: Optional[float] = Field(default=None, example=0.40)
class PricingConfig(BaseModel):
    gemini_2_5_flash: Optional[PricingModel] = Field(
        default=None,
        example={
            "input_per_million": 0.10,
            "output_per_million": 0.40
        }
    )
class ScoringConfig(BaseModel):
    final_score_max: Optional[int] = Field(default=None, example=100)
    normalize: Optional[bool] = Field(default=None, example=True)
    round_digits: Optional[int] = Field(default=None, example=2)
    aggregation_method: Optional[str] = Field(default=None, example="weighted_sum")
class GlobalUpdatePayload(BaseModel):
    version: Optional[str] = Field(default="global_v1", example="global_v1")
    setting: Optional[SettingConfig] = Field(default=None)
    pricing: Optional[PricingConfig] = Field(default=None)
    scoring: Optional[ScoringConfig] = Field(default=None)

@app.put("/config/global",tags=["Admin"])
def update_global_config(payload:GlobalUpdatePayload):
    updated = update_global(payload.model_dump())
    return {
        "status":"updated",
        "config":updated
    }

### Admin.API15 ##############################################################
from core.weightupdate import update_weight
class Criteria(BaseModel):
    Completeness: Optional[int]   = Field(default=10)
    ContentQuality: Optional[int] = Field(default=10)
    Grammar: Optional[int]        = Field(default=10)
    Length: Optional[int]         = Field(default=10)
    RoleRelevance: Optional[int]  = Field(default=10)
    section_weight: Optional[float] = Field(default=0.1)
class ResumeParts(BaseModel):
    Profile: Optional[Criteria]  = Field(
        default = None,
        example={
            "Completeness": 10,
            "ContentQuality": 10,
            "Grammar": 0,
            "Length": 0,
            "RoleRelevance": 0,
            "section_weight": 0.1
        })
    Summary: Optional[Criteria]  = Field(
        default = None,
        example={
            "Completeness": 10,
            "ContentQuality": 10,
            "Grammar": 10,
            "Length": 10,
            "RoleRelevance": 10,
            "section_weight": 0.1
        })
    Education: Optional[Criteria]  = Field(
        default = None,
        example={
            "Completeness": 10,
            "ContentQuality": 0,
            "Grammar": 0,
            "Length": 0,
            "RoleRelevance": 10,
            "section_weight": 0.2
        })
    Experience: Optional[Criteria]  = Field(
        default = None,
        example={
            "Completeness": 10,
            "ContentQuality": 10,
            "Grammar": 10,
            "Length": 10,
            "RoleRelevance": 10,
            "section_weight": 0.2
        })
    Activities: Optional[Criteria]  = Field(
        default = None,
        example={
            "Completeness": 10,
            "ContentQuality": 10,
            "Grammar": 10,
            "Length": 10,
            "RoleRelevance": 10,
            "section_weight": 0.2
        })
    Skills: Optional[Criteria]  = Field(
        default = None,
        example={
            "Completeness": 10,
            "ContentQuality": 0,
            "Grammar": 0,
            "Length": 10,
            "RoleRelevance": 10,
            "section_weight": 0.2
        })
class WeightUpdatePayload(BaseModel):
    version: Optional[str] = Field(default="weights_v1")
    weights: Optional[ResumeParts]   = Field(default=None)

@app.put("/config/weight",tags=['Admin'])
def update_global_config(payload:WeightUpdatePayload):
    updated = update_weight(payload.model_dump())
    return {
        "status":"updated",
        "config":updated
    }



