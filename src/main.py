from fastapi import FastAPI,Response,Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from time import time
import asyncio

from core.helper import Helper
from core.llmcaller import LlmCaller
from core.getmetadata import get_metadata
from core.promptbuilder import PromptBuilder
from core.aggregator import SectionScoreAggregator, GlobalAggregator
from core.logcost import estimate_gemini_cost
from core.llm_excel_logger import log_llm_usage
from core.configupdate import update_global,update_model,update_weight,update_prompt

from schema.lab_schema import PromptBuilderPayload,PromptUpdatePayload,PROMPT_V2_EXAMPLE
from schema.evaluation_schema import EvaluationPayload
from schema.admin_schema import ModelUpdatePayload, GlobalUpdatePayload, WeightUpdatePayload


app = FastAPI(
    title="CV/Resume Evaluation API",
    version="0.1.5",
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
usd2bath  = Helper.load_yaml("src/config/global.yaml")['currency']['USD_to_THB']
log_digit = Helper.load_yaml("src/config/global.yaml")['logging']['logging_round_digit']
### Health & Metadata #######################################################
### Health & Metadata.API:01 ################################################
@app.get(
    "/", 
    tags=["Health & Metadata"],
    description="API:01 Basic health check endpoint for uptime monitoring."
)

def health_fastapi():
    start_time  = time()
    # for i in range(100000):
    #     print(i)
    finish_time = time()
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
    description="API:02 Connectivity health check for Gemini LLM service. Verifies API availability and measures round-trip response latency."
)

def health_gemini():
    start_time = time()
    res,_ = caller.call(
        '''This is just test connect to Gemini model 
        just Return this as JSON: 
        {
            "response": {
                "section": "ConnectionStatus",
                "scores": {
                "GeminiModelStatus": {
                    "score": 5,
                    "feedback": "Status: connected."
                    }
                }
            }
        }
        only'''
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
    description="API:03 Metadata health check endpoint. Verifies metadata retrieval functionality and measures response latency."
)

def metadata():
    start_time = time()
    resp   = get_metadata()
    finish_time   = time()
    return {
        "message":resp,
        "response_time" : f"{finish_time - start_time:.5f} s"
        }

#############################################################################
#############################################################################

### Debug & Lab #############################################################
### Debug & Lab.API:04 ######################################################
@app.get(
    "/evaluation/logexamplepayload",
    tags=["Debug & Lab"],
    description="API:04 Debug endpoint that returns a mock resume JSON payload as an example request body for evaluation APIs."
)

def show_example_of_payload_json_body():
    return {
        "response":mock_data
        }


### Debug & Lab.API:05 ######################################################
@app.get(
    "/evaluation/callexamplepayload",
    tags=["Debug & Lab"],
    description="API:05 Debug endpoint that builds a sample prompt from mock resume data and invokes the LLM to demonstrate an end-to-end evaluation flow with response latency."
)
def call_example_payload_json_body():
    test_payload = {
        "resume_json": mock_data
        }
    start_time = time()
    p1 = PromptBuilder(
        section    = "Profile",
        criteria   = ["Completeness", "ContentQuality"],
        targetrole = "data scientist",
        cvresume   = test_payload["resume_json"]
    )
    prompt = p1.build()
    res,raw = caller.call(prompt)
    finish_time = time()

    usage_time = finish_time - start_time
    cost = estimate_gemini_cost(raw)
    ip = {
            "id":"API05",
            "output_lange":"-",
            "prompt_length_chars":len(prompt),
            "input_tokens":cost['prompt_tokens'],
            "output_tokens":cost['output_tokens'],
            "total_tokens":cost['prompt_tokens']+cost['output_tokens'],
            "input_cost":cost['input_cost'],
            "output_cost":cost['output_cost'],
            "estimated_cost_usd":cost['total_cost'],
            "estimated_cost_thd": round(cost['total_cost']*usd2bath,log_digit),
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)

    return {
        "response": res,
        "response_time_sec" : f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost['total_cost']*usd2bath):.5f} ฿"
        }

### Debug & Lab.API:06 ######################################################
@app.post(
    "/test/prompt",
    tags=["Debug & Lab"],
    description="API:06 Debug endpoint for generating and inspecting a prompt using provided section, criteria, and target role parameters without invoking the LLM."
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
    description = "API:07 Update the prompt configuration (prompt.yaml) used by the CV Evaluation service."
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
    description="API:08 Evaluates the Profile section of a resume using predefined criteria and role context, returning aggregated LLM-based scores with processing latency."
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
    op1,raw = caller.call(prompt)
    s1 = agg.aggregate(op1)
    finish_time = time()

    usage_time = finish_time - start_time
    cost = estimate_gemini_cost(raw)
    ip = {
            "id":"API08",
            "output_lange":payload.output_lang,
            "prompt_length_chars":len(prompt),
            "input_tokens" :cost['prompt_tokens'],
            "output_tokens":cost['output_tokens'],
            "total_tokens" :cost['prompt_tokens']+cost['output_tokens'],
            "input_cost"  :cost['input_cost'],
            "output_cost" :cost['output_cost'],
            "estimated_cost_usd":cost['total_cost'],
            "estimated_cost_thd":cost['total_cost']*usd2bath,
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)    

    return {
        "response": s1,
        "response_time": f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost['total_cost']*usd2bath):.5f} ฿"
    }

# def evaluation_profile(payload: EvaluationPayload):
#     Inlang = payload.output_lang
#     p1 = PromptBuilder(
#         section     = "Profile",
#         criteria    = ["Completeness", "ContentQuality"],
#         targetrole  = payload.target_role,
#         cvresume    = payload.resume_json,
#         output_lang = Inlang 
#     )
#     prompt = p1.build()
#     s1,meta = caller.run_llm(
#         prompt = prompt,
#         api_id = 'API08',
#         Oplang = Inlang
#         )
#     return {
#         "response": s1,
#         "response_time": f"{meta['usage_time']:.5f} s",
#         "estimated_cost_thd": f"{meta['total_cost']:.5f} ฿"
#     }
### Evaluation.API:09 #######################################################
@app.post(
    "/evaluation/summary",
    tags=["Evaluation"],   
    description="API:09 Evaluates the Summary section of a resume against multiple quality and relevance criteria, returning aggregated LLM-based scores with processing latency."
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
    op2,raw = caller.call(prompt)
    s2 = agg.aggregate(op2)
    finish_time   = time()

    usage_time = finish_time - start_time
    cost = estimate_gemini_cost(raw)

    ip = {
            "id":"API09",
            "output_lange":payload.output_lang,
            "prompt_length_chars":len(prompt),
            "input_tokens" :cost['prompt_tokens'],
            "output_tokens":cost['output_tokens'],
            "total_tokens" :cost['prompt_tokens']+cost['output_tokens'],
            "input_cost"  :cost['input_cost'],
            "output_cost" :cost['output_cost'],
            "estimated_cost_usd":cost['total_cost'],
            "estimated_cost_thd":cost['total_cost']*usd2bath,
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)    

    return {
        "response": s2,
        "response_time" : f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost['total_cost']*usd2bath):.5f} ฿"
        }

### Evaluation.API:10 #######################################################
@app.post(
    "/evaluation/education",
    tags=["Evaluation"],
    description="API:10 Evaluates the Education section of a resume for completeness and role relevance, returning aggregated LLM-based scores with processing latency."
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
    op3,raw = caller.call(prompt3)
    s3 = agg.aggregate(op3)
    finish_time   = time()

    usage_time = finish_time - start_time
    cost = estimate_gemini_cost(raw)
    ip = {
            "id":"API10",
            "output_lange":payload.output_lang,
            "prompt_length_chars":len(prompt3),
            "input_tokens" :cost['prompt_tokens'],
            "output_tokens":cost['output_tokens'],
            "total_tokens" :cost['prompt_tokens']+cost['output_tokens'],
            "input_cost"  :cost['input_cost'],
            "output_cost" :cost['output_cost'],
            "estimated_cost_usd":cost['total_cost'],
            "estimated_cost_thd":cost['total_cost']*usd2bath,
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)    

    return {
        "response": s3,
        "response_time" : f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost['total_cost']*usd2bath):.5f} ฿"
        }

### Evaluation.API:11 #######################################################
@app.post(
    "/evaluation/experience",
    tags=["Evaluation"],
    description="API:11 Evaluates the Experience section of a resume using content quality, completeness, grammar, length, and role relevance criteria, returning aggregated LLM-based scores with processing latency."
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
    op4,raw = caller.call(prompt4)
    s4 = agg.aggregate(op4)
    finish_time   = time()

    usage_time = finish_time - start_time
    cost = estimate_gemini_cost(raw)
    ip = {
            "id":"API11",
            "output_lange":payload.output_lang,
            "prompt_length_chars":len(prompt4),
            "input_tokens" :cost['prompt_tokens'],
            "output_tokens":cost['output_tokens'],
            "total_tokens" :cost['prompt_tokens']+cost['output_tokens'],
            "input_cost"  :cost['input_cost'],
            "output_cost" :cost['output_cost'],
            "estimated_cost_usd":cost['total_cost'],
            "estimated_cost_thd":cost['total_cost']*usd2bath,
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)    

    return {
        "response": s4,
        "response_time" : f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost['total_cost']*usd2bath):.5f} ฿"
        }


### Evaluation.API:12 #######################################################
@app.post(
    "/evaluation/activities",
    tags=["Evaluation"],
    description="API:12 Evaluates the Activities section of a resume based on completeness, content quality, grammar, and length criteria, returning aggregated LLM-based scores with processing latency."
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
    op5,raw = caller.call(prompt5)
    s5 = agg.aggregate(op5)
    finish_time   = time()

    usage_time = finish_time - start_time
    cost = estimate_gemini_cost(raw)
    ip = {
            "id":"API12",
            "output_lange":payload.output_lang,
            "prompt_length_chars":len(prompt5),
            "input_tokens" :cost['prompt_tokens'],
            "output_tokens":cost['output_tokens'],
            "total_tokens" :cost['prompt_tokens']+cost['output_tokens'],
            "input_cost"  :cost['input_cost'],
            "output_cost" :cost['output_cost'],
            "estimated_cost_usd":cost['total_cost'],
            "estimated_cost_thd":cost['total_cost']*usd2bath,
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)    

    return {
        "response": s5,
        "response_time" : f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost['total_cost']*usd2bath):.5f} ฿"
        }


### Evaluation.API:13 #######################################################
@app.post(
    "/evaluation/skills",
    tags=["Evaluation"],
    description="API:13 Evaluates the Skills section of a resume based on completeness, length, and role relevance criteria, returning aggregated LLM-based scores with processing latency."
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
    op6,raw = caller.call(prompt6)
    s6 = agg.aggregate(op6)
    finish_time   = time()

    usage_time = finish_time - start_time
    cost = estimate_gemini_cost(raw)
    ip = {
            "id":"API13",
            "output_lange":payload.output_lang,
            "prompt_length_chars":len(prompt6),
            "input_tokens" :cost['prompt_tokens'],
            "output_tokens":cost['output_tokens'],
            "total_tokens" :cost['prompt_tokens']+cost['output_tokens'],
            "input_cost"  :cost['input_cost'],
            "output_cost" :cost['output_cost'],
            "estimated_cost_usd":cost['total_cost'],
            "estimated_cost_thd":cost['total_cost']*usd2bath,
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)    

    return {
        "response": s6,
        "response_time" : f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost['total_cost']*usd2bath):.5f} ฿"
        }

#############################################################################
#############################################################################

### Composite evaluation ####################################################
### Composite evaluation.API:14 #############################################

@app.post(
    "/evaluation/final-resume-score",
    tags=["Composite Evaluation"],
    description="API:14 Performs a full resume evaluation by scoring all major sections and aggregating them into a final composite resume score with overall processing latency."
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

    op1,raw1 = caller.call(prompt1)
    op2,raw2 = caller.call(prompt2)
    op3,raw3 = caller.call(prompt3)
    op4,raw4 = caller.call(prompt4)
    op5,raw5 = caller.call(prompt5)
    op6,raw6 = caller.call(prompt6)

    s1 = agg.aggregate(op1)
    s2 = agg.aggregate(op2)
    s3 = agg.aggregate(op3)
    s4 = agg.aggregate(op4)
    s5 = agg.aggregate(op5)
    s6 = agg.aggregate(op6)

    x = GlobalAggregator(SectionScoreAggregator_output = [s1,s2,s3,s4,s5,s6])

    output = x.fn0()

    finish_time   = time()
    usage_time = finish_time - start_time
    cost1 = estimate_gemini_cost(raw1)
    cost2 = estimate_gemini_cost(raw2)
    cost3 = estimate_gemini_cost(raw3)
    cost4 = estimate_gemini_cost(raw4)
    cost5 = estimate_gemini_cost(raw5)
    cost6 = estimate_gemini_cost(raw6)
    ip = {
            "id":"API14",
            "output_lange":payload.output_lang,
            "prompt_length_chars":len(prompt1)+len(prompt2)+len(prompt3)+len(prompt4)+len(prompt5)+len(prompt6),
            "input_tokens" :cost1['prompt_tokens']+cost2['prompt_tokens']+cost3['prompt_tokens']+cost4['prompt_tokens']+cost5['prompt_tokens']+cost6['prompt_tokens'],
            "output_tokens":cost1['output_tokens']+cost2['output_tokens']+cost3['output_tokens']+cost4['output_tokens']+cost5['output_tokens']+cost6['output_tokens'],
            "total_tokens" :cost1['prompt_tokens']+cost2['prompt_tokens']+cost3['prompt_tokens']+cost4['prompt_tokens']+cost5['prompt_tokens']+cost6['prompt_tokens']+cost1['output_tokens']+cost2['output_tokens']+cost3['output_tokens']+cost4['output_tokens']+cost5['output_tokens']+cost6['output_tokens'],
            "input_cost" :cost1['input_cost']+cost2['input_cost']+cost3['input_cost']+cost4['input_cost']+cost5['input_cost']+cost6['input_cost'],
            "output_cost":cost1['output_cost']+cost2['output_cost']+cost3['output_cost']+cost4['output_cost']+cost5['output_cost']+cost6['output_cost'],
            "estimated_cost_usd":cost1['total_cost']+cost2['total_cost']+cost3['total_cost']+cost4['total_cost']+cost5['total_cost']+cost6['total_cost'],
            "estimated_cost_thd":(cost1['total_cost']+cost2['total_cost']+cost3['total_cost']+cost4['total_cost']+cost5['total_cost']+cost6['total_cost'])*usd2bath,
            "response_time_sec": round(usage_time, log_digit)
        }
    log_llm_usage(ip)    

    return {
        "response": output,
        "response_time" : f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{(cost1['total_cost']+cost2['total_cost']+cost3['total_cost']+cost4['total_cost']+cost5['total_cost']+cost6['total_cost'])*usd2bath:.5f} ฿"
    }

### Composite evaluation ####################################################
### Composite evaluation.API:14 #############################################
@app.post(
    "/evaluation/final-resume-score-async",
    tags=["Composite Evaluation"],
    description="API:14-2 Full resume evaluation (async parallel LLM calls)"
)
async def evaluate_resume(payload: EvaluationPayload):
    start_time = time()

    resume_json = payload.resume_json
    targetrole  = payload.target_role
    output_lang = payload.output_lang

    builders = [
        PromptBuilder("Profile",    ["Completeness","ContentQuality"], targetrole, resume_json, output_lang=output_lang),
        PromptBuilder("Summary",    ["Completeness","ContentQuality","Grammar","Length","RoleRelevance"], targetrole, resume_json, output_lang=output_lang),
        PromptBuilder("Education",  ["Completeness","RoleRelevance"], targetrole, resume_json, output_lang=output_lang),
        PromptBuilder("Experience", ["Completeness","ContentQuality","Grammar","Length","RoleRelevance"], targetrole, resume_json, output_lang=output_lang),
        PromptBuilder("Activities", ["Completeness","ContentQuality","Grammar","Length"], targetrole, resume_json, output_lang=output_lang),
        PromptBuilder("Skills",     ["Completeness","Length","RoleRelevance"], targetrole, resume_json, output_lang=output_lang),
    ]

    prompts = [b.build() for b in builders]

    results = await asyncio.gather(                         # sequencial call -> async gathering call
        *[caller.call_async(p) for p in prompts]
    )

    parsed_outputs = []
    raw_outputs    = []

    for parsed, raw in results:
        parsed_outputs.append(parsed)
        raw_outputs.append(raw)

    Ss = [agg.aggregate(s) for s in parsed_outputs]

    final = GlobalAggregator(
        SectionScoreAggregator_output=Ss
    ).fn0()

    finish_time = time()
    usage_time  = finish_time - start_time

    # cost aggregation (unchanged logic)
    costs = [estimate_gemini_cost(r) for r in raw_outputs]

    ip = {
        "id": "API14-2",
        "output_lange":payload.output_lang,
        "prompt_length_chars": sum(len(p) for p in prompts),
        "input_tokens": sum(c["prompt_tokens"] for c in costs),
        "output_tokens": sum(c["output_tokens"] for c in costs),
        "total_tokens": sum(c["prompt_tokens"] + c["output_tokens"] for c in costs),
        "input_cost": sum(c["input_cost"] for c in costs),
        "output_cost": sum(c["output_cost"] for c in costs),
        "estimated_cost_usd": sum(c["total_cost"] for c in costs),
        "estimated_cost_thd": sum(c["total_cost"] for c in costs) * usd2bath,
        "response_time_sec": round(usage_time, log_digit)
    }

    log_llm_usage(ip)

    return {
        "response": final,
        "response_time": f"{usage_time:.5f} s",
        "estimated_cost_thd": f"{sum(c["total_cost"] for c in costs) * usd2bath:.5f} ฿",
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
def update_weight_config(payload:WeightUpdatePayload):
    updated = update_weight(payload.model_dump())
    return {
        "status":"updated",
        "config":updated
    }



