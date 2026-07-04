# CBSL Exercise 02 — Financial Sector Data Analysis

This repository contains a reproducible solution for **Exercise 02: Financial Sector Data Analysis** using the supplied ABC Bank PLC loan portfolio dataset and structured macroeconomic context.

## Current portfolio highlights

| KPI | Result |
|---|---:|
| Number of loans | 50,000 |
| Total outstanding | Rs. 164,930.23 Mn |
| NPL ratio by outstanding amount | 18.74% |
| Unsecured exposure share | 34.66% |
| Top sector by exposure | Construction (17.28%) |
| Highest composite risk sector | Infrastructure Development (80.36/100) |
| Origination-year coverage | 2015–2023 |

## Folder structure

```text
scripts/                         Reproducible ETL, EDA/KPI, dashboard scripts
outputs/                         KPI, risk, anomaly, and EDA CSV outputs
reports/                         Methodology and findings report
dashboard/                       Offline HTML dashboard and Power BI notes
data/processed/                  Cleaned loan and macro-panel datasets
```

## How to run locally

Place the supplied Excel file at:

```text
data/raw/loan_portfolio.xlsx
```

Then run:

```bash
python scripts/run_all.py
```

Open:

```text
dashboard/abc_bank_loan_dashboard.html
```

## Analytical approach

1. Extract the Excel loan book into a structured loan-level dataset.
2. Clean and validate loan IDs, dates, sector labels, collateral, ratings, performance status, and outstanding amounts.
3. Create derived variables: origination year/month, NPL flag, rating rank, and Rs. million exposure.
4. Compile structured annual macro variables for Sri Lanka and merge by year.
5. Conduct EDA across sector, loan type, collateral, rating, month, and year.
6. Calculate financial indicators: exposure, portfolio share, NPL ratio, annual growth, unsecured share, average ticket, rating quality, composite sector risk score, and anomaly score.
7. Communicate findings using an offline dashboard plus a report.

## Important interpretation note

Annual growth is calculated using outstanding exposure by loan origination year in the supplied dataset. It should be interpreted as portfolio vintage/exposure growth, not as an audited balance-sheet time series. The composite risk score is a prioritisation index for supervisory review, not a calibrated regulatory capital model.
