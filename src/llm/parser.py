import json
import logging
from typing import List
from src.models.restaurant import Restaurant
from src.models.recommendation import Recommendation, RecommendationResponse
from src.config import settings

logger = logging.getLogger(__name__)

def build_fallback_response(
    candidates: List[Restaurant],
    summary_prefix: str = "Showing top rated results as a fallback recommendation."
) -> RecommendationResponse:
    """
    Constructs a deterministic RecommendationResponse from the top candidates
    when LLM inference or JSON parsing fails.
    """
    # Sort candidates deterministically: rating DESC, cost DESC, name ASC
    sorted_candidates = list(candidates)
    def sorting_key(rest: Restaurant):
        rating_part = -rest.rating
        cost_part = -rest.cost_for_two if rest.cost_for_two is not None else 0
        name_part = rest.name.lower()
        return (rating_part, cost_part, name_part)
    sorted_candidates.sort(key=sorting_key)

    recommendations = []
    top_k = settings.top_k_results
    fallback_candidates = sorted_candidates[:top_k]
    
    for i, r in enumerate(fallback_candidates):
        cost_str = f"₹{r.cost_for_two} for two" if r.cost_for_two else "Moderate cost"
        explanation = (
            f"Recommended based on its high rating of {r.rating} and matching preferences "
            f"for location '{r.location}' and budget tier '{r.budget_tier}'."
        )
        recommendations.append(
            Recommendation(
                rank=i + 1,
                restaurant_name=r.name,
                cuisine=", ".join(r.cuisines),
                rating=r.rating,
                estimated_cost=cost_str,
                explanation=explanation
            )
        )
    
    return RecommendationResponse(
        summary=summary_prefix,
        recommendations=recommendations
    )


def parse_recommendation_response(
    raw_response: str,
    candidates: List[Restaurant]
) -> RecommendationResponse:
    """
    Parses the raw JSON text from Groq into a validated RecommendationResponse.
    Falls back to a deterministic recommendation list if JSON is malformed or invalid.
    """
    try:
        cleaned_text = raw_response.strip()
        
        # Clean markdown code blocks (e.g. ```json ... ```)
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()
            
        data = json.loads(cleaned_text)
        
        # Validate structure via Pydantic
        response_obj = RecommendationResponse.model_validate(data)
        
        # Hallucination validation: Ensure names match candidate pool
        candidate_names = {c.name.strip().lower() for c in candidates}
        valid_recs = []
        for rec in response_obj.recommendations:
            if rec.restaurant_name.strip().lower() in candidate_names:
                valid_recs.append(rec)
            else:
                logger.warning(
                    f"LLM hallucinated restaurant name '{rec.restaurant_name}' not in candidates. Skipping."
                )
                
        # Re-index ranks
        for idx, rec in enumerate(valid_recs):
            rec.rank = idx + 1
            
        response_obj.recommendations = valid_recs
        
        # If response became empty after filtering out hallucinations, trigger fallback
        if not response_obj.recommendations:
            logger.warning("No valid recommendations found after filtering hallucinations. Triggering fallback.")
            return build_fallback_response(candidates, "Showing top rated results (fallback) due to validation errors.")
            
        return response_obj
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse LLM response as valid JSON: {e}. Raw response: {raw_response}")
        return build_fallback_response(
            candidates,
            "Showing top rated results (fallback) as the recommendation engine returned an unparseable response."
        )
