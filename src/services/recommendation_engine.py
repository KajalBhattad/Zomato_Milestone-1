import time
import logging
from typing import Optional
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.data.cache import get_restaurants
from src.services.filter_service import filter_restaurants
from src.services.prompt_builder import build_prompt
from src.llm.groq_client import GroqLLMClient
from src.llm.parser import parse_recommendation_response, build_fallback_response

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Main orchestration class that coordinates filtering candidate restaurants,
    building LLM prompts, querying Groq, and parsing the ranked results.
    """
    def __init__(self, groq_client: Optional[GroqLLMClient] = None) -> None:
        # Allow passing a pre-configured or mocked client for flexibility
        self._groq_client = groq_client

    def _get_client(self) -> GroqLLMClient:
        if self._groq_client is None:
            self._groq_client = GroqLLMClient()
        return self._groq_client

    def get_recommendations(self, preferences: UserPreferences) -> RecommendationResponse:
        """
        Processes user preferences to retrieve and rank the top recommended restaurants.
        
        Args:
            preferences: The validated search preferences.
            
        Returns:
            The parsed and ranked recommendation response.
        """
        # 1. Load data and apply deterministic filters
        all_restaurants = get_restaurants()
        candidates = filter_restaurants(all_restaurants, preferences)
        
        # 2. Edge Case: 0 candidate matches -> return empty response immediately (no LLM cost)
        if not candidates:
            logger.info("Zero matching restaurants found. Skipping LLM call.")
            return RecommendationResponse(
                summary="No restaurants match your selected criteria. Try adjusting your filters.",
                recommendations=[]
            )
            
        # 3. Construct the LLM prompt
        system_prompt, user_prompt = build_prompt(preferences, candidates)
        
        # 4. Invoke LLM with error catching and fallback logic
        logger.info(f"Submitting {len(candidates)} candidates to LLM engine.")
        start_time = time.time()
        try:
            client = self._get_client()
            raw_response = client.complete(system_prompt, user_prompt)
            latency = time.time() - start_time
            logger.info(f"Groq API call resolved in {latency:.2f} seconds.")
            
            # 5. Parse and validate LLM output
            return parse_recommendation_response(raw_response, candidates)
            
        except Exception as e:
            logger.error(
                f"Recommendation Engine error: {e}. "
                "Degrading gracefully to deterministic fallback."
            )
            # Graceful degradation on API timeouts, key errors, or rate limits
            return build_fallback_response(
                candidates,
                "Showing top rated results (fallback) as the recommendation engine is currently offline."
            )
