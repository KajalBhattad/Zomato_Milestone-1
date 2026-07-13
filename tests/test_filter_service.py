import pytest
from src.models.restaurant import Restaurant
from src.models.preferences import UserPreferences
from src.services.filter_service import filter_restaurants

@pytest.fixture
def sample_restaurants():
    return [
        Restaurant(
            id="1",
            name="Jalsa",
            location="Banashankari",
            cuisines=["North Indian", "Mughlai"],
            rating=4.1,
            cost_for_two=800,
            budget_tier="medium"
        ),
        Restaurant(
            id="2",
            name="Pizza Place",
            location="Banashankari",
            cuisines=["Italian", "Pizza"],
            rating=4.5,
            cost_for_two=450,
            budget_tier="low"
        ),
        Restaurant(
            id="3",
            name="Bistro-1",
            location="Banashankari",
            cuisines=["Continental", "Italian"],
            rating=4.5,
            cost_for_two=1200,
            budget_tier="medium"
        ),
        Restaurant(
            id="4",
            name="Bistro-2",
            location="Banashankari",
            cuisines=["Continental", "Italian"],
            rating=4.5,
            cost_for_two=900,
            budget_tier="medium"
        ),
        Restaurant(
            id="5",
            name="Dhaba",
            location="Indiranagar",
            cuisines=["North Indian"],
            rating=4.2,
            cost_for_two=400,
            budget_tier="low"
        ),
        Restaurant(
            id="6",
            name="Low Rating Cafe",
            location="Banashankari",
            cuisines=["Chinese"],
            rating=2.5,
            cost_for_two=300,
            budget_tier="low"
        )
    ]

def test_filter_by_location(sample_restaurants):
    prefs = UserPreferences(location="banashankari", budget="medium", min_rating=0.0)
    results = filter_restaurants(sample_restaurants, prefs)
    
    # Indiranagar restaurant should be excluded
    assert all(r.location == "Banashankari" for r in results)
    assert len(results) == 3  # Jalsa, Bistro-1, Bistro-2

def test_filter_by_budget(sample_restaurants):
    prefs = UserPreferences(location="Banashankari", budget="low", min_rating=0.0)
    results = filter_restaurants(sample_restaurants, prefs)
    
    # Medium budget restaurants excluded
    assert all(r.budget_tier == "low" for r in results)
    assert len(results) == 2  # Pizza Place, Low Rating Cafe

def test_filter_by_cuisine(sample_restaurants):
    # Search for Italian (should match "Italian, Pizza" and "Continental, Italian")
    prefs = UserPreferences(location="Banashankari", budget="medium", cuisine="Italian", min_rating=0.0)
    results = filter_restaurants(sample_restaurants, prefs)
    
    assert len(results) == 2  # Bistro-1, Bistro-2
    assert all("Italian" in r.cuisines for r in results)

    # Search for North Indian
    prefs_north = UserPreferences(location="Banashankari", budget="medium", cuisine="North Indian", min_rating=0.0)
    results_north = filter_restaurants(sample_restaurants, prefs_north)
    assert len(results_north) == 1  # Jalsa

def test_filter_by_min_rating(sample_restaurants):
    prefs = UserPreferences(location="Banashankari", budget="low", min_rating=4.0)
    results = filter_restaurants(sample_restaurants, prefs)
    
    assert len(results) == 1  # Pizza Place (4.5), Low Rating Cafe (2.5) excluded
    assert results[0].name == "Pizza Place"

def test_deterministic_sorting_and_tie_breaking(sample_restaurants):
    # Bistro-1 and Bistro-2 both have 4.5 rating, Banashankari location, medium budget, and Italian cuisine
    prefs = UserPreferences(location="Banashankari", budget="medium", cuisine="Italian", min_rating=0.0)
    results = filter_restaurants(sample_restaurants, prefs)
    
    # Expected order:
    # 1. Bistro-1 (Rating 4.5, Cost 1200) -> higher cost comes first in our sort function
    # 2. Bistro-2 (Rating 4.5, Cost 900)
    assert len(results) == 2
    assert results[0].name == "Bistro-1"
    assert results[1].name == "Bistro-2"

def test_zero_matches(sample_restaurants):
    prefs = UserPreferences(location="Banashankari", budget="high", min_rating=4.8)
    results = filter_restaurants(sample_restaurants, prefs)
    assert len(results) == 0

def test_filter_and_sort_with_unrated(sample_restaurants):
    # Add an unrated restaurant to the list
    unrated_restaurant = Restaurant(
        id="7",
        name="New Unrated Spot",
        location="Banashankari",
        cuisines=["Fast Food"],
        rating=None,  # NEW / Unrated
        rating_text="NEW",
        cost_for_two=200,
        budget_tier="low"
    )
    all_rests = sample_restaurants + [unrated_restaurant]

    # If min_rating is 3.0, the unrated restaurant (None -> 0.0) should be excluded
    prefs_min_rating = UserPreferences(location="Banashankari", budget="low", min_rating=3.0)
    res_min = filter_restaurants(all_rests, prefs_min_rating)
    assert unrated_restaurant not in res_min

    # If min_rating is 0.0, the unrated restaurant should be included but sorted to the bottom
    prefs_zero_rating = UserPreferences(location="Banashankari", budget="low", min_rating=0.0)
    res_zero = filter_restaurants(all_rests, prefs_zero_rating)
    assert unrated_restaurant in res_zero
    # "Pizza Place" (4.5) -> "Low Rating Cafe" (2.5) -> "New Unrated Spot" (None/0.0)
    assert res_zero[-1].name == "New Unrated Spot"

