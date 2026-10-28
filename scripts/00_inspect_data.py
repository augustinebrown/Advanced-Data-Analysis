# 00_inspect_data.py
# Purpose: look at the two raw data files and print basic facts about them.
# This script ONLY reads and prints. It does not clean, change or save any data.
# Section 7 also checks numbers from the raw files that are quoted in the documentation.
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

# The industry column of the vacancy file, written once here to avoid typing mistakes
NAICS_COLUMN = "North American Industry Classification System (NAICS)"


def check(passed, description):
    """Print PASS if a validation check is true, otherwise stop the script with an error."""
    if passed:
        print("PASS:", description)
    else:
        raise ValueError("CHECK FAILED: " + description)


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


# =====================================================================
# 7. CHECKS ON NUMBERS FROM THE RAW FILES QUOTED IN THE DOCUMENTATION
# =====================================================================
# Each check below recalculates a number quoted in README.md, docs/data_dictionary.md
# or docs/research_log.md from the raw files, and stops with an error if it does not match.
print("\n" + "=" * 70)
print("7. NUMBERS QUOTED IN THE DOCUMENTATION")
print("=" * 70)

# 7a. Number of industries, geographies and statistics in the vacancy file (data dictionary, section 1.1)
check(vacancies[NAICS_COLUMN].nunique() == 21, "vacancy file has 21 industry names (all industries + 20 sectors)")
check(vacancies["GEO"].nunique() == 14, "vacancy file has 14 geography names (Canada, 10 provinces, 3 territories)")
check(vacancies["Statistics"].nunique() == 4, "vacancy file has 4 statistics names")

# 7b. January 2016, Canada, unadjusted, ages 15 and over (data dictionary, section 1.3), in thousands
january_2016 = labour_force[
    (labour_force["REF_DATE"] == "2016-01")
    & (labour_force["GEO"] == "Canada")
    & (labour_force["Age group"] == "15 years and over")
    & (labour_force["Data type"] == "Unadjusted")
].set_index("Labour force characteristics")["VALUE"]
print("\nJanuary 2016, Canada, unadjusted, ages 15 and over (thousands):")
print(january_2016.to_string())
check(january_2016["Population"] == 29218.7, "population aged 15 and over = 29,218.7 thousand")
check(january_2016["Labour force"] == 18988.4, "labour force = 18,988.4 thousand")
check(january_2016["Employment"] == 17520.5, "employment = 17,520.5 thousand")
check(january_2016["Unemployment"] == 1467.8, "unemployment = 1,467.8 thousand")
employment_plus_unemployment = round(january_2016["Employment"] + january_2016["Unemployment"], 1)
check(employment_plus_unemployment == 18988.3,
      "employment + unemployment = 18,988.3 thousand, 0.1 below the labour force (rounding)")

# 7c. Vacancy quality in 2015Q1, the reason the analysis starts in 2016Q1 (README, Key data decisions)
first_quarter = vacancies[
    (vacancies["REF_DATE"] == "2015-01")
    & (vacancies["Statistics"] == "Job vacancies")
    & (vacancies[NAICS_COLUMN] == "Total, all industries")
].set_index("GEO")
print("\nJob vacancies, all industries, 2015Q1:")
print(first_quarter[["VALUE", "STATUS"]].to_string())
unpublished = first_quarter[first_quarter["VALUE"].isna()].index
check(sorted(set(unpublished) - {"Yukon", "Northwest Territories", "Nunavut"})
      == ["Newfoundland and Labrador", "Prince Edward Island"],
      "2015Q1: the two provinces with unpublished estimates are Newfoundland and Labrador and Prince Edward Island (F)")
check(first_quarter.loc[["Alberta", "Manitoba", "Saskatchewan"], "STATUS"].tolist() == ["E", "E", "D"],
      "2015Q1: Prairie grades are Alberta E, Manitoba E, Saskatchewan D")

# 7d. Saskatchewan 2022Q3: the 20 sectors add up to 85 fewer vacancies than "Total, all industries",
# because Management of companies and enterprises [55] is graded F (research log)
saskatchewan = vacancies[
    (vacancies["REF_DATE"] == "2022-07")
    & (vacancies["GEO"] == "Saskatchewan")
    & (vacancies["Statistics"] == "Job vacancies")
]
total = saskatchewan[saskatchewan[NAICS_COLUMN] == "Total, all industries"]["VALUE"].iloc[0]
sectors = saskatchewan[saskatchewan[NAICS_COLUMN] != "Total, all industries"]
blank_sectors = sectors[sectors["VALUE"].isna()]
print(f"\nSaskatchewan 2022Q3: total {total:,.0f}, sum of 20 sectors {sectors['VALUE'].sum():,.0f}")
check(total - sectors["VALUE"].sum() == 85, "Saskatchewan 2022Q3: the sectors add up to 85 fewer vacancies than the total")
check(blank_sectors[NAICS_COLUMN].tolist() == ["Management of companies and enterprises [55]"]
      and blank_sectors["STATUS"].tolist() == ["F"],
      "Saskatchewan 2022Q3: the only blank sector is Management of companies and enterprises [55], graded F")
