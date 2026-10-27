# Data Dictionary

This file has two parts:

1. **Statistics Canada codebook** for the two raw source files: table information, official definitions, the meaning of each raw column and code, and the Statistics Canada notes that affect this project. Definitions are quoted from the metadata files that Statistics Canada publishes with each table, saved in `docs/source_metadata/` (`Labour force characteristics_MetaData.csv` and `Job vacancies_MetaData.csv`). Note numbers refer to the "Note ID" in those files: LFS notes are from Table 14-10-0287-01 and JVWS notes are from Table 14-10-0442-01.
2. **Processed files**: every column in the files produced by the scripts in `data/processed/`.

---

## Part 1: Statistics Canada codebook

### 1.1 Source tables

| | Labour Force Survey (LFS) | Job Vacancy and Wage Survey (JVWS) |
|---|---|---|
| Raw file | `data/raw/CA_Labour_Force_Monthly.csv` | `data/raw/CA_Job_Vacancies_Wages_Quarterly.csv` |
| Statistics Canada table title (from metadata) | Labour force characteristics, monthly, seasonally adjusted and trend-cycle | Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted for seasonality |
| Table number (from metadata) | 14-10-0287-01 (Product ID 14100287) | 14-10-0442-01 (Product ID 14100442); the raw file uses the table's sector-level rows |
| Table link | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028701 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410044201 |
| Survey | Labour Force Survey (survey code 3701) | Job Vacancy and Wage Survey (survey code 5217) |
| Frequency | Monthly | Quarterly |
| Period in the full table (from metadata) | January 1976 to September 2026 | Q1 2015 to Q2 2026 |
| Period in the raw file used here | January 2015 to December 2025 | Q1 2015 to Q4 2025 (Q2 and Q3 2020 not available) |
| Geography in the raw file | Canada and the 10 provinces. The table excludes the territories (note 19: "Excluding the territories.") | Canada, the 10 provinces and the 3 territories |

**JVWS source table.** The PPOL 652 dataset list cites Table 14-10-0326-01. That table was archived and replaced by Table 14-10-0442-01, which includes the same sector-level estimates. Because this file contains data to 2025Q4, after the archived table stopped being updated, it was taken from 14-10-0442-01. The raw file contains only the sector-level rows of that table: all 21 industry names ("Total, all industries" and the 20 two-digit sectors, with their codes) match the sector-level member names in the 14-10-0442-01 metadata exactly, as do the 14 geography names and the 4 statistics names.

**Curated extract.** Both raw files are the PPOL 652 curated extracts, which end at December 2025 (LFS) and 2025Q4 (JVWS). The Statistics Canada tables have since been updated with later periods, which are not used here.

### 1.2 Official definitions of the concepts used

| Concept | Statistics Canada definition | Source |
|---|---|---|
| Unemployment | "Number of persons who, during the reference week, were without work, had looked for work in the past four weeks, and were available for work. Those persons on layoff or who had a new job to start in four weeks or less are considered unemployed. Estimates in thousands, rounded to the nearest hundred." | LFS note 7 |
| Job vacancy | "A job is vacant if it meets the following conditions: it is vacant on the reference date (first day of the month) or will become vacant during the month; there are tasks to be carried out during the month for the job in question; and the employer is actively seeking a worker outside the organization to fill the job. The jobs could be full-time, part-time, permanent, temporary, casual, or seasonal. Jobs reserved for subcontractors, external consultants, or other workers who are not considered employees, are excluded." | JVWS note 7 |
| Total, all industries (JVWS) | All industries covered by the survey, based on NAICS 2022 Version 1.0. "The following categories are excluded from the survey: 'Religious organizations' (8131) ..., 'Private households' (814), 'Federal, government public administration' (911), 'Provincial and territorial public administration' (912) and 'International and other extra-territorial public administration' (919)." | JVWS note 2 |
| Seasonal adjustment | "A seasonally adjusted series is one from which seasonal movements have been eliminated. Seasonal movements are defined as those which are caused by regular annual events such as climate, holidays, vacation periods and cycles related to crops, production and retail sales..." This project uses the **Unadjusted** LFS series because the JVWS data is "unadjusted for seasonality" (table title). | LFS note 1; JVWS table title |
| Data quality indicators (JVWS) | "Data quality indicators are based on the coefficient of variation (CV), the non-response errors, the imputation errors, and subject matter expertise: A – Excellent; B - Very good; C - Good; D – Acceptable; E - Use with caution; F - Too unreliable to publish." The grades are not based on the CV alone. | JVWS note 1 |

### 1.3 Raw file columns: Labour Force Survey

| Column | Description | Values in the raw file | Used in this project |
|---|---|---|---|
| `REF_DATE` | Reference month | `YYYY-MM`, 2015-01 to 2025-12 (132 months) | 2016-01 to 2025-12 (120 months), grouped into quarters |
| `GEO` | Geography | Canada and the 10 provinces | The 10 provinces (Canada row dropped) |
| `Labour force characteristics` | Labour market measure | Population, Labour force, Employment, Full-time employment, Part-time employment, Unemployment | Unemployment |
| `Age group` | Age group | 15 years and over, 15 to 24 years, 25 to 54 years, 55 years and over | 15 years and over |
| `Data type` | Seasonal adjustment | Seasonally adjusted, Unadjusted | Unadjusted |
| `UOM` | Unit of measure | Persons in thousands | |
| `SCALAR_FACTOR` | Scale of `VALUE` | thousands | Used to convert to persons (x 1,000) |
| `VALUE` | The estimate | Number, one decimal place (e.g. 171.6 = 171,600 persons) | Becomes `unemployed` |

**Dimensions not in the raw file.** The full Statistics Canada table also has a **Gender** dimension (Total - Gender, Men+, Women+) and a **Statistics** dimension (Estimate, or one of three standard errors). The raw LFS file has no Gender or Statistics column. I assume it contains the Total - Gender estimates, because the course dataset list does not mention a gender breakdown, there is one row per geography, characteristic, age group, data type and month, and the values are internally consistent (labour force equals employment plus unemployment, apart from rounding (17,520.5 + 1,467.8 = 18,988.3, compared with 18,988.4), and the population figures are the size of the whole population aged 15 and over, not about half of it, as they would be if the file contained only one gender). The same reasoning applies to the Statistics dimension, which I assume is Estimate rather than a standard error. (January 2016, Canada, unadjusted, thousands: population aged 15 and over 29,218.7; labour force 18,988.4; employment 17,520.5; unemployment 1,467.8)

### 1.4 Raw file columns: Job Vacancy and Wage Survey

| Column | Description | Values in the raw file | Used in this project |
|---|---|---|---|
| `REF_DATE` | Reference quarter, dated by its first month | `2015-01` (Q1), `2015-04` (Q2), `2015-07` (Q3), `2015-10` (Q4); 42 quarters | 2016Q1 to 2025Q4 (38 quarters), converted to `YYYYQn` |
| `GEO` | Geography | Canada, 10 provinces, Yukon, Northwest Territories, Nunavut | The 10 provinces (Canada and territories dropped) |
| `North American Industry Classification System (NAICS)` | Industry (NAICS 2022 Version 1.0); code in square brackets | Total, all industries, plus 20 sectors (e.g. Construction [23], Manufacturing [31-33]) | Total, all industries |
| `Statistics` | Measure | Job vacancies, Payroll employees, Job vacancy rate, Average offered hourly wage | Job vacancies |
| `UOM` | Unit of measure | Number (vacancies, employees), Percent (vacancy rate), Dollars (hourly wage) | Number |
| `SCALAR_FACTOR` | Scale of `VALUE` | units | No rescaling needed |
| `VALUE` | The estimate | Number; blank when the estimate is not published (see `STATUS`) | Becomes `vacancies` |
| `STATUS` | Statistics Canada symbol for the value: data quality grade or reason for a blank | See section 1.5 | Becomes `vacancy_quality_flag` |

### 1.5 Symbol legend (`STATUS` column)

Symbols from the Statistics Canada "Symbol Legend" (identical in both metadata files). For what the quality grades A to F are based on, see "Data quality indicators" in section 1.2.

| Symbol | Meaning | In raw JVWS file | In the rows used (10 provinces, all industries, job vacancies, 2016Q1 to 2025Q4) |
|---|---|---|---|
| A | Data quality: excellent | yes | yes (305 rows) |
| B | Data quality: very good | yes | yes (61 rows) |
| C | Data quality: good | yes | yes (13 rows, all Prince Edward Island) |
| D | Data quality: acceptable | yes | yes (1 row: Prince Edward Island 2019Q4) |
| E | Use with caution | yes | no |
| F | Too unreliable to be published (value left blank) | yes | no |
| x | Suppressed to meet the confidentiality requirements of the Statistics Act (value left blank) | yes | no |
| .. | Not available for a specific reference period (value left blank) | yes | no |
| (blank) | No symbol | yes | no |
| ... | Not applicable | no | no |
| `<LOD` | Less than the limit of detection | no | no |
| 0s | Value rounded to zero | no | no |
| p | Preliminary | no | no |
| r | Revised | no | no |
| t | Terminated | no | no |

### 1.6 Statistics Canada notes that affect this project

| Note | What Statistics Canada says | Effect on this project |
|---|---|---|
| JVWS note 12 | "Data for the second and third quarters of 2020 are unavailable due to some Statistics Canada operations being temporarily suspended during the COVID-19 pandemic." | 2020Q2 and 2020Q3 are missing for every province and group; not imputed. Quarterly charts will show a break in the line with a note at 2020Q2 and 2020Q3. 2020 is excluded from period comparisons. |
| JVWS note 3 | "Due to the reduced sample size in the first quarter of 2015, the Finance and insurance (52) and Management of companies and enterprises (55) sectors were calibrated to a combined total from the Survey of Employment, Payrolls and Hours ... for the first quarter of 2015 only." | The note reports a reduced sample size in 2015Q1 and says that two sectors (52 and 55) were calibrated to the Survey of Employment, Payrolls and Hours for that quarter only. This is consistent with the low quality grades in 2015Q1 (Prairies D and E; NL and PEI F), but Statistics Canada does not give it as the reason for those grades. 2015 is excluded from the analysis, which covers 2016Q1 to 2025Q4. |
| JVWS note 2 | Religious organizations, private households, and federal, provincial/territorial and international public administration are excluded from the survey. | "Total, all industries" vacancies do not include these employers, while LFS unemployment covers all industries, so the ratio understates tightness. See README.md, "Limitations". |
| JVWS note 7 / LFS note 7 | Vacancies refer to the first day of the month (or vacant during the month); unemployment refers to the LFS reference week. | The two surveys measure slightly different moments. Both are combined at the quarterly level. |
| LFS note 7 | "Estimates in thousands, rounded to the nearest hundred." | Explains why our Canada total (sum of 10 rounded provinces) differs from the published Canada total by up to 200 persons. |
| LFS note 19 | Geography: "Excluding the territories." | Territories cannot be matched, so they are dropped from JVWS too, and national totals are built from the 10 provinces. |
| LFS note 11 | Estimates below a threshold are suppressed (1,500 for Canada, Quebec, Ontario, Alberta and British Columbia; 500 for Newfoundland and Labrador, Nova Scotia, New Brunswick, Manitoba and Saskatchewan; 200 for Prince Edward Island). | No unemployment value in the rows used is suppressed (the cleaned file has no missing values). |
| LFS note 1 | Explanation of seasonal adjustment. | Reason for using the Unadjusted series to match the unadjusted JVWS data, and for using complete calendar years in period comparisons. |

### 1.7 Course concordance table: `data/raw/concord.csv`

**Source:** provided by the PPOL 652 instructor. The instructor created the file during class on the author's computer, typing the header and the January row; Claude Code completed the remaining 11 months at the instructor's request. The file has not been changed since.

**Use:** only to validate the month-to-quarter rule (`make_quarter`) in `scripts/01_clean.py`. It is not merged into any data file.

| Column | Description | Values | Notes |
|---|---|---|---|
| `month` | Month name | January to December (12 rows, one per month) | Text |
| `q` | Calendar quarter the month belongs to | 1 to 4, each appearing 3 times | The file has a space after each comma, so the header reads `" q"`; the script reads it with `skipinitialspace=True` to ignore these spaces. |

---

## Part 2: Processed files

All processed files cover **2016Q1 to 2025Q4**. The raw files start in 2015, but 2015 is filtered out by `scripts/01_clean.py`.

Intermediate files `lfs_unemployment_quarterly.csv` (400 rows: 10 provinces x 40 quarters) and `jvws_vacancies_quarterly.csv` (380 rows: 10 provinces x 38 quarters, with 2020Q2 and 2020Q3 absent), produced by `scripts/01_clean.py`, contain the same `province`, `quarter`, `unemployed`, `vacancies` and `vacancy_quality_flag` columns described below, before merging.

### merged_province_quarter.csv

One row per province and quarter: 10 provinces x 40 quarters (2016Q1 to 2025Q4) = 400 rows. Produced by `scripts/02_merge_and_ratio.py`.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `province` | Province name | LFS and JVWS (`GEO` column) | Text | The 10 provinces only. The published "Canada" rows are dropped from both files, and the three territories are dropped from JVWS (LFS does not cover them). Used with `quarter` to join the two files. |
| `region` | Comparison region the province belongs to | Created in `02_merge_and_ratio.py` | Text | "Prairies" for Alberta, Saskatchewan and Manitoba; "Rest of Canada" for the other seven provinces. |
| `quarter` | Calendar quarter | Created from `REF_DATE` in `01_clean.py` | Text, format `YYYYQn` (e.g. `2019Q1`) | LFS: months grouped as Jan to Mar = Q1, Apr to Jun = Q2, Jul to Sep = Q3, Oct to Dec = Q4. JVWS: `REF_DATE` is the first month of the quarter (`2016-04` = 2016Q2). Covers 2016Q1 to 2025Q4. Kept as the key used to join the two datasets. |
| `year` | Calendar year of the quarter | Created from `quarter` in `02_merge_and_ratio.py` | Whole number (e.g. `2019`) | The first four characters of `quarter`. 2016 to 2025. |
| `quarter_number` | Quarter of the year | Created from `quarter` in `02_merge_and_ratio.py` | Whole number, 1 to 4 | The last character of `quarter` (1 = Jan to Mar, 2 = Apr to Jun, 3 = Jul to Sep, 4 = Oct to Dec). The script checks that `year` + "Q" + `quarter_number` rebuilds `quarter` in every row. |
| `unemployed` | Number of unemployed persons aged 15 and over, quarterly average | LFS: "Unemployment", "15 years and over", "Unadjusted" | Persons | Statistics Canada definition: see section 1.2. Raw `VALUE` (thousands of persons) multiplied by 1,000, then averaged over the three months of each quarter (every quarter uses exactly 3 months). Not seasonally adjusted, to match JVWS. Not rounded after averaging, so values can have decimals. No missing values. |
| `vacancies` | Number of job vacancies, all industries | JVWS: "Job vacancies", "Total, all industries" | Vacancies (positions) | Statistics Canada definition: see section 1.2 (excludes the industries listed in JVWS note 2). Raw `VALUE`, not rescaled. Not seasonally adjusted. Missing (blank, not zero) in 20 rows: all 10 provinces in 2020Q2 and 2020Q3 (not collected by Statistics Canada, JVWS note 12). No other missing values. |
| `ratio` | Vacancy-to-unemployment ratio: job vacancies per unemployed person | Calculated in `02_merge_and_ratio.py` | Vacancies per unemployed person (no units) | `vacancies / unemployed`. Above 1 = more vacancies than unemployed people (tight); well below 1 = slack. Missing in the same 20 rows as `vacancies`. Range in this file: 0.067 to 1.34. |
| `vacancy_quality_flag` | Statistics Canada data quality grade for the vacancy estimate | JVWS (`STATUS` column) | Code | See sections 1.2 and 1.5: A = excellent, B = very good, C = good, D = acceptable, E = use with caution, F = too unreliable to be published (value left blank). Blank in the 20 rows for 2020Q2 and 2020Q3, which have no JVWS record. Prairie provinces are all A or B (110 A, 4 B). |

### group_quarter.csv

One row per comparison group and quarter: 6 groups x 40 quarters (2016Q1 to 2025Q4) = 240 rows. Produced by `scripts/02_merge_and_ratio.py`.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group` | Comparison group | Created in `02_merge_and_ratio.py` | Text | Alberta, Saskatchewan, Manitoba (single provinces); Prairies (sum of the three Prairie provinces); Rest of Canada (sum of the other seven provinces); Canada (sum of all ten provinces, built from the provinces rather than the published Canada total). |
| `quarter` | Calendar quarter | As in `merged_province_quarter.csv` | Text, format `YYYYQn` | |
| `year` | Calendar year of the quarter | As in `merged_province_quarter.csv` | Whole number (e.g. `2019`) | |
| `quarter_number` | Quarter of the year | As in `merged_province_quarter.csv` | Whole number, 1 to 4 | |
| `unemployed` | Total unemployed persons aged 15 and over in the group | Sum of `unemployed` from `merged_province_quarter.csv` | Persons | No missing values. Canada = Prairies + Rest of Canada in every quarter. Within 200 persons (0.016%) of the published LFS Canada total, a difference due to Statistics Canada rounding to the nearest 100 persons (LFS note 7). |
| `vacancies` | Total job vacancies in the group | Sum of `vacancies` from `merged_province_quarter.csv` | Vacancies (positions) | Calculated only when every province in the group has a value (pandas `sum` with `min_count` = number of provinces in the group); otherwise blank, never zero or understated. Missing for all groups in 2020Q2 and 2020Q3, and nowhere else. The Canada total is 1,220 to 3,970 smaller than the published JVWS Canada total because it excludes the territories. |
| `ratio` | Group vacancy-to-unemployment ratio | Calculated in `02_merge_and_ratio.py` | Vacancies per unemployed person (no units) | Total `vacancies` divided by total `unemployed` for the group. Not an average of provincial ratios, so larger provinces carry more weight (the Prairies figure is dominated by Alberta). Missing wherever `vacancies` is missing. |
