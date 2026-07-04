from pathlib import Path
import pandas as pd

# ============================================================
# Exercise 02 - Step 08
# Final Analytical Report
#
# Purpose:
# Create a management / supervisory analytical report explaining:
# - analytical approach
# - methodology
# - data sources
# - assumptions
# - metric logic
# - risk scoring logic
# - anomaly detection logic
# - model training purpose
# - dashboard design justification
# - relationships and insights
# - limitations
# - decision-making relevance
# ============================================================

BASE_DIR = Path.cwd()

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "reports"
DASHBOARD_DIR = BASE_DIR / "dashboard"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

PANEL_PATH = PROCESSED_DIR / "04_loan_macro_panel.csv"
PORTFOLIO_SUMMARY_PATH = OUTPUT_DIR / "05_portfolio_summary.csv"
SECTOR_KPI_PATH = OUTPUT_DIR / "05_sector_kpi.csv"
YEARLY_PATH = OUTPUT_DIR / "05_yearly_trend_macro_kpi.csv"
CONCENTRATION_PATH = OUTPUT_DIR / "05_concentration_indicators.csv"
RISK_PATH = OUTPUT_DIR / "06_sector_composite_risk_score.csv"
FEATURE_PATH = OUTPUT_DIR / "06_risk_driver_feature_importance.csv"
MODEL_METRICS_PATH = OUTPUT_DIR / "06_model_metrics.txt"
MACRO_SOURCE_PATH = OUTPUT_DIR / "03_macro_variable_sources.csv"
DASHBOARD_PATH = DASHBOARD_DIR / "abc_bank_loan_portfolio_dashboard.html"

print("Reading final report inputs...")

df = pd.read_csv(PANEL_PATH)
portfolio = pd.read_csv(PORTFOLIO_SUMMARY_PATH).iloc[0]
sector = pd.read_csv(SECTOR_KPI_PATH)
yearly = pd.read_csv(YEARLY_PATH)
concentration = pd.read_csv(CONCENTRATION_PATH).iloc[0]
risk = pd.read_csv(RISK_PATH)
features = pd.read_csv(FEATURE_PATH)

if MACRO_SOURCE_PATH.exists():
    macro_sources = pd.read_csv(MACRO_SOURCE_PATH)
else:
    macro_sources = pd.DataFrame({"note": ["Macro source tracking file was not found."]})

# ------------------------------------------------------------
# Extract key values
# ------------------------------------------------------------

total_loans = int(portfolio["number_of_loans"])
total_outstanding_mn = portfolio["total_outstanding_mn_lkr"]
npl_ratio_count = portfolio["npl_ratio_count_pct"]
npl_ratio_amount = portfolio["npl_ratio_amount_pct"]
fully_unsecured_share = portfolio["fully_unsecured_share_amount_pct"]
unsecured_partial_share = portfolio["unsecured_or_partial_share_amount_pct"]
weak_rating_share = portfolio["weak_rating_share_count_pct"]
large_exposure_share = portfolio["large_exposure_share_count_pct"]

top_sector = sector.sort_values("total_outstanding_lkr", ascending=False).iloc[0]
highest_npl_sector = sector.sort_values("npl_ratio_amount_pct", ascending=False).iloc[0]
top_risk_sector = risk.sort_values("composite_risk_score", ascending=False).iloc[0]

top_3_sector_share = concentration["top_3_sector_share_pct"]
top_5_sector_share = concentration["top_5_sector_share_pct"]
sector_hhi = concentration["sector_hhi"]

top_driver = features.iloc[0]["feature"]
top_driver_importance = features.iloc[0]["importance"]

roc_auc = "Not available"

if MODEL_METRICS_PATH.exists():
    text = MODEL_METRICS_PATH.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if "ROC AUC" in line:
            roc_auc = line.replace("ROC AUC:", "").strip()
            break

yearly_min = int(yearly["year"].min())
yearly_max = int(yearly["year"].max())

worst_growth_year = yearly.dropna(subset=["annual_portfolio_growth_pct"]).sort_values(
    "annual_portfolio_growth_pct"
).iloc[0]

best_growth_year = yearly.dropna(subset=["annual_portfolio_growth_pct"]).sort_values(
    "annual_portfolio_growth_pct",
    ascending=False
).iloc[0]

macro_high_stress_year = yearly.sort_values(
    "domestic_macro_stress_score",
    ascending=False
).iloc[0]

# ------------------------------------------------------------
# Prepare report tables
# ------------------------------------------------------------

sector_report_table = sector[
    [
        "sector",
        "portfolio_share_pct",
        "npl_ratio_amount_pct",
        "average_collateral_risk_score",
        "average_rating_rank"
    ]
].copy()

sector_report_table = sector_report_table.round(2)

risk_report_table = risk[
    [
        "sector",
        "portfolio_share_pct",
        "npl_ratio_amount_pct",
        "composite_risk_score"
    ]
].copy()

risk_report_table = risk_report_table.round(2)

feature_table = features.head(10).copy()
feature_table["importance"] = feature_table["importance"].round(4)

yearly_table = yearly[
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

yearly_table = yearly_table.round(2)

macro_source_table = macro_sources.copy()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------

markdown_report = f"""
# Final Analytical Report  
## Exercise 02 — Financial Sector Data Analysis  
## ABC Bank PLC Loan Portfolio

---

## 1. Executive Summary

This report analyses the supplied ABC Bank PLC loan portfolio together with annual macroeconomic context. The analysis covers data cleaning, transformation, portfolio performance indicators, sector concentration, non-performing loan risk, underlying drivers of risk, anomaly detection and dashboard design for management or supervisory decision-making.

The final analysis-ready panel contains **{total_loans:,} loan records** and total outstanding exposure of **Rs. {total_outstanding_mn:,.2f} Mn**. The portfolio-level NPL ratio is **{npl_ratio_count:.2f}% by count** and **{npl_ratio_amount:.2f}% by amount**.

The largest exposure sector is **{top_sector['sector']}**, accounting for **{top_sector['portfolio_share_pct']:.2f}%** of the total portfolio. The highest NPL ratio by amount is observed in **{highest_npl_sector['sector']}**, while the highest composite sector risk score is assigned to **{top_risk_sector['sector']}**.

A Random Forest model was trained as an explanatory risk-driver model to identify variables associated with NPL status. The model achieved ROC AUC of **{roc_auc}**, with **{top_driver}** emerging as the most important driver.

---

## 2. Analytical Objective

The objective of the analysis is to support financial sector monitoring and decision-making by:

1. Preparing a clean and analysis-ready loan portfolio dataset.
2. Integrating loan-level data with external macroeconomic and financial-sector variables.
3. Calculating relevant portfolio performance and risk indicators.
4. Identifying sector-level risk concentrations.
5. Detecting loans and sectors that may warrant further examination.
6. Developing an interactive dashboard and reporting framework for management or supervisory use.

---

## 3. Data Sources

### 3.1 Institution-Specific Loan Data

The primary dataset is the supplied ABC Bank PLC loan portfolio. It contains loan-level information including loan origination date, sector, loan type, collateral, initial rating, performance status and outstanding amount.

### 3.2 External Macro and Financial Variables

The external data process attempted to collect annual macroeconomic indicators from the World Bank API. When the API returned server or timeout errors, a structured fallback reference table was used to preserve reproducibility. CBSL/publication-based variables such as policy rate and private-sector credit growth were included as structured public-source variables.

Macro variables include:

- GDP growth
- Inflation
- Unemployment
- Exchange rate
- Policy rate
- Private-sector credit growth
- Private credit by banks as percentage of GDP
- Global GDP growth
- Global inflation
- Domestic macro stress score
- Global macro stress score

---

## 4. Data Preparation Methodology

The workflow followed these steps:

1. Imported and inspected the raw Excel file.
2. Standardised column names and category labels.
3. Corrected spelling inconsistencies such as Telecommumication to Telecommunication.
4. Standardised performance status into Performing and Non-Performing.
5. Created date fields such as year, month and quarter.
6. Created risk features including NPL flag, rating rank, weak rating flag, collateral risk score and large exposure flag.
7. Created annual macroeconomic context variables.
8. Merged loan data with macro variables by origination year.
9. Created EDA outputs, financial indicators, risk scores, anomaly watchlists and dashboard files.

---

## 5. Key Metrics and Logic

### NPL Ratio by Count

`NPL Ratio by Count = Number of Non-Performing Loans / Total Loans × 100`

### NPL Ratio by Amount

`NPL Ratio by Amount = Non-Performing Outstanding Amount / Total Outstanding Amount × 100`

This is important because a small number of large non-performing loans can create material balance-sheet risk.

### Annual Portfolio Growth

`Annual Growth = Current Year Exposure / Previous Year Exposure - 1`

Because the dataset is origination-level loan data rather than a complete monthly balance-sheet series, annual growth is interpreted as origination-year exposure movement.

### Sector Concentration

The top 3 sectors account for **{top_3_sector_share:.2f}%** of the portfolio, while the top 5 sectors account for **{top_5_sector_share:.2f}%**. The sector HHI is **{sector_hhi:.2f}**.

### Collateral Risk

Collateral categories were used as a simplified risk proxy:

- Secured = lower collateral risk
- Partially secured = medium collateral risk
- Unsecured = higher collateral risk

The portfolio has **{fully_unsecured_share:.2f}%** fully unsecured exposure by amount and **{unsecured_partial_share:.2f}%** unsecured or partially secured exposure by amount.

### Rating Risk

Initial rating was converted into a rating rank. Weaker ratings receive higher rank values. Loans rated BB, B and CCC were flagged as weak-rated loans.

Weak-rated loans account for **{weak_rating_share:.2f}%** of loan count.

---

## 6. Composite Sector Risk Score

A composite sector risk score was created to prioritise sectors for review.

The score combines:

- 45% NPL ratio by amount
- 25% collateral risk
- 20% rating weakness
- 10% portfolio concentration

This score is not a regulatory capital model. It is a management and supervisory prioritisation index.

The highest composite risk sector is **{top_risk_sector['sector']}**, with a score of **{top_risk_sector['composite_risk_score']:.2f}/100**.

---

## 7. Underlying Risk Drivers

A Random Forest classifier was trained with `is_npl` as the target variable. The purpose was not to create a production credit-risk model but to identify variables associated with NPL status.

Model result:

- ROC AUC: **{roc_auc}**
- Top driver: **{top_driver}**
- Top driver importance: **{top_driver_importance:.4f}**

The model suggests that loan rating quality is the strongest available indicator of NPL risk in the supplied dataset.

---

## 8. Anomaly Detection Logic

Loan-level anomalies were identified using a composite anomaly score.

The score combines:

- Sector-relative loan size
- NPL status
- Unsecured or partially secured collateral
- Weak rating
- Large exposure flag
- Sector composite risk score

The anomaly watchlist is a prioritised review list for management or supervisory follow-up.

---

## 9. Relationships and Insights

1. The largest sector by exposure is **{top_sector['sector']}**.
2. The highest NPL ratio by amount is observed in **{highest_npl_sector['sector']}**, with an NPL ratio of **{highest_npl_sector['npl_ratio_amount_pct']:.2f}%**.
3. The model identifies **{top_driver}** as the strongest available NPL risk driver.
4. A significant portion of the portfolio is unsecured or partially secured.
5. The highest domestic macro stress score is observed in **{int(macro_high_stress_year['year'])}**.
6. The strongest annual portfolio growth occurred in **{int(best_growth_year['year'])}**, with growth of **{best_growth_year['annual_portfolio_growth_pct']:.2f}%**.
7. The weakest annual movement occurred in **{int(worst_growth_year['year'])}**, with growth of **{worst_growth_year['annual_portfolio_growth_pct']:.2f}%**.

---

## 10. Dashboard Design and Visualisation Justification

The dashboard was designed for management and supervisory decision-making.

Selected visuals and justification:

1. KPI cards provide immediate portfolio health indicators.
2. Sector exposure charts identify concentration risk.
3. Sector NPL charts identify asset-quality pressure.
4. Composite risk score charts prioritise sectors for further examination.
5. Bubble charts show the relationship between concentration, NPL ratio and risk score.
6. Treemap shows exposure concentration visually.
7. Rating, collateral and loan type charts explain structural portfolio risk.
8. Macro charts place portfolio performance in economic context.
9. Feature importance charts communicate underlying NPL risk drivers.
10. Anomaly tables provide a loan-level review list.

---

## 11. Assumptions

The analysis is based on the following assumptions:

1. The supplied ABC Bank PLC loan portfolio represents the intended loan population for this assessment.
2. Outstanding amount is treated as the main exposure measure.
3. Performance status is assumed to correctly classify loans as Performing or Non-Performing.
4. Annual macroeconomic indicators are merged using loan origination year.
5. Macro variables are used for contextual interpretation, not causal inference.
6. Initial rating is assumed to represent relative loan or borrower credit quality.
7. Collateral category is used as a simplified proxy for collateral protection.
8. Large exposures are defined using the 95th percentile of outstanding amount.
9. The composite sector risk score is a prioritisation index, not a regulatory capital model.
10. The anomaly score supports review prioritisation and is not a fraud detection model.
11. The Random Forest model identifies risk drivers and is not a production probability-of-default model.
12. Because external API calls returned timeout or server errors, structured public-source reference values were used to preserve reproducibility.

---

## 12. Limitations

Important limitations include:

1. The dataset does not contain borrower income, repayment history, days past due, collateral valuation, recovery amount or maturity date.
2. The dataset is loan-level origination data, not a monthly loan performance panel.
3. Annual growth is based on origination-year exposure, not full balance-sheet stock movement.
4. Macro variables are annual and may not capture intra-year stress.
5. The macro API failed during execution, so structured reference values were used for workflow continuity.
6. The Random Forest model is explanatory and should not be used as a production probability-of-default model.
7. Anomaly detection is rule-based and prioritisation-oriented, not fraud detection.

---

## 13. Decision-Making Relevance

The analysis supports decision-making by helping users:

- Identify high-exposure sectors.
- Monitor NPL concentration.
- Prioritise high-risk sectors for review.
- Understand drivers of NPL risk.
- Investigate large, weakly rated or insufficiently secured loans.
- Interpret portfolio risk in macroeconomic context.
- Communicate findings through an interactive dashboard.

---

## 14. Recommended Further Examination

The following areas warrant further review:

1. **{top_risk_sector['sector']}** due to highest composite sector risk.
2. **{highest_npl_sector['sector']}** due to highest NPL ratio by amount.
3. Large exposures with weak ratings and unsecured or partially secured collateral.
4. Loans in sectors with both high exposure and above-average NPL ratios.
5. Financial-sector loans because the dataset reports 0.00% NPL despite high exposure, which should be validated.
6. Macro-sensitive years with high domestic stress scores.

---

## 15. Deliverables Created

The workflow created:

- Cleaned loan portfolio dataset
- External macro variable dataset
- Loan-macro analysis panel
- Portfolio KPI outputs
- Sector KPI outputs
- Annual trend outputs
- Composite sector risk score
- Risk-driver model outputs
- Anomaly watchlist
- Interactive HTML dashboard
- Power BI implementation guide
- Final analytical report

---

## 16. Conclusion

The analysis provides a complete financial-sector monitoring workflow for ABC Bank PLC's loan portfolio. It combines data cleaning, portfolio risk metrics, sector concentration analysis, macro context, risk-driver modelling, anomaly detection and dashboard communication. The results indicate that credit rating quality, collateral weakness, sector concentration and sector-level NPL ratios are key areas for supervisory and management attention.
"""

# ------------------------------------------------------------
# HTML report
# ------------------------------------------------------------

html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Final Analytical Report - ABC Bank PLC Loan Portfolio</title>
    <style>
        body {{
            font-family: "Segoe UI", Arial, sans-serif;
            margin: 0;
            background: #f4f6f8;
            color: #172033;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #0b2545 0%, #134e8a 60%, #0f766e 100%);
            color: white;
            padding: 32px 42px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
        }}
        .header p {{
            margin-top: 8px;
            color: #dbeafe;
        }}
        .container {{
            max-width: 1180px;
            margin: auto;
            padding: 28px;
        }}
        .card {{
            background: white;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 22px;
            box-shadow: 0 8px 22px rgba(16,24,40,0.08);
        }}
        h2 {{
            color: #0b2545;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 6px;
        }}
        h3 {{
            color: #134e8a;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin: 18px 0;
        }}
        .kpi {{
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
        }}
        .kpi .label {{
            color: #667085;
            font-size: 13px;
            font-weight: 600;
        }}
        .kpi .value {{
            color: #0b2545;
            font-size: 24px;
            font-weight: 800;
            margin-top: 6px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #e5e7eb;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background: #e9eef5;
        }}
        tr:nth-child(even) {{
            background: #f9fafb;
        }}
        .note {{
            background: #fffbeb;
            border-left: 6px solid #b7791f;
            padding: 14px;
            border-radius: 10px;
        }}
        .good {{
            background: #ecfdf3;
            border-left: 6px solid #0f766e;
            padding: 14px;
            border-radius: 10px;
        }}
        .footer {{
            text-align: center;
            color: #667085;
            font-size: 12px;
            padding: 25px;
        }}
        code {{
            background: #f1f5f9;
            padding: 2px 5px;
            border-radius: 5px;
        }}
        @media (max-width: 900px) {{
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>

<body>

<div class="header">
    <h1>Final Analytical Report</h1>
    <p>Exercise 02 — ABC Bank PLC Financial Sector Data Analysis</p>
</div>

<div class="container">

<div class="card">
    <h2>1. Executive Summary</h2>
    <p>
        This report analyses the supplied ABC Bank PLC loan portfolio together with annual macroeconomic context.
        The analysis covers data cleaning, transformation, portfolio performance indicators, sector concentration,
        non-performing loan risk, underlying drivers of risk, anomaly detection and dashboard design.
    </p>

    <div class="kpi-grid">
        <div class="kpi"><div class="label">Total Loans</div><div class="value">{total_loans:,}</div></div>
        <div class="kpi"><div class="label">Total Outstanding</div><div class="value">Rs. {total_outstanding_mn:,.0f} Mn</div></div>
        <div class="kpi"><div class="label">NPL Ratio by Amount</div><div class="value">{npl_ratio_amount:.2f}%</div></div>
        <div class="kpi"><div class="label">NPL Ratio by Count</div><div class="value">{npl_ratio_count:.2f}%</div></div>
    </div>

    <p>
        The largest exposure sector is <b>{top_sector['sector']}</b>, accounting for
        <b>{top_sector['portfolio_share_pct']:.2f}%</b> of total exposure.
        The highest composite risk sector is <b>{top_risk_sector['sector']}</b>.
        The model-based top risk driver is <b>{top_driver}</b>.
    </p>
</div>

<div class="card">
    <h2>2. Analytical Objective</h2>
    <p>
        The objective of the analysis is to support financial sector monitoring and decision-making by preparing
        a clean loan portfolio dataset, integrating it with macroeconomic context, calculating financial indicators,
        identifying risks, detecting anomalies and communicating insights through an interactive dashboard.
    </p>
</div>

<div class="card">
    <h2>3. Data Sources</h2>
    <h3>Institution-Specific Loan Data</h3>
    <p>
        The primary dataset is the supplied ABC Bank PLC loan portfolio. It contains loan-level information including
        loan origination date, sector, loan type, collateral, initial rating, performance status and outstanding amount.
    </p>

    <h3>External Macro and Financial Variables</h3>
    <p>
        The external data process attempted to collect annual macroeconomic indicators from the World Bank API.
        When the API returned server or timeout errors, a structured fallback reference table was used to preserve
        reproducibility. CBSL/publication-based variables such as policy rate and private-sector credit growth were
        included as structured public-source variables.
    </p>
</div>

<div class="card">
    <h2>4. Data Preparation Methodology</h2>
    <ol>
        <li>Imported and inspected the raw Excel file.</li>
        <li>Standardised column names and category labels.</li>
        <li>Corrected spelling inconsistencies such as Telecommumication to Telecommunication.</li>
        <li>Standardised performance status into Performing and Non-Performing.</li>
        <li>Created date fields such as year, month and quarter.</li>
        <li>Created risk features including NPL flag, rating rank, weak rating flag, collateral risk score and large exposure flag.</li>
        <li>Created annual macroeconomic context variables.</li>
        <li>Merged loan data with macro variables by origination year.</li>
        <li>Created EDA outputs, financial indicators, risk scores, anomaly watchlists and dashboard files.</li>
    </ol>
</div>

<div class="card">
    <h2>5. Metrics, Logic and Performance Measures</h2>

    <h3>NPL Ratio by Count</h3>
    <p><code>NPL Count / Total Loans × 100</code></p>

    <h3>NPL Ratio by Amount</h3>
    <p><code>Non-Performing Outstanding Amount / Total Outstanding Amount × 100</code></p>

    <h3>Annual Portfolio Growth</h3>
    <p><code>Current Year Outstanding / Previous Year Outstanding - 1</code></p>

    <h3>Sector Concentration</h3>
    <p>
        Top 3 sectors account for <b>{top_3_sector_share:.2f}%</b> of exposure.
        Top 5 sectors account for <b>{top_5_sector_share:.2f}%</b>.
        Sector HHI is <b>{sector_hhi:.2f}</b>.
    </p>

    <h3>Collateral and Rating Risk</h3>
    <p>
        Fully unsecured exposure is <b>{fully_unsecured_share:.2f}%</b> by amount.
        Unsecured or partially secured exposure is <b>{unsecured_partial_share:.2f}%</b> by amount.
        Weak-rated loans account for <b>{weak_rating_share:.2f}%</b> of loan count.
    </p>
</div>

<div class="card">
    <h2>6. Composite Sector Risk Score</h2>
    <p>
        The composite risk score combines NPL ratio by amount, collateral risk, rating weakness and portfolio concentration.
        It is used to prioritise sectors for management or supervisory review.
    </p>
    <p><code>Composite Risk Score = 45% NPL Risk + 25% Collateral Risk + 20% Rating Weakness + 10% Concentration Risk</code></p>
    <p>
        The highest composite risk sector is <b>{top_risk_sector['sector']}</b>, with a score of
        <b>{top_risk_sector['composite_risk_score']:.2f}/100</b>.
    </p>
</div>

<div class="card">
    <h2>7. Underlying Risk Drivers</h2>
    <p>
        A Random Forest classifier was trained with <code>is_npl</code> as the target variable. The purpose was to identify
        variables associated with NPL status, not to create a production probability-of-default model.
    </p>
    <p>
        Model ROC AUC: <b>{roc_auc}</b><br>
        Top risk driver: <b>{top_driver}</b><br>
        Top driver importance: <b>{top_driver_importance:.4f}</b>
    </p>
    {feature_table.to_html(index=False)}
</div>

<div class="card">
    <h2>8. Anomaly Detection Logic</h2>
    <p>
        Loan-level anomalies were identified using a composite anomaly score. The score combines sector-relative loan size,
        NPL status, unsecured or partially secured collateral, weak rating, large exposure flag and sector composite risk score.
    </p>
    <p>
        The anomaly watchlist is a review-prioritisation tool for management or supervisory follow-up.
    </p>
</div>

<div class="card">
    <h2>9. Relationships and Insights</h2>
    <ul>
        <li>The largest sector by exposure is <b>{top_sector['sector']}</b>.</li>
        <li>The highest NPL ratio by amount is in <b>{highest_npl_sector['sector']}</b> at <b>{highest_npl_sector['npl_ratio_amount_pct']:.2f}%</b>.</li>
        <li>The model identifies <b>{top_driver}</b> as the strongest available NPL risk driver.</li>
        <li><b>{unsecured_partial_share:.2f}%</b> of exposure is unsecured or partially secured.</li>
        <li>The highest domestic macro stress score is observed in <b>{int(macro_high_stress_year['year'])}</b>.</li>
        <li>The strongest annual portfolio growth occurred in <b>{int(best_growth_year['year'])}</b>, with growth of <b>{best_growth_year['annual_portfolio_growth_pct']:.2f}%</b>.</li>
        <li>The weakest annual movement occurred in <b>{int(worst_growth_year['year'])}</b>, with growth of <b>{worst_growth_year['annual_portfolio_growth_pct']:.2f}%</b>.</li>
    </ul>
</div>

<div class="card">
    <h2>10. Dashboard Design and Visualisation Justification</h2>
    <ul>
        <li>KPI cards provide immediate portfolio health indicators.</li>
        <li>Sector exposure charts identify concentration risk.</li>
        <li>NPL charts identify asset-quality pressure.</li>
        <li>Composite risk score charts prioritise sectors for further examination.</li>
        <li>Bubble charts show the relationship between concentration, NPL ratio and risk score.</li>
        <li>Treemap shows exposure concentration visually.</li>
        <li>Rating, collateral and loan type charts explain structural portfolio risk.</li>
        <li>Macro charts place portfolio performance in economic context.</li>
        <li>Feature importance charts communicate underlying NPL risk drivers.</li>
        <li>Anomaly tables provide a loan-level review list.</li>
    </ul>
</div>

<div class="card">
    <h2>11. Assumptions</h2>

    <p>The analysis is based on the following assumptions:</p>

    <ol>
        <li>
            <b>Loan portfolio completeness:</b>
            The supplied ABC Bank PLC loan portfolio is assumed to represent the intended loan population for this assessment.
        </li>

        <li>
            <b>Outstanding amount as exposure:</b>
            The field <code>amount_outstanding_lkr</code> is treated as the main exposure measure for portfolio size, concentration, NPL exposure and risk analysis.
        </li>

        <li>
            <b>Performance status as asset-quality target:</b>
            The field <code>performance_status</code> is assumed to correctly classify loans as Performing or Non-Performing.
        </li>

        <li>
            <b>Origination year for macro merge:</b>
            Annual macroeconomic indicators are merged using loan origination year. This assumes that macro conditions in the origination year provide useful context for interpreting portfolio risk.
        </li>

        <li>
            <b>Macro variables are contextual:</b>
            GDP growth, inflation, unemployment, exchange rate, policy rate and macro stress scores are used for contextual interpretation, not causal inference.
        </li>

        <li>
            <b>Rating rank as credit-quality proxy:</b>
            Initial rating is assumed to represent relative borrower or loan credit quality. Weaker ratings are treated as higher-risk categories.
        </li>

        <li>
            <b>Collateral category as protection proxy:</b>
            Collateral type is used as a simplified proxy for collateral protection. Secured loans are treated as lower collateral-risk than partially secured or unsecured loans.
        </li>

        <li>
            <b>Large exposure threshold:</b>
            Large exposures are defined using the 95th percentile of outstanding amount. This is a portfolio-based threshold created for review prioritisation.
        </li>

        <li>
            <b>Composite risk score purpose:</b>
            The composite sector risk score is assumed to be a management and supervisory prioritisation index. It is not a regulatory capital model.
        </li>

        <li>
            <b>Anomaly score purpose:</b>
            The loan anomaly score is assumed to support review prioritisation. It is not a fraud detection model.
        </li>

        <li>
            <b>Model purpose:</b>
            The Random Forest model is used to identify risk drivers associated with NPL status. It is not treated as a production probability-of-default model.
        </li>

        <li>
            <b>Structured macro fallback:</b>
            Because external API calls returned timeout or server errors during execution, structured public-source reference values were used to preserve reproducibility. These should be replaced with directly downloaded CBSL / World Bank / IMF values when stable access is available.
        </li>
    </ol>
</div>

<div class="card">
    <h2>12. Sector KPI Table</h2>
    {sector_report_table.to_html(index=False)}
</div>

<div class="card">
    <h2>13. Composite Sector Risk Table</h2>
    {risk_report_table.to_html(index=False)}
</div>

<div class="card">
    <h2>14. Annual Loan-Macro Summary</h2>
    {yearly_table.to_html(index=False)}
</div>

<div class="card">
    <h2>15. Data Sources and Source Tracking</h2>
    {macro_source_table.to_html(index=False)}
</div>

<div class="card">
    <h2>16. Limitations</h2>
    <ul>
        <li>The dataset does not include borrower income, repayment history, days past due, collateral values or recovery data.</li>
        <li>The dataset is loan-level origination data, not a monthly balance-sheet time series.</li>
        <li>Annual growth is interpreted using origination-year exposure.</li>
        <li>Macro variables are annual and may not capture intra-year stress.</li>
        <li>The macro API failed during execution, so structured reference values were used for workflow continuity.</li>
        <li>The Random Forest model is explanatory, not a production probability-of-default model.</li>
        <li>The anomaly score is a review-prioritisation tool, not a fraud detection model.</li>
    </ul>
</div>

<div class="card">
    <h2>17. Decision-Making Relevance</h2>
    <p>The analysis supports decision-making by helping users:</p>
    <ul>
        <li>Identify high-exposure sectors.</li>
        <li>Monitor NPL concentration.</li>
        <li>Prioritise high-risk sectors for review.</li>
        <li>Understand drivers of NPL risk.</li>
        <li>Investigate large, weakly rated or insufficiently secured loans.</li>
        <li>Interpret portfolio risk in macroeconomic context.</li>
        <li>Communicate findings through an interactive dashboard.</li>
    </ul>
</div>

<div class="card">
    <h2>18. Recommendations for Further Examination</h2>
    <ol>
        <li>Review <b>{top_risk_sector['sector']}</b> due to its highest composite sector risk score.</li>
        <li>Review <b>{highest_npl_sector['sector']}</b> due to its high NPL ratio by amount.</li>
        <li>Investigate large exposures with weak ratings and unsecured or partially secured collateral.</li>
        <li>Validate Financial Sector loans because the dataset reports 0.00% NPL despite high exposure.</li>
        <li>Monitor loans originated during years with high domestic macro stress.</li>
    </ol>
</div>

<div class="card">
    <h2>19. Conclusion</h2>
    <p>
        The analysis provides a complete financial-sector monitoring workflow for ABC Bank PLC's loan portfolio.
        It combines data cleaning, portfolio risk metrics, sector concentration analysis, macro context,
        risk-driver modelling, anomaly detection and dashboard communication.
    </p>
    <p>
        The results indicate that credit rating quality, collateral weakness, sector concentration and sector-level
        NPL ratios are key areas for supervisory and management attention.
    </p>
</div>

</div>

<div class="footer">
    Final Analytical Report | Exercise 02 | Generated by scripts/08_final_report.py
</div>

</body>
</html>
"""

# ------------------------------------------------------------
# Save report files
# ------------------------------------------------------------

md_path = REPORT_DIR / "final_analytical_report.md"
html_path = REPORT_DIR / "final_analytical_report.html"

md_path.write_text(markdown_report, encoding="utf-8")
html_path.write_text(html_report, encoding="utf-8")

# ------------------------------------------------------------
# Open-file note
# ------------------------------------------------------------

link_note_path = REPORT_DIR / "open_report_and_dashboard.txt"

link_note = f"""
Open these files for final review:

1. Interactive Dashboard:
{DASHBOARD_PATH}

2. Final Analytical Report:
{html_path}

3. Markdown Report:
{md_path}
"""

link_note_path.write_text(link_note, encoding="utf-8")

print("\nStep 08 final analytical report completed successfully.")
print(f"Markdown report saved to: {md_path}")
print(f"HTML report saved to: {html_path}")
print(f"Open-file note saved to: {link_note_path}")