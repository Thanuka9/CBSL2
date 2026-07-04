from pathlib import Path
import pandas as pd
import requests
import time

# ============================================================
# Exercise 02 - Step 03
# External macroeconomic data collection and fallback structure
#
# This script:
# 1. Attempts to fetch macro indicators from the World Bank API
# 2. Saves raw API extracts where available
# 3. Uses a documented fallback table if API access fails
# 4. Adds CBSL/public-source financial indicators
# 5. Creates a clean annual macro file for merging with loan data
# ============================================================

BASE_DIR = Path.cwd()

RAW_EXTERNAL_DIR = BASE_DIR / "data" / "external_raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

RAW_EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

START_YEAR = 2015
END_YEAR = 2024
COUNTRY_CODE = "LKA"

# ------------------------------------------------------------
# Fallback structured macro reference data
# Used only when API fetch fails or returns missing values.
# ------------------------------------------------------------

fallback_macro = pd.DataFrame([
    {
        "year": 2015,
        "sri_lanka_gdp_growth_pct": 5.0,
        "sri_lanka_inflation_pct": 3.8,
        "sri_lanka_unemployment_pct": 4.7,
        "avg_exchange_rate_lkr_usd": 135.9,
        "private_credit_by_banks_pct_gdp": 46.0,
        "policy_rate_pct": 6.00,
        "private_sector_credit_growth_pct": 25.1,
        "global_gdp_growth_pct": 3.5,
        "global_inflation_pct": 2.8,
    },
    {
        "year": 2016,
        "sri_lanka_gdp_growth_pct": 4.5,
        "sri_lanka_inflation_pct": 4.0,
        "sri_lanka_unemployment_pct": 4.4,
        "avg_exchange_rate_lkr_usd": 145.6,
        "private_credit_by_banks_pct_gdp": 49.0,
        "policy_rate_pct": 7.00,
        "private_sector_credit_growth_pct": 21.9,
        "global_gdp_growth_pct": 3.3,
        "global_inflation_pct": 2.8,
    },
    {
        "year": 2017,
        "sri_lanka_gdp_growth_pct": 3.6,
        "sri_lanka_inflation_pct": 6.6,
        "sri_lanka_unemployment_pct": 4.2,
        "avg_exchange_rate_lkr_usd": 152.5,
        "private_credit_by_banks_pct_gdp": 50.0,
        "policy_rate_pct": 7.25,
        "private_sector_credit_growth_pct": 14.7,
        "global_gdp_growth_pct": 3.8,
        "global_inflation_pct": 3.2,
    },
    {
        "year": 2018,
        "sri_lanka_gdp_growth_pct": 3.3,
        "sri_lanka_inflation_pct": 4.3,
        "sri_lanka_unemployment_pct": 4.4,
        "avg_exchange_rate_lkr_usd": 162.5,
        "private_credit_by_banks_pct_gdp": 51.0,
        "policy_rate_pct": 8.00,
        "private_sector_credit_growth_pct": 15.9,
        "global_gdp_growth_pct": 3.6,
        "global_inflation_pct": 3.6,
    },
    {
        "year": 2019,
        "sri_lanka_gdp_growth_pct": 2.3,
        "sri_lanka_inflation_pct": 4.3,
        "sri_lanka_unemployment_pct": 4.8,
        "avg_exchange_rate_lkr_usd": 178.8,
        "private_credit_by_banks_pct_gdp": 52.0,
        "policy_rate_pct": 7.00,
        "private_sector_credit_growth_pct": 4.3,
        "global_gdp_growth_pct": 2.9,
        "global_inflation_pct": 3.5,
    },
    {
        "year": 2020,
        "sri_lanka_gdp_growth_pct": -4.6,
        "sri_lanka_inflation_pct": 4.6,
        "sri_lanka_unemployment_pct": 5.5,
        "avg_exchange_rate_lkr_usd": 185.5,
        "private_credit_by_banks_pct_gdp": 56.0,
        "policy_rate_pct": 4.50,
        "private_sector_credit_growth_pct": 6.5,
        "global_gdp_growth_pct": -2.7,
        "global_inflation_pct": 3.2,
    },
    {
        "year": 2021,
        "sri_lanka_gdp_growth_pct": 3.5,
        "sri_lanka_inflation_pct": 6.0,
        "sri_lanka_unemployment_pct": 5.1,
        "avg_exchange_rate_lkr_usd": 198.9,
        "private_credit_by_banks_pct_gdp": 55.0,
        "policy_rate_pct": 5.00,
        "private_sector_credit_growth_pct": 13.1,
        "global_gdp_growth_pct": 6.5,
        "global_inflation_pct": 4.7,
    },
    {
        "year": 2022,
        "sri_lanka_gdp_growth_pct": -7.8,
        "sri_lanka_inflation_pct": 46.4,
        "sri_lanka_unemployment_pct": 4.7,
        "avg_exchange_rate_lkr_usd": 322.4,
        "private_credit_by_banks_pct_gdp": 44.0,
        "policy_rate_pct": 15.50,
        "private_sector_credit_growth_pct": 6.0,
        "global_gdp_growth_pct": 3.5,
        "global_inflation_pct": 8.7,
    },
    {
        "year": 2023,
        "sri_lanka_gdp_growth_pct": -2.3,
        "sri_lanka_inflation_pct": 17.4,
        "sri_lanka_unemployment_pct": 4.7,
        "avg_exchange_rate_lkr_usd": 327.4,
        "private_credit_by_banks_pct_gdp": 42.0,
        "policy_rate_pct": 9.00,
        "private_sector_credit_growth_pct": -1.0,
        "global_gdp_growth_pct": 3.3,
        "global_inflation_pct": 6.8,
    },
    {
        "year": 2024,
        "sri_lanka_gdp_growth_pct": 5.0,
        "sri_lanka_inflation_pct": 1.2,
        "sri_lanka_unemployment_pct": 4.4,
        "avg_exchange_rate_lkr_usd": 302.1,
        "private_credit_by_banks_pct_gdp": 43.0,
        "policy_rate_pct": 8.00,
        "private_sector_credit_growth_pct": 6.0,
        "global_gdp_growth_pct": 3.2,
        "global_inflation_pct": 5.7,
    },
])

# ------------------------------------------------------------
# World Bank API indicators
# ------------------------------------------------------------

WORLD_BANK_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "sri_lanka_gdp_growth_pct",
    "FP.CPI.TOTL.ZG": "sri_lanka_inflation_pct",
    "SL.UEM.TOTL.ZS": "sri_lanka_unemployment_pct",
    "PA.NUS.FCRF": "avg_exchange_rate_lkr_usd",
    "FS.AST.PRVT.GD.ZS": "private_credit_by_banks_pct_gdp"
}

def fetch_world_bank_indicator(country_code, indicator_code, start_year, end_year):
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}"
        f"/indicator/{indicator_code}"
        f"?format=json&per_page=1000&date={start_year}:{end_year}"
    )

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    if len(data) < 2 or data[1] is None:
        return pd.DataFrame(columns=["year", indicator_code])

    rows = []

    for item in data[1]:
        rows.append({
            "year": int(item["date"]),
            indicator_code: item["value"]
        })

    out = pd.DataFrame(rows)
    out = out.sort_values("year").reset_index(drop=True)

    return out

# ------------------------------------------------------------
# Start macro file using years only
# ------------------------------------------------------------

macro = pd.DataFrame({"year": list(range(START_YEAR, END_YEAR + 1))})
source_rows = []

for indicator_code, clean_name in WORLD_BANK_INDICATORS.items():
    api_success = False

    try:
        print(f"Fetching World Bank indicator: {indicator_code}")

        indicator_df = fetch_world_bank_indicator(
            COUNTRY_CODE,
            indicator_code,
            START_YEAR,
            END_YEAR
        )

        raw_path = RAW_EXTERNAL_DIR / f"worldbank_{indicator_code}.csv"
        indicator_df.to_csv(raw_path, index=False)

        if not indicator_df.empty and indicator_df[indicator_code].notna().sum() > 0:
            indicator_df = indicator_df.rename(columns={indicator_code: clean_name})
            macro = macro.merge(indicator_df, on="year", how="left")
            api_success = True

            source_rows.append({
                "variable": clean_name,
                "source_used": "World Bank API",
                "indicator_code": indicator_code,
                "source_url": (
                    f"https://api.worldbank.org/v2/country/{COUNTRY_CODE}"
                    f"/indicator/{indicator_code}?format=json&date={START_YEAR}:{END_YEAR}"
                ),
                "fallback_used": "No"
            })

        time.sleep(0.5)

    except Exception as e:
        print(f"Warning: API fetch failed for {indicator_code}: {e}")

    if not api_success:
        macro = macro.merge(
            fallback_macro[["year", clean_name]],
            on="year",
            how="left"
        )

        source_rows.append({
            "variable": clean_name,
            "source_used": "Structured fallback reference table",
            "indicator_code": indicator_code,
            "source_url": (
                f"https://api.worldbank.org/v2/country/{COUNTRY_CODE}"
                f"/indicator/{indicator_code}?format=json&date={START_YEAR}:{END_YEAR}"
            ),
            "fallback_used": "Yes - API unavailable or incomplete during run"
        })

# ------------------------------------------------------------
# Add CBSL/public financial-sector variables
# ------------------------------------------------------------

cbsl_cols = [
    "year",
    "policy_rate_pct",
    "private_sector_credit_growth_pct"
]

macro = macro.merge(
    fallback_macro[cbsl_cols],
    on="year",
    how="left"
)

source_rows.extend([
    {
        "variable": "policy_rate_pct",
        "source_used": "CBSL publications / structured reference table",
        "indicator_code": "Policy rate / standing facility rate context",
        "source_url": "Central Bank of Sri Lanka publications",
        "fallback_used": "Structured from public-source reference"
    },
    {
        "variable": "private_sector_credit_growth_pct",
        "source_used": "CBSL publications / structured reference table",
        "indicator_code": "Private sector credit growth",
        "source_url": "Central Bank of Sri Lanka publications",
        "fallback_used": "Structured from public-source reference"
    }
])

# ------------------------------------------------------------
# Add global macro context
# ------------------------------------------------------------

global_cols = [
    "year",
    "global_gdp_growth_pct",
    "global_inflation_pct"
]

macro = macro.merge(
    fallback_macro[global_cols],
    on="year",
    how="left"
)

source_rows.extend([
    {
        "variable": "global_gdp_growth_pct",
        "source_used": "IMF World Economic Outlook / structured reference table",
        "indicator_code": "Global GDP growth",
        "source_url": "IMF World Economic Outlook",
        "fallback_used": "Structured from public-source reference"
    },
    {
        "variable": "global_inflation_pct",
        "source_used": "IMF World Economic Outlook / structured reference table",
        "indicator_code": "Global inflation",
        "source_url": "IMF World Economic Outlook",
        "fallback_used": "Structured from public-source reference"
    }
])

# ------------------------------------------------------------
# Derived indicators
# ------------------------------------------------------------

macro = macro.sort_values("year").reset_index(drop=True)

macro["exchange_rate_yoy_change_pct"] = (
    macro["avg_exchange_rate_lkr_usd"].pct_change() * 100
)

macro["real_policy_rate_pct"] = (
    macro["policy_rate_pct"] - macro["sri_lanka_inflation_pct"]
)

macro["domestic_macro_stress_score"] = (
    macro["sri_lanka_inflation_pct"].rank(pct=True)
    + (-macro["sri_lanka_gdp_growth_pct"]).rank(pct=True)
    + macro["policy_rate_pct"].rank(pct=True)
    + macro["avg_exchange_rate_lkr_usd"].rank(pct=True)
) / 4 * 100

macro["global_macro_stress_score"] = (
    macro["global_inflation_pct"].rank(pct=True)
    + (-macro["global_gdp_growth_pct"]).rank(pct=True)
) / 2 * 100

def macro_note(year):
    if year <= 2018:
        return "Pre-crisis / normal macro period"
    elif year == 2019:
        return "Domestic shock and weaker credit conditions"
    elif year == 2020:
        return "COVID-19 contraction"
    elif year == 2021:
        return "Post-COVID recovery with rising pressure"
    elif year == 2022:
        return "Economic crisis, high inflation and exchange-rate depreciation"
    elif year == 2023:
        return "Stabilisation phase after crisis"
    elif year == 2024:
        return "Recovery phase with lower inflation"
    else:
        return "Other"

macro["macro_period_note"] = macro["year"].apply(macro_note)

# ------------------------------------------------------------
# Save outputs
# ------------------------------------------------------------

macro_path = PROCESSED_DIR / "03_macro_variables_annual.csv"
macro.to_csv(macro_path, index=False)

sources_path = OUTPUT_DIR / "03_macro_variable_sources.csv"
pd.DataFrame(source_rows).to_csv(sources_path, index=False)

notes_path = LOG_DIR / "03_macro_data_notes.txt"

notes = """
Exercise 02 - Step 03 Macro Data Notes
======================================================================

The Exercise 02 guideline requires both institution-specific loan data
and external macroeconomic / financial variables.

Source strategy:
1. World Bank API was attempted for programmatic extraction of:
   - GDP growth
   - Inflation
   - Unemployment
   - Exchange rate
   - Private credit by banks as % of GDP

2. If API calls fail because of timeout, network restriction, or server
   errors, the script uses a structured fallback reference table so the
   analysis remains reproducible during the timed assessment.

3. CBSL/publication-based financial variables are included as structured
   reference variables:
   - Policy rate
   - Private sector credit growth

4. Global macro context is included using structured IMF/global reference
   variables:
   - Global GDP growth
   - Global inflation

Important limitation:
The supplied loan portfolio is loan-level origination data. Therefore,
annual macro indicators are merged by origination year and used for
contextual financial-risk analysis, not causal inference.
"""

notes_path.write_text(notes, encoding="utf-8")

# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

missing_by_col = macro.isna().sum()
missing_path = OUTPUT_DIR / "03_macro_missing_check.csv"
missing_by_col.to_csv(missing_path, header=["missing_count"])

print("\nStep 03 macro data completed successfully.")
print(f"Macro dataset saved to: {macro_path}")
print(f"Source file saved to: {sources_path}")
print(f"Missing check saved to: {missing_path}")
print(f"Notes saved to: {notes_path}")

print("\nMacro preview:")
print(macro)

print("\nMissing values by column:")
print(missing_by_col)