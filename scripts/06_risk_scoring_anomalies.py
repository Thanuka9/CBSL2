from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

# ============================================================
# Exercise 02 - Step 06
# Risk Scoring, Risk Drivers and Anomaly Detection
#
# This script creates:
# - Composite sector risk score
# - Loan-level anomaly watchlist
# - Random Forest model to identify NPL risk drivers
# - Risk visualisations
# ============================================================

BASE_DIR = Path.cwd()

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
FIGURE_DIR = BASE_DIR / "figures"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = PROCESSED_DIR / "04_loan_macro_panel.csv"
SECTOR_KPI_PATH = OUTPUT_DIR / "05_sector_kpi.csv"

print(f"Reading panel data: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

print(f"Reading sector KPI data: {SECTOR_KPI_PATH}")
sector = pd.read_csv(SECTOR_KPI_PATH)

print("\nData loaded.")
print(f"Panel rows: {df.shape[0]:,}")
print(f"Panel columns: {df.shape[1]:,}")

# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------

def minmax(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())

# ------------------------------------------------------------
# 1. Composite sector risk score
# ------------------------------------------------------------
# Score logic:
# - NPL ratio by amount: strongest weight
# - Collateral risk: unsecured / partially secured exposure risk
# - Rating weakness: average rating rank
# - Portfolio concentration: large sectors create systemic exposure
#
# This is a prioritisation index, not a regulatory capital model.
# ------------------------------------------------------------

sector["score_npl"] = minmax(sector["npl_ratio_amount_pct"])
sector["score_collateral_risk"] = minmax(sector["average_collateral_risk_score"])
sector["score_rating_weakness"] = minmax(sector["average_rating_rank"])
sector["score_concentration"] = minmax(sector["portfolio_share_pct"])

sector["composite_risk_score"] = (
    0.45 * sector["score_npl"]
    + 0.25 * sector["score_collateral_risk"]
    + 0.20 * sector["score_rating_weakness"]
    + 0.10 * sector["score_concentration"]
) * 100

sector_risk = sector.sort_values("composite_risk_score", ascending=False)

sector_risk_path = OUTPUT_DIR / "06_sector_composite_risk_score.csv"
sector_risk.to_csv(sector_risk_path, index=False)

# ------------------------------------------------------------
# 2. Loan-level anomaly detection
# ------------------------------------------------------------
# A loan is more interesting for review if it is:
# - unusually large within its own sector
# - non-performing
# - unsecured or partially secured
# - weakly rated
# - in a high-risk sector
# ------------------------------------------------------------

df = df.merge(
    sector_risk[["sector", "composite_risk_score"]],
    on="sector",
    how="left"
)

df["sector_amount_mean"] = df.groupby("sector")["amount_outstanding_lkr"].transform("mean")
df["sector_amount_std"] = df.groupby("sector")["amount_outstanding_lkr"].transform("std")

df["amount_zscore_within_sector"] = (
    (df["amount_outstanding_lkr"] - df["sector_amount_mean"])
    / df["sector_amount_std"]
)

df["amount_zscore_within_sector"] = df["amount_zscore_within_sector"].replace(
    [np.inf, -np.inf],
    0
).fillna(0)

df["positive_amount_zscore"] = df["amount_zscore_within_sector"].clip(lower=0)

df["sector_risk_scaled"] = df["composite_risk_score"] / 100

df["loan_anomaly_score"] = (
    df["positive_amount_zscore"] * 1.5
    + df["is_npl"] * 2.0
    + df["has_unsecured_risk"] * 1.0
    + df["weak_rating_flag"] * 1.0
    + df["large_exposure_flag"] * 1.5
    + df["sector_risk_scaled"] * 1.0
)

anomaly_cols = [
    "loan_id",
    "loan_date",
    "year",
    "sector",
    "loan_type",
    "collateral",
    "initial_rating",
    "performance_status",
    "amount_outstanding_lkr",
    "amount_outstanding_mn_lkr",
    "amount_zscore_within_sector",
    "is_npl",
    "has_unsecured_risk",
    "weak_rating_flag",
    "large_exposure_flag",
    "composite_risk_score",
    "loan_anomaly_score",
    "sri_lanka_gdp_growth_pct",
    "sri_lanka_inflation_pct",
    "policy_rate_pct",
    "domestic_macro_stress_score"
]

anomalies = df.sort_values("loan_anomaly_score", ascending=False)[anomaly_cols]

anomaly_path = OUTPUT_DIR / "06_top_250_anomaly_watchlist.csv"
anomalies.head(250).to_csv(anomaly_path, index=False)

full_anomaly_path = OUTPUT_DIR / "06_all_loans_with_anomaly_score.csv"
df.to_csv(full_anomaly_path, index=False)

# ------------------------------------------------------------
# 3. Risk driver model
# ------------------------------------------------------------
# Classification model:
# target = is_npl
#
# Objective:
# Identify variables associated with NPL status.
#
# This is an explanatory / screening model, not a production PD model.
# ------------------------------------------------------------

features = [
    "sector",
    "loan_type",
    "collateral",
    "initial_rating",
    "amount_outstanding_mn_lkr",
    "collateral_risk_score",
    "rating_rank",
    "large_exposure_flag",
    "sri_lanka_gdp_growth_pct",
    "sri_lanka_inflation_pct",
    "sri_lanka_unemployment_pct",
    "avg_exchange_rate_lkr_usd",
    "policy_rate_pct",
    "private_sector_credit_growth_pct",
    "domestic_macro_stress_score",
    "global_macro_stress_score"
]

target = "is_npl"

model_df = df[features + [target]].dropna().copy()

X = model_df[features]
y = model_df[target]

categorical_features = [
    "sector",
    "loan_type",
    "collateral",
    "initial_rating"
]

numeric_features = [
    col for col in features if col not in categorical_features
]

preprocess = ColumnTransformer(
    transformers=[
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numeric", "passthrough", numeric_features)
    ]
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=50,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(
    steps=[
        ("preprocess", preprocess),
        ("model", model)
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("\nTraining Random Forest risk-driver model...")
pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)
report = classification_report(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

# ------------------------------------------------------------
# Feature importance
# ------------------------------------------------------------

encoded_cat_names = list(
    pipeline
    .named_steps["preprocess"]
    .named_transformers_["categorical"]
    .get_feature_names_out(categorical_features)
)

feature_names = encoded_cat_names + numeric_features

importances = pipeline.named_steps["model"].feature_importances_

feature_importance = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
}).sort_values("importance", ascending=False)

feature_importance_path = OUTPUT_DIR / "06_risk_driver_feature_importance.csv"
feature_importance.to_csv(feature_importance_path, index=False)

model_metrics_path = OUTPUT_DIR / "06_model_metrics.txt"

with open(model_metrics_path, "w", encoding="utf-8") as f:
    f.write("Exercise 02 - Step 06 Risk Driver Model Metrics\n")
    f.write("=" * 80 + "\n\n")
    f.write("Model: RandomForestClassifier\n")
    f.write("Target: is_npl\n\n")
    f.write(f"ROC AUC: {auc:.4f}\n\n")
    f.write("Classification Report:\n")
    f.write(report)
    f.write("\n\nConfusion Matrix:\n")
    f.write(str(cm))
    f.write("\n\nInterpretation Note:\n")
    f.write(
        "This model is used to identify risk drivers associated with NPL status. "
        "It should be interpreted as an explanatory screening model rather than "
        "a production probability-of-default model because borrower-level repayment "
        "history, income, days-past-due, collateral valuation, and recovery data are "
        "not available in the supplied dataset.\n"
    )

# ------------------------------------------------------------
# 4. Visualisations
# ------------------------------------------------------------

# Composite risk score by sector
plot_sector = sector_risk.sort_values("composite_risk_score", ascending=True)

plt.figure(figsize=(11, 6))
plt.barh(plot_sector["sector"], plot_sector["composite_risk_score"])
plt.title("Composite Sector Risk Score")
plt.xlabel("Risk Score")
plt.ylabel("Sector")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "06_sector_composite_risk_score.png", dpi=150)
plt.close()

# Feature importance top 20
plot_importance = feature_importance.head(20).sort_values("importance", ascending=True)

plt.figure(figsize=(11, 7))
plt.barh(plot_importance["feature"], plot_importance["importance"])
plt.title("Top Risk Driver Feature Importance")
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "06_risk_driver_feature_importance.png", dpi=150)
plt.close()

# Anomaly score distribution
plt.figure(figsize=(10, 5))
plt.hist(df["loan_anomaly_score"], bins=50)
plt.title("Loan Anomaly Score Distribution")
plt.xlabel("Anomaly Score")
plt.ylabel("Loan Count")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "06_anomaly_score_distribution.png", dpi=150)
plt.close()

# ------------------------------------------------------------
# 5. Written summary
# ------------------------------------------------------------

top_risk_sector = sector_risk.iloc[0]
top_anomaly = anomalies.iloc[0]
top_driver = feature_importance.iloc[0]

summary_path = LOG_DIR / "06_risk_scoring_anomalies_summary.txt"

with open(summary_path, "w", encoding="utf-8") as f:
    f.write("Exercise 02 - Step 06 Risk Scoring and Anomaly Summary\n")
    f.write("=" * 80 + "\n\n")

    f.write("Composite Sector Risk Score\n")
    f.write("-" * 80 + "\n")
    f.write(
        "The composite risk score combines NPL ratio, collateral risk, "
        "rating weakness and portfolio concentration. It is used to prioritise "
        "sectors for supervisory or management review.\n\n"
    )
    f.write(
        f"Highest risk sector: {top_risk_sector['sector']} "
        f"with score {top_risk_sector['composite_risk_score']:.2f}/100.\n\n"
    )

    f.write("Loan-Level Anomaly Detection\n")
    f.write("-" * 80 + "\n")
    f.write(
        "The anomaly score combines sector-relative loan size, NPL status, "
        "collateral risk, weak rating, large exposure flag and sector risk. "
        "The top 250 loans are saved as a watchlist for further review.\n\n"
    )
    f.write(
        f"Top anomaly loan: {top_anomaly['loan_id']}, "
        f"sector: {top_anomaly['sector']}, "
        f"amount: Rs. {top_anomaly['amount_outstanding_mn_lkr']:.2f} Mn, "
        f"score: {top_anomaly['loan_anomaly_score']:.2f}.\n\n"
    )

    f.write("Risk Driver Model\n")
    f.write("-" * 80 + "\n")
    f.write(f"Random Forest ROC AUC: {auc:.4f}\n")
    f.write(f"Top model feature: {top_driver['feature']}.\n\n")
    f.write(
        "The model is used for interpretability and driver identification. "
        "It should not be treated as a regulatory PD model without more complete "
        "borrower-level performance data.\n\n"
    )

    f.write("Generated Outputs\n")
    f.write("-" * 80 + "\n")
    f.write("- outputs/06_sector_composite_risk_score.csv\n")
    f.write("- outputs/06_top_250_anomaly_watchlist.csv\n")
    f.write("- outputs/06_all_loans_with_anomaly_score.csv\n")
    f.write("- outputs/06_risk_driver_feature_importance.csv\n")
    f.write("- outputs/06_model_metrics.txt\n")
    f.write("- figures/06_sector_composite_risk_score.png\n")
    f.write("- figures/06_risk_driver_feature_importance.png\n")
    f.write("- figures/06_anomaly_score_distribution.png\n")

print("\nStep 06 risk scoring and anomaly detection completed successfully.")
print(f"Sector risk score saved to: {sector_risk_path}")
print(f"Top anomaly watchlist saved to: {anomaly_path}")
print(f"Feature importance saved to: {feature_importance_path}")
print(f"Model metrics saved to: {model_metrics_path}")
print(f"Summary saved to: {summary_path}")

print("\nTop sectors by composite risk score:")
print(sector_risk[["sector", "composite_risk_score", "npl_ratio_amount_pct", "portfolio_share_pct"]].head(10))

print("\nModel ROC AUC:")
print(auc)

print("\nTop 10 risk drivers:")
print(feature_importance.head(10))