"""
Profiler & Cleaner Module

Loads the raw Titanic dataset, runs profiling metrics (info, describe, shape),
assesses missing-value percentages, cleans the data according to the assignment rules,
saves a report, and exports the cleaned dataset to CSV.
"""

import sys
import io
import pandas as pd
from config import RAW_TITANIC_CSV, CLEANED_TITANIC_CSV, MISSING_REPORT_TXT


def profile_and_clean_data() -> None:
    """
    Reads data/titanic.csv, performs data profiling, calculates missing percentages,
    applies cleaning heuristics, and exports reports and the cleaned dataset.
    """
    if not RAW_TITANIC_CSV.exists():
        print(f"Error: Raw CSV not found at {RAW_TITANIC_CSV}. Run data_loader.py first.")
        sys.exit(1)

    # 1. Load Raw Dataset
    df = pd.read_csv(RAW_TITANIC_CSV)

    # Capture df.info() output as a string to write to report
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    # 2. Print Profiling info to Console
    print("=" * 60)
    print("                 DATA PROFILING & SHAPE                       ")
    print("=" * 60)
    print(f"Shape: {df.shape}\n")
    print("DataFrame Info:")
    print(info_str)
    print("Descriptive Statistics:")
    print(df.describe(include="all"))
    print("=" * 60 + "\n")

    # 3. Assess Missing Value Percentages
    total_rows = len(df)
    missing_counts = df.isnull().sum()
    missing_pcts = (missing_counts / total_rows) * 100

    print("Missing-Value Percentages:")
    for col in df.columns:
        print(f"  {col:15s}: {missing_pcts[col]:6.2f}% ({missing_counts[col]} missing)")
    print("\n")

    # Keep a copy of raw columns and missing stats for reports
    profiling_summary = []
    profiling_summary.append("============================================================\n")
    profiling_summary.append("                 TITANIC DATA PROFILING REPORT              \n")
    profiling_summary.append("============================================================\n\n")
    profiling_summary.append(f"Original Shape: {df.shape}\n\n")
    profiling_summary.append("--- DataFrame Info ---\n")
    profiling_summary.append(info_str + "\n")
    profiling_summary.append("--- Descriptive Statistics ---\n")
    profiling_summary.append(df.describe(include="all").to_string() + "\n\n")
    profiling_summary.append("--- Missing Value Percentages ---\n")
    for col in df.columns:
        profiling_summary.append(f"{col:15s}: {missing_pcts[col]:6.2f}% ({missing_counts[col]} missing)\n")
    profiling_summary.append("\n")

    # 4. Apply Missing Value Handling Heuristics
    cleaning_log = []
    cleaning_log.append("--- Missing Value Handling Strategy ---\n")

    df_cleaned = df.copy()

    # Columns with missing values
    missing_cols = [c for c in df.columns if missing_counts[c] > 0]

    for col in df.columns:
        pct = missing_pcts[col]
        if pct == 0:
            continue

        if pct < 5.0:
            # Rule: < 5% missing -> Drop rows
            rows_before = len(df_cleaned)
            df_cleaned = df_cleaned.dropna(subset=[col])
            dropped = rows_before - len(df_cleaned)
            msg = (f"Column '{col}' ({pct:.2f}% missing): <5% threshold. "
                   f"Dropped {dropped} rows containing null values.")
            print(msg)
            cleaning_log.append(msg + "\n")

        elif 5.0 <= pct <= 30.0:
            # Rule: 5-30% missing -> Impute
            if df_cleaned[col].dtype.kind in 'biufc':  # Numeric
                median_val = df_cleaned[col].median()
                df_cleaned[col] = df_cleaned[col].fillna(median_val)
                msg = (f"Column '{col}' ({pct:.2f}% missing): 5-30% threshold (numeric). "
                       f"Imputed missing values with median: {median_val}.")
            else:  # Categorical
                mode_val = df_cleaned[col].mode()[0]
                df_cleaned[col] = df_cleaned[col].fillna(mode_val)
                msg = (f"Column '{col}' ({pct:.2f}% missing): 5-30% threshold (categorical). "
                       f"Imputed missing values with mode: '{mode_val}'.")
            print(msg)
            cleaning_log.append(msg + "\n")

        else:
            # Rule: >30% missing -> Create "Missing" category
            # Cast column to string to handle 'Missing' values cleanly
            df_cleaned[col] = df_cleaned[col].astype(str)
            df_cleaned[col] = df_cleaned[col].replace({'nan': 'Missing', 'None': 'Missing'})
            df_cleaned[col] = df_cleaned[col].fillna("Missing")
            msg = (f"Column '{col}' ({pct:.2f}% missing): >30% threshold (very high missing). "
                   f"Substituted nulls with 'Missing' category.")
            print(msg)
            cleaning_log.append(msg + "\n")

    cleaning_log.append(f"\nFinal Shape After Cleaning: {df_cleaned.shape}\n")
    print(f"\nFinal Shape After Cleaning: {df_cleaned.shape}\n")

    # Verify no missing values remain
    post_missing = df_cleaned.isnull().sum().sum()
    verification_msg = f"Verification: Number of missing values remaining = {post_missing}"
    print(verification_msg)
    cleaning_log.append(verification_msg + "\n")

    # 5. Save Report to outputs/reports/missing_values_report.txt
    MISSING_REPORT_TXT.parent.mkdir(parents=True, exist_ok=True)
    with open(MISSING_REPORT_TXT, "w", encoding="utf-8") as f:
        f.writelines(profiling_summary)
        f.writelines(cleaning_log)

    print(f"Missing values report saved to: {MISSING_REPORT_TXT}")

    # 6. Save Cleaned Dataset to data/cleaned_titanic.csv
    df_cleaned.to_csv(CLEANED_TITANIC_CSV, index=False)
    print(f"Cleaned dataset saved to: {CLEANED_TITANIC_CSV}\n")


if __name__ == "__main__":
    profile_and_clean_data()
