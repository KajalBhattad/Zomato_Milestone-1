import json
from typing import List, Tuple
from src.config import settings
from src.models.restaurant import Restaurant
from src.models.preferences import UserPreferences

def build_prompt(
    preferences: UserPreferences,
    candidates: List[Restaurant]
) -> Tuple[str, str]:
    """
    Constructs the system and user messages for the Groq LLM prompt.
    
    Args:
        preferences: The validated user preferences.
        candidates: The pre-filtered list of candidate restaurants.
        
    Returns:
        A tuple of (system_prompt, user_prompt).
    """
    top_k = settings.top_k_results
    
    system_prompt = (
        "You are an expert restaurant recommendation assistant specializing in Indian cities.\n"
        f"Given a list of candidate restaurants and user preferences, select and rank the top {top_k} "
        "restaurants that best match the criteria. If fewer than 5 candidates are provided, rank all of them.\n\n"
        "Rules:\n"
        "1. You MUST ONLY recommend restaurants that are present in the provided 'Candidate Restaurants' list. "
        "Do NOT invent or recommend any restaurant not explicitly listed.\n"
        "2. Analyze 'Additional Preferences' (e.g. family-friendly, outdoor seating, quick service, etc.) and use them "
        "to influence the ranking. The 'explanation' field MUST be exactly a single, concise sentence (maximum 20 words) "
        "explaining why this restaurant fits. Do NOT write multiple sentences, reviews, or long paragraphs.\n"
        "3. Since specific menu lists may be missing, perform **Cuisine-Based Inference**: use the 'cuisines' list "
        "and 'dish_liked' tags to infer the types of dishes served (e.g. if cuisine includes 'Italian', infer they serve "
        "pastas/pizzas; if 'Chinese', infer noodles/momos; if 'Mughlai', infer biryani/kebabs) in your explanations.\n"
        "4. Output a valid, parsable JSON object exactly matching the schema below. Do not include markdown code block formatting "
        "(e.g., do not wrap the JSON in ```json ... ```) or any extra text before or after the JSON.\n\n"
        "Output JSON Schema:\n"
        "{\n"
        '  "summary": "A brief overview explaining the selection and ranking,",\n'
        '  "recommendations": [\n'
        "    {\n"
        '      "rank": 1,\n'
        '      "restaurant_name": "Exact Name of Restaurant",\n'
        '      "cuisine": "Cuisines offered (comma-separated)",\n'
        '      "rating": 4.2,\n'
        '      "estimated_cost": "₹800 for two",\n'
        '      "explanation": "A single-sentence explanation of why this restaurant fits the preferences (max 20 words)"\n'
        "    }\n"
        "  ]\n"
        "}"

    )
    
    # Serialize candidates to a minimal JSON format to conserve token usage
    minimal_candidates = []
    for r in candidates:
        minimal_candidates.append({
            "name": r.name,
            "cuisines": r.cuisines,
            "rating": r.rating_text,
            "cost_for_two": r.cost_for_two,
            "budget_tier": r.budget_tier,
            # If available, we could pass dish_liked or other tags to assist with additional preferences reasoning
            "dish_liked": r.raw.get("dish_liked") if r.raw else None
        })
        
    candidates_json = json.dumps(minimal_candidates, indent=2)
    
    user_prompt = (
        "User Preferences:\n"
        f"- Location: {preferences.location}\n"
        f"- Budget Tier: {preferences.budget}\n"
        f"- Cuisine: {preferences.cuisine or 'Any'}\n"
        f"- Minimum Rating: {preferences.min_rating}\n"
        f"- Additional Preferences: {preferences.additional_preferences or 'None'}\n\n"
        f"Candidate Restaurants:\n{candidates_json}"
    )
    
    return system_prompt, user_prompt
