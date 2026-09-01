from pydantic import BaseModel, Field

from .skills import Skill


class Education(BaseModel):
    """Educational qualification."""

    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_year: int | None = None
    end_year: int | None = None


class Experience(BaseModel):
    """Professional or internship experience."""

    company: str
    role: str

    description: str = ""

    start_date: str | None = None
    end_date: str | None = None

    skills: list[str] = Field(default_factory=list)


class Project(BaseModel):
    """Project listed or identified from a résumé."""

    name: str
    description: str = ""

    technologies: list[str] = Field(default_factory=list)

    repository_url: str | None = None

    highlights: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    """Structured representation of a candidate's resume."""

    candidate_name: str | None = None

    summary: str | None = None

    skills: list[Skill] = Field(default_factory=list)

    education: list[Education] = Field(default_factory=list)

    experience: list[Experience] = Field(default_factory=list)

    projects: list[Project] = Field(default_factory=list)

    certifications: list[str] = Field(default_factory=list)

    achievements: list[str] = Field(default_factory=list)

    raw_text: str | None = None