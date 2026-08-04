"""
Configuration module for the Analytics Pipeline.
Defines folder structure for data, plots, and reports, and ensures they exist on load.
"""

from pathlib import Path

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# OUTPUT AND DATA FOLDERS
# -----------------------------
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
PLOTS_DIR = OUTPUTS_DIR / "plots"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Ensure all directory structures exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# FILES
# -----------------------------
RAW_TITANIC_CSV = DATA_DIR / "titanic.csv"
CLEANED_TITANIC_CSV = DATA_DIR / "cleaned_titanic.csv"
MISSING_REPORT_TXT = REPORTS_DIR / "missing_values_report.txt"
EDA_SUMMARY_TXT = REPORTS_DIR / "eda_summary.txt"
BEST_MODEL_JOBLIB = DATA_DIR / "best_pipeline.joblib"
MODEL_REPORT_TXT = REPORTS_DIR / "model_evaluation_report.txt"

