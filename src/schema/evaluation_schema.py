from pydantic import BaseModel, Field
from typing import Optional,Literal


class EvaluationPayload(BaseModel):
    output_lang: Literal["en","th"] = Field(
        default = "en",
        description = "Output language for feedback text"
    )
    target_role: str  | None = Field (default="Data scientist")
    resume_json: dict | None = Field (default="resume_json")