# Labour Market Tightness in the Prairie Provinces, 2016 to 2025

**Author:** Augustine Brown, Master of Public Policy student, Max Bell School of Public Policy, McGill University
**Course:** PPOL 652, Complexity Seminar (Advanced Stream), Fall 2026


## Research question

How has labour market tightness, measured as job vacancies per unemployed person, evolved in Alberta, Saskatchewan and Manitoba relative to the rest of Canada between 2016 and 2025, and have the three Prairie provinces followed a common trajectory?

## Why this matters

[One or two paragraphs on the policy relevance. For example: labour shortages are a recurring concern for regional economic development policy, and federal and provincial programs often treat "the Prairies" as a single region. If the three provinces' labour markets have diverged, policies designed for a common regional labour market may be poorly targeted.]

## Summary of findings

[To be completed after analysis. State the central finding in two or three sentences, and avoid causal language.]

## Data sources

Both datasets are published by Statistics Canada and were provided through the PPOL 652 curated dataset collection (Theme 3).

| File | Source | Frequency | Coverage | Units |
|---|---|---|---|---|
| `CA_Labour_Force_Monthly.csv` | Statistics Canada, Labour Force Survey, Table 14-10-0287-01 | Monthly | January 2015 to December 2025; Canada and the ten provinces | Persons, in thousands |
| `CA_Job_Vacancies_Wages_Quarterly.csv` | Statistics Canada, Job Vacancy and Wage Survey, Table 14-10-0442-01, "Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted for seasonality" (sector-level rows) | Quarterly | Q1 2015 to Q4 2025; Canada, provinces and territories | Vacancies in units (persons) |

The PPOL 652 dataset list cites Table 14-10-0326-01. That table was archived and replaced by Table 14-10-0442-01, which includes the same sector-level estimates. Because this file contains data to 2025Q4, after the archived table stopped being updated, it was taken from 14-10-0442-01.

`data/raw/concord.csv` is a month-to-quarter concordance table provided by the PPOL 652 instructor (started by the instructor in class and completed by Claude Code at the instructor's request). It is used only to check that the scripts assign months to quarters correctly.

The analysis uses the PPOL 652 curated extract of each table, which ends at 2025Q4 (December 2025 for the monthly Labour Force Survey data), although the Statistics Canada tables have since been updated with later periods.

Statistics Canada data is used under the Statistics Canada Open Licence (https://www.statcan.gc.ca/en/reference/licence). Adapted from Statistics Canada, Table 14-10-0287-01 (Labour force characteristics, monthly, seasonally adjusted and trend-cycle) and Table 14-10-0442-01 (Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted for seasonality), accessed through the PPOL 652 curated dataset collection, October 2026. This does not constitute an endorsement by Statistics Canada of this product.

## Project structure

```
labour-tightness-prairies/
├── README.md                  This file
├── requirements.txt           Python packages needed to run the analysis
├── data/
│   ├── raw/                   Original CSV files, never modified
│   └── processed/             Cleaned and merged files produced by the scripts
├── scripts/
│   ├── 00_inspect_data.py     Initial inspection of both raw files
│   ├── 01_clean.py            Filters and reshapes each dataset
│   ├── 02_merge_and_ratio.py  Joins the datasets and calculates the ratio
│   └── 03_figures.py          Produces the figures used in the report and presentation
├── outputs/
│   ├── figures/
│   └── tables/
└── docs/
    ├── research_log.md        Dated record of decisions, problems and AI-generated code reviewed
    └── data_dictionary.md     Definitions of every variable in the processed data
```

## How to reproduce the analysis

1. Install Python 3.10 or later.
2. Install the required packages by running `pip install -r requirements.txt` from the project folder.
3. Confirm that both raw CSV files are in `data/raw/`.
4. Run the scripts in numerical order from the project folder:
   ```
   python scripts/00_inspect_data.py
   python scripts/01_clean.py
   python scripts/02_merge_and_ratio.py
   python scripts/03_figures.py
   ```
5. Processed data will be written to `data/processed/` and figures to `outputs/figures/`.

## Methodology

### Indicator

The main indicator is the vacancy-to-unemployment ratio, calculated for each province and quarter as the number of job vacancies divided by the number of unemployed persons. A ratio above 1 means there are more vacancies than unemployed people, which indicates a tight labour market, and a ratio well below 1 indicates slack.

### Data preparation

Steps 1 to 4 are done in `scripts/01_clean.py` and steps 5 to 7 in `scripts/02_merge_and_ratio.py`. Each script runs validation checks and saves its output only if every check passes; the results are recorded in `docs/research_log.md`.

1. From the Labour Force Survey, keep unemployment for persons aged 15 and over, using the unadjusted series, for the ten provinces (the published "Canada" row is dropped), from January 2016 to December 2025.
2. Convert unemployment from thousands of persons to persons so that it matches the units of the vacancy data.
3. Convert monthly unemployment to quarterly values by averaging the three months in each quarter.
4. From the Job Vacancy and Wage Survey, keep job vacancies for "Total, all industries" for the ten provinces (the "Canada" row and the three territories are dropped), from 2016Q1 to 2025Q4. Each quarter is dated by its first month (`2016-04` is 2016Q2).
5. Join the two datasets on province and quarter, keeping every Labour Force Survey row so that quarters without vacancy data remain as missing values.
6. Calculate the ratio as vacancies divided by unemployed persons.
7. Build comparison groups (Alberta, Saskatchewan, Manitoba, Prairies, Rest of Canada, Canada) by summing provincial vacancies and unemployment separately and then dividing, rather than using the published "Canada" totals or averaging provincial ratios. A group total is calculated only when every province in the group has data.

### Key data decisions

| Decision | Reason |
|---|---|
| Use unadjusted Labour Force Survey data | The vacancy data is not seasonally adjusted, so both series should be on the same basis. |
| Exclude the three territories | The Labour Force Survey file does not include them, so they cannot be matched. |
| Build national totals from the provinces | The published "Canada" vacancy total includes the territories while the Labour Force Survey total does not, so the two totals are not directly comparable. |
| Treat Q2 and Q3 2020 as missing | Statistics Canada did not collect vacancy data for these quarters. They are not imputed; quarterly charts show a break in the line with a note at that point. 2020 is excluded from all period comparisons: it has only two quarters of vacancy data (Q1 and Q4) and falls between the comparison periods. |
| Compare three periods of complete calendar years, the same for all six groups: 2016 to 2019 (pre-pandemic, 16 quarters), 2021 to 2022 (post-pandemic peak, 8 quarters) and 2023 to 2025 (cooling, 12 quarters) | The periods separate the pre-pandemic labour market, the post-pandemic peak in vacancies and the cooling that followed. Because the data is not seasonally adjusted, each period contains complete calendar years so that every quarter of the year is equally represented. |
| Analysis starts in 2016Q1 | The vacancy survey began in 2015, but its first quarter had unpublished estimates for two provinces and low-quality estimates for all three Prairie provinces. Starting in 2016 also gives every comparison period complete calendar years, which matters because the data is not seasonally adjusted. |
| Build group ratios from totals, not averages of provincial ratios | Summing vacancies and unemployment first gives the ratio for the group as a whole. Averaging ratios would give small provinces the same weight as large ones. |
| Retain Statistics Canada quality flags | Vacancy estimates graded below B are kept but noted. From 2016Q1 onward, all Prairie observations are graded A or B. |

## Limitations

- The ratio treats all vacancies and all unemployed people as interchangeable. It cannot show whether unemployed workers have the skills, or live in the locations, that match the available vacancies.
- The analysis is descriptive. It shows how tightness has changed but does not establish why the provinces' labour markets differ.
- Vacancy data is missing for two quarters of 2020, during the most volatile period of the pandemic.
- Both surveys are sample-based estimates with sampling error, and some vacancy estimates carry lower quality grades.
- The analysis uses all-industry totals, which may hide differences between sectors.
- Job vacancies exclude federal, provincial and territorial public administration, private households and religious organizations (Job Vacancy and Wage Survey, note 2), while unemployment covers all industries, so the ratio understates tightness. In my own assessment (not a Statistics Canada statement), because federal public administration is concentrated in Ontario and Quebec, this exclusion may understate the Rest of Canada ratio slightly more than the Prairies ratio.
- The Prairies aggregate should be read with caution. Alberta accounts for between 66% and 74% of Prairie unemployment and between 61% and 69% of Prairie vacancies, depending on the quarter, so the Prairies figure mostly reflects Alberta and may hide differences between the three provinces. For this reason, results are also reported for Alberta, Saskatchewan and Manitoba separately.

## Use of AI tools

Analytical scripts were written with the assistance of Claude Code. All generated code was reviewed, run and checked against the raw data by the author. Checks performed and errors found are recorded in `docs/research_log.md`.

## References

Statistics Canada. Table 14-10-0287-01  Labour force characteristics, monthly, seasonally adjusted and trend-cycle

Statistics Canada. Table 14-10-0442-01  Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted for seasonality