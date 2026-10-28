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

# Period covered by the analysis: 2016Q1 to 2025Q4.
# 2015 is excluded because the vacancy survey's first quarter (2015Q1) had unpublished
# estimates (Newfoundland and Labrador, Prince Edward Island) and low-quality estimates
# (all three Prairie provinces), and because the comparison periods use complete
# calendar years starting in 2016. The raw files still contain 2015; it is only
# filtered out here.
FIRST_MONTH, LAST_MONTH = "2016-01", "2025-12"
FIRST_QUARTER, LAST_QUARTER = "2016Q1", "2025Q4"


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
# PART 0: CHECK THE QUARTER RULE AGAINST THE COURSE CONCORDANCE TABLE
# =====================================================================
# data/raw/concord.csv is the PPOL 652 month-to-quarter concordance table
# (columns: month, q). It is used only to validate make_quarter's rule: for every
# month, the rule must give the same quarter as the table. If any month disagrees,
# the script stops before any data is processed.
print("=" * 70)
print("QUARTER RULE VS COURSE CONCORDANCE TABLE")
print("=" * 70)

# Read the table. skipinitialspace=True ignores the space after each comma in the file.
concord = pd.read_csv(RAW_FOLDER / "concord.csv", skipinitialspace=True)

# Month names and their numbers (January = 1, ..., December = 12)
MONTH_NUMBERS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}

# CHECK: 12 rows, each month exactly once, each quarter (1 to 4) exactly 3 times
print("\nRows in concordance table:", len(concord))
check(len(concord) == 12, "concordance table has exactly 12 rows")
check(sorted(concord["month"]) == sorted(MONTH_NUMBERS), "concordance table lists each month exactly once")
check(sorted(concord["q"].unique()) == [1, 2, 3, 4] and (concord["q"].value_counts() == 3).all(),
      "each quarter 1 to 4 appears exactly 3 times")

# Convert each month name to its number, build a date like "2016-02" for it, and run it
# through make_quarter itself, so the check tests the actual function used on the data.
# .str.zfill(2) adds a leading zero to one-digit months ("2" -> "02").
concord["month_number"] = concord["month"].map(MONTH_NUMBERS)
dates = "2016-" + concord["month_number"].astype(str).str.zfill(2)
concord["rule_quarter"] = make_quarter(dates).str[-1].astype(int)

# CHECK: the rule and the table agree for all 12 months
print(concord[["month", "month_number", "q", "rule_quarter"]].to_string(index=False))
disagree = concord[concord["rule_quarter"] != concord["q"]]
check(len(disagree) == 0, "make_quarter gives the same quarter as the concordance table for all 12 months")
print()


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

# Step 2b: keep only months from 2016-01 to 2025-12 (see the period note at the top).
# Dates written as "YYYY-MM" sort correctly as text, so >= and <= work on them.
lfs = lfs[(lfs["REF_DATE"] >= FIRST_MONTH) & (lfs["REF_DATE"] <= LAST_MONTH)]

# Rename GEO to a clearer name
lfs = lfs.rename(columns={"GEO": "province"})

# CHECK: before averaging, each of the 10 provinces should have 120 months (2016-2025)
print("\nMonthly rows per province after filtering:")
print(lfs["province"].value_counts().sort_index().to_string())
print("Total monthly rows:", len(lfs))
check(len(lfs) == 1200, "filtered LFS data has 1,200 monthly rows")
check(lfs["province"].nunique() == 10, "filtered LFS data has 10 provinces")
check((lfs["province"].value_counts() == 120).all(), "every province has exactly 120 monthly rows")

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

# Step 3b: keep only quarters from 2016Q1 to 2025Q4 (see the period note at the top).
# Quarters written as "YYYYQn" also sort correctly as text.
jvws = jvws[(jvws["quarter"] >= FIRST_QUARTER) & (jvws["quarter"] <= LAST_QUARTER)]

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

# Size of the cleaned LFS file: 10 provinces x 40 quarters = 400 rows
print("\nLFS cleaned rows:", len(lfs_quarterly))
check(len(lfs_quarterly) == 400, "cleaned LFS file has 400 rows")
check(lfs_quarterly["province"].nunique() == 10, "cleaned LFS file has 10 provinces")
check((lfs_quarterly["province"].value_counts() == 40).all(), "every province has 40 quarters in LFS")

# Size of the cleaned JVWS file: 10 provinces x 38 quarters (40 minus 2020Q2 and 2020Q3) = 380 rows
print("\nJVWS cleaned rows:", len(jvws))
check(len(jvws) == 380, "cleaned JVWS file has 380 rows")
check(jvws["province"].nunique() == 10, "cleaned JVWS file has 10 provinces")
check((jvws["province"].value_counts() == 38).all(), "every province has 38 quarters in JVWS")

# No quarter before the start of the analysis period in either file
print("\nEarliest quarter in LFS:", lfs_quarterly["quarter"].min(), "  latest:", lfs_quarterly["quarter"].max())
print("Earliest quarter in JVWS:", jvws["quarter"].min(), "  latest:", jvws["quarter"].max())
check((lfs_quarterly["quarter"] >= FIRST_QUARTER).all(), "no LFS quarter earlier than 2016Q1")
check((jvws["quarter"] >= FIRST_QUARTER).all(), "no JVWS quarter earlier than 2016Q1")

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

# No missing vacancy numbers at all. (The only blanks in the raw rows we use were
# NL and PEI in 2015Q1, which are now outside the analysis period.)
missing_vacancies = jvws[jvws["vacancies"].isna()]
print("\nRows with missing vacancies:", len(missing_vacancies))
if len(missing_vacancies) > 0:
    print(missing_vacancies.to_string(index=False))
check(len(missing_vacancies) == 0, "no missing values in vacancies")

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
if len(low_grade) > 0:
    print(low_grade.to_string(index=False))

# CHECK: the quality-grade counts quoted in the README and data dictionary.
# Prairie provinces: all A or B (110 A, 4 B)
prairie_grades = prairie_jvws["vacancy_quality_flag"].value_counts()
check(prairie_jvws["vacancy_quality_flag"].isin(["A", "B"]).all(), "every Prairie row is graded A or B")
check(prairie_grades.get("A", 0) == 110 and prairie_grades.get("B", 0) == 4, "Prairie rows: 110 graded A and 4 graded B")

# All ten provinces: 305 A, 61 B, 13 C (all Prince Edward Island), 1 D (Prince Edward Island 2019Q4), nothing lower
all_grades = jvws["vacancy_quality_flag"].value_counts()
print("\nVacancy quality flags, all ten provinces:")
print(all_grades.to_string())
grade_c = jvws[jvws["vacancy_quality_flag"] == "C"]
grade_d = jvws[jvws["vacancy_quality_flag"] == "D"]
check(all_grades.get("A", 0) == 305 and all_grades.get("B", 0) == 61, "all provinces: 305 rows graded A and 61 graded B")
check(len(grade_c) == 13 and (grade_c["province"] == "Prince Edward Island").all(),
      "13 rows graded C, all Prince Edward Island")
check(len(grade_d) == 1 and grade_d["province"].iloc[0] == "Prince Edward Island" and grade_d["quarter"].iloc[0] == "2019Q4",
      "1 row graded D: Prince Edward Island 2019Q4")
check(not jvws["vacancy_quality_flag"].isin(["E", "F"]).any(), "no row graded E or F")

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
