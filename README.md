# Labour Market Tightness in the Prairie Provinces, 2016 to 2025

**Author:** Augustine Brown, Master of Public Policy student, Max Bell School of Public Policy, McGill University
**Course:** PPOL 652, Complexity Seminar (Advanced Stream), Fall 2026


## Research question

How has labour market tightness, measured as job vacancies per unemployed person, evolved in Alberta, Saskatchewan and Manitoba relative to the rest of Canada between 2016 and 2025, and have the three Prairie provinces followed a common trajectory?

## Why this matters

Labour shortages are a recurring concern in regional economic development policy, and the Prairie provinces are often discussed and served as a single region. If Alberta, Saskatchewan and Manitoba have experienced different labour market conditions, a Prairie-wide figure could hide those differences, and policies designed for a common regional labour market could be poorly targeted.

This project tests whether that regional framing holds for one standard indicator of labour market tightness, job vacancies per unemployed person. A descriptive answer is useful on its own, because it shows whether provincial figures, rather than a Prairie total, are needed when assessing labour shortages in the region.

## Summary of findings

Before the pandemic (2016 to 2019), all three Prairie provinces had fewer job vacancies per unemployed person than the rest of Canada, and all three tightened sharply through the 2021 to 2022 post-pandemic peak along with the rest of the country. In 2023 to 2025 they diverged: relative to the rest of Canada, Saskatchewan's labour market was 40% tighter (1.40) and Manitoba's 22% tighter (1.22), while Alberta's remained looser (0.91) (Figures 2 and 2b). After the peak, the clearest difference was in vacancies: average quarterly vacancies fell by about a third in the rest of Canada, by about 14% in Alberta and Manitoba, and by less than 2% in Saskatchewan (Figure 3). The combined Prairie figure for 2023 to 2025 (1.03) sits close to the rest of Canada and hides this divergence.

These are descriptive estimates. They show how tightness changed and which side of the ratio moved, but not why the provinces diverged. Differences are not significance-tested, and, in my assessment, the Labour Force Survey's exclusion of people living on reserves may make Saskatchewan and Manitoba appear somewhat tighter than they are.

## Data sources

Both datasets are published by Statistics Canada and were provided through the PPOL 652 curated dataset collection (Theme 3). The curated extracts end at 2025Q4, although Statistics Canada has since published later periods.

| File | Source | Frequency | Coverage | Units |
|---|---|---|---|---|
| `CA_Labour_Force_Monthly.csv` | Statistics Canada, Labour Force Survey, Table 14-10-0287-01 | Monthly | January 2015 to December 2025; Canada and the ten provinces | Persons, in thousands |
| `CA_Job_Vacancies_Wages_Quarterly.csv` | Statistics Canada, Job Vacancy and Wage Survey, Table 14-10-0442-01, "Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted for seasonality" (sector-level rows) | Quarterly | Q1 2015 to Q4 2025; Canada, provinces and territories | Number of vacant positions |

The PPOL 652 dataset list cites Table 14-10-0326-01, which was archived and replaced by Table 14-10-0442-01 (same sector-level estimates, with data to 2025Q4). `data/raw/concord.csv`, a month-to-quarter table started by the PPOL 652 instructor in class and completed by Claude Code at the instructor's request, is used only to check that the scripts assign months to quarters correctly. Column definitions and the relevant Statistics Canada notes are in `docs/data_dictionary.md`.

Statistics Canada data is used under the Statistics Canada Open Licence (https://www.statcan.gc.ca/en/reference/licence). Adapted from Statistics Canada, Table 14-10-0287-01 (Labour force characteristics, monthly, seasonally adjusted and trend-cycle) and Table 14-10-0442-01 (Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted for seasonality), accessed through the PPOL 652 curated dataset collection, October 2026. This does not constitute an endorsement by Statistics Canada of this product.

## Project structure

```
Advanced-Data-Analysis/
├── README.md                  This file
├── requirements.txt           Python packages needed to run the analysis
├── data/
│   ├── raw/                   Original CSV files, never modified
│   └── processed/             Cleaned and merged files produced by the scripts
├── scripts/
│   ├── 00_inspect_data.py     Initial inspection of both raw files
│   ├── 00b_explore_distributions.py  Summary statistics, outlier flags, the Q1 seasonality comparison and exploratory charts
│   ├── 01_clean.py            Filters and reshapes each dataset
│   ├── 02_merge_and_ratio.py  Joins the datasets and calculates the ratio
│   ├── 03_analysis.py         Period ratios, tightness relative to Rest of Canada, decomposition and sensitivity check
│   └── 04_figures.py          Produces the figures used in the report and presentation
├── outputs/
│   ├── figures/               Report figures from 04_figures.py, each as PNG (300 dpi) and SVG:
│   │   ├── fig1_tightness_over_time          Annual ratio, 2016 to 2025
│   │   ├── fig2_relative_to_rest_of_canada   Each province and the Prairies combined relative to Rest of Canada, by period
│   │   ├── fig2b_relative_diverging          Variant of Figure 2: % difference from Rest of Canada, bars diverging from 0
│   │   ├── fig3_change_after_peak            Change in vacancies and in unemployed persons after the 2021 to 2022 peak (two panels)
│   │   └── exploratory/       Exploratory charts from 00b_explore_distributions.py
│   └── tables/                Analysis tables from 03_analysis.py, plus annual_ratios.csv
│                              (the annual ratios plotted in Figure 1) from 04_figures.py
│                              and seasonal_q1_comparison.csv from 00b_explore_distributions.py
└── docs/
    ├── research_log.md        Dated record of decisions, problems and AI-generated code reviewed
    ├── data_dictionary.md     Definitions of the raw files, processed data, output tables and figures
    └── source_metadata/       Statistics Canada metadata files for the two source tables
```

## How to reproduce the analysis

1. Install Python 3.11 or later, then run `pip install -r requirements.txt` from the project folder.
2. Confirm that the three raw files are in `data/raw/`: `CA_Labour_Force_Monthly.csv`, `CA_Job_Vacancies_Wages_Quarterly.csv` and `concord.csv`.
3. Run the scripts in numerical order from the project folder:
   ```
   python scripts/00_inspect_data.py
   python scripts/00b_explore_distributions.py   # (exploratory checks and charts)
   python scripts/01_clean.py
   python scripts/02_merge_and_ratio.py
   python scripts/03_analysis.py
   python scripts/04_figures.py
   ```
4. Processed data is written to `data/processed/`, analysis tables to `outputs/tables/` and figures to `outputs/figures/`.

## Methodology

### Data preparation

Unadjusted monthly Labour Force Survey unemployment (persons aged 15 and over, converted from thousands to persons and averaged over the three months of each quarter) is joined to quarterly Job Vacancy and Wage Survey vacancies ("Total, all industries") for the ten provinces, 2016Q1 to 2025Q4 (`01_clean.py`, `02_merge_and_ratio.py`). Quarters without vacancy data stay missing. Each script that saves outputs does so only if every validation check passes; the checks and results are recorded in `docs/research_log.md`.

### Indicator

The indicator is job vacancies divided by unemployed persons. Higher values mean a tighter labour market. A ratio of 1 would mean one vacancy for every unemployed person; every group in this analysis stayed below 1 in all three comparison periods, so the analysis is about relative tightness. Ratios for Prairies, Rest of Canada (the seven other provinces) and Canada are calculated from summed vacancies and summed unemployment.

### Analysis

The main analysis is in `03_analysis.py`; the Q1 seasonality comparison is in `00b_explore_distributions.py`; each output table is defined in `docs/data_dictionary.md`.

- **Periods:** three periods of complete calendar years, the same for all groups: 2016 to 2019 (pre-pandemic, 16 quarters), 2021 to 2022 (post-pandemic peak, 8 quarters) and 2023 to 2025 (cooling, 12 quarters). Each period ratio is total vacancies divided by total unemployed over the period.
- **Comparison with the rest of Canada:** each group's period ratio is divided by the Rest of Canada ratio for the same period. Above 1 means tighter than the rest of Canada; below 1 means looser.
- **Decomposition:** the change in the ratio between consecutive periods is split exactly into a vacancies part and an unemployment part: log change in the ratio = log change in average quarterly vacancies minus log change in average quarterly unemployed.
- **Sensitivity check:** period values are recalculated as the simple average of the quarterly ratios. No province's position relative to the rest of Canada changes in any period.

### Key data decisions

| Decision | Reason |
|---|---|
| Use unadjusted Labour Force Survey data | The vacancy data is not seasonally adjusted, so both series are on the same basis. |
| Exclude the three territories | The Labour Force Survey file does not include them, so they cannot be matched. |
| Build national totals from the provinces | The published "Canada" vacancy total includes the territories while the Labour Force Survey total does not. |
| Treat Q2 and Q3 2020 as missing | Statistics Canada did not collect vacancy data for these quarters; they are not imputed, and charts show a break. 2020 is in no comparison period, because only Q1 and Q4 have vacancy data. |
| Compare periods of complete calendar years | Because the data is not seasonally adjusted, complete years represent every quarter of the year equally. |
| Analysis starts in 2016Q1 | The vacancy survey's first quarter, in 2015, had unpublished estimates for two provinces and low-quality estimates for all three Prairie provinces. |
| Build group ratios from totals, not averages of provincial ratios | Averaging ratios would give small provinces the same weight as large ones. |
| Retain Statistics Canada quality flags | Vacancy estimates graded below B are kept but noted. From 2016Q1 onward, all Prairie observations are graded A or B. |

## Limitations

- The ratio treats all vacancies and all unemployed people as interchangeable, so it cannot show whether unemployed workers have the skills, or live in the locations, that match the vacancies.
- The analysis is descriptive: it shows how tightness changed, not why the provinces' labour markets differ.
- Vacancy data is missing for 2020Q2 and 2020Q3, the most volatile period of the pandemic.
- Both surveys are sample-based estimates with sampling error, and some vacancy estimates carry lower quality grades.
- All-industry totals may hide differences between sectors.
- Job vacancies exclude federal, provincial and territorial public administration, private households and religious organizations (Job Vacancy and Wage Survey, note 2), so the ratio understates tightness. In my own assessment, this may understate the Rest of Canada ratio slightly more than the Prairies ratio, because federal public administration is concentrated in Ontario and Quebec.
- The Labour Force Survey excludes persons living on reserves and other Indigenous settlements in the provinces, full-time members of the Canadian Armed Forces and the institutionalized population, approximately 2% of the population aged 15 and older (Statistics Canada, Guide to the Labour Force Survey, 71-543-G, Section 4). In my own assessment, the reserve exclusion is likely to matter more for Saskatchewan and Manitoba, which have relatively large on-reserve populations, so their unemployment may be understated and their ratios may appear tighter than they are.
- Alberta accounts for between 66% and 74% of Prairie unemployment and between 61% and 69% of Prairie vacancies, depending on the quarter, so the Prairies figure mostly reflects Alberta; results are therefore also reported for each province separately.

## Use of AI tools

Analytical scripts and much of the project documentation (this README, the data dictionary and research log entries) were drafted with the assistance of Claude Code and Claude. The author made the key analytical decisions, reviewed and ran all code, reviewed the documentation by hand, and checked results by hand against the raw Statistics Canada data; checks performed and errors found are recorded in `docs/research_log.md`.

## References

Statistics Canada. Table 14-10-0287-01  Labour force characteristics, monthly, seasonally adjusted and trend-cycle. https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028701

Statistics Canada. Table 14-10-0442-01  Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted for seasonality. https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410044201

Statistics Canada. Guide to the Labour Force Survey (71-543-G). https://www150.statcan.gc.ca/n1/pub/71-543-g/71-543-g2025001-eng.htm