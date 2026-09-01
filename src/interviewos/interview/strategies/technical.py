from pydantic import BaseModel, Field
from enum import StrEnum
from interviewos.models import JobProfile

from ..strategy import InterviewStrategy


class TechnicalInterviewStrategy(
    InterviewStrategy
):
    """Technical interview strategy."""

    def competencies(self) -> list[str]:
        return [
            "technical_knowledge",
            "problem_solving",
            "system_design",
            "communication",
        ]

    def build_context(
        self,
        job: JobProfile,
    ) -> str:
        return (
            f"Technical interview for "
            f"{job.title}."
        )

class TechnicalCompetency(BaseModel):
    """A technical competency to be evaluated."""
    name: str
    importance: float = Field(ge=0.0, le=1.0)
    required: bool
    topics: list[str]

class TechnicalInterviewBlueprint(BaseModel):
    """Blueprint for a technical interview."""
    role: str
    competencies: list[TechnicalCompetency]
    priority: dict[str, str] # e.g. {"PyTorch": "HIGH"}

class TechnicalBlueprintGenerator:
    """Generates a TechnicalInterviewBlueprint using an LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def generate(self, job: JobProfile) -> TechnicalInterviewBlueprint:
                
        prompt = f"""
Generate a Technical Interview Blueprint for a {job.title}.
The JD emphasizes: {job.summary}

Required skills: {', '.join(s.name for s in job.required_skills)}
Preferred skills: {', '.join(s.name for s in job.preferred_skills)}

Identify the core technical competencies (e.g. Python, PyTorch, Machine Learning) and the specific sub-topics to evaluate.
Do not include non-technical competencies like communication or teamwork.
Assign priorities (HIGH, MEDIUM, LOW) to each competency.

Return ONLY structured JSON matching this schema:
{TechnicalInterviewBlueprint.model_json_schema()}
"""
        return await self.llm.generate_structured(prompt=prompt,
            system_prompt="You are an expert technical interviewer designing an interview blueprint based on a job description.", model=TechnicalInterviewBlueprint)

class QuestionType(StrEnum):
    CONCEPTUAL = "conceptual"
    MECHANISM = "mechanism"
    SCENARIO = "scenario"
    TRADEOFF = "tradeoff"
    DESIGN_REASONING = "design_reasoning"
    DEBUGGING_REASONING = "debugging_reasoning"

class TechnicalQuestion(BaseModel):
    competency: str
    topic: str
    question_type: QuestionType
    question_text: str

class TechnicalQuestionGenerator:
    """Generates technical questions using an LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def generate(self, job: JobProfile, competency: str, topic: str, difficulty: str, transcript: str) -> TechnicalQuestion:
                
        prompt = f"""
Generate a Technical Question for a {job.title}.
Difficulty: {difficulty}
Target Competency: {competency}
Target Topic: {topic}

The JD emphasizes: {job.summary}

Current Interview Transcript (to avoid repetition):
{transcript}

Rules:
1. Ensure the question type matches one of: CONCEPTUAL, MECHANISM, SCENARIO, TRADEOFF, DESIGN_REASONING, DEBUGGING_REASONING.
2. Avoid trivia unless strictly necessary. Prefer questions that reveal understanding.
3. Do not ask for code syntax. Ask for concepts, mechanisms, scenarios, tradeoffs, and debugging strategies.
4. Do not repeat questions already in the transcript.

Return ONLY structured JSON matching this schema:
{TechnicalQuestion.model_json_schema()}
"""
        return await self.llm.generate_structured(prompt=prompt,
            system_prompt="You are an expert technical interviewer designing deep reasoning questions.", model=TechnicalQuestion)