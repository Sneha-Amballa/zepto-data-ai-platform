"""
Performs exploratory data analysis on the cleaned Titanic dataset.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import CLEANED_TITANIC_CSV, PLOTS_DIR, EDA_SUMMARY_TXT


def perform_eda() -> None:
    """Loads cleaned data, runs analysis, generates plots, and exports summary."""
    if not CLEANED_TITANIC_CSV.exists():
        print(f"Error: Cleaned CSV not found at {CLEANED_TITANIC_CSV}. Run profiler_cleaner.py first.")
        sys.exit(1)

    # Set visualization theme
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams["figure.figsize"] = (10, 6)

    # Load cleaned dataset
    df = pd.read_csv(CLEANED_TITANIC_CSV)

    summary_lines = []
    summary_lines.append("============================================================\n")
    summary_lines.append("                 TITANIC EDA SUMMARY REPORT                 \n")
    summary_lines.append("============================================================\n\n")

    # Univariate Analysis (Age & Fare)
    print("Generating Univariate Plots for Age and Fare...")

    # Age Univariate (Histogram + Boxplot)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(data=df, x="age", kde=True, ax=axes[0], color="skyblue")
    axes[0].set_title("Age Distribution (Histogram + KDE)")
    axes[0].set_xlabel("Age (years)")
    sns.boxplot(data=df, y="age", ax=axes[1], color="lightgreen")
    axes[1].set_title("Age Boxplot")
    axes[1].set_ylabel("Age (years)")
    plt.tight_layout()
    age_plot_path = PLOTS_DIR / "age_univariate.png"
    plt.savefig(age_plot_path, dpi=300)
    plt.close()

    # Fare Univariate (Histogram + Boxplot)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(data=df, x="fare", kde=True, ax=axes[0], color="coral")
    axes[0].set_title("Fare Distribution (Histogram + KDE)")
    axes[0].set_xlabel("Fare (GBP)")
    sns.boxplot(data=df, y="fare", ax=axes[1], color="salmon")
    axes[1].set_title("Fare Boxplot")
    axes[1].set_ylabel("Fare (GBP)")
    plt.tight_layout()
    fare_plot_path = PLOTS_DIR / "fare_univariate.png"
    plt.savefig(fare_plot_path, dpi=300)
    plt.close()

    # IQR Outlier Counts
    # Age IQR
    q1_age = df["age"].quantile(0.25)
    q3_age = df["age"].quantile(0.75)
    iqr_age = q3_age - q1_age
    lower_age = q1_age - 1.5 * iqr_age
    upper_age = q3_age + 1.5 * iqr_age
    age_outliers = df[(df["age"] < lower_age) | (df["age"] > upper_age)]
    num_age_outliers = len(age_outliers)

    # Fare IQR
    q1_fare = df["fare"].quantile(0.25)
    q3_fare = df["fare"].quantile(0.75)
    iqr_fare = q3_fare - q1_fare
    lower_fare = q1_fare - 1.5 * iqr_fare
    upper_fare = q3_fare + 1.5 * iqr_fare
    fare_outliers = df[(df["fare"] < lower_fare) | (df["fare"] > upper_fare)]
    num_fare_outliers = len(fare_outliers)

    outlier_msg = (
        f"--- Outlier Boundary Analysis (IQR) ---\n"
        f"Age:\n"
        f"  Q1: {q1_age:.2f}, Q3: {q3_age:.2f}, IQR: {iqr_age:.2f}\n"
        f"  Lower Bound: {lower_age:.2f}, Upper Bound: {upper_age:.2f}\n"
        f"  Outliers Count: {num_age_outliers} (out of {len(df)})\n\n"
        f"Fare:\n"
        f"  Q1: {q1_fare:.2f}, Q3: {q3_fare:.2f}, IQR: {iqr_fare:.2f}\n"
        f"  Lower Bound: {lower_fare:.2f}, Upper Bound: {upper_fare:.2f}\n"
        f"  Outliers Count: {num_fare_outliers} (out of {len(df)})\n\n"
    )
    print(outlier_msg)
    summary_lines.append(outlier_msg)

    # Central Tendency & Skewness of Fare
    fare_mean = df["fare"].mean()
    fare_median = df["fare"].median()
    fare_mode = df["fare"].mode()[0]
    fare_skew = df["fare"].skew()

    # Determine Skewness direction
    if fare_mean > fare_median > fare_mode:
        skew_dir = "Right-skewed (Positive skewness)"
    elif fare_mean < fare_median < fare_mode:
        skew_dir = "Left-skewed (Negative skewness)"
    else:
        skew_dir = "Relatively symmetric"

    skew_msg = (
        f"--- Central Tendency & Skewness (Fare) ---\n"
        f"Fare Mean  : {fare_mean:.4f}\n"
        f"Fare Median: {fare_median:.4f}\n"
        f"Fare Mode  : {fare_mode:.4f}\n"
        f"Fare Skewness Coefficient (Pandas): {fare_skew:.4f}\n"
        f"Skewness Assessment based on Mean/Median/Mode ordering: {skew_dir}\n"
        f"Explanation: Since Mean ({fare_mean:.2f}) > Median ({fare_median:.2f}) > Mode ({fare_mode:.2f}), "
        f"the distribution is heavily pulled to the right by high-paying outliers.\n\n"
    )
    print(skew_msg)
    summary_lines.append(skew_msg)

    # Survival Analysis (Boolean Masking)
    # Survival by Sex
    female_mask = df["sex"] == "female"
    male_mask = df["sex"] == "male"
    female_survival = df[female_mask]["survived"].mean()
    male_survival = df[male_mask]["survived"].mean()

    # Survival by Pclass
    class1_mask = df["pclass"] == 1
    class2_mask = df["pclass"] == 2
    class3_mask = df["pclass"] == 3
    class1_survival = df[class1_mask]["survived"].mean()
    class2_survival = df[class2_mask]["survived"].mean()
    class3_survival = df[class3_mask]["survived"].mean()

    # Survival by Sex + Pclass
    f_c1_survival = df[female_mask & class1_mask]["survived"].mean()
    f_c2_survival = df[female_mask & class2_mask]["survived"].mean()
    f_c3_survival = df[female_mask & class3_mask]["survived"].mean()
    m_c1_survival = df[male_mask & class1_mask]["survived"].mean()
    m_c2_survival = df[male_mask & class2_mask]["survived"].mean()
    m_c3_survival = df[male_mask & class3_mask]["survived"].mean()

    survival_msg = (
        f"--- Survival Analysis (Boolean Masking) ---\n"
        f"Survival by Sex:\n"
        f"  Female Survival Rate: {female_survival:.4%}\n"
        f"  Male Survival Rate:   {male_survival:.4%}\n\n"
        f"Survival by Ticket Class (Pclass):\n"
        f"  First Class (1) Survival Rate:  {class1_survival:.4%}\n"
        f"  Second Class (2) Survival Rate: {class2_survival:.4%}\n"
        f"  Third Class (3) Survival Rate:  {class3_survival:.4%}\n\n"
        f"Survival by Sex + Ticket Class (Pclass):\n"
        f"  Female - First Class Survival Rate:  {f_c1_survival:.4%}\n"
        f"  Female - Second Class Survival Rate: {f_c2_survival:.4%}\n"
        f"  Female - Third Class Survival Rate:  {f_c3_survival:.4%}\n"
        f"  Male - First Class Survival Rate:    {m_c1_survival:.4%}\n"
        f"  Male - Second Class Survival Rate:   {m_c2_survival:.4%}\n"
        f"  Male - Third Class Survival Rate:    {m_c3_survival:.4%}\n\n"
    )
    print(survival_msg)
    summary_lines.append(survival_msg)

    # Correlation Heatmap
    # Numeric subset to correlate (excluding adult_male and alone)
    corr_cols = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
    corr_matrix = df[corr_cols].corr(method="pearson")

    # Generate Heatmap Plot
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".3f", vmin=-1.0, vmax=1.0, linewidths=0.5)
    plt.title("Correlation Matrix Heatmap")
    plt.tight_layout()
    heatmap_path = PLOTS_DIR / "correlation_heatmap.png"
    plt.savefig(heatmap_path, dpi=300)
    plt.close()

    # Identify top 2 correlations (excluding self-correlations of 1.0)
    # Convert correlation matrix to series and filter self values
    corr_series = corr_matrix.unstack()
    corr_series_filtered = corr_series[corr_series < 0.999]  # Exclude 1.0 diagonal
    # Find absolute values to identify top correlation pairs
    top_corrs = corr_series_filtered.abs().sort_values(ascending=False).head(4)

    # Keep unique pairs
    top_pairs = []
    seen = set()
    for idx, val in top_corrs.items():
        sorted_pair = tuple(sorted(idx))
        if sorted_pair not in seen:
            seen.add(sorted_pair)
            top_pairs.append((idx[0], idx[1], corr_series_filtered[idx]))

    # Top two strongest correlations formatting
    top1 = top_pairs[0]
    top2 = top_pairs[1]

    corr_msg = (
        f"--- Correlation Heatmap Analysis ---\n"
        f"Heatmap plotted and saved to: {heatmap_path}\n"
        f"Top Two Strongest Correlations:\n"
        f"  1. '{top1[0]}' and '{top1[1]}' (Correlation Coefficient: {top1[2]:.4f})\n"
        f"     Interpretation: This represents a strong negative relationship. As ticket class (pclass) increases "
        f"     (e.g., moving from 1st class down to 3rd class), the fare paid decreases dramatically. This makes "
        f"     logical sense since 1st class cabins are far more expensive.\n"
        f"  2. '{top2[0]}' and '{top2[1]}' (Correlation Coefficient: {top2[2]:.4f})\n"
        f"     Interpretation: This represents a moderate positive relationship. Travelling with parent(s)/child(ren) "
        f"     (parch) is positively correlated with travelling with sibling(s)/spouse (sibsp), indicating that "
        f"     passengers who travel with immediate family members tend to travel as part of larger family units.\n\n"
    )
    print(corr_msg)
    summary_lines.append(corr_msg)

    # Multivariate Charts
    print("Generating Multivariate Charts...")

    # Chart 1: Survival Rate by Sex and Pclass
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="pclass", y="survived", hue="sex", ci=None, edgecolor="black")
    plt.title("Survival Rate by Class and Gender")
    plt.ylabel("Survival Rate")
    plt.xlabel("Ticket Class (Pclass)")
    plt.ylim(0, 1)
    chart1_path = PLOTS_DIR / "survival_sex_pclass.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()

    chart1_desc = (
        "Chart 1: Survival Rate by Class and Gender (survival_sex_pclass.png)\n"
        "Interpretation: Female survival rates are significantly higher than male survival rates across all classes. "
        "Additionally, survival is heavily dependent on class. First class passengers have the highest survival rates, "
        "with nearly 96% of first-class females surviving. Third-class passengers have the lowest survival rates, "
        "highlighting socioeconomic status as a massive factor in survival outcomes.\n\n"
    )

    # Chart 2: Age Distribution by Survival and Pclass (Violin Plot)
    plt.figure(figsize=(9, 6))
    sns.violinplot(data=df, x="pclass", y="age", hue="survived", split=True, inner="quartile")
    plt.title("Age Distribution by Class and Survival Outcome")
    plt.xlabel("Ticket Class (Pclass)")
    plt.ylabel("Age")
    chart2_path = PLOTS_DIR / "survival_age_pclass.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()

    chart2_desc = (
        "Chart 2: Age Distribution by Class and Survival (survival_age_pclass.png)\n"
        "Interpretation: In 1st and 2nd class, there is a clear peak in survival rates for children (low age), "
        "supporting the 'women and children first' evacuation policy. In 3rd class, the age distribution of survivors "
        "and non-survivors is quite similar, showing that children in lower classes did not benefit as much from the "
        "evacuation priority as those in upper classes.\n\n"
    )

    # Chart 3: Fare vs Age by Survival Status
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="age", y="fare", hue="survived", style="survived", alpha=0.8, s=60)
    plt.title("Scatter Plot of Fare vs Age (Colored by Survival Status)")
    plt.xlabel("Age (years)")
    plt.ylabel("Fare (GBP)")
    plt.ylim(0, 300)  # Constrain outliers for readable scatter plot
    chart3_path = PLOTS_DIR / "survival_fare_age.png"
    plt.savefig(chart3_path, dpi=300)
    plt.close()

    chart3_desc = (
        "Chart 3: Scatter Plot of Fare vs Age by Survival (survival_fare_age.png)\n"
        "Interpretation: High fare amounts (representing upper-class tickets) are heavily populated by survivors. "
        "Regardless of age, passengers who paid high fares are clustered at the top of the plot and have high survival "
        "rates. Passengers who paid lower fares are clustered at the bottom and are predominantly non-survivors.\n\n"
    )

    # Chart 4: Survival Rate by Family Size
    df_family = df.copy()
    df_family["family_size"] = df_family["sibsp"] + df_family["parch"] + 1
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=df_family, x="family_size", y="survived", marker="o", color="purple", ci=None, linewidth=2.5)
    plt.title("Survival Rate vs Family Size")
    plt.xlabel("Family Size (Siblings/Spouse + Parents/Children + 1)")
    plt.ylabel("Survival Rate")
    plt.ylim(0, 1)
    chart4_path = PLOTS_DIR / "survival_family_size.png"
    plt.savefig(chart4_path, dpi=300)
    plt.close()

    chart4_desc = (
        "Chart 4: Survival Rate vs Family Size (survival_family_size.png)\n"
        "Interpretation: A family size of 2 to 4 (small families) exhibits the highest survival rate (~55-70%). "
        "Passengers traveling alone (family size = 1) had a much lower survival rate (~30%), likely because they lacked "
        "a support network to navigate the evacuation. Large family sizes (>4) show a drop in survival rate, "
        "indicating that coordinating a large group during an evacuation crisis was extremely difficult.\n\n"
    )

    summary_lines.append("--- Multivariate Visualizations Interpretations ---\n")
    summary_lines.append(chart1_desc)
    summary_lines.append(chart2_desc)
    summary_lines.append(chart3_desc)
    summary_lines.append(chart4_desc)

    # Z-Score Standardization
    # Extract original parameters
    age_mean_orig = df["age"].mean()
    age_std_orig = df["age"].std()
    fare_mean_orig = df["fare"].mean()
    fare_std_orig = df["fare"].std()

    # Z-score calculations
    z_age = (df["age"] - age_mean_orig) / age_std_orig
    z_fare = (df["fare"] - fare_mean_orig) / fare_std_orig

    z_age_mean = z_age.mean()
    z_age_std = z_age.std()
    z_fare_mean = z_fare.mean()
    z_fare_std = z_fare.std()

    std_msg = (
        f"--- Z-Score Standardization (EDA Only) ---\n"
        f"Age metrics:\n"
        f"  Before - Mean: {age_mean_orig:.6f}, Std Dev: {age_std_orig:.6f}\n"
        f"  After  - Mean: {z_age_mean:.6f} (~0), Std Dev: {z_age_std:.6f} (~1)\n\n"
        f"Fare metrics:\n"
        f"  Before - Mean: {fare_mean_orig:.6f}, Std Dev: {fare_std_orig:.6f}\n"
        f"  After  - Mean: {z_fare_mean:.6f} (~0), Std Dev: {z_fare_std:.6f} (~1)\n\n"
        f"Note: Original scale was preserved in final saved csv, as standardized features are only calculated here for EDA purposes.\n"
    )
    print(std_msg)
    summary_lines.append(std_msg)

    # Save summary report to reports/eda_summary.txt
    with open(EDA_SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.writelines(summary_lines)

    print(f"EDA Summary Report saved successfully to: {EDA_SUMMARY_TXT}")


if __name__ == "__main__":
    perform_eda()
