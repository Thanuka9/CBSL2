from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# Exercise 02 - Step 07
# Advanced Interactive Dashboard / Visualisation
#
# Creates:
# 1. Professional HTML management dashboard
# 2. Power BI implementation guide
# 3. Dashboard design note
#
# Purpose:
# - KPI reporting
# - Sector exposure monitoring
# - NPL and asset-quality analysis
# - Macro context
# - Risk-driver storytelling
# - Anomaly review
# - Management / supervisory decision support
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
MODEL_METRICS_PATH = OUTPUT_DIR / "06_model_metrics.txt"
MACRO_SOURCE_PATH = OUTPUT_DIR / "03_macro_variable_sources.csv"

print("Reading dashboard datasets...")

df = pd.read_csv(PANEL_PATH)
sector = pd.read_csv(SECTOR_KPI_PATH)
yearly = pd.read_csv(YEARLY_PATH)
risk = pd.read_csv(RISK_PATH)
anomalies = pd.read_csv(ANOMALY_PATH)
features = pd.read_csv(FEATURE_PATH)

if MACRO_SOURCE_PATH.exists():
    macro_sources = pd.read_csv(MACRO_SOURCE_PATH)
else:
    macro_sources = pd.DataFrame({"note": ["Macro source tracking file was not found."]})


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def apply_layout(fig, height=460):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=40, r=30, t=70, b=55),
        title_font=dict(size=19),
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


def read_roc_auc(metrics_path):
    if not metrics_path.exists():
        return "Not available"

    text = metrics_path.read_text(encoding="utf-8", errors="ignore")

    for line in text.splitlines():
        if "ROC AUC" in line:
            return line.replace("ROC AUC:", "").strip()

    return "Not available"


# ------------------------------------------------------------
# KPI values
# ------------------------------------------------------------

total_loans = len(df)
total_outstanding_lkr = df["amount_outstanding_lkr"].sum()
total_outstanding_mn = df["amount_outstanding_mn_lkr"].sum()

npl_amount_lkr = df.loc[df["is_npl"] == 1, "amount_outstanding_lkr"].sum()
npl_ratio_amount = npl_amount_lkr / total_outstanding_lkr * 100
npl_ratio_count = df["is_npl"].mean() * 100

fully_unsecured_share_amount = (
    df.loc[df["is_fully_unsecured"] == 1, "amount_outstanding_lkr"].sum()
    / total_outstanding_lkr
    * 100
)

unsecured_partial_share_amount = (
    df.loc[df["has_unsecured_risk"] == 1, "amount_outstanding_lkr"].sum()
    / total_outstanding_lkr
    * 100
)

weak_rating_share = df["weak_rating_flag"].mean() * 100
large_exposure_share = df["large_exposure_flag"].mean() * 100

top_sector = sector.sort_values("total_outstanding_lkr", ascending=False).iloc[0]
highest_npl_sector = sector.sort_values("npl_ratio_amount_pct", ascending=False).iloc[0]
top_risk_sector = risk.sort_values("composite_risk_score", ascending=False).iloc[0]

roc_auc_text = read_roc_auc(MODEL_METRICS_PATH)
top_driver = features.iloc[0]["feature"]
top_driver_importance = features.iloc[0]["importance"]


# ------------------------------------------------------------
# Prepare dashboard tables
# ------------------------------------------------------------

sector_plot = sector.copy()
sector_plot["total_outstanding_bn_lkr"] = (
    sector_plot["total_outstanding_lkr"] / 1_000_000_000
)

risk_plot = risk.copy()
risk_plot["total_outstanding_bn_lkr"] = (
    risk_plot["total_outstanding_lkr"] / 1_000_000_000
)

rating_summary = (
    df.groupby("initial_rating")
    .agg(
        loan_count=("loan_id", "count"),
        total_outstanding_mn_lkr=("amount_outstanding_mn_lkr", "sum"),
        npl_ratio_count_pct=("is_npl", lambda x: x.mean() * 100),
        rating_rank=("rating_rank", "mean")
    )
    .reset_index()
    .sort_values("rating_rank")
)

collateral_summary = (
    df.groupby("collateral")
    .agg(
        loan_count=("loan_id", "count"),
        total_outstanding_mn_lkr=("amount_outstanding_mn_lkr", "sum"),
        npl_ratio_count_pct=("is_npl", lambda x: x.mean() * 100),
        collateral_risk_score=("collateral_risk_score", "mean")
    )
    .reset_index()
    .sort_values("total_outstanding_mn_lkr", ascending=False)
)

loan_type_summary = (
    df.groupby("loan_type")
    .agg(
        loan_count=("loan_id", "count"),
        total_outstanding_mn_lkr=("amount_outstanding_mn_lkr", "sum"),
        npl_ratio_count_pct=("is_npl", lambda x: x.mean() * 100)
    )
    .reset_index()
    .sort_values("total_outstanding_mn_lkr", ascending=False)
)

sector_rating_pivot = (
    df.pivot_table(
        index="sector",
        columns="initial_rating",
        values="amount_outstanding_mn_lkr",
        aggfunc="sum",
        fill_value=0
    )
)

rating_order = [
    col for col in ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    if col in sector_rating_pivot.columns
]

sector_rating_pivot = sector_rating_pivot[rating_order]

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
].head(25).copy()

anomaly_table["amount_outstanding_mn_lkr"] = (
    anomaly_table["amount_outstanding_mn_lkr"].round(2)
)

anomaly_table["loan_anomaly_score"] = (
    anomaly_table["loan_anomaly_score"].round(2)
)

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

risk_table = risk_table.round(2)

macro_table = yearly[
    [
        "year",
        "total_outstanding_mn_lkr",
        "annual_portfolio_growth_pct",
        "npl_ratio_amount_pct",
        "sri_lanka_gdp_growth_pct",
        "sri_lanka_inflation_pct",
        "policy_rate_pct",
        "domestic_macro_stress_score"
    ]
].copy()

macro_table = macro_table.round(2)


# ------------------------------------------------------------
# Charts
# ------------------------------------------------------------

fig_sector_exposure = px.bar(
    sector_plot.sort_values("total_outstanding_mn_lkr", ascending=True),
    x="total_outstanding_mn_lkr",
    y="sector",
    orientation="h",
    title="Outstanding Exposure by Economic Sector",
    labels={
        "total_outstanding_mn_lkr": "Outstanding Rs. Mn",
        "sector": "Sector"
    },
    text="total_outstanding_mn_lkr"
)

fig_sector_exposure.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

apply_layout(fig_sector_exposure, height=520)

fig_sector_npl = px.bar(
    sector.sort_values("npl_ratio_amount_pct", ascending=False),
    x="sector",
    y="npl_ratio_amount_pct",
    title="NPL Ratio by Sector",
    labels={
        "npl_ratio_amount_pct": "NPL Ratio by Amount (%)",
        "sector": "Sector"
    },
    text="npl_ratio_amount_pct"
)

fig_sector_npl.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_sector_npl.update_xaxes(tickangle=-35)
apply_layout(fig_sector_npl, height=500)

fig_risk_score = px.bar(
    risk.sort_values("composite_risk_score", ascending=True),
    x="composite_risk_score",
    y="sector",
    orientation="h",
    title="Composite Sector Risk Score",
    labels={
        "composite_risk_score": "Risk Score / 100",
        "sector": "Sector"
    },
    text="composite_risk_score"
)

fig_risk_score.update_traces(
    texttemplate="%{text:.1f}",
    textposition="outside"
)

apply_layout(fig_risk_score, height=520)

fig_sector_bubble = px.scatter(
    risk_plot,
    x="portfolio_share_pct",
    y="npl_ratio_amount_pct",
    size="total_outstanding_bn_lkr",
    color="composite_risk_score",
    hover_name="sector",
    title="Sector Risk Map: Concentration vs Asset Quality",
    labels={
        "portfolio_share_pct": "Portfolio Share (%)",
        "npl_ratio_amount_pct": "NPL Ratio by Amount (%)",
        "total_outstanding_bn_lkr": "Exposure Rs. Bn",
        "composite_risk_score": "Risk Score"
    },
    size_max=55
)

apply_layout(fig_sector_bubble, height=530)

fig_treemap = px.treemap(
    sector_plot,
    path=["sector"],
    values="total_outstanding_mn_lkr",
    color="npl_ratio_amount_pct",
    title="Portfolio Concentration Treemap by Sector",
    labels={
        "total_outstanding_mn_lkr": "Outstanding Rs. Mn",
        "npl_ratio_amount_pct": "NPL Ratio (%)"
    }
)

apply_layout(fig_treemap, height=520)

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

apply_layout(fig_yearly_exposure, height=440)

fig_growth = px.bar(
    yearly,
    x="year",
    y="annual_portfolio_growth_pct",
    title="Annual Portfolio Growth by Origination Year",
    labels={
        "year": "Year",
        "annual_portfolio_growth_pct": "Annual Growth (%)"
    },
    text="annual_portfolio_growth_pct"
)

fig_growth.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

apply_layout(fig_growth, height=440)

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
        y=yearly["sri_lanka_gdp_growth_pct"],
        mode="lines+markers",
        name="GDP Growth (%)"
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

apply_layout(fig_macro_npl, height=510)

fig_exchange_policy = go.Figure()

fig_exchange_policy.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["avg_exchange_rate_lkr_usd"],
        mode="lines+markers",
        name="Avg LKR/USD Exchange Rate",
        yaxis="y1"
    )
)

fig_exchange_policy.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["policy_rate_pct"],
        mode="lines+markers",
        name="Policy Rate (%)",
        yaxis="y2"
    )
)

fig_exchange_policy.update_layout(
    title="Exchange Rate and Interest Rate Context",
    xaxis=dict(title="Year"),
    yaxis=dict(title="Avg LKR/USD"),
    yaxis2=dict(
        title="Policy Rate (%)",
        overlaying="y",
        side="right"
    )
)

apply_layout(fig_exchange_policy, height=460)

top_features = features.head(15).sort_values("importance", ascending=True)

fig_features = px.bar(
    top_features,
    x="importance",
    y="feature",
    orientation="h",
    title=f"Top Risk Drivers from Random Forest Model | ROC AUC: {roc_auc_text}",
    labels={
        "importance": "Feature Importance",
        "feature": "Risk Driver"
    },
    text="importance"
)

fig_features.update_traces(
    texttemplate="%{text:.3f}",
    textposition="outside"
)

apply_layout(fig_features, height=560)

fig_rating = px.bar(
    rating_summary,
    x="initial_rating",
    y="loan_count",
    title="Loan Count by Initial Rating",
    labels={
        "initial_rating": "Initial Rating",
        "loan_count": "Loan Count"
    },
    text="loan_count"
)

fig_rating.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

apply_layout(fig_rating, height=430)

fig_collateral = px.pie(
    collateral_summary,
    values="total_outstanding_mn_lkr",
    names="collateral",
    title="Outstanding Exposure by Collateral Type",
    hole=0.45
)

apply_layout(fig_collateral, height=430)

fig_loan_type = px.bar(
    loan_type_summary,
    x="loan_type",
    y="total_outstanding_mn_lkr",
    title="Outstanding Exposure by Loan Type",
    labels={
        "loan_type": "Loan Type",
        "total_outstanding_mn_lkr": "Outstanding Rs. Mn"
    },
    text="total_outstanding_mn_lkr"
)

fig_loan_type.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

apply_layout(fig_loan_type, height=430)

fig_heatmap = px.imshow(
    sector_rating_pivot,
    title="Sector x Rating Exposure Heatmap | Rs. Mn",
    labels=dict(
        x="Initial Rating",
        y="Sector",
        color="Rs. Mn"
    ),
    aspect="auto"
)

apply_layout(fig_heatmap, height=520)


# ------------------------------------------------------------
# Convert charts to HTML
# ------------------------------------------------------------

chart_html = {
    "sector_exposure": fig_sector_exposure.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    ),
    "sector_npl": fig_sector_npl.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "risk_score": fig_risk_score.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "risk_bubble": fig_sector_bubble.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "treemap": fig_treemap.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "yearly": fig_yearly_exposure.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "growth": fig_growth.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "macro_npl": fig_macro_npl.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "exchange_policy": fig_exchange_policy.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "features": fig_features.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "rating": fig_rating.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "collateral": fig_collateral.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "loan_type": fig_loan_type.to_html(
        full_html=False,
        include_plotlyjs=False
    ),
    "heatmap": fig_heatmap.to_html(
        full_html=False,
        include_plotlyjs=False
    )
}


# ------------------------------------------------------------
# Written dashboard insights
# ------------------------------------------------------------

executive_insight = f"""
The portfolio contains <b>{total_loans:,.0f}</b> loans with total outstanding exposure of
<b>Rs. {total_outstanding_mn:,.0f} Mn</b>. The NPL ratio is
<b>{npl_ratio_amount:.2f}% by amount</b> and <b>{npl_ratio_count:.2f}% by count</b>.
The largest exposure sector is <b>{top_sector['sector']}</b>, while
<b>{top_risk_sector['sector']}</b> has the highest composite risk score.
"""

model_insight = f"""
The Random Forest risk-driver model achieved ROC AUC of <b>{roc_auc_text}</b>.
The strongest model driver is <b>{top_driver}</b>, showing that credit rating quality is the
dominant available signal for identifying non-performing loans in the supplied dataset.
"""

macro_note = """
Macro variables are merged by loan origination year. They provide useful economic context for
portfolio monitoring, but they should not be interpreted as causal drivers because the supplied
loan data is not a monthly borrower-level performance panel.
"""

source_table_html = macro_sources.to_html(index=False, classes="styled-table")


# ------------------------------------------------------------
# Build professional dashboard HTML
# ------------------------------------------------------------

dashboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ABC Bank PLC Loan Portfolio Dashboard</title>
    <style>
        :root {{
            --bg: #eef2f7;
            --card: #ffffff;
            --text: #172033;
            --muted: #667085;
            --navy: #0b2545;
            --blue: #134e8a;
            --teal: #0f766e;
            --amber: #b7791f;
            --border: #d8dee9;
            --shadow: 0 8px 22px rgba(16, 24, 40, 0.10);
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: "Segoe UI", Arial, sans-serif;
            margin: 0;
            background-color: var(--bg);
            color: var(--text);
        }}

        .header {{
            background: linear-gradient(135deg, #0b2545 0%, #134e8a 55%, #0f766e 100%);
            color: white;
            padding: 28px 38px;
        }}

        .header h1 {{
            margin: 0;
            font-size: 30px;
        }}

        .header p {{
            margin: 8px 0 0 0;
            color: #dbeafe;
            font-size: 15px;
        }}

        .nav {{
            position: sticky;
            top: 0;
            z-index: 10;
            background: #ffffff;
            border-bottom: 1px solid var(--border);
            padding: 10px 35px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}

        .nav a {{
            color: var(--navy);
            text-decoration: none;
            margin-right: 18px;
            font-weight: 600;
            font-size: 14px;
        }}

        .container {{
            padding: 25px 35px 45px 35px;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section h2 {{
            color: var(--navy);
            margin-bottom: 12px;
            font-size: 23px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 18px;
        }}

        .kpi-card {{
            background: var(--card);
            border-radius: 14px;
            padding: 18px;
            box-shadow: var(--shadow);
            border: 1px solid #edf0f5;
        }}

        .kpi-card .label {{
            color: var(--muted);
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .kpi-card .value {{
            margin-top: 7px;
            font-size: 27px;
            font-weight: 800;
            color: var(--navy);
        }}

        .kpi-card .sub {{
            margin-top: 6px;
            color: var(--muted);
            font-size: 13px;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }}

        .grid-3 {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 18px;
        }}

        .card {{
            background: var(--card);
            border-radius: 14px;
            padding: 16px;
            box-shadow: var(--shadow);
            border: 1px solid #edf0f5;
            margin-bottom: 18px;
        }}

        .note {{
            background: #fffbeb;
            padding: 16px;
            border-left: 6px solid var(--amber);
            border-radius: 10px;
            color: #513c06;
            line-height: 1.5;
            margin-bottom: 18px;
        }}

        .insight {{
            background: #ecfdf3;
            padding: 16px;
            border-left: 6px solid var(--teal);
            border-radius: 10px;
            color: #064e3b;
            line-height: 1.55;
            margin-bottom: 18px;
        }}

        .model-note {{
            background: #eff6ff;
            padding: 16px;
            border-left: 6px solid var(--blue);
            border-radius: 10px;
            color: #102a56;
            line-height: 1.55;
            margin-bottom: 18px;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            background: white;
            font-size: 13px;
            margin-top: 8px;
        }}

        th, td {{
            border: 1px solid #e5e7eb;
            padding: 9px;
            text-align: left;
        }}

        th {{
            background-color: #e9eef5;
            color: #111827;
        }}

        tr:nth-child(even) {{
            background: #f9fafb;
        }}

        .footer {{
            text-align: center;
            color: var(--muted);
            font-size: 12px;
            padding: 25px;
        }}

        @media (max-width: 1100px) {{
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .grid-2, .grid-3 {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 650px) {{
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
            .container {{
                padding: 18px;
            }}
        }}
    </style>
</head>

<body>

<div class="header">
    <h1>ABC Bank PLC Loan Portfolio Dashboard</h1>
    <p>Exercise 02: Financial Sector Data Analysis | Loan book, macro context, risk drivers and anomaly monitoring</p>
</div>

<div class="nav">
    <a href="#overview">Overview</a>
    <a href="#sector">Sector Risk</a>
    <a href="#structure">Portfolio Structure</a>
    <a href="#macro">Macro Context</a>
    <a href="#drivers">Risk Drivers</a>
    <a href="#anomalies">Anomalies</a>
    <a href="#powerbi">Power BI</a>
</div>

<div class="container">

<section id="overview" class="section">
    <h2>1. Executive Overview</h2>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="label">Total Loans</div>
            <div class="value">{total_loans:,.0f}</div>
            <div class="sub">Loan-level records analysed</div>
        </div>

        <div class="kpi-card">
            <div class="label">Total Outstanding</div>
            <div class="value">Rs. {total_outstanding_mn:,.0f} Mn</div>
            <div class="sub">Institution-specific loan exposure</div>
        </div>

        <div class="kpi-card">
            <div class="label">NPL Ratio by Amount</div>
            <div class="value">{npl_ratio_amount:.2f}%</div>
            <div class="sub">Asset-quality indicator</div>
        </div>

        <div class="kpi-card">
            <div class="label">NPL Ratio by Count</div>
            <div class="value">{npl_ratio_count:.2f}%</div>
            <div class="sub">Share of loans marked non-performing</div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="label">Fully Unsecured Exposure</div>
            <div class="value">{fully_unsecured_share_amount:.2f}%</div>
            <div class="sub">Outstanding exposure share</div>
        </div>

        <div class="kpi-card">
            <div class="label">Unsecured / Partial Exposure</div>
            <div class="value">{unsecured_partial_share_amount:.2f}%</div>
            <div class="sub">Broader collateral-risk exposure</div>
        </div>

        <div class="kpi-card">
            <div class="label">Largest Sector</div>
            <div class="value">{top_sector['sector']}</div>
            <div class="sub">{top_sector['portfolio_share_pct']:.2f}% of portfolio</div>
        </div>

        <div class="kpi-card">
            <div class="label">Highest Risk Sector</div>
            <div class="value">{top_risk_sector['sector']}</div>
            <div class="sub">Composite score {top_risk_sector['composite_risk_score']:.2f}/100</div>
        </div>
    </div>

    <div class="insight">
        <b>Executive interpretation:</b> {executive_insight}
    </div>
</section>

<section id="sector" class="section">
    <h2>2. Sector Exposure and Asset Quality</h2>

    <div class="grid-2">
        <div class="card">{chart_html['sector_exposure']}</div>
        <div class="card">{chart_html['sector_npl']}</div>
    </div>

    <div class="grid-2">
        <div class="card">{chart_html['risk_score']}</div>
        <div class="card">{chart_html['risk_bubble']}</div>
    </div>

    <div class="card">{chart_html['treemap']}</div>

    <h2>Sector Risk Table</h2>
    <div class="card">
        {risk_table.to_html(index=False)}
    </div>
</section>

<section id="structure" class="section">
    <h2>3. Portfolio Structure</h2>

    <div class="grid-3">
        <div class="card">{chart_html['rating']}</div>
        <div class="card">{chart_html['collateral']}</div>
        <div class="card">{chart_html['loan_type']}</div>
    </div>

    <div class="card">{chart_html['heatmap']}</div>
</section>

<section id="macro" class="section">
    <h2>4. Macro-Financial Context</h2>

    <div class="note">
        <b>Macro interpretation note:</b> {macro_note}
    </div>

    <div class="grid-2">
        <div class="card">{chart_html['yearly']}</div>
        <div class="card">{chart_html['growth']}</div>
    </div>

    <div class="grid-2">
        <div class="card">{chart_html['macro_npl']}</div>
        <div class="card">{chart_html['exchange_policy']}</div>
    </div>

    <h2>Annual Loan-Macro Summary</h2>
    <div class="card">
        {macro_table.to_html(index=False)}
    </div>
</section>

<section id="drivers" class="section">
    <h2>5. Underlying Drivers of Risk</h2>

    <div class="model-note">
        <b>Model interpretation:</b> {model_insight}
        This is an explanatory screening model, not a production regulatory PD model.
    </div>

    <div class="card">{chart_html['features']}</div>
</section>

<section id="anomalies" class="section">
    <h2>6. Loan-Level Anomaly Watchlist</h2>

    <div class="note">
        The anomaly score prioritises loans for review using sector-relative loan size, NPL status,
        collateral risk, weak rating, large exposure flag and sector risk score.
    </div>

    <div class="card">
        {anomaly_table.to_html(index=False)}
    </div>
</section>

<section id="powerbi" class="section">
    <h2>7. Power BI / BI Tool Implementation</h2>

    <div class="card">
        <p>
            This HTML dashboard is generated using Python and Plotly. The same prepared CSV files can be loaded
            into Power BI Desktop to create a formal PBIX dashboard. A detailed Power BI measure guide is created automatically at:
        </p>
        <p><b>dashboard/powerbi_measures.md</b></p>
    </div>

    <h2>Macro Variable Source Tracking</h2>
    <div class="card">
        {source_table_html}
    </div>
</section>

<div class="footer">
    ABC Bank PLC Loan Portfolio Dashboard | Exercise 02 | Generated by scripts/07_dashboard.py
</div>

</div>
</body>
</html>
"""

dashboard_path = DASHBOARD_DIR / "abc_bank_loan_portfolio_dashboard.html"
dashboard_path.write_text(dashboard_html, encoding="utf-8")


# ------------------------------------------------------------
# Dashboard design note
# ------------------------------------------------------------

design_note = f"""
Exercise 02 - Dashboard Design Note
======================================================================

Dashboard objective:
To communicate ABC Bank PLC loan portfolio risk, exposure concentration,
asset quality, macroeconomic context, risk drivers and anomaly watchlist
to support management or supervisory decision-making.

Key KPIs:
- Total loans: {total_loans:,.0f}
- Total outstanding: Rs. {total_outstanding_mn:,.2f} Mn
- NPL ratio by amount: {npl_ratio_amount:.2f}%
- NPL ratio by count: {npl_ratio_count:.2f}%
- Fully unsecured exposure share: {fully_unsecured_share_amount:.2f}%
- Unsecured / partially secured exposure share: {unsecured_partial_share_amount:.2f}%
- Largest sector: {top_sector['sector']}
- Highest composite risk sector: {top_risk_sector['sector']}

Dashboard sections:
1. Executive Overview
2. Sector Exposure and Asset Quality
3. Portfolio Structure
4. Macro-Financial Context
5. Underlying Drivers of Risk
6. Loan-Level Anomaly Watchlist
7. Power BI / BI Tool Implementation

Visualisation justification:
- KPI cards provide immediate portfolio health indicators.
- Sector exposure charts identify concentration risk.
- NPL charts identify asset-quality pressure.
- Bubble chart combines sector concentration, NPL ratio and risk score.
- Treemap shows concentration visually.
- Rating and collateral charts explain structural portfolio risk.
- Macro charts place loan portfolio risk in economic context.
- Feature importance chart explains model-based NPL risk drivers.
- Anomaly table supports loan-level investigation.

Limitations:
The supplied dataset is loan-level origination data rather than a full monthly balance-sheet time series.
Annual portfolio growth is therefore interpreted by origination-year exposure. Macro variables are used
for contextual interpretation, not causal inference.
"""

design_note_path = LOG_DIR / "07_dashboard_design_note.txt"
design_note_path.write_text(design_note, encoding="utf-8")
