from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from typing import Optional

from core.llmcaller import LlmCaller
from core.getmetadata import get_metadata      # 13
from core.globalupdate import update_global    # 14

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
# Health & Metadata
# 01. Health x / 
@app.get("/", tags=["Health & Metadata"])
def health_fastapi():
    return {"status": "ok", "service": "FastAPI"}

caller = LlmCaller()
# 02. Gemini health x
@app.get("/health/gemini", tags=["Health & Metadata"])
def health_gemini():
    res = caller.call(
        "Return this as JSON: {'status': 'connected'}"
    )
    return {"response":res}

# 03. Metadata
@app.get("/health/metadata", tags=["Health & Metadata"])
def metadata():
    return {"message":get_metadata()}

### Admin ####################################################################
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
            "Grammar": 10,
            "Length": 10,
            "RoleRelevance": 10,
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
            "ContentQuality": 10,
            "Grammar": 10,
            "Length": 10,
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
            "ContentQuality": 10,
            "Grammar": 10,
            "Length": 10,
            "RoleRelevance": 10,
            "section_weight": 0.2
        })
class WeightUpdatePayload(BaseModel):
    version: Optional[str] = Field(default="weights_v1")
    weights: Optional[ResumeParts]   = Field(default=None)
# 15. Update weight
@app.put("/config/weight",tags=['Admin'])
def update_global_config(payload:WeightUpdatePayload):
    updated = update_weight(payload.model_dump())
    return {
        "status":"updated",
        "config":updated
    }