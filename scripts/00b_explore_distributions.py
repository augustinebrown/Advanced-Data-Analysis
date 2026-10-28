# 00b_explore_distributions.py
# Purpose: look at the distributions of unemployed, vacancies and ratio, and flag
# possible outliers, before the analysis. This script is exploratory only:
#   - it reads data/processed/merged_province_quarter.csv and group_quarter.csv
#   - it does not change any file in data/, and it does not remove or change any observation
#   - it saves two charts to outputs/figures/exploratory/
#   - Part B2 checks numbers quoted in the documentation and stops with an error if one does not match
# Run from the project folder with:  uv run python scripts/00b_explore_distributions.py

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw charts straight to files, without opening a window
import matplotlib.pyplot as plt
import pandas as pd

# Find the project folders, starting from where this script is saved
PROJECT_FOLDER = Path(__file__).parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"
FIGURE_FOLDER = PROJECT_FOLDER / "outputs" / "figures" / "exploratory"

# A quarter is flagged if its ratio is more than 50% above or below the previous available quarter
CHANGE_THRESHOLD = 0.50

# The six groups in a fixed order, each with a fixed colour (the first six slots of a
# colour-blind-checked palette). The three combined groups are dashed, so lines can be
# told apart without relying on colour alone.
GROUP_STYLES = {
    "Alberta": ("#2a78d6", "-"),
    "Saskatchewan": ("#eb6834", "-"),
    "Manitoba": ("#1baf7a", "-"),
    "Prairies": ("#eda100", "--"),
    "Rest of Canada": ("#e87ba4", "--"),
    "Canada": ("#008300", "--"),
}

# Chart colours for background, text and gridlines
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"

# Show wide tables on one line when printing
pd.set_option("display.width", 200)


def check(passed, description):
    """Print PASS if a validation check is true, otherwise stop the script with an error."""
    if passed:
        print("PASS:", description)
    else:
        raise ValueError("CHECK FAILED: " + description)


# Read the two processed files (reading does not change them)
merged = pd.read_csv(PROCESSED_FOLDER / "merged_province_quarter.csv")
groups = pd.read_csv(PROCESSED_FOLDER / "group_quarter.csv")


# =====================================================================
# PART A: SUMMARY STATISTICS FOR EACH PROVINCE
# =====================================================================
print("=" * 70)
print("SUMMARY STATISTICS BY PROVINCE, 2016Q1 TO 2025Q4")
print("=" * 70)
print("count = quarters with a value (vacancies and ratio are blank in 2020Q2 and 2020Q3)")

# For each measure, calculate the statistics for each province
for column in ["unemployed", "vacancies", "ratio"]:
    summary = merged.groupby("province")[column].agg(["count", "mean", "median", "min", "max", "std"])
    # Ratios are small numbers, so show 3 decimals; persons and vacancies as whole numbers
    decimals = 3 if column == "ratio" else 0
    print(f"\n--- {column} ---")
    print(summary.round(decimals).to_string())


# =====================================================================
# PART B: FLAG POSSIBLE OUTLIERS
# =====================================================================
print("\n" + "=" * 70)
print("POSSIBLE OUTLIERS")
print("=" * 70)

# 1. Quarters whose ratio is more than 50% above or below the previous available quarter
flagged_tables = []
for province, rows in merged.groupby("province"):
    # Keep only quarters that have a ratio, in time order. Because 2020Q2 and 2020Q3
    # are blank, 2020Q4 is compared with 2020Q1 (the previous available quarter).
    rows = rows.dropna(subset=["ratio"]).sort_values("quarter")
    # .shift(1) moves each value down one row, so each quarter sits next to the one before it
    rows["previous_quarter"] = rows["quarter"].shift(1)
    rows["previous_ratio"] = rows["ratio"].shift(1)
    rows["change_pct"] = (rows["ratio"] / rows["previous_ratio"] - 1) * 100
    flagged_tables.append(rows[rows["change_pct"].abs() > CHANGE_THRESHOLD * 100])

flagged = pd.concat(flagged_tables)
print(f"\nQuarters where the ratio changed by more than {CHANGE_THRESHOLD:.0%} from the previous available quarter:",
      len(flagged))
if len(flagged) > 0:
    print(flagged[["province", "previous_quarter", "previous_ratio", "quarter", "ratio",
                   "change_pct", "vacancy_quality_flag"]].round(3).to_string(index=False))

# 2. The highest and lowest ratio for each province (blank quarters are skipped)
highest = merged.loc[merged.groupby("province")["ratio"].idxmax(), ["province", "quarter", "ratio"]]
lowest = merged.loc[merged.groupby("province")["ratio"].idxmin(), ["province", "quarter", "ratio"]]
print("\nHighest ratio for each province:")
print(highest.round(3).to_string(index=False))
print("\nLowest ratio for each province:")
print(lowest.round(3).to_string(index=False))


# =====================================================================
# PART B2: CHECKS ON NUMBERS QUOTED IN THE DOCUMENTATION
# =====================================================================
# Each check recalculates a number quoted in docs/data_dictionary.md or docs/research_log.md
# and stops with an error if it does not match.
print("\n" + "=" * 70)
print("NUMBERS QUOTED IN THE DOCUMENTATION")
print("=" * 70)

# Range of the provincial ratio (data dictionary): 0.067 to 1.34
check(round(merged["ratio"].min(), 3) == 0.067 and round(merged["ratio"].max(), 2) == 1.34,
      f"provincial ratio ranges from {merged['ratio'].min():.3f} to {merged['ratio'].max():.2f}")

# Outlier flags (research log): every flagged quarter is graded A, B or C; the largest jump is
# Prince Edward Island 2018Q2 (+204%); PEI's smallest quarterly vacancy count is 770
check(flagged["vacancy_quality_flag"].isin(["A", "B", "C"]).all(), "every flagged quarter is graded A, B or C")
largest_jump = flagged.loc[flagged["change_pct"].idxmax()]
check(largest_jump["province"] == "Prince Edward Island" and largest_jump["quarter"] == "2018Q2"
      and round(largest_jump["change_pct"]) == 204, "largest flagged jump: Prince Edward Island 2018Q2, +204%")
check(merged[merged["province"] == "Prince Edward Island"]["vacancies"].min() == 770,
      "Prince Edward Island's smallest quarterly vacancy count is 770")

# 2021Q1 to 2022Q4 (research log): all 80 province-quarters graded A (69) or B (11)
peak_years = merged[merged["quarter"].between("2021Q1", "2022Q4")]
peak_grades = peak_years["vacancy_quality_flag"].value_counts()
check(len(peak_years) == 80 and peak_grades.get("A", 0) == 69 and peak_grades.get("B", 0) == 11,
      "2021Q1 to 2022Q4: 80 province-quarters, 69 graded A and 11 graded B")

# Each province's highest-ratio quarter is graded A or B (research log)
peak_rows = merged.loc[merged.groupby("province")["ratio"].idxmax()]
check(peak_rows["vacancy_quality_flag"].isin(["A", "B"]).all(), "every province's peak ratio quarter is graded A or B")

# Provinces peaking in 2022Q2. The research log says "8 of 10 provinces peak in 2022Q2":
# that is true for vacancies (8); for the ratio it is 7.
vacancy_peaks = merged.loc[merged.groupby("province")["vacancies"].idxmax(), "quarter"]
ratio_peaks = peak_rows["quarter"]
print("\nQuarter of each province's highest vacancies:", vacancy_peaks.value_counts().to_dict())
print("Quarter of each province's highest ratio:", ratio_peaks.value_counts().to_dict())
check((vacancy_peaks == "2022Q2").sum() == 8, "8 of 10 provinces have their highest vacancies in 2022Q2")
check((ratio_peaks == "2022Q2").sum() == 7, "7 of 10 provinces have their highest ratio in 2022Q2")


# =====================================================================
# PART C: EXPLORATORY CHARTS
# =====================================================================
# Create the output folder if it does not exist yet (this writes only to outputs/)
FIGURE_FOLDER.mkdir(parents=True, exist_ok=True)

# Position each quarter on a time axis: 2019Q1 -> 2019.0, 2019Q2 -> 2019.25, and so on
groups["x"] = groups["year"] + (groups["quarter_number"] - 1) / 4

# --- Chart 1: quarterly ratio for the six groups ---
fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=SURFACE)
ax.set_facecolor(SURFACE)

# Shade the two quarters with no vacancy data. The lines break there by themselves,
# because the ratio is blank (not zero) and matplotlib does not draw through blanks.
ax.axvspan(2020.125, 2020.625, color=GRID, alpha=0.6, linewidth=0)
ax.text(2020.375, 0.97, "2020Q2 to Q3:\nno vacancy data\n(not collected,\nnot imputed)",
        ha="center", va="top", fontsize=8, color=MUTED)

# Reference line: a ratio of 1 means one vacancy per unemployed person
ax.axhline(1, color=MUTED, linewidth=1, linestyle=":")
ax.text(2016, 1.01, "1 vacancy per unemployed person", fontsize=8, color=MUTED, va="bottom")

# One line per group, in the fixed order and colours above
for group_name, (colour, line_style) in GROUP_STYLES.items():
    rows = groups[groups["group"] == group_name].sort_values("x")
    ax.plot(rows["x"], rows["ratio"], color=colour, linestyle=line_style, linewidth=2, label=group_name)

# Axes, labels and a light grid
ax.set_title("Quarterly vacancy-to-unemployment ratio, 2016Q1 to 2025Q4 (exploratory)",
             loc="left", fontsize=12, color=TEXT)
ax.set_ylabel("Vacancies per unemployed person", color=TEXT)
ax.set_xticks(range(2016, 2026))
ax.set_ylim(0, 1.1)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.tick_params(colors=MUTED)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
for side in ["left", "bottom"]:
    ax.spines[side].set_color(GRID)
ax.legend(ncol=3, frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0, -0.08))
fig.text(0.01, 0.01, "Source: Statistics Canada, Tables 14-10-0287-01 and 14-10-0442-01. Not seasonally adjusted. "
         "Prairies, Rest of Canada and Canada are dashed.", fontsize=7, color=MUTED)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(FIGURE_FOLDER / "ratio_by_group_quarterly.png", dpi=150, facecolor=SURFACE)
plt.close(fig)
print("\nSaved outputs/figures/exploratory/ratio_by_group_quarterly.png")

# --- Chart 2: histogram of the quarterly ratio across all provinces ---
ratios = merged["ratio"].dropna()
fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=SURFACE)
ax.set_facecolor(SURFACE)

# Bars 0.05 wide, from 0 to 1.40; a thin gap between bars in the background colour
bins = [i * 0.05 for i in range(0, 29)]
ax.hist(ratios, bins=bins, color="#2a78d6", edgecolor=SURFACE, linewidth=1.5)
ax.axvline(1, color=MUTED, linewidth=1, linestyle=":")
ax.text(1.01, ax.get_ylim()[1] * 0.95, "1 vacancy per\nunemployed person", fontsize=8, color=MUTED, va="top")

ax.set_title(f"Quarterly ratio, all 10 provinces ({len(ratios)} province-quarters, exploratory)",
             loc="left", fontsize=12, color=TEXT)
ax.set_xlabel("Vacancies per unemployed person", color=TEXT)
ax.set_ylabel("Number of province-quarters", color=TEXT)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.tick_params(colors=MUTED)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
for side in ["left", "bottom"]:
    ax.spines[side].set_color(GRID)
fig.tight_layout()
fig.savefig(FIGURE_FOLDER / "ratio_histogram_provinces.png", dpi=150, facecolor=SURFACE)
plt.close(fig)
print("Saved outputs/figures/exploratory/ratio_histogram_provinces.png")
