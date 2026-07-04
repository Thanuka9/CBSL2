"""
run_all.py

Run the complete CBSL Exercise 02 data analysis pipeline.

Usage:
    python scripts/run_all.py
"""

import subprocess
import sys
from pathlib import Path

# Root directory of the project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Python executable
PYTHON = sys.executable

# Pipeline scripts (executed in order)
PIPELINE = [
    "scripts/01_import_inspect.py",
    "scripts/01_extract_clean.py",
    "scripts/01b_raw_data_profile.py",
    "scripts/02_clean_transform.py",
    "scripts/03_create_macro_data.py",
    "scripts/04_merge_loan_macro.py",
    "scripts/05_eda_financial_indicators.py",
    "scripts/06_risk_scoring_anomalies.py",
    "scripts/07_dashboard.py",
    "scripts/08_final_report.py",
]


def run_script(script_path):
    """Run a single Python script."""
    script = PROJECT_ROOT / script_path

    if not script.exists():
        raise FileNotFoundError(f"Script not found: {script}")

    print("\n" + "=" * 80)
    print(f"Running: {script.name}")
    print("=" * 80)

    subprocess.run(
        [PYTHON, str(script)],
        cwd=PROJECT_ROOT,
        check=True,
    )

    print(f"✓ Completed: {script.name}")


def main():
    print("\n" + "=" * 80)
    print("CBSL Exercise 02 Pipeline")
    print("=" * 80)

    for script in PIPELINE:
        try:
            run_script(script)
        except subprocess.CalledProcessError as e:
            print("\n" + "=" * 80)
            print(f"Pipeline failed while running: {script}")
            print(f"Exit code: {e.returncode}")
            print("=" * 80)
            sys.exit(e.returncode)

        except Exception as e:
            print("\n" + "=" * 80)
            print(f"Error while running: {script}")
            print(e)
            print("=" * 80)
            sys.exit(1)

    print("\n" + "=" * 80)
    print("✓ PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)

    print("\nGenerated outputs include:")
    print("  • data/processed/")
    print("  • outputs/")
    print("  • reports/final_analytical_report.html")
    print("  • reports/final_analytical_report.md")
    print("  • reports/methodology_and_findings.md")
    print("  • dashboard/ (Interactive HTML Dashboard)")
    print()


if __name__ == "__main__":
    main()