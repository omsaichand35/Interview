from enum import StrEnum
from pydantic import BaseModel, Field
import json
from interviewos.interview.strategy import InterviewStrategy
from interviewos.interview.session import InterviewSession, InterviewAction
from interviewos.interview.state import InterviewState, InterviewEvent
from interviewos.interview.context import InterviewContext
from interviewos.models import JobProfile

class ManagerialCompetency(StrEnum):
    LEADERSHIP = "Leadership"
    DECISION_MAKING = "Decision Making"
    PRIORITIZATION = "Prioritization"
    DELEGATION = "Delegation"
    CONFLICT_MANAGEMENT = "Conflict Management"
    STAKEHOLDER_MANAGEMENT = "Stakeholder Management"
    STRATEGIC_THINKING = "Strategic Thinking"
    ACCOUNTABILITY = "Accountability"

class ManagerialQuestionTarget(BaseModel):
    competency: ManagerialCompetency
    priority: int = Field(ge=1, le=5)
    rationale: str

class ManagerialInterviewBlueprint(BaseModel):
    targets: list[ManagerialQuestionTarget] = Field(default_factory=list)
    duration_minutes: int
    total_questions: int

class ManagerialBlueprintGenerator:
    def __init__(self, llm):
        self.llm = llm

    async def generate(self, job: JobProfile, resume: dict | None = None) -> ManagerialInterviewBlueprint:
        prompt = f"""
Generate a Managerial Interview Blueprint for the following job profile:
Title: {job.title}
Summary: {job.summary}

Identify the top managerial competencies required from these options:
Leadership, Decision Making, Prioritization, Delegation, Conflict Management, Stakeholder Management, Strategic Thinking, Accountability.

Assign a priority (1=highest, 5=lowest) and a rationale.

Return a JSON object matching this exact structure:

{{
    "targets": [
        {{
            "competency": "Leadership",
            "priority": 1,
            "rationale": "Required to lead technical teams and drive project vision"
        }},
        {{
            "competency": "Decision Making",
            "priority": 2,
            "rationale": "Essential for making technical and architectural decisions under pressure"
        }},
        {{
            "competency": "Accountability",
            "priority": 3,
            "rationale": "Important for owning project outcomes and delivery"
        }}
    ],
    "duration_minutes": 45,
    "total_questions": 4
}}

IMPORTANT: Return ONLY valid JSON, no markdown or schema metadata.
"""
        return await self.llm.generate_structured(prompt=prompt, system_prompt="You are an expert executive recruiter.", model=ManagerialInterviewBlueprint)

class ManagerialQuestionGenerator:
    def __init__(self, llm):
        self.llm = llm

    async def generate(self, job: JobProfile, competency: ManagerialCompetency, transcript_text: str) -> str:
        prompt = f"""
Generate a behavioral/managerial interview question for the competency: {competency}.
Role: {job.title}
Context: {job.summary}

Previous conversation:
{transcript_text}

Rules:
1. Do not repeat questions.
2. Ask for a specific scenario or tradeoff analysis, not a hypothetical 'what would you do'.
3. Focus purely on managerial and leadership aspects.
Output ONLY the question text.
"""
        response = await self.llm.generate(prompt=prompt, system_prompt="You are an expert executive interviewer.")
        return response.strip()

class ManagerialInterviewStrategy(InterviewStrategy):
    """Strategy for evaluating managerial and behavioral competencies."""

    def get_system_prompt_additions(self) -> str:
        return "" # Handled by the brain prompt
        
    def build_context(self, job: JobProfile) -> str:
        return f"Managerial interview for {job.title}"
        
    def competencies(self) -> list[str]:
        return [c.value for c in ManagerialCompetency]

    def get_context_additions(self, session: InterviewSession) -> str:
        if session.managerial_blueprint:
            return f"Managerial Blueprint Targets: {[t.competency for t in session.managerial_blueprint.targets]}"
        return ""

    def determine_next_action(self, context: InterviewContext, llm_decision: dict) -> InterviewEvent:
        action = llm_decision.get("action", InterviewAction.MOVE_ON)
        if action == InterviewAction.ASK_FOLLOW_UP:
            return InterviewEvent.FOLLOW_UP_REQUIRED
        elif action == InterviewAction.DEEP_DIVE:
            return InterviewEvent.DEEP_DIVE_REQUIRED
        elif action == InterviewAction.MOVE_ON:
            return InterviewEvent.QUESTION_COMPLETE
        elif action == InterviewAction.END_INTERVIEW:
            return InterviewEvent.END
        return InterviewEvent.QUESTION_COMPLETE

    def update_session(self, session: InterviewSession, context: InterviewContext, llm_decision: dict) -> None:
        if "assessment" in llm_decision:
            from interviewos.interview.session import AnswerAssessment
            
            # The LLM outputs dict, convert to AnswerAssessment
            assessment_data = llm_decision["assessment"]
            
            # Handle ManagerialEvidence conversion if present
            if "managerial_evidence" in assessment_data:
                from interviewos.interview.session import ManagerialEvidence
                evidence_list = []
                for ev in assessment_data["managerial_evidence"]:
                    evidence_list.append(ManagerialEvidence(**ev))
                assessment_data["managerial_evidence"] = evidence_list
            
            assessment = AnswerAssessment(**assessment_data)
            session.scores.append(assessment)
            
        if "next_question" in llm_decision:
            session.current_question = llm_decision["next_question"]