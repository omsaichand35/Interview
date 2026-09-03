from .providers import LLMProvider


class LLMClient:
    """
    Application-facing interface for language models.

    Application services should depend on this class rather than
    directly depending on a specific provider.
    """

    def __init__(self, provider: LLMProvider, default_timeout: float | None = None) -> None:
        self.provider = provider
        self.default_timeout = default_timeout

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        return await self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

    def sync_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        import asyncio
        import concurrent.futures

        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                ))
            finally:
                loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(_run).result()

    def sync_generate_structured(
        self,
        prompt: str,
        model: type["BaseModel"], # type: ignore
        system_prompt: str | None = None,
        max_retries: int = 3,
        timeout_seconds: float | None = None,
    ) -> "BaseModel": # type: ignore
        import asyncio
        import concurrent.futures

        if timeout_seconds is None:
            timeout_seconds = self.default_timeout

        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.generate_structured(
                    prompt=prompt,
                    model=model,
                    system_prompt=system_prompt,
                    max_retries=max_retries,
                    timeout_seconds=timeout_seconds,
                ))
            finally:
                loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(_run).result()


    async def generate_structured(
        self,
        prompt: str,
        model: type["BaseModel"], # type: ignore
        system_prompt: str | None = None,
        max_retries: int = 4,
        timeout_seconds: float | None = None,
    ) -> "BaseModel": # type: ignore
        """Generate a response and parse it into a Pydantic model with retries and timeouts."""
        import asyncio
        import logging
        import random
        from pydantic import BaseModel
        from interviewos.core.exceptions import (
            LLMUnavailableError,
            InvalidLLMResponseError,
            LLMError,
            LLMRateLimitError,
        )
        from interviewos.llm.structured_output import parse_structured_output, StructuredOutputError

        if timeout_seconds is None:
            timeout_seconds = self.default_timeout
        
        logger = logging.getLogger(__name__)
        
        current_prompt = prompt
        
        for attempt in range(1, max_retries + 1):
            try:
                # 1. Enforce timeout only if explicitly configured
                if timeout_seconds is not None and timeout_seconds > 0:
                    response = await asyncio.wait_for(
                        self.generate(current_prompt, system_prompt),
                        timeout=timeout_seconds
                    )
                else:
                    response = await self.generate(current_prompt, system_prompt)
                
                # 2. Parse structured output
                parsed = parse_structured_output(response, model)
                return parsed
                
            except asyncio.TimeoutError as e:
                logger.warning(f"[LLMClient] Attempt {attempt}/{max_retries} timed out after {timeout_seconds}s.")
                if attempt == max_retries:
                    raise LLMUnavailableError(f"LLM request timed out after {max_retries} attempts.") from e
                await asyncio.sleep(min(2 * attempt, 10))
                    
            except StructuredOutputError as e:
                logger.warning(f"[LLMClient] Validation failed on attempt {attempt}/{max_retries}. Error: {e}")
                if attempt == max_retries:
                    raise InvalidLLMResponseError(f"Failed to validate LLM response after {max_retries} attempts.") from e
                
                # 3. Repair/Retry logic: Append the error to the prompt for the next iteration
                current_prompt = (
                    f"{current_prompt}\n\n"
                    f"Your previous response failed validation with the following error:\n{e}\n"
                    f"Please correct your output to exactly match the required JSON schema."
                )
                await asyncio.sleep(1)
                
            except LLMRateLimitError as e:
                logger.warning(f"[LLMClient] Rate limit hit on attempt {attempt}/{max_retries}. Error: {e}")
                if attempt == max_retries:
                    raise LLMUnavailableError(f"LLM request failed due to rate limits after {max_retries} attempts.") from e
                # Exponential backoff with random jitter for rate limits (base 2s)
                backoff = min(30.0, 2.0 * (2 ** (attempt - 1)))
                jitter = random.uniform(0.2, 1.5)
                sleep_time = backoff + jitter
                logger.info(f"[LLMClient] Retrying after {sleep_time:.2f}s backoff...")
                await asyncio.sleep(sleep_time)

            except LLMError as e:
                logger.warning(f"[LLMClient] LLM API error on attempt {attempt}/{max_retries}. Error: {e}")
                if attempt == max_retries:
                    raise LLMUnavailableError(f"LLM request failed after {max_retries} attempts.") from e
                # Exponential backoff with random jitter for general LLM errors
                backoff = min(15.0, 1.5 * (2 ** (attempt - 1)))
                jitter = random.uniform(0.1, 1.0)
                await asyncio.sleep(backoff + jitter)
                
            except Exception as e:
                logger.error(f"[LLMClient] Unexpected error: {e}")
                raise

        raise InvalidLLMResponseError("Max retries exceeded.")