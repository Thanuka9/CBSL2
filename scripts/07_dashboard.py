from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# Exercise 02 - Step 07
# Interactive Dashboard / Visualisation
#
# Creates an HTML dashboard for management / supervisory use.
# This supports:
# - KPI reporting
# - Sector exposure monitoring
# - NPL and risk analysis
# - Macro context interpretation
# - Anomaly watchlist review
# ============================================================

BASE_DIR = Path.cwd()

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
DASHBOARD_DIR = BASE_DIR / "dashboard"
LOG_DIR = BASE_DIR / "logs"

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

PANEL_PATH = PROCESSED_DIR / "04_loan_macro_panel.csv"
SECTOR_KPI_PATH = OUTPUT_DIR / "05_sector_kpi.csv"
YEARLY_PATH = OUTPUT_DIR / "05_yearly_trend_macro_kpi.csv"
RISK_PATH = OUTPUT_DIR / "06_sector_composite_risk_score.csv"
ANOMALY_PATH = OUTPUT_DIR / "06_top_250_anomaly_watchlist.csv"
FEATURE_PATH = OUTPUT_DIR / "06_risk_driver_feature_importance.csv"

print("Reading dashboard datasets...")

df = pd.read_csv(PANEL_PATH)
sector = pd.read_csv(SECTOR_KPI_PATH)
yearly = pd.read_csv(YEARLY_PATH)
risk = pd.read_csv(RISK_PATH)
anomalies = pd.read_csv(ANOMALY_PATH)
features = pd.read_csv(FEATURE_PATH)

# ------------------------------------------------------------
# KPI values
# ------------------------------------------------------------

total_loans = len(df)
total_outstanding_mn = df["amount_outstanding_mn_lkr"].sum()

npl_ratio_amount = (
    df.loc[df["is_npl"] == 1, "amount_outstanding_lkr"].sum()
    / df["amount_outstanding_lkr"].sum()
    * 100
)

npl_ratio_count = df["is_npl"].mean() * 100

fully_unsecured_share_amount = (
    df.loc[df["is_fully_unsecured"] == 1, "amount_outstanding_lkr"].sum()
    / df["amount_outstanding_lkr"].sum()
    * 100
)

unsecured_partial_share_amount = (
    df.loc[df["has_unsecured_risk"] == 1, "amount_outstanding_lkr"].sum()
    / df["amount_outstanding_lkr"].sum()
    * 100
)

top_sector = sector.sort_values("total_outstanding_lkr", ascending=False).iloc[0]
top_risk_sector = risk.sort_values("composite_risk_score", ascending=False).iloc[0]

# ------------------------------------------------------------
# Charts
# ------------------------------------------------------------

fig_sector_exposure = px.bar(
    sector.sort_values("total_outstanding_mn_lkr", ascending=False),
    x="sector",
    y="total_outstanding_mn_lkr",
    title="Outstanding Exposure by Economic Sector",
    labels={
        "sector": "Sector",
        "total_outstanding_mn_lkr": "Outstanding Rs. Mn"
    }
)

fig_sector_npl = px.bar(
    sector.sort_values("npl_ratio_amount_pct", ascending=False),
    x="sector",
    y="npl_ratio_amount_pct",
    title="NPL Ratio by Sector",
    labels={
        "sector": "Sector",
        "npl_ratio_amount_pct": "NPL Ratio by Amount (%)"
    }
)

fig_risk_score = px.bar(
    risk.sort_values("composite_risk_score", ascending=False),
    x="sector",
    y="composite_risk_score",
    title="Composite Sector Risk Score",
    labels={
        "sector": "Sector",
        "composite_risk_score": "Risk Score / 100"
    }
)

fig_yearly_exposure = px.line(
    yearly,
    x="year",
    y="total_outstanding_mn_lkr",
    markers=True,
    title="Annual Loan Portfolio by Origination Year",
    labels={
        "year": "Year",
        "total_outstanding_mn_lkr": "Outstanding Rs. Mn"
    }
)

fig_growth = px.bar(
    yearly,
    x="year",
    y="annual_portfolio_growth_pct",
    title="Annual Portfolio Growth by Origination Year",
    labels={
        "year": "Year",
        "annual_portfolio_growth_pct": "Annual Growth (%)"
    }
)

fig_macro_npl = go.Figure()

fig_macro_npl.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["npl_ratio_amount_pct"],
        mode="lines+markers",
        name="NPL Ratio by Amount (%)"
    )
)

fig_macro_npl.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["sri_lanka_inflation_pct"],
        mode="lines+markers",
        name="Inflation (%)"
    )
)

fig_macro_npl.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["domestic_macro_stress_score"],
        mode="lines+markers",
        name="Domestic Macro Stress Score"
    )
)

fig_macro_npl.update_layout(
    title="Portfolio Risk and Macro Context",
    xaxis_title="Year",
    yaxis_title="Percent / Score"
)

top_features = features.head(15).sort_values("importance", ascending=True)

fig_features = px.bar(
    top_features,
    x="importance",
    y="feature",
    orientation="h",
    title="Top Risk Drivers from Random Forest Model",
    labels={
        "importance": "Feature Importance",
        "feature": "Risk Driver"
    }
)

# ------------------------------------------------------------
# Table HTML
# ------------------------------------------------------------

anomaly_table = anomalies[
    [
        "loan_id",
        "sector",
        "loan_type",
        "collateral",
        "initial_rating",
        "performance_status",
        "amount_outstanding_mn_lkr",
        "loan_anomaly_score"
    ]
].head(20).copy()

anomaly_table["amount_outstanding_mn_lkr"] = anomaly_table["amount_outstanding_mn_lkr"].round(2)
anomaly_table["loan_anomaly_score"] = anomaly_table["loan_anomaly_score"].round(2)

risk_table = risk[
    [
        "sector",
        "portfolio_share_pct",
        "npl_ratio_amount_pct",
        "average_collateral_risk_score",
        "average_rating_rank",
        "composite_risk_score"
    ]
].copy()

risk_table["portfolio_share_pct"] = risk_table["portfolio_share_pct"].round(2)
risk_table["npl_ratio_amount_pct"] = risk_table["npl_ratio_amount_pct"].round(2)
risk_table["average_collateral_risk_score"] = risk_table["average_collateral_risk_score"].round(2)
risk_table["average_rating_rank"] = risk_table["average_rating_rank"].round(2)
risk_table["composite_risk_score"] = risk_table["composite_risk_score"].round(2)

# ------------------------------------------------------------
# Build dashboard HTML
# ------------------------------------------------------------

dashboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ABC Bank PLC Loan Portfolio Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 25px;
            background-color: #f4f6f8;
            color: #222;
        }}
        h1, h2 {{
            color: #1f2937;
        }}
        .subtitle {{
            color: #555;
            margin-bottom: 25px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }}
        .kpi-card {{
            background: white;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }}
        .kpi-card h2 {{
            margin: 0;
            font-size: 26px;
            color: #0f4c81;
        }}
        .kpi-card p {{
            margin: 6px 0 0 0;
            color: #666;
            font-size: 14px;
        }}
        .chart-card {{
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 22px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background: white;
            font-size: 13px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #e9eef5;
        }}
        .note {{
            background: #fff8dc;
            padding: 15px;
            border-left: 5px solid #d9a300;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>

<h1>ABC Bank PLC Loan Portfolio Dashboard</h1>

<p class="subtitle">
Exercise 02: Financial Sector Data Analysis. This dashboard combines the supplied ABC Bank loan portfolio
with annual macroeconomic context to support management and supervisory decision-making.
</p>

<div class="kpi-grid">
    <div class="kpi-card">
        <h2>{total_loans:,.0f}</h2>
        <p>Total Loans</p>
    </div>
    <div class="kpi-card">
        <h2>Rs. {total_outstanding_mn:,.0f} Mn</h2>
        <p>Total Outstanding</p>
    </div>
    <div class="kpi-card">
        <h2>{npl_ratio_amount:.2f}%</h2>
        <p>NPL Ratio by Amount</p>
    </div>
    <div class="kpi-card">
        <h2>{unsecured_partial_share_amount:.2f}%</h2>
        <p>Unsecured / Partially Secured Exposure</p>
    </div>
</div>

<div class="kpi-grid">
    <div class="kpi-card">
        <h2>{npl_ratio_count:.2f}%</h2>
        <p>NPL Ratio by Count</p>
    </div>
    <div class="kpi-card">
        <h2>{fully_unsecured_share_amount:.2f}%</h2>
        <p>Fully Unsecured Exposure</p>
    </div>
    <div class="kpi-card">
        <h2>{top_sector['sector']}</h2>
        <p>Largest Sector: {top_sector['portfolio_share_pct']:.2f}% of portfolio</p>
    </div>
    <div class="kpi-card">
        <h2>{top_risk_sector['sector']}</h2>
        <p>Highest Composite Risk Score: {top_risk_sector['composite_risk_score']:.2f}</p>
    </div>
</div>

<div class="note">
    <b>Interpretation note:</b>
    The macro variables are merged by loan origination year. They are used for contextual
    financial-risk interpretation, not causal inference, because the supplied loan data is
    loan-level origination data rather than a full monthly balance-sheet time series.
</div>

<div class="chart-card">
    {fig_sector_exposure.to_html(full_html=False, include_plotlyjs="cdn")}
</div>

<div class="chart-card">
    {fig_sector_npl.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="chart-card">
    {fig_risk_score.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="chart-card">
    {fig_yearly_exposure.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="chart-card">
    {fig_growth.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="chart-card">
    {fig_macro_npl.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="chart-card">
    {fig_features.to_html(full_html=False, include_plotlyjs=False)}
</div>

<h2>Sector Risk Table</h2>
{risk_table.to_html(index=False)}

<h2>Top 20 Loan Anomaly Watchlist</h2>
{anomaly_table.to_html(index=False)}

<h2>Management / Supervisory Use</h2>
<ul>
    <li>Monitor sectors with high exposure and high NPL ratios.</li>
    <li>Prioritise sectors with high composite risk scores for review.</li>
    <li>Investigate anomaly-watchlist loans with large exposure, weak ratings, unsecured collateral, and NPL status.</li>
    <li>Use macro stress indicators as context for portfolio surveillance.</li>
</ul>

</body>
</html>
"""

dashboard_path = DASHBOARD_DIR / "abc_bank_loan_portfolio_dashboard.html"
dashboard_path.write_text(dashboard_html, encoding="utf-8")

# ------------------------------------------------------------
# Save dashboard design note
# ------------------------------------------------------------

design_note = """
Exercise 02 - Dashboard Design Note
======================================================================

Dashboard objective:
To communicate ABC Bank PLC loan portfolio risk, exposure concentration,
asset quality and macroeconomic context to management or supervisors.

Selected visuals:
1. KPI cards:
   - Total loans
   - Total outstanding
   - NPL ratio by amount
   - Unsecured / partially secured exposure
   These provide immediate portfolio health indicators.

2. Sector exposure bar chart:
   Shows concentration across economic sectors.

3. Sector NPL ratio chart:
   Identifies sectors with weaker asset quality.

4. Composite sector risk score chart:
   Combines NPL, collateral risk, rating weakness and concentration.

5. Annual portfolio trend:
   Shows origination-year exposure and portfolio movement.

6. Macro and NPL trend:
   Places loan portfolio risk in the context of inflation and macro stress.

7. Risk-driver feature importance:
   Explains underlying drivers of NPL risk from the Random Forest model.

8. Anomaly watchlist:
   Supports loan-level review and targeted investigation.

Limitations:
The dashboard is generated as an HTML BI-style dashboard. In Power BI,
the same CSV outputs can be loaded and the same measures recreated.
"""

design_note_path = LOG_DIR / "07_dashboard_design_note.txt"
design_note_path.write_text(design_note, encoding="utf-8")

print("\nStep 07 dashboard completed successfully.")
print(f"Dashboard saved to: {dashboard_path}")
print(f"Dashboard design note saved to: {design_note_path}")