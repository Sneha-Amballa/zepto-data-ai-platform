"""
Initializes SQLite database and populates it with cleaned books data.
"""

import sqlite3
import pandas as pd

from config import CLEAN_CSV, SQLITE_DB


def create_database() -> None:
    """Recreates schema and inserts cleaned CSV data into database."""
    # Load cleaned data
    df = pd.read_csv(CLEAN_CSV)

    # Connect to DB
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    print(f"\nConnected to SQLite Database: {SQLITE_DB}")

    # Reset tables
    cursor.execute("DROP TABLE IF EXISTS books;")
    cursor.execute("DROP TABLE IF EXISTS categories;")

    # Create Categories table
    cursor.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    );
    """)

    # Create Books table
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

    # Populate categories
    categories = df["category"].unique()
    for category in categories:
        cursor.execute("""
            INSERT OR IGNORE INTO categories (category_name)
            VALUES (?);
        """, (category,))
    conn.commit()
    print(f"Categories Inserted : {len(categories)}")

    # Map category names to IDs
    cursor.execute("SELECT category_id, category_name FROM categories;")
    category_dict = {name: cid for cid, name in cursor.fetchall()}

    # Populate books
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