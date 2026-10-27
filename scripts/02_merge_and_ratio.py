# 02_merge_and_ratio.py
# Purpose: join the two cleaned files, calculate the vacancy-to-unemployment ratio
# for each province and quarter, and build comparison groups (Prairies, Rest of Canada, Canada).
#   - data/processed/merged_province_quarter.csv  (one row per province and quarter)
#   - data/processed/group_quarter.csv            (one row per group and quarter)
# Reads from data/processed (and data/raw only for comparison checks). Never changes data/raw.
# Run from the project folder with:  uv run python scripts/02_merge_and_ratio.py

from pathlib import Path

import pandas as pd

# Find the project folders, starting from where this script is saved
PROJECT_FOLDER = Path(__file__).parent.parent
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw"
PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"

# The two regions, written out in full so every province is listed exactly once
PRAIRIES = ["Alberta", "Saskatchewan", "Manitoba"]
REST_OF_CANADA = [
    "British Columbia", "Ontario", "Quebec", "New Brunswick", "Nova Scotia",
    "Prince Edward Island", "Newfoundland and Labrador",
]
TERRITORIES = ["Yukon", "Northwest Territories", "Nunavut"]

# The comparison groups: each group name and the provinces it adds up
GROUPS = {
    "Alberta": ["Alberta"],
    "Saskatchewan": ["Saskatchewan"],
    "Manitoba": ["Manitoba"],
    "Prairies": PRAIRIES,
    "Rest of Canada": REST_OF_CANADA,
    "Canada": PRAIRIES + REST_OF_CANADA,
}

# Quarters with no vacancy data at all (Statistics Canada did not collect them)
NOT_COLLECTED = ["2020Q2", "2020Q3"]


def check(passed, description):
    """Print PASS if a validation check is true, otherwise stop the script with an error."""
    if passed:
        print("PASS:", description)
    else:
        raise ValueError("CHECK FAILED: " + description)


def make_quarter(ref_date):
    """Turn dates like '2015-04' into quarters like '2015Q2' (same rule as 01_clean.py)."""
    year = ref_date.str[:4]
    month = ref_date.str[5:7].astype(int)
    quarter_number = (month - 1) // 3 + 1
    return year + "Q" + quarter_number.astype(str)


# =====================================================================
# PART A: MERGE THE TWO CLEANED FILES AND CALCULATE THE RATIO
# =====================================================================
print("=" * 70)
print("MERGE AND PROVINCIAL RATIO")
print("=" * 70)

# Step 1: read the two cleaned files
lfs = pd.read_csv(PROCESSED_FOLDER / "lfs_unemployment_quarterly.csv")
jvws = pd.read_csv(PROCESSED_FOLDER / "jvws_vacancies_quarterly.csv")

# Step 2: join them on province and quarter.
#   how="left"   keeps every row of the LFS file, so 2020Q2 and 2020Q3 stay as rows
#                with blank vacancies.
#   indicator    adds a column "_merge" saying whether each row was found in both files
#                ("both") or only in the LFS file ("left_only").
#   validate     stops with an error if any province-quarter appears more than once
#                in either file (which would create duplicated rows).
merged = pd.merge(
    lfs, jvws,
    on=["province", "quarter"],
    how="left",
    indicator=True,
    validate="one_to_one",
)

# Print how many rows matched and how many did not
print("\nMerge result (both = found in both files, left_only = LFS only):")
print(merged["_merge"].value_counts().to_string())
check((merged["_merge"] == "both").sum() == 380, "380 rows matched in both files")
check((merged["_merge"] == "left_only").sum() == 20, "20 rows found only in LFS (2020Q2 and 2020Q3)")
check(merged.loc[merged["_merge"] == "left_only", "quarter"].isin(NOT_COLLECTED).all(),
      "every unmatched row is in 2020Q2 or 2020Q3")

# The indicator column was only needed for this check, so remove it
merged = merged.drop(columns="_merge")

# Step 3: ratio = vacancies / unemployed.
# Dividing a blank (missing) number gives a blank result, not zero, so missing stays missing.
merged["ratio"] = merged["vacancies"] / merged["unemployed"]

# Step 4: add the region column. Start everyone as "Rest of Canada",
# then change the three Prairie provinces to "Prairies".
merged["region"] = "Rest of Canada"
merged.loc[merged["province"].isin(PRAIRIES), "region"] = "Prairies"

# Step 5: put the columns in the agreed order (saving happens at the end)
merged = merged[["province", "region", "quarter", "unemployed", "vacancies", "ratio", "vacancy_quality_flag"]]


# =====================================================================
# PART B: BUILD THE COMPARISON GROUPS
# =====================================================================
# Step 6 and 7: for each group, add up vacancies and add up unemployed for each quarter,
# then divide the totals. We do NOT average the provincial ratios, because that would
# give PEI the same weight as Ontario.
#
# Step 8: missing values. By default pandas treats blanks as zero when adding up,
# so a quarter with missing provinces would get a total that is too small.
# min_count = the number of provinces in the group means: "only give a total if
# at least this many provinces have a value; otherwise leave the total blank."
# Because every group has one row per province per quarter, this means a total is
# calculated only when EVERY province in the group has data.
group_tables = []
for group_name, provinces in GROUPS.items():
    # Keep only the provinces in this group
    rows = merged[merged["province"].isin(provinces)]
    # Add up each quarter, requiring all provinces in the group to have a value
    totals = rows.groupby("quarter", as_index=False)[["unemployed", "vacancies"]].sum(
        min_count=len(provinces)
    )
    totals["group"] = group_name
    group_tables.append(totals)

# Stack the six group tables into one table
groups = pd.concat(group_tables, ignore_index=True)

# Ratio of the totals (blank vacancies give a blank ratio)
groups["ratio"] = groups["vacancies"] / groups["unemployed"]

# Put the columns in the agreed order
groups = groups[["group", "quarter", "unemployed", "vacancies", "ratio"]]


# =====================================================================
# PART C: VALIDATION CHECKS
# =====================================================================
print("\n" + "=" * 70)
print("VALIDATION CHECKS")
print("=" * 70)

# Every province is in exactly one region (catches spelling mistakes in the lists above)
print()
check(sorted(PRAIRIES + REST_OF_CANADA) == sorted(merged["province"].unique()),
      "the 3 Prairie + 7 Rest of Canada names match the 10 provinces in the data")

# --- Merged file: size and missing vacancies ---
print("\nMerged rows:", len(merged))
check(len(merged) == 400, "merged file has 400 rows")

missing = merged[merged["vacancies"].isna()]
print("Rows with missing vacancies:", len(missing))
check(len(missing) == 20, "exactly 20 rows have missing vacancies")
check(missing["quarter"].isin(NOT_COLLECTED).all(),
      "all 20 are in 2020Q2 or 2020Q3 (10 provinces x 2 quarters)")
check(merged["ratio"].isna().sum() == 20, "ratio is missing in exactly the same 20 rows")

# --- Ratios: never zero, never negative ---
print()
check((merged["ratio"] != 0).all(), "no provincial ratio is exactly zero")
check(not (merged["ratio"] < 0).any(), "no provincial ratio is negative")
check((groups["ratio"] != 0).all(), "no group ratio is exactly zero")
check(not (groups["ratio"] < 0).any(), "no group ratio is negative")

# --- Group file: size ---
print("\nGroup rows:", len(groups))
check(len(groups) == 6 * 40, "group file has 240 rows (6 groups x 40 quarters)")

# --- Canada = Prairies + Rest of Canada (unemployed), for every quarter ---
# We allow a difference of less than 0.01 person, because computers store decimals
# with tiny rounding errors (e.g. 0.1 + 0.2 = 0.30000000000000004).
canada_unemp = groups[groups["group"] == "Canada"].set_index("quarter")["unemployed"]
prairie_unemp = groups[groups["group"] == "Prairies"].set_index("quarter")["unemployed"]
rest_unemp = groups[groups["group"] == "Rest of Canada"].set_index("quarter")["unemployed"]
largest_gap = (canada_unemp - (prairie_unemp + rest_unemp)).abs().max()
print("\nLargest gap between Canada and Prairies + Rest of Canada (unemployed):", largest_gap)
check(largest_gap < 0.01, "Canada unemployed = Prairies + Rest of Canada in every quarter")

# --- Group file: 2020Q2 and 2020Q3 missing (not zero) for every group ---
groups_2020 = groups[groups["quarter"].isin(NOT_COLLECTED)]
print("\nGroup rows for 2020Q2 and 2020Q3:")
print(groups_2020.to_string(index=False))
check(len(groups_2020) == 12, "12 group rows in 2020Q2 and 2020Q3 (6 groups x 2)")
check(groups_2020["vacancies"].isna().all(), "vacancies missing (not zero) for every group in 2020Q2 and 2020Q3")
check(groups_2020["ratio"].isna().all(), "ratio missing (not zero) for every group in 2020Q2 and 2020Q3")

# No other missing values anywhere in the group file
print()
check(groups["vacancies"].isna().sum() == 12, "group file has exactly 12 missing vacancies (all in 2020Q2 and 2020Q3)")
check(groups["unemployed"].isna().sum() == 0, "group file has no missing unemployed")

# --- Compare our Canada unemployment with the published LFS Canada total ---
# Rebuild the published Canada series the same way as the provinces in 01_clean.py
lfs_raw = pd.read_csv(RAW_FOLDER / "CA_Labour_Force_Monthly.csv")
published_lfs = lfs_raw[
    (lfs_raw["Labour force characteristics"] == "Unemployment")
    & (lfs_raw["Age group"] == "15 years and over")
    & (lfs_raw["Data type"] == "Unadjusted")
    & (lfs_raw["GEO"] == "Canada")
].copy()
published_lfs["published_unemployed"] = published_lfs["VALUE"] * 1000
published_lfs["quarter"] = make_quarter(published_lfs["REF_DATE"])
published_lfs = published_lfs.groupby("quarter", as_index=False)["published_unemployed"].mean()

# Put our total and the published total side by side
compare_unemp = pd.merge(
    groups[groups["group"] == "Canada"][["quarter", "unemployed"]],
    published_lfs, on="quarter",
)
compare_unemp["difference"] = compare_unemp["unemployed"] - compare_unemp["published_unemployed"]
largest_unemp_difference = compare_unemp["difference"].abs().max()
print("\n--- Our Canada unemployed vs published LFS Canada ---")
print("Quarters compared:", len(compare_unemp))
print("Largest absolute difference (persons):", round(largest_unemp_difference, 1))
print("Largest difference as % of published total:",
      round(100 * (compare_unemp["difference"].abs() / compare_unemp["published_unemployed"]).max(), 4), "%")
# Published values are rounded to the nearest 100 persons (0.1 thousand), so adding up
# 10 rounded provinces can differ from the rounded Canada total by a few hundred persons.
check(len(compare_unemp) == 40, "published Canada series covers all 40 quarters (2016Q1 to 2025Q4)")
check(largest_unemp_difference < 1000, "our Canada unemployed is within 1,000 persons of the published total")

# --- Compare our Canada vacancies with the published JVWS Canada total ---
jvws_raw = pd.read_csv(RAW_FOLDER / "CA_Job_Vacancies_Wages_Quarterly.csv")
jvws_raw = jvws_raw[
    (jvws_raw["Statistics"] == "Job vacancies")
    & (jvws_raw["North American Industry Classification System (NAICS)"] == "Total, all industries")
].copy()
jvws_raw["quarter"] = make_quarter(jvws_raw["REF_DATE"])

# Published Canada total
published_jvws = jvws_raw[jvws_raw["GEO"] == "Canada"][["quarter", "VALUE"]]
published_jvws = published_jvws.rename(columns={"VALUE": "published_canada"})

# Sum of the three territories (blank if any territory is blank), to explain the gap
territories = jvws_raw[jvws_raw["GEO"].isin(TERRITORIES)]
territories = territories.groupby("quarter", as_index=False)["VALUE"].sum(min_count=3)
territories = territories.rename(columns={"VALUE": "territories_total"})

# Put our total, the published total and the territories side by side
compare_vac = groups[groups["group"] == "Canada"][["quarter", "vacancies"]]
compare_vac = compare_vac.rename(columns={"vacancies": "our_10_provinces"})
compare_vac = pd.merge(compare_vac, published_jvws, on="quarter")
compare_vac = pd.merge(compare_vac, territories, on="quarter")
compare_vac["published_minus_ours"] = compare_vac["published_canada"] - compare_vac["our_10_provinces"]

# Only quarters where both totals exist can be compared (not 2020Q2 or 2020Q3)
comparable = compare_vac.dropna(subset=["our_10_provinces", "published_canada"])
print("\n--- Our Canada vacancies vs published JVWS Canada ---")
print("Selected quarters:")
print(comparable[comparable["quarter"].isin(["2016Q1", "2019Q1", "2022Q2", "2025Q4"])].to_string(index=False))
print("\nQuarters compared:", len(comparable))
print("Quarters where our total is smaller than published:", (comparable["published_minus_ours"] > 0).sum())
print("Smallest and largest gap (published minus ours):",
      comparable["published_minus_ours"].min(), "to", comparable["published_minus_ours"].max())
check((comparable["published_minus_ours"] > 0).all(),
      "our 10-province vacancy total is smaller than the published Canada total in every comparable quarter")

# --- Hand check: Alberta 2019Q1 ratio ---
alberta = merged[(merged["province"] == "Alberta") & (merged["quarter"] == "2019Q1")]
print("\n--- Hand check: Alberta, 2019Q1 ---")
print(alberta.to_string(index=False))
alberta_vacancies = alberta["vacancies"].iloc[0]
alberta_unemployed = alberta["unemployed"].iloc[0]
alberta_ratio = alberta["ratio"].iloc[0]
print(f"ratio = vacancies / unemployed = {alberta_vacancies:,.0f} / {alberta_unemployed:,.2f} = {alberta_ratio:.4f}")
print(f"In words: about {alberta_ratio:.2f} vacancies per unemployed person, "
      f"or about {1 / alberta_ratio:.1f} unemployed people per vacancy.")
check(abs(alberta_ratio - 0.281) < 0.0005, "Alberta 2019Q1 ratio is about 0.281")

# --- Annual average ratios (for information only; not saved) ---
# Average of the quarterly ratios in each year, 2016 to 2025. Blank quarters are
# skipped, so 2020 uses 2 quarters; every other year uses 4.
groups["year"] = groups["quarter"].str[:4]
annual = groups.pivot_table(index="year", columns="group", values="ratio", aggfunc="mean")
annual = annual[list(GROUPS.keys())].round(2)
quarters_used = groups.pivot_table(index="year", columns="group", values="ratio", aggfunc="count")
annual["note"] = ""
annual.loc["2020", "note"] = "excluded from period comparisons, only two quarters available"
print("\n--- Annual average ratio (vacancies per unemployed person) ---")
print(annual.to_string())
print("\nNumber of quarters behind each annual average:")
print(quarters_used[list(GROUPS.keys())].to_string())
groups = groups.drop(columns="year")

print("\nAll checks passed.")


# =====================================================================
# PART D: SAVE THE FILES
# This runs only if every check above passed (a failed check stops the script
# before reaching this point), so an unchecked file is never saved.
# =====================================================================
merged.to_csv(PROCESSED_FOLDER / "merged_province_quarter.csv", index=False)
print("\nSaved data/processed/merged_province_quarter.csv")

groups.to_csv(PROCESSED_FOLDER / "group_quarter.csv", index=False)
print("Saved data/processed/group_quarter.csv")
