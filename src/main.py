from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta

from core.llmcaller import LlmCaller
from core.getmetadata import get_metadata

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
##############################################################################
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

# 13. Update models x
class test(BaseModel):
    provider         :str | None = Field (default="google")
    embedding_model  :str | None = Field (default="text-embedding-004")
    generation_model :str | None = Field (default="gemini-2.5-flash")

from core.modelupdate import update_model
@app.put("/config/model",tags=["admin"])
def updatemodel(payload:test):
    update_model(payload.model_dump())
    return {
        "status":"updated",
        "payload":payload
    }