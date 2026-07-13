import json
# pyrefly: ignore [missing-import]
import pytest
from src.models.restaurant import Restaurant
from src.models.recommendation import RecommendationResponse
from src.llm.parser import parse_recommendation_response, build_fallback_response

@pytest.fixture
def sample_candidates():
    return [
        Restaurant(
            id="1",
            name="Jalsa",
            location="Banashankari",
            cuisines=["North Indian"],
            rating=4.1,
            cost_for_two=800,
            budget_tier="medium"
        ),
        Restaurant(
            id="2",
            name="Pizza Place",
            location="Banashankari",
            cuisines=["Italian"],
            rating=4.5,
            cost_for_two=450,
            budget_tier="low"
        )
    ]

def test_parse_valid_json(sample_candidates):
    raw_response = json.dumps({
        "summary": "Here are recommendations.",
        "recommendations": [
            {
                "rank": 1,
                "restaurant_name": "Pizza Place",
                "cuisine": "Italian",
                "rating": 4.5,
                "estimated_cost": "₹450 for two",
                "explanation": "Matches low budget and rating"
            }
        ]
    })
    
    result = parse_recommendation_response(raw_response, sample_candidates)
    assert isinstance(result, RecommendationResponse)
    assert result.summary == "Here are recommendations."
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_name == "Pizza Place"
    assert result.recommendations[0].rank == 1

def test_parse_markdown_json_wrapping(sample_candidates):
    raw_response = (
        "```json\n"
        "{\n"
        '  "summary": "Markdown wrapper",\n'
        '  "recommendations": [\n'
        "    {\n"
        '      "rank": 1,\n'
        '      "restaurant_name": "Jalsa",\n'
        '      "cuisine": "North Indian",\n'
        '      "rating": 4.1,\n'
        '      "estimated_cost": "₹800 for two",\n'
        '      "explanation": "Great food"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```"
    )
    
    result = parse_recommendation_response(raw_response, sample_candidates)
    assert isinstance(result, RecommendationResponse)
    assert result.summary == "Markdown wrapper"
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_name == "Jalsa"

def test_parse_malformed_json_triggers_fallback(sample_candidates):
    raw_response = "{ malformed json ... "
    result = parse_recommendation_response(raw_response, sample_candidates)
    
    # Assert fallback response is triggered
    assert isinstance(result, RecommendationResponse)
    assert "unparseable response" in result.summary
    assert len(result.recommendations) == 2  # Pizza Place, Jalsa (sorted by rating desc)
    assert result.recommendations[0].restaurant_name == "Pizza Place"
    assert result.recommendations[1].restaurant_name == "Jalsa"

def test_hallucination_filtering(sample_candidates):
    # LLM recommends "Hallucinated Palace" which is not in sample_candidates
    raw_response = json.dumps({
        "summary": "Mixed results",
        "recommendations": [
            {
                "rank": 1,
                "restaurant_name": "Hallucinated Palace",
                "cuisine": "Continental",
                "rating": 4.8,
                "estimated_cost": "₹1500 for two",
                "explanation": "Hallucinated"
            },
            {
                "rank": 2,
                "restaurant_name": "Jalsa",
                "cuisine": "North Indian",
                "rating": 4.1,
                "estimated_cost": "₹800 for two",
                "explanation": "Valid restaurant"
            }
        ]
    })
    
    result = parse_recommendation_response(raw_response, sample_candidates)
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_name == "Jalsa"
    # Ranks should be re-indexed starting from 1
    assert result.recommendations[0].rank == 1

def test_all_hallucinated_triggers_fallback(sample_candidates):
    raw_response = json.dumps({
        "summary": "All hallucinated",
        "recommendations": [
            {
                "rank": 1,
                "restaurant_name": "Not In List Cafe",
                "cuisine": "Continental",
                "rating": 4.8,
                "estimated_cost": "₹1500 for two",
                "explanation": "Not in candidates list"
            }
        ]
    })
    
    result = parse_recommendation_response(raw_response, sample_candidates)
    assert "validation errors" in result.summary
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_name == "Pizza Place"
