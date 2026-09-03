from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

def _find_env_file() -> tuple[Path, ...]:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return (parent / ".env", Path(".env"))
    return (Path(".env"),)

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    #Application
    environment: str = Field(
        default="development",
        validation_alias="INTERVIEWOS_ENV"
    )

    log_level: str = Field(
        default="INFO",
        validation_alias="INTERVIEWOS_LOG_LEVEL"
    )

    #LLM
    llm_provider: str = Field(
        default="nvidia",
        validation_alias="LLM_PROVIDER"
    )

    llm_model: str = Field(
        default="nvidia/nemotron-3.5-lightning-30b-a3b",
        validation_alias="LLM_MODEL"
    )

    llm_base_url: str | None = Field(
        default=None,
        validation_alias="LLM_BASE_URL"
    )

    llm_timeout: float | None = Field(
        default=None,
        validation_alias="LLM_TIMEOUT"
    )

    llm_api_key: str | None = Field(
        default=None,
        validation_alias="LLM_API_KEY"
    )


    github_token: str | None = Field(
        default=None,
        validation_alias="GITHUB_TOKEN"
    )

    # Embeddings
    embeddings_model: str = Field(
        default="",
        validation_alias="EMBEDDINGS_MODEL"
    )

    # Vector Store
    vector_store_path: Path = Field(
        default=Path("data/vectorstore"),
        validation_alias="VECTOR_STORE_PATH"
    )

    # DSA Interview Weights
    dsa_weight_understanding: float = Field(default=0.15, validation_alias="DSA_WEIGHT_UNDERSTANDING")
    dsa_weight_algorithmic: float = Field(default=0.25, validation_alias="DSA_WEIGHT_ALGORITHMIC")
    dsa_weight_data_structure: float = Field(default=0.15, validation_alias="DSA_WEIGHT_DATA_STRUCTURE")
    dsa_weight_correctness: float = Field(default=0.20, validation_alias="DSA_WEIGHT_CORRECTNESS")
    dsa_weight_optimization: float = Field(default=0.10, validation_alias="DSA_WEIGHT_OPTIMIZATION")
    dsa_weight_complexity: float = Field(default=0.10, validation_alias="DSA_WEIGHT_COMPLEXITY")
    dsa_weight_communication: float = Field(default=0.05, validation_alias="DSA_WEIGHT_COMMUNICATION")

    # Technical Interview Weights
    tech_weight_correctness: float = Field(default=0.25, validation_alias="TECH_WEIGHT_CORRECTNESS")
    tech_weight_conceptual_depth: float = Field(default=0.20, validation_alias="TECH_WEIGHT_CONCEPTUAL_DEPTH")
    tech_weight_precision: float = Field(default=0.15, validation_alias="TECH_WEIGHT_PRECISION")
    tech_weight_practical_understanding: float = Field(default=0.15, validation_alias="TECH_WEIGHT_PRACTICAL_UNDERSTANDING")
    tech_weight_reasoning: float = Field(default=0.10, validation_alias="TECH_WEIGHT_REASONING")
    tech_weight_tradeoff: float = Field(default=0.10, validation_alias="TECH_WEIGHT_TRADEOFF")
    tech_weight_communication: float = Field(default=0.05, validation_alias="TECH_WEIGHT_COMMUNICATION")

    # HR Interview Weights
    hr_weight_communication: float = Field(default=0.15, validation_alias="HR_WEIGHT_COMMUNICATION")
    hr_weight_teamwork: float = Field(default=0.15, validation_alias="HR_WEIGHT_TEAMWORK")
    hr_weight_ownership: float = Field(default=0.15, validation_alias="HR_WEIGHT_OWNERSHIP")
    hr_weight_problem_solving: float = Field(default=0.10, validation_alias="HR_WEIGHT_PROBLEM_SOLVING")
    hr_weight_conflict_resolution: float = Field(default=0.10, validation_alias="HR_WEIGHT_CONFLICT_RESOLUTION")
    hr_weight_adaptability: float = Field(default=0.10, validation_alias="HR_WEIGHT_ADAPTABILITY")
    hr_weight_self_awareness: float = Field(default=0.10, validation_alias="HR_WEIGHT_SELF_AWARENESS")
    hr_weight_motivation: float = Field(default=0.10, validation_alias="HR_WEIGHT_MOTIVATION")
    hr_weight_professionalism: float = Field(default=0.05, validation_alias="HR_WEIGHT_PROFESSIONALISM")

@lru_cache
def get_settings() -> Settings:
    return Settings()
