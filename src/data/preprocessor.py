import hashlib
import logging
from typing import Any, Dict, List, Optional
from src.config import settings
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

def generate_id(name: str, url: Optional[str] = None, address: Optional[str] = None) -> str:
    """Generates a stable MD5 hash as a unique ID."""
    if url:
        return hashlib.md5(url.encode("utf-8")).hexdigest()
    key = f"{name}-{address or ''}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()

def parse_rating(raw_rating: Any) -> tuple[Optional[float], str]:
    """
    Parses Zomato rating string (e.g. '4.1/5', 'NEW', '-') into (rating_float, rating_text).
    Returns (None, 'Unrated') for missing/invalid cases, and (None, 'NEW') for NEW.
    """
    if not raw_rating:
        return None, "Unrated"
    
    val_str = str(raw_rating).strip()
    if val_str == "NEW":
        return None, "NEW"
    elif val_str in ("-", ""):
        return None, "Unrated"
        
    try:
        # Extract first part if string contains '/' (like '4.1/5')
        if "/" in val_str:
            val_str = val_str.split("/")[0].strip()
        rating_val = float(val_str)
        return rating_val, str(rating_val)
    except ValueError:
        logger.warning(f"Could not parse rating value: '{raw_rating}'")
        return None, "Unrated"

def parse_cost(raw_cost: Any) -> Optional[int]:
    """
    Parses cost string (e.g. '800', '1,200') into integer.
    Returns None if missing or invalid.
    """
    if not raw_cost:
        return None
        
    val_str = str(raw_cost).replace(",", "").strip()
    if not val_str:
        return None
        
    try:
        return int(float(val_str))  # Handle cases like '800.0' or '800'
    except ValueError:
        logger.warning(f"Could not parse cost value: '{raw_cost}'")
        return None

def derive_budget_tier(cost: Optional[int]) -> str:
    """
    Derives budget tier ('low', 'medium', 'high') based on cost_for_two.
    Defaults to 'medium' if cost is missing.
    """
    if cost is None:
        return "medium"
        
    if cost <= settings.budget_low_max:
        return "low"
    elif cost <= settings.budget_medium_max:
        return "medium"
    else:
        return "high"

def preprocess_row(row: Dict[str, Any]) -> Optional[Restaurant]:
    """
    Preprocesses a raw dataset row and validates it against the Restaurant schema.
    Returns None if critical fields (name, location) are missing.
    """
    name = row.get("name")
    location = row.get("location")
    
    if not name or not str(name).strip() or not location or not str(location).strip():
        # Drop rows missing name or location
        return None
        
    name = str(name).strip()
    location = str(location).strip()
    
    # Process cuisines
    raw_cuisines = row.get("cuisines", "")
    cuisines_list: List[str] = []
    if raw_cuisines:
        cuisines_list = [c.strip() for c in str(raw_cuisines).split(",") if c.strip()]
        
    # Process rating
    rating, rating_text = parse_rating(row.get("rate"))
    
    # Process cost for two
    # The column name is typically 'approx_cost(for two people)'
    raw_cost = row.get("approx_cost(for two people)")
    cost_for_two = parse_cost(raw_cost)
    
    # Budget tier
    budget_tier = derive_budget_tier(cost_for_two)
    
    # ID
    rest_id = generate_id(name, row.get("url"), row.get("address"))
    
    return Restaurant(
        id=rest_id,
        name=name,
        location=location,
        cuisines=cuisines_list,
        rating=rating,
        rating_text=rating_text,
        cost_for_two=cost_for_two,
        budget_tier=budget_tier,
        dish_liked=str(row.get("dish_liked")).strip() if row.get("dish_liked") else None
    )

def preprocess_dataset(raw_dataset: List[Dict[str, Any]]) -> List[Restaurant]:
    """
    Preprocesses a collection of raw rows into a list of normalized Restaurants.
    """
    normalized_restaurants = []
    for row in raw_dataset:
        restaurant = preprocess_row(row)
        if restaurant:
            normalized_restaurants.append(restaurant)
    logger.info(f"Preprocessed {len(normalized_restaurants)} restaurants out of {len(raw_dataset)} raw records.")
    return normalized_restaurants
