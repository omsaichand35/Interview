from datetime import datetime
from typing import TYPE_CHECKING, Any
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from .state import InterviewState, InterviewType, InterviewAction
from interviewos.interview.project.profile import ProjectProfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interviewos.interview.strategies.technical import TechnicalInterviewBlueprint

class InterviewMessage(BaseModel):
    """One message in the interview transcript."""

    role: str

    content: str

    timestamp: datetime


class InterviewScore(BaseModel):
    """Score for one competency."""

    competency: str

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    feedback: str = ""

    expected_answer: str = ""

    strengths: list[str] = Field(
        default_factory=list,
    )

    weaknesses: list[str] = Field(
        default_factory=list,
    )



class InterviewSession(BaseModel):
    """State of one interview attempt."""

    id: str

    candidate_id: str

    job_id: str

    interview_type: InterviewType

    state: InterviewState = (
        InterviewState.CREATED
    )

    difficulty: str = "medium"

    duration_minutes: int = Field(
        ge=1,
    )

    transcript: list[InterviewMessage] = Field(
        default_factory=list,
    )

    questions_asked: int = 0

    current_question: str | None = None
    
    current_question_evidence: list['InterviewQuestionEvidence'] = Field(
        default_factory=list,
    )

    competencies: list[str] = Field(
        default_factory=list,
    )

    scores: list[InterviewScore] = Field(
        default_factory=list,
    )

    covered_competencies: list[str] = Field(
        default_factory=list,
    )

    covered_topics: list[str] = Field(
        default_factory=list,
    )

    project_profile: ProjectProfile | None = None
    
    technical_blueprint: Any | None = None
    
    hr_blueprint: Any | None = None
    
    managerial_blueprint: Any | None = None
    
    dsa_problems: list['DSAProblem'] = Field(
        default_factory=list,
    )
    
    current_dsa_problem: 'DSAProblem | None' = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    @property
    def time_elapsed_minutes(self) -> float:
        if not self.started_at:
            return 0.0
        now = self.completed_at or datetime.now()
        return (now - self.started_at).total_seconds() / 60.0

    @property
    def time_elapsed_seconds(self) -> int:
        if not self.started_at:
            return 0
        now = self.completed_at or datetime.now()
        return max(0, int((now - self.started_at).total_seconds()))

    @property
    def time_remaining_seconds(self) -> int:
        if not self.duration_minutes:
            return 0
        total_seconds = self.duration_minutes * 60
        remaining = total_seconds - self.time_elapsed_seconds
        return max(0, remaining)

    @property
    def timer_display(self) -> str:
        elapsed_m, elapsed_s = divmod(self.time_elapsed_seconds, 60)
        if not self.duration_minutes:
            return f"⏱ {elapsed_m:02d}:{elapsed_s:02d}"
        
        rem_m, rem_s = divmod(self.time_remaining_seconds, 60)
        tot_m = self.duration_minutes
        return f"⏱ {rem_m:02d}:{rem_s:02d} left ({elapsed_m:02d}:{elapsed_s:02d} / {tot_m:02d}:00)"

    @property
    def is_time_up(self) -> bool:
        if not self.duration_minutes:
            return False
        return self.time_elapsed_minutes >= self.duration_minutes

    def add_message(
            self,
            role: str,
            content: str,
    ) -> None:
        """Add a message to the transcript."""

        self.transcript.append(
            InterviewMessage(
                role=role,
                content=content,
                timestamp=datetime.now(),
            )
        )

    @classmethod
    def create(
            cls,
            candidate_id: str,
            job_id: str,
            interview_type: InterviewType,
            duration_minutes: int = 30,
            difficulty: str = "medium",
    ) -> "InterviewSession":
        return cls(
            id=str(uuid4()),
            candidate_id=candidate_id,
            job_id=job_id,
            interview_type=interview_type,
            duration_minutes=duration_minutes,
            difficulty=difficulty,
        )


class DSAProblem(BaseModel):
    """A Data Structures and Algorithms problem."""

    problem_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(default="DSA Problem")
    statement: str = Field(default="")
    difficulty: str = Field(default="medium")
    topics: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    examples: list[dict[str, str]] = Field(default_factory=list)  # [{'input': '...', 'output': '...'}]
    expected_complexity: str = Field(default="O(N)")
    hidden_solution_information: str = Field(default="")

    @field_validator("statement", mode="before")
    @classmethod
    def normalize_statement(cls, v):
        if isinstance(v, dict):
            return v.get("description") or v.get("statement") or v.get("problem") or str(v)
        return str(v) if v else ""

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, v):
        if isinstance(v, dict):
            return v.get("name") or v.get("title") or "DSA Problem"
        return str(v) if v else "DSA Problem"

    @field_validator("hidden_solution_information", mode="before")
    @classmethod
    def normalize_solution(cls, v):
        if isinstance(v, dict):
            return v.get("solution") or v.get("overview") or v.get("explanation") or str(v)
        return str(v) if v else ""


class DepthLevel(StrEnum):
    FOUNDATIONAL = "foundational"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Misconception(BaseModel):
    """A detected technical misconception."""
    concept: str
    misconception: str
    correction: str

class AnswerAssessment(BaseModel):
    """Assessment of a candidate's answer."""

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    strengths: list[str] = Field(
        default_factory=list,
    )

    weaknesses: list[str] = Field(
        default_factory=list,
    )

    missing_concepts: list[str] = Field(
        default_factory=list,
    )

    feedback: str = ""

    expected_answer: str = ""
    
    # DSA Specific Fields
    problem_understanding_score: float | None = Field(default=None, ge=0.0, le=1.0)
    algorithmic_reasoning_score: float | None = Field(default=None, ge=0.0, le=1.0)
    data_structure_score: float | None = Field(default=None, ge=0.0, le=1.0)
    correctness_score: float | None = Field(default=None, ge=0.0, le=1.0)
    optimization_score: float | None = Field(default=None, ge=0.0, le=1.0)
    complexity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    communication_score: float | None = Field(default=None, ge=0.0, le=1.0)
    incorrect_assumptions: list[str] = Field(default_factory=list)

    # Technical Specific Fields
    technical_correctness_score: float | None = Field(default=None, ge=0.0, le=1.0)
    conceptual_depth_score: float | None = Field(default=None, ge=0.0, le=1.0)
    technical_precision_score: float | None = Field(default=None, ge=0.0, le=1.0)
    practical_understanding_score: float | None = Field(default=None, ge=0.0, le=1.0)
    reasoning_score: float | None = Field(default=None, ge=0.0, le=1.0)
    tradeoff_awareness_score: float | None = Field(default=None, ge=0.0, le=1.0)
    
    misconceptions: list[Misconception] = Field(default_factory=list)
    demonstrated_depth: DepthLevel | None = None

    # HR Specific Fields
    hr_relevance_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_clarity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_specificity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_ownership_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_reasoning_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_self_awareness_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_communication_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_behavioral_maturity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_consistency_score: float | None = Field(default=None, ge=0.0, le=1.0)
    hr_evidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    
    hr_concerns: list[str] = Field(default_factory=list)
    hr_evidence: list['HREvidence'] = Field(default_factory=list)
    
    # Managerial Specific Fields
    managerial_leadership_score: float | None = Field(default=None, ge=0.0, le=1.0)
    managerial_decision_making_score: float | None = Field(default=None, ge=0.0, le=1.0)
    managerial_prioritization_score: float | None = Field(default=None, ge=0.0, le=1.0)
    managerial_ownership_score: float | None = Field(default=None, ge=0.0, le=1.0)
    managerial_delegation_score: float | None = Field(default=None, ge=0.0, le=1.0)
    managerial_communication_score: float | None = Field(default=None, ge=0.0, le=1.0)
    managerial_stakeholder_management_score: float | None = Field(default=None, ge=0.0, le=1.0)
    managerial_strategic_thinking_score: float | None = Field(default=None, ge=0.0, le=1.0)
    
    managerial_concerns: list[str] = Field(default_factory=list)
    managerial_evidence: list['ManagerialEvidence'] = Field(default_factory=list)

    @field_validator(
        "strengths",
        "weaknesses",
        "missing_concepts",
        "incorrect_assumptions",
        "misconceptions",
        "hr_concerns",
        "hr_evidence",
        "managerial_concerns",
        "managerial_evidence",
        mode="before",
    )
    @classmethod
    def normalize_assessment_lists(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            if "\n" in v:
                return [s.strip("- *").strip() for s in v.split("\n") if s.strip()]
            if "," in v:
                return [s.strip() for s in v.split(",") if s.strip()]
            return [v.strip()] if v.strip() else []
        return v

class ManagerialEvidence(BaseModel):
    """Evidence distinguishing observed actions from subjective inference."""
    observed_action: str | None = None
    inferred_competency: str | None = None
    
class HREvidence(BaseModel):
    """STAR framework evidence extracted from candidate answers."""
    situation: str | None = None
    task: str | None = None
    action: str | None = None
    result: str | None = None
    reflection: str | None = None

class DifficultyChange(StrEnum):
    INCREASE = "increase"
    SAME = "same"
    DECREASE = "decrease"

class InterviewQuestionEvidence(BaseModel):
    """Repository evidence supporting a question."""

    source_file: str | None = None

    evidence: str

    reason: str

class InterviewDecision(BaseModel):
    """Decision made after evaluating an answer."""

    assessment: AnswerAssessment

    action: InterviewAction = InterviewAction.MOVE_ON

    next_competency: str | None = None

    next_question: str | None = None

    reasoning: str = ""

    difficulty_change: DifficultyChange = DifficultyChange.SAME

    question_evidence: list[
        InterviewQuestionEvidence
    ] = Field(
        default_factory=list,
    )

    @field_validator("question_evidence", mode="before")
    @classmethod
    def normalize_question_evidence(cls, value):
        """Accept plain text and MCP text blocks as evidence items."""
        if value is None:
            return []
        if isinstance(value, dict):
            value = [value]
        if not isinstance(value, list):
            value = [value]

        normalized = []
        for item in value:
            if isinstance(item, str):
                normalized.append({"evidence": item, "reason": ""})
                continue

            if isinstance(item, dict):
                text = item.get("text")
                if item.get("type") == "text" and isinstance(text, str):
                    normalized.append({"evidence": text, "reason": ""})
                    continue

                if "evidence" in item and "reason" not in item:
                    item = {**item, "reason": ""}

            normalized.append(item)

        return normalized

    @field_validator("action", mode="before")
    @classmethod
    def normalize_action(cls, v):
        if v is None:
            return InterviewAction.MOVE_ON
        if isinstance(v, str):
            v_clean = v.lower().strip()
            if "follow_up" in v_clean or "followup" in v_clean:
                return InterviewAction.ASK_FOLLOW_UP
            if "deep_dive" in v_clean or "deepdive" in v_clean:
                return InterviewAction.DEEP_DIVE
            if "end" in v_clean or "close" in v_clean:
                return InterviewAction.END_INTERVIEW
            if "move" in v_clean or "next" in v_clean:
                return InterviewAction.MOVE_ON
            try:
                return InterviewAction(v_clean)
            except ValueError:
                return InterviewAction.MOVE_ON
        return v

    @field_validator("difficulty_change", mode="before")
    @classmethod
    def normalize_difficulty_change(cls, v):
        if v is None:
            return DifficultyChange.SAME
        if isinstance(v, str):
            v_clean = v.lower().strip()
            if "inc" in v_clean or "up" in v_clean or "high" in v_clean:
                return DifficultyChange.INCREASE
            if "dec" in v_clean or "down" in v_clean or "low" in v_clean:
                return DifficultyChange.DECREASE
            if "same" in v_clean or "maintain" in v_clean or "keep" in v_clean:
                return DifficultyChange.SAME
            try:
                return DifficultyChange(v_clean)
            except ValueError:
                return DifficultyChange.SAME
        return v

InterviewSession.model_rebuild()

