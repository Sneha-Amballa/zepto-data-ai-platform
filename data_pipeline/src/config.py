"""
Configuration module for the Zepto Data Ingestion and Processing Pipeline.
Defines base directory, data folders, input/output files, URLs, and currency conversion rate.
"""

from pathlib import Path

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# DATA FOLDERS
# -----------------------------
RAW_DATA = BASE_DIR / "data" / "raw"
PROCESSED_DATA = BASE_DIR / "data" / "processed"
DATABASE = BASE_DIR / "data" / "database"
OUTPUTS = BASE_DIR / "outputs"

# Ensure all directory structures exist
RAW_DATA.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
DATABASE.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

# -----------------------------
# FILES
# -----------------------------
RAW_CSV = RAW_DATA / "raw_books.csv"
CLEAN_CSV = PROCESSED_DATA / "cleaned_books.csv"
SQLITE_DB = DATABASE / "zepto_books.db"
SQL_RESULTS_TXT = OUTPUTS / "sql_query_results.txt"
PANDAS_RESULTS_TXT = OUTPUTS / "pandas_results.txt"

# -----------------------------
# WEBSITE
# -----------------------------
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

# -----------------------------
# FIXED CONVERSION RATE
# -----------------------------
GBP_TO_INR = 105.50