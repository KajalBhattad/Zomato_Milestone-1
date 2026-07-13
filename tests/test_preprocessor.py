import pytest
from src.data.preprocessor import (
    parse_rating,
    parse_cost,
    derive_budget_tier,
    preprocess_row,
    preprocess_dataset
)
from src.config import settings

def test_parse_rating():
    # Valid ratings
    assert parse_rating("4.1/5") == (4.1, "4.1")
    assert parse_rating("3.5") == (3.5, "3.5")
    assert parse_rating(4.2) == (4.2, "4.2")
    
    # Placeholder strings
    assert parse_rating("NEW") == (None, "NEW")
    assert parse_rating("-") == (None, "Unrated")
    assert parse_rating("") == (None, "Unrated")
    assert parse_rating(None) == (None, "Unrated")
    
    # Invalid strings
    assert parse_rating("not-a-rating") == (None, "Unrated")

def test_parse_cost():
    # Valid costs
    assert parse_cost("800") == 800
    assert parse_cost("1,200") == 1200
    assert parse_cost(500) == 500
    assert parse_cost("500.0") == 500
    
    # Empty / Invalid costs
    assert parse_cost("") is None
    assert parse_cost(None) is None
    assert parse_cost("free") is None

def test_derive_budget_tier():
    # settings.budget_low_max = 500
    # settings.budget_medium_max = 1500
    
    # Low budget
    assert derive_budget_tier(200) == "low"
    assert derive_budget_tier(500) == "low"
    
    # Medium budget
    assert derive_budget_tier(501) == "medium"
    assert derive_budget_tier(1500) == "medium"
    
    # High budget
    assert derive_budget_tier(1501) == "high"
    assert derive_budget_tier(3000) == "high"
    
    # Missing cost fallback
    assert derive_budget_tier(None) == "medium"

def test_preprocess_row_valid():
    row = {
        "name": "Jalsa",
        "location": "Banashankari",
        "cuisines": "North Indian, Mughlai, Chinese",
        "rate": "4.1/5",
        "approx_cost(for two people)": "800",
        "url": "https://www.zomato.com/bangalore/jalsa",
        "address": "Banashankari, Bangalore"
    }
    
    restaurant = preprocess_row(row)
    assert restaurant is not None
    assert restaurant.name == "Jalsa"
    assert restaurant.location == "Banashankari"
    assert restaurant.cuisines == ["North Indian", "Mughlai", "Chinese"]
    assert restaurant.rating == 4.1
    assert restaurant.rating_text == "4.1"
    assert restaurant.cost_for_two == 800
    assert restaurant.budget_tier == "medium"
    assert restaurant.id is not None
    assert restaurant.raw == row

def test_preprocess_row_skips_on_missing_critical():
    # Missing name
    row_no_name = {
        "location": "Banashankari",
        "rate": "4.1/5"
    }
    assert preprocess_row(row_no_name) is None

    # Missing location
    row_no_loc = {
        "name": "Jalsa",
        "rate": "4.1/5"
    }
    assert preprocess_row(row_no_loc) is None
    
    # Empty name string
    row_empty_name = {
        "name": "   ",
        "location": "Banashankari"
    }
    assert preprocess_row(row_empty_name) is None

def test_preprocess_dataset():
    rows = [
        {"name": "Rest A", "location": "Loc A", "rate": "4.0/5"},
        {"name": "  ", "location": "Loc B"},  # Should be skipped
        {"name": "Rest C", "location": "Loc C", "rate": "3.5/5"}
    ]
    
    results = preprocess_dataset(rows)
    assert len(results) == 2
    assert results[0].name == "Rest A"
    assert results[1].name == "Rest C"
