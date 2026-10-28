# Data Dictionary

This file has four parts:

1. **Statistics Canada codebook** for the two raw source files: table information, official definitions, the meaning of each raw column and code, and the Statistics Canada notes that affect this project. Definitions are quoted from the metadata files that Statistics Canada publishes with each table, saved in `docs/source_metadata/` (`Labour force characteristics_MetaData.csv` and `Job vacancies_MetaData.csv`). Note numbers refer to the "Note ID" in those files: LFS notes are from Table 14-10-0287-01 and JVWS notes are from Table 14-10-0442-01.
2. **Processed files**: every column in the files produced by the scripts in `data/processed/`.
3. **Analysis output tables**: every column in the tables produced by `scripts/03_analysis.py` in `outputs/tables/`.
4. **Figure table and figures**: `annual_ratios.csv` and the three figures produced by `scripts/04_figures.py`.

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

---

## Part 3: Analysis output tables

Produced by `scripts/03_analysis.py` from `data/processed/group_quarter.csv` and saved in `outputs/tables/`, only after every check has passed. Periods are assigned from the `year` column: **2016-2019** (16 quarters), **2021-2022** (8 quarters) and **2023-2025** (12 quarters). 2020 is in no period.

### period_ratios.csv

One row per group and period: 6 groups x 3 periods = 18 rows.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group` | Comparison group | `group_quarter.csv` | Text | Alberta, Saskatchewan, Manitoba, Prairies, Rest of Canada, Canada. |
| `period` | Comparison period | Assigned from `year` | Text | `2016-2019`, `2021-2022` or `2023-2025`. |
| `quarters` | Number of quarters in the period | Count | Quarters | 16, 8 or 12. |
| `total_vacancies` | Sum of the quarterly `vacancies` over the period | Sum of `vacancies` | Vacancy-quarters | A sum of quarterly values, used only to calculate the ratio; not a count of separate vacancies. |
| `total_unemployed` | Sum of the quarterly `unemployed` over the period | Sum of `unemployed` | Person-quarters | A sum of quarterly averages, used only to calculate the ratio; not a count of separate people. |
| `period_ratio` | Period vacancy-to-unemployment ratio | Calculated | Vacancies per unemployed person | `total_vacancies / total_unemployed` ("add up first, then divide"), so quarters with more unemployed people carry more weight. |

### relative_to_rest_of_canada.csv

One row per group and period: 18 rows.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group`, `period`, `period_ratio` | As in `period_ratios.csv` | `period_ratios.csv` | | |
| `rest_of_canada_ratio` | Rest of Canada's period ratio for the same period | `period_ratios.csv` | Vacancies per unemployed person | |
| `relative_to_rest_of_canada` | Group's period ratio divided by Rest of Canada's period ratio | Calculated | Ratio (no units) | Above 1 = tighter than Rest of Canada; below 1 = looser. Exactly 1 for Rest of Canada. |
| `position` | Label for `relative_to_rest_of_canada` | Calculated | Text | `tighter` (above 1), `looser` (below 1) or `same` (exactly 1). A description of the estimate, not a test of statistical significance. |

### quarterly_relative_to_rest_of_canada.csv

One row per group and quarter: 6 groups x 40 quarters = 240 rows. Intended for charts.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group`, `quarter`, `year`, `quarter_number`, `ratio` | As in `group_quarter.csv` | `group_quarter.csv` | | |
| `rest_of_canada_ratio` | Rest of Canada's ratio in the same quarter | `group_quarter.csv` | Vacancies per unemployed person | Blank in 2020Q2 and 2020Q3. |
| `relative_to_rest_of_canada` | Group's quarterly ratio divided by Rest of Canada's ratio in the same quarter | Calculated | Ratio (no units) | Blank (not zero) in the 12 rows for 2020Q2 and 2020Q3. Exactly 1 for Rest of Canada in every other quarter. |

### decomposition.csv

One row per group and change between consecutive periods: 5 groups (Alberta, Saskatchewan, Manitoba, Prairies, Rest of Canada) x 2 changes (2016-2019 to 2021-2022; 2021-2022 to 2023-2025) = 10 rows.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group` | Comparison group | | Text | Canada is not included. |
| `from_period`, `to_period` | The earlier and later period | | Text | |
| `avg_vacancies_from`, `avg_vacancies_to` | Average quarterly vacancies in each period | `total_vacancies / quarters` | Vacancies | Averages make periods of different lengths comparable. |
| `avg_unemployed_from`, `avg_unemployed_to` | Average quarterly unemployed in each period | `total_unemployed / quarters` | Persons | |
| `ratio_from`, `ratio_to` | Ratio of the average quarterly values | Calculated | Vacancies per unemployed person | Equal to `period_ratio` (checked in the script). |
| `pct_change_ratio`, `pct_change_vacancies`, `pct_change_unemployed` | Percentage change from the earlier to the later period | Calculated | Percent | |
| `log_change_ratio` | Natural log of (`ratio_to` / `ratio_from`) | Calculated | Log points | |
| `vacancies_part` | Natural log of (`avg_vacancies_to` / `avg_vacancies_from`) | Calculated | Log points | |
| `unemployed_part` | Minus the natural log of (`avg_unemployed_to` / `avg_unemployed_from`) | Calculated | Log points | Negative sign because more unemployed people lowers the ratio. `vacancies_part + unemployed_part = log_change_ratio` exactly (checked in the script). |
| `vacancies_share`, `unemployed_share` | Each part divided by `log_change_ratio` | Calculated | Share (no units) | The two shares add up to 1. A share below 0 or above 1 means the two parts moved the ratio in opposite directions. Shares are large and unstable when `log_change_ratio` is close to zero (for example Saskatchewan, 2021-2022 to 2023-2025, where the ratio changed by 1.3%). |

### trajectory_summary.csv

One row per Prairie province and period: 3 provinces x 3 periods = 9 rows.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `province`, `period`, `period_ratio`, `relative_to_rest_of_canada` | As in `relative_to_rest_of_canada.csv` | | | |
| `position_vs_rest_of_canada` | `tighter` or `looser` than Rest of Canada | Calculated | Text | Same rule as `position`. |
| `change_from_previous_period` | Whether the period ratio `rose` or `fell` compared with the previous period | Calculated | Text | Blank for 2016-2019 (no previous period). |
| `pct_change_from_previous_period` | Percentage change in the period ratio from the previous period | Calculated | Percent | Blank for 2016-2019. |

### sensitivity_averaging_method.csv

One row per group and period: 18 rows. Compares the main method with an alternative.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group`, `period` | As above | | Text | |
| `ratio_total_over_total` | Main method: `period_ratio` | `period_ratios.csv` | Vacancies per unemployed person | Weights each quarter by its number of unemployed people. |
| `ratio_average_of_quarters` | Alternative method: simple average of the quarterly ratios in the period | Calculated | Vacancies per unemployed person | Gives every quarter the same weight. |
| `difference` | `ratio_average_of_quarters` minus `ratio_total_over_total` | Calculated | Vacancies per unemployed person | |
| `relative_total_over_total`, `relative_average_of_quarters` | Ratio relative to Rest of Canada under each method | Calculated | Ratio (no units) | Each method's ratio divided by Rest of Canada's ratio under the same method. |
| `position_total_over_total`, `position_average_of_quarters` | `tighter`, `looser` or `same` under each method | Calculated | Text | |
| `position_changes` | Whether the position differs between the two methods | Calculated | `yes` / `no` | `no` in all 18 rows. |

---

## Part 4: Figure table and figures

Produced by `scripts/04_figures.py` from `data/processed/group_quarter.csv` and the tables in `outputs/tables/`, only after every check has passed.

### annual_ratios.csv

Saved in `outputs/tables/`. One row per group and year for the four groups shown in Figure 1 (Alberta, Saskatchewan, Manitoba, Rest of Canada) and the nine years 2016 to 2019 and 2021 to 2025: 4 x 9 = 36 rows. These are the values plotted in Figure 1.

| Variable name | Description | Source | Units | Notes |
|---|---|---|---|---|
| `group` | Comparison group | `group_quarter.csv` | Text | Alberta, Saskatchewan, Manitoba or Rest of Canada. |
| `year` | Calendar year | `year` in `group_quarter.csv` | Year | 2020 is not included: it has vacancy data for only two quarters (Q1 and Q4), so an annual ratio would add up 2 quarters of vacancies and 4 quarters of unemployed. |
| `quarters` | Number of quarters with vacancy data in the year | Count | Quarters | Always 4 (checked in the script). |
| `total_vacancies` | Sum of the quarterly `vacancies` over the year | Sum of `vacancies` | Vacancy-quarters | Used only to calculate the ratio. Adding up the years in each period gives the totals in `period_ratios.csv` (checked in the script). |
| `total_unemployed` | Sum of the quarterly `unemployed` over the year | Sum of `unemployed` | Person-quarters | Used only to calculate the ratio. |
| `annual_ratio` | Annual vacancy-to-unemployment ratio | Calculated | Vacancies per unemployed person | `total_vacancies / total_unemployed`, the same "add up first, then divide" rule as the period ratios. |

### Figures

Saved in `outputs/figures/`, each as PNG (300 dpi) and SVG. Every figure carries the same source and methodology note at the bottom, followed by figure-specific notes, except that Figure 3, which shows vacancies only, replaces the ratio definition with "Job vacancies are for all industries."

| File name (without extension) | What it shows | Data used |
|---|---|---|
| `fig1_tightness_over_time` | Annual ratio for Alberta, Saskatchewan, Manitoba and Rest of Canada, 2016 to 2025, with the three comparison periods shaded. The lines break at 2020, which is omitted. | `annual_ratios.csv` |
| `fig2_relative_to_rest_of_canada` | Each province's period ratio divided by Rest of Canada's, one group of bars per period, with a line at 1 (Rest of Canada). | `relative_to_rest_of_canada.csv` (`relative_to_rest_of_canada`) |
| `fig3_change_after_peak` | Percentage change in average quarterly vacancies, 2021-2022 to 2023-2025, for Alberta, Saskatchewan, Manitoba and Rest of Canada (one bar per group). The note states that unemployment changed by less than 6% in every group. | `decomposition.csv` (`pct_change_vacancies`; `pct_change_unemployed` for the note) |

Colours are the same in every figure: Alberta blue `#2a78d6`, Saskatchewan orange `#eb6834`, Manitoba aqua `#1baf7a`, Rest of Canada dark grey `#52514e`. The `outputs/figures/exploratory/` charts from `00b_explore_distributions.py` use a different, earlier colour scheme and are not report figures.
