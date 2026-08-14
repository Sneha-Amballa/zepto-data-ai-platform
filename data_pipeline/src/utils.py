"""
Helper functions for cleaning and processing fields.
"""

import re
from typing import Union, Any
import pandas as pd

# Mapping of text-based star ratings to integer values
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def clean_price(price: Any) -> Union[float, Any]:
    """Extracts numeric float price from raw price data."""
    try:
        # Match the first sequence of digits and decimal point
        match = re.search(r'\d+\.?\d*', str(price))
        if match:
            return float(match.group(0))
        return pd.NA
    except (ValueError, TypeError):
        return pd.NA


def clean_rating(rating: Any) -> Union[int, Any]:
    """Converts a text-based rating to an integer equivalent."""
    if pd.isna(rating):
        return pd.NA
    return RATING_MAP.get(str(rating).strip(), pd.NA)


def clean_stock(text: Any) -> bool:
    """Checks if item availability string indicates in-stock status."""
    return "In stock" in str(text)


def convert_to_inr(price_gbp: Any, rate: float) -> Union[float, Any]:
    """Converts a price from GBP to INR."""
    if pd.isna(price_gbp):
        return pd.NA
    try:
        return round(float(price_gbp) * rate, 2)
    except (ValueError, TypeError):
        return pd.NA