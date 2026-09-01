from datetime import datetime
from enum import StrEnum
from uuid import uuid4
from pydantic import BaseModel, Field

class InterviewRoundType(StrEnum):
    OA = "oa"
    TECHNICAL = "technical"
    DSA = "dsa"
    PROJECT = "project"
    HR = "hr"
    MANAGERIAL = "managerial"

class InterviewRound(BaseModel):
    round_id: str = Field(default_factory=lambda: str(uuid4()))
    type: InterviewRoundType
    name: str
    order: int
    enabled: bool = True
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    required: bool = True
    duration_minutes: int = 30
    configuration: dict = Field(default_factory=dict)

class InterviewPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    role: str
    rounds: list[InterviewRound] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    configuration: dict = Field(default_factory=dict)
    final_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    
class RoundStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    PASSED = "passed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    
class RoundResult(BaseModel):
    round_id: str
    round_type: InterviewRoundType
    score: float = Field(ge=0.0, le=1.0)
    status: RoundStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_minutes: int | None = None
    competencies: dict[str, float] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    transcript_reference: str | None = None
    metadata: dict = Field(default_factory=dict)

class CandidateStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"
    SHORTLISTED = "shortlisted"
    NOT_SHORTLISTED = "not_shortlisted"
    
class ShortlistPolicy(StrEnum):
    ALL_REQUIRED_ROUNDS_PASS = "all_required_rounds_pass"
    WEIGHTED_SCORE = "weighted_score"
    HYBRID = "hybrid"

class FinalCandidateStatus(StrEnum):
    SHORTLISTED = "shortlisted"
    NOT_SHORTLISTED = "not_shortlisted"
    INCOMPLETE = "incomplete"

class FinalInterviewEvaluation(BaseModel):
    candidate_id: str
    role: str
    rounds_completed: int
    round_scores: dict[str, float]
    weighted_score: float | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    competency_summary: dict[str, float] = Field(default_factory=dict)
    jd_coverage: dict[str, str] = Field(default_factory=dict)
    final_status: FinalCandidateStatus
    recommendation: str

class CandidateInterviewContext(BaseModel):
    candidate_id: str
    job_id: str
    resume_id: str | None = None
    interview_plan_id: str
    completed_rounds: list[str] = Field(default_factory=list)
    round_results: dict[str, RoundResult] = Field(default_factory=dict)
    current_round_type: InterviewRoundType | None = None
    weaknesses: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    topics_already_tested: list[str] = Field(default_factory=list)
    areas_to_probe: list[str] = Field(default_factory=list)
