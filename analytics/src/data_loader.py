"""
Loads the raw Titanic dataset using Seaborn and caches it locally.
"""

import seaborn as sns
from config import RAW_TITANIC_CSV


def load_and_save_titanic() -> None:
    """Loads and saves the Titanic dataset to raw CSV."""
    if RAW_TITANIC_CSV.exists():
        print(f"Dataset already exists at {RAW_TITANIC_CSV}. Skipping download.")
        return

    print("Loading Titanic dataset from seaborn...")
    df = sns.load_dataset("titanic")

    print(f"Saving dataset to {RAW_TITANIC_CSV}...")
    df.to_csv(RAW_TITANIC_CSV, index=False)
    print("Dataset loaded and cached successfully.")


if __name__ == "__main__":
    load_and_save_titanic()
