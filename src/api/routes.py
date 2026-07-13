import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, status
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.recommendation_engine import RecommendationEngine
from src.data.cache import is_cache_initialized
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(preferences: UserPreferences) -> RecommendationResponse:
    """
    HTTP POST endpoint to query restaurant recommendations based on preferences.
    """
    if not is_cache_initialized():
        logger.error("Dataset cache is not initialized.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The restaurant database is currently loading. Please try again in a few moments."
        )

    engine = RecommendationEngine()
    response = engine.get_recommendations(preferences)
    
    # 404 handler for empty recommendations (indicating no matching filter records)
    if not response.recommendations:
        logger.info(f"No restaurants matched preferences: {preferences.model_dump()}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response.summary or "No restaurants match your selected criteria. Try adjusting your preferences."
        )
        
    return response

@router.get("/health")
def health_check():
    """
    HTTP GET health check endpoint reporting loading status and API key configuration state.
    """
    cache_ready = is_cache_initialized()
    
    # Simple check to see if Groq is configured (offline validation of key formatting)
    groq_configured = False
    try:
        settings.validate_api_key()
        groq_configured = True
    except ValueError:
        pass
        
    status_str = "healthy" if (cache_ready and groq_configured) else "degraded"
    
    return {
        "status": status_str,
        "cache_initialized": cache_ready,
        "groq_configured": groq_configured
    }
