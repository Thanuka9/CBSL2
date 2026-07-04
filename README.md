# CBSL Exercise 02 – Financial Sector Data Analysis

## Overview

This repository contains a complete, reproducible solution for **CBSL Exercise 02: Financial Sector Data Analysis** using the ABC Bank PLC loan portfolio dataset together with Sri Lankan macroeconomic indicators.

The project demonstrates an end-to-end data analytics workflow including:

- Data inspection and extraction
- Data cleaning and transformation
- Exploratory Data Analysis (EDA)
- Financial KPI calculation
- Macroeconomic data integration
- Risk scoring
- Anomaly detection
- Interactive dashboard generation
- Automated analytical reporting

---

# Project Structure

```text
.
├── data/
│   ├── raw/
│   │   └── loan_portfolio.xlsx
│   └── processed/
│
├── outputs/
│
├── reports/
│   ├── final_analytical_report.html
│   ├── final_analytical_report.md
│   ├── methodology_and_findings.md
│   ├── macro_data_source_note.md
│   └── open_report_and_dashboard.txt
│
├── scripts/
│   ├── 01_import_inspect.py
│   ├── 01_extract_clean.py
│   ├── 01b_raw_data_profile.py
│   ├── 02_clean_transform.py
│   ├── 03_create_macro_data.py
│   ├── 04_merge_loan_macro.py
│   ├── 05_eda_financial_indicators.py
│   ├── 06_risk_scoring_anomalies.py
│   ├── 07_dashboard.py
│   ├── 08_final_report.py
│   └── run_all.py
│
├── summary.json
├── README.md
└── requirements.txt
```

---

# Pipeline

The project executes the following workflow:

| Step | Script | Description |
|------|--------|-------------|
| 1 | `01_import_inspect.py` | Inspect the source Excel workbook |
| 2 | `01_extract_clean.py` | Extract loan data from Excel |
| 3 | `01b_raw_data_profile.py` | Generate raw data quality profile |
| 4 | `02_clean_transform.py` | Clean and transform the loan portfolio |
| 5 | `03_create_macro_data.py` | Create annual macroeconomic dataset |
| 6 | `04_merge_loan_macro.py` | Merge loan and macroeconomic data |
| 7 | `05_eda_financial_indicators.py` | Perform EDA and compute financial indicators |
| 8 | `06_risk_scoring_anomalies.py` | Calculate risk scores and identify anomalies |
| 9 | `07_dashboard.py` | Generate interactive dashboard |
| 10 | `08_final_report.py` | Produce the final analytical report |

---

# Requirements

- Python 3.10+
- pandas
- numpy
- matplotlib
- seaborn
- plotly
- openpyxl
- scipy

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Step 1

Place the supplied dataset inside

```text
data/raw/loan_portfolio.xlsx
```

---

## Step 2

Run the complete pipeline

```bash
python scripts/run_all.py
```

---

# Generated Outputs

After execution the following outputs are produced.

## Processed Data

```
data/processed/
```

Contains cleaned loan data, macroeconomic data and merged datasets.

---

## Outputs

```
outputs/
```

Contains

- Financial indicators
- EDA summaries
- Risk scores
- Anomaly detection results
- Intermediate analysis tables

---

## Reports

```
reports/
```

Contains

- Final analytical report (HTML)
- Final analytical report (Markdown)
- Methodology document
- Macroeconomic data notes

---

## Dashboard

```
dashboard/
```

Contains the interactive HTML dashboard for portfolio analysis.

---

# Analytical Workflow

The analysis consists of the following stages:

1. Inspect raw data
2. Extract Excel data
3. Profile raw data quality
4. Clean and standardize variables
5. Engineer analytical features
6. Create macroeconomic dataset
7. Merge macroeconomic indicators with loan portfolio
8. Perform exploratory data analysis
9. Calculate portfolio KPIs
10. Build composite risk scores
11. Detect statistical anomalies
12. Generate dashboard
13. Produce final analytical report

---

# Key Performance Indicators

The project calculates metrics including:

- Total Outstanding Exposure
- Non-Performing Loan (NPL) Ratio
- Sector-wise Exposure
- Loan Type Distribution
- Rating Distribution
- Collateral Coverage
- Average Loan Size
- Portfolio Growth
- Composite Risk Score
- Risk Ranking by Sector
- Statistical Anomaly Scores

---

# Methodology

The workflow follows a reproducible data analytics pipeline:

- Data Validation
- Data Cleaning
- Feature Engineering
- Exploratory Data Analysis
- Financial Indicator Calculation
- Macroeconomic Integration
- Composite Risk Scoring
- Anomaly Detection
- Data Visualization
- Automated Reporting

---

# Notes

- Annual growth is based on loan origination years rather than audited balance-sheet growth.
- Composite Risk Scores are analytical prioritization measures and should not be interpreted as regulatory capital models.
- All outputs are reproducible by rerunning the pipeline.

---