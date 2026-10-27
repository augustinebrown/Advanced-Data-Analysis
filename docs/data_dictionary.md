# Data Dictionary

Definitions of every variable in the final processed data files in `data/processed/`.

**Sources**
- **LFS:** Statistics Canada, Labour Force Survey, Table 14-10-0287-01 (`data/raw/CA_Labour_Force_Monthly.csv`)
- **JVWS:** Statistics Canada, Job Vacancy and Wage Survey, Table 14-10-0326-01 (`data/raw/CA_Job_Vacancies_Wages_Quarterly.csv`)

Intermediate files `lfs_unemployment_quarterly.csv` and `jvws_vacancies_quarterly.csv` (produced by `scripts/01_clean.py`) contain the same `province`, `quarter`, `unemployed`, `vacancies` and `vacancy_quality_flag` columns described below, before merging.

## merged_province_quarter.csv

One row per province and quarter: 10 provinces x 44 quarters (2015Q1 to 2025Q4) = 440 rows. Produced by `scripts/02_merge_and_ratio.py`.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `province` | Province name | LFS and JVWS (`GEO` column) | Text | The 10 provinces only. The published "Canada" rows are dropped from both files, and the three territories are dropped from JVWS (LFS does not cover them). Used with `quarter` to join the two files. |
| `region` | Comparison region the province belongs to | Created in `02_merge_and_ratio.py` | Text | "Prairies" for Alberta, Saskatchewan and Manitoba; "Rest of Canada" for the other seven provinces. |
| `quarter` | Calendar quarter | Created from `REF_DATE` in `01_clean.py` | Text, format `YYYYQn` (e.g. `2019Q1`) | LFS: months grouped as Jan to Mar = Q1, Apr to Jun = Q2, Jul to Sep = Q3, Oct to Dec = Q4. JVWS: `REF_DATE` is the first month of the quarter (`2015-04` = 2015Q2). |
| `unemployed` | Number of unemployed persons aged 15 and over, quarterly average | LFS: "Unemployment", "15 years and over", "Unadjusted" | Persons | Raw `VALUE` (thousands of persons) multiplied by 1,000, then averaged over the three months of each quarter (every quarter uses exactly 3 months). Not seasonally adjusted, to match JVWS. Not rounded after averaging, so values can have decimals. No missing values. |
| `vacancies` | Number of job vacancies, all industries | JVWS: "Job vacancies", "Total, all industries" | Vacancies (positions) | Raw `VALUE`, not rescaled. Not seasonally adjusted. Missing (blank, not zero) in 22 rows: all 10 provinces in 2020Q2 and 2020Q3 (not collected by Statistics Canada), and Newfoundland and Labrador and Prince Edward Island in 2015Q1 (graded F, not published). |
| `ratio` | Vacancy-to-unemployment ratio: job vacancies per unemployed person | Calculated in `02_merge_and_ratio.py` | Vacancies per unemployed person (no units) | `vacancies / unemployed`. Above 1 = more vacancies than unemployed people (tight); well below 1 = slack. Missing in the same 22 rows as `vacancies`. Range in this file: 0.067 to 1.34. |
| `vacancy_quality_flag` | Statistics Canada data quality grade for the vacancy estimate | JVWS (`STATUS` column) | Code | A = excellent, B = very good, C = good, D = acceptable, E = use with caution, F = too unreliable to be published (value left blank). Blank in the 20 rows for 2020Q2 and 2020Q3, which have no JVWS record. Prairie provinces are all A or B except 2015Q1: Alberta E, Manitoba E, Saskatchewan D. |

## group_quarter.csv

One row per comparison group and quarter: 6 groups x 44 quarters = 264 rows. Produced by `scripts/02_merge_and_ratio.py`.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group` | Comparison group | Created in `02_merge_and_ratio.py` | Text | Alberta, Saskatchewan, Manitoba (single provinces); Prairies (sum of the three Prairie provinces); Rest of Canada (sum of the other seven provinces); Canada (sum of all ten provinces, built from the provinces rather than the published Canada total). |
| `quarter` | Calendar quarter | As in `merged_province_quarter.csv` | Text, format `YYYYQn` | |
| `unemployed` | Total unemployed persons aged 15 and over in the group | Sum of `unemployed` from `merged_province_quarter.csv` | Persons | No missing values. Canada = Prairies + Rest of Canada in every quarter. Within 200 persons (0.016%) of the published LFS Canada total, a difference due to Statistics Canada rounding to the nearest 100 persons. |
| `vacancies` | Total job vacancies in the group | Sum of `vacancies` from `merged_province_quarter.csv` | Vacancies (positions) | Calculated only when every province in the group has a value (pandas `sum` with `min_count` = number of provinces in the group); otherwise blank, never zero or understated. Missing for all groups in 2020Q2 and 2020Q3, and for Rest of Canada and Canada in 2015Q1. The Canada total is 1,220 to 3,970 smaller than the published JVWS Canada total because it excludes the territories. |
| `ratio` | Group vacancy-to-unemployment ratio | Calculated in `02_merge_and_ratio.py` | Vacancies per unemployed person (no units) | Total `vacancies` divided by total `unemployed` for the group. Not an average of provincial ratios, so larger provinces carry more weight (the Prairies figure is dominated by Alberta). Missing wherever `vacancies` is missing. |
