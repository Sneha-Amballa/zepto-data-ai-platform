"""
Utility Functions

Contains helper functions for cleaning price, rating, and stock fields,
and for converting currencies.
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
    """
    Cleans the raw price string by extracting the numeric float value.
    
    Args:
        price: Raw price data (usually a string like '£51.77' or 'Â£51.77').
        
    Returns:
        float: The numeric value of the price, or pd.NA if conversion fails.
    """
    try:
        # Match the first sequence of digits and decimal point
        match = re.search(r'\d+\.?\d*', str(price))
        if match:
            return float(match.group(0))
        return pd.NA
    except (ValueError, TypeError):
        return pd.NA


def clean_rating(rating: Any) -> Union[int, Any]:
    """
    Converts a text-based rating description (e.g. 'Three') to its integer equivalent (e.g. 3).
    
    Args:
        rating: The raw rating string.
        
    Returns:
        int: The mapped integer value (1-5), or pd.NA if not found.
    """
    if pd.isna(rating):
        return pd.NA
    return RATING_MAP.get(str(rating).strip(), pd.NA)


def clean_stock(text: Any) -> bool:
    """
    Converts an availability description to a boolean indicating whether the item is in stock.
    
    Args:
        text: Raw stock description text.
        
    Returns:
        bool: True if the item is in stock, False otherwise.
    """
    return "In stock" in str(text)


def convert_to_inr(price_gbp: Any, rate: float) -> Union[float, Any]:
    """
    Converts a price in GBP to INR using a fixed currency conversion rate.
    
    Args:
        price_gbp: Numeric price in GBP.
        rate: The fixed conversion rate factor.
        
    Returns:
        float: Rounded converted price in INR, or pd.NA if inputs are invalid/missing.
    """
    if pd.isna(price_gbp):
        return pd.NA
    try:
        return round(float(price_gbp) * rate, 2)
    except (ValueError, TypeError):
        return pd.NA