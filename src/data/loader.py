import os
import gc
import logging
from typing import Any, List
import pandas as pd
# pyrefly: ignore [missing-import]
from datasets import load_dataset
from src.config import settings
from src.models.restaurant import Restaurant
from src.data.preprocessor import preprocess_row

logger = logging.getLogger(__name__)

# Only these columns are used by preprocess_row(). Loading only these from the
# 20+ column parquet cuts memory from ~300 MB to ~60 MB.
REQUIRED_COLUMNS = [
    "name", "location", "cuisines", "rate",
    "approx_cost(for two people)", "url", "address", "dish_liked"
]


def save_dataset_to_parquet(dataset_rows: Any, file_path: str) -> None:
    """
    Saves raw dataset rows as a local Parquet file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    df = pd.DataFrame(dataset_rows)
    df.to_parquet(file_path, index=False)
    logger.info(f"Successfully exported dataset to local Parquet at '{file_path}'")


def _load_and_preprocess_from_parquet(parquet_path: str) -> List[Restaurant]:
    """
    Memory-efficient loader: reads only the required columns from the parquet
    file and converts rows to Restaurant objects one at a time, avoiding the
    massive intermediate list-of-dicts that was causing OOM on Railway (512 MB).

    Peak memory: ~80 MB (only needed columns) instead of ~800 MB (all columns +
    full dict list + df copy).
    """
    # Only read the columns we actually use
    available_cols = pd.read_parquet(parquet_path, columns=[]).columns.tolist()
    cols_to_load = [c for c in REQUIRED_COLUMNS if c in available_cols]

    logger.info(f"Reading {len(cols_to_load)} columns from parquet (out of {len(available_cols)} total)")
    df = pd.read_parquet(parquet_path, columns=cols_to_load)

    # Process row-by-row directly from the DataFrame — no to_dict(orient="records")
    restaurants: List[Restaurant] = []
    for idx in range(len(df)):
        # Build a small dict for just this row (gets garbage collected each iteration)
        row = {col: (None if pd.isna(val) else val) for col, val in df.iloc[idx].items()}
        restaurant = preprocess_row(row)
        if restaurant:
            restaurants.append(restaurant)

    logger.info(f"Preprocessed {len(restaurants)} restaurants from {len(df)} rows")

    # Explicitly free the DataFrame
    del df
    gc.collect()

    return restaurants


def load_restaurants_from_local(parquet_path: str) -> List[Restaurant]:
    """
    Loads and preprocesses restaurants from the local parquet file.
    Returns the list of Restaurant objects ready for caching.
    """
    logger.info(f"Loading dataset from local Parquet backup: '{parquet_path}'")
    return _load_and_preprocess_from_parquet(parquet_path)


def load_raw_dataset() -> Any:
    """
    Loads the Zomato restaurant dataset. First attempts to load from the local
    Parquet file. If it doesn't exist, loads from the Hugging Face Hub and saves
    a copy locally.

    Returns:
        An iterable collection of raw records (list of dicts).
    """
    parquet_path = settings.local_parquet_path

    # 1. Attempt to load from local Parquet file
    if os.path.exists(parquet_path):
        logger.info(f"Loading dataset from local Parquet backup: '{parquet_path}'")
        try:
            # Read only needed columns to save memory
            available_cols = pd.read_parquet(parquet_path, columns=[]).columns.tolist()
            cols_to_load = [c for c in REQUIRED_COLUMNS if c in available_cols]
            df = pd.read_parquet(parquet_path, columns=cols_to_load)
            df = df.where(pd.notnull(df), None)
            records = df.to_dict(orient="records")
            del df
            gc.collect()
            return records
        except Exception as e:
            logger.error(f"Failed to load local Parquet file '{parquet_path}': {e}. Falling back to Hugging Face.")

    # 2. Fallback: Load from Hugging Face Hub
    dataset_name = settings.hf_dataset_name
    logger.info(f"Loading Hugging Face dataset: '{dataset_name}'")
    try:
        dataset = load_dataset(dataset_name)
        split = "train"
        if "train" not in dataset:
            split = list(dataset.keys())[0]
            logger.warning(f"'train' split not found. Using '{split}' split instead.")
        raw_rows = dataset[split]

        # Save a copy locally for future runs
        try:
            logger.info(f"Saving a local Parquet copy to '{parquet_path}'...")
            save_dataset_to_parquet(raw_rows, parquet_path)
            del raw_rows
            del dataset
            gc.collect()
            logger.info(f"Loading dataset back from saved Parquet: '{parquet_path}'")
            available_cols = pd.read_parquet(parquet_path, columns=[]).columns.tolist()
            cols_to_load = [c for c in REQUIRED_COLUMNS if c in available_cols]
            df = pd.read_parquet(parquet_path, columns=cols_to_load)
            df = df.where(pd.notnull(df), None)
            records = df.to_dict(orient="records")
            del df
            gc.collect()
            return records
        except Exception as save_err:
            logger.warning(f"Could not save local Parquet backup: {save_err}. Using in-memory dataset.")
            return list(raw_rows)
    except Exception as e:
        logger.error(f"Failed to load dataset '{dataset_name}' from Hugging Face: {e}")
        raise e

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.info("Initializing dataset export utility...")
    load_raw_dataset()
    logger.info("Dataset loading and local export check complete.")
