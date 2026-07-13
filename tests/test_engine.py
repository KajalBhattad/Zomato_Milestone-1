# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import MagicMock
from src.models.restaurant import Restaurant
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.recommendation_engine import RecommendationEngine
from src.llm.groq_client import GroqLLMClient

@pytest.fixture
def mock_groq_client():
    client = MagicMock(spec=GroqLLMClient)
    client.complete.return_value = '{"summary": "Test", "recommendations": [{"rank": 1, "restaurant_name": "Jalsa", "cuisine": "North Indian", "rating": 4.1, "estimated_cost": "₹800 for two", "explanation": "Fits"}]}'
    return client

@pytest.fixture
def mock_restaurants(monkeypatch):
    restaurants = [
        Restaurant(
            id="1",
            name="Jalsa",
            location="Banashankari",
            cuisines=["North Indian"],
            rating=4.1,
            cost_for_two=800,
            budget_tier="medium"
        )
    ]
    monkeypatch.setattr("src.services.recommendation_engine.get_restaurants", lambda: restaurants)
    return restaurants

def test_engine_success(mock_groq_client, mock_restaurants):
    engine = RecommendationEngine(groq_client=mock_groq_client)
    prefs = UserPreferences(location="Banashankari", budget="medium", min_rating=0.0)
    
    response = engine.get_recommendations(prefs)
    
    assert isinstance(response, RecommendationResponse)
    assert response.summary == "Test"
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant_name == "Jalsa"
    
    # Assert Groq client was invoked
    mock_groq_client.complete.assert_called_once()

def test_engine_empty_candidates(mock_groq_client, mock_restaurants):
    engine = RecommendationEngine(groq_client=mock_groq_client)
    # Filter for indiranagar where mock_restaurants is in Banashankari (so 0 matches)
    prefs = UserPreferences(location="Indiranagar", budget="medium", min_rating=0.0)
    
    response = engine.get_recommendations(prefs)
    
    assert isinstance(response, RecommendationResponse)
    assert "No restaurants match" in response.summary
    assert len(response.recommendations) == 0
    
    # Assert Groq client was NOT invoked
    mock_groq_client.complete.assert_not_called()

def test_engine_groq_failure_fallback(mock_groq_client, mock_restaurants):
    # Setup mock to raise an exception (like rate limits or timeout)
    mock_groq_client.complete.side_effect = Exception("API Offline")
    engine = RecommendationEngine(groq_client=mock_groq_client)
    prefs = UserPreferences(location="Banashankari", budget="medium", min_rating=0.0)
    
    response = engine.get_recommendations(prefs)
    
    # Assert it falls back gracefully
    assert isinstance(response, RecommendationResponse)
    assert "currently offline" in response.summary
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant_name == "Jalsa"
    assert "Recommended based on its high rating" in response.recommendations[0].explanation
