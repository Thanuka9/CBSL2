# Exercise 02: Financial Sector Data Analysis — Methodology and Findings

## Objective

Analyse ABC Bank PLC's loan portfolio across economic sectors and combine institution-specific loan data with relevant macroeconomic variables to support financial-sector monitoring, management review, and supervisory decision-making.

## Data extraction and structuring

The supplied Excel workbook contains 50,000 loan records with loan ID, originating date, sector, loan type, collateral, initial rating, performance status, and amount outstanding. The workflow converts the workbook into a clean loan-level CSV and adds derived fields: year, month, NPL flag, rating rank, and Rs. million exposure.

A structured annual macro table is included for GDP growth, inflation, unemployment, exchange rate, and placeholders for policy/credit variables. In a live assessment environment, the same structure can be refreshed from CBSL/public statistical tables and joined to the loan book by year.

## Cleaning and validation

The ETL pipeline applies these controls:

- duplicate loan IDs removed;
- Excel serial dates converted to ISO dates;
- `Telecommumication` standardised to `Telecommunication`;
- collateral standardised as `Secured` / `Unsecured`;
- `Non Performing` converted to `Non-Performing`;
- ratings mapped to ordinal risk ranks;
- NPL encoded as binary `is_npl`;
- outstanding amount represented in LKR and Rs. million;
- validation checks for unique loan IDs, non-negative exposure, and valid NPL flags.

## Key findings

| KPI | Result |
|---|---:|
| Number of loans | 50,000 |
| Total outstanding | Rs. 164,930.23 Mn |
| NPL ratio by outstanding amount | 18.74% |
| Unsecured exposure share | 34.66% |
| Largest sector by exposure | Construction, 17.28% |
| Highest composite risk sector | Infrastructure Development, 80.36/100 |

## Indicators calculated

The solution calculates total outstanding, portfolio share, NPL ratio by amount, annual growth by origination-year exposure, unsecured share, average ticket size, average rating rank, composite sector risk score, and an anomaly score.

Composite sector risk score weights: 45% NPL ratio, 25% unsecured share, 20% average rating rank, and 10% portfolio concentration. The score is a prioritisation index for review, not a regulatory capital measure.

## Anomaly detection

The anomaly watchlist combines sector-level amount z-score, NPL status, unsecured collateral, and weak rating. This highlights loans that are unusually large within their sector and also carry additional credit-risk flags.

## Dashboard design

The dashboard uses KPI cards, sector exposure bars, risk-score rankings, annual macro/portfolio tables, risk-driver tables, and a searchable anomaly watchlist. These visualisations are selected because they directly support management and supervisory questions: where is exposure concentrated, where is asset quality weaker, what sectors need review, and which individual loans should be examined first.

## Limitations

- The supplied dataset appears to be point-in-time/origination-level rather than a full audited balance-sheet time series.
- Annual growth is therefore interpreted as origination-year exposure/vintage growth, not official total loan-book growth.
- Macro variables are annual, so within-year shocks are not captured.
- Borrower-level income, days-past-due, collateral valuation, recovery, and repayment history were not provided.
- The risk score is interpretable but not calibrated as PD/LGD/ECL.

## Recommendations

1. Prioritise review of Infrastructure Development, Energy, Healthcare, and Agriculture because they have the highest composite risk scores.
2. Review high-value anomalies, especially loans combining non-performing status, unsecured collateral, weak ratings, and unusually large sector-relative exposure.
3. Monitor sectors with both high exposure concentration and elevated NPL ratios.
4. Refresh macro data from CBSL/public sources and compare loan-sector risk against GDP, inflation, exchange rate, interest rates, and private-sector credit growth.
5. Extend to Power BI using the documented DAX measures for a formal BI submission.
