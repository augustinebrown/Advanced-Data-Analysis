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
