# pyrefly: ignore [missing-import]
import pytest
from src.models.restaurant import Restaurant
from src.models.preferences import UserPreferences
from src.services.prompt_builder import build_prompt

def test_build_prompt():
    prefs = UserPreferences(
        location="Indiranagar",
        budget="low",
        cuisine="Chinese",
        min_rating=4.0,
        additional_preferences="quiet environment"
    )
    
    candidates = [
        Restaurant(
            id="1",
            name="Rest A",
            location="Indiranagar",
            cuisines=["Chinese"],
            rating=4.2,
            cost_for_two=300,
            budget_tier="low"
        )
    ]
    
    system_prompt, user_prompt = build_prompt(prefs, candidates)
    
    # Assert system prompt properties
    assert "expert restaurant recommendation assistant" in system_prompt
    assert "Output JSON Schema" in system_prompt
    assert "MUST ONLY recommend restaurants" in system_prompt
    
    # Assert user prompt preferences are injected
    assert "Indiranagar" in user_prompt
    assert "low" in user_prompt
    assert "Chinese" in user_prompt
    assert "4.0" in user_prompt
    assert "quiet environment" in user_prompt
    assert "Rest A" in user_prompt
