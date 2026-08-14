"""
Loads, cleans, and processes the raw books dataset.
"""

import pandas as pd

from config import RAW_CSV, CLEAN_CSV, GBP_TO_INR
from utils import clean_price, clean_rating, clean_stock, convert_to_inr


def clean_dataset() -> None:
    """Loads raw CSV, cleans, and outputs cleaned dataset."""
    print("Loading Raw Dataset...")
    df = pd.read_csv(RAW_CSV)
    print(f"Rows Before Cleaning : {len(df)}")

    # Clean price
    df["price_gbp"] = df["price"].apply(clean_price)

    # Clean rating
    df["rating"] = df["star_rating"].apply(clean_rating)

    # Clean stock
    df["in_stock"] = df["availability"].apply(clean_stock)

    # Convert GBP to INR
    df["price_inr"] = df["price_gbp"].apply(
        lambda x: convert_to_inr(x, GBP_TO_INR)
    )

    # Impute missing values
    median_price = df["price_gbp"].median()
    median_rating = df["rating"].median()

    df["price_gbp"] = df["price_gbp"].fillna(median_price)
    df["rating"] = df["rating"].fillna(median_rating)
    df["price_inr"] = df["price_inr"].fillna(median_price * GBP_TO_INR)

    # Filter columns
    df = df[
        [
            "title",
            "category",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock"
        ]
    ]

    # Save CSV
    df.to_csv(CLEAN_CSV, index=False)

    print()
    print("=" * 50)
    print("Cleaning Completed")
    print("=" * 50)
    print()
    print(f"Rows After Cleaning : {len(df)}")
    print(f"Saved To : {CLEAN_CSV}")
    print()
    print(df.head())


if __name__ == "__main__":
    clean_dataset()
