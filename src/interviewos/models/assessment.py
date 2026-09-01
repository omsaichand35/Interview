from enum import StrEnum

from pydantic import BaseModel, Field
from datetime import datetime


class QuestionType(StrEnum):
    """Supported objective-assessment question types."""

    MCQ = "mcq"
    MULTIPLE_SELECT = "multiple_select"
    TRUE_FALSE = "true_false"


class Difficulty(StrEnum):
    """Question difficulty."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AssessmentTopic(BaseModel):
    """A topic that the assessment should evaluate."""

    name: str

    weight: float = Field(
        ge=0.0,
        le=1.0,
    )

    question_count: int = Field(
        ge=1,
    )

    difficulty: Difficulty = Difficulty.MEDIUM


class AssessmentBlueprint(BaseModel):
    """Blueprint defining what an OA should test."""

    role: str

    duration_minutes: int = Field(
        ge=1,
    )

    total_questions: int = Field(
        ge=1,
    )

    question_types: list[QuestionType]

    topics: list[AssessmentTopic]


class MCQOption(BaseModel):
    """One option in a multiple-choice question."""

    id: str

    text: str


class AssessmentQuestion(BaseModel):
    """A generated assessment question."""

    id: str

    question_type: QuestionType

    topic: str

    difficulty: Difficulty

    question: str

    options: list[MCQOption] = Field(
        default_factory=list,
    )

    correct_options: list[str] = Field(
        default_factory=list,
    )

    explanation: str

    concepts_tested: list[str] = Field(
        default_factory=list,
    )


class CandidateAnswer(BaseModel):
    """Candidate's answer to one assessment question."""

    question_id: str

    selected_options: list[str] = Field(
        default_factory=list,
    )


class QuestionEvaluation(BaseModel):
    """Evaluation of one assessment answer."""

    question_id: str

    correct: bool

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    feedback: str


class TopicScore(BaseModel):
    """Score for an individual assessment topic."""

    topic: str
    total_questions: int
    correct_answers: int
    score: float = Field(ge=0.0, le=1.0)

class AssessmentResult(BaseModel):
    """Final result of an OA."""

    total_questions: int

    correct_answers: int

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    topic_scores: list[TopicScore] = Field(
        default_factory=list,
    )

    question_results: list[QuestionEvaluation]

    passed: bool = False

class ValidationIssue(BaseModel):
    """A problem detected in a generated question."""

    code: str

    message: str

    severity: str = "error"


class QuestionValidationResult(BaseModel):
    """Result of validating an assessment question."""

    valid: bool

    issues: list[ValidationIssue] = Field(
        default_factory=list
    )

class QuestionBankItem(BaseModel):
    """A validated question stored in the question bank."""

    question: AssessmentQuestion

    created_at: datetime

    source: str = "llm_generated"

    quality_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    times_used: int = Field(
        default=0,
        ge=0,
    )


class AssessmentSessionStatus(StrEnum):
    """Assessment session states."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EVALUATED = "evaluated"


class AssessmentSession(BaseModel):
    """A candidate's assessment session."""

    id: str

    candidate_id: str

    role: str

    assessment_id: str

    question_ids: list[str]

    answers: list[CandidateAnswer] = Field(
        default_factory=list,
    )

    status: AssessmentSessionStatus = (
        AssessmentSessionStatus.CREATED
    )

    duration_minutes: int = Field(
        ge=1,
    )

    started_at: datetime | None = None

    submitted_at: datetime | None = None

    result: AssessmentResult | None = None

class Candidate(BaseModel):
    """Candidate taking an assessment."""

    id: str

    name: str

    email: str

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )

class Assessment(BaseModel):
    """Reusable assessment definition."""

    id: str

    name: str

    role: str

    blueprint: AssessmentBlueprint

    threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
    )

    version: int = Field(
        default=1,
        ge=1,
    )

class SelectionStatus(StrEnum):
    """Candidate selection status."""

    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"


class SelectionPolicy(BaseModel):
    """Rules used to select candidates."""

    minimum_score: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
    )

    maximum_candidates: int | None = Field(
        default=None,
        ge=1,
    )

    require_topic_thresholds: bool = False

    topic_thresholds: dict[str, float] = Field(
        default_factory=dict,
    )


class CandidateSelection(BaseModel):
    """Selection decision for one candidate."""

    candidate_id: str

    assessment_id: str

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    status: SelectionStatus

    rank: int | None = None

    reasons: list[str] = Field(
        default_factory=list,
    )


class SelectionResult(BaseModel):
    """Result of selecting candidates."""

    selections: list[CandidateSelection]

    shortlisted_candidate_ids: list[str]