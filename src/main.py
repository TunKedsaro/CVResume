from fastapi import FastAPI,Response,Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from time import time

from core.helper import Helper
from core.llmcaller import LlmCaller
from core.getmetadata import get_metadata
from core.globalupdate import update_global
from core.scoreaggregator import SectionScoreAggregator
from core.promptbuilder import PromptBuilder
from core.promptupdate import update_prompt
from core.globalaggregator import GlobalAggregator
from core.modelupdate import update_model
from core.weightupdate import update_weight

from schema.lab_schema import PromptBuilderPayload,PromptUpdatePayload,PROMPT_V2_EXAMPLE
from schema.evaluation_schema import EvaluationPayload
from schema.admin_schema import ModelUpdatePayload, GlobalUpdatePayload, WeightUpdatePayload

app = FastAPI(
    title="CV/Resume Evaluation API",
    version="0.1.3",
    description=(
        "Microservices for CV/Resume evaluation (In progress krub)"
        "<br>"
        f"Last time Update : 2025-12-20 11:00:15.996293+07:00"
        # f"Last time Update : {str(datetime.now(tz=(timezone(timedelta(hours=7)))))}"
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

caller    = LlmCaller()
agg       = SectionScoreAggregator()
mock_data = Helper.load_json("src/mock/resume3.json")   

### Health & Metadata #######################################################
### Health & Metadata.API:01 ################################################
@app.get(
    "/", 
    tags=["Health & Metadata"],
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
@app.get(
    "/health/gemini", 
    tags=["Health & Metadata"],
    description="Connectivity health check for Gemini LLM service. Verifies API availability and measures round-trip response latency."
)

def health_gemini():
    start_time = time()
    res = caller.call(
        "Return this as JSON: {'status': 'connected'}"
    )
    finish_time = time()
    return {
        "response":res,
        "response_time" : f"{finish_time - start_time:.5f} s"
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
    return {
        "message":get_metadata(),
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

#############################################################################
### Debug & Lab #############################################################
### Debug & Lab.API:04 ######################################################
@app.get(
    "/evaluation/logexamplepayload",
    tags=["Debug & Lab"],
    description="Debug endpoint that returns a mock resume JSON payload as an example request body for evaluation APIs."
)

def show_example_of_payload_json_body():
    return {
        "response":mock_data
        }

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
        section    = "Profile",
        criteria   = ["Completeness", "ContentQuality"],
        targetrole = "data scientist",
        cvresume   = test_payload["resume_json"]
    )
    prompt = p1.build()
    res = caller.call(prompt)
    finish_time = time()
    return {
        "response": res,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

### Debug & Lab.API:06 ######################################################
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
@app.put(
    "/config/prompt",
    tags=["Debug & Lab"],
    description = "Update the prompt configuration (prompt.yaml) used by the CV Evaluation service."
)
def update_prompt_config(
    payload: PromptUpdatePayload = Body(example=PROMPT_V2_EXAMPLE)
):
    payload_dict = payload.model_dump(exclude_none=True)
    updated_yaml = update_prompt(payload_dict)
    return {
        "message": "prompt.yaml updated !!!",
        "updated_keys": list(payload_dict.keys()),
        "config": updated_yaml
    }

#############################################################################
#############################################################################

### Evaluation ##############################################################
### Evaluation.API:08 #######################################################
@app.post(
    "/evaluation/profile",
    tags=["Evaluation"],
    description="Evaluates the Profile section of a resume using predefined criteria and role context, returning aggregated LLM-based scores with processing latency."
)
def evaluation_profile(payload: EvaluationPayload):
    start_time = time()
    p1 = PromptBuilder(
        section     = "Profile",
        criteria    = ["Completeness", "ContentQuality"],
        targetrole  = payload.target_role,
        cvresume    = payload.resume_json,
        output_lang = payload.output_lang 
    )
    prompt = p1.build()
    op1 = caller.call(prompt)
    s1 = agg.aggregate(op1)
    finish_time = time()
    return {
        "response": s1,
        "response_time": f"{finish_time - start_time:.5f} s"
    }

### Evaluation.API:09 #######################################################
@app.post(
    "/evaluation/summary",
    tags=["Evaluation"],   
    description="Evaluates the Summary section of a resume against multiple quality and relevance criteria, returning aggregated LLM-based scores with processing latency."
)

def evaluate_summary(payload: EvaluationPayload):
    start_time = time()
    p2 = PromptBuilder( 
        section     = "Summary", 
        criteria    = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole  = payload.target_role,
        cvresume    = payload.resume_json,
        output_lang = payload.output_lang 
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
    p3 = PromptBuilder( 
        section     = "Education", 
        criteria    = ["Completeness","RoleRelevance"],
        targetrole  = payload.target_role,
        cvresume    = payload.resume_json,
        output_lang = payload.output_lang 
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
    p4 = PromptBuilder( 
        section     = "Experience", 
        criteria    = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole  = payload.target_role,
        cvresume    = payload.resume_json,
        output_lang = payload.output_lang 
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
    p5 = PromptBuilder( 
        section     = "Activities", 
        criteria    = ["Completeness", "ContentQuality","Grammar","Length"],
        targetrole  = payload.target_role,
        cvresume    = payload.resume_json,
        output_lang = payload.output_lang 
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
    p6 = PromptBuilder( 
        section     = "Skills", 
        criteria    = ["Completeness","Length","RoleRelevance"],
        targetrole  = payload.target_role,
        cvresume    = payload.resume_json,
        output_lang = payload.output_lang 
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
@app.post(
    "/evaluation/final-resume-score",
    tags=["Composite Evaluation"],
    description="Performs a full resume evaluation by scoring all major sections and aggregating them into a final composite resume score with overall processing latency."
)

def evaluate_resume(payload: EvaluationPayload):
    start_time  = time()
    resume_json = payload.resume_json
    targetrole  = payload.target_role
    output_lang = payload.output_lang 

    p1 = PromptBuilder(
        section     = "Profile",
        criteria    = ["Completeness", "ContentQuality"],
        targetrole  = targetrole,
        cvresume    = resume_json,
        output_lang = output_lang 
    )
    prompt1 = p1.build()
    
    p2 = PromptBuilder( 
        section     = "Summary", 
        criteria    = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole  = targetrole,
        cvresume    = resume_json,
        output_lang = output_lang 
    )
    prompt2 = p2.build()
    
    p3 = PromptBuilder( 
        section     = "Education", 
        criteria    = ["Completeness","RoleRelevance"],
        targetrole  = targetrole,
        cvresume    = resume_json,
        output_lang = output_lang 
    )
    prompt3 = p3.build()

    p4 = PromptBuilder( 
        section     = "Experience", 
        criteria    = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"],
        targetrole  = targetrole,
        cvresume    = resume_json,
        output_lang = output_lang 
    )
    prompt4 = p4.build()
    
    p5 = PromptBuilder( 
        section     = "Activities", 
        criteria    = ["Completeness", "ContentQuality","Grammar","Length"],
        targetrole  = targetrole,
        cvresume    = resume_json,
        output_lang = output_lang 
    )
    prompt5 = p5.build()
    
    p6 = PromptBuilder( 
        section     = "Skills", 
        criteria    = ["Completeness","Length","RoleRelevance"],
        targetrole  = targetrole,
        cvresume    = resume_json,
        output_lang = output_lang 
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
@app.put(
    "/config/model",
    tags=["Admin"],
    description="Update the prompt configuration (model.yaml) used by the CV Evaluation service"
)
def update_model_config(payload:ModelUpdatePayload):
    update_model(payload.model_dump())
    return {
        "status":"updated",
        "payload":payload
    }
### Admin.API16 ##############################################################
# 14. Update global x
@app.put(
    "/config/global",
    tags=["Admin"],
    description="Update the prompt configuration (global.yaml) used by the CV Evaluation service"
)
def update_global_config(payload:GlobalUpdatePayload):
    updated = update_global(payload.model_dump())
    return {
        "status":"updated",
        "config":updated
    }

### Admin.API17 ##############################################################
@app.put(
    "/config/weight",
    tags=['Admin'],
    description="Update the prompt configuration (weight.yaml) used by the CV Evaluation service"
)
def update_global_config(payload:WeightUpdatePayload):
    updated = update_weight(payload.model_dump())
    return {
        "status":"updated",
        "config":updated
    }



