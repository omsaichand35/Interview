from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from interviewos.core.exceptions import LLMError


class LLMProvider(ABC):
    """Base interface for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of the LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is required.")

        if not model:
            raise ValueError("OpenAI model is required.")

        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:

        try:
            messages = []

            if system_prompt:
                messages.append(
                    {
                        "role": "system",
                        "content": system_prompt,
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )

            content = response.choices[0].message.content

            if not content:
                raise LLMError(
                    "The LLM returned an empty response."
                )

            return content

        except LLMError:
            raise

        except Exception as exc:
            raise LLMError(
                f"OpenAI request failed: {exc}"
            ) from exc