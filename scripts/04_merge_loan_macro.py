from pathlib import Path
import pandas as pd

# ============================================================
# Exercise 02 - Step 04
# Merge cleaned institution-specific loan data with macro data
#
# Purpose:
# Create one analysis-ready panel dataset containing:
# - loan-level ABC Bank portfolio data
# - Sri Lanka macroeconomic indicators
# - global macro context indicators
#
# Merge key:
# - loan origination year
# ============================================================

BASE_DIR = Path.cwd()

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOAN_PATH = PROCESSED_DIR / "02_clean_loan_portfolio.csv"
MACRO_PATH = PROCESSED_DIR / "03_macro_variables_annual.csv"
PANEL_PATH = PROCESSED_DIR / "04_loan_macro_panel.csv"

# ------------------------------------------------------------
# Load datasets
# ------------------------------------------------------------

print(f"Reading cleaned loan data: {LOAN_PATH}")
loans = pd.read_csv(LOAN_PATH)

print(f"Reading macro data: {MACRO_PATH}")
macro = pd.read_csv(MACRO_PATH)

print("\nLoan data shape:")
print(loans.shape)

print("\nMacro data shape:")
print(macro.shape)

# ------------------------------------------------------------
# Validate merge keys
# ------------------------------------------------------------

if "year" not in loans.columns:
    raise ValueError("Loan dataset does not contain 'year' column.")

if "year" not in macro.columns:
    raise ValueError("Macro dataset does not contain 'year' column.")

loan_years = sorted(loans["year"].dropna().unique())
macro_years = sorted(macro["year"].dropna().unique())

print("\nLoan years:")
print(loan_years)

print("\nMacro years:")
print(macro_years)

missing_macro_years = sorted(set(loan_years) - set(macro_years))

if missing_macro_years:
    raise ValueError(f"Macro data missing for loan years: {missing_macro_years}")

# ------------------------------------------------------------
# Merge loan-level data with macro variables
# ------------------------------------------------------------

panel = loans.merge(
    macro,
    on="year",
    how="left",
    validate="many_to_one"
)

# ------------------------------------------------------------
# Check merge quality
# ------------------------------------------------------------

macro_columns = [col for col in macro.columns if col != "year"]

missing_macro_after_merge = panel[macro_columns].isna().sum()

merge_check = pd.DataFrame({
    "column": missing_macro_after_merge.index,
    "missing_count": missing_macro_after_merge.values,
    "missing_pct": missing_macro_after_merge.values / len(panel) * 100
})

merge_check_path = OUTPUT_DIR / "04_merge_missing_check.csv"
merge_check.to_csv(merge_check_path, index=False)

# ------------------------------------------------------------
# Create annual portfolio summary with macro context
# ------------------------------------------------------------

yearly_panel = (
    panel.groupby("year")
    .agg(
        loan_count=("loan_id", "count"),
        total_outstanding_lkr=("amount_outstanding_lkr", "sum"),
        total_outstanding_mn_lkr=("amount_outstanding_mn_lkr", "sum"),
        npl_count=("is_npl", "sum"),
        npl_ratio_count_pct=("is_npl", lambda x: x.mean() * 100),
        npl_amount_lkr=(
            "amount_outstanding_lkr",
            lambda x: panel.loc[x.index[panel.loc[x.index, "is_npl"] == 1], "amount_outstanding_lkr"].sum()
        ),
        average_rating_rank=("rating_rank", "mean"),
        collateral_risk_score=("collateral_risk_score", "mean"),
        sri_lanka_gdp_growth_pct=("sri_lanka_gdp_growth_pct", "first"),
        sri_lanka_inflation_pct=("sri_lanka_inflation_pct", "first"),
        sri_lanka_unemployment_pct=("sri_lanka_unemployment_pct", "first"),
        avg_exchange_rate_lkr_usd=("avg_exchange_rate_lkr_usd", "first"),
        policy_rate_pct=("policy_rate_pct", "first"),
        private_sector_credit_growth_pct=("private_sector_credit_growth_pct", "first"),
        domestic_macro_stress_score=("domestic_macro_stress_score", "first"),
        global_macro_stress_score=("global_macro_stress_score", "first")
    )
    .reset_index()
)

yearly_panel["npl_ratio_amount_pct"] = (
    yearly_panel["npl_amount_lkr"] / yearly_panel["total_outstanding_lkr"] * 100
)

yearly_panel["annual_portfolio_growth_pct"] = (
    yearly_panel["total_outstanding_lkr"].pct_change() * 100
)

yearly_path = OUTPUT_DIR / "04_yearly_loan_macro_summary.csv"
yearly_panel.to_csv(yearly_path, index=False)

# ------------------------------------------------------------
# Save final panel
# ------------------------------------------------------------

panel.to_csv(PANEL_PATH, index=False)

# ------------------------------------------------------------
# Save merge log
# ------------------------------------------------------------

log_path = LOG_DIR / "04_merge_loan_macro_log.txt"

with open(log_path, "w", encoding="utf-8") as f:
    f.write("Exercise 02 - Step 04 Loan + Macro Merge Log\n")
    f.write("=" * 70 + "\n\n")

    f.write("Input Files\n")
    f.write("-" * 70 + "\n")
    f.write(f"Loan file: {LOAN_PATH}\n")
    f.write(f"Macro file: {MACRO_PATH}\n\n")

    f.write("Dataset Shapes\n")
    f.write("-" * 70 + "\n")
    f.write(f"Loan data rows: {loans.shape[0]:,}\n")
    f.write(f"Loan data columns: {loans.shape[1]:,}\n")
    f.write(f"Macro data rows: {macro.shape[0]:,}\n")
    f.write(f"Macro data columns: {macro.shape[1]:,}\n")
    f.write(f"Panel rows: {panel.shape[0]:,}\n")
    f.write(f"Panel columns: {panel.shape[1]:,}\n\n")

    f.write("Merge Key\n")
    f.write("-" * 70 + "\n")
    f.write("Merged on loan origination year.\n\n")

    f.write("Loan Years\n")
    f.write("-" * 70 + "\n")
    f.write(str(loan_years))
    f.write("\n\n")

    f.write("Macro Years\n")
    f.write("-" * 70 + "\n")
    f.write(str(macro_years))
    f.write("\n\n")

    f.write("Missing Macro Values After Merge\n")
    f.write("-" * 70 + "\n")
    f.write(str(missing_macro_after_merge))
    f.write("\n\n")

    f.write("Methodological Note\n")
    f.write("-" * 70 + "\n")
    f.write(
        "The macro variables were merged by origination year. "
        "This is appropriate for contextual portfolio-risk analysis because "
        "the supplied loan dataset is loan-level origination data rather than "
        "a full monthly balance-sheet time series. The merged macro variables "
        "should not be interpreted as causal drivers without more granular "
        "borrower-level and time-series data.\n"
    )

print("\nStep 04 merge completed successfully.")
print(f"Panel dataset saved to: {PANEL_PATH}")
print(f"Yearly loan-macro summary saved to: {yearly_path}")
print(f"Merge missing check saved to: {merge_check_path}")
print(f"Merge log saved to: {log_path}")

print("\nPanel shape:")
print(panel.shape)

print("\nYearly loan-macro summary preview:")
print(yearly_panel.head())