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
- *(Superseded: 2015 is no longer in the analysis, so these two rows are no longer in the processed data; see the 2016Q1 to 2025Q4 decision below.)* **Keep the two blank vacancy rows (Newfoundland and Labrador 2015Q1, Prince Edward Island 2015Q1) as missing, not zero, not dropped, not estimated.** Statistics Canada graded both F ("too unreliable to be published") and did not publish a value. Keeping the rows blank keeps the gap visible, and is consistent with how 2020Q2 and 2020Q3 are treated. Estimating them would mean creating numbers Statistics Canada judged unreliable. Neither is a Prairie province, so the Alberta, Saskatchewan, Manitoba and Prairies series are unaffected.
  - The validation check now allows missing vacancies only where the flag is F, and never in a Prairie province (and expects exactly 2).
  - *(Superseded: 2015 is no longer in the analysis and the periods were revised, so 2015Q1 and the 19-quarter comparison no longer apply; the rule that a group total needs every province still applies, for 2020Q2 and 2020Q3.)* In `02_merge_and_ratio.py`, a group total will be calculated only when every province in that group has data. Rest of Canada and Canada will therefore be missing in 2015Q1 rather than understated. The 2015 to 2019 comparison for those two groups uses 19 quarters instead of 20.
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

Review Notes for Day 2: **What I checked and the results**

I checked the cleaning and merging scripts against the raw Statistics Canada files, using Excel rather than the processed files, so that the scripts were not being checked against their own output.

- Check 1: I filtered the raw LFS file to Alberta, unemployment, 15 years and over, unadjusted, January to March 2019. The three values (171.6, 186.3 and 173.6 thousand) average to 177.17 thousand, which matches the cleaned file.
- Check 2: I recalculated Saskatchewan 2022Q3 by hand. Unemployment averaged 26.87 thousand (26,866.67 persons), vacancies were 25,465, and the ratio was 0.948. All three numbers match merged_province_quarter.csv.
- Check 3: I recalculated the Prairies 2022Q3 row by hand in Excel, using the raw files for all three provinces. I added the three provinces' vacancies (103,495 + 25,465 + 32,305 = 161,265) and unemployment (138,000 + 26,866.67 + 36,766.67 = 201,633.33) and divided, giving 0.7998. group_quarter.csv shows 0.7998. The simple average of the three provincial ratios (0.750, 0.948 and 0.879) was 0.859, which is higher, because Saskatchewan and Manitoba had higher ratios that quarter and the simple average gives them the same weight as Alberta, even though Alberta has more unemployed people than the other two combined.
- Check 7: I opened group_quarter.csv and confirmed that 2020Q2 and 2020Q3 are blank for all groups, and that Rest of Canada and Canada are blank in 2015Q1, rather than zero.
- Check 9: At my request, Claude Code removed min_count from 02_merge_and_ratio.py and reran the script while I reviewed the output. The script stopped at the "no group ratio is exactly zero" check because, without min_count, the blank 2020Q2 and 2020Q3 vacancies were added up as 0, giving all 12 group rows in those two quarters (6 groups x 2 quarters) a ratio of exactly 0 instead of a blank. No processed data files were changed. Claude Code then restored the file with git restore, and the script passed every check again.
- I have finished check 10: I read both scripts and can explain each step in my own words.

I did not repeat checks 4, 5, 6 and 8 separately, because the automated checks already cover them.

**Problems or surprises**

My first attempt at check 2 did not match. I had not filtered the industry column, so I summed every industry plus the "Total, all industries" row and got about double the correct figure. After fixing the filter, the numbers matched. I also noticed that the individual industries add up to 85 fewer vacancies than the published total. One industry, Management of companies and enterprises [55], has no published value because Statistics Canada graded it F (too unreliable to publish), and that missing industry could account for the whole gap. This is why the project uses the published total rather than adding up industries.

**Decisions I made**

I chose to keep Newfoundland and Labrador and PEI 2015Q1 as missing rather than filling them in, to start the comparison periods in 2016 so each period contains complete calendar years of unadjusted data, and not to impute 2020Q2 and 2020Q3. After checking the Statistics Canada metadata, I also corrected the vacancy table citation from 14-10-0326-01, which is archived, to 14-10-0442-01, which my data must have come from.

**What I'm still unsure about**

After completing check 10, I can explain what each step of both scripts does and why the project needs it. I am less confident about the Python syntax itself, such as exactly how the pandas functions are written, so I would need to look things up or ask for help to modify the code. The validation checks and my hand calculations are how I confirmed the code does what the comments say.

These notes were drafted with AI assistance from my account of the checks, and I confirmed that they accurately describe what I did.

### Checks I should do myself on the code
1. **Done by me by hand.** Open `data/raw/CA_Labour_Force_Monthly.csv` in Excel, filter to Alberta, Unemployment, 15 years and over, Unadjusted, January to March 2019, and confirm the three values and their average.
2. **Done by me by hand.** Repeat the full calculation by hand for a different province and quarter (e.g. Saskatchewan 2022Q3): unemployment from the raw LFS months, vacancies from the raw JVWS row, then the ratio. Compare with `merged_province_quarter.csv`.
3. **Done by me by hand.** Recalculate one Prairies row by hand: add the three provinces' vacancies and unemployed for one quarter, divide, and compare with `group_quarter.csv`. Also calculate the simple average of the three provincial ratios to see how it differs.
4. **Not repeated separately (see note below).** Check that the filter text in `01_clean.py` ("Unemployment", "15 years and over", "Unadjusted", "Job vacancies", "Total, all industries") exactly matches the category names printed by `00_inspect_data.py`.
5. **Not repeated separately (see note below).** Check the `make_quarter` rule at the edges: months 03 -> Q1, 04 -> Q2, 06 -> Q2, 09 -> Q3, 10 -> Q4, 12 -> Q4.
6. **Not repeated separately (see note below).** Check the `PRAIRIES` and `REST_OF_CANADA` lists in `02_merge_and_ratio.py`: 3 + 7 provinces, each listed once.
7. **Done by me by hand.** Open `group_quarter.csv` and confirm that 2020Q2, 2020Q3, and Rest of Canada and Canada in 2015Q1 are blank, not 0.
8. **Not repeated separately (see note below).** Test that a check really stops the script: temporarily change an expected number (e.g. 440 to 441), run the script, confirm it stops with "CHECK FAILED" and saves nothing new, then undo the change (do not commit it).
9. **Done by me by hand.** Test the `min_count` rule: temporarily remove `min_count=len(provinces)`, run the script and confirm it stops at the "no group ratio is exactly zero" check, because without `min_count` the blank 2020Q2 and 2020Q3 vacancies add up to 0 (giving ratios of 0) instead of staying blank. Then undo the change.
10. **Done by me.** Read every comment in both scripts and make sure I can explain each step in my own words.

*Note on checks 4, 5, 6 and 8 (not repeated separately):* Covered by the automated checks. A misspelled filter would have matched zero rows and failed the 132-month check (check 4); a wrong quarter rule would have failed the exactly-3-months check, and my hand checks 1 and 2 confirmed that the quarter labels are correct (January to March 2019 is 2019Q1, July to September 2022 is 2022Q3) (check 5); a missing, duplicated or misspelled province would have failed the check that the 3 Prairie and 7 Rest of Canada names match the 10 provinces in the data (check 6); check 9 already confirmed that a failed check stops the script (check 8).

### Hand calculation record

Check 1, Alberta 2019Q1 (raw LFS, unemployment, 15+, unadjusted): 171.6, 186.3 and 173.6 thousand. Average 177.17 thousand = 177,166.67 persons. Matches lfs_unemployment_quarterly.csv.

Check 2, Saskatchewan 2022Q3: unemployment 26.4, 32.7 and 21.5 thousand, average 26.87 thousand = 26,866.67 persons. Vacancies (Total, all industries, July 2022) 25,465, grade A. Ratio 25,465 / 26,866.67 = 0.9478. Matches merged_province_quarter.csv.

Check 3, Alberta 2022Q3: unemployment 131.4, 154.5 and 128.1 thousand, average 138.0 thousand = 138,000 persons. Vacancies 103,495, grade A. Ratio 103,495 / 138,000 = 0.7500. Matches merged_province_quarter.csv.

Check 3, Manitoba 2022Q3: unemployment 32.8, 48.8 and 28.7 thousand, average 36.77 thousand = 36,766.67 persons. Vacancies 32,305, grade A. Ratio 32,305 / 36,766.67 = 0.8786. Matches merged_province_quarter.csv.

Check 3, Prairies 2022Q3: total vacancies 161,265 / total unemployed 201,633.33 = 0.7998. Matches group_quarter.csv. Simple average of the three provincial ratios = 0.859.

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
- *(Superseded: 2015 no longer appears on charts as context; see the research question scope decision below.)* **2015 is excluded from period averages** but stays in the data files and appears on quarterly charts as context. Excluding the whole year also means the 2015Q1 problems fall outside every period: Rest of Canada and Canada are missing 2015Q1, and the three Prairie 2015Q1 values have low quality grades (Alberta E, Manitoba E, Saskatchewan D). Every group has complete data in every quarter of all three periods.
- **2020Q2 and 2020Q3 remain missing and will not be imputed.** Quarterly charts will show a break in the line with a note at that point. 2020 remains excluded from period comparisons.
- *(Superseded: 2015 is no longer in the analysis, so this sensitivity check has been dropped; see the 2016Q1 to 2025Q4 decision below.)* **Sensitivity check (replaces the earlier one):** compare the 2016 to 2019 averages with averages that also include 2015Q2 to 2015Q4.
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
- My own check: I compared Construction, Retail trade, and Mining, quarrying, and oil and gas extraction in the raw vacancy file with the 14-10-0442-01 metadata member list, and the names match.

## 2026-10-27 (Research question scope changed to 2016 to 2025)

### What I did
- Changed the scope of the research question and the README title from 2015 to 2025 to 2016 to 2025. Updated the README "Key data decisions" row about 2015. No scripts or data files were changed; the 2015 rows stay in the data.

### Decisions and reasons
- **The research question now covers 2016 to 2025.** Reason: the comparison periods already start in 2016 (2016 to 2019, 2021 to 2022, 2023 to 2025), so starting the question in 2016 keeps the question, the comparisons and the charts consistent.
- *(Superseded: 2015 is now removed from the processed data and the sensitivity check has been dropped; see the 2016Q1 to 2025Q4 decision below.)* **2015 is outside the research question's scope.** It remains in the data files because the source data starts in 2015, and it is used only in the sensitivity check, which tests whether adding 2015Q2 to 2015Q4 changes the 2016 to 2019 comparison.
- **Charts will start in 2016Q1.** This supersedes the earlier statement (revised period decision above) that 2015 would appear on quarterly charts as context.

### Problems encountered
- None.

### AI-generated code I reviewed and how I checked it
- None. This change is documentation only; no code was written or changed.

## 2026-10-27 (Analysis restricted to 2016Q1 to 2025Q4)

### What I did
- Removed 2015 from the analysis entirely. `scripts/01_clean.py` now keeps Labour Force Survey months from 2016-01 to 2025-12 (before averaging to quarters) and Job Vacancy and Wage Survey quarters from 2016Q1 to 2025Q4. The raw files are unchanged; the filtering happens in the script.
- Updated the validation checks in both scripts, reran both scripts, and regenerated the four processed files (commit "Restrict analysis to 2016Q1 to 2025Q4").
- Updated README.md and `docs/data_dictionary.md` for the 2016 to 2025 scope.

### Decisions and reasons
- **The analysis covers 2016Q1 to 2025Q4.** Reasons: the vacancy survey began in 2015, but its first quarter had unpublished estimates for two provinces (Newfoundland and Labrador and Prince Edward Island, graded F) and low-quality estimates for all three Prairie provinces (Alberta E, Manitoba E, Saskatchewan D). Starting in 2016 also gives every comparison period complete calendar years, which matters because the data is not seasonally adjusted.
- This supersedes the earlier decisions that referred to 2015: keeping NL and PEI 2015Q1 as missing, the 2015Q2 start, the sensitivity check adding 2015Q2 to 2015Q4, and 2015 appearing on charts as context. The sensitivity check is dropped.
- The missing-vacancies check is back to "no missing vacancies at all", since the NL and PEI 2015Q1 exception no longer applies.
- `min_count=len(provinces)` is kept in `02_merge_and_ratio.py`, because it is still needed so that 2020Q2 and 2020Q3 group totals are blank rather than zero.

### New row counts
- Filtered LFS before averaging: 1,200 monthly rows (120 per province).
- `lfs_unemployment_quarterly.csv`: 400 rows (10 provinces x 40 quarters).
- `jvws_vacancies_quarterly.csv`: 380 rows (10 provinces x 38 quarters; 2020Q2 and 2020Q3 absent).
- `merged_province_quarter.csv`: 400 rows; 380 matched, 20 LFS-only; exactly 20 missing vacancies, all in 2020Q2 or 2020Q3.
- `group_quarter.csv`: 240 rows (6 groups x 40 quarters); 12 missing vacancies, all in 2020Q2 and 2020Q3.

### Validation results
- Both scripts passed every check. No quarter earlier than 2016Q1 in either cleaned file; no missing vacancies in the cleaned vacancy file.
- Prairie quality flags, 2016Q1 to 2025Q4: Alberta 38 A; Manitoba 38 A; Saskatchewan 34 A, 4 B. No Prairie rows graded C or lower.
- Our Canada unemployed vs published LFS Canada: largest difference 200 persons (0.016%), over 40 quarters. Our Canada vacancies smaller than the published total in all 38 comparable quarters, by 1,220 to 3,970.
- Raw file fingerprints (hashes) were unchanged before and after running both scripts.

### Hand-check values unchanged
- Alberta 2019Q1 ratio 0.2813, Saskatchewan 2022Q3 ratio 0.9478 and Prairies 2022Q3 ratio 0.7998: all unchanged from before.
- Every 2016 to 2025 row in `merged_province_quarter.csv` (400 rows) and `group_quarter.csv` (240 rows) is identical to the previous version of each file, so removing 2015 deleted rows without changing any value.

### Problems encountered
- None.

### AI-generated code I reviewed and how I checked it
- Claude Code changed `scripts/01_clean.py` and `scripts/02_merge_and_ratio.py`. Checks: all built-in validation checks passed; raw file hashes unchanged; the three hand-check values above are unchanged; and a comparison with the previously committed processed files showed that the only difference is the removed 2015 rows.

## 2026-10-27 (Year and quarter_number columns)

### What I did
- Added `year` and `quarter_number` columns to `merged_province_quarter.csv` and `group_quarter.csv` in `scripts/02_merge_and_ratio.py`, split from the `quarter` label (e.g. `2019Q1` becomes 2019 and 1). Updated `docs/data_dictionary.md`.

### Decisions and reasons
- The `quarter` column is kept, because it is the key used to join the two datasets and the clearest label for charts. The new columns make it easy to filter or group by year (for example, the comparison periods) or by quarter of the year.
- The annual-averages section now uses the new `year` column. It previously created and then deleted a temporary text `year` column, which would have removed the new column before saving.

### Problems encountered
- None.

### AI-generated code I reviewed and how I checked it
- Claude Code wrote the change. New checks in the script: rebuilding `year` + "Q" + `quarter_number` gives the original `quarter` label in every row; every year is 2016 to 2025; every quarter number is 1 to 4. All 29 checks passed, the annual averages are unchanged, and apart from the two new columns both files are identical to the previous versions.

## 2026-10-27 (Quarter rule validated against course concordance table)

### What I did
- Added `data/raw/concord.csv`, a month-to-quarter concordance table for PPOL 652, and used it as a validation check in `scripts/01_clean.py`. Documented it in `docs/data_dictionary.md` (section 1.7) and the README data sources section.

### Decisions and reasons
- **Use the course concordance table to validate the quarter rule, not to replace it.** The scripts keep using `make_quarter`; the new check confirms that the rule gives the same quarter as the course table for all 12 months, and stops the script if any month disagrees.
- **Source of the file:** the PPOL 652 instructor created it during class on my computer, typing the header and the January row; Claude Code completed the remaining 11 months at the instructor's request. It is stored in `data/raw/` and has not been changed since. The script reads it with `skipinitialspace=True` because of the space after each comma, rather than editing the file.

### Validation results
- The table has 12 rows, each month exactly once, and each quarter 1 to 4 exactly 3 times.
- `make_quarter` gives the same quarter as the table for all 12 months.
- `01_clean.py` passed all 23 checks (4 new) and `02_merge_and_ratio.py` passed all 29. All processed and raw files were identical before and after the run.

### Problems encountered
- Limitation: because Claude Code completed 11 of the 12 rows using the standard calendar quarters, the check confirms that the scripts agree with the course table as completed in class, rather than with a fully independent source.

### AI-generated code I reviewed and how I checked it
- Claude Code wrote the check. It passes month dates through the actual `make_quarter` function (not a copy of the rule) and compares the result with the `q` column, printing all 12 months side by side.

## 2026-10-27 (Distributions and outlier check)

### What I did
- Wrote and ran `scripts/00b_explore_distributions.py`, which reads only `data/processed/merged_province_quarter.csv` and `group_quarter.csv`. It prints summary statistics by province, flags quarters whose ratio changed by more than 50% from the previous available quarter, and lists each province's highest and lowest ratio. It saves two exploratory charts to `outputs/figures/exploratory/`: the quarterly ratio for the six groups (with a break at 2020Q2 and 2020Q3) and a histogram of the quarterly ratio across all provinces.
- No observations were removed or changed, and no file in `data/` changed (all 7 data file fingerprints identical before and after).

### Main findings (from the data)
- Most province-quarters have a ratio between 0.2 and 0.5, with a long right tail up to 1.34. The mean ratio is above the median in all 10 provinces.
- 10 province-quarters have a ratio of 1 or more, all in British Columbia (5) and Quebec (5), between 2021Q4 and 2023Q2. No Prairie province reaches 1: the highest are Saskatchewan 0.978 (2022Q4), Manitoba 0.957 (2022Q2) and Alberta 0.758 (2022Q2).
- 8 of 10 provinces have their highest ratio in 2022Q2 (Prince Edward Island 2022Q3, Saskatchewan 2022Q4, Newfoundland and Labrador 2023Q3).
- Most provinces have their lowest ratio in 2016 or 2017. Exceptions: Alberta 2020Q4 (0.179) and Ontario 2025Q3 (0.245).
- Unemployment was highest in 2020Q2 in 9 of 10 provinces (Newfoundland and Labrador: 2017Q1), but the ratio is not available for that quarter.
- 28 quarters were flagged for a change of more than 50% from the previous available quarter. All 28 are increases; 27 are Q1 to Q2; 24 are in the four Atlantic provinces; 1 compares across the 2020 gap (Nova Scotia 2020Q1 to 2020Q4). The only Prairie flags are Alberta 2021Q2, Manitoba 2017Q2 and Saskatchewan 2021Q2.
- The mean ratio across all provinces is 0.355 in Q1 quarters and 0.450 in Q2 to Q4 quarters.

### Interpretation (my reading, not shown directly by the data)
- The Q1 to Q2 flags look like genuine seasonal variation, not data problems: the data is not seasonally adjusted (LFS note 1), the jump recurs in the same quarter every year, and every flagged quarter has a published quality grade of A, B or C. The pattern is strongest in the Atlantic provinces, which is consistent with more seasonal industries there, but the data does not show the cause.
- The 2021Q1 to 2021Q2 flags (Alberta, New Brunswick, Newfoundland and Labrador, Prince Edward Island, Quebec, Saskatchewan) combine the usual seasonal jump with the start of the 2021 to 2022 post-pandemic rise in vacancies.
- None of the flagged quarters looks like a data problem.
- The 50% threshold is asymmetric: a halving is -50% but a doubling is +100%. No quarter fell by more than 50%; the largest fall was -43.3% (Prince Edward Island, 2017Q3 to 2017Q4).

### Quarters to keep an eye on
- Prince Edward Island 2016Q2, 2017Q2, 2018Q2 and 2019Q2: the largest jumps (up to +204% in 2018Q2), graded C ("good"); PEI has the smallest numbers (as few as 770 vacancies in a quarter), so small changes give large percentages. PEI 2019Q4 is graded D ("acceptable"). See JVWS note 1 on how grades are assigned.
- Nova Scotia 2020Q4: compared with 2020Q1 across the gap (JVWS note 12), so the change spans three quarters, not one.
- Alberta 2020Q4: Alberta's lowest ratio, in the first quarter after the gap.
- Ontario 2025Q3: Ontario's lowest ratio, at the end of the series.
- In general, Q1 values are lower because of the seasonal pattern, so single quarters should be compared with the same quarter in other years, or whole years should be compared (as the comparison periods do).

### Problems encountered
- None.

### AI-generated code I reviewed and how I checked it
- Claude Code wrote `scripts/00b_explore_distributions.py`. Checks: the fingerprints of all 7 files in `data/` were identical before and after the run; both charts were opened and inspected; the counts quoted above (flags by type, ratios of 1 or more, peaks, Q1 averages) were calculated from the processed files rather than read off the charts.

## 2026-10-27 (Triage follow-up: subtotals, metadata checks and exclusions)

### What I did
- Documented how subtotal rows were handled, checked both metadata files in `docs/source_metadata/` for corrections and method changes within 2016 to 2025, and recorded my assessment of the exclusions. No data or scripts were changed.

### Subtotal rows
- **Canada rows:** dropped from both files and rebuilt from the ten provinces, so the national total is defined the same way in both surveys (the published JVWS Canada total includes the territories; the LFS total does not).
- **"Total, all industries" (JVWS):** used directly instead of adding up the industries. In my check (Saskatchewan 2022Q3), the industries add up to 85 fewer vacancies than the published total, because one industry, Management of companies and enterprises [55], was graded F and has no published value.
- **LFS subtotal and component rows:** "Labour force" (employment plus unemployment), "Employment" with its "Full-time employment" and "Part-time employment" components, and the age groups that make up "15 years and over" (15 to 24, 25 to 54, 55 and over) are all avoided by filtering to "Unemployment" and "15 years and over" only, so no person is counted twice.

### Metadata check: corrections and method changes, 2016 to 2025
Source: only the two metadata files in `docs/source_metadata/`.
- **Correction notes.** LFS (Table 14-10-0287-01): none. JVWS (Table 14-10-0442-01): one, Correction ID 3809, dated 2024-04-12: "average offered hourly wage estimates have been corrected for the Q4 2023 reference period." It is within 2016 to 2025 but affects only the hourly wage estimates, not job vacancies or unemployment.
- **Method or coverage changes within 2016 to 2025.**
  - LFS note 21: the LFS started collecting gender in 2022; before 2022 it collected sex. Statistics Canada states that the change "is not expected to have a significant impact on data analysis and historical comparability."
  - JVWS note 12: collection was suspended for 2020Q2 and 2020Q3 (a gap in the data, not a change of method).
  - No other note describes a change within the period. LFS note 14 (level shift around 2001) and note 20 (processing changes from 2006) are before the period; JVWS note 3 applies to 2015Q1 only; JVWS note 2 states that industries are based on NAICS 2022 but gives no date of adoption, and the project uses only the all-industry total; JVWS note 11 concerns the calibration of employment estimates, which are not used.
- **The 2021 to 2022 rise (my assessment):** I treat the rise in the ratio in 2021 and 2022 as genuine, because it appears in every province at the same time (8 of 10 provinces peak in 2022Q2), all 80 province-quarters in 2021Q1 to 2022Q4 are graded A (69) or B (11), every province's peak quarter is graded A or B, and no metadata note describes a change in method at that time.
- **The Q1 dips (cause is my assessment):** I treat the lower Q1 ratios as seasonal, because they recur every year and the data is not seasonally adjusted (LFS note 1). Q1 ratios average 0.355, against 0.450 in the other quarters (all provinces, 2016 to 2025).

### Exclusions: considered, not tested (directions are my assessment)
The exclusions below were considered but not tested or measured; there is no sensitivity analysis for them.
- **Employers excluded from the JVWS** (federal, provincial and territorial public administration, private households, religious organizations; JVWS note 2): vacancies are undercounted while unemployment covers everyone, so the ratio understates tightness everywhere, possibly slightly more for Rest of Canada, where federal public administration is concentrated (Ontario and Quebec).
- **Persons living on reserves excluded from the LFS:** this may lower measured unemployment in Saskatchewan and Manitoba, which have relatively large on-reserve populations, which would make their ratios look tighter than they are.
- **The 2020Q2 and 2020Q3 gap and the removal of 2015:** both fall outside the comparison periods (2016 to 2019, 2021 to 2022, 2023 to 2025), so they do not affect the period comparisons.

### Problems encountered
- None.

### AI-generated code I reviewed and how I checked it
- No project code was written or changed. Claude Code extracted the correction notes and dated notes from the two metadata files, and confirmed from `merged_province_quarter.csv` that all 2021Q1 to 2022Q4 quarters and every province's peak quarter are graded A or B.
