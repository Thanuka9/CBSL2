"""Run the full Exercise 02 pipeline."""
import subprocess, sys

steps = [
    [sys.executable, "scripts/01_extract_clean.py", "--input", "data/raw/loan_portfolio.xlsx", "--output", "data/processed/clean_loan_portfolio.csv"],
    [sys.executable, "scripts/02_eda_indicators.py"],
    [sys.executable, "scripts/03_dashboard.py"],
]

for step in steps:
    print("\n>>>", " ".join(step))
    subprocess.check_call(step)

print("\nPipeline completed. Review outputs/ and dashboard/.")
