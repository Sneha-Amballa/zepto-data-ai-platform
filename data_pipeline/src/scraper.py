"""
scraper.py

Scrapes product information from the WebScraper.io
test e-commerce website and saves it as raw CSV.
"""

from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


# ==========================================================
# Configuration
# ==========================================================

BASE_URL = "https://webscraper.io/test-sites/e-commerce/allinone"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "Zepto-Data-Pipeline"
    )
}


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FOLDER = BASE_DIR / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RAW_FOLDER / "raw_products.csv"


# ==========================================================
# Download Page
# ==========================================================

def get_page():

    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ==========================================================
# Parse Products
# ==========================================================

def parse_products(html):

    soup = BeautifulSoup(html, "lxml")

    products = []

    cards = soup.select(".thumbnail")

    for card in cards:

        name = card.select_one(".title")
        price = card.select_one(".price")
        description = card.select_one(".description")
        reviews = card.select_one(".ratings p.pull-right")
        stars = len(card.select(".ratings span.glyphicon-star"))

        products.append({

            "product_name":
                name.get("title") if name else None,

            "price":
                price.text.strip() if price else None,

            "description":
                description.text.strip() if description else None,

            "rating":
                stars,

            "review_count":
                reviews.text.split()[0]
                if reviews else None,

            "category":
                "Electronics",

            "product_url":
                BASE_URL,

            "scraped_at":
                datetime.now().isoformat()

        })

    return products


# ==========================================================
# Save CSV
# ==========================================================

def save_csv(products):

    dataframe = pd.DataFrame(products)

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False
    )

    return dataframe


# ==========================================================
# Main
# ==========================================================

def main():

    print("Downloading page...")

    html = get_page()

    print("Extracting products...")

    products = parse_products(html)

    dataframe = save_csv(products)

    print(f"Products Scraped : {len(dataframe)}")

    print(f"Saved To : {OUTPUT_FILE}")


if __name__ == "__main__":

    main()