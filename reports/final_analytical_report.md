
# Final Analytical Report  
## Exercise 02 — Financial Sector Data Analysis  
## ABC Bank PLC Loan Portfolio

---

## 1. Executive Summary

This report analyses the supplied ABC Bank PLC loan portfolio together with annual macroeconomic context. The analysis covers data cleaning, transformation, portfolio performance indicators, sector concentration, non-performing loan risk, underlying drivers of risk, anomaly detection and dashboard design for management or supervisory decision-making.

The final analysis-ready panel contains **50,000 loan records** and total outstanding exposure of **Rs. 164,930.23 Mn**. The portfolio-level NPL ratio is **20.63% by count** and **18.74% by amount**.

The largest exposure sector is **Construction**, accounting for **17.28%** of the total portfolio. The highest NPL ratio by amount is observed in **Agriculture**, while the highest composite sector risk score is assigned to **Energy**.

A Random Forest model was trained as an explanatory risk-driver model to identify variables associated with NPL status. The model achieved ROC AUC of **0.8737**, with **rating_rank** emerging as the most important driver.

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

The top 3 sectors account for **47.02%** of the portfolio, while the top 5 sectors account for **71.17%**. The sector HHI is **1240.68**.

### Collateral Risk

Collateral categories were used as a simplified risk proxy:

- Secured = lower collateral risk
- Partially secured = medium collateral risk
- Unsecured = higher collateral risk

The portfolio has **34.66%** fully unsecured exposure by amount and **54.81%** unsecured or partially secured exposure by amount.

### Rating Risk

Initial rating was converted into a rating rank. Weaker ratings receive higher rank values. Loans rated BB, B and CCC were flagged as weak-rated loans.

Weak-rated loans account for **45.91%** of loan count.

---

## 6. Composite Sector Risk Score

A composite sector risk score was created to prioritise sectors for review.

The score combines:

- 45% NPL ratio by amount
- 25% collateral risk
- 20% rating weakness
- 10% portfolio concentration

This score is not a regulatory capital model. It is a management and supervisory prioritisation index.

The highest composite risk sector is **Energy**, with a score of **72.40/100**.

---

## 7. Underlying Risk Drivers

A Random Forest classifier was trained with `is_npl` as the target variable. The purpose was not to create a production credit-risk model but to identify variables associated with NPL status.

Model result:

- ROC AUC: **0.8737**
- Top driver: **rating_rank**
- Top driver importance: **0.4956**

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

1. The largest sector by exposure is **Construction**.
2. The highest NPL ratio by amount is observed in **Agriculture**, with an NPL ratio of **24.94%**.
3. The model identifies **rating_rank** as the strongest available NPL risk driver.
4. A significant portion of the portfolio is unsecured or partially secured.
5. The highest domestic macro stress score is observed in **2022**.
6. The strongest annual portfolio growth occurred in **2020**, with growth of **7.42%**.
7. The weakest annual movement occurred in **2018**, with growth of **-5.74%**.

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

1. **Energy** due to highest composite sector risk.
2. **Agriculture** due to highest NPL ratio by amount.
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
