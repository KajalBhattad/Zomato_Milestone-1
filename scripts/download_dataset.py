"""
Build-time dataset download script.

This script is executed ONCE during Railway's image build step (via nixpacks.toml).
It downloads the Zomato dataset from HuggingFace and saves it as a local Parquet file
at data/restaurants.parquet, which is then baked into the container image.

This eliminates cold-start dataset downloads: every container restart loads the
pre-built Parquet file (fast local read) instead of re-downloading from HuggingFace.
"""
import logging
import sys
import os

# Ensure the project root (parent of this scripts/ directory) is on sys.path
# so that `from src.data.loader import ...` resolves when this script is run
# directly as `python scripts/download_dataset.py` during the nixpacks build.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("build_dataset")

PARQUET_PATH = "data/restaurants.parquet"


def main():
    # If the parquet already exists (e.g., re-running the build), skip download
    if os.path.exists(PARQUET_PATH):
        size_mb = os.path.getsize(PARQUET_PATH) / (1024 * 1024)
        logger.info(
            f"[BUILD] Parquet already exists at '{PARQUET_PATH}' ({size_mb:.1f} MB). "
            f"Skipping download."
        )
        return

    logger.info(f"[BUILD] Parquet not found at '{PARQUET_PATH}'. Starting download from HuggingFace...")

    # Import here so the script can be run standalone without the full src package
    try:
        from src.data.loader import load_raw_dataset
    except ImportError as e:
        logger.error(f"[BUILD] Failed to import loader: {e}")
        sys.exit(1)

    try:
        # load_raw_dataset() already saves to PARQUET_PATH as a side-effect
        records = load_raw_dataset()
        logger.info(f"[BUILD] Dataset downloaded and saved. {len(records)} records loaded.")
    except Exception as e:
        logger.critical(f"[BUILD] FATAL: Could not download dataset: {e}")
        # Exit non-zero so Railway's build fails loudly rather than silently
        sys.exit(1)

    if not os.path.exists(PARQUET_PATH):
        logger.critical(f"[BUILD] FATAL: Parquet was not saved to '{PARQUET_PATH}' after download.")
        sys.exit(1)

    size_mb = os.path.getsize(PARQUET_PATH) / (1024 * 1024)
    logger.info(f"[BUILD] Successfully baked dataset into image: {size_mb:.1f} MB at '{PARQUET_PATH}'")


if __name__ == "__main__":
    main()
