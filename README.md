# Labour Market Tightness in the Prairie Provinces, 2015 to 2025

**Author:** Augustine Brown, Master of Public Policy student, Max Bell School of Public Policy, McGill University
**Course:** PPOL 652, Complexity Seminar (Advanced Stream), Fall 2026
**Last updated:** [DATE]

## Research question

How has labour market tightness, measured as job vacancies per unemployed person, evolved in Alberta, Saskatchewan and Manitoba relative to the rest of Canada between 2015 and 2025, and have the three Prairie provinces followed a common trajectory?

## Why this matters

[One or two paragraphs on the policy relevance. For example: labour shortages are a recurring concern for regional economic development policy, and federal and provincial programs often treat "the Prairies" as a single region. If the three provinces' labour markets have diverged, policies designed for a common regional labour market may be poorly targeted.]

## Summary of findings

[To be completed after analysis. State the central finding in two or three sentences, and avoid causal language.]

## Data sources

Both datasets are published by Statistics Canada and were provided through the PPOL 652 curated dataset collection (Theme 3).

| File | Source | Frequency | Coverage | Units |
|---|---|---|---|---|
| `CA_Labour_Force_Monthly.csv` | Statistics Canada, Labour Force Survey, Table 14-10-0287-01 | Monthly | January 2015 to December 2025; Canada and the ten provinces | Persons, in thousands |
| `CA_Job_Vacancies_Wages_Quarterly.csv` | Statistics Canada, Job Vacancy and Wage Survey, Table 14-10-0326-01 | Quarterly | Q1 2015 to Q4 2025; Canada, provinces and territories | Vacancies in units (persons) |

Statistics Canada data is used under the Statistics Canada Open Licence. [Confirm the licence wording and add a link.]

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

[Expand this section as the analysis proceeds. The steps planned so far are listed below.]

1. From the Labour Force Survey, keep unemployment for persons aged 15 and over, using the unadjusted series.
2. Convert monthly unemployment to quarterly values by averaging the three months in each quarter.
3. Convert unemployment from thousands of persons to persons so that it matches the units of the vacancy data.
4. From the Job Vacancy and Wage Survey, keep job vacancies for "Total, all industries."
5. Join the two datasets on province and quarter.
6. Build comparison groups (Prairie provinces and rest of Canada) by summing provincial values, rather than using the published "Canada" totals.

### Key data decisions

| Decision | Reason |
|---|---|
| Use unadjusted Labour Force Survey data | The vacancy data is not seasonally adjusted, so both series should be on the same basis. |
| Exclude the three territories | The Labour Force Survey file does not include them, so they cannot be matched. |
| Build national totals from the provinces | The published "Canada" vacancy total includes the territories while the Labour Force Survey total does not, so the two totals are not directly comparable. |
| Treat Q2 and Q3 2020 as missing | Statistics Canada did not collect vacancy data for these quarters. They are shown as a gap rather than estimated. [Decide how 2020 is handled in any annual averages.] |
| Retain Statistics Canada quality flags | Vacancy estimates graded E ("use with caution") are kept but noted. [List any affected Prairie observations.] |

## Limitations

[Expand as needed. Points identified so far:]

- The ratio treats all vacancies and all unemployed people as interchangeable. It cannot show whether unemployed workers have the skills, or live in the locations, that match the available vacancies.
- The analysis is descriptive. It shows how tightness has changed but does not establish why the provinces' labour markets differ.
- Vacancy data is missing for two quarters of 2020, during the most volatile period of the pandemic.
- Both surveys are sample-based estimates with sampling error, and some vacancy estimates carry lower quality grades.
- The analysis uses all-industry totals, which may hide differences between sectors.

## Use of AI tools

Analytical scripts were written with the assistance of Claude Code. All generated code was reviewed, run and checked against the raw data by the author. Checks performed and errors found are recorded in `docs/research_log.md`.

## Contact

[Your McGill email address]
