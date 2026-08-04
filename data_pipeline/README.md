# Project Overview

The **Data Pipeline** module is an end-to-end data ingestion, cleaning, and processing subsystem for the Zepto Data AI Platform. It is designed to:
1. Scrape books catalog data from the online store [Books to Scrape](https://books.toscrape.com).
2. Clean and preprocess fields such as price, availability, and star ratings.
3. Handle missing numeric variables via median imputation.
4. Perform currency conversion to Indian Rupees (INR) using a fixed conversion factor.
5. Store the clean structured datasets in a normalized SQLite relational database containing Primary/Foreign key constraints.
6. Execute analytical queries using raw SQL, replicate operations via Pandas, and verify the equivalence of both methods.

---

# Folder Structure

```text
data_pipeline/
├── README.md
├── requirements.txt
├── outputs/
│   ├── sql_query_results.txt
│   └── pandas_results.txt
├── data/
│   ├── raw/
│   │   └── raw_books.csv
│   ├── processed/
│   │   └── cleaned_books.csv
│   └── database/
│       └── zepto_books.db
└── src/
    ├── config.py
    ├── scraper.py
    ├── cleaner.py
    ├── utils.py
    ├── database.py
    ├── sql_queries.py
    └── pandas_queries.py
```

---

# Technologies

- **requests**: For fetching remote web pages using HTTP protocols.
- **BeautifulSoup** (bs4) & **lxml**: For parsing the fetched HTML content and extracting details about books catalog.
- **pandas**: For structural data transformation, imputation, file exported operations, and query operations.
- **sqlite3**: Relational SQL engine embedded in Python for schema construction and execution.
- **NumPy**: Underpins DataFrame numeric operations and datatype alignments.

---

# Installation

To install all components required by this module, execute the following command:

```bash
pip install -r requirements.txt
```

---

# Execution Order

To run the pipeline from ingestion to query execution and verification, run the scripts in the following order:

```bash
# 1. Scrape catalog pages and extract raw CSV data
python src/scraper.py

# 2. Clean fields, impute missing data, and convert currencies
python src/cleaner.py

# 3. Create the database and insert normalized records
python src/database.py

# 4. Run analytical SQL queries and save console reports
python src/sql_queries.py

# 5. Run comparative pandas queries, execute pd.merge, and run similarity checks
python src/pandas_queries.py
```

---

# Data Cleaning

Data cleaning operations are defined in `src/utils.py` and run inside `src/cleaner.py`:

- **Price Conversion**: Raw prices like `£51.77` are processed by stripping the currency symbol (`£`) and casting the value to a float.
- **Rating Conversion**: Textual representations of star ratings (e.g. `"One"`, `"Two"`, `"Three"`, `"Four"`, `"Five"`) are mapped to integer values `1` through `5` using a lookup mapping.
- **Availability Conversion**: Check availability textual descriptions for `"In stock"`. If present, availability is represented as a boolean `True`; otherwise, it returns `False`.
- **Median Imputation**:
  - Missing or malformed price values are imputed with the median price computed across the non-null dataset.
  - Missing star ratings are imputed with the median rating.
  - Missing INR values are filled with the imputed GBP value multiplied by the fixed exchange rate.
- **Fixed GBP→INR Conversion**: Translates book pricing in GBP to Indian Rupees (INR) using a fixed multiplier.

---

# Fixed Currency Rate

The exchange rate applied in the pipeline is:
```text
1 GBP = 105.50 INR
```
*Note: This exchange factor is the project-defined constant.*

---

# Database Schema

The SQLite database (`data/database/zepto_books.db`) contains two normalized tables to prevent redundant category storage:

### 1. `categories` Table
- `category_id` (INTEGER, Primary Key, AUTOINCREMENT): Unique identifier for a category.
- `category_name` (TEXT, UNIQUE, NOT NULL): Name of the category (e.g., `'Books'`).

### 2. `books` Table
- `book_id` (INTEGER, Primary Key, AUTOINCREMENT): Unique identifier for a book.
- `title` (TEXT, NOT NULL): Book title.
- `price_gbp` (REAL): Numerical price in British Pounds.
- `price_inr` (REAL): Numerical price in Indian Rupees.
- `rating` (INTEGER): Star rating ranging from 1 to 5.
- `in_stock` (INTEGER): Boolean flag representing stock presence (0 or 1).
- `category_id` (INTEGER): Foreign Key reference mapped to `categories(category_id)`.

---

# SQL Queries

The following six SQL queries are executed and evaluated in `src/sql_queries.py`:

1. **SELECT + WHERE**: Extracts book `title`, `price_gbp`, and `rating` for books rated 4 stars and above.
2. **ORDER BY + LIMIT**: Identifies the Top 10 most expensive books by sorting by `price_gbp` in descending order.
3. **DISTINCT**: Lists unique values present inside the `rating` column.
4. **BETWEEN**: Filters books with prices falling within the range of `£20.0` and `£40.0`.
5. **IN**: Extracts books with ratings belonging to the set `(4, 5)`.
6. **JOIN**: Unifies the `books` and `categories` tables on `category_id` to retrieve unified category metadata sorted by rating and price.

---

# Pandas Queries

The script `src/pandas_queries.py` replicates the SQL analytics operations inside Python:
- **`pd.read_sql()`**: Executes raw SELECT and ORDER SQL scripts and loads results directly into Pandas DataFrames.
- **`pd.merge()`**: Re-implements SQL `INNER JOIN` in Pandas by merging the individual `books` and `categories` tables on the shared column `category_id`.
- **Comparison**: Evaluates output equivalency using `sql_join.equals(pandas_join)` to prove that the database relational output and the memory-merged result are identical.

---

# Outputs Generated

Running the pipeline populates these files:
- **[raw_books.csv](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/data_pipeline/data/raw/raw_books.csv)**: Contains raw scraped data.
- **[cleaned_books.csv](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/data_pipeline/data/processed/cleaned_books.csv)**: Contains processed and cleaned book listings.
- **[zepto_books.db](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/data_pipeline/data/database/zepto_books.db)**: Relational SQLite database.
- **[sql_query_results.txt](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/data_pipeline/outputs/sql_query_results.txt)**: Formatted console export of the six SQL queries.
- **[pandas_results.txt](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/data_pipeline/outputs/pandas_results.txt)**: Formatted export of Pandas query results and the JOIN equivalency comparison.

---

# Validation Status

- **Status**: Passed
- **Verification Method**: End-to-end comparative analysis between SQL JOIN query and Pandas merge operations
- **Equivalency Result**: 100% Identical (outputs match)
