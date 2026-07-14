import gc
import os
import logging
import threading
from typing import List, Optional
from src.models.restaurant import Restaurant
from src.config import settings

logger = logging.getLogger(__name__)

# Module-level cache storage and a lock to prevent concurrent initialization
_cached_restaurants: Optional[List[Restaurant]] = None
_cache_lock = threading.Lock()

def initialize_cache(force: bool = False) -> List[Restaurant]:
    """
    Loads and preprocesses the Hugging Face dataset, storing the normalized
    list in memory.

    This function is safe to call from multiple threads simultaneously.
    Only the first caller will perform the actual download/load; subsequent
    concurrent callers will block on the lock and then return the already-
    populated cache without re-downloading.

    Args:
        force: If True, reloads the dataset even if it is already cached.
    """
    global _cached_restaurants

    # Fast path: already loaded and not forcing a reload
    if _cached_restaurants is not None and not force:
        logger.info("Dataset cache already initialized.")
        return _cached_restaurants

    # Slow path: acquire the lock so only one thread downloads at a time
    with _cache_lock:
        # Re-check inside the lock in case another thread just finished
        if _cached_restaurants is not None and not force:
            logger.info("Dataset cache was initialized by another thread. Returning cached data.")
            return _cached_restaurants

        logger.info("Initializing dataset cache...")
        try:
            parquet_path = settings.local_parquet_path

            if os.path.exists(parquet_path):
                # Memory-efficient path: reads only needed columns from parquet
                # and processes row-by-row without a huge intermediate dict list.
                # Peak memory: ~80 MB instead of ~800 MB.
                from src.data.loader import load_restaurants_from_local
                _cached_restaurants = load_restaurants_from_local(parquet_path)
            else:
                # Fallback: download from HuggingFace, save parquet, then preprocess
                from src.data.loader import load_raw_dataset
                from src.data.preprocessor import preprocess_dataset
                raw_rows = load_raw_dataset()
                _cached_restaurants = preprocess_dataset(raw_rows)
                del raw_rows
                gc.collect()

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
