"""
Configuration for the Zepto Data Ingestion and Processing Pipeline.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw"
PROCESSED_DATA = BASE_DIR / "data" / "processed"
DATABASE = BASE_DIR / "data" / "database"
OUTPUTS = BASE_DIR / "outputs"

# Ensure directories exist
RAW_DATA.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
DATABASE.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

# Files
RAW_CSV = RAW_DATA / "raw_books.csv"
CLEAN_CSV = PROCESSED_DATA / "cleaned_books.csv"
SQLITE_DB = DATABASE / "zepto_books.db"
SQL_RESULTS_TXT = OUTPUTS / "sql_query_results.txt"
PANDAS_RESULTS_TXT = OUTPUTS / "pandas_results.txt"

# Website URLs
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

# Currency Conversion
GBP_TO_INR = 105.50