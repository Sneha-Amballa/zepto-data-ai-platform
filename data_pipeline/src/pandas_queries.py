"""
Pandas Queries Module

Performs comparison between:
1. SQL JOIN query run via sqlite3 + pd.read_sql
2. Pandas pd.merge() operation on individual 'books' and 'categories' DataFrames

Saves the outputs and comparison result to outputs/pandas_results.txt.
"""

import sqlite3
import pandas as pd

from config import SQLITE_DB, PANDAS_RESULTS_TXT


def main() -> None:
    """
    Connects to the database, pulls raw tables and inner-joined views,
    replicates the inner join using Pandas merge, compares the two results,
    and writes comparison output to outputs/pandas_results.txt.
    """
    conn = sqlite3.connect(SQLITE_DB)

    print("=" * 60)
    print("DATABASE CONNECTED")
    print("=" * 60)

    # 1. Query 1 using pd.read_sql()
    print("\nQuery 1 using pd.read_sql()\n")
    query1 = """
    SELECT title,
           price_gbp,
           rating
    FROM books
    WHERE rating >= 4;
    """
    df1 = pd.read_sql(query1, conn)
    print(df1.head())

    # 2. Query 2 using pd.read_sql()
    print("\nQuery 2 using pd.read_sql()\n")
    query2 = """
    SELECT title,
           price_gbp
    FROM books
    ORDER BY price_gbp DESC
    LIMIT 10;
    """
    df2 = pd.read_sql(query2, conn)
    print(df2)

    # 3. Read complete tables for pandas merge
    books = pd.read_sql("SELECT * FROM books", conn)
    categories = pd.read_sql("SELECT * FROM categories", conn)

    # 4. SQL JOIN execution via SQLite
    sql_join = pd.read_sql("""
        SELECT b.title,
               c.category_name,
               b.rating,
               b.price_gbp
        FROM books b
        INNER JOIN categories c ON b.category_id = c.category_id;
    """, conn)

    # 5. Pandas Merge reproduction
    pandas_join = pd.merge(
        books,
        categories,
        on="category_id",
        how="inner"
    )
    pandas_join = pandas_join[
        [
            "title",
            "category_name",
            "rating",
            "price_gbp"
        ]
    ]

    # Display Results on console
    print("\n")
    print("=" * 60)
    print("SQL JOIN")
    print("=" * 60)
    print(sql_join.head())

    print("\n")
    print("=" * 60)
    print("PANDAS MERGE")
    print("=" * 60)
    print(pandas_join.head())

    # Compare outputs
    same = sql_join.equals(pandas_join)

    print("\n")
    print("=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"Outputs Match : {same}")

    conn.close()

    # Save to outputs/pandas_results.txt
    PANDAS_RESULTS_TXT.parent.mkdir(parents=True, exist_ok=True)
    with open(PANDAS_RESULTS_TXT, "w", encoding="utf-8") as f:
        f.write("======================================================================\n")
        f.write("                       PANDAS JOIN COMPARISON                         \n")
        f.write("======================================================================\n\n")

        f.write("1. SQL JOIN RESULT (First 10 Rows):\n")
        f.write("-" * 40 + "\n")
        f.write(sql_join.head(10).to_string(index=False))
        f.write("\n\n")

        f.write("2. PANDAS MERGE RESULT (First 10 Rows):\n")
        f.write("-" * 40 + "\n")
        f.write(pandas_join.head(10).to_string(index=False))
        f.write("\n\n")

        f.write("3. COMPARISON RESULT:\n")
        f.write("-" * 40 + "\n")
        f.write(f"SQL JOIN and Pandas Merge DataFrames are Identical (DataFrame.equals): {same}\n")

    print(f"\nPandas query results saved to: {PANDAS_RESULTS_TXT}\n")


if __name__ == "__main__":
    main()