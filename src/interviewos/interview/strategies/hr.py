from interviewos.models import JobProfile

from pydantic import BaseModel, Field
from enum import StrEnum
from ..strategy import InterviewStrategy

class HRInterviewStrategy(InterviewStrategy):
    """HR interview strategy."""

    def competencies(self) -> list[str]:
        return [
            "communication",
            "motivation",
            "teamwork",
            "ownership"
        ]

    def build_context(self, job: JobProfile) -> str:
        return f"HR interview for {job.title}."

class HRCompetency(BaseModel):
    """An HR competency to be evaluated."""
    name: str
    importance: float = Field(ge=0.0, le=1.0)
    description: str
    evidence_requirements: list[str]

class HRInterviewBlueprint(BaseModel):
    """Blueprint for an HR interview."""
    role: str
    competencies: list[HRCompetency]
    priority: dict[str, str] # e.g. {"Teamwork": "HIGH"}

class HRBlueprintGenerator:
    """Generates an HRInterviewBlueprint using an LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def generate(self, job: JobProfile) -> HRInterviewBlueprint:
                
        prompt = f"""
Generate an HR Interview Blueprint for a {job.title}.
The JD emphasizes: {job.summary}

Identify the core behavioral competencies (e.g. Communication, Teamwork, Conflict Resolution, Ownership) to evaluate.
Determine priorities (HIGH, MEDIUM, LOW) based on the JD. 

Return ONLY structured JSON matching this schema:
{HRInterviewBlueprint.model_json_schema()}
"""
        return await self.llm.generate_structured(prompt=prompt,
            system_prompt="You are an expert HR interviewer designing an interview blueprint based on a job description.", model=HRInterviewBlueprint)

class HRQuestionType(StrEnum):
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    MOTIVATION = "motivation"
    SELF_AWARENESS = "self_awareness"
    CONFLICT = "conflict"
    FAILURE = "failure"
    OWNERSHIP = "ownership"
    LEADERSHIP = "leadership"

class HRQuestion(BaseModel):
    competency: str
    question_type: HRQuestionType
    question_text: str

class HRQuestionGenerator:
    """Generates HR questions using an LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def generate(self, job: JobProfile, competency: str, transcript: str) -> HRQuestion:
                
        prompt = f"""
Generate an HR Question for a {job.title}.
Target Competency: {competency}

The JD emphasizes: {job.summary}

Current Interview Transcript (to avoid repetition):
{transcript}

Rules:
1. Generate a question targeting the competency (e.g., behavioral, situational).
2. Do not repeat questions already in the transcript.
3. If a resume is mentioned in the transcript, you can reference it, but otherwise rely on standard HR probing.

Return ONLY structured JSON matching this schema:
{HRQuestion.model_json_schema()}
"""
        return await self.llm.generate_structured(prompt=prompt,
            system_prompt="You are an expert HR interviewer designing behavioral questions.", model=HRQuestion)