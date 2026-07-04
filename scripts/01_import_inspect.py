from pathlib import Path
import pandas as pd

# ============================================================
# Exercise 02 - Step 01
# Import and inspect the raw ABC Bank loan portfolio dataset.
# ============================================================

BASE_DIR = Path.cwd()
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Read raw file name created by 00_setup_project.py
# ------------------------------------------------------------

config_file = RAW_DIR / "raw_file_name.txt"

if config_file.exists():
    raw_file_name = config_file.read_text(encoding="utf-8").strip()
    RAW_FILE = RAW_DIR / raw_file_name
else:
    excel_files = list(RAW_DIR.glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError("No Excel file found in data/raw.")
    RAW_FILE = excel_files[0]

print(f"Reading raw Excel file: {RAW_FILE}")

# ------------------------------------------------------------
# Load Excel
# ------------------------------------------------------------

df = pd.read_excel(RAW_FILE)

print("\nRaw data loaded successfully.")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]:,}")

# ------------------------------------------------------------
# Save sample rows
# ------------------------------------------------------------

sample_path = OUTPUT_DIR / "01_raw_data_sample.csv"
df.head(20).to_csv(sample_path, index=False)

# ------------------------------------------------------------
# Prepare inspection report
# ------------------------------------------------------------

inspection_path = OUTPUT_DIR / "01_data_inspection_summary.txt"

with open(inspection_path, "w", encoding="utf-8") as f:
    f.write("Exercise 02 - ABC Bank Loan Portfolio Inspection\n")
    f.write("=" * 70 + "\n\n")

    f.write("1. Dataset Shape\n")
    f.write("-" * 70 + "\n")
    f.write(f"Rows: {df.shape[0]:,}\n")
    f.write(f"Columns: {df.shape[1]:,}\n\n")

    f.write("2. Column Names\n")
    f.write("-" * 70 + "\n")
    for col in df.columns:
        f.write(f"- {col}\n")

    f.write("\n3. Data Types\n")
    f.write("-" * 70 + "\n")
    f.write(str(df.dtypes))
    f.write("\n\n")

    f.write("4. Missing Values\n")
    f.write("-" * 70 + "\n")
    f.write(str(df.isna().sum()))
    f.write("\n\n")

    f.write("5. Duplicate Rows\n")
    f.write("-" * 70 + "\n")
    f.write(f"Duplicate rows: {df.duplicated().sum():,}\n\n")

    f.write("6. Basic Numeric Summary\n")
    f.write("-" * 70 + "\n")
    f.write(str(df.describe(include="all")))
    f.write("\n\n")

    f.write("7. Categorical Value Counts\n")
    f.write("-" * 70 + "\n")

    for col in df.select_dtypes(include="object").columns:
        f.write(f"\nColumn: {col}\n")
        f.write(str(df[col].value_counts(dropna=False).head(20)))
        f.write("\n")

print(f"\nSaved raw sample to: {sample_path}")
print(f"Saved inspection report to: {inspection_path}")
print("\nStep 01 completed successfully.")