# 01_clean.py
# Purpose: prepare each raw dataset separately and save one cleaned file for each.
#   - Labour Force Survey (monthly)  -> data/processed/lfs_unemployment_quarterly.csv
#   - Job Vacancy and Wage Survey    -> data/processed/jvws_vacancies_quarterly.csv
# The raw files in data/raw are only read, never changed.
# Run from the project folder with:  uv run python scripts/01_clean.py

from pathlib import Path

import pandas as pd

# Find the project folders, starting from where this script is saved
PROJECT_FOLDER = Path(__file__).parent.parent
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw"
PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"

# Names used in more than one place, written once here to avoid typing mistakes
TERRITORIES = ["Yukon", "Northwest Territories", "Nunavut"]
PRAIRIES = ["Alberta", "Saskatchewan", "Manitoba"]
NAICS_COLUMN = "North American Industry Classification System (NAICS)"


def check(passed, description):
    """Print PASS if a validation check is true, otherwise stop the script with an error."""
    if passed:
        print("PASS:", description)
    else:
        raise ValueError("CHECK FAILED: " + description)


def make_quarter(ref_date):
    """Turn dates like '2015-04' into quarters like '2015Q2'."""
    # The year is the first four characters ("2015")
    year = ref_date.str[:4]
    # The month is characters 6 and 7 ("04"), turned into a number (4)
    month = ref_date.str[5:7].astype(int)
    # Months 1-3 -> 1, 4-6 -> 2, 7-9 -> 3, 10-12 -> 4.
    # "//" is whole-number division, e.g. (4 - 1) // 3 = 1, then + 1 = 2.
    quarter_number = (month - 1) // 3 + 1
    # Join the pieces into text like "2015Q2"
    return year + "Q" + quarter_number.astype(str)


# =====================================================================
# PART A: LABOUR FORCE SURVEY (monthly unemployment)
# =====================================================================
print("=" * 70)
print("LABOUR FORCE SURVEY")
print("=" * 70)

# Read the raw monthly file
lfs = pd.read_csv(RAW_FOLDER / "CA_Labour_Force_Monthly.csv")

# Step 1: keep only unemployment, ages 15 and over, unadjusted
# (unadjusted because the vacancy data is not seasonally adjusted)
lfs = lfs[
    (lfs["Labour force characteristics"] == "Unemployment")
    & (lfs["Age group"] == "15 years and over")
    & (lfs["Data type"] == "Unadjusted")
]

# Step 2: drop the published Canada total (national totals are built from provinces later)
lfs = lfs[lfs["GEO"] != "Canada"]

# Rename GEO to a clearer name
lfs = lfs.rename(columns={"GEO": "province"})

# CHECK: before averaging, each of the 10 provinces should have 132 months (2015-2025)
print("\nMonthly rows per province after filtering:")
print(lfs["province"].value_counts().sort_index().to_string())
print("Total monthly rows:", len(lfs))
check(len(lfs) == 1320, "filtered LFS data has 1,320 monthly rows")
check(lfs["province"].nunique() == 10, "filtered LFS data has 10 provinces")
check((lfs["province"].value_counts() == 132).all(), "every province has exactly 132 monthly rows")

# Step 3: convert thousands of persons to persons.
# .round() removes tiny computer rounding errors (e.g. 330400.00000000006 -> 330400);
# it changes nothing real, because the raw values have one decimal place in thousands.
lfs["unemployed"] = (lfs["VALUE"] * 1000).round()

# Step 4: create the quarter column ("2015Q1") from the month
lfs["quarter"] = make_quarter(lfs["REF_DATE"])

# Keep a copy of the monthly data so we can show raw months for the hand check at the end
lfs_monthly = lfs.copy()

# Step 5: average the three months in each province and quarter,
# and count how many months went into each average
lfs_quarterly = lfs.groupby(["province", "quarter"], as_index=False).agg(
    unemployed=("unemployed", "mean"),
    months_used=("unemployed", "count"),
)

# CHECK: every average must be based on exactly 3 months
short_quarters = lfs_quarterly[lfs_quarterly["months_used"] != 3]
print("\nProvince-quarters not based on exactly 3 months:", len(short_quarters))
check(len(short_quarters) == 0, "every province-quarter average uses exactly 3 months")

# Step 6: keep only the columns we need
lfs_quarterly = lfs_quarterly[["province", "quarter", "unemployed"]]

# Step 7 (saving) happens at the very end, only after every check has passed


# =====================================================================
# PART B: JOB VACANCY AND WAGE SURVEY (quarterly vacancies)
# =====================================================================
print("\n" + "=" * 70)
print("JOB VACANCY AND WAGE SURVEY")
print("=" * 70)

# Read the raw quarterly file
jvws = pd.read_csv(RAW_FOLDER / "CA_Job_Vacancies_Wages_Quarterly.csv")

# Step 1: keep only job vacancies for all industries combined
jvws = jvws[
    (jvws["Statistics"] == "Job vacancies")
    & (jvws[NAICS_COLUMN] == "Total, all industries")
]

# Step 2: drop the Canada total and the three territories
jvws = jvws[jvws["GEO"] != "Canada"]
jvws = jvws[~jvws["GEO"].isin(TERRITORIES)]  # "~" means "not"

# CHECK: dates should only be quarter-start months (01, 04, 07, 10);
# if not, the month-to-quarter rule below would give wrong answers
months_present = sorted(jvws["REF_DATE"].str[5:7].unique())
print("\nMonths that appear in REF_DATE:", months_present)
check(months_present == ["01", "04", "07", "10"], "vacancy dates are all quarter-start months")

# Step 3: create the quarter column. Same rule as above: 01 -> Q1, 04 -> Q2, 07 -> Q3, 10 -> Q4
jvws["quarter"] = make_quarter(jvws["REF_DATE"])

# Step 4: rename columns (vacancies are already in persons, so no rescaling)
jvws = jvws.rename(columns={
    "GEO": "province",
    "VALUE": "vacancies",
    "STATUS": "vacancy_quality_flag",
})

# Step 5: keep only the columns we need
jvws = jvws[["province", "quarter", "vacancies", "vacancy_quality_flag"]]

# Step 6 (saving) happens at the very end, only after every check has passed


# =====================================================================
# PART C: VALIDATION CHECKS ON THE CLEANED FILES
# =====================================================================
print("\n" + "=" * 70)
print("VALIDATION CHECKS")
print("=" * 70)

# Size of the cleaned LFS file: 10 provinces x 44 quarters = 440 rows
print("\nLFS cleaned rows:", len(lfs_quarterly))
check(len(lfs_quarterly) == 440, "cleaned LFS file has 440 rows")
check(lfs_quarterly["province"].nunique() == 10, "cleaned LFS file has 10 provinces")
check((lfs_quarterly["province"].value_counts() == 44).all(), "every province has 44 quarters in LFS")

# Size of the cleaned JVWS file: 10 provinces x 42 quarters = 420 rows
print("\nJVWS cleaned rows:", len(jvws))
check(len(jvws) == 420, "cleaned JVWS file has 420 rows")
check(jvws["province"].nunique() == 10, "cleaned JVWS file has 10 provinces")
check((jvws["province"].value_counts() == 42).all(), "every province has 42 quarters in JVWS")

# The two quarters Statistics Canada did not collect should not appear
print()
check(not jvws["quarter"].isin(["2020Q2", "2020Q3"]).any(), "JVWS has no rows for 2020Q2 or 2020Q3")

# No province should appear twice for the same quarter
print()
check(not lfs_quarterly.duplicated(subset=["province", "quarter"]).any(), "no duplicate province-quarters in LFS")
check(not jvws.duplicated(subset=["province", "quarter"]).any(), "no duplicate province-quarters in JVWS")

# No missing unemployment numbers at all
print()
print("Missing values in unemployed:", lfs_quarterly["unemployed"].isna().sum())
check(lfs_quarterly["unemployed"].isna().sum() == 0, "no missing values in unemployed")

# Missing vacancies are allowed ONLY where Statistics Canada graded the value F
# (too unreliable to publish) and left it blank, and never for a Prairie province.
# We keep these rows (blank, not zero) so the gap stays visible in the data.
missing_vacancies = jvws[jvws["vacancies"].isna()]
print("\nRows with missing vacancies:", len(missing_vacancies))
print(missing_vacancies.to_string(index=False))
check(len(missing_vacancies) == 2, "exactly 2 missing vacancy values (expected: NL and PEI, 2015Q1)")
check((missing_vacancies["vacancy_quality_flag"] == "F").all(), "every missing vacancy value is flagged F")
check(not missing_vacancies["province"].isin(PRAIRIES).any(), "no Prairie province has a missing vacancy value")

# The province names must match exactly, or the merge in the next script will fail silently
lfs_provinces = sorted(lfs_quarterly["province"].unique())
jvws_provinces = sorted(jvws["province"].unique())
print("\nLFS provinces: ", lfs_provinces)
print("JVWS provinces:", jvws_provinces)
check(lfs_provinces == jvws_provinces, "province names match exactly in both files")

# Quality flags for the three Prairie provinces
prairie_jvws = jvws[jvws["province"].isin(PRAIRIES)]
print("\nVacancy quality flags, Prairie provinces (A = excellent ... F = too unreliable):")
print(pd.crosstab(prairie_jvws["province"], prairie_jvws["vacancy_quality_flag"].fillna("(blank)")).to_string())

# List any Prairie row graded C or lower (C = good, D = acceptable, E = use with caution, F = unreliable)
low_grade = prairie_jvws[prairie_jvws["vacancy_quality_flag"].isin(["C", "D", "E", "F"])]
print("\nPrairie rows graded C or lower:", len(low_grade))
print(low_grade.to_string(index=False))

# Hand check: Alberta 2019Q1 in both cleaned files
print("\n--- Hand check: Alberta, 2019Q1 ---")
print("Cleaned LFS row:")
print(lfs_quarterly[(lfs_quarterly["province"] == "Alberta") & (lfs_quarterly["quarter"] == "2019Q1")].to_string(index=False))
print("\nCleaned JVWS row:")
print(jvws[(jvws["province"] == "Alberta") & (jvws["quarter"] == "2019Q1")].to_string(index=False))

# The three raw monthly values behind the Alberta 2019Q1 average (VALUE is in thousands)
print("\nRaw monthly unemployment, Alberta, Jan-Mar 2019 (VALUE in thousands):")
alberta_months = lfs_monthly[
    (lfs_monthly["province"] == "Alberta")
    & (lfs_monthly["REF_DATE"].isin(["2019-01", "2019-02", "2019-03"]))
]
print(alberta_months[["REF_DATE", "province", "VALUE"]].to_string(index=False))

print("\nAll checks passed.")


# =====================================================================
# PART D: SAVE THE CLEANED FILES
# This runs only if every check above passed (a failed check stops the script
# before reaching this point), so an unchecked file is never saved.
# =====================================================================
lfs_quarterly.to_csv(PROCESSED_FOLDER / "lfs_unemployment_quarterly.csv", index=False)
print("\nSaved data/processed/lfs_unemployment_quarterly.csv")

jvws.to_csv(PROCESSED_FOLDER / "jvws_vacancies_quarterly.csv", index=False)
print("Saved data/processed/jvws_vacancies_quarterly.csv")
