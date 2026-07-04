# Macro Data Source Note

The Exercise 02 guideline requires the loan portfolio analysis to incorporate macroeconomic and financial-sector variables such as GDP growth, inflation, unemployment, exchange rates, interest rates, private sector credit and financial-market indicators.

The macro-data script first attempted to extract public annual indicators from the World Bank API for Sri Lanka. During execution, the API returned timeout / 502 server errors. To ensure the analytical workflow remained reproducible within the assessment time limit, a structured fallback macro reference table was used.

The fallback values are included as public-source reference variables and should be replaced with directly downloaded CBSL / World Bank / IMF values when stable access is available. CBSL publications remain the preferred source for policy rates, private sector credit, lending rates, deposit rates and sectoral credit growth.

The macro variables are merged with the loan portfolio by loan origination year. Since the supplied loan dataset is loan-level origination data rather than a complete monthly balance-sheet time series, the macro variables are used for contextual financial-risk interpretation and not for causal inference.