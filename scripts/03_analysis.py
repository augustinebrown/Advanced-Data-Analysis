# 03_analysis.py
# Purpose: compare labour market tightness across the six groups and three periods.
#   Reads data/processed/group_quarter.csv (it is only read, never changed).
#   Writes six tables to outputs/tables/, only after every check has passed:
#     period_ratios.csv, relative_to_rest_of_canada.csv,
#     quarterly_relative_to_rest_of_canada.csv, decomposition.csv,
#     trajectory_summary.csv, sensitivity_averaging_method.csv
# Run from the project folder with:  uv run python scripts/03_analysis.py

import math
from pathlib import Path

import pandas as pd

# Find the project folders, starting from where this script is saved
PROJECT_FOLDER = Path(__file__).parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"
TABLE_FOLDER = PROJECT_FOLDER / "outputs" / "tables"

# The six groups, always shown in this order
GROUP_ORDER = ["Alberta", "Saskatchewan", "Manitoba", "Prairies", "Rest of Canada", "Canada"]
PRAIRIE_PROVINCES = ["Alberta", "Saskatchewan", "Manitoba"]
DECOMPOSITION_GROUPS = ["Alberta", "Saskatchewan", "Manitoba", "Prairies", "Rest of Canada"]

# The three comparison periods: name -> (first year, last year, expected number of quarters).
# 2020 is not in any period.
PERIODS = {
    "2016-2019": (2016, 2019, 16),
    "2021-2022": (2021, 2022, 8),
    "2023-2025": (2023, 2025, 12),
}
PERIOD_ORDER = list(PERIODS)

# Consecutive pairs of periods, for the decomposition of change
PERIOD_CHANGES = [("2016-2019", "2021-2022"), ("2021-2022", "2023-2025")]

# Show wide tables in full when printing
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)


def check(passed, description):
    """Print PASS if a validation check is true, otherwise stop the script with an error."""
    if passed:
        print("PASS:", description)
    else:
        raise ValueError("CHECK FAILED: " + description)


def position(relative_value):
    """Describe a value relative to Rest of Canada: above 1 is tighter, below 1 is looser."""
    if relative_value > 1:
        return "tighter"
    if relative_value < 1:
        return "looser"
    return "same"


def percent_change(before, after):
    """Percentage change from 'before' to 'after'."""
    return (after / before - 1) * 100


# Read the group file
groups = pd.read_csv(PROCESSED_FOLDER / "group_quarter.csv")


# =====================================================================
# PART A: ASSIGN EACH QUARTER TO A PERIOD (using the year column)
# =====================================================================
# Start with an empty period for every row, then fill in the period for its years.
# Quarters in 2020 keep an empty period, so they are left out of every period.
groups["period"] = ""
for period_name, (first_year, last_year, expected_quarters) in PERIODS.items():
    groups.loc[groups["year"].between(first_year, last_year), "period"] = period_name

# Keep only the quarters that belong to a period
in_periods = groups[groups["period"] != ""]

print("=" * 70)
print("CHECKS: PERIOD ASSIGNMENT")
print("=" * 70)

# CHECK: the file has exactly the six groups
check(sorted(groups["group"].unique()) == sorted(GROUP_ORDER), "the group file contains exactly the six groups")

# CHECK: no 2020 quarter is in a period
print("\nRows from 2020 in the group file:", (groups["year"] == 2020).sum(),
      "| of which assigned to a period:", (in_periods["year"] == 2020).sum())
check((in_periods["year"] != 2020).all(), "no 2020 quarter is assigned to a period")

# CHECK: every group has 16, 8 and 12 quarters in the three periods
quarter_counts = in_periods.pivot_table(index="group", columns="period", values="quarter", aggfunc="count")
print("\nNumber of quarters in each group and period:")
print(quarter_counts.loc[GROUP_ORDER, PERIOD_ORDER].to_string())
for period_name, (first_year, last_year, expected_quarters) in PERIODS.items():
    check((quarter_counts[period_name] == expected_quarters).all(),
          f"every group has exactly {expected_quarters} quarters in {period_name}")

# CHECK: no missing values inside any period
missing_inside_periods = in_periods[["unemployed", "vacancies", "ratio"]].isna().sum().sum()
print("\nMissing values inside the periods:", missing_inside_periods)
check(missing_inside_periods == 0, "no missing values inside any period")


# =====================================================================
# STEP 1: PERIOD RATIOS (add up first, then divide)
# =====================================================================
# For each group and period, add up vacancies and unemployed over all quarters in the
# period, then divide. "Total" here means the sum of the quarterly values, which is
# used only to calculate the ratio; it is not a count of separate vacancies or people.
rows = []
for group in GROUP_ORDER:
    for period_name in PERIOD_ORDER:
        data = in_periods[(in_periods["group"] == group) & (in_periods["period"] == period_name)]
        total_vacancies = data["vacancies"].sum()
        total_unemployed = data["unemployed"].sum()
        rows.append({
            "group": group,
            "period": period_name,
            "quarters": len(data),
            "total_vacancies": total_vacancies,
            "total_unemployed": total_unemployed,
            "period_ratio": total_vacancies / total_unemployed,
        })
period_ratios = pd.DataFrame(rows)


# =====================================================================
# STEP 2: TIGHTNESS RELATIVE TO REST OF CANADA
# =====================================================================
# Period version: each group's period ratio divided by Rest of Canada's period ratio.
# Above 1 = tighter than Rest of Canada; below 1 = looser.
rest_period_ratio = period_ratios[period_ratios["group"] == "Rest of Canada"].set_index("period")["period_ratio"]
relative = period_ratios[["group", "period", "period_ratio"]].copy()
relative["rest_of_canada_ratio"] = relative["period"].map(rest_period_ratio)
relative["relative_to_rest_of_canada"] = relative["period_ratio"] / relative["rest_of_canada_ratio"]
relative["position"] = relative["relative_to_rest_of_canada"].apply(position)

# Quarterly version (for charts later): each group's quarterly ratio divided by
# Rest of Canada's ratio in the same quarter. Blank divided by anything stays blank,
# so 2020Q2 and 2020Q3 are blank.
rest_quarterly_ratio = groups[groups["group"] == "Rest of Canada"].set_index("quarter")["ratio"]
quarterly_relative = groups[["group", "quarter", "year", "quarter_number", "ratio"]].copy()
quarterly_relative["rest_of_canada_ratio"] = quarterly_relative["quarter"].map(rest_quarterly_ratio)
quarterly_relative["relative_to_rest_of_canada"] = (
    quarterly_relative["ratio"] / quarterly_relative["rest_of_canada_ratio"]
)


# =====================================================================
# STEP 3: DECOMPOSITION OF CHANGE BETWEEN CONSECUTIVE PERIODS
# =====================================================================
# Average quarterly values (total divided by number of quarters) make periods of
# different lengths comparable. The ratio of the averages equals the period ratio.
#
# Exact log decomposition: because ratio = vacancies / unemployed,
#   log change in ratio = log change in vacancies - log change in unemployed.
# "vacancies_part" is the log change in vacancies; "unemployed_part" is MINUS the
# log change in unemployed (fewer unemployed pushes the ratio up). The two parts add
# up to the log change in the ratio. Each part divided by the log change in the
# ratio gives its share; the two shares add up to 1.
def get_period_row(group, period_name):
    """Return the Step 1 row for one group and period."""
    match = period_ratios[(period_ratios["group"] == group) & (period_ratios["period"] == period_name)]
    return match.iloc[0]


rows = []
for group in DECOMPOSITION_GROUPS:
    for from_period, to_period in PERIOD_CHANGES:
        before = get_period_row(group, from_period)
        after = get_period_row(group, to_period)

        # Average quarterly vacancies and unemployed in each period
        vacancies_before = before["total_vacancies"] / before["quarters"]
        vacancies_after = after["total_vacancies"] / after["quarters"]
        unemployed_before = before["total_unemployed"] / before["quarters"]
        unemployed_after = after["total_unemployed"] / after["quarters"]
        ratio_before = vacancies_before / unemployed_before
        ratio_after = vacancies_after / unemployed_after

        # Log changes (math.log is the natural logarithm)
        log_change_ratio = math.log(ratio_after / ratio_before)
        vacancies_part = math.log(vacancies_after / vacancies_before)
        unemployed_part = -math.log(unemployed_after / unemployed_before)

        rows.append({
            "group": group,
            "from_period": from_period,
            "to_period": to_period,
            "avg_vacancies_from": vacancies_before,
            "avg_vacancies_to": vacancies_after,
            "avg_unemployed_from": unemployed_before,
            "avg_unemployed_to": unemployed_after,
            "ratio_from": ratio_before,
            "ratio_to": ratio_after,
            "pct_change_ratio": percent_change(ratio_before, ratio_after),
            "pct_change_vacancies": percent_change(vacancies_before, vacancies_after),
            "pct_change_unemployed": percent_change(unemployed_before, unemployed_after),
            "log_change_ratio": log_change_ratio,
            "vacancies_part": vacancies_part,
            "unemployed_part": unemployed_part,
            "vacancies_share": vacancies_part / log_change_ratio,
            "unemployed_share": unemployed_part / log_change_ratio,
        })
decomposition = pd.DataFrame(rows)


# =====================================================================
# STEP 4: TRAJECTORY SUMMARY FOR THE THREE PRAIRIE PROVINCES
# =====================================================================
# For each province and period: tighter or looser than Rest of Canada, and whether
# its period ratio rose or fell compared with the previous period.
rows = []
for province in PRAIRIE_PROVINCES:
    previous_ratio = None
    for period_name in PERIOD_ORDER:
        row = relative[(relative["group"] == province) & (relative["period"] == period_name)].iloc[0]
        if previous_ratio is None:
            direction = ""  # first period: nothing to compare with
            change = None
        else:
            change = percent_change(previous_ratio, row["period_ratio"])
            direction = "rose" if change > 0 else ("fell" if change < 0 else "unchanged")
        rows.append({
            "province": province,
            "period": period_name,
            "period_ratio": row["period_ratio"],
            "relative_to_rest_of_canada": row["relative_to_rest_of_canada"],
            "position_vs_rest_of_canada": row["position"],
            "change_from_previous_period": direction,
            "pct_change_from_previous_period": change,
        })
        previous_ratio = row["period_ratio"]
trajectory = pd.DataFrame(rows)


# =====================================================================
# STEP 5: SENSITIVITY CHECK ON THE AVERAGING METHOD
# =====================================================================
# Alternative method: the simple average of the quarterly ratios in each period.
# Compare it with the main method (total vacancies / total unemployed).
average_of_quarters = (
    in_periods.groupby(["group", "period"], as_index=False)["ratio"].mean()
    .rename(columns={"ratio": "ratio_average_of_quarters"})
)
sensitivity = period_ratios[["group", "period", "period_ratio"]].rename(
    columns={"period_ratio": "ratio_total_over_total"}
)
sensitivity = sensitivity.merge(average_of_quarters, on=["group", "period"], how="left")
sensitivity["difference"] = sensitivity["ratio_average_of_quarters"] - sensitivity["ratio_total_over_total"]

# Position relative to Rest of Canada under each method
rest_average = sensitivity[sensitivity["group"] == "Rest of Canada"].set_index("period")["ratio_average_of_quarters"]
sensitivity["relative_total_over_total"] = sensitivity["ratio_total_over_total"] / sensitivity["period"].map(rest_period_ratio)
sensitivity["relative_average_of_quarters"] = sensitivity["ratio_average_of_quarters"] / sensitivity["period"].map(rest_average)
sensitivity["position_total_over_total"] = sensitivity["relative_total_over_total"].apply(position)
sensitivity["position_average_of_quarters"] = sensitivity["relative_average_of_quarters"].apply(position)
sensitivity["position_changes"] = (
    sensitivity["position_total_over_total"] != sensitivity["position_average_of_quarters"]
).map({True: "yes", False: "no"})


# =====================================================================
# PART C: VALIDATION CHECKS ON THE RESULTS
# =====================================================================
print("\n" + "=" * 70)
print("CHECKS: RESULTS")
print("=" * 70)

# Step 1: 18 rows (6 groups x 3 periods), quarters as expected, no blanks
check(len(period_ratios) == 18, "period_ratios has 18 rows (6 groups x 3 periods)")
check(period_ratios["period_ratio"].notna().all() and (period_ratios["period_ratio"] > 0).all(),
      "every period ratio exists and is above zero")

# Step 2: Rest of Canada compared with itself must be exactly 1
rest_relative = relative[relative["group"] == "Rest of Canada"]["relative_to_rest_of_canada"]
print("\nRest of Canada relative value in each period:", rest_relative.tolist())
check((rest_relative == 1).all(), "Rest of Canada's relative value is exactly 1 in every period")

# Quarterly version: 240 rows, blanks only in 2020Q2 and 2020Q3, Rest of Canada = 1 elsewhere
blank_quarterly = quarterly_relative[quarterly_relative["relative_to_rest_of_canada"].isna()]
check(len(quarterly_relative) == 240, "quarterly relative table has 240 rows (6 groups x 40 quarters)")
check(len(blank_quarterly) == 12 and blank_quarterly["quarter"].isin(["2020Q2", "2020Q3"]).all(),
      "quarterly relative values are blank in exactly 12 rows, all in 2020Q2 and 2020Q3")
rest_quarterly = quarterly_relative[quarterly_relative["group"] == "Rest of Canada"]["relative_to_rest_of_canada"].dropna()
check((rest_quarterly == 1).all(), "Rest of Canada's quarterly relative value is exactly 1 in every quarter with data")

# Step 3: the ratio of the averages equals the Step 1 period ratio. Line up each
# decomposition row with its Step 1 row (same group, "from" period) and compare.
lined_up = decomposition.merge(period_ratios, left_on=["group", "from_period"], right_on=["group", "period"])
check((lined_up["ratio_from"] - lined_up["period_ratio"]).abs().max() < 1e-12,
      "the ratio of average quarterly values equals the period ratio in every row")

# Step 3: the parts add up exactly (allowing only for tiny computer rounding)
largest_gap = (decomposition["vacancies_part"] + decomposition["unemployed_part"] - decomposition["log_change_ratio"]).abs().max()
print("\nLargest gap between (vacancies part + unemployed part) and the log change in the ratio:", largest_gap)
check(largest_gap < 1e-12, "the two decomposition parts add up to the total log change in every row")
check(((decomposition["vacancies_share"] + decomposition["unemployed_share"] - 1).abs() < 1e-12).all(),
      "the two shares add up to 1 in every row")
check((decomposition["log_change_ratio"].abs() > 0.001).all(),
      "no log change in the ratio is close to zero (so the shares are meaningful)")

# Step 4: 9 rows (3 provinces x 3 periods)
check(len(trajectory) == 9, "trajectory summary has 9 rows (3 provinces x 3 periods)")

# Step 5: 18 rows, no blanks
check(len(sensitivity) == 18 and sensitivity["ratio_average_of_quarters"].notna().all(),
      "sensitivity table has 18 rows with both methods filled in")

# --- Hand check: Saskatchewan 2023-2025 ---
print("\n--- Hand check: Saskatchewan, 2023-2025 ---")
sask = get_period_row("Saskatchewan", "2023-2025")
rest = get_period_row("Rest of Canada", "2023-2025")
print(f"Quarters: {sask['quarters']}")
print(f"Total vacancies: {sask['total_vacancies']:,.0f}")
print(f"Total unemployed: {sask['total_unemployed']:,.2f}")
print(f"Period ratio = {sask['total_vacancies']:,.0f} / {sask['total_unemployed']:,.2f} = {sask['period_ratio']:.4f}")
print(f"Rest of Canada period ratio = {rest['total_vacancies']:,.0f} / {rest['total_unemployed']:,.2f} = {rest['period_ratio']:.4f}")
print(f"Relative to Rest of Canada = {sask['period_ratio']:.4f} / {rest['period_ratio']:.4f} = "
      f"{sask['period_ratio'] / rest['period_ratio']:.4f}")

print("\nAll checks passed.")


# =====================================================================
# PART D: PRINT ALL OUTPUT TABLES (rounded to three decimals)
# =====================================================================
print("\n" + "=" * 70)
print("STEP 1: PERIOD RATIOS")
print("=" * 70)
print(period_ratios.round(3).to_string(index=False))

print("\n" + "=" * 70)
print("STEP 2: RELATIVE TO REST OF CANADA (above 1 = tighter, below 1 = looser)")
print("=" * 70)
print(relative.round(3).to_string(index=False))

print("\nQuarterly relative to Rest of Canada (240 rows):")
print(quarterly_relative.round(3).to_string(index=False))

print("\n" + "=" * 70)
print("STEP 3: DECOMPOSITION OF CHANGE (average quarterly values)")
print("=" * 70)
print(decomposition.round(3).to_string(index=False))

print("\n" + "=" * 70)
print("STEP 4: TRAJECTORY SUMMARY")
print("=" * 70)
print(trajectory.round(3).to_string(index=False))

print("\n" + "=" * 70)
print("STEP 5: SENSITIVITY CHECK ON THE AVERAGING METHOD")
print("=" * 70)
print(sensitivity.round(3).to_string(index=False))
changed = sensitivity[(sensitivity["group"].isin(PRAIRIE_PROVINCES)) & (sensitivity["position_changes"] == "yes")]
if len(changed) == 0:
    print("\nNo province's position relative to Rest of Canada (above or below 1) changes between the two methods.")
else:
    print("\nProvinces whose position relative to Rest of Canada changes between the two methods:")
    print(changed[["group", "period", "position_total_over_total", "position_average_of_quarters"]].to_string(index=False))


# =====================================================================
# PART E: SAVE THE TABLES
# This runs only if every check above passed (a failed check stops the script
# before reaching this point), so an unchecked table is never saved.
# =====================================================================
TABLE_FOLDER.mkdir(parents=True, exist_ok=True)
period_ratios.to_csv(TABLE_FOLDER / "period_ratios.csv", index=False)
relative.to_csv(TABLE_FOLDER / "relative_to_rest_of_canada.csv", index=False)
quarterly_relative.to_csv(TABLE_FOLDER / "quarterly_relative_to_rest_of_canada.csv", index=False)
decomposition.to_csv(TABLE_FOLDER / "decomposition.csv", index=False)
trajectory.to_csv(TABLE_FOLDER / "trajectory_summary.csv", index=False)
sensitivity.to_csv(TABLE_FOLDER / "sensitivity_averaging_method.csv", index=False)
print("\nSaved 6 tables to outputs/tables/")
