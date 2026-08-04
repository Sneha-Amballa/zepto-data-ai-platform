"""
database.py

Creates the SQLite database and required tables
for the Zepto Data & AI Platform.
"""

from pathlib import Path
import sqlite3


# -------------------------------------------------------
# Database Location
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FOLDER = BASE_DIR / "database"

DATABASE_FOLDER.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_FOLDER / "zepto_products.db"


# -------------------------------------------------------
# Create Connection
# -------------------------------------------------------

def create_connection():
    """
    Create SQLite database connection.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    return connection


# -------------------------------------------------------
# Create Tables
# -------------------------------------------------------

def create_tables(connection):

    cursor = connection.cursor()

    # Categories Table

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS categories(

            category_id INTEGER PRIMARY KEY AUTOINCREMENT,

            category_name TEXT UNIQUE NOT NULL

        )

    """)

    # Products Table

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS products(

            product_id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            price REAL,

            description TEXT,

            rating REAL,

            review_count INTEGER,

            availability TEXT,

            product_url TEXT,

            scraped_at TEXT,

            category_id INTEGER,

            FOREIGN KEY(category_id)

            REFERENCES categories(category_id)

        )

    """)

    connection.commit()


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main():

    connection = create_connection()

    create_tables(connection)

    connection.close()

    print("Database created successfully.")


if __name__ == "__main__":

    main()