from pathlib import Path
import pandas as pd
import numpy as np
import re

# ============================================================
# Exercise 02 - Step 02
# Clean and transform ABC Bank PLC loan portfolio data
#
# This script:
# 1. Reads the raw Excel file from data/raw
# 2. Standardises column names
# 3. Cleans sector, collateral, rating and performance labels
# 4. Checks duplicates, missing values and invalid amounts
# 5. Creates analysis-ready variables
# 6. Saves cleaned dataset, cleaning log and summary
# ============================================================

BASE_DIR = Path.cwd()
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Find raw Excel file from setup config
# ------------------------------------------------------------

config_file = RAW_DIR / "raw_file_name.txt"

if config_file.exists():
    raw_file_name = config_file.read_text(encoding="utf-8").strip()
    RAW_FILE = RAW_DIR / raw_file_name
else:
    excel_files = list(RAW_DIR.glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError("No Excel file found in data/raw.")
    RAW_FILE = excel_files[0]

print(f"Reading raw Excel file: {RAW_FILE}")

df = pd.read_excel(RAW_FILE)

print("\nRaw dataset loaded.")
print(f"Raw rows: {df.shape[0]:,}")
print(f"Raw columns: {df.shape[1]:,}")

# ------------------------------------------------------------
# Keep original columns for documentation
# ------------------------------------------------------------

original_columns = list(df.columns)

# ------------------------------------------------------------
# Standardise column names
# ------------------------------------------------------------

def clean_column_name(col):
    col = str(col).strip().lower()
    col = col.replace("/", " ")
    col = col.replace("(", " ")
    col = col.replace(")", " ")
    col = col.replace(".", " ")
    col = re.sub(r"[^a-z0-9]+", "_", col)
    col = col.strip("_")
    return col

df.columns = [clean_column_name(col) for col in df.columns]

print("\nCleaned column names:")
for col in df.columns:
    print(f"- {col}")

# ------------------------------------------------------------
# Rename expected columns into analytical names
# ------------------------------------------------------------

rename_map = {
    "loan_id": "loan_id",
    "loan_originating_date": "loan_date",
    "sector": "sector",
    "loan_type": "loan_type",
    "collateral": "collateral",
    "initial_rating": "initial_rating",
    "performing_non_performing": "performance_status",
    "amount_outstanding_rs": "amount_outstanding_lkr"
}

df = df.rename(columns=rename_map)

required_columns = [
    "loan_id",
    "loan_date",
    "sector",
    "loan_type",
    "collateral",
    "initial_rating",
    "performance_status",
    "amount_outstanding_lkr"
]

missing_required = [col for col in required_columns if col not in df.columns]

if missing_required:
    raise ValueError(f"Missing required columns after cleaning: {missing_required}")

# ------------------------------------------------------------
# Basic field cleaning
# ------------------------------------------------------------

df["loan_id"] = df["loan_id"].astype(str).str.strip()

df["loan_date"] = pd.to_datetime(df["loan_date"], errors="coerce")

df["sector"] = df["sector"].astype(str).str.strip()

df["loan_type"] = (
    df["loan_type"]
    .astype(str)
    .str.strip()
    .str.replace("_", " ", regex=False)
    .str.title()
)

df["initial_rating"] = df["initial_rating"].astype(str).str.strip().str.upper()

df["performance_status"] = df["performance_status"].astype(str).str.strip()

df["amount_outstanding_lkr"] = pd.to_numeric(
    df["amount_outstanding_lkr"],
    errors="coerce"
)

# ------------------------------------------------------------
# Standardise sector labels
# Raw profile showed spelling issue: Telecommumication
# ------------------------------------------------------------

df["sector"] = df["sector"].replace({
    "Telecommumication": "Telecommunication",
    "telecommumication": "Telecommunication",
    "Telecommunication": "Telecommunication"
})

df["sector"] = (
    df["sector"]
    .astype(str)
    .str.strip()
    .str.replace("_", " ", regex=False)
    .str.title()
)

# Fix title-case for common sector names
df["sector"] = df["sector"].replace({
    "Financial Sector": "Financial Sector",
    "Infrastructure Development": "Infrastructure Development",
    "Telecommunication": "Telecommunication"
})

# ------------------------------------------------------------
# Standardise collateral labels
# Raw values include secured, unsecured, partially_secured
# ------------------------------------------------------------

df["collateral"] = (
    df["collateral"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace("_", " ", regex=False)
    .str.title()
)

df["collateral"] = df["collateral"].replace({
    "Secured": "Secured",
    "Unsecured": "Unsecured",
    "Partially Secured": "Partially Secured"
})

# ------------------------------------------------------------
# Standardise performance status
# ------------------------------------------------------------

df["performance_status"] = df["performance_status"].replace({
    "Non Performing": "Non-Performing",
    "Non-performing": "Non-Performing",
    "NonPerforming": "Non-Performing",
    "Performing": "Performing"
})

# ------------------------------------------------------------
# Remove invalid / duplicate records
# ------------------------------------------------------------

before_rows = len(df)

duplicate_loan_ids = df["loan_id"].duplicated().sum()
missing_date = df["loan_date"].isna().sum()
missing_amount = df["amount_outstanding_lkr"].isna().sum()
negative_amount = (df["amount_outstanding_lkr"] < 0).sum()

df = df.drop_duplicates(subset=["loan_id"], keep="first")
df = df.dropna(subset=["loan_date", "amount_outstanding_lkr"])
df = df[df["amount_outstanding_lkr"] >= 0].copy()

after_rows = len(df)

# ------------------------------------------------------------
# Feature engineering
# ------------------------------------------------------------

df["year"] = df["loan_date"].dt.year
df["month"] = df["loan_date"].dt.to_period("M").astype(str)
df["quarter"] = df["loan_date"].dt.to_period("Q").astype(str)

df["amount_outstanding_mn_lkr"] = df["amount_outstanding_lkr"] / 1_000_000

# Non-performing loan flag
df["is_npl"] = np.where(df["performance_status"] == "Non-Performing", 1, 0)

# Exact unsecured flag
df["is_fully_unsecured"] = np.where(df["collateral"] == "Unsecured", 1, 0)

# Broader collateral risk flag:
# Partially secured loans still carry some unsecured exposure risk.
df["has_unsecured_risk"] = np.where(
    df["collateral"].isin(["Unsecured", "Partially Secured"]),
    1,
    0
)

# Collateral risk score:
# 0 = secured, 0.5 = partially secured, 1 = unsecured
collateral_risk_map = {
    "Secured": 0.0,
    "Partially Secured": 0.5,
    "Unsecured": 1.0
}

df["collateral_risk_score"] = df["collateral"].map(collateral_risk_map)

# Rating rank:
# lower number = stronger credit rating
# higher number = weaker credit rating
rating_rank_map = {
    "AAA": 1,
    "AA": 2,
    "A": 3,
    "BBB": 4,
    "BB": 5,
    "B": 6,
    "CCC": 7,
    "CC": 8,
    "C": 9,
    "D": 10
}

df["rating_rank"] = df["initial_rating"].map(rating_rank_map)

df["weak_rating_flag"] = np.where(df["rating_rank"] >= 5, 1, 0)

# Large exposure flag:
# loans above the 95th percentile are marked for monitoring.
large_exposure_threshold = df["amount_outstanding_lkr"].quantile(0.95)
df["large_exposure_flag"] = np.where(
    df["amount_outstanding_lkr"] >= large_exposure_threshold,
    1,
    0
)

# ------------------------------------------------------------
# Validation checks
# ------------------------------------------------------------

assert df["loan_id"].is_unique, "Loan IDs are not unique after cleaning."
assert df["amount_outstanding_lkr"].min() >= 0, "Negative outstanding amount remains."
assert df["is_npl"].isin([0, 1]).all(), "Invalid NPL flag found."
assert df["is_fully_unsecured"].isin([0, 1]).all(), "Invalid unsecured flag found."
assert df["has_unsecured_risk"].isin([0, 1]).all(), "Invalid unsecured risk flag found."

if df["rating_rank"].isna().sum() > 0:
    print("\nWarning: Some ratings were not mapped to rating_rank.")
    print(df.loc[df["rating_rank"].isna(), "initial_rating"].value_counts())

if df["collateral_risk_score"].isna().sum() > 0:
    print("\nWarning: Some collateral values were not mapped to collateral_risk_score.")
    print(df.loc[df["collateral_risk_score"].isna(), "collateral"].value_counts())

# ------------------------------------------------------------
# Save cleaned dataset
# ------------------------------------------------------------

clean_path = PROCESSED_DIR / "02_clean_loan_portfolio.csv"
df.to_csv(clean_path, index=False)

# ------------------------------------------------------------
# Save cleaning log
# ------------------------------------------------------------

log_path = LOG_DIR / "02_cleaning_log.txt"

with open(log_path, "w", encoding="utf-8") as f:
    f.write("Exercise 02 - Step 02 Cleaning Log\n")
    f.write("=" * 70 + "\n\n")

    f.write("Original Columns:\n")
    for col in original_columns:
        f.write(f"- {col}\n")

    f.write("\nCleaned Columns:\n")
    for col in df.columns:
        f.write(f"- {col}\n")

    f.write("\nCleaning Summary:\n")
    f.write(f"Rows before cleaning: {before_rows:,}\n")
    f.write(f"Rows after cleaning: {after_rows:,}\n")
    f.write(f"Rows removed: {before_rows - after_rows:,}\n")
    f.write(f"Duplicate loan IDs found before cleaning: {duplicate_loan_ids:,}\n")
    f.write(f"Missing dates before cleaning: {missing_date:,}\n")
    f.write(f"Missing amount values before cleaning: {missing_amount:,}\n")
    f.write(f"Negative amount values before cleaning: {negative_amount:,}\n")
    f.write(f"Large exposure threshold, 95th percentile LKR: {large_exposure_threshold:,.2f}\n")

    f.write("\nUnique Sectors:\n")
    f.write(str(sorted(df["sector"].dropna().unique())))

    f.write("\n\nUnique Loan Types:\n")
    f.write(str(sorted(df["loan_type"].dropna().unique())))

    f.write("\n\nUnique Collateral Types:\n")
    f.write(str(sorted(df["collateral"].dropna().unique())))

    f.write("\n\nUnique Ratings:\n")
    f.write(str(sorted(df["initial_rating"].dropna().unique())))

    f.write("\n\nPerformance Status Values:\n")
    f.write(str(df["performance_status"].value_counts()))

    f.write("\n\nCollateral Risk Score Mapping:\n")
    f.write("Secured = 0.0\n")
    f.write("Partially Secured = 0.5\n")
    f.write("Unsecured = 1.0\n")

    f.write("\nRating Rank Mapping:\n")
    for rating, rank in rating_rank_map.items():
        f.write(f"{rating} = {rank}\n")

# ------------------------------------------------------------
# Save cleaning summary
# ------------------------------------------------------------

summary = {
    "rows_before_cleaning": before_rows,
    "rows_after_cleaning": after_rows,
    "rows_removed": before_rows - after_rows,
    "duplicate_loan_ids_before_cleaning": duplicate_loan_ids,
    "missing_dates_before_cleaning": missing_date,
    "missing_amount_before_cleaning": missing_amount,
    "negative_amount_before_cleaning": negative_amount,
    "total_outstanding_lkr": df["amount_outstanding_lkr"].sum(),
    "total_outstanding_mn_lkr": df["amount_outstanding_mn_lkr"].sum(),
    "average_loan_size_mn_lkr": df["amount_outstanding_mn_lkr"].mean(),
    "median_loan_size_mn_lkr": df["amount_outstanding_mn_lkr"].median(),
    "max_loan_size_mn_lkr": df["amount_outstanding_mn_lkr"].max(),
    "large_exposure_threshold_mn_lkr": large_exposure_threshold / 1_000_000,
    "npl_ratio_count_pct": df["is_npl"].mean() * 100,
    "npl_ratio_amount_pct": (
        df.loc[df["is_npl"] == 1, "amount_outstanding_lkr"].sum()
        / df["amount_outstanding_lkr"].sum()
        * 100
    ),
    "fully_unsecured_share_count_pct": df["is_fully_unsecured"].mean() * 100,
    "fully_unsecured_share_amount_pct": (
        df.loc[df["is_fully_unsecured"] == 1, "amount_outstanding_lkr"].sum()
        / df["amount_outstanding_lkr"].sum()
        * 100
    ),
    "unsecured_or_partially_secured_share_count_pct": df["has_unsecured_risk"].mean() * 100,
    "unsecured_or_partially_secured_share_amount_pct": (
        df.loc[df["has_unsecured_risk"] == 1, "amount_outstanding_lkr"].sum()
        / df["amount_outstanding_lkr"].sum()
        * 100
    ),
    "average_rating_rank": df["rating_rank"].mean(),
    "weak_rating_share_count_pct": df["weak_rating_flag"].mean() * 100
}

summary_path = OUTPUT_DIR / "02_cleaning_summary.csv"
pd.DataFrame([summary]).to_csv(summary_path, index=False)

# ------------------------------------------------------------
# Save cleaned category distributions for quick review
# ------------------------------------------------------------

df["sector"].value_counts().to_csv(
    OUTPUT_DIR / "02_clean_sector_distribution.csv",
    header=["loan_count"]
)

df["loan_type"].value_counts().to_csv(
    OUTPUT_DIR / "02_clean_loan_type_distribution.csv",
    header=["loan_count"]
)

df["collateral"].value_counts().to_csv(
    OUTPUT_DIR / "02_clean_collateral_distribution.csv",
    header=["loan_count"]
)

df["initial_rating"].value_counts().to_csv(
    OUTPUT_DIR / "02_clean_rating_distribution.csv",
    header=["loan_count"]
)

df["performance_status"].value_counts().to_csv(
    OUTPUT_DIR / "02_clean_performance_distribution.csv",
    header=["loan_count"]
)

print("\nStep 02 cleaning completed successfully.")
print(f"Rows before cleaning: {before_rows:,}")
print(f"Rows after cleaning: {after_rows:,}")
print(f"Rows removed: {before_rows - after_rows:,}")
print(f"Cleaned data saved to: {clean_path}")
print(f"Cleaning log saved to: {log_path}")
print(f"Cleaning summary saved to: {summary_path}")

print("\nMain cleaned categories:")
print("\nSector:")
print(df["sector"].value_counts())

print("\nCollateral:")
print(df["collateral"].value_counts())

print("\nPerformance Status:")
print(df["performance_status"].value_counts())