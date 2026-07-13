import pytest
from unittest.mock import patch
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from src.main import app
from src.models.recommendation import RecommendationResponse, Recommendation

client = TestClient(app)

@pytest.fixture
def mock_engine_response():
    return RecommendationResponse(
        summary="Test recommendations",
        recommendations=[
            Recommendation(
                rank=1,
                restaurant_name="Jalsa",
                cuisine="North Indian",
                rating=4.1,
                estimated_cost="₹800 for two",
                explanation="Fits medium budget"
            )
        ]
    )

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cache_initialized" in data
    assert "groq_configured" in data

@patch("src.api.routes.is_cache_initialized", return_value=True)
@patch("src.api.routes.RecommendationEngine")
def test_recommend_endpoint_success(mock_engine_class, mock_cache_init, mock_engine_response):
    # Setup mock engine instance
    mock_instance = mock_engine_class.return_value
    mock_instance.get_recommendations.return_value = mock_engine_response
    
    payload = {
        "location": "Banashankari",
        "budget": "medium",
        "cuisine": "Indian",
        "min_rating": 4.0
    }
    
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Test recommendations"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["restaurant_name"] == "Jalsa"

def test_recommend_endpoint_validation_failure():
    # Missing required field 'location'
    payload = {
        "budget": "medium",
        "min_rating": 4.0
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()

@patch("src.api.routes.is_cache_initialized", return_value=True)
@patch("src.api.routes.RecommendationEngine")
def test_recommend_endpoint_not_found(mock_engine_class, mock_cache_init):
    mock_instance = mock_engine_class.return_value
    mock_instance.get_recommendations.return_value = RecommendationResponse(
        summary="No restaurants match your selected criteria. Try adjusting your preferences.",
        recommendations=[]
    )
    
    payload = {
        "location": "EmptyLocation",
        "budget": "low",
        "min_rating": 5.0
    }
    
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "No restaurants match" in response.json()["detail"]


def test_root_endpoint_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Zomato AI Dashboard" in response.text


