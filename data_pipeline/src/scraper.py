"""
BooksToScrape Scraper Module

Scrapes the first five pages of the books catalogue from https://books.toscrape.com/
and saves the raw scraped books data to a CSV file.
"""

from typing import List, Dict, Any
import requests
import pandas as pd
from bs4 import BeautifulSoup

from config import CATALOGUE_URL, RAW_CSV

# Default request headers
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_star_rating(article: BeautifulSoup) -> str:
    """
    Extracts the star rating class string from a book article element.
    
    Args:
        article: A BeautifulSoup Tag representing the <article class="product_pod">.
        
    Returns:
        str: The rating class name (e.g. 'One', 'Two', 'Three', 'Four', 'Five').
    """
    classes = article.find("p", class_="star-rating")["class"]
    return classes[1]


def scrape_page(page: int) -> List[Dict[str, Any]]:
    """
    Scrapes a single page of books from the catalog and extracts relevant details.
    
    Args:
        page: The page number to scrape.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dict represents a scraped book.
    """
    url = CATALOGUE_URL.format(page)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    books = []
    articles = soup.find_all("article", class_="product_pod")

    for article in articles:
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").text.strip()
        rating = get_star_rating(article)
        availability = article.find("p", class_="instock availability").text.strip()
        book_link = article.h3.a["href"]

        books.append({
            "title": title,
            "price": price,
            "star_rating": rating,
            "availability": availability,
            "category": "Books",
            "book_link": book_link
        })

    return books


def scrape_books() -> List[Dict[str, Any]]:
    """
    Scrapes the first 5 pages of books to scrape a total of 100 books.
    
    Returns:
        List[Dict[str, Any]]: A combined list of scraped book dictionaries.
    """
    all_books = []
    for page in range(1, 6):
        print(f"Scraping Page {page}")
        books = scrape_page(page)
        all_books.extend(books)
    return all_books


def save_books(data: List[Dict[str, Any]]) -> None:
    """
    Converts raw scraped books data to a DataFrame and saves it as a CSV.
    
    Args:
        data: A list of dictionaries containing book details.
    """
    df = pd.DataFrame(data)
    df.to_csv(RAW_CSV, index=False)

    print()
    print("=" * 50)
    print("Scraping Completed")
    print("=" * 50)
    print()
    print(f"Books Scraped : {len(df)}")
    print(f"Saved To      : {RAW_CSV}")
    print()


if __name__ == "__main__":
    books_data = scrape_books()
    save_books(books_data)