import logging
# pyrefly: ignore [missing-import]
import groq
# pyrefly: ignore [missing-import]
from groq import Groq
# pyrefly: ignore [missing-import]
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from src.config import settings

logger = logging.getLogger(__name__)

class GroqLLMClient:
    """
    Wrapper around the official Groq client to manage chat completions,
    handling configuration, rate limiting, and gateway errors via retries.
    """
    def __init__(self) -> None:
        # Fail-fast during initialization if the key is missing
        settings.validate_api_key()
        
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model
        self._temperature = settings.groq_temperature

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        retry=retry_if_exception_type((
            groq.RateLimitError,
            groq.InternalServerError,
            groq.APIConnectionError
        )),
        reraise=True
    )
    def complete(self, system: str, user: str) -> str:
        """
        Executes a chat completion query against Groq API, with rate limits
        and internal server error retries.
        
        Returns:
            The raw string response (JSON formatted) from the LLM.
        """
        logger.info(f"Submitting completion request to Groq using model {self._model}")
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=self._temperature,
                response_format={"type": "json_object"}
            )
            # Log token usage
            usage = getattr(response, "usage", None)
            if usage:
                logger.info(
                    f"Groq API success. Tokens used - Prompt: {usage.prompt_tokens}, "
                    f"Completion: {usage.completion_tokens}, Total: {usage.total_tokens}"
                )
            return response.choices[0].message.content
        except groq.APIError as e:
            logger.error(f"Groq API Error: {e.message} (status_code={e.status_code})")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error calling Groq: {e}")
            raise e
