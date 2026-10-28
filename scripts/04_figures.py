# 04_figures.py
# Purpose: draw the three figures for the report and presentation.
#   Reads data/processed/group_quarter.csv and three tables in outputs/tables/
#   (period_ratios.csv, relative_to_rest_of_canada.csv, decomposition.csv). They are only read, never changed.
#   Writes, only after every check has passed:
#     outputs/tables/annual_ratios.csv
#     outputs/figures/fig1_tightness_over_time.png and .svg
#     outputs/figures/fig2_relative_to_rest_of_canada.png and .svg
#     outputs/figures/fig3_change_after_peak.png and .svg
# Run from the project folder with:  uv run python scripts/04_figures.py

import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw charts straight to files, without opening a window
import matplotlib.pyplot as plt
import pandas as pd

# Find the project folders, starting from where this script is saved
PROJECT_FOLDER = Path(__file__).parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"
TABLE_FOLDER = PROJECT_FOLDER / "outputs" / "tables"
FIGURE_FOLDER = PROJECT_FOLDER / "outputs" / "figures"

# The three provinces and the comparison group, always in this order
PROVINCES = ["Alberta", "Saskatchewan", "Manitoba"]
PLOTTED_GROUPS = PROVINCES + ["Rest of Canada"]

# One fixed colour per group, used in every figure. The three provinces take the first
# three slots of a colour-blind-checked palette (blue, orange, aqua). Rest of Canada is
# the benchmark, so it is a dark neutral grey rather than a fourth colour; a fourth colour
# from the palette failed the colour-blindness check against the other three.
GROUP_COLOURS = {
    "Alberta": "#2a78d6",
    "Saskatchewan": "#eb6834",
    "Manitoba": "#1baf7a",
    "Rest of Canada": "#52514e",
}

# The three comparison periods: name -> (first year, last year, label shown on the figures)
PERIODS = {
    "2016-2019": (2016, 2019, "2016 to 2019\npre-pandemic"),
    "2021-2022": (2021, 2022, "2021 to 2022\npost-pandemic peak"),
    "2023-2025": (2023, 2025, "2023 to 2025\ncooling"),
}

# Years shown in Figure 1. 2020 is in the list so that the lines break there.
YEARS = list(range(2016, 2026))

# Chart colours for background, text, shading and lines
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SHADE = "#f0efec"

# Two numbers count as equal if they differ by less than this (computer rounding only)
TOLERANCE = 1e-9

# The source and methodology note printed at the bottom of every figure
SOURCE_NOTE = (
    "Source: Statistics Canada, Table 14-10-0287-01 (Labour Force Survey) and Table 14-10-0442-01 "
    "(Job Vacancy and Wage Survey), unadjusted; author's calculations. Ratio = job vacancies (all industries) "
    "divided by unemployed persons aged 15 and over. Ten provinces; territories excluded. Rest of Canada = "
    "the seven provinces outside the Prairies. The Labour Force Survey excludes people living on reserves, "
    "the Canadian Armed Forces and the institutionalized population; vacancy counts exclude federal and "
    "provincial public administration."
)

# Figure 3 shows only vacancies, not the ratio, so its source note replaces the ratio sentence
RATIO_SENTENCE = "Ratio = job vacancies (all industries) divided by unemployed persons aged 15 and over."
FIGURE3_SOURCE_NOTE = SOURCE_NOTE.replace(RATIO_SENTENCE, "Job vacancies are for all industries.")

# Make the SVG files identical on every run: by default matplotlib gives the internal labels in
# each SVG random names. A fixed "salt" makes the names the same every time. (The save date is
# removed when saving, in Part F.)
plt.rcParams["svg.hashsalt"] = "04_figures"

# Show wide tables in full when printing
pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 100)


def check(passed, description):
    """Print PASS if a validation check is true, otherwise stop the script with an error."""
    if passed:
        print("PASS:", description)
    else:
        raise ValueError("CHECK FAILED: " + description)


def new_figure():
    """Create an empty figure with one chart area, in the background colour."""
    fig, ax = plt.subplots(figsize=(10, 7), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    # Keep only the left and bottom axis lines, in a light colour
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=SECONDARY, labelsize=9)
    return fig, ax


def add_title_legend_and_notes(fig, title, subtitle, figure_notes, legend_handles=None, legend_columns=1,
                               source_note=SOURCE_NOTE):
    """Add the title (main message), subtitle (technical description), legend (if any) and the notes at the bottom."""
    # Long titles are wrapped onto two lines; the subtitle and legend move down to make room
    title_lines = textwrap.wrap(title, width=80)
    fig.text(0.04, 0.965, "\n".join(title_lines), fontsize=13, fontweight="bold", color=TEXT, va="top")
    subtitle_top = 0.965 - 0.037 * len(title_lines) - 0.005
    fig.text(0.04, subtitle_top, subtitle, fontsize=10, color=SECONDARY, va="top")
    # The legend goes under the subtitle; a figure without a legend starts its chart area there instead
    legend_top = subtitle_top - 0.045
    if legend_handles is not None:
        fig.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(0.04, legend_top),
                   ncol=legend_columns, frameon=False, fontsize=9)
    else:
        legend_top = subtitle_top
    # The source note comes first, then the notes for this figure, wrapped to the figure width
    note_lines = textwrap.wrap(source_note, width=175)
    for note in figure_notes:
        note_lines += textwrap.wrap("Note: " + note, width=175)
    fig.text(0.04, 0.02, "\n".join(note_lines), fontsize=7, color=SECONDARY, va="bottom", linespacing=1.4)
    # Leave room for the title, the legend and the notes around the chart area
    fig.subplots_adjust(left=0.09, right=0.96, top=legend_top - 0.07, bottom=0.12 + 0.022 * len(note_lines))


# Read the input files (reading does not change them)
groups = pd.read_csv(PROCESSED_FOLDER / "group_quarter.csv")
period_ratios = pd.read_csv(TABLE_FOLDER / "period_ratios.csv")
relative = pd.read_csv(TABLE_FOLDER / "relative_to_rest_of_canada.csv")
decomposition = pd.read_csv(TABLE_FOLDER / "decomposition.csv")

# Every value drawn is recorded here, so it can be printed and compared with the tables
plotted_values = []


# =====================================================================
# PART A: ANNUAL RATIOS FOR FIGURE 1
# =====================================================================
print("=" * 70)
print("PART A: ANNUAL RATIOS")
print("=" * 70)

# Keep the four groups shown in Figure 1
rows = groups[groups["group"].isin(PLOTTED_GROUPS)]

# For each group and year: count the quarters with vacancy data, and add up vacancies and unemployed.
# "count" counts only quarters that have a value, so 2020 has 2 (Q1 and Q4).
annual_all_years = rows.groupby(["group", "year"], as_index=False).agg(
    quarters_with_data=("vacancies", "count"),
    total_vacancies=("vacancies", "sum"),
    total_unemployed=("unemployed", "sum"),
)

# Check 1: every year except 2020 has all 4 quarters of vacancy data; 2020 has only 2
not_2020 = annual_all_years[annual_all_years["year"] != 2020]
year_2020 = annual_all_years[annual_all_years["year"] == 2020]
check((not_2020["quarters_with_data"] == 4).all(), "every year except 2020 has exactly 4 quarters of vacancy data")
check((year_2020["quarters_with_data"] == 2).all(), "2020 has only 2 quarters of vacancy data in every group")

# Keep only years with all 4 quarters. This removes 2020: adding up 2 quarters of vacancies
# and 4 quarters of unemployed would not give a meaningful annual ratio.
annual = annual_all_years[annual_all_years["quarters_with_data"] == 4].copy()
annual["annual_ratio"] = annual["total_vacancies"] / annual["total_unemployed"]
annual = annual.rename(columns={"quarters_with_data": "quarters"})

# Check 2: 2020 is not in the annual table, which has 9 years for each of the 4 groups
check(2020 not in annual["year"].values, "2020 is not in the annual ratio table")
check(len(annual) == 9 * len(PLOTTED_GROUPS), f"annual table has {len(annual)} rows (9 years x 4 groups = 36)")

# Check 3: adding up the annual totals for the years in each period gives the same totals
# as period_ratios.csv, so Figure 1 and the period tables are built from the same numbers
for period_name, (first_year, last_year, label) in PERIODS.items():
    in_period = annual[annual["year"].between(first_year, last_year)]
    summed = in_period.groupby("group")[["total_vacancies", "total_unemployed"]].sum()
    from_table = period_ratios[period_ratios["period"] == period_name].set_index("group").loc[PLOTTED_GROUPS]
    gap = (summed.loc[PLOTTED_GROUPS] - from_table[["total_vacancies", "total_unemployed"]]).abs().max().max()
    check(gap < 1e-6, f"{period_name}: annual totals add up to the totals in period_ratios.csv")

print("\nAnnual ratios (job vacancies per unemployed person):")
print(annual.pivot(index="year", columns="group", values="annual_ratio")[PLOTTED_GROUPS].round(3).to_string())


# =====================================================================
# PART B: FIGURE 1, TIGHTNESS OVER TIME
# =====================================================================
fig1, ax1 = new_figure()

# Lightly shade the three comparison periods and label each one at the top
for period_name, (first_year, last_year, label) in PERIODS.items():
    ax1.axvspan(first_year - 0.4, last_year + 0.4, color=SHADE, linewidth=0, zorder=0)
    ax1.text((first_year + last_year) / 2, 1.03, label, ha="center", va="top", fontsize=8.5, color=SECONDARY)

# Mark 2020 on the chart, where the lines break
ax1.text(2020, 0.03, "2020\nomitted", ha="center", va="bottom", fontsize=8, color=MUTED)

# Faint horizontal gridlines only, to help read values off the y-axis
ax1.grid(axis="y", color=GRID, linewidth=0.6)
ax1.set_axisbelow(True)

# One line per group. Reindexing to all years puts a blank in 2020, so the line breaks there.
figure1_lines = {}
for group_name in PLOTTED_GROUPS:
    series = annual[annual["group"] == group_name].set_index("year")["annual_ratio"].reindex(YEARS)
    line, = ax1.plot(series.index, series.values, color=GROUP_COLOURS[group_name], linewidth=2,
                     marker="o", markersize=5, label=group_name, zorder=3)
    figure1_lines[group_name] = line

# Name each line at its right end (2025). Labels closer than 0.045 are moved apart so they do not overlap.
end_values = sorted((figure1_lines[g].get_ydata()[-1], g) for g in PLOTTED_GROUPS)
label_heights = []
for value, group_name in end_values:
    height = value if not label_heights else max(value, label_heights[-1] + 0.045)
    label_heights.append(height)
    ax1.text(2025.25, height, group_name, va="center", fontsize=9, color=TEXT)

# Axes, legend and text
ax1.set_xlim(2015.5, 2026.3)
ax1.set_xticks(YEARS)
ax1.set_ylim(0, 1.05)
ax1.set_ylabel("Job vacancies per unemployed person (annual)", fontsize=10, color=TEXT)
add_title_legend_and_notes(
    fig1,
    "Labour market tightness peaked in 2022 and has eased since; Saskatchewan has been the tightest since 2023",
    "Job vacancies per unemployed person, Alberta, Saskatchewan, Manitoba and the rest of Canada, annual, 2016 to 2025",
    ["Annual ratio = total vacancies divided by total unemployed over the four quarters of each year. "
     "Shaded areas are the three comparison periods.",
     "2020 omitted: vacancy data not collected in Q2 and Q3."],
    list(figure1_lines.values()), 4,
)


# =====================================================================
# PART C: FIGURE 2, TIGHTNESS RELATIVE TO THE REST OF CANADA
# =====================================================================
fig2, ax2 = new_figure()

period_names = list(PERIODS)
bar_width = 0.2

# Four bars in each period group: the three provinces, then the Prairies combined. The Prairies bar is
# light grey with diagonal hatching, so it reads as a combined figure rather than a fourth province.
FIGURE2_GROUPS = PROVINCES + ["Prairies"]
bar_styles = {province: {"color": GROUP_COLOURS[province], "label": province} for province in PROVINCES}
bar_styles["Prairies"] = {"color": "#c3c2b7", "hatch": "///", "hatchcolor": SECONDARY, "label": "Prairies combined"}

# A thin background-coloured edge separates the bars
figure2_bars = {}
for i, group_name in enumerate(FIGURE2_GROUPS):
    values = [relative[(relative["group"] == group_name) & (relative["period"] == p)]["relative_to_rest_of_canada"].iloc[0]
              for p in period_names]
    positions = [p + (i - 1.5) * bar_width for p in range(len(period_names))]
    bars = ax2.bar(positions, values, width=bar_width, edgecolor=SURFACE, linewidth=1.5, zorder=2,
                   **bar_styles[group_name])
    # Label each bar with its value to two decimals. The labels have a background so the line at 1
    # does not run through them.
    value_labels = ax2.bar_label(bars, labels=[f"{v:.2f}" for v in values], padding=3, fontsize=9, color=TEXT,
                                 zorder=4)
    for value_label in value_labels:
        value_label.set_bbox(dict(facecolor=SURFACE, edgecolor="none", pad=1))
    figure2_bars[group_name] = bars

# Reference line at 1: the rest of Canada. Above the line = tighter, below = looser.
ax2.axhline(1, color=GROUP_COLOURS["Rest of Canada"], linewidth=1.5, linestyle="--", zorder=3)
ax2.text(2.45, 1.015, "Rest of Canada = 1", ha="left", va="bottom", fontsize=9, color=TEXT)
ax2.text(2.45, 1.12, "Above the line:\ntighter than the\nrest of Canada", ha="left", va="bottom",
         fontsize=8, color=SECONDARY)
ax2.text(2.45, 0.96, "Below the line:\nlooser than the\nrest of Canada", ha="left", va="top",
         fontsize=8, color=SECONDARY)

# Axes, legend and text. The y-axis starts at zero.
ax2.set_xticks(range(len(period_names)))
ax2.set_xticklabels([PERIODS[p][2] for p in period_names], fontsize=9.5, color=TEXT)
ax2.tick_params(axis="x", length=0)
ax2.set_xlim(-0.5, 3.1)
ax2.set_ylim(0, 1.6)
ax2.set_ylabel("Tightness relative to the rest of Canada (rest of Canada = 1)", fontsize=10, color=TEXT)
add_title_legend_and_notes(
    fig2,
    "Saskatchewan and Manitoba went from looser to tighter than the rest of Canada; Alberta stayed looser",
    "Job vacancies per unemployed person in each province, divided by the same ratio for the rest of Canada, by period",
    ["Period values are total vacancies divided by total unemployed over each period. "
     "Prairies combined = total Prairie vacancies divided by total Prairie unemployed, "
     "not an average of the three provinces."],
    list(figure2_bars.values()), 4,
)


# =====================================================================
# PART D: FIGURE 3, WHAT CHANGED AFTER THE PEAK
# =====================================================================
fig3, ax3 = new_figure()

# Keep the change from 2021-2022 to 2023-2025 for the four groups, in the fixed order
after_peak = decomposition[(decomposition["from_period"] == "2021-2022") & (decomposition["to_period"] == "2023-2025")]
after_peak = after_peak.set_index("group").loc[PLOTTED_GROUPS]

# One bar per group: the percentage change in average quarterly vacancies, in the group's colour
figure3_bars = {}
for i, group_name in enumerate(PLOTTED_GROUPS):
    vacancies_change = after_peak.loc[group_name, "pct_change_vacancies"]
    bar = ax3.bar(i, vacancies_change, width=0.6, color=GROUP_COLOURS[group_name], zorder=2)
    # Label each bar with its value to one decimal, with a + or - sign
    ax3.bar_label(bar, labels=[f"{vacancies_change:+.1f}%"], padding=3, fontsize=9, color=TEXT)
    figure3_bars[group_name] = bar

# Line at zero: bars below it fell
ax3.axhline(0, color=SECONDARY, linewidth=1, zorder=3)

# Axes and text. The groups are named on the x-axis, so no legend is needed.
ax3.set_xticks(range(len(PLOTTED_GROUPS)))
ax3.set_xticklabels(PLOTTED_GROUPS, fontsize=10, color=TEXT)
ax3.tick_params(axis="x", length=0)
ax3.set_ylim(-38, 5)
ax3.set_ylabel("Change in average quarterly job vacancies (%)", fontsize=10, color=TEXT)
add_title_legend_and_notes(
    fig3,
    "After the peak, vacancies fell by a third in the rest of Canada but barely changed in Saskatchewan",
    "Percentage change in average quarterly job vacancies, 2021 to 2022 compared with 2023 to 2025",
    ["Change in average quarterly levels between 2021 to 2022 and 2023 to 2025. "
     "Unemployment changed by less than 6% in every group."],
    source_note=FIGURE3_SOURCE_NOTE,
)


# =====================================================================
# PART E: CHECK EVERY PLOTTED VALUE AGAINST THE TABLES
# =====================================================================
print("\n" + "=" * 70)
print("PART E: VALIDATION CHECKS ON THE FIGURES")
print("=" * 70)

# --- Figure 1: read the values back from the drawn lines ---
for group_name, line in figure1_lines.items():
    table_rows = annual[annual["group"] == group_name].set_index("year")["annual_ratio"]
    for year, value in zip(line.get_xdata(), line.get_ydata()):
        if year == 2020:
            # Check 4: 2020 is blank in the line, so nothing is drawn for it
            check(pd.isna(value), f"Figure 1, {group_name}: 2020 is not plotted")
            continue
        plotted_values.append({"figure": "Figure 1", "group": group_name, "point": str(year),
                               "measure": "annual ratio", "plotted": value, "table": table_rows.loc[year]})

# --- Figure 2: read the bar heights back from the drawn bars ---
for group_name, bars in figure2_bars.items():
    for period_name, bar in zip(period_names, bars):
        table_value = relative[(relative["group"] == group_name) & (relative["period"] == period_name)][
            "relative_to_rest_of_canada"].iloc[0]
        plotted_values.append({"figure": "Figure 2", "group": group_name, "point": period_name,
                               "measure": "relative to Rest of Canada", "plotted": bar.get_height(),
                               "table": table_value})

# --- Figure 3: read the bar heights back from the drawn bars ---
for group_name, bar in figure3_bars.items():
    table_row = decomposition[(decomposition["group"] == group_name) & (decomposition["from_period"] == "2021-2022")
                              & (decomposition["to_period"] == "2023-2025")].iloc[0]
    plotted_values.append({"figure": "Figure 3", "group": group_name, "point": "2021-2022 to 2023-2025",
                           "measure": "% change vacancies", "plotted": bar[0].get_height(),
                           "table": table_row["pct_change_vacancies"]})

plotted = pd.DataFrame(plotted_values)
plotted["difference"] = (plotted["plotted"] - plotted["table"]).abs()

# Check 5: the expected number of values was drawn (36 points, 12 bars, 4 bars)
counts = plotted["figure"].value_counts()
check(counts["Figure 1"] == 36, f"Figure 1 has {counts['Figure 1']} plotted points (9 years x 4 groups)")
check(counts["Figure 2"] == 12, f"Figure 2 has {counts['Figure 2']} bars (3 periods x 3 provinces + Prairies combined)")
figure2_prairies = plotted[(plotted["figure"] == "Figure 2") & (plotted["group"] == "Prairies")]
check(len(figure2_prairies) == 3, "Figure 2 has a Prairies combined bar in each of the 3 periods")
check(counts["Figure 3"] == 4, f"Figure 3 has {counts['Figure 3']} bars (1 per group)")

# Check 6: every plotted value matches its table value
for figure_name in ["Figure 1", "Figure 2", "Figure 3"]:
    largest_gap = plotted[plotted["figure"] == figure_name]["difference"].max()
    check(largest_gap < TOLERANCE, f"{figure_name}: every plotted value matches the table (largest gap {largest_gap:.1e})")

# Check 7: no plotted point in Figure 1 is from 2020
check("2020" not in plotted[plotted["figure"] == "Figure 1"]["point"].values, "Figure 1 has no plotted point in 2020")

# Check 8: Figure 3's source note has the ratio sentence replaced, and everything else is the same
check(RATIO_SENTENCE in SOURCE_NOTE and RATIO_SENTENCE not in FIGURE3_SOURCE_NOTE
      and "Job vacancies are for all industries." in FIGURE3_SOURCE_NOTE,
      "Figure 3 source note: ratio sentence replaced with 'Job vacancies are for all industries.'")

# Check 9: the statements written in the figure notes are correct.
# Figure 2: the Prairies combined value is total Prairie vacancies divided by total Prairie unemployed,
# which is not the same as the average of the three provinces' ratios.
for period_name in period_names:
    in_period = period_ratios[period_ratios["period"] == period_name].set_index("group")
    totals_ratio = in_period.loc[PROVINCES, "total_vacancies"].sum() / in_period.loc[PROVINCES, "total_unemployed"].sum()
    average_of_provinces = in_period.loc[PROVINCES, "period_ratio"].mean()
    prairies_ratio = in_period.loc["Prairies", "period_ratio"]
    check(abs(prairies_ratio - totals_ratio) < TOLERANCE and abs(prairies_ratio - average_of_provinces) > 0.001,
          f"Figure 2 note, {period_name}: Prairies ratio {prairies_ratio:.4f} = totals {totals_ratio:.4f}, "
          f"not the average of the provinces {average_of_provinces:.4f}")
# Figure 3: unemployment changed by less than 6% in every group
largest_unemployed_change = after_peak["pct_change_unemployed"].abs().max()
check(largest_unemployed_change < 6,
      f"Figure 3 note: unemployment changed by less than 6% in every group (largest {largest_unemployed_change:.1f}%)")

# Check 10: each title's statement is true in the data
ratio_by_year = annual.pivot(index="year", columns="group", values="annual_ratio")
for group_name in PLOTTED_GROUPS:
    peak_year = ratio_by_year[group_name].idxmax()
    falling = ratio_by_year.loc[2022:2025, group_name].is_monotonic_decreasing
    check(peak_year == 2022 and falling, f"Figure 1 title: {group_name} peaked in 2022 and fell every year after")
for year in [2023, 2024, 2025]:
    check(ratio_by_year.loc[year].idxmax() == "Saskatchewan", f"Figure 1 title: Saskatchewan is the tightest in {year}")

relative_by_period = relative.pivot(index="group", columns="period", values="relative_to_rest_of_canada")
for province in ["Saskatchewan", "Manitoba"]:
    went_tighter = (relative_by_period.loc[province, ["2016-2019", "2021-2022"]] < 1).all() \
        and relative_by_period.loc[province, "2023-2025"] > 1
    check(went_tighter, f"Figure 2 title: {province} was below 1 before 2023 and above 1 in 2023-2025")
check((relative_by_period.loc["Alberta"] < 1).all(), "Figure 2 title: Alberta is below 1 in all three periods")

# "Fell by a third" is taken to mean a fall of between 30% and 36.7% (one third, give or take 10% of it);
# "barely changed" is taken to mean a change of less than 2% either way
rest_of_canada_change = after_peak.loc["Rest of Canada", "pct_change_vacancies"]
saskatchewan_change = after_peak.loc["Saskatchewan", "pct_change_vacancies"]
check(-36.7 < rest_of_canada_change < -30,
      f"Figure 3 title: Rest of Canada vacancies fell by about a third ({rest_of_canada_change:.1f}%)")
check(abs(saskatchewan_change) < 2,
      f"Figure 3 title: Saskatchewan vacancies barely changed ({saskatchewan_change:.1f}%)")

# Print every plotted value, so it can be compared with the tables by hand
print("\nEvery plotted value, with the matching table value:")
print(plotted.round(4).to_string(index=False))


# =====================================================================
# PART F: SAVE (only reached if every check above has passed)
# =====================================================================
FIGURE_FOLDER.mkdir(parents=True, exist_ok=True)

annual = annual[["group", "year", "quarters", "total_vacancies", "total_unemployed", "annual_ratio"]]
annual.to_csv(TABLE_FOLDER / "annual_ratios.csv", index=False)
print("\nSaved outputs/tables/annual_ratios.csv")

figures = {
    "fig1_tightness_over_time": fig1,
    "fig2_relative_to_rest_of_canada": fig2,
    "fig3_change_after_peak": fig3,
}
for file_name, fig in figures.items():
    fig.savefig(FIGURE_FOLDER / f"{file_name}.png", dpi=300, facecolor=SURFACE)
    # "Date": None leaves the save date out of the SVG, so rerunning does not change the file
    fig.savefig(FIGURE_FOLDER / f"{file_name}.svg", facecolor=SURFACE, metadata={"Date": None})
    plt.close(fig)
    print(f"Saved outputs/figures/{file_name}.png and .svg")
