from pydantic import BaseModel, Field, field_validator

from .evidence import ProjectEvidence


class ProjectProfile(BaseModel):
    """Structured understanding of a candidate project."""

    repository_name: str = ""

    repository_url: str = ""

    summary: str = ""

    languages: list[str] = Field(
        default_factory=list,
    )

    frameworks: list[str] = Field(
        default_factory=list,
    )

    libraries: list[str] = Field(
        default_factory=list,
    )

    architecture: list[str] = Field(
        default_factory=list,
    )

    technologies: list[str] = Field(
        default_factory=list,
    )

    important_files: list[str] = Field(
        default_factory=list,
    )

    testing_approach: str = ""

    deployment_approach: str = ""
    
    database_usage: str = ""
    
    external_services: list[str] = Field(
        default_factory=list,
    )
    
    architectural_decisions: list[str] = Field(
        default_factory=list,
    )

    potential_interview_topics: list[str] = Field(
        default_factory=list,
    )

    evidence: list[ProjectEvidence] = Field(
        default_factory=list,
    )
    
    unresolved_areas: list[str] = Field(
        default_factory=list,
    )
    
    analysis_completeness: str = "INCOMPLETE"
    
    @field_validator(
        "languages",
        "frameworks",
        "libraries",
        "architecture",
        "technologies",
        "important_files",
        "external_services",
        "architectural_decisions",
        "potential_interview_topics",
        "unresolved_areas",
        mode="before",
    )
    @classmethod
    def normalize_string_lists(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            if "\n" in v:
                return [s.strip("- *").strip() for s in v.split("\n") if s.strip()]
            if "," in v:
                return [s.strip() for s in v.split(",") if s.strip()]
            return [v.strip()]
        if isinstance(v, list):
            return [str(item).strip() for item in v if item is not None]
        return v

    @field_validator("evidence", mode="before")
    @classmethod
    def normalize_evidence(cls, v):
        if not v:
            return []
        if isinstance(v, list):
            res = []
            for item in v:
                if isinstance(item, str):
                    res.append(ProjectEvidence(category="General", description=item))
                elif isinstance(item, dict):
                    cat = item.get("category", "General")
                    desc = item.get("description") or item.get("evidence") or item.get("text") or item.get("summary") or str(item)
                    res.append(ProjectEvidence(category=cat, description=desc, snippet=item.get("snippet"), source_file=item.get("source_file")))
                else:
                    res.append(item)
            return res
        return v