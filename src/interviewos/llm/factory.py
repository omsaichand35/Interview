from interviewos.config import get_settings
from interviewos.core.exceptions import ConfigurationError

from .client import LLMClient
from .providers import OpenAIProvider


def create_llm_client() -> LLMClient:
    """Create the configured LLM client."""

    settings = get_settings()

    provider = settings.llm_provider.lower()

    if provider in ("openai", "nvidia"):
        if not settings.llm_api_key:
            raise ConfigurationError(
                "LLM_API_KEY is required."
            )

        if not settings.llm_model:
            raise ConfigurationError(
                "LLM_MODEL is required."
            )

        # NVIDIA NIM uses an OpenAI-compatible API.
        base_url = None
        if provider == "nvidia":
            base_url = (
                "https://integrate.api.nvidia.com/v1"
            )

        return LLMClient(
            provider=OpenAIProvider(
                api_key=settings.llm_api_key,
                model=settings.llm_model,
                base_url=base_url,
            ),
            default_timeout=settings.llm_timeout,
        )

    raise ConfigurationError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )