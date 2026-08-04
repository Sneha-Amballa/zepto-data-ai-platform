"""
Cleaning Pipeline Module

Loads the raw CSV dataset, performs data type conversions, processes stock and rating
fields, applies median imputation for missing numeric values, performs currency conversion,
and exports the cleaned DataFrame to a processed CSV file.
"""

import pandas as pd

from config import RAW_CSV, CLEAN_CSV, GBP_TO_INR
from utils import clean_price, clean_rating, clean_stock, convert_to_inr


def clean_dataset() -> None:
    """
    Loads raw_books.csv, cleans and validates columns, performs GBP to INR conversion,
    imputes missing fields, and outputs the result to cleaned_books.csv.
    """
    print("Loading Raw Dataset...")
    df = pd.read_csv(RAW_CSV)
    print(f"Rows Before Cleaning : {len(df)}")

    # 1. Clean price column
    df["price_gbp"] = df["price"].apply(clean_price)

    # 2. Clean rating column
    df["rating"] = df["star_rating"].apply(clean_rating)

    # 3. Clean stock availability to boolean
    df["in_stock"] = df["availability"].apply(clean_stock)

    # 4. Convert price in GBP to INR using fixed conversion rate
    df["price_inr"] = df["price_gbp"].apply(
        lambda x: convert_to_inr(x, GBP_TO_INR)
    )

    # 5. Handle missing numeric values using median imputation
    median_price = df["price_gbp"].median()
    median_rating = df["rating"].median()

    df["price_gbp"] = df["price_gbp"].fillna(median_price)
    df["rating"] = df["rating"].fillna(median_rating)
    df["price_inr"] = df["price_inr"].fillna(median_price * GBP_TO_INR)

    # 6. Filter for final schema columns
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

    # Save to processed directory
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