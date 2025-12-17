# 📄 CV Evaluation API

A production-ready **LLM-powered CV / Resume Evaluation Service** built with **FastAPI**, **YAML-driven configuration**, and **Google Gemini**.

This service evaluates structured resume data across multiple sections (Profile, Summary, Education, Experience, Activities, Skills), computes section-level scores using configurable criteria, and returns a final composite resume score suitable for frontend consumption.

---

## 🚀 Key Capabilities

- Section-based CV evaluation (Profile, Summary, Education, Experience, Activities, Skills)
- Config-driven prompt generation (YAML)
- Multi-criteria scoring with weighted aggregation
- Role relevance evaluation (configurable)
- Composite resume scoring
- Latency & cost tracking per request
- Fully containerized (Docker)
- Cloud-ready (GCP Cloud Run)

---

## 🧠 Architecture Overview

High-level request flow:

```text
Client
↓
FastAPI (BFF / Orchestrator)
↓
PromptBuilder (YAML-driven)
↓
LLM Caller (Google Gemini)
↓
SectionScoreAggregator
↓
GlobalAggregator
↓
Final API Response
```


The API abstracts all internal complexity such as prompt construction, validation, scoring logic, and LLM orchestration.

---

## 📁 Project Structure

```text
C:\Users\TunKedsaro\Desktop\CVResume>docker exec -it 688bfffa322d bash
root@688bfffa322d:/code# tree
.
├── Dockerfile.dev
├── Dockerfile.prod
├── README.md
├── cloudbuild.yaml
├── design
├── docs
├── requirements.txt
└── src
    ├── config
    │   ├── global.yaml
    │   ├── model.yaml
    │   ├── prompt.yaml
    │   └── weight.yaml
    ├── core
    │   ├── __init__.py
    │   ├── getmetadata.py
    │   ├── globalaggregator.py
    │   ├── globalupdate.py
    │   ├── helper.py
    │   ├── llmcaller.py
    │   ├── modelupdate.py
    │   ├── promptbuilder.py
    │   ├── promptupdate.py
    │   ├── scoreaggregator.py
    │   └── weightupdate.py
    ├── main.py
    └── mock
        ├── resume1.json
        ├── resume2.json
        └── resume3.json
```


---

## ⚙️ Configuration System (YAML-Driven)

All evaluation logic is controlled via versioned YAML files.

### prompt.yaml
- Section instructions
- Expected content
- Few-shot examples
- Scoring criteria descriptions

### weight.yaml
- Section weights
- Criteria weights
- Composite score calculation rules

### model.yaml
- LLM provider & model selection
- Generation parameters

### global.yaml
- Feature toggles
- Runtime settings
- Environment behavior

This enables **zero-code changes** for most evaluation updates.

---

## 🧪 Sandbox (Experimentation Layer)

The `sandbox/` directory is used to:

- Test PromptBuilder output
- Debug LLM responses
- Validate scoring math
- Measure latency & token usage
- Experiment safely before promoting logic into `src/`

Rules:

- ❌ No production logic in notebooks  
- ❌ No notebook code imported into API  
- ✅ All final logic must live in `src/`

---

## 📡 API Endpoints (Summary)

| Method | Endpoint | Description |
|------|---------|-------------|
| POST | `/evaluation/profile` | Evaluate Profile section |
| POST | `/evaluation/summary` | Evaluate Summary section |
| POST | `/evaluation/education` | Evaluate Education section |
| POST | `/evaluation/experience` | Evaluate Experience section |
| POST | `/evaluation/activities` | Evaluate Activities section |
| POST | `/evaluation/skills` | Evaluate Skills section |
| POST | `/evaluation/final-resume-score` | Full composite evaluation |
| GET  | `/` | Health check |

Full request / response schema is available in:

docs/api.md

---

## 📥 Request Format (High-Level)

```text
{
  "resume_json": {
    "...": "structured resume data"
  }
}
```
- The API does not enforce a strict schema
- Input must be compatible with internal PromptBuilder logic

```json
{
  "response": {
    "final_score": 86.5,
    "sections": [
      {
        "section": "Experience",
        "total_score": 85.0,
        "scores": { ... }
      }
    ],
    "metadata": {
      "latency_ms": 53210,
      "token_usage": {
        "input": 3200,
        "output": 420
      }
    }
  }
}
```

## 🐳 Running Locally (Docker)
Development
```text
docker build -f Dockerfile.dev -t cv-eval-dev .
docker run -p 4000:4000 --env GOOGLE_API_KEY=xxx cv-eval-dev
```

```text
docker build -f Dockerfile.prod -t cv-eval-prod .
docker run -p 4000:4000 --env GOOGLE_API_KEY=xxx cv-eval-prod
```

## ☁️ Deployment
- Platform: Google Cloud Run
- Build: Cloud Build
- Registry: Artifact Registry
- Logging: Cloud Logging
- The service is stateless and horizontally scalable.