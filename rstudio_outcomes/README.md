# Separate outcome files for RStudio

Each outcome is a **separate Excel document**. There are 12 documents covering the ten outcomes, because LVESV has three incompatible units.

| File | Outcome |
|---|---|
| [01_six_minute_walk_distance.xlsx](01_six_minute_walk_distance.xlsx) | Six-minute walk distance |
| [02_nyha_class.xlsx](02_nyha_class.xlsx) | NYHA class |
| [03_quality_of_life.xlsx](03_quality_of_life.xlsx) | Quality of life |
| [04_qrs_duration.xlsx](04_qrs_duration.xlsx) | QRS duration |
| [05_lvef.xlsx](05_lvef.xlsx) | Left ventricular ejection fraction |
| [06_lvesv_ml.xlsx](06_lvesv_ml.xlsx) | LV end-systolic volume, mL |
| [07_lvesv_percent_change.xlsx](07_lvesv_percent_change.xlsx) | LV end-systolic volume, relative percentage change |
| [08_lvesv_index_ml_m2.xlsx](08_lvesv_index_ml_m2.xlsx) | Indexed LV end-systolic volume, mL/m² |
| [09_pacing_threshold.xlsx](09_pacing_threshold.xlsx) | Pacing threshold |
| [10_composite_outcome.xlsx](10_composite_outcome.xlsx) | Composite clinical outcome; retain study-specific definitions |
| [11_heart_failure_hospitalization.xlsx](11_heart_failure_hospitalization.xlsx) | Heart-failure hospitalization; retain study-specific definitions |
| [12_all_cause_mortality.xlsx](12_all_cause_mortality.xlsx) | All-cause mortality |

## Import one file

```r
library(readxl)
qrs <- read_excel("04_qrs_duration.xlsx", sheet = "data")
```

Or open this folder as an RStudio project and run [import_outcomes.R](import_outcomes.R) to load all 12 files into the `outcomes` list.

## Clean data layout

The first worksheet, **data**, contains one study per row, plain column headers, and numeric Excel cells. It starts with:

- Continuous outcomes: `study`, `n_csp`, `mean_csp`, `sd_csp`, `n_biv`, `mean_biv`, `sd_biv`.
- Binary outcomes: `study`, `n_csp`, `event_csp`, `n_biv`, `event_biv`.

CSP is the experimental arm; BiVP is the comparator. `n` is the total number of participants, not the number without events. Remaining columns retain only essential measurement, timepoint, unit, shared-cohort and analysis-use information. `row_id` links to supporting worksheets.

**Blank cells remain missing.** This is a formatting simplification of the two uploaded source-checked workbooks, not new extraction or statistical imputation. All 96 primary rows and their 512 numeric arm-data cells are retained unchanged. Unverified forest-plot values have not been reintroduced.

`has_inputs = TRUE` means the required numerical fields are present as mean/SD or event counts. It does **not** mean a row should automatically enter the analysis. Review `analysis_use` and the source notes. For example, LEVEL-AT and CONSYST-CRT overlap, crossover data are paired, and clinical composite definitions differ.

## Supporting worksheets

Long audit columns are kept off the main data sheet:

- **review_notes**: source citations, verification status, population/denominator details and unresolved issues.
- **other_statistics**, where needed: medians/IQRs, model SEs or CIs. These are not raw SDs and have not been silently converted.
- **alternatives**, where available: other source timepoints/populations, kept separate to prevent duplicate inclusion.
- **reported_contrasts**, where available: the original study's between-group estimates and CIs.
- **read_me**: short explanation of the file and columns.

These supporting tabs belong to the relevant outcome document; outcomes are not combined into a single workbook.

## Reproducibility

`build_clean_files.py` accepts the original continuous and binary workbooks as its two arguments. `manifest.json` records input and output hashes. The files were opened and checked with R/readxl; see `validation_report.txt`.
