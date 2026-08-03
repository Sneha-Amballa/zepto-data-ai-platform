# Zepto Data AI Platform

A unified platform for data ingestion, analytics, and support assistant capabilities.

## Repository Structure

```text
zepto-data-ai-platform/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data_pipeline/         # Data ingestion and processing pipeline
│   ├── README.md
│   ├── requirements.txt
│   ├── src/               # Ingestion & processing source code
│   ├── data/
│   │   ├── raw/           # Raw landing zone
│   │   └── processed/     # Processed/Cleaned data
│   ├── database/          # DB connections or local DB storage
│   └── output/            # Exported outputs
│
├── analytics/             # Model training and data analysis
│   ├── README.md
│   ├── requirements.txt
│   ├── notebooks/         # Jupyter notebooks
│   ├── src/               # Analytics logic
│   ├── dataset/           # Dataset storage
│   ├── models/            # Serialized models
│   └── output/            # Analysis outputs & reports
│
└── support_assistant/     # RAG support assistant system
    ├── README.md
    ├── requirements.txt
    ├── src/               # RAG logic & APIs
    ├── documents/         # Source documents
    ├── vector_store/      # Vector database index files
    └── output/            # QA and support helper outputs
```

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
