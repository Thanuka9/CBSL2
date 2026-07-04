from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Exercise 02 - Step 05
# Exploratory Data Analysis and Financial Indicators
#
# This script calculates:
# - Portfolio overview KPIs
# - Sector exposure and concentration
# - NPL ratios by sector, loan type, collateral and rating
# - Annual portfolio growth
# - Macro + portfolio trend indicators
# - Correlation analysis
# - Visualisations for dashboard/report
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

print(f"Reading loan-macro panel: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

print("\nPanel loaded.")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]:,}")

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def npl_amount_ratio(group):
    total = group["amount_outstanding_lkr"].sum()
    npl = group.loc[group["is_npl"] == 1, "amount_outstanding_lkr"].sum()
    if total == 0:
        return 0
    return npl / total * 100

def exposure_share(group_total, portfolio_total):
    if portfolio_total == 0:
        return 0
    return group_total / portfolio_total * 100

portfolio_total_lkr = df["amount_outstanding_lkr"].sum()

# ------------------------------------------------------------
# 1. Portfolio summary KPIs
# ------------------------------------------------------------

portfolio_summary = {
    "number_of_loans": len(df),
    "total_outstanding_lkr": portfolio_total_lkr,
    "total_outstanding_mn_lkr": df["amount_outstanding_mn_lkr"].sum(),
    "average_loan_size_mn_lkr": df["amount_outstanding_mn_lkr"].mean(),
    "median_loan_size_mn_lkr": df["amount_outstanding_mn_lkr"].median(),
    "max_loan_size_mn_lkr": df["amount_outstanding_mn_lkr"].max(),
    "npl_count": df["is_npl"].sum(),
    "npl_ratio_count_pct": df["is_npl"].mean() * 100,
    "npl_amount_lkr": df.loc[df["is_npl"] == 1, "amount_outstanding_lkr"].sum(),
    "npl_ratio_amount_pct": (
        df.loc[df["is_npl"] == 1, "amount_outstanding_lkr"].sum()
        / portfolio_total_lkr
        * 100
    ),
    "fully_unsecured_share_count_pct": df["is_fully_unsecured"].mean() * 100,
    "fully_unsecured_share_amount_pct": (
        df.loc[df["is_fully_unsecured"] == 1, "amount_outstanding_lkr"].sum()
        / portfolio_total_lkr
        * 100
    ),
    "unsecured_or_partial_share_count_pct": df["has_unsecured_risk"].mean() * 100,
    "unsecured_or_partial_share_amount_pct": (
        df.loc[df["has_unsecured_risk"] == 1, "amount_outstanding_lkr"].sum()
        / portfolio_total_lkr
        * 100
    ),
    "average_rating_rank": df["rating_rank"].mean(),
    "weak_rating_share_count_pct": df["weak_rating_flag"].mean() * 100,
    "large_exposure_share_count_pct": df["large_exposure_flag"].mean() * 100,
    "loan_year_min": df["year"].min(),
    "loan_year_max": df["year"].max()
}

portfolio_summary_path = OUTPUT_DIR / "05_portfolio_summary.csv"
pd.DataFrame([portfolio_summary]).to_csv(portfolio_summary_path, index=False)

# ------------------------------------------------------------
# 2. Sector KPI table
# ------------------------------------------------------------

sector_kpi = (
    df.groupby("sector")
    .apply(
        lambda g: pd.Series({
            "loan_count": len(g),
            "total_outstanding_lkr": g["amount_outstanding_lkr"].sum(),
            "total_outstanding_mn_lkr": g["amount_outstanding_mn_lkr"].sum(),
            "average_loan_size_mn_lkr": g["amount_outstanding_mn_lkr"].mean(),
            "median_loan_size_mn_lkr": g["amount_outstanding_mn_lkr"].median(),
            "npl_count": g["is_npl"].sum(),
            "npl_ratio_count_pct": g["is_npl"].mean() * 100,
            "npl_ratio_amount_pct": npl_amount_ratio(g),
            "fully_unsecured_share_count_pct": g["is_fully_unsecured"].mean() * 100,
            "unsecured_or_partial_share_count_pct": g["has_unsecured_risk"].mean() * 100,
            "average_collateral_risk_score": g["collateral_risk_score"].mean(),
            "average_rating_rank": g["rating_rank"].mean(),
            "weak_rating_share_count_pct": g["weak_rating_flag"].mean() * 100,
            "large_exposure_count": g["large_exposure_flag"].sum()
        })
    )
    .reset_index()
)

sector_kpi["portfolio_share_pct"] = (
    sector_kpi["total_outstanding_lkr"] / portfolio_total_lkr * 100
)

sector_kpi = sector_kpi.sort_values("total_outstanding_lkr", ascending=False)

sector_kpi_path = OUTPUT_DIR / "05_sector_kpi.csv"
sector_kpi.to_csv(sector_kpi_path, index=False)

# ------------------------------------------------------------
# 3. Loan type KPI
# ------------------------------------------------------------

loan_type_kpi = (
    df.groupby("loan_type")
    .apply(
        lambda g: pd.Series({
            "loan_count": len(g),
            "total_outstanding_lkr": g["amount_outstanding_lkr"].sum(),
            "total_outstanding_mn_lkr": g["amount_outstanding_mn_lkr"].sum(),
            "portfolio_share_pct": g["amount_outstanding_lkr"].sum() / portfolio_total_lkr * 100,
            "npl_ratio_count_pct": g["is_npl"].mean() * 100,
            "npl_ratio_amount_pct": npl_amount_ratio(g),
            "average_rating_rank": g["rating_rank"].mean(),
            "average_collateral_risk_score": g["collateral_risk_score"].mean()
        })
    )
    .reset_index()
    .sort_values("total_outstanding_lkr", ascending=False)
)

loan_type_kpi_path = OUTPUT_DIR / "05_loan_type_kpi.csv"
loan_type_kpi.to_csv(loan_type_kpi_path, index=False)

# ------------------------------------------------------------
# 4. Collateral KPI
# ------------------------------------------------------------

collateral_kpi = (
    df.groupby("collateral")
    .apply(
        lambda g: pd.Series({
            "loan_count": len(g),
            "total_outstanding_lkr": g["amount_outstanding_lkr"].sum(),
            "total_outstanding_mn_lkr": g["amount_outstanding_mn_lkr"].sum(),
            "portfolio_share_pct": g["amount_outstanding_lkr"].sum() / portfolio_total_lkr * 100,
            "npl_ratio_count_pct": g["is_npl"].mean() * 100,
            "npl_ratio_amount_pct": npl_amount_ratio(g),
            "average_rating_rank": g["rating_rank"].mean()
        })
    )
    .reset_index()
    .sort_values("total_outstanding_lkr", ascending=False)
)

collateral_kpi_path = OUTPUT_DIR / "05_collateral_kpi.csv"
collateral_kpi.to_csv(collateral_kpi_path, index=False)

# ------------------------------------------------------------
# 5. Rating KPI
# ------------------------------------------------------------

rating_kpi = (
    df.groupby("initial_rating")
    .apply(
        lambda g: pd.Series({
            "loan_count": len(g),
            "total_outstanding_lkr": g["amount_outstanding_lkr"].sum(),
            "total_outstanding_mn_lkr": g["amount_outstanding_mn_lkr"].sum(),
            "portfolio_share_pct": g["amount_outstanding_lkr"].sum() / portfolio_total_lkr * 100,
            "npl_ratio_count_pct": g["is_npl"].mean() * 100,
            "npl_ratio_amount_pct": npl_amount_ratio(g),
            "rating_rank": g["rating_rank"].mean()
        })
    )
    .reset_index()
    .sort_values("rating_rank", ascending=True)
)

rating_kpi_path = OUTPUT_DIR / "05_rating_kpi.csv"
rating_kpi.to_csv(rating_kpi_path, index=False)

# ------------------------------------------------------------
# 6. Annual trend with macro context
# ------------------------------------------------------------

yearly = (
    df.groupby("year")
    .apply(
        lambda g: pd.Series({
            "loan_count": len(g),
            "total_outstanding_lkr": g["amount_outstanding_lkr"].sum(),
            "total_outstanding_mn_lkr": g["amount_outstanding_mn_lkr"].sum(),
            "npl_ratio_count_pct": g["is_npl"].mean() * 100,
            "npl_ratio_amount_pct": npl_amount_ratio(g),
            "average_rating_rank": g["rating_rank"].mean(),
            "average_collateral_risk_score": g["collateral_risk_score"].mean(),
            "sri_lanka_gdp_growth_pct": g["sri_lanka_gdp_growth_pct"].iloc[0],
            "sri_lanka_inflation_pct": g["sri_lanka_inflation_pct"].iloc[0],
            "sri_lanka_unemployment_pct": g["sri_lanka_unemployment_pct"].iloc[0],
            "avg_exchange_rate_lkr_usd": g["avg_exchange_rate_lkr_usd"].iloc[0],
            "policy_rate_pct": g["policy_rate_pct"].iloc[0],
            "private_sector_credit_growth_pct": g["private_sector_credit_growth_pct"].iloc[0],
            "domestic_macro_stress_score": g["domestic_macro_stress_score"].iloc[0],
            "global_macro_stress_score": g["global_macro_stress_score"].iloc[0]
        })
    )
    .reset_index()
    .sort_values("year")
)

yearly["annual_portfolio_growth_pct"] = (
    yearly["total_outstanding_lkr"].pct_change() * 100
)

yearly_path = OUTPUT_DIR / "05_yearly_trend_macro_kpi.csv"
yearly.to_csv(yearly_path, index=False)

# ------------------------------------------------------------
# 7. Concentration indicators
# ------------------------------------------------------------

sector_exposures = sector_kpi["total_outstanding_lkr"] / portfolio_total_lkr
hhi_sector = (sector_exposures ** 2).sum() * 10000

top_3_sector_share = sector_kpi.head(3)["portfolio_share_pct"].sum()
top_5_sector_share = sector_kpi.head(5)["portfolio_share_pct"].sum()

concentration = {
    "sector_hhi": hhi_sector,
    "top_3_sector_share_pct": top_3_sector_share,
    "top_5_sector_share_pct": top_5_sector_share,
    "largest_sector": sector_kpi.iloc[0]["sector"],
    "largest_sector_share_pct": sector_kpi.iloc[0]["portfolio_share_pct"]
}

concentration_path = OUTPUT_DIR / "05_concentration_indicators.csv"
pd.DataFrame([concentration]).to_csv(concentration_path, index=False)

# ------------------------------------------------------------
# 8. Correlation analysis
# ------------------------------------------------------------

corr_cols = [
    "amount_outstanding_mn_lkr",
    "is_npl",
    "is_fully_unsecured",
    "has_unsecured_risk",
    "collateral_risk_score",
    "rating_rank",
    "weak_rating_flag",
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

corr = df[corr_cols].corr(numeric_only=True)

corr_path = OUTPUT_DIR / "05_correlation_matrix.csv"
corr.to_csv(corr_path)

# ------------------------------------------------------------
# 9. Charts
# ------------------------------------------------------------

# Sector exposure
plot_df = sector_kpi.sort_values("total_outstanding_mn_lkr", ascending=True)

plt.figure(figsize=(11, 6))
plt.barh(plot_df["sector"], plot_df["total_outstanding_mn_lkr"])
plt.title("Outstanding Loan Exposure by Sector")
plt.xlabel("Outstanding Amount Rs. Mn")
plt.ylabel("Sector")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "05_sector_exposure.png", dpi=150)
plt.close()

# Sector NPL ratio
plot_df = sector_kpi.sort_values("npl_ratio_amount_pct", ascending=False)

plt.figure(figsize=(11, 6))
plt.bar(plot_df["sector"], plot_df["npl_ratio_amount_pct"])
plt.title("NPL Ratio by Sector")
plt.xlabel("Sector")
plt.ylabel("NPL Ratio by Amount (%)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "05_sector_npl_ratio.png", dpi=150)
plt.close()

# Annual portfolio growth
plt.figure(figsize=(10, 5))
plt.plot(yearly["year"], yearly["total_outstanding_mn_lkr"], marker="o")
plt.title("Annual Loan Portfolio by Origination Year")
plt.xlabel("Year")
plt.ylabel("Outstanding Amount Rs. Mn")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "05_annual_portfolio_trend.png", dpi=150)
plt.close()

# Annual NPL and inflation
plt.figure(figsize=(10, 5))
plt.plot(yearly["year"], yearly["npl_ratio_amount_pct"], marker="o", label="NPL Ratio by Amount (%)")
plt.plot(yearly["year"], yearly["sri_lanka_inflation_pct"], marker="o", label="Inflation (%)")
plt.title("NPL Ratio and Inflation Trend")
plt.xlabel("Year")
plt.ylabel("Percent")
plt.legend()
plt.tight_layout()
plt.savefig(FIGURE_DIR / "05_npl_inflation_trend.png", dpi=150)
plt.close()

# Rating distribution
rating_order = rating_kpi.sort_values("rating_rank")["initial_rating"]

rating_counts = df["initial_rating"].value_counts().reindex(rating_order)

plt.figure(figsize=(9, 5))
plt.bar(rating_counts.index, rating_counts.values)
plt.title("Loan Count by Initial Rating")
plt.xlabel("Initial Rating")
plt.ylabel("Loan Count")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "05_rating_distribution.png", dpi=150)
plt.close()

# ------------------------------------------------------------
# 10. Written EDA summary
# ------------------------------------------------------------

top_sector = sector_kpi.iloc[0]
highest_npl_sector = sector_kpi.sort_values("npl_ratio_amount_pct", ascending=False).iloc[0]
highest_exposure_loan_type = loan_type_kpi.iloc[0]
highest_npl_collateral = collateral_kpi.sort_values("npl_ratio_amount_pct", ascending=False).iloc[0]

summary_text_path = LOG_DIR / "05_eda_financial_indicators_summary.txt"

with open(summary_text_path, "w", encoding="utf-8") as f:
    f.write("Exercise 02 - Step 05 EDA and Financial Indicators Summary\n")
    f.write("=" * 80 + "\n\n")

    f.write("Portfolio Overview\n")
    f.write("-" * 80 + "\n")
    f.write(f"Number of loans: {portfolio_summary['number_of_loans']:,.0f}\n")
    f.write(f"Total outstanding: Rs. {portfolio_summary['total_outstanding_mn_lkr']:,.2f} Mn\n")
    f.write(f"NPL ratio by count: {portfolio_summary['npl_ratio_count_pct']:.2f}%\n")
    f.write(f"NPL ratio by amount: {portfolio_summary['npl_ratio_amount_pct']:.2f}%\n")
    f.write(f"Fully unsecured exposure share by amount: {portfolio_summary['fully_unsecured_share_amount_pct']:.2f}%\n")
    f.write(f"Unsecured or partially secured exposure share by amount: {portfolio_summary['unsecured_or_partial_share_amount_pct']:.2f}%\n\n")

    f.write("Key Sector Findings\n")
    f.write("-" * 80 + "\n")
    f.write(
        f"Largest sector by exposure: {top_sector['sector']} "
        f"({top_sector['portfolio_share_pct']:.2f}% of portfolio).\n"
    )
    f.write(
        f"Highest NPL sector by amount: {highest_npl_sector['sector']} "
        f"({highest_npl_sector['npl_ratio_amount_pct']:.2f}%).\n"
    )
    f.write(
        f"Top 3 sectors account for {top_3_sector_share:.2f}% of total exposure.\n"
    )
    f.write(
        f"Top 5 sectors account for {top_5_sector_share:.2f}% of total exposure.\n"
    )
    f.write(f"Sector HHI: {hhi_sector:.2f}\n\n")

    f.write("Loan Type / Collateral Findings\n")
    f.write("-" * 80 + "\n")
    f.write(
        f"Largest loan type by exposure: {highest_exposure_loan_type['loan_type']}.\n"
    )
    f.write(
        f"Collateral category with highest NPL ratio by amount: "
        f"{highest_npl_collateral['collateral']} "
        f"({highest_npl_collateral['npl_ratio_amount_pct']:.2f}%).\n\n"
    )

    f.write("Macro Context\n")
    f.write("-" * 80 + "\n")
    f.write(
        "Macro variables were merged by loan origination year. "
        "They provide context for risk interpretation, especially during "
        "the 2020 COVID contraction and the 2022-2023 Sri Lanka crisis period. "
        "Because the loan data is loan-level origination data, these macro "
        "variables are not interpreted as direct causal drivers.\n\n"
    )

    f.write("Generated Outputs\n")
    f.write("-" * 80 + "\n")
    f.write("- outputs/05_portfolio_summary.csv\n")
    f.write("- outputs/05_sector_kpi.csv\n")
    f.write("- outputs/05_loan_type_kpi.csv\n")
    f.write("- outputs/05_collateral_kpi.csv\n")
    f.write("- outputs/05_rating_kpi.csv\n")
    f.write("- outputs/05_yearly_trend_macro_kpi.csv\n")
    f.write("- outputs/05_concentration_indicators.csv\n")
    f.write("- outputs/05_correlation_matrix.csv\n")
    f.write("- figures/05_sector_exposure.png\n")
    f.write("- figures/05_sector_npl_ratio.png\n")
    f.write("- figures/05_annual_portfolio_trend.png\n")
    f.write("- figures/05_npl_inflation_trend.png\n")
    f.write("- figures/05_rating_distribution.png\n")

print("\nStep 05 EDA and financial indicators completed successfully.")
print(f"Portfolio summary saved to: {portfolio_summary_path}")
print(f"Sector KPI saved to: {sector_kpi_path}")
print(f"Yearly trend saved to: {yearly_path}")
print(f"Correlation matrix saved to: {corr_path}")
print(f"Summary note saved to: {summary_text_path}")

print("\nMain portfolio KPIs:")
print(pd.DataFrame([portfolio_summary]).T)

print("\nTop sectors by exposure:")
print(sector_kpi[["sector", "total_outstanding_mn_lkr", "portfolio_share_pct", "npl_ratio_amount_pct"]].head(10))