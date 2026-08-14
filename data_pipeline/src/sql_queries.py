"""
Executes SQLite database queries and writes results to file.
"""

import sqlite3
import pandas as pd

from config import SQLITE_DB, SQL_RESULTS_TXT


def run_query(title: str, query: str) -> None:
    """Executes a SQL query, prints to console, and appends to output file."""
    # Print to console
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    conn = sqlite3.connect(SQLITE_DB)
    df = pd.read_sql(query, conn)
    print(df)
    conn.close()

    # Save to file
    with open(SQL_RESULTS_TXT, "a", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("-" * len(title) + "\n")
        f.write(f"SQL Statement:\n{query.strip()}\n\n")
        f.write("Result Table:\n")
        f.write(df.to_string(index=False))
        f.write("\n")
        f.write("=" * 70 + "\n\n")


def main() -> None:
    """Clears results file and executes all SQL queries."""
    # Initialize results file
    SQL_RESULTS_TXT.parent.mkdir(parents=True, exist_ok=True)
    with open(SQL_RESULTS_TXT, "w", encoding="utf-8") as f:
        f.write("======================================================================\n")
        f.write("                       SQL QUERY RESULTS                             \n")
        f.write("======================================================================\n\n")

    # Query 1: SELECT + WHERE
    query1 = """
    SELECT title,
           price_gbp,
           rating
    FROM books
    WHERE rating >= 4;
    """
    run_query(
        "Query 1 : Books with Rating >= 4",
        query1
    )

    # Query 2: ORDER BY + LIMIT
    query2 = """
    SELECT title,
           price_gbp
    FROM books
    ORDER BY price_gbp DESC
    LIMIT 10;
    """
    run_query(
        "Query 2 : Top 10 Most Expensive Books",
        query2
    )

    # Query 3: DISTINCT
    query3 = """
    SELECT DISTINCT rating
    FROM books
    ORDER BY rating;
    """
    run_query(
        "Query 3 : Distinct Ratings",
        query3
    )

    # Query 4: BETWEEN
    query4 = """
    SELECT title,
           price_gbp
    FROM books
    WHERE price_gbp BETWEEN 20.0 AND 40.0;
    """
    run_query(
        "Query 4 : Books Between £20 and £40",
        query4
    )

    # Query 5: IN
    query5 = """
    SELECT title,
           rating
    FROM books
    WHERE rating IN (4, 5);
    """
    run_query(
        "Query 5 : Books Rated 4 or 5",
        query5
    )

    # Query 6: JOIN
    query6 = """
    SELECT b.title,
           c.category_name,
           b.rating,
           b.price_gbp
    FROM books b
    INNER JOIN categories c ON b.category_id = c.category_id
    ORDER BY b.rating DESC,
             b.price_gbp DESC
    LIMIT 10;
    """
    run_query(
        "Query 6 : JOIN Categories and Books",
        query6
    )


if __name__ == "__main__":
    main()