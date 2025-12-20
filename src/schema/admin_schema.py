from pydantic import BaseModel, Field
from typing import Optional,Literal,Dict

class ModelUpdatePayload(BaseModel):
    provider         :str | None = Field (default="google")
    embedding_model  :str | None = Field (default="text-embedding-004")
    generation_model :str | None = Field (default="gemini-2.5-flash")





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