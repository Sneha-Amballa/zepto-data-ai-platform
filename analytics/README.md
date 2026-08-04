# Module 2: Analytics Pipeline (Part A)

This module builds Part A of the Analytics Pipeline using the classic Titanic dataset. It focuses on dataset ingestion, profiling, strict rule-based missing-value handling, statistical univariate/multivariate analysis, correlation evaluation, and visualization.

---

# Dataset Description

The Titanic dataset represents demographic and travel information for 891 passengers on the Titanic's maiden voyage. The core columns include:
- `survived` (int): Survival flag (0 = No, 1 = Yes).
- `pclass` (int): Ticket class (1 = 1st, 2 = 2nd, 3 = 3rd).
- `sex` (str): Gender of passenger (male, female).
- `age` (float): Passenger age in years.
- `sibsp` (int): Number of siblings or spouses aboard the Titanic.
- `parch` (int): Number of parents or children aboard the Titanic.
- `fare` (float): Passenger ticket fare.
- `embarked` (str): Port of Embarkation (C = Cherbourg, Q = Queenstown, S = Southampton).
- `class` (str): Text representation of pclass (First, Second, Third).
- `who` (str): Passenger group category (man, woman, child).
- `adult_male` (bool): True if passenger is adult male, False otherwise.
- `deck` (str): Deck location of cabin (A through G, or missing).
- `embark_town` (str): Embarkation port town name.
- `alive` (str): Text survival indicator (yes, no).
- `alone` (bool): True if traveling with no family, False otherwise.

---

# Cleaning Strategy & Missing-Value Justification

Missing value percentages are computed before cleaning. Based on the calculated percentages, we apply the following rules:

1. **Category `< 5% Missing` (embarked, embark_town at 0.22% missing)**:
   - **Action**: Drop rows.
   - **Justification**: Since the missing rate is extremely low (only 2 out of 891 records), removing these rows has negligible impact on dataset volume while maintaining clean rows with no imputation noise.

2. **Category `5% - 30% Missing` (age at 19.87% missing)**:
   - **Action**: Impute with median.
   - **Justification**: Dropping nearly 20% of the dataset would severely reduce data size and introduce bias. The median age (`28.0`) is preferred over the mean to prevent distortion from outlier values.

3. **Category `Very High Missing (> 30%)` (deck at 77.22% missing)**:
   - **Action**: Create a distinct `"Missing"` category.
   - **Justification**: Dropping the column would result in complete loss of a potentially useful feature (e.g., deck level correlates strongly with cabin class and survival). Replacing nulls with `"Missing"` preserves the feature structure without introducing fake records.

---

# Correlation Interpretation

The Pearson correlation coefficients computed across numerical columns (excluding `adult_male` and `alone`) reveal the following top two strongest relationships:

1. **`pclass` vs `fare` (Correlation: -0.5482)**:
   - **Interpretation**: A strong negative correlation. As the class value increases (e.g., from 1st class down to 3rd class), ticket fare paid decreases. This matches the logical pricing structure where 1st class tickets cost significantly more.
2. **`sibsp` vs `parch` (Correlation: 0.4145)**:
   - **Interpretation**: A moderate positive correlation. Passengers traveling with siblings/spouses also tended to travel with parents/children, representing cohesive family travel groups.

---

# Chart Interpretations

### Univariate Charts
- **[age_univariate.png](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/analytics/outputs/plots/age_univariate.png)**: Shows a relatively symmetric distribution of age centered around the late 20s. Imputing the median age has reinforced the spike at 28 years. The boxplot shows outliers on the upper tail (older passengers).
- **[fare_univariate.png](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/analytics/outputs/plots/fare_univariate.png)**: Displays a highly right-skewed distribution. The mean (£32.10) is pulled significantly higher than the median (£14.45) by a few high-priced tickets, leading to a skewness coefficient of 4.8014. The boxplot confirms a dense field of outliers above £65.66.

### Multivariate Charts
- **[survival_sex_pclass.png](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/analytics/outputs/plots/survival_sex_pclass.png)**: Shows that females survived at a much higher rate (~74%) than males (~19%). Additionally, survival rates decrease for both genders as class moves from 1st to 3rd class.
- **[survival_age_pclass.png](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/analytics/outputs/plots/survival_age_pclass.png)**: Highlights that younger ages (children) had higher survival rates in 1st and 2nd class due to evacuation priorities. However, 3rd class child survival was much lower, indicating socioeconomic status superseded age constraints.
- **[survival_fare_age.png](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/analytics/outputs/plots/survival_fare_age.png)**: Demonstrates that regardless of age, passengers paying higher fares (above £100) survived at a high rate. Low-paying passengers are clustered at the bottom of the scatter plot and show low survival rates.
- **[survival_family_size.png](file:///c:/Users/USER/OneDrive/Desktop/Projects/zepto-data-ai-platform/analytics/outputs/plots/survival_family_size.png)**: Illustrates that small families (size 2-4) had the highest survival rates (~55-70%). Solo travelers (size 1) had low survival rates (~30%), while large family units (>4) show a drop due to coordination issues during evacuation.

---

# Outputs Generated

The following artifacts are successfully populated:
- **Datasets**:
  - `analytics/data/titanic.csv`: Cached raw dataset loaded from Seaborn.
  - `analytics/data/cleaned_titanic.csv`: Cleaned dataset with missing value resolutions.
- **Reports**:
  - `analytics/outputs/reports/missing_values_report.txt`: Profiling outputs and step-by-step missing values actions.
  - `analytics/outputs/reports/eda_summary.txt`: Statistics, outlier counts, survival masking rates, correlations, and standardization metrics.
- **Plots**:
  - `analytics/outputs/plots/age_univariate.png`: Age distribution and boxplot.
  - `analytics/outputs/plots/fare_univariate.png`: Fare distribution and boxplot.
  - `analytics/outputs/plots/correlation_heatmap.png`: Correlation matrix heatmap.
  - `analytics/outputs/plots/survival_sex_pclass.png`: Survival rate by sex and ticket class.
  - `analytics/outputs/plots/survival_age_pclass.png`: Age distribution by survival split by class.
  - `analytics/outputs/plots/survival_fare_age.png`: Fare vs Age scatter colored by survival.
  - `analytics/outputs/plots/survival_family_size.png`: Line plot of survival vs family size.

---

# Execution Steps

1. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Download and cache the dataset**:
   ```bash
   python src/data_loader.py
   ```
3. **Execute profiling and missing value resolution**:
   ```bash
   python src/profiler_cleaner.py
   ```
4. **Execute EDA and generate reports/visualizations**:
   ```bash
   python src/eda_analysis.py
   ```
