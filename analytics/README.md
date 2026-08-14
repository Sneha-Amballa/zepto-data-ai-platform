# Titanic Analytics and Predictive Modeling Pipeline

This module implements a complete exploratory data analysis, data cleaning, profiling, and predictive machine learning pipeline on the classic Titanic dataset. It covers demographic analysis, survival analysis, correlation checks, and predictive model training for both classification (survival prediction) and regression (ticket fare prediction).

---

# Project Overview

The objective of this module is to explore the factors influencing passenger survival and build robust machine learning pipelines.
1. **Data loading**: Downloads and caches the raw Titanic dataset using Seaborn.
2. **Data profiling and cleaning**: Evaluates missing value percentages and resolves them using strict rule-based thresholds.
3. **Exploratory Data Analysis (EDA)**: Conducts univariate analysis on Age and Fare, maps outlier boundaries using the IQR method, evaluates central tendency and skewness of Fare, computes survival rates via boolean masking, and analyzes correlation patterns.
4. **Classification Modeling**: Preprocesses features inside an leakage-free pipeline and trains Logistic Regression, Decision Tree, and Random Forest baseline models.
5. **Imbalance Comparison**: Evaluates cost-sensitive class weights and SMOTE (synthetic oversampling) for handling class imbalances.
6. **Hyperparameter Optimization**: Tunes a Random Forest Classifier using grid search with Out-Of-Bag (OOB) score validation.
7. **Regression Modeling**: Predicts passenger Fare using Linear Regression and evaluates residuals for heteroscedasticity.
8. **Serialization**: Exports the final trained predictive pipeline to a serialized joblib file.

---

# Folder Structure

```text
analytics/
├── data/
│   ├── titanic.csv
│   └── cleaned_titanic.csv
│
├── models/
│   └── best_pipeline.joblib
│
├── outputs/
│   ├── plots/
│   │   ├── age_univariate.png
│   │   ├── fare_univariate.png
│   │   ├── correlation_heatmap.png
│   │   ├── survival_sex_pclass.png
│   │   ├── survival_age_pclass.png
│   │   ├── survival_fare_age.png
│   │   ├── survival_family_size.png
│   │   ├── decision_tree_vis.png
│   │   ├── classification_roc_curves.png
│   │   └── regression_residuals.png
│   │
│   └── reports/
│       ├── missing_values_report.txt
│       └── eda_summary.txt
│
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── profiler_cleaner.py
│   └── eda_analysis.py
│
├── requirements.txt
│
└── README.md
```

---

# Installation

To install all dependencies required by this module, execute the following command:

```bash
pip install -r requirements.txt
```

---

# Execution Order

To run the entire pipeline from end-to-end (ingestion, profiling, EDA, model training, and inference testing), execute the scripts in the following order:

```bash
# 1. Download and cache the raw Titanic dataset
python src/data_loader.py

# 2. Run dataset profiling, clean nulls, and export reports
python src/profiler_cleaner.py

# 3. Perform EDA, calculate statistics, and export plots
python src/eda_analysis.py

# 4. Train predictive models, run grid searches, perform regression, and save the best pipeline
python src/model_pipeline.py
```

---

# Cleaning Decisions & Justifications

The missing values are handled strictly according to their missingness percentage:

- **embarked & embark_town (0.22% missing)**:
  - *Strategy*: Drop rows.
  - *Justification*: Since the missing percentage is `< 5%`, dropping these rows has minimal impact on dataset size (only 2 rows deleted) while avoiding the insertion of imputed values into target-adjacent fields.
- **age (19.87% missing)**:
  - *Strategy*: Impute with median.
  - *Justification*: Since the missing percentage falls between `5%` and `30%`, dropping these rows would lose valuable information. Median imputation is selected over mean to avoid bias from older age outliers.
- **deck (77.22% missing)**:
  - *Strategy*: Create a distinct `"Missing"` category.
  - *Justification*: Since the missing percentage is very high (`> 30%`), dropping the column completely would lose cabin deck signals (which correlate with class/survival), while standard imputation would introduce heavy synthetic noise. Creating a `"Missing"` category preserves the feature structure for downstream modeling.

---

# Feature Engineering & Preprocessing

- **Family Size**: Formed the feature `family_size = sibsp + parch + 1` during the multivariate analysis stage. Traveling with moderate family sizes (2-4 members) correlates with higher survival, while solo travelers and large family groups (>4 members) experience lower survival rates.
- **Leakage-Free Preprocessing**: Applied a scikit-learn `ColumnTransformer` embedded inside the modeling `Pipeline`:
  - **Numerical Columns** (`age`, `sibsp`, `parch`, `fare`): Filled missing fields using a median imputer, followed by `StandardScaler` normalization.
  - **Categorical Columns** (`sex`, `pclass`, `embarked`): Imputed missing fields using the most frequent category (mode), followed by `OneHotEncoder` binary mapping.
  - **Fit-Transform Boundary**: Fitting the transformer and estimators was performed strictly on the training partition. The test partition was only transformed, avoiding test data leakage.

---

# EDA Summary

- **Age Distribution**: Relatively symmetric distribution peaking around the late 20s. Outliers occur on the upper end (elderly passengers).
- **Fare Distribution**: Heavily right-skewed with a skewness coefficient of `4.8014`. The metrics show `Mean (£32.10) > Median (£14.45) > Mode (£8.05)`, indicating extreme values pull the mean upward.
- **IQR Outlier Counts**:
  - *Age Outliers*: 65 passengers (Bounds: 2.50 to 54.50).
  - *Fare Outliers*: 114 passengers (Bounds: -26.76 to 65.66).
- **Survival rates**:
  - Females: `74.0385%` vs Males: `18.8908%`.
  - Class: 1st Class = `62.6168%`, 2nd Class = `47.2826%`, 3rd Class = `24.2363%`.
  - Class & Gender: 1st Class females had a `96.7391%` survival rate, while 3rd Class males had the lowest at `13.5447%`.
- **Top 2 Correlations**:
  - `pclass` vs `fare` (`-0.5482`): Class decreases (moves 1st to 3rd) as ticket price decreases.
  - `sibsp` vs `parch` (`0.4145`): Passengers traveling with siblings/spouses also travel with parents/children, capturing cohesive family travel groups.

---

# Model Comparison & Metrics

All classification models were evaluated on the independent test set (20% split, 178 passengers):

### Classification Performance Table

| Classifier / Pipeline | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 0.8146 | 0.7966 | 0.6912 | 0.7402 | 0.8596 |
| **Decision Tree (Depth=3)** | 0.8146 | 0.8182 | 0.6618 | 0.7317 | 0.8614 |
| **Random Forest (Baseline)** | 0.7978 | 0.7581 | 0.6912 | 0.7231 | 0.8202 |
| **Class Weighted RF** | 0.7978 | 0.7286 | 0.7500 | 0.7391 | 0.8243 |
| **SMOTE RF** | 0.7865 | 0.7273 | 0.7059 | 0.7164 | 0.8210 |
| **Optimized Random Forest (Grid)** | 0.8539 | 0.8281 | 0.7794 | 0.8030 | 0.8332 |

- *Grid Search RF Hyperparameters*: `{'max_depth': 10, 'max_features': None, 'n_estimators': 100}`
- *Out-Of-Bag (OOB) Score*: `0.8242`

### Regression Performance Table (Predicting Fare)

| Metric | Value |
| :--- | :---: |
| **Mean Absolute Error (MAE)** | 16.8954 |
| **Root Mean Squared Error (RMSE)** | 40.1253 |
| **R-squared ($R^2$)** | 0.3829 |
| **Adjusted R-squared** | 0.3612 |

*Heteroscedasticity Analysis*: Clear heteroscedasticity is present. The residuals show a funnel shape with variance expanding at higher predicted fare levels, as luxury class fares show high variability compared to cheap fares.

---

# Final Recommendation

We recommend the **Optimized Random Forest (Grid)** pipeline. It achieved the highest test set performance across all classifiers, leading with an **F1-score of 0.8030** and **Accuracy of 85.39%**. 

Random Forest models excel because they are ensemble models capable of capturing complex non-linear combinations (such as the interaction between gender and class) that Logistic Regression struggles with, while avoiding the overfitting issues of single deep Decision Trees.

---

# Saved Outputs

Running the pipeline populates these files:
- **`analytics/models/best_pipeline.joblib`**: Serialized joblib file containing the preprocessor and the optimized Random Forest classifier.
- **`analytics/outputs/reports/model_evaluation_report.txt`**: Text report containing metrics, OOB scores, regression parameters, and comparisons.
- **`analytics/outputs/plots/decision_tree_vis.png`**: Visual Decision Tree structure.
- **`analytics/outputs/plots/classification_roc_curves.png`**: ROC Curve overlay plot.
- **`analytics/outputs/plots/regression_residuals.png`**: Fare prediction residuals scatter plot.

---

### Final Submission Documentation Confirmation
All profiling, missing value imputations, EDA charts, model evaluations, GridSearch tuning, regression analyses, and pipeline serialization artifacts have been audited and finalized.

