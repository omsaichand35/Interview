from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    """Role of a message in a mentor conversation."""

    USER = "user"
    MENTOR = "mentor"
    SYSTEM = "system"


class ConversationTurn(BaseModel):
    """One turn in a mentor conversation."""

    role: MessageRole

    content: str

    timestamp: datetime = Field(default_factory=datetime.now)


class LearningProgress(BaseModel):
    """Progress for a particular skill/topic."""

    topic: str

    mastery_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    completed: bool = False

    notes: list[str] = Field(default_factory=list)
    
    priority: str | None = None


class LearnerState(BaseModel):
    """Current state of the candidate's learning journey."""

    candidate_name: str | None = None

    target_role: str | None = None

    current_topic: str | None = None

    progress: list[LearningProgress] = Field(default_factory=list)

    known_strengths: list[str] = Field(default_factory=list)

    weak_topics: list[str] = Field(default_factory=list)

    conversation: list[ConversationTurn] = Field(
        default_factory=list
    )

class EvaluationResult(BaseModel):
    """Evaluation of a candidate's response."""

    topic: str

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    correct: bool

    strengths: list[str] = Field(
        default_factory=list
    )

    weaknesses: list[str] = Field(
        default_factory=list
    )

    feedback: str

    recommended_action: str


class PracticeQuestion(BaseModel):
    """A question generated for learning practice."""

    question: str

    topic: str

    difficulty: str = "medium"

    expected_concepts: list[str] = Field(
        default_factory=list
    )

class MentorAction(StrEnum):
    """Actions the mentor agent can take."""

    TEACH = "teach"
    PRACTICE = "practice"
    EVALUATE = "evaluate"
    REVIEW = "review"
    MOVE_FORWARD = "move_forward"
    CLARIFY = "clarify"


class MentorDecision(BaseModel):
    """Decision made by the mentor agent."""

    action: MentorAction

    topic: str | None = None

    reasoning: str

    difficulty: str = "medium"

    retrieval_query: str | None = None