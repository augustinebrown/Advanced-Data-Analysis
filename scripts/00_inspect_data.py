# 00_inspect_data.py
# Purpose: look at the two raw data files and print basic facts about them.
# This script ONLY reads and prints. It does not clean, change or save any data.
# Run from the project folder with:  uv run python scripts/00_inspect_data.py

from pathlib import Path

import pandas as pd

# Find the data/raw folder, starting from where this script is saved
# (scripts/ -> project folder -> data/raw), so the script works from any folder.
PROJECT_FOLDER = Path(__file__).parent.parent
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw"

# If a text column has more unique values than this, print only a sample of them
# instead of the full list, so the output stays readable.
MAX_VALUES_TO_LIST = 40


def inspect_file(file_name):
    """Print a basic summary of one raw CSV file."""

    # Print a header so it is clear which file the output below belongs to
    print("=" * 70)
    print("FILE:", file_name)
    print("=" * 70)

    # Read the CSV file into a table (a pandas "DataFrame").
    # Reading does not change the file on disk.
    data = pd.read_csv(RAW_FOLDER / file_name)

    # 1. Size: how many rows (observations) and columns (variables)
    print("\n--- 1. Size ---")
    print("Rows:", len(data))
    print("Columns:", len(data.columns))
    print("Column names:", list(data.columns))

    # 2. Date range: earliest and latest value in the REF_DATE column.
    # Dates are stored as text like "2015-01", which sorts correctly as text.
    print("\n--- 2. Date range ---")
    print("First date:", data["REF_DATE"].min())
    print("Last date:", data["REF_DATE"].max())
    print("Number of different dates:", data["REF_DATE"].nunique())

    # 3. Unique values of each text (non-number) column
    print("\n--- 3. Unique values in each text column ---")
    for column in data.columns:
        # Skip number columns (such as VALUE); we only want text columns here
        if pd.api.types.is_numeric_dtype(data[column]):
            continue

        # Get the list of different values in this column (blanks not included)
        unique_values = data[column].dropna().unique()
        print(f"\n{column}: {len(unique_values)} unique values")

        # Print every value if the list is short, otherwise just the first few
        if len(unique_values) <= MAX_VALUES_TO_LIST:
            for value in unique_values:
                print("   ", value)
        else:
            print("    (too many to list; first 10 shown)")
            for value in unique_values[:10]:
                print("   ", value)

    # 4. Missing values: how many blank cells are in each column
    print("\n--- 4. Missing values per column ---")
    print(data.isna().sum().to_string())

    # 5. Duplicates: rows that are exactly the same as another row
    print("\n--- 5. Duplicate rows ---")
    print("Number of fully duplicated rows:", data.duplicated().sum())

    # Return the table so we can do file-specific checks afterwards
    return data


# Inspect the monthly Labour Force Survey file
labour_force = inspect_file("CA_Labour_Force_Monthly.csv")

# Inspect the quarterly Job Vacancy and Wage Survey file
vacancies = inspect_file("CA_Job_Vacancies_Wages_Quarterly.csv")

# Extra check for the vacancy file only: count each Statistics Canada quality flag
# in the STATUS column. dropna=False also counts blank cells (no flag).
print("\n--- 6. Vacancy file: count of each STATUS value ---")
print(vacancies["STATUS"].value_counts(dropna=False).to_string())
