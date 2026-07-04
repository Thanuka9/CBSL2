from pathlib import Path
import pandas as pd

# ============================================================
# Exercise 02 - Step 01b
# Raw data profiling before cleaning
#
# Purpose:
# Understand the raw dataset before transformation.
# This step documents data quality issues, distributions,
# possible category inconsistencies, and early risk patterns.
# ============================================================

BASE_DIR = Path.cwd()
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Load raw file
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

df = pd.read_excel(RAW_FILE)

print(f"Loaded raw dataset: {RAW_FILE}")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]:,}")

# ------------------------------------------------------------
# Basic raw profiling
# ------------------------------------------------------------

profile_rows = []

for col in df.columns:
    profile_rows.append({
        "column": col,
        "data_type": str(df[col].dtype),
        "missing_count": df[col].isna().sum(),
        "missing_pct": df[col].isna().mean() * 100,
        "unique_count": df[col].nunique(dropna=True),
        "duplicate_values_possible": df[col].duplicated().sum()
    })

profile_df = pd.DataFrame(profile_rows)
profile_df.to_csv(OUTPUT_DIR / "01b_raw_column_profile.csv", index=False)

# ------------------------------------------------------------
# Raw categorical distributions
# ------------------------------------------------------------

categorical_output = []

for col in df.columns:
    if df[col].dtype == "object" or df[col].dtype == "string":
        counts = df[col].value_counts(dropna=False).reset_index()
        counts.columns = ["value", "count"]
        counts["column"] = col
        counts["share_pct"] = counts["count"] / len(df) * 100
        categorical_output.append(counts)

if categorical_output:
    category_df = pd.concat(categorical_output, ignore_index=True)
    category_df = category_df[["column", "value", "count", "share_pct"]]
    category_df.to_csv(OUTPUT_DIR / "01b_raw_category_distribution.csv", index=False)

# ------------------------------------------------------------
# Raw numerical summary
# ------------------------------------------------------------

numeric_df = df.select_dtypes(include=["number"])

if not numeric_df.empty:
    numeric_summary = numeric_df.describe().T
    numeric_summary.to_csv(OUTPUT_DIR / "01b_raw_numeric_summary.csv")

# ------------------------------------------------------------
# Early raw relationship checks
# These are not final findings yet.
# They help us understand whether useful risk relationships exist.
# ------------------------------------------------------------

relationship_tables = {}

required_cols = [
    "Sector",
    "Loan Type",
    "Collateral",
    "Initial Rating",
    "Performing / Non Performing",
    "Amount Outstanding (Rs.)"
]

available_required = [col for col in required_cols if col in df.columns]

if len(available_required) == len(required_cols):

    temp = df.copy()

    temp["Amount Outstanding (Rs.)"] = pd.to_numeric(
        temp["Amount Outstanding (Rs.)"],
        errors="coerce"
    )

    # Sector vs performance
    sector_performance = (
        temp.groupby(["Sector", "Performing / Non Performing"])
        .agg(
            loan_count=("Loan ID", "count"),
            outstanding_lkr=("Amount Outstanding (Rs.)", "sum")
        )
        .reset_index()
    )
    sector_performance.to_csv(
        OUTPUT_DIR / "01b_raw_sector_vs_performance.csv",
        index=False
    )

    # Collateral vs performance
    collateral_performance = (
        temp.groupby(["Collateral", "Performing / Non Performing"])
        .agg(
            loan_count=("Loan ID", "count"),
            outstanding_lkr=("Amount Outstanding (Rs.)", "sum")
        )
        .reset_index()
    )
    collateral_performance.to_csv(
        OUTPUT_DIR / "01b_raw_collateral_vs_performance.csv",
        index=False
    )

    # Rating vs performance
    rating_performance = (
        temp.groupby(["Initial Rating", "Performing / Non Performing"])
        .agg(
            loan_count=("Loan ID", "count"),
            outstanding_lkr=("Amount Outstanding (Rs.)", "sum")
        )
        .reset_index()
    )
    rating_performance.to_csv(
        OUTPUT_DIR / "01b_raw_rating_vs_performance.csv",
        index=False
    )

    # Loan type vs performance
    loan_type_performance = (
        temp.groupby(["Loan Type", "Performing / Non Performing"])
        .agg(
            loan_count=("Loan ID", "count"),
            outstanding_lkr=("Amount Outstanding (Rs.)", "sum")
        )
        .reset_index()
    )
    loan_type_performance.to_csv(
        OUTPUT_DIR / "01b_raw_loan_type_vs_performance.csv",
        index=False
    )

# ------------------------------------------------------------
# Written interpretation
# ------------------------------------------------------------

report_path = OUTPUT_DIR / "01b_raw_data_profile_report.txt"

with open(report_path, "w", encoding="utf-8") as f:
    f.write("Exercise 02 - Raw Data Profile Before Cleaning\n")
    f.write("=" * 70 + "\n\n")

    f.write("Purpose\n")
    f.write("-" * 70 + "\n")
    f.write(
        "This profile was prepared before formal data cleaning to understand "
        "the original structure, completeness, category consistency, and early "
        "risk relationships in the supplied ABC Bank PLC loan portfolio.\n\n"
    )

    f.write("Dataset Shape\n")
    f.write("-" * 70 + "\n")
    f.write(f"Rows: {df.shape[0]:,}\n")
    f.write(f"Columns: {df.shape[1]:,}\n\n")

    f.write("Columns\n")
    f.write("-" * 70 + "\n")
    for col in df.columns:
        f.write(f"- {col}\n")

    f.write("\nInitial Data Quality Observations\n")
    f.write("-" * 70 + "\n")
    f.write("The raw dataset was checked for missing values, duplicate values, ")
    f.write("data types, category labels, and numeric ranges. These checks help ")
    f.write("identify cleaning requirements before any transformation is applied.\n\n")

    f.write("Early Relationship Checks\n")
    f.write("-" * 70 + "\n")
    f.write(
        "Preliminary cross-tabulations were created for sector, collateral, "
        "initial rating, and loan type against performance status. These raw "
        "relationship checks are used only for initial understanding. Final "
        "EDA and financial indicators are calculated after cleaning and "
        "standardisation to avoid misleading results caused by spelling or "
        "formatting inconsistencies.\n\n"
    )

    f.write("Generated Files\n")
    f.write("-" * 70 + "\n")
    f.write("- outputs/01b_raw_column_profile.csv\n")
    f.write("- outputs/01b_raw_category_distribution.csv\n")
    f.write("- outputs/01b_raw_numeric_summary.csv\n")
    f.write("- outputs/01b_raw_sector_vs_performance.csv\n")
    f.write("- outputs/01b_raw_collateral_vs_performance.csv\n")
    f.write("- outputs/01b_raw_rating_vs_performance.csv\n")
    f.write("- outputs/01b_raw_loan_type_vs_performance.csv\n")

print("\nStep 01b raw data profiling completed successfully.")
print("Saved outputs:")
print("- outputs/01b_raw_column_profile.csv")
print("- outputs/01b_raw_category_distribution.csv")
print("- outputs/01b_raw_numeric_summary.csv")
print("- outputs/01b_raw_sector_vs_performance.csv")
print("- outputs/01b_raw_collateral_vs_performance.csv")
print("- outputs/01b_raw_rating_vs_performance.csv")
print("- outputs/01b_raw_loan_type_vs_performance.csv")
print("- outputs/01b_raw_data_profile_report.txt")