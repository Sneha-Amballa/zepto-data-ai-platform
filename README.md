# Zepto Data AI Platform

Welcome to the **Zepto Data AI Platform** workspace. This repository represents a unified multi-module platform consisting of a scraped and normalized data ingestion pipeline, a predictive machine learning analytics module, and a LangGraph-powered customer support RAG assistant.

---

## Repository Structure

```text
zepto-data-ai-platform/
│
├── README.md               # Unified platform documentation (this file)
│
├── data_pipeline/          # Module 1: Data Ingestion & DB Normalization
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── database/
│   │   └── books.db
│   ├── src/
│   │   ├── config.py
│   │   ├── scraper.py
│   │   ├── cleaner.py
│   │   ├── database.py
│   │   ├── sql_queries.py
│   │   ├── pandas_queries.py
│   │   └── utils.py
│   ├── requirements.txt
│   └── README.md
│
├── analytics/              # Module 2: Data Profiling, EDA, & Machine Learning
│   ├── data/
│   │   ├── titanic.csv
│   │   └── cleaned_titanic.csv
│   ├── models/
│   │   └── best_pipeline.joblib
│   ├── outputs/
│   │   ├── plots/          # Visualizations (.png)
│   │   └── reports/        # Analytical findings (.txt)
│   ├── src/
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   ├── profiler_cleaner.py
│   │   ├── eda_analysis.py
│   │   └── model_pipeline.py
│   ├── requirements.txt
│   └── README.md
│
└── support_assistant/      # Module 3: Policy RAG & LangGraph API
    ├── docs/               # Policy documents (doc_01.txt to doc_08.txt)
    ├── chroma_db/          # Persistent vector database
    ├── requirements.txt
    ├── Dockerfile
    ├── schema.py
    ├── prompts.py
    ├── graph.py
    ├── ingest.py
    ├── main.py
    ├── test_pipeline.py
    ├── test_api.py
    └── README.md
```

---

## Setup & Installations

Each module manages its dependencies independently via a local `requirements.txt` file located in its respective folder. This isolates libraries and prevents conflicts.

To setup the platform:

1. **Create and Activate a Virtual Environment** in the repository root:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Dependencies** for the module you wish to run:
   - For **Data Pipeline**:
     ```bash
     pip install -r data_pipeline/requirements.txt
     ```
   - For **Analytics**:
     ```bash
     pip install -r analytics/requirements.txt
     ```
   - For **Support Assistant**:
     ```bash
     pip install -r support_assistant/requirements.txt
     ```

---

## How to Run Each Module End-to-End

Activate the virtual environment, change to the respective module directory, and run the commands as follows:

### Module 1: Data Pipeline
Extract, clean, and load book catalogs from [books.toscrape.com](https://books.toscrape.com):
```bash
cd data_pipeline
python src/scraper.py
python src/cleaner.py
python src/database.py
python src/sql_queries.py
python src/pandas_queries.py
```
This will extract 100 books from the first 5 pagination pages, clean columns (price conversions, star mapping, availability parsing), save a normalized SQLite DB (`database/books.db`), execute 6 validation queries, and output a side-by-side SQL vs. Pandas merge verification showing identical counts.

---

### Module 2: Analytics Pipeline
Run profiling, exploratory analysis, standardizations, regressions, and predictive classification on the Titanic dataset:
```bash
cd analytics
python src/data_loader.py
python src/profiler_cleaner.py
python src/eda_analysis.py
python src/model_pipeline.py
```
This loads the dataset exactly once via Seaborn, dumps it to `data/titanic.csv`, applies threshold-based imputation rules, computes outlier bounds and Fare skewness direction, generates 10 univariate/multivariate charts, trains three classification models (imbalance-weighted and optimized via GridSearchCV to F1 = `0.8030`), fits a Fare linear regression (verifying residuals heteroscedasticity), and serializes the preprocessing + random forest classifier pipeline into `models/best_pipeline.joblib`.

---

### Module 3: Customer Support Assistant
Build, index, and query the local policies RAG assistant:
```bash
cd support_assistant
# 1. Ingest policy documents
python ingest.py
# 2. Run graph integration test
python test_pipeline.py
# 3. Launch FastAPI server
python -m uvicorn main:app --host 127.0.0.1 --port 7860
```
This reads the 8 policy text files, encodes them locally via the `all-MiniLM-L6-v2` transformer, populates the persistent `chroma_db/`, compiles a LangGraph StateGraph (featuring intent classification, vector search retrieval, and direct routing), and launches a FastAPI endpoint at `http://127.0.0.1:7860/ask`.

---

## Design-Decision Summaries

### Module 1: Data Pipeline
- **SQLite Database Normalization**: Standardized into `categories` and `books` tables linked by a Foreign Key (`category_id`) to ensure database integrity and avoid redundant text entries.
- **Star Rating & Availability Handling**: Converted textual numbers (`One` to `Five`) to integers (`1` to `5`) and parsed availability (`In stock`) to booleans to support query arithmetic and numerical indexing.
- **Conversion Rate**: Standardized prices to INR using a fixed, declared conversion rate of **1 GBP = 105.50 INR**.

### Module 2: Analytics Pipeline
- **Missing Value Handling Rules**:
  - `embarked` / `embark_town` (<5% missing) $\rightarrow$ Dropped rows (minimal data loss, avoids guessing origin location).
  - `age` (19.87% missing) $\rightarrow$ Imputed using median (avoids skewed mean representation due to elderly outliers).
  - `deck` (77.22% missing) $\rightarrow$ Replaced with `"Missing"` category (very high null rate; preserves potential cabin deck location features without synthetic imputation bias).
- **Stratified Splitting**: Applied stratified train/test splitting based on the `survived` target to ensure that both training and testing sets retain equalized survival ratios (~38% survived), avoiding evaluation bias.
- **Model Choice**: Selected the **Optimized Random Forest** over Logistic Regression and shallow Decision Trees. Random Forest handles non-linear combination features (e.g. sex-class interaction) while avoiding tree overfitting.
- **Standardization**: Applied Z-score standardization on Age and Fare as an EDA-only sanity check to compare centered scaling. Final preprocessing normalization was kept inside pipeline transformers to avoid test leakage.

### Module 3: Support Assistant
- **Chunking Strategy**: Since each of the 8 policy documents describes a single topic and contains fewer than 100 words, they are treated as individual chunks, avoiding semantic fragmentation.
- **Embedding Model**: Used the open-source `sentence-transformers` model `all-MiniLM-L6-v2` locally. It produces high-quality, 384-dimensional cosine similarity embeddings without needing API tokens or network requests.
- **LangGraph StateGraph**: Designed exactly 3 nodes (`classify_intent`, `retrieve_and_answer`, `direct_answer`) with a conditional routing edge. This ensures structured execution control and decouples classification logic from prompt generation.
- **Validation Retry Loop**: Implemented a validation retry loop inside the actual LLM `MOCK_LLM=0` branch. If the output fails to parse into the validated Pydantic schema (`AnswerResponse`), it repeats the request up to 3 times to guarantee API payload reliability.

---

## Submission Affirmations

- **Unified Codebase**: Built inside a single public git repository containing `data_pipeline/`, `analytics/`, and `support_assistant/` modules.
- **Written Interpretations**: All analytical findings, metrics tables, and recommendations are composed solely in Markdown text (in READMEs) without external dependencies on slideshows, videos, or PDFs.
- **Git History**: Contains feature branches (`feature/analytics-polish`, `feature/support-assistant-rag`, `feature/support-assistant-api`) that were created, committed to multiple times, and merged back into the `main` branch.
- **Service Free Tier**: All integrations (like Seaborn datasets, local sentence-transformers, ChromaDB vector databases, and stubs for Groq) are designed to run fully offline without fees.
