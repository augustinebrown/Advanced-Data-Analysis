# Research Log

A dated record of what I did, the decisions I made and why, problems I ran into, and any AI-generated code I reviewed. Newest entries go at the bottom.

<!--
TEMPLATE: copy this block for each new day.

## YYYY-MM-DD

### What I did
-

### Decisions and reasons
-

### Problems encountered
-

### AI-generated code I reviewed and how I checked it
-
-->

## 2026-10-26

### What I did
- Read README.md to confirm the planned project structure and methods.
- Created the folder structure: `data/raw`, `data/processed`, `scripts`, `outputs/figures`, `outputs/tables`, `docs`.
- Moved `CA_Labour_Force_Monthly.csv` and `CA_Job_Vacancies_Wages_Quarterly.csv` into `data/raw/`.
- Created `requirements.txt` (pandas, matplotlib), this research log, a blank data dictionary template, and a `.gitignore`.

### Decisions and reasons
- Raw data files are kept in `data/raw/` and will never be modified by any script, so the analysis can always be re-run from the original Statistics Canada files.
- Added empty `.gitkeep` files to folders that are empty for now, because Git does not track empty folders.

### Problems encountered
- Python and Git were not installed on this computer. Installed uv (0.13.6) to manage Python and GitHub Desktop (3.6.10), which includes Git (2.56). Used uv to create a project virtual environment (`.venv`) with Python 3.12.16 and installed pandas 3.1.0 and matplotlib 3.11.2. Pinned these versions in `requirements.txt` so results can be reproduced.
- The quarterly vacancy file records dates as months (e.g. `2015-01`), not as quarters. To be confirmed in the inspection step.

### AI-generated code I reviewed and how I checked it
- Setup files (folders, requirements.txt, .gitignore, this log) were created by Claude Code. I checked that the folder structure matches README.md and that both CSV files are in `data/raw/` with unchanged file sizes.

## 2026-10-27 (Day 1, continued: setup and inspection)

### What I did
- Installed uv and GitHub Desktop, created the `.venv` environment, and pinned package versions in `requirements.txt`.
- Initialized the Git repository and made the first commit. Deleted two empty, unused files (`sample.md`, `sample.py`).
- Added `.gitattributes` so Git never changes the raw CSV files (including line endings).
- Wrote and ran `scripts/00_inspect_data.py`, which only reads and prints summaries of both raw files.

### Decisions and reasons
- Raw data is committed to the repository (about 12 MB, open licence) so the project can be reproduced from a fresh copy.
- The inspection script does not save or change anything, so it can be re-run at any time without risk.

### Problems encountered
- None blocking. Findings from the inspection:
  - Labour Force Survey: 69,696 rows = 11 regions x 6 characteristics x 4 age groups x 2 data types x 132 months, so the table is complete. Jan 2015 to Dec 2025, no missing values, no duplicates, no territories.
  - Job Vacancy and Wage Survey: 49,392 rows = 14 regions x 21 industries x 4 statistics x 42 quarters. Quarters are labelled by their first month (2015-01 = Q1). Q2 and Q3 2020 (2020-04, 2020-07) are absent from the file entirely, not blank.
  - 9,567 blank `VALUE` cells, exactly matching the STATUS codes F (7,099) + x (1,987) + .. (481). 475 rows have no STATUS flag. Flags for the specific rows used in the analysis still need checking.

### AI-generated code I reviewed and how I checked it
- `scripts/00_inspect_data.py` (written by Claude Code). Checks: confirmed it only uses `pd.read_csv` and print statements, with no writing or saving. Compared file hashes of both raw CSVs before and after running it (unchanged). Checked that row counts equal the product of the category counts, and that the blank VALUE count equals the F + x + .. STATUS counts.

## 2026-10-27 (Day 2: cleaning and merging)

### What I did
- Wrote `scripts/01_clean.py` to filter and reshape each raw dataset and save two cleaned files in `data/processed/`.
- First run stopped at the check "no missing values in vacancies": 2 of 420 rows were blank. Deleted the two files that run had saved, changed the script (see decisions below) and reran it. All checks passed.
- Wrote and ran `scripts/02_merge_and_ratio.py`, which joins the two cleaned files, calculates the vacancy-to-unemployment ratio, and builds six comparison groups. Saves `merged_province_quarter.csv` and `group_quarter.csv`. All checks passed.
- Filled in `docs/data_dictionary.md` and updated the "Data preparation" and "Key data decisions" sections of README.md.

### Decisions and reasons

**Cleaning the Labour Force Survey (`01_clean.py`)**
- Keep "Unemployment", "15 years and over", "Unadjusted". Unadjusted because the vacancy data is not seasonally adjusted, so both series are on the same basis.
- Drop the published "Canada" row. National and regional totals are built from the ten provinces so they are defined the same way for both surveys.
- Multiply `VALUE` by 1,000 to convert thousands of persons to persons, matching the vacancy units. Monthly values are rounded to whole persons only to remove tiny computer arithmetic errors (raw values have one decimal in thousands, so nothing real changes).
- Quarterly unemployment = average of the three months in the quarter. The script stops if any province-quarter does not use exactly 3 months. The quarterly average is not rounded, to avoid adding rounding error.

**Cleaning the Job Vacancy and Wage Survey (`01_clean.py`)**
- Keep "Job vacancies" for "Total, all industries".
- Drop the "Canada" row and the three territories. The LFS does not cover the territories, and the published Canada vacancy total includes them, so it is not comparable with the LFS.
- `REF_DATE` is the first month of each quarter (`2015-04` = 2015Q2). The script checks that only months 01, 04, 07 and 10 appear before converting.
- Vacancies are already in persons, so they are not rescaled. Statistics Canada quality flags are kept as `vacancy_quality_flag`.
- **Keep the two blank vacancy rows (Newfoundland and Labrador 2015Q1, Prince Edward Island 2015Q1) as missing, not zero, not dropped, not estimated.** Statistics Canada graded both F ("too unreliable to be published") and did not publish a value. Keeping the rows blank keeps the gap visible, and is consistent with how 2020Q2 and 2020Q3 are treated. Estimating them would mean creating numbers Statistics Canada judged unreliable. Neither is a Prairie province, so the Alberta, Saskatchewan, Manitoba and Prairies series are unaffected.
  - The validation check now allows missing vacancies only where the flag is F, and never in a Prairie province (and expects exactly 2).
  - In `02_merge_and_ratio.py`, a group total will be calculated only when every province in that group has data. Rest of Canada and Canada will therefore be missing in 2015Q1 rather than understated. The 2015 to 2019 comparison for those two groups uses 19 quarters instead of 20.
- **Save cleaned files only after every validation check passes.** The first version saved the files before running the checks, so the failed run still left unchecked files in `data/processed/`. Saving is now the last step of the script, so a failed check stops the script before anything is written. `02_merge_and_ratio.py` follows the same rule.

**Merging and ratio (`02_merge_and_ratio.py`)**
- Left join on province and quarter, keeping every LFS row, so 2020Q2 and 2020Q3 stay in the data as rows with blank vacancies rather than disappearing. `validate="one_to_one"` stops the script if any province-quarter appears twice in either file.
- `ratio = vacancies / unemployed`. A blank vacancy value gives a blank ratio, never zero.
- `region` = "Prairies" for Alberta, Saskatchewan and Manitoba, "Rest of Canada" for the other seven provinces.

**Comparison groups (`02_merge_and_ratio.py`)**
- Six groups: Alberta, Saskatchewan, Manitoba, Prairies, Rest of Canada, Canada (all ten provinces).
- Group ratio = total vacancies / total unemployed, NOT the average of provincial ratios. Averaging ratios would give PEI the same weight as Ontario; adding up first gives the ratio for the group as a whole.
- A group total is calculated only when every province in the group has data (pandas `sum` with `min_count` = number of provinces in the group). Otherwise it is blank. By default pandas treats blanks as zero, which would understate the total. Result: all groups are blank in 2020Q2 and 2020Q3; Rest of Canada and Canada are blank in 2015Q1.

**Analysis periods (for the later analysis script)**
- *(Period dates superseded by the revised period decision below; the 2020 exclusion still applies.)* **Exclude 2020 from all period comparisons.** Comparison periods: 2015 to 2019 (pre-pandemic), 2021 to 2022 (post-pandemic peak), 2023 to 2025 (cooling). Reason: 2020 has only two quarters of vacancy data (Q1 and Q4) and falls between the periods. It appears only as a gap in quarterly charts. Period averages are not calculated yet; they will be done in a separate analysis script.
- *(Superseded by the revised period decision below.)* **The pre-pandemic period is 2015Q2 to 2019Q4 (19 quarters) for all six groups**, using only quarters where every group has data. Reasons: (1) Rest of Canada and Canada are missing 2015Q1; (2) the data is not seasonally adjusted, so dropping a Q1 (typically a low-ratio winter quarter) for some groups but not others would bias the comparison; (3) the three Prairie 2015Q1 values have low quality grades (Alberta E, Manitoba E, Saskatchewan D). A version that includes 2015Q1 for the Prairie groups will be run as a sensitivity check in the analysis script.

**Interpretation notes**
- The 2015 annual averages printed by `02_merge_and_ratio.py` are not comparable across groups (Rest of Canada and Canada use 3 quarters, the Prairie groups use 4, and the data is unadjusted). They must not be reported as a finding.
- The Prairies aggregate is dominated by Alberta because of its size: Alberta accounts for 66% to 74% of Prairie unemployment and 61% to 73% of Prairie vacancies across the quarters. The Prairies figure may therefore hide differences between the three provinces, so the provinces should also be shown separately.

### Validation results

**`01_clean.py`: all checks passed**
- Filtered LFS: 1,320 monthly rows, 132 for each of the 10 provinces. Every quarterly average uses exactly 3 months.
- Cleaned LFS: 440 rows (10 provinces x 44 quarters), no duplicates, no missing values.
- Cleaned JVWS: 420 rows (10 provinces x 42 quarters), no rows for 2020Q2 or 2020Q3, no duplicates. Dates are only quarter-start months.
- Exactly 2 missing vacancy values (NL and PEI, 2015Q1), both flagged F, none in a Prairie province.
- Province names match exactly in both files.
- Prairie quality flags: Alberta 41 A, 1 E; Manitoba 40 A, 1 B, 1 E; Saskatchewan 36 A, 5 B, 1 D. Rows graded C or lower: 3, all 2015Q1 (Alberta E, Manitoba E, Saskatchewan D).
- Hand check, Alberta 2019Q1: raw months 171.6, 186.3, 173.6 thousand; average 177.1667 thousand = 177,166.67 persons, matching the cleaned file. Vacancies 49,840 (grade A).

**`02_merge_and_ratio.py`: all checks passed**
- Merge: 420 rows matched, 20 LFS-only (all 2020Q2 or 2020Q3).
- Merged file: 440 rows; 22 missing vacancies (20 in 2020Q2 and 2020Q3, plus NL and PEI in 2015Q1); ratio missing in the same 22 rows.
- No ratio is zero or negative (provinces or groups). Provincial ratios range from 0.067 to 1.34.
- Group file: 264 rows (6 groups x 44 quarters). Canada unemployed = Prairies + Rest of Canada in every quarter.
- Vacancies and ratio are missing (not zero) for every group in 2020Q2 and 2020Q3, and for Rest of Canada and Canada in 2015Q1. Alberta, Saskatchewan, Manitoba and Prairies all have 2015Q1 values. No other missing values (14 in total).
- Our Canada unemployed vs published LFS Canada: largest difference 200 persons (0.016%), due to Statistics Canada rounding each published figure to the nearest 100 persons.
- Our Canada vacancies vs published JVWS Canada: ours is smaller in all 41 comparable quarters, by 1,220 to 3,970. The gap matches the three territories' total within about 10 vacancies (e.g. 2019Q1: gap 1,950, territories 1,955; 2022Q2: gap and territories both 3,710), confirming the difference is the territories.
- Hand check, Alberta 2019Q1: 49,840 / 177,166.67 = 0.2813, matching my expected value of about 0.281.

### Problems encountered
- First run of `01_clean.py` failed the "no missing vacancies" check (NL and PEI, 2015Q1, graded F). Resolved by keeping the rows as missing and changing the check and group method (see decisions above).
- The first version of `01_clean.py` saved files before the checks ran. Fixed by moving saving to the end.
- Because the data is unadjusted, the missing 2015Q1 for Rest of Canada and Canada would bias the 2015 to 2019 comparison. Resolved by the 2015Q2 to 2019Q4 period decision above (later superseded by the revised period decision below).

### AI-generated code I reviewed and how I checked it
- `scripts/01_clean.py` and `scripts/02_merge_and_ratio.py` were written by Claude Code. Both include built-in validation checks that stop the script if a result is unexpected, and both save files only after every check passes.
- Both scripts were run with the raw file fingerprints (hashes) recorded before and after: unchanged.
- I checked the Alberta 2019Q1 quarterly average and ratio against my own calculation (see validation results).
- [Add my own review notes here as I complete the checks below.]

### Checks I should do myself on the code
1. Open `data/raw/CA_Labour_Force_Monthly.csv` in Excel, filter to Alberta, Unemployment, 15 years and over, Unadjusted, January to March 2019, and confirm the three values and their average.
2. Repeat the full calculation by hand for a different province and quarter (e.g. Saskatchewan 2022Q3): unemployment from the raw LFS months, vacancies from the raw JVWS row, then the ratio. Compare with `merged_province_quarter.csv`.
3. Recalculate one Prairies row by hand: add the three provinces' vacancies and unemployed for one quarter, divide, and compare with `group_quarter.csv`. Also calculate the simple average of the three provincial ratios to see how it differs.
4. Check that the filter text in `01_clean.py` ("Unemployment", "15 years and over", "Unadjusted", "Job vacancies", "Total, all industries") exactly matches the category names printed by `00_inspect_data.py`.
5. Check the `make_quarter` rule at the edges: months 03 -> Q1, 04 -> Q2, 06 -> Q2, 09 -> Q3, 10 -> Q4, 12 -> Q4.
6. Check the `PRAIRIES` and `REST_OF_CANADA` lists in `02_merge_and_ratio.py`: 3 + 7 provinces, each listed once.
7. Open `group_quarter.csv` and confirm that 2020Q2, 2020Q3, and Rest of Canada and Canada in 2015Q1 are blank, not 0.
8. Test that a check really stops the script: temporarily change an expected number (e.g. 440 to 441), run the script, confirm it stops with "CHECK FAILED" and saves nothing new, then undo the change (do not commit it).
9. Test the `min_count` rule: temporarily remove `min_count=len(provinces)`, run the script and see the checks fail because 2015Q1 Rest of Canada now gets an understated total. Then undo the change.
10. Read every comment in both scripts and make sure I can explain each step in my own words.

## 2026-10-27 (Revised period decision)

### What I did
- Revised the comparison periods so that each period contains complete calendar years. Updated the "Key data decisions" table in README.md. No scripts or data files were changed (period averages have not been calculated yet).

### Decisions and reasons
- **This decision replaces the earlier decision to start the pre-pandemic period at 2015Q2 (2015Q2 to 2019Q4, 19 quarters).**
- **New comparison periods, the same for all six groups:**
  - 2016 to 2019, pre-pandemic (16 quarters)
  - 2021 to 2022, post-pandemic peak (8 quarters)
  - 2023 to 2025, cooling (12 quarters)
- **Reason: each period contains complete calendar years.** The data is not seasonally adjusted, so the ratio has a seasonal pattern within each year. With complete years, Q1, Q2, Q3 and Q4 are equally represented in every period, so differences between periods are not caused by a different mix of seasons. The previous 2015Q2 to 2019Q4 period had five each of Q2, Q3 and Q4 but only four Q1s, so it under-weighted the winter quarter.
- **2015 is excluded from period averages** but stays in the data files and appears on quarterly charts as context. Excluding the whole year also means the 2015Q1 problems fall outside every period: Rest of Canada and Canada are missing 2015Q1, and the three Prairie 2015Q1 values have low quality grades (Alberta E, Manitoba E, Saskatchewan D). Every group has complete data in every quarter of all three periods.
- **2020Q2 and 2020Q3 remain missing and will not be imputed.** Quarterly charts will show a break in the line with a note at that point. 2020 remains excluded from period comparisons.
- **Sensitivity check (replaces the earlier one):** compare the 2016 to 2019 averages with averages that also include 2015Q2 to 2015Q4.
- The 2015 annual averages printed by `02_merge_and_ratio.py` are still not comparable across groups and must not be reported as a finding (see interpretation notes above).

### Problems encountered
- None.

### AI-generated code I reviewed and how I checked it
- None. This change is documentation only; no code was written or changed.

## 2026-10-27 (Correction: JVWS source table)

### What I did
- Corrected the source table for the Job Vacancy and Wage Survey file from Table 14-10-0326-01 to Table 14-10-0442-01 in README.md and `docs/data_dictionary.md`, using the official title from the metadata file.
- Removed the "[from Table 14-10-0442-01 metadata; to be checked against 14-10-0326-01]" and "[title to be checked...]" markers from the data dictionary, and the label saying the 14-10-0442-01 metadata was downloaded in error.
- Added a note on the table change to the data sources sections of both files.

### Decisions and reasons
- **The JVWS source is Table 14-10-0442-01 (sector-level rows), not 14-10-0326-01.** The PPOL 652 dataset list cites 14-10-0326-01, but that table was archived (Statistics Canada stopped updating it around the end of 2023) and replaced by 14-10-0442-01, which includes the same sector-level estimates. My vacancy file runs to 2025Q4, after the archived table stopped being updated, so it must come from 14-10-0442-01.
- The metadata file already saved in `docs/source_metadata/Job vacancies_MetaData.csv` is therefore the correct one, and the JVWS note numbers in the data dictionary (notes 1, 2, 3, 7 and 12) refer to the correct table.
- No scripts or data files changed. The analysis uses only "Total, all industries", so the table change does not affect any result.

### Problems encountered
- The data dictionary and README previously cited 14-10-0326-01 and treated the 14-10-0442-01 metadata as downloaded in error. Two later downloads meant to be the 14-10-0326-01 metadata turned out to be the 14-10-0442-01 file again (`1410044201_MetaData.csv`) and the Labour Force Survey metadata (`1410028701_MetaData.csv`); both were identical to files already saved and were not added to the project.

### AI-generated code I reviewed and how I checked it
- Claude Code ran a one-off check (not saved in the project) comparing the raw vacancy file with the dimension members listed in the 14-10-0442-01 metadata. Result: all 21 industry names in the raw file ("Total, all industries" and the 20 sectors, with codes in brackets) match the 21 sector-level members exactly, with none missing on either side. The 14 geography names and the 4 "Statistics" names also match exactly.
- [Add my own check: e.g. compare a few industry names in the raw file with the member list in the metadata file by eye.]
