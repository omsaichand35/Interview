from pydantic import BaseModel, Field

from .skills import SkillRequirement


class JobResponsibility(BaseModel):
    """Responsibility extracted from a job description."""

    description: str

    skills: list[str] = Field(default_factory=list)


class JobProfile(BaseModel):
    """Structured representation of a job description."""

    title: str

    company: str | None = None

    location: str | None = None

    employment_type: str | None = None

    summary: str | None = None

    required_skills: list[SkillRequirement] = Field(default_factory=list)

    preferred_skills: list[SkillRequirement] = Field(default_factory=list)

    responsibilities: list[JobResponsibility] = Field(
        default_factory=list
    )

    qualifications: list[str] = Field(default_factory=list)

    interview_topics: list[str] = Field(default_factory=list)

    raw_text: str | None = None