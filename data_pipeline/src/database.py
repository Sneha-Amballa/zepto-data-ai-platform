"""
Database Module

Initializes the SQLite database with a normalized schema.
Creates 'categories' and 'books' tables with Primary Key and Foreign Key constraints,
and loads the cleaned books data from CSV into the database.
"""

import sqlite3
import pandas as pd

from config import CLEAN_CSV, SQLITE_DB


def create_database() -> None:
    """
    Connects to the SQLite database, resets (drops and recreates) the schema
    for 'categories' and 'books', and populates them with data from cleaned_books.csv.
    """
    # Load cleaned data
    df = pd.read_csv(CLEAN_CSV)

    # Establish database connection
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    print(f"\nConnected to SQLite Database: {SQLITE_DB}")

    # Drop existing tables to ensure clean, duplicate-free execution
    cursor.execute("DROP TABLE IF EXISTS books;")
    cursor.execute("DROP TABLE IF EXISTS categories;")

    # Create Categories Table
    cursor.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    );
    """)

    # Create Books Table
    cursor.execute("""
    CREATE TABLE books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price_gbp REAL,
        price_inr REAL,
        rating INTEGER,
        in_stock INTEGER,
        category_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(category_id)
    );
    """)
    print("Tables Created Successfully")

    # Insert unique categories into Categories Table
    categories = df["category"].unique()
    for category in categories:
        cursor.execute("""
            INSERT OR IGNORE INTO categories (category_name)
            VALUES (?);
        """, (category,))
    conn.commit()
    print(f"Categories Inserted : {len(categories)}")

    # Retrieve categories to construct a name -> ID lookup dictionary
    cursor.execute("SELECT category_id, category_name FROM categories;")
    category_dict = {name: cid for cid, name in cursor.fetchall()}

    # Insert books into Books Table
    books_inserted = 0
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """, (
            row["title"],
            row["price_gbp"],
            row["price_inr"],
            int(row["rating"]),
            int(row["in_stock"]),
            category_dict[row["category"]]
        ))
        books_inserted += 1

    conn.commit()
    print(f"Books Inserted      : {books_inserted}")
    print("Database Saved Successfully\n")

    conn.close()


if __name__ == "__main__":
    create_database()