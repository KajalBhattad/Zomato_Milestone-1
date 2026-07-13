import logging
from typing import List, Optional
from src.models.restaurant import Restaurant
from src.data.loader import load_raw_dataset
from src.data.preprocessor import preprocess_dataset

logger = logging.getLogger(__name__)

# Module-level cache storage
_cached_restaurants: Optional[List[Restaurant]] = None

def initialize_cache(force: bool = False) -> List[Restaurant]:
    """
    Loads and preprocesses the Hugging Face dataset, storing the normalized
    list in memory.
    
    Args:
        force: If True, reloads the dataset even if it is already cached.
    """
    global _cached_restaurants
    if _cached_restaurants is not None and not force:
        logger.info("Dataset cache already initialized.")
        return _cached_restaurants
        
    logger.info("Initializing dataset cache...")
    try:
        raw_rows = load_raw_dataset()
        # Convert dataset split/generator to list of dicts if necessary
        # HF datasets can be directly iterated or indexed as dict-like objects
        _cached_restaurants = preprocess_dataset(raw_rows)
        logger.info(f"Successfully initialized cache with {len(_cached_restaurants)} restaurants.")
        return _cached_restaurants
    except Exception as e:
        logger.error(f"Error initializing dataset cache: {e}")
        raise e

def get_restaurants() -> List[Restaurant]:
    """
    Retrieves the cached list of restaurants. Automatically initializes
    the cache if it hasn't been loaded yet.
    """
    global _cached_restaurants
    if _cached_restaurants is None:
        return initialize_cache()
    return _cached_restaurants

def is_cache_initialized() -> bool:
    """Returns True if the dataset cache contains loaded records."""
    return _cached_restaurants is not None
