import logging
from typing import List
from src.config import settings
from src.models.restaurant import Restaurant
from src.models.preferences import UserPreferences

logger = logging.getLogger(__name__)

def filter_restaurants(
    restaurants: List[Restaurant],
    preferences: UserPreferences
) -> List[Restaurant]:
    """
    Applies a deterministic filtering pipeline to narrow candidates before LLM ranking.
    
    Pipeline Steps:
    1. Filter by location (case-insensitive match)
    2. Filter by budget tier (exact match)
    3. Filter by cuisine (case-insensitive substring match, if provided)
    4. Filter by minimum rating (rating >= min_rating)
    5. Sort deterministically (rating desc, cost_for_two desc, name asc)
    6. Cap results to MAX_CANDIDATES
    """
    logger.info(
        f"Filtering {len(restaurants)} restaurants with preferences: "
        f"location={preferences.location}, budget={preferences.budget}, "
        f"cuisine={preferences.cuisine}, min_rating={preferences.min_rating}"
    )

    filtered = []
    seen_names = set()
    loc_query = preferences.location.strip().lower()
    budget_query = preferences.budget.strip().lower()
    cuisine_query = preferences.cuisine.strip().lower() if preferences.cuisine else None
    min_rating_query = preferences.min_rating

    for r in restaurants:
        # Prevent duplicate restaurant recommendations
        name_key = r.name.strip().lower()
        if name_key in seen_names:
            continue

        # 1. Location match (case-insensitive)
        if not r.location or r.location.strip().lower() != loc_query:
            continue

        # 2. Budget match (exact)
        if not r.budget_tier or r.budget_tier.lower() != budget_query:
            continue

        # 3. Cuisine match (case-insensitive substring match in cuisines list, if query exists)
        if cuisine_query:
            if not r.cuisines or not any(cuisine_query in c.lower() for c in r.cuisines):
                continue

        # 4. Rating match (>= min_rating)
        rating_val = r.rating if r.rating is not None else 0.0
        if rating_val < min_rating_query:
            continue

        seen_names.add(name_key)
        filtered.append(r)

    # 5. Deterministic sorting:
    # - rating DESC (primary key; missing/None treated as 0.0)
    # - cost_for_two DESC (secondary key; missing cost treated as 0)
    # - name ASC (tertiary key for tie-breaking)
    def sorting_key(rest: Restaurant):
        rating_part = -rest.rating if rest.rating is not None else 0.0
        cost_part = -rest.cost_for_two if rest.cost_for_two is not None else 0
        name_part = rest.name.lower()
        return (rating_part, cost_part, name_part)

    filtered.sort(key=sorting_key)

    # 6. Cap to configured maximum candidates
    max_c = settings.max_candidates
    capped_list = filtered[:max_c]
    
    logger.info(
        f"Filter pipeline complete: {len(filtered)} matches found. "
        f"Capped to {len(capped_list)} candidates."
    )
    
    return capped_list
