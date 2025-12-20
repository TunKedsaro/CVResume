from pydantic import BaseModel, Field
from typing import Optional,Literal,Dict


class PromptBuilderPayload(BaseModel):
        section    : str  | None = Field (default = "Summary")
        criteria   : list | None = Field (default = ["Completeness", "ContentQuality","Grammar","Length","RoleRelevance"])
        targetrole : str  | None = Field (default = "Data scientist")


############################################################################

class PromptRole(BaseModel):
    role1: Optional[str] = None
class PromptObjective(BaseModel):
    objective1: Optional[str] = None
class PromptSectionName(BaseModel):
    section1: Optional[str] = None
class ExpectedContent(BaseModel):
    Profile: Optional[str] = None
    Summary: Optional[str] = None
    Education: Optional[str] = None
    Experience: Optional[str] = None
    Activities: Optional[str] = None
    Skills: Optional[str] = None
class PromptScale(BaseModel):
    score1: Optional[str] = None
class LanguageOutputStyle(BaseModel):
    en: Optional[str] = None
    th: Optional[str] = None

class OutputFormat(BaseModel):
    format1: Optional[str] = None
    format2: Optional[str] = None
    format3: Optional[str] = None
CriteriaBlock = Dict[str, Dict[str, str]]

class PromptUpdatePayload(BaseModel):
    version: Optional[str] = "prompt_v2"

    role: Optional[PromptRole] = None
    objective: Optional[PromptObjective] = None
    section: Optional[PromptSectionName] = None
    expected_content: Optional[ExpectedContent] = None
    scale: Optional[PromptScale] = None
    Language_output_style: Optional[LanguageOutputStyle] = None
    criteria: Optional[CriteriaBlock] = None

PROMPT_V2_EXAMPLE = {
    "version": "prompt_v2",
    "role": {
        "role1": "You are the expert HR evaluator"
    },
    "objective": {
        "objective1": (
            "Evaluate the <section_name> section from the resume using the scoring criteria\n"
            "Measure how well the candidate matches the <targetrole> role.\n"
            "Consider: degree relevance, experience alignment, skills/tools, and seniority evidence.\n"
            "Score 0-5 using the scale above."
        )
    },
    "section": {
        "section1": "You are evaluating the <section_name> section."
    },
    "expected_content": {
        "Profile": "- Candidate's basic professional identity\n- Clear positioning (e.g., 'Data Analyst', 'ML Engineer')\n- Career direction or headline\n- Avoid unnecessary personal details\n- Feedback word 20 words",
        "Summary": "- 2-4 sentence summary of experience\n- Technical & domain strengths\n- Career focus & value proposition\n- Avoid buzzwords\n- Feedback word 20 words",
        "Education": "- Institution name\n- Degree & field of study\n- Dates attended\n- GPA, honors (optional)\n- Relevance to data career\n- Feedback word 20 words",
        "Experience": "- Job title, employer, dates\n- Clear bullet points\n- Action -> method -> impact structure\n- Technical tools used\n- Quantifiable metrics\n- Feedback word 20 words",
        "Activities": "- Competitions, hackathons, club activities\n- Project descriptions with responsibilities\n- Mention of tools/tech if applicable\n- Feedback word 20 words",
        "Skills": "- Technical skills (Python, SQL, ML, Cloud)\n- Tools (Power BI, Git, TensorFlow)\n- Soft skills\n- Language proficiency\n- Clear grouping/categorization\n- Feedback word 20 words"
    },
    "scale": {
        "score1": (
            "0 = missing\n"
            "1 = poor\n"
            "2 = weak\n"
            "3 = sufficient\n"
            "4 = strong\n"
            "5 = excellent"
        )
    },
    "Language_output_style": {
        "en": (
            "- All feedback text MUST be written in English.\n"
            "- Scores MUST remain numeric.\n"
            "- JSON keys MUST remain in English exactly as defined"
        ),
        "th": (
            "- All feedback text MUST be written in Thai.\n"
            "- Scores MUST remain numeric.\n"
            "- JSON keys MUST remain in English exactly as defined.\n"
            "- Do NOT translate field names or schema keys."
        )
    },
    "criteria": {
        "Completeness": {
            "score5": "Section contains all key elements from expected_content for this section with enoughdetail to understand the candidate's background and context. No major information gaps.",
            "score3": "Section contains all key elements from expected_content for this section with enoughdetail to understand the candidate's background and context. No major information gaps.",
            "score1": "Section is very sparse or missing most key elements; important information is absentor only hinted at. Hard to understand the candidate from this section alone."
        },
        "ContentQuality": {
            "score5": "Follows clear Action -> Method -> Impact with quantifiable results; very specific; includestools, methods, or techniques; shows strong, measurable improvement.Examples: social media with +35% engagement; Random Forest churn model (72%->88%, churn -20%);stakeholder management reducing escalations by 60%.",
            "score3": "Partially follows Action -> Method -> Impact; has some specifics but lacks clear, quantifiedresults; reasonable but not strong.Examples: using Meta Business Suite to plan/publish content; churn model mentioned but no metrics;weekly stakeholder meetings to keep schedule.",
            "score1": "Very generic; only action with no method or impact; no tools, no metrics, low clarity.Examples: Managed social media, Built a prediction model, Worked with stakeholders"
        },
        "Grammar": {
            "score5": "Grammar, spelling, and sentence structure are correct and natural; bullets are easy to read;verb tenses are consistent; only very minor or rare typos, if any.",
            "score3": "Some grammar or spelling issues, but the text remains understandable; occasional awkward phrasingor tense inconsistency, yet overall readability is acceptable.",
            "score1": "Frequent grammar and spelling mistakes; sentences are confusing or broken; tense usage isinconsistent; the reader must work hard to interpret the meaning."
        },
        "Length": {
            "score5": "Length is appropriate for the section: not too short, not overly long; information is denseand relevant; each sentence or bullet adds value without obvious redundancy.",
            "score3": "Length is somewhat suboptimal: either a bit short (missing some detail) or somewhat long withmild repetition or low-value bullets, but still usable.",
            "score1": "Length is clearly inappropriate: either extremely short (1-2 vague lines) or very long andrepetitive with many low-information bullets or sentences."
        },
        "RoleRelevance": {
            "score5": "Content is strongly aligned with the target role: tasks, tools, domain, and responsibilitiesclearly match what is expected for the <targetrole> role; shows appropriate seniority and impact.",
            "score3": "Content has partial alignment with the target role: some relevant skills or responsibilities,but mixed with less relevant tasks or not yet at the depth/seniority typically expected for<targetrole>.",
            "score1": "Content is mostly unrelated to the target role: focuses on other domains or generic duties;very little evidence that directly supports readiness for <targetrole>."
        }
    }
}