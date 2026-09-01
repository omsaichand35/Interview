from enum import StrEnum

from pydantic import BaseModel, Field


class LearningPriority(StrEnum):
    """Priority assigned to a learning objective."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LearningGap(BaseModel):
    """A gap identified from interview performance."""
    competency: str
    topic: str
    current_score: float = Field(ge=0.0, le=1.0)
    target_score: float = Field(ge=0.0, le=1.0)
    priority: LearningPriority
    evidence: list[str] = Field(default_factory=list)
    source_round: str
    recommended_action: str


class LearningObjective(BaseModel):
    """A specific learning goal."""

    title: str

    description: str

    related_skills: list[str] = Field(default_factory=list)

    priority: LearningPriority = LearningPriority.MEDIUM

    estimated_hours: float = Field(default=1.0, gt=0)

    prerequisites: list[str] = Field(default_factory=list)


class LearningModule(BaseModel):
    """A group of related learning objectives."""

    title: str

    description: str

    objectives: list[LearningObjective] = Field(
        default_factory=list
    )

    order: int = Field(ge=1)


class LearningPlan(BaseModel):
    """Personalized learning plan generated from resume + JD analysis."""

    candidate_name: str | None = None

    target_role: str

    modules: list[LearningModule] = Field(default_factory=list)

    total_estimated_hours: float = Field(default=0.0, ge=0)

    goals: list[str] = Field(default_factory=list)