# CVResume evaluation API
## Overview
The CV/Resume Evaluation API is a microservice that evaluates resume sections using an LLM scoring pipeline.

It exposes
1. Health & metadata endpoint
    - Basic uptime & latency checks
    - Gemini connectivity check
    - Metadata retrieval check
2. Debug & Lab endpoints 
    - Return example resume  payload
    - Call LLM on example payload
    - Build and inspect raw prompts
3. Section Evaluation endpoints
    - Evaluate individual resume section (Profile, Summary, Education, Experience, Activity, Skills)
    - Return criteria-level scores + feedback
4. Composite Evaluation endpoint
    - Run all sections (Profile + Summary + Education + Experience + Activities + Skills) in one go
    - Return a final composite resume score plus section-level details

The Evaluation API hides internal complexity related to prompt building, LLM interaction, section weight aggregation, and scoring normalization.

---

## Interactive API Docs (Swagger UI)
The service exposes Swagger UI for exploration and testing:
- Swagger UI:
    https://cvresume-service-du7yhkyaqq-as.a.run.app/docs
- OpenAPI JSON (for tools/codegen):
    https://cvresume-service-du7yhkyaqq-as.a.run.app/openapi.json (if exposed)

---

## Architecture Role

```text
Client / UI / Other Backend
    |
    |  POST /evaluation/*                  (section evaluation)
    |  POST /evaluation/final-resume-score (composite)
    v
    CV/Resume Evaluation API
    ├─ Build prompts from resume_json + prompt.yaml config
    ├─ Call Gemini LLM (LlmCaller) + model.yaml config
    ├─ Aggregate scores (SectionScoreAggregator)
    ├─ Compute final resume score (GlobalAggregator) + score.yaml config
    └─ Return clean JSON response + response_time (seconds)
```

##### Upstream data source
- resume_json is typically produced by upstream systems (e.g. CV Generation Service, E-Portfolio Service)

##### Downstream dependency
- Google Gemini LLM (via internal LlmCaller wrapper)

##### Internal configuration
- YAML-based configuration: 
    - prompt.yaml : Prompt templates 
    - weight.yaml  : Scoring weights 
    - model.yaml : model config 
    - global.yaml : global thing (e.g. version, cost)

Configuration is not exposed via public endpoints in this version

---

## Base URL (Production)

[`https://cvresume-service-du7yhkyaqq-as.a.run.app`](https://cvresume-service-du7yhkyaqq-as.a.run.app)

---


## Common concepts

#### `Request` : Body → **EvaluationPayload**  
#### `Used by` : all `/evaluation/` POST endpoints.

### Example payload

```json
{
  "resume_json": { "..." : "..." }
}
```

resume_json
#### Type : object
#### Required : yes (for all evaluation endpoints)
#### Description : Structured resume payload.

  Typical fields (example only, not enforced by this service):

  - `job_id` : string
  - `template_id` : string
  - `language` : string ("en" / "th")
  - `status` : string
  - `sections` : object
      - `key`   : section names (Profile, Summary, Education, Experience, Activities, Skills)
      - `value` : section text & metadata
  - `skills` : list of skill objects

Note:
The Evaluation API does not enforce a strict schema on resume_json.
It expects a valid JSON object compatible with the internal PromptBuilder logic.

### Real resume json example:

```json
{
  "response": {
    "contact_information": {
      "name": "Juan Jose Carin",
      "email": "juanjose.carin@gmail.com",
      "phone": "650-336-4590",
      "linkedin": "linkedin.com/in/juanjosecarin",
      "jobdb_link": "-",
      "portfolio_link": "juanjocarin.github.io"
    },
    "professional_summary": {
      "has_summary": "Yes",
      "summary_points": [
        "Passionate about data analysis and experiments, mainly focused on user behavior, experience, and engagement.",
        "Solid background in data science and statistics, with extensive experience using data insights to drive business growth."
      ]
    },
    "education": [
      {
        "institution": "University of California, Berkeley",
        "degree": "Master of Information and Data Science",
        "dates": "2016",
        "gpa": "3.93",
        "honors": "Relevant courses: Machine Learning; Machine Learning at Scale; ..."
      },
      {
        "institution": "Universidad Politécnica de Madrid",
        "degree": "M.S. in Statistical and Computational Information Processing",
        "dates": "2014",
        "gpa": "3.69",
        "honors": "Relevant courses: Data Mining; Multivariate Analysis; ..."
      }
    ],
    "experience": [
      {
        "title": "Data Scientist",
        "company": "CONENTO (Madrid, Spain)",
        "dates": "Jan 2016 - Mar 2016",
        "description": [
          "Designed and implemented the ETL pipeline for a predictive model of traffic.",
          "Automated scripts in R to extract, transform, clean, and load into MySQL."
        ]
      }
    ],
    "skills": {
      "technical": [
        "Data Analysis",
        "Statistics",
        "Experiment Design",
        "ETL"
      ],
      "soft_skills": [
        "Team Leadership",
        "Customer Service Improvement"
      ],
      "tools_with_levels": [
        {
          "tool": "Python",
          "level": "proficient"
        }
      ]
    }
  }
}
```
---

## SectionAggregator Output Format
- Used by all /evaluation/<section> endpoints
```json
{
  "response": {
    "section": "Experience",
    "scores": {
      "RoleRelevance": { "score": 5, "feedback": "xxx" },
      "Length":        { "score": 4, "feedback": "yyy" },
      "Grammar":       { "score": 5, "feedback": "zzz" },
      "ContentQuality":{ "score": 3, "feedback": "aaa" },
      "Completeness":  { "score": 3, "feedback": "bbb" }
    }
  },
  "response_time": "0.12345 s"
}
```
#### Notes

No total_score here → because SectionAggregator returns raw (unweighted) criteria scores before global normalization.

Used directly in your section endpoints.

## GlobalAggregator Output Format
- Used by /evaluation/final-resume-score
```json
{
  "conclusion": {
    "final_resume_score": 82.4,
    "section_contribution": {
      "Profile": {
        "section_total": 78.0,
        "section_weight": 40,
        "contribution": 31.2
      },
      "Experience": {
        "section_total": 90.0,
        "section_weight": 10,
        "contribution": 9.0
      }
    }
  },
  "section_details": {
    "Profile": {
      "total_score": 78.0,
      "scores": {
        "RoleRelevance":  { "score": 30.0, "feedback": "xxx" },
        "Length":         { "score": 8.0,  "feedback": "yyy" },
        "Grammar":        { "score": 10.0, "feedback": "zzz" },
        "ContentQuality": { "score": 24.0, "feedback": "aaa" },
        "Completeness":   { "score": 6.0,  "feedback": "bbb" }
      }
    },
    "Experience": {
      "total_score": 90.0,
      "scores": {
        "RoleRelevance":  { "score": 20.0, "feedback": "xxx" },
        "Length":         { "score": 10.0, "feedback": "yyy" },
        "Grammar":        { "score": 25.0, "feedback": "zzz" },
        "ContentQuality": { "score": 22.0, "feedback": "aaa" },
        "Completeness":   { "score": 13.0, "feedback": "bbb" }
      }
    }
  },
  "metadata": {
    "model_name": "gemini-2.5-flash",
    "timestamp": "2025-12-03T11:45:00+07:00",
    "weights_version": "weights_v1",
    "prompt_version": "prompt_v1"
  }
}
```
### Field Explanation
`conclusion.final_resume_score`
Final composite score after applying:
→ Section weights
→ Normalization
→ Aggregation formula

`conclusion.section_contribution`
Shows how much each section contributes to the final score.

`section_details`
Contains each full SectionAggregator result but with total_score added.

`metadata`
Audit + debugging info (model, timestamp, versions, etc.)

---
*** 

## Endpoints

### 1. Health & Metadata

#### 1.1 Health Check (FastAPI service)

**GET /**

Simple liveness endpoint. Useful for uptime monitoring.


### Request

No body.


### Response

```json
{
  "status": "ok",
  "service": "FastAPI",
  "response_time": "0.00001 s"
}
```
#### `status` : "ok" when API is reachable.
#### `service` : static identifier for this service.
#### `response_time` : local processing time (no external calls).

---

### 1.2 Gemini Health Check

**GET /health/gemini**

Connectivity health check for Gemini LLM.  
Verifies that the LLM is reachable and measures round-trip (RT) latency.

### Request

No body.

### Response

```json
{
  "response": {
    "status": "connected"
  },
  "response_time": "1.23456 s"
}
```
#### `response` : Parsed JSON returned by Gemini.
#### `response_time` : Total time from sending the prompt to receiving the response.

---

### 1.3 Metadata Health Check

**GET /health/metadata**

Verifies that metadata retrieval (via `get_metadata()`) is functioning correctly.

### Request

No body.

### Response

```json
{
  "message": { "...": "..." },
  "response_time": "0.01234 s"
}
```

#### `message` : Arbitrary metadata object returned from get_metadata() (e.g. config version, environment information).
#### `response_time` : Processing time for metadata retrieval.

---

## 2. Debug & Lab

**Note**: These endpoints are for debugging and internal testing. (They should be restricted or disabled in production if needed.)

### 2.1 Get Example Resume Payload

**GET /evaluation/logexamplepayload**

Returns a mock resume JSON payload (from `src/mock/resume3.json`) for testing purposes.

### Request

No body.

### Response

```json
{
  "response": {
    "...": "mock resume data"
  }
}
```

<hr>


### 2.2 Call LLM with Example Payload

**GET /evaluation/callexamplepayload**

Runs an end-to-end evaluation pipeline on the mock resume payload:

- Build **Profile** prompt
- Call **Gemini**
- Aggregate section scores

### Request

No body.

### Response

```json
{
  "response": {
    "section": "Profile",
    "total_score": 85.0,
    "scores": {
      "Completeness":   { "score": 40.0, "feedback": "..." },
      "ContentQuality": { "score": 45.0, "feedback": "..." }
    }
  },
  "response_time": "2.34567 s"
}
```
(Actual numbers depend on the LLM output and configured weights.)

<hr>

### 2.3 Prompt Builder Lab

**POST /test/prompt**

Builds a prompt using the `PromptBuilder` without calling the LLM.  
Useful for debugging prompt design and criteria selection.

### Request Body

```json
{
  "section": "Summary",
  "criteria": ["Completeness", "ContentQuality", "Grammar", "Length", "RoleRelevance"],
  "targetrole": "Data scientist"
}
```

#### Request Fields
##### `section` (string, optional) : "Profile", "Summary", "Education", "Experience", "Activities", "Skills"
##### `criteria` (array[string], optional) : ["Completeness", "ContentQuality", "Grammar", "Length", "RoleRelevance"]
##### `targetrole` (string, optional) Default: "Data scientist"

#### Response

##### Content-Type: text/plain

##### Body: Raw prompt text that would be sent to the LLM.

### Example (truncated)
```text
Role :
You are the expert HR evaluator

objectvie :
Evaluate the Summary section from the resume using the scoring criteria
Measure how well the candidate matches the Data science role.
Consider: degree relevance, experience alignment, skills/tools, and seniority evidence.
Score 0-5 using the scale above.

section :
You are evaluating the Summary section.

expected :
- 2-4 sentence summary of experience
- Technical & domain strengths
- Career focus & value proposition
- Avoid buzzwords
- Feedback word 20 words

Criteria :
- RoleRelevance
    score 5: Content is strongly aligned with the target role: tasks, tools, domain, and responsibilitiesclearly match what is expected for the Data science role; shows appropriate seniority and impact.
    score 3: Content has partial alignment with the target role: some relevant skills or responsibilities,but mixed with less relevant tasks or not yet at the depth/seniority typically expected forData science.
    score 1: Content is mostly unrelated to the target role: focuses on other domains or generic duties;very little evidence that directly supports readiness for Data science.
- Length
    score 5: Length is appropriate for the section: not too short, not overly long; information is denseand relevant; each sentence or bullet adds value without obvious redundancy.
    score 3: Length is somewhat suboptimal: either a bit short (missing some detail) or somewhat long withmild repetition or low-value bullets, but still usable.
    score 1: Length is clearly inappropriate: either extremely short (1-2 vague lines) or very long andrepetitive with many low-information bullets or sentences.
- Grammar
    score 5: Grammar, spelling, and sentence structure are correct and natural; bullets are easy to read;verb tenses are consistent; only very minor or rare typos, if any.
    score 3: Some grammar or spelling issues, but the text remains understandable; occasional awkward phrasingor tense inconsistency, yet overall readability is acceptable.
    score 1: Frequent grammar and spelling mistakes; sentences are confusing or broken; tense usage isinconsistent; the reader must work hard to interpret the meaning.
- ContentQuality
    score 5: Follows clear Action → Method → Impact with quantifiable results; very specific; includestools, methods, or techniques; shows strong, measurable improvement.Examples: social media with +35% engagement; Random Forest churn model (72%→88%, churn -20%);stakeholder management reducing escalations by 60%.
    score 3: Partially follows Action → Method → Impact; has some specifics but lacks clear, quantifiedresults; reasonable but not strong.Examples: using Meta Business Suite to plan/publish content; churn model mentioned but no metrics;weekly stakeholder meetings to keep schedule.
    score 1: Very generic; only action with no method or impact; no tools, no metrics, low clarity.Examples: "Managed social media", "Built a prediction model", "Worked with stakeholders".
- Completeness
    score 5: Section contains all key elements from expected_content for this section with enoughdetail to understand the candidate's background and context. No major information gaps.
    score 3: Section contains all key elements from expected_content for this section with enoughdetail to understand the candidate's background and context. No major information gaps.
    score 1: Section is very sparse or missing most key elements; important information is absentor only hinted at. Hard to understand the candidate from this section alone.

Scale :
0 = missing
1 = poor
2 = weak
3 = sufficient
4 = strong
5 = excellent

output :
{
  "section": "Summary",
  "scores": {
    "RoleRelevance": {
      "score": 0,
      "feedback": ""
    },
    "Length": {
      "score": 0,
      "feedback": ""
    },
    "Grammar": {
      "score": 0,
      "feedback": ""
    },
    "ContentQuality": {
      "score": 0,
      "feedback": ""
    },
    "Completeness": {
      "score": 0,
      "feedback": ""
    }
  }
}

CV/Resume: 
resume_json
```

---

## 3. Section Evaluation

All section evaluation endpoints share the following characteristics:

- **Method**: POST  
- **Body**: `EvaluationPayload`  
- **Response**: Section score schema + `response_time`


### 3.1 Evaluate Profile

**POST /evaluation/profile**

Evaluates the **Profile** section of the resume.

### Criteria Used
- Completeness
- ContentQuality

### Request

```json
{
  "output_lang": "en",
  "resume_json": "resume_json"
}
```
#### Request Fields
##### `output_lang` (string, optional) : "en", "th"
##### `resume_json` (object, required) : Structured resume payload. Must follow the resume schema.

### Request example
```json
{
  "output_lang": "en",
  "resume_json": {
  "response": {
    "contact_information": {
      "name": "Juan Jose Carin",
      "email": "juanjose.carin@gmail.com",
      "phone": "650-336-4590",
      "linkedin": "linkedin.com/in/juanjosecarin",
      "jobdb_link": "-",
      "portfolio_link": "juanjocarin.github.io"
    },
    "professional_summary": {
      "has_summary": "Yes",
      "summary_points": [
        "Passionate about data analysis and experiments, mainly focused on user behavior, experience, and engagement.",
        "Solid background in data science and statistics, with extensive experience using data insights to drive business growth."
      ]
    },
    "education": [
      {
        "institution": "University of California, Berkeley",
        "degree": "Master of Information and Data Science",
        "dates": "2016",
        "gpa": "3.93",
        "honors": "Relevant courses: Machine Learning; Machine Learning at Scale; Storing and Retrieving Data; Field Experiments; Applied Regression and Time Series Analysis; Exploring and Analyzing Data; Data Visualization and Communication; Research Design and Applications for Data Analysis."
      },
      {
        "institution": "Universidad Politécnica de Madrid",
        "degree": "M.S. in Statistical and Computational Information Processing",
        "dates": "2014",
        "gpa": "3.69",
        "honors": "Relevant courses: Data Mining; Multivariate Analysis; Time Series; Neural Networks and Statistical Learning; Regression and Prediction Methods; Optimization Techniques; Monte Carlo Techniques; Numerical Methods in Finance; Stochastic Models in Finance; Bayesian Networks."
      },
      {
        "institution": "Universidad Politécnica de Madrid",
        "degree": "M.S. in Telecommunication Engineering",
        "dates": "2005",
        "gpa": "3.03",
        "honors": "Focus Area: Radio communication systems (radar and mobile). Fellowship: First year at University, due to Honors obtained last year at high school."
      }
    ],
    "experience": [
      {
        "title": "Data Scientist",
        "company": "CONENTO (Madrid, Spain) — working remotely",
        "dates": "Jan 2016 - Mar 2016",
        "description": [
          "Designed and implemented the ETL pipeline for a predictive model of traffic on the main roads in eastern Spain (project for the Spanish government).",
          "Automated scripts in R to extract, transform, clean (including anomaly detection), and load into MySQL data from multiple sources (road traffic sensors, accidents, road works, weather)."
        ]
      },
      {
        "title": "Data Scientist",
        "company": "CONENTO (Madrid, Spain)",
        "dates": "Jun 2014 - Sep 2014",
        "description": [
          "Designed an experiment for Google Spain (conducted in Oct 2014) to measure the impact of YouTube ads on the sales of a car manufacturer's dealer network.",
          "Used a matched-pair, cluster-randomized design selecting test/control groups from 50+ cities based on sales-wise similarity over time (using wavelets and R)."
        ]
      },
      {
        "title": "Head of Sales, Spain & Portugal - Test & Measurement dept.",
        "company": "YOKOGAWA (Madrid, Spain)",
        "dates": "Feb 2009 - Aug 2013",
        "description": [
          "Applied analysis of sales and market trends to decide the direction of the department.",
          "Led a team of 7 people.",
          "Increased revenue by 6.3%, gross profit by 4.2%, and operating income by 146%; achieved a 30% ratio of new customers (3x growth) by entering new markets and improving customer service and training."
        ]
      },
      {
        "title": "Sales Engineer - Test & Measurement dept.",
        "company": "YOKOGAWA (Madrid, Spain)",
        "dates": "Apr 2008 - Jan 2009",
        "description": [
          "Promoted to head of sales after 5 months leading the sales team."
        ]
      },
      {
        "title": "Sales & Application Engineer",
        "company": "AYSCOM (Madrid, Spain)",
        "dates": "Sep 2004 - Mar 2008",
        "description": [
          "Exceeded sales target every year from 2005 to 2007; achieved 60% of the target in the first 3 months of 2008."
        ]
      },
      {
        "title": "Tutor of Differential & Integral Calculus, Physics, and Digital Electronic Circuits",
        "company": "ACADEMIA UNIVERSITARIA (Madrid, Spain)",
        "dates": "Jul 2002 - Jun 2004",
        "description": [
          "Highest-rated professor in student surveys in 4 of the 6 terms.",
          "Increased ratio of students passing the course by 25%."
        ]
      }
    ],
    "skills": {
      "technical": [
        "Data Analysis",
        "Statistics",
        "Experiment Design",
        "ETL",
        "Anomaly Detection",
        "MySQL",
        "Machine Learning",
        "Data Visualization",
        "Big Data"
      ],
      "soft_skills": [
        "Team Leadership",
        "Customer Service Improvement",
        "Training & Mentoring"
      ],
      "tools_with_levels": [
        {
          "tool": "Python",
          "level": "proficient"
        },
        {
          "tool": "R",
          "level": "proficient"
        },
        {
          "tool": "SQL",
          "level": "proficient"
        },
        {
          "tool": "Hadoop",
          "level": "proficient"
        },
        {
          "tool": "Hive",
          "level": "proficient"
        },
        {
          "tool": "MrJob",
          "level": "proficient"
        },
        {
          "tool": "Tableau",
          "level": "proficient"
        },
        {
          "tool": "Git",
          "level": "proficient"
        },
        {
          "tool": "AWS",
          "level": "proficient"
        },
        {
          "tool": "Spark",
          "level": "intermediate"
        },
        {
          "tool": "Storm",
          "level": "intermediate"
        },
        {
          "tool": "Bash",
          "level": "intermediate"
        },
        {
          "tool": "SPSS",
          "level": "intermediate"
        },
        {
          "tool": "SAS",
          "level": "intermediate"
        },
        {
          "tool": "Matlab",
          "level": "intermediate"
        },
        {
          "tool": "EViews",
          "level": "basic"
        },
        {
          "tool": "Demetra+",
          "level": "basic"
        },
        {
          "tool": "D3.js",
          "level": "basic"
        },
        {
          "tool": "Gephi",
          "level": "basic"
        },
        {
          "tool": "Neo4j",
          "level": "basic"
        },
        {
          "tool": "QGIS",
          "level": "basic"
        }
      ],
      "languages": [
        {
          "language": "Python",
          "level": "proficient"
        },
        {
          "language": "R",
          "level": "proficient"
        },
        {
          "language": "SQL",
          "level": "proficient"
        },
        {
          "language": "Bash",
          "level": "intermediate"
        },
        {
          "language": "Matlab",
          "level": "intermediate"
        }
      ]
    }
  }
}
}
```

#### Response

##### Content-Type: text/plain

##### Body: Raw prompt text that would be sent to the LLM.

### Example (output)
```json
{
  "response": {
    "section": "Profile",
    "total_score": 16,
    "scores": {
      "ContentQuality": {
        "score": 6,
        "feedback": "The summary clearly outlines the candidate's passion and background in data science, focusing on user behavior and business growth, but lacks quantifiable achievements."
      },
      "Completeness": {
        "score": 10,
        "feedback": "The profile section effectively establishes the candidate's professional identity, clear positioning in data science, and career direction with no missing elements."
      }
    }
  },
  "response_time": "6.15841 s"
}
```

---

### 3.2 Evaluate Summary

**POST /evaluation/summary**

Evaluates the **Summary** section of the resume.

### Criteria Used
- Completeness
- ContentQuality
- Grammar
- Length
- RoleRelevance

### Request

```json
{
  "output_lang": "en",
  "resume_json": { "...": "..." }
}
```
#### Request Fields
##### `output_lang` (string, optional) : Allowed values: "en", "th" Specifies the language of the evaluation feedback.
##### `resume_json` (object, required) : Structured resume payload. Must follow the resume schema.


### 3.3 Evaluate Education

**POST /evaluation/education**

Evaluates the **Education** section of the resume.

### Criteria Used
- Completeness
- RoleRelevance

### Request

```json
{
  "output_lang": "en",
  "resume_json": { "...": "..." }
}
```
#### Request Fields
##### `output_lang` (string, optional) : Allowed values: "en", "th" Specifies the language of the evaluation feedback.
##### `resume_json` (object, required) : Structured resume payload. Must follow the resume schema.


### 3.4 Evaluate Experience

**POST /evaluation/experience**

Evaluates the **Experience** section of the resume.

### Criteria Used
- Completeness
- ContentQuality
- Grammar
- Length
- RoleRelevance

### Request

```json
{
  "output_lang": "en",
  "resume_json": { "...": "..." }
}
```
#### Request Fields
##### `output_lang` (string, optional) : Allowed values: "en", "th" Specifies the language of the evaluation feedback.
##### `resume_json` (object, required) : Structured resume payload. Must follow the resume schema.




### 3.5 Evaluate Activities

**POST /evaluation/activities**

Evaluates the **Activities** section of the resume  
(competitions, clubs, hackathons, etc.).

### Criteria Used
- Completeness
- ContentQuality
- Grammar
- Length

### Request

```json
{
  "output_lang": "en",
  "resume_json": { "...": "..." }
}
```
#### Request Fields
##### `output_lang` (string, optional) : Allowed values: "en", "th" Specifies the language of the evaluation feedback.
##### `resume_json` (object, required) : Structured resume payload. Must follow the resume schema.




### 3.6 Evaluate Skills

**POST /evaluation/skills**

Evaluates the **Skills** section of the resume.

### Criteria Used
- Completeness
- Length
- RoleRelevance

### Request

```json
{
  "output_lang": "en",
  "resume_json": { "...": "..." }
}
```
#### Request Fields
##### `output_lang` (string, optional) : Allowed values: "en", "th" Specifies the language of the evaluation feedback.
##### `resume_json` (object, required) : Structured resume payload. Must follow the resume schema.

---

## 4. Composite Evaluation

### 4.1 Final Resume Score

**POST /evaluation/final-resume-score**

Runs the full evaluation pipeline:

- Build prompts for the following sections:
  - Profile
  - Summary
  - Education
  - Experience
  - Activities
  - Skills
- Call **Gemini** once per section
- Aggregate per-section scores via `SectionScoreAggregator`
- Compute a final composite score via `GlobalAggregator.fn0()`

### Request

```json
{
  "output_lang": "en",
  "resume_json": { "...": "..." }
}
```
#### Request Fields
##### `output_lang` (string, optional) : Allowed values: "en", "th" Specifies the language of the evaluation feedback.
##### `resume_json` (object, required) : Structured resume payload. Must follow the resume schema.

### Request example
```json
{
  "output_lang": "en",
  "resume_json": {
  "response": {
    "contact_information": {
      "name": "Juan Jose Carin",
      "email": "juanjose.carin@gmail.com",
      "phone": "650-336-4590",
      "linkedin": "linkedin.com/in/juanjosecarin",
      "jobdb_link": "-",
      "portfolio_link": "juanjocarin.github.io"
    },
    "professional_summary": {
      "has_summary": "Yes",
      "summary_points": [
        "Passionate about data analysis and experiments, mainly focused on user behavior, experience, and engagement.",
        "Solid background in data science and statistics, with extensive experience using data insights to drive business growth."
      ]
    },
    "education": [
      {
        "institution": "University of California, Berkeley",
        "degree": "Master of Information and Data Science",
        "dates": "2016",
        "gpa": "3.93",
        "honors": "Relevant courses: Machine Learning; Machine Learning at Scale; Storing and Retrieving Data; Field Experiments; Applied Regression and Time Series Analysis; Exploring and Analyzing Data; Data Visualization and Communication; Research Design and Applications for Data Analysis."
      },
      {
        "institution": "Universidad Politécnica de Madrid",
        "degree": "M.S. in Statistical and Computational Information Processing",
        "dates": "2014",
        "gpa": "3.69",
        "honors": "Relevant courses: Data Mining; Multivariate Analysis; Time Series; Neural Networks and Statistical Learning; Regression and Prediction Methods; Optimization Techniques; Monte Carlo Techniques; Numerical Methods in Finance; Stochastic Models in Finance; Bayesian Networks."
      },
      {
        "institution": "Universidad Politécnica de Madrid",
        "degree": "M.S. in Telecommunication Engineering",
        "dates": "2005",
        "gpa": "3.03",
        "honors": "Focus Area: Radio communication systems (radar and mobile). Fellowship: First year at University, due to Honors obtained last year at high school."
      }
    ],
    "experience": [
      {
        "title": "Data Scientist",
        "company": "CONENTO (Madrid, Spain) — working remotely",
        "dates": "Jan 2016 - Mar 2016",
        "description": [
          "Designed and implemented the ETL pipeline for a predictive model of traffic on the main roads in eastern Spain (project for the Spanish government).",
          "Automated scripts in R to extract, transform, clean (including anomaly detection), and load into MySQL data from multiple sources (road traffic sensors, accidents, road works, weather)."
        ]
      },
      {
        "title": "Data Scientist",
        "company": "CONENTO (Madrid, Spain)",
        "dates": "Jun 2014 - Sep 2014",
        "description": [
          "Designed an experiment for Google Spain (conducted in Oct 2014) to measure the impact of YouTube ads on the sales of a car manufacturer's dealer network.",
          "Used a matched-pair, cluster-randomized design selecting test/control groups from 50+ cities based on sales-wise similarity over time (using wavelets and R)."
        ]
      },
      {
        "title": "Head of Sales, Spain & Portugal - Test & Measurement dept.",
        "company": "YOKOGAWA (Madrid, Spain)",
        "dates": "Feb 2009 - Aug 2013",
        "description": [
          "Applied analysis of sales and market trends to decide the direction of the department.",
          "Led a team of 7 people.",
          "Increased revenue by 6.3%, gross profit by 4.2%, and operating income by 146%; achieved a 30% ratio of new customers (3x growth) by entering new markets and improving customer service and training."
        ]
      },
      {
        "title": "Sales Engineer - Test & Measurement dept.",
        "company": "YOKOGAWA (Madrid, Spain)",
        "dates": "Apr 2008 - Jan 2009",
        "description": [
          "Promoted to head of sales after 5 months leading the sales team."
        ]
      },
      {
        "title": "Sales & Application Engineer",
        "company": "AYSCOM (Madrid, Spain)",
        "dates": "Sep 2004 - Mar 2008",
        "description": [
          "Exceeded sales target every year from 2005 to 2007; achieved 60% of the target in the first 3 months of 2008."
        ]
      },
      {
        "title": "Tutor of Differential & Integral Calculus, Physics, and Digital Electronic Circuits",
        "company": "ACADEMIA UNIVERSITARIA (Madrid, Spain)",
        "dates": "Jul 2002 - Jun 2004",
        "description": [
          "Highest-rated professor in student surveys in 4 of the 6 terms.",
          "Increased ratio of students passing the course by 25%."
        ]
      }
    ],
    "skills": {
      "technical": [
        "Data Analysis",
        "Statistics",
        "Experiment Design",
        "ETL",
        "Anomaly Detection",
        "MySQL",
        "Machine Learning",
        "Data Visualization",
        "Big Data"
      ],
      "soft_skills": [
        "Team Leadership",
        "Customer Service Improvement",
        "Training & Mentoring"
      ],
      "tools_with_levels": [
        {
          "tool": "Python",
          "level": "proficient"
        },
        {
          "tool": "R",
          "level": "proficient"
        },
        {
          "tool": "SQL",
          "level": "proficient"
        },
        {
          "tool": "Hadoop",
          "level": "proficient"
        },
        {
          "tool": "Hive",
          "level": "proficient"
        },
        {
          "tool": "MrJob",
          "level": "proficient"
        },
        {
          "tool": "Tableau",
          "level": "proficient"
        },
        {
          "tool": "Git",
          "level": "proficient"
        },
        {
          "tool": "AWS",
          "level": "proficient"
        },
        {
          "tool": "Spark",
          "level": "intermediate"
        },
        {
          "tool": "Storm",
          "level": "intermediate"
        },
        {
          "tool": "Bash",
          "level": "intermediate"
        },
        {
          "tool": "SPSS",
          "level": "intermediate"
        },
        {
          "tool": "SAS",
          "level": "intermediate"
        },
        {
          "tool": "Matlab",
          "level": "intermediate"
        },
        {
          "tool": "EViews",
          "level": "basic"
        },
        {
          "tool": "Demetra+",
          "level": "basic"
        },
        {
          "tool": "D3.js",
          "level": "basic"
        },
        {
          "tool": "Gephi",
          "level": "basic"
        },
        {
          "tool": "Neo4j",
          "level": "basic"
        },
        {
          "tool": "QGIS",
          "level": "basic"
        }
      ],
      "languages": [
        {
          "language": "Python",
          "level": "proficient"
        },
        {
          "language": "R",
          "level": "proficient"
        },
        {
          "language": "SQL",
          "level": "proficient"
        },
        {
          "language": "Bash",
          "level": "intermediate"
        },
        {
          "language": "Matlab",
          "level": "intermediate"
        }
      ]
    }
  }
}
}
```

### Response
```json
{
    "conclution":{
        "final_resume_score": 82.4,
        "section_contribution":{
            "Profile":{
                "section_total":78.0,
                "section_weight":40,
                "contribution":31.2
            },
            "Experience":{
                "section_total":90.0,
                "section_weight":10,
                "contribution":9.0
            }
        }
    },
    "section_details":{
        "Profile":{
            "total_score":78.0,
            "scores":{
                    'RoleRelevance':  {'score': 30.0, 'feedback': 'xxx'},
                    'Length':         {'score': 8.0, 'feedback': 'yyy'},
                    'Grammar':        {'score': 10.0, 'feedback': 'zzz'},
                    'ContentQuality': {'score': 24.0, 'feedback': 'aaa'},
                    'Completeness':   {'score': 6.0, 'feedback': 'bbb'}
            }
        },
        "Experience":{
            "total_score":90.0,
            "scores":{
                    'RoleRelevance':  {'score': 20.0, 'feedback': 'xxx'},
                    'Length':         {'score': 10.0, 'feedback': 'yyy'},
                    'Grammar':        {'score': 25.0, 'feedback': 'zzz'},
                    'ContentQuality': {'score': 22.0, 'feedback': 'aaa'},
                    'Completeness':   {'score': 13.0, 'feedback': 'bbb'}
            }      
        }
    },
    "metadata":{
        "model_name":"gemini-2.5-flash",
        "timestamp": "2025-12-03T11:45:00+07:00",
        "weights_version":"weights_v1",
        "prompt_version":"prompt_v1"
    },
  "response_time": "58.82124 s"
}      

```

### Notes
- The exact shape of the response depends on the GlobalAggregator.fn0() implementation.
- The example above reflects the current design: per-section breakdown, final composite score, and aggregation metadata.