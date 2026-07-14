import os
import logging
from typing import Any
import pandas as pd
# pyrefly: ignore [missing-import]
from datasets import load_dataset
from src.config import settings

logger = logging.getLogger(__name__)

def save_dataset_to_parquet(dataset_rows: Any, file_path: str) -> None:
    """
    Saves raw dataset rows as a local Parquet file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    df = pd.DataFrame(dataset_rows)
    df.to_parquet(file_path, index=False)
    logger.info(f"Successfully exported dataset to local Parquet at '{file_path}'")

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
            df = pd.read_parquet(parquet_path)
            # Replace NaN/null elements with None so dict mapping works correctly
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
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
        
        # Save a copy locally for future runs, then load from parquet to free
        # the HF Dataset from memory before preprocessing (prevents OOM on Railway).
        try:
            logger.info(f"Saving a local Parquet copy to '{parquet_path}'...")
            save_dataset_to_parquet(raw_rows, parquet_path)
            # Release the HF Dataset object and return the lighter parquet-backed list
            del raw_rows
            logger.info(f"Loading dataset back from saved Parquet: '{parquet_path}'")
            df = pd.read_parquet(parquet_path)
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
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

