from enum import StrEnum

from pydantic import BaseModel, Field


class SkillLevel(StrEnum):
    """Normalized skill proficiency levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    UNKNOWN = "unknown"


class Skill(BaseModel):
    """A skill identified from a candidate or job description."""

    name: str
    level: SkillLevel = SkillLevel.UNKNOWN
    years_experience: float | None = Field(default=None, ge=0)
    evidence: list[str] = Field(default_factory=list)


class SkillRequirement(BaseModel):
    """A skill requirement extracted from a job description."""

    name: str
    required: bool = True
    expected_level: SkillLevel = SkillLevel.UNKNOWN
    importance: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class SkillEvidence(BaseModel):
    """Evidence connecting a candidate's experience to a skill."""

    skill: str
    evidence: str
    source: str


class SkillGap(BaseModel):
    """Difference between candidate capability and job requirement."""

    skill: str

    candidate_level: SkillLevel
    required_level: SkillLevel

    gap_score: float = Field(ge=0.0, le=1.0)

    importance: float = Field(default=1.0, ge=0.0, le=1.0)

    priority: str = "medium"

    reasoning: str

    evidence: list[SkillEvidence] = Field(default_factory=list)


class SkillGapReport(BaseModel):
    """Complete skill-gap analysis for a candidate/job pair."""

    gaps: list[SkillGap] = Field(default_factory=list)

    strengths: list[Skill] = Field(default_factory=list)

    missing_skills: list[SkillRequirement] = Field(default_factory=list)