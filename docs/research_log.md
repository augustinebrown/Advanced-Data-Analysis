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
- First run stopped at the check "no missing values in vacancies": 2 of 420 rows were blank. Deleted the two files that run had saved, changed the script (see decisions below) and reran it.

### Decisions and reasons
- **Keep the two blank vacancy rows (Newfoundland and Labrador 2015Q1, Prince Edward Island 2015Q1) as missing, not zero, not dropped, not estimated.** Statistics Canada graded both F ("too unreliable to be published") and did not publish a value. Keeping the rows blank keeps the gap visible, and is consistent with how 2020Q2 and 2020Q3 are treated. Estimating them would mean creating numbers Statistics Canada judged unreliable. Neither is a Prairie province, so the Alberta, Saskatchewan, Manitoba and Prairies series are unaffected.
  - The validation check now allows missing vacancies only where the flag is F, and never in a Prairie province (and expects exactly 2).
  - In `02_merge_and_ratio.py`, a group total will be calculated only when every province in that group has data. Rest of Canada and Canada will therefore be missing in 2015Q1 rather than understated. The 2015 to 2019 comparison for those two groups uses 19 quarters instead of 20.
- **Save cleaned files only after every validation check passes.** The first version saved the files before running the checks, so the failed run still left unchecked files in `data/processed/`. Saving is now the last step of the script, so a failed check stops the script before anything is written.
