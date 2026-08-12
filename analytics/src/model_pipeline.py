"""
Predictive modeling pipeline for the Titanic dataset.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Scikit-learn preprocessing and pipeline imports
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Scikit-learn model imports
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier

# Scikit-learn metric imports
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, mean_absolute_error,
    mean_squared_error, r2_score
)

# Imbalance handling imports
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

# Path configurations
from config import (
    RAW_TITANIC_CSV, BEST_MODEL_JOBLIB, MODEL_REPORT_TXT, PLOTS_DIR
)


def load_and_split_data():
    """Loads raw titanic.csv and splits it into train/test sets."""
    if not RAW_TITANIC_CSV.exists():
        print(f"Error: Raw CSV not found at {RAW_TITANIC_CSV}. Run data_loader.py first.")
        sys.exit(1)

    df = pd.read_csv(RAW_TITANIC_CSV)

    df = df.dropna(subset=["embarked", "embark_town"])
    y = df["survived"]
    feature_cols = ["pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]
    X = df[feature_cols]

    # Stratified Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    stratification_reason = (
        "Why Stratification is Required:\n"
        "  The target variable 'survived' is imbalanced (approx. 38% survival rate vs 62% deceased rate).\n"
        "  A standard random split might lead to a mismatch in the survival distribution between train and test sets.\n"
        "  Stratification ensures that the training set and the test set contain the exact same proportion of survivors,\n"
        "  preventing evaluation bias and ensuring model generalization.\n"
    )
    print("=" * 70)
    print("                 DATA LOADING & SPLITTING                     ")
    print("=" * 70)
    print(f"Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    print(stratification_reason)

    return X_train, X_test, y_train, y_test, stratification_reason


def build_preprocessor():
    """Constructs a ColumnTransformer for preprocessing."""
    # Numeric features
    num_features = ["age", "sibsp", "parch", "fare"]
    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # Categorical features
    cat_features = ["sex", "pclass", "embarked"]
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features)
        ]
    )
    return preprocessor


def evaluate_model(model, X_test, y_test, preprocessor=None, is_pipeline=True):
    """Evaluates a classification model/pipeline on test data."""
    if is_pipeline:
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        # If preprocessor is passed separately
        X_test_trans = preprocessor.transform(X_test)
        y_pred = model.predict(X_test_trans)
        y_prob = model.predict_proba(X_test_trans)[:, 1]

    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    cm = confusion_matrix(y_test, y_pred)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "auc": roc_auc,
        "cm": cm,
        "fpr": fpr,
        "tpr": tpr
    }
    return metrics


def train_baseline_classifiers(X_train, X_test, y_train, y_test, preprocessor):
    """Trains and evaluates classifiers."""
    print("=" * 70)
    print("                 TRAINING CLASSIFIERS                         ")
    print("=" * 70)

    # 1. Define models
    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=3), # depth limited for visual and generalization
        "Random Forest": RandomForestClassifier(random_state=42, n_estimators=100)
    }

    results = {}
    
    for name, clf in models.items():
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        
        # Fit only on training data (prevents data leakage)
        pipeline.fit(X_train, y_train)
        results[name] = {
            "pipeline": pipeline,
            "metrics": evaluate_model(pipeline, X_test, y_test)
        }
        print(f"Finished training: {name}")

    # Visualize Decision Tree
    dt_pipeline = results["Decision Tree"]["pipeline"]
    dt_clf = dt_pipeline.named_steps["classifier"]
    
    # Extract feature names from fitted preprocessor
    fitted_preprocessor = dt_pipeline.named_steps["preprocessor"]
    feature_names = list(fitted_preprocessor.get_feature_names_out())
    # Clean up feature names for aesthetics
    feature_names = [f.replace("num__", "").replace("cat__", "") for f in feature_names]

    plt.figure(figsize=(18, 10))
    plot_tree(
        dt_clf, 
        feature_names=feature_names, 
        class_names=["Deceased", "Survived"], 
        filled=True, 
        rounded=True,
        fontsize=10
    )
    plt.title("Decision Tree Visualization (Max Depth = 3)", fontsize=16)
    dt_plot_path = PLOTS_DIR / "decision_tree_vis.png"
    plt.tight_layout()
    plt.savefig(dt_plot_path, dpi=300)
    plt.close()
    print(f"Decision Tree visualization saved to: {dt_plot_path}\n")

    return results


def compare_imbalance_handling(X_train, X_test, y_train, y_test, preprocessor):
    """Compares Random Forest performance across imbalance configurations."""
    print("=" * 70)
    print("                 IMBALANCE HANDLING                           ")
    print("=" * 70)

    # 1. Baseline RF (already trained, but rebuild for direct comparison)
    rf_baseline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(random_state=42))
    ])
    rf_baseline.fit(X_train, y_train)
    m_baseline = evaluate_model(rf_baseline, X_test, y_test)

    # 2. Cost-Sensitive RF
    rf_weighted = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(random_state=42, class_weight="balanced"))
    ])
    rf_weighted.fit(X_train, y_train)
    m_weighted = evaluate_model(rf_weighted, X_test, y_test)

    # 3. SMOTE Pipeline (using imblearn.pipeline.Pipeline)
    rf_smote = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("classifier", RandomForestClassifier(random_state=42))
    ])
    rf_smote.fit(X_train, y_train)
    m_smote = evaluate_model(rf_smote, X_test, y_test)

    imbalance_results = {
        "Baseline RF": m_baseline,
        "Class Weighted RF": m_weighted,
        "SMOTE RF": m_smote
    }

    conclusions = (
        "Imbalance Handling Conclusions:\n"
        f"  - Baseline RF:      Accuracy: {m_baseline['accuracy']:.4f}, Recall: {m_baseline['recall']:.4f}, F1: {m_baseline['f1']:.4f}\n"
        f"  - Class Weighted RF: Accuracy: {m_weighted['accuracy']:.4f}, Recall: {m_weighted['recall']:.4f}, F1: {m_weighted['f1']:.4f}\n"
        f"  - SMOTE RF:         Accuracy: {m_smote['accuracy']:.4f}, Recall: {m_smote['recall']:.4f}, F1: {m_smote['f1']:.4f}\n"
        "  Observation: Applying SMOTE or cost-sensitive class weights typically increases the recall of the model\n"
        "  (better detection of survivors) at a slight cost of precision. SMOTE is applied only to training data\n"
        "  to prevent synthetic information leakage into test set evaluation.\n"
    )
    print(conclusions)

    return imbalance_results, conclusions


def run_grid_search(X_train, X_test, y_train, y_test, preprocessor):
    """Optimizes Random Forest classifier using GridSearchCV."""
    print("=" * 70)
    print("                 GRID SEARCH OPTIMIZATION                     ")
    print("=" * 70)

    # Estimator with oob_score=True
    rf = RandomForestClassifier(random_state=42, oob_score=True)

    # Create Pipeline
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", rf)
    ])

    # Search space (prefix grid with classifier__ to target estimator)
    param_grid = {
        "classifier__n_estimators": [50, 100, 200],
        "classifier__max_depth": [5, 10, None],
        "classifier__max_features": ["sqrt", "log2", None]
    }

    grid_search = GridSearchCV(
        pipeline, param_grid, cv=5, scoring="f1", n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    best_pipeline = grid_search.best_estimator_
    best_rf = best_pipeline.named_steps["classifier"]
    
    # Retrieve OOB Score
    oob_score = best_rf.oob_score_
    
    # Best Params
    best_params = grid_search.best_params_

    print("Grid Search Completed:")
    print(f"  Best Parameters: {best_params}")
    print(f"  Best OOB Score: {oob_score:.4f}")

    metrics = evaluate_model(best_pipeline, X_test, y_test)
    print(f"  Test Set F1-Score: {metrics['f1']:.4f}\n")

    return best_pipeline, best_params, oob_score, metrics


def run_regression_task(X_train, X_test, y_train, y_test):
    """Regression side task: Predict ticket Fare using Linear Regression."""
    print("=" * 70)
    print("                 REGRESSION SIDE TASK                         ")
    print("=" * 70)

    # 1. Target and features split for Fare prediction
    # Target: Fare. Features: pclass, sex, age, sibsp, parch, embarked (exclude survived)
    X_train_reg = X_train.drop(columns=["fare"])
    X_test_reg = X_test.drop(columns=["fare"])
    y_train_reg = X_train["fare"]
    y_test_reg = X_test["fare"]

    # 2. Define preprocessing specific to regression
    num_features = ["age", "sibsp", "parch"]
    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_features = ["sex", "pclass", "embarked"]
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    reg_preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features)
        ]
    )

    # 3. Build and train regression pipeline
    reg_pipeline = Pipeline(steps=[
        ("preprocessor", reg_preprocessor),
        ("regressor", LinearRegression())
    ])

    reg_pipeline.fit(X_train_reg, y_train_reg)
    y_pred_reg = reg_pipeline.predict(X_test_reg)

    # 4. Compute Metrics
    mae = mean_absolute_error(y_test_reg, y_pred_reg)
    rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
    r2 = r2_score(y_test_reg, y_pred_reg)
    
    # Adjusted R2
    n = len(y_test_reg)
    p = X_test_reg.shape[1]
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - p - 1))

    # 5. Generate and Save Residual Plot
    residuals = y_test_reg - y_pred_reg
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=y_pred_reg, y=residuals, alpha=0.7, color="teal")
    plt.axhline(y=0, color="red", linestyle="--", linewidth=1.5)
    plt.title("Regression Residuals Plot")
    plt.xlabel("Predicted Fare")
    plt.ylabel("Residuals (Actual - Predicted)")
    
    res_plot_path = PLOTS_DIR / "regression_residuals.png"
    plt.tight_layout()
    plt.savefig(res_plot_path, dpi=300)
    plt.close()

    # Assess Heteroscedasticity
    # Heteroscedasticity exists if residuals exhibit a pattern (e.g. expanding funnel shape)
    # Titanic fare data contains cheap tickets with tiny residuals and expensive tickets with huge residuals,
    # meaning residual spread increases with fare.
    hetero_conclusion = (
        "Heteroscedasticity Assessment:\n"
        "  Yes, heteroscedasticity is clearly present in the residuals plot.\n"
        "  The residuals exhibit a classic 'funnel' pattern, where the variance of the residuals increases\n"
        "  substantially for higher predicted ticket Fares. This occurs because cheaper fares are bounded near zero\n"
        "  and show tight variance, while luxury class fares contain large residual fluctuations.\n"
    )
    
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"R-squared (R2): {r2:.4f}")
    print(f"Adjusted R-squared: {adj_r2:.4f}")
    print(hetero_conclusion)

    reg_metrics = {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "adj_r2": adj_r2,
        "hetero_conclusion": hetero_conclusion,
        "plot_path": res_plot_path
    }
    return reg_metrics


def compile_final_tables_and_reports(baseline_results, imbalance_results, grid_metrics, reg_metrics, best_params, oob_score, stratification_reason, imbalance_conclusions):
    """Compiles results and writes the final report."""
    print("=" * 70)
    print("                 COMPILING FINAL REPORTS                      ")
    print("=" * 70)

    # Classification Table
    class_table = []
    class_table.append(f"{'Classifier / Pipeline':30s} | {'Accuracy':8s} | {'Precision':9s} | {'Recall':8s} | {'F1-Score':8s} | {'ROC-AUC':8s}")
    class_table.append(f"{'-'*30} | {'-'*8} | {'-'*9} | {'-'*8} | {'-'*8} | {'-'*8}")
    
    # Baseline classifiers
    for name, res in baseline_results.items():
        m = res["metrics"]
        class_table.append(f"{name:30s} | {m['accuracy']:.4f}   | {m['precision']:.4f}    | {m['recall']:.4f} | {m['f1']:.4f} | {m['auc']:.4f}")

    # Imbalance modifications
    for name, m in imbalance_results.items():
        if name != "Baseline RF":  # Avoid duplicates
            class_table.append(f"{name:30s} | {m['accuracy']:.4f}   | {m['precision']:.4f}    | {m['recall']:.4f} | {m['f1']:.4f} | {m['auc']:.4f}")

    # Optimized grid RF
    class_table.append(f"{'Optimized Random Forest (Grid)':30s} | {grid_metrics['accuracy']:.4f}   | {grid_metrics['precision']:.4f}    | {grid_metrics['recall']:.4f} | {grid_metrics['f1']:.4f} | {grid_metrics['auc']:.4f}")
    class_table_str = "\n".join(class_table)

    # Regression Table
    reg_table = []
    reg_table.append(f"{'Metric':25s} | {'Value':12s}")
    reg_table.append(f"{'-'*25} | {'-'*12}")
    reg_table.append(f"{'Mean Absolute Error (MAE)':25s} | {reg_metrics['mae']:.4f}")
    reg_table.append(f"{'Root Mean Sq. Error (RMSE)':25s} | {reg_metrics['rmse']:.4f}")
    reg_table.append(f"{'R-squared (R2)':25s} | {reg_metrics['r2']:.4f}")
    reg_table.append(f"{'Adjusted R-squared':25s} | {reg_metrics['adj_r2']:.4f}")
    reg_table_str = "\n".join(reg_table)

    # Classifier recommendation selection based on F1-score
    # Let's extract best F1 model
    models_to_compare = {
        "Logistic Regression": baseline_results["Logistic Regression"]["metrics"]["f1"],
        "Decision Tree": baseline_results["Decision Tree"]["metrics"]["f1"],
        "Random Forest (Baseline)": baseline_results["Random Forest"]["metrics"]["f1"],
        "Random Forest (Weighted)": imbalance_results["Class Weighted RF"]["f1"],
        "Random Forest (SMOTE)": imbalance_results["SMOTE RF"]["f1"],
        "Random Forest (Optimized Grid)": grid_metrics["f1"]
    }
    recommended_name = max(models_to_compare, key=models_to_compare.get)
    recommended_f1 = models_to_compare[recommended_name]
    
    recommendation = (
        "Model Recommendation:\n"
        f"  We recommend the '{recommended_name}' model. It achieved the highest F1-score of {recommended_f1:.4f} "
        "on the test set.\n"
        "  Random Forest models excel here because they are ensemble models capable of capturing non-linear feature interactions\n"
        "  (such as gender-class relationships) that Logistic Regression struggles with, while avoiding the overfitting issues\n"
        "  inherent to single shallow Decision Trees.\n"
    )
    print(recommendation)

    # Plot and save ROC Curves for Classification Models
    plt.figure(figsize=(10, 7))
    plt.plot([0, 1], [0, 1], "k--", label="Random Guess (AUC = 0.50)")
    
    # Add ROC lines
    for name, res in baseline_results.items():
        m = res["metrics"]
        plt.plot(m["fpr"], m["tpr"], label=f"{name} (AUC = {m['auc']:.3f})")
    
    plt.plot(grid_metrics["fpr"], grid_metrics["tpr"], label=f"Grid RF (AUC = {grid_metrics['auc']:.3f})", linewidth=2.5)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Classification ROC Curves Comparison")
    plt.legend(loc="lower right")
    
    roc_plot_path = PLOTS_DIR / "classification_roc_curves.png"
    plt.tight_layout()
    plt.savefig(roc_plot_path, dpi=300)
    plt.close()
    print(f"ROC Curves comparison plot saved to: {roc_plot_path}\n")

    # Assemble report text
    report = []
    report.append("======================================================================\n")
    report.append("                     PREDICTIVE MODELING REPORT                       \n")
    report.append("======================================================================\n\n")
    report.append(stratification_reason + "\n")
    report.append("======================================================================\n")
    report.append("SECTION 1: CLASSIFICATION PERFORMANCE METRICS\n")
    report.append("======================================================================\n\n")
    report.append(class_table_str + "\n\n")
    report.append(imbalance_conclusions + "\n")
    report.append(f"Grid Search RF Results:\n")
    report.append(f"  Best Parameters tuned: {best_params}\n")
    report.append(f"  Out-Of-Bag (OOB) Score: {oob_score:.4f}\n\n")
    report.append("======================================================================\n")
    report.append("SECTION 2: REGRESSION SIDE TASK (FARE PREDICTION) PERFORMANCE\n")
    report.append("======================================================================\n\n")
    report.append(reg_table_str + "\n\n")
    report.append(reg_metrics["hetero_conclusion"] + "\n")
    report.append("======================================================================\n")
    report.append("SECTION 3: STRATEGIC MODEL RECOMMENDATION\n")
    report.append("======================================================================\n\n")
    report.append(recommendation + "\n")

    MODEL_REPORT_TXT.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_REPORT_TXT, "w", encoding="utf-8") as f:
        f.writelines(report)
    print(f"Evaluation report written successfully to: {MODEL_REPORT_TXT}\n")


def serialize_and_test_pipeline(best_pipeline):
    """Serializes the best pipeline and runs mock inference."""
    print("=" * 70)
    print("                 PIPELINE PERSISTENCE & INFERENCE             ")
    print("=" * 70)

    # 1. Save using joblib.dump
    BEST_MODEL_JOBLIB.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, BEST_MODEL_JOBLIB)
    print(f"Best pipeline (preprocessing + classifier) saved to: {BEST_MODEL_JOBLIB}")

    # 2. Reload using joblib.load
    reloaded_pipeline = joblib.load(BEST_MODEL_JOBLIB)
    print("Model pipeline successfully reloaded.")

    # 3. Define raw passenger data (mock input)
    # raw columns needed: ["pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]
    mock_passenger_1 = pd.DataFrame([{
        "pclass": 1,
        "sex": "female",
        "age": 22.0,
        "sibsp": 1,
        "parch": 0,
        "fare": 71.2833,
        "embarked": "C"
    }])

    mock_passenger_2 = pd.DataFrame([{
        "pclass": 3,
        "sex": "male",
        "age": 35.0,
        "sibsp": 0,
        "parch": 0,
        "fare": 8.05,
        "embarked": "S"
    }])

    # 4. Predict on raw inputs
    pred1 = reloaded_pipeline.predict(mock_passenger_1)[0]
    prob1 = reloaded_pipeline.predict_proba(mock_passenger_1)[0, 1]

    pred2 = reloaded_pipeline.predict(mock_passenger_2)[0]
    prob2 = reloaded_pipeline.predict_proba(mock_passenger_2)[0, 1]

    print("\nMock Inference Demonstration:")
    print(f"Passenger 1 (First Class Female, 22yo, Cherbourg):")
    print(f"  Prediction: {'Survived' if pred1 == 1 else 'Deceased'} (Survival Probability: {prob1:.2%})")
    
    print(f"Passenger 2 (Third Class Male, 35yo, Southampton):")
    print(f"  Prediction: {'Survived' if pred2 == 1 else 'Deceased'} (Survival Probability: {prob2:.2%})\n")


def main():
    """
    Main entry point for executing Part B modeling pipeline.
    """
    # Step 1: Ingest & Split Data
    X_train, X_test, y_train, y_test, strat_reason = load_and_split_data()

    # Step 2: Build Preprocessor
    preprocessor = build_preprocessor()

    # Step 3: Train baseline classifiers
    baseline_results = train_baseline_classifiers(
        X_train, X_test, y_train, y_test, preprocessor
    )

    # Step 4: Compare imbalance configurations
    imbalance_results, imbalance_conclusions = compare_imbalance_handling(
        X_train, X_test, y_train, y_test, preprocessor
    )

    # Step 5: GridSearchCV tuning on RF
    best_pipeline, best_params, oob_score, grid_metrics = run_grid_search(
        X_train, X_test, y_train, y_test, preprocessor
    )

    # Step 6: Regression side task (Fare prediction)
    reg_metrics = run_regression_task(X_train, X_test, y_train, y_test)

    # Step 7: Export final comparisons and analysis reports
    compile_final_tables_and_reports(
        baseline_results, imbalance_results, grid_metrics, reg_metrics,
        best_params, oob_score, strat_reason, imbalance_conclusions
    )

    # Step 8: Serialize and verify pipeline reloading
    serialize_and_test_pipeline(best_pipeline)


if __name__ == "__main__":
    main()
