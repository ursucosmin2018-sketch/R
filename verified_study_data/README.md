# CSP versus BiVP: primary-source audit

Checked all **96 study/outcome rows** across **13 uploaded documents**, covering **64 continuous and32 binary rows** in the10 plotted outcomes. Compared512 arm-data cells.

All13 supplied documents were reviewed. This does **not** mean all data are complete: missing supplements, follow-up reports, measured sample sizes and numerical graph data prevent some values from being certified. Blank cells are intentional.

## Workbooks

- `CSP_vs_BiVP_continuous_source_checked.xlsx`: seven continuous outcomes; LVESV separated into mL, percent change andmL/m2; additional source rows and published contrasts.
- `CSP_vs_BiVP_binary_source_checked.xlsx`: composite, HF hospitalization andall-cause mortality, with exact endpoint definitions.
- `CSP_vs_BiVP_audit_and_sources.xlsx`: all96 row reviews,512-cell audit, study citations/hashes andmissing-information list.

## Confirmed corrections and source discrepancies

|Study|Field|Forest|Source|Reference|
|---|---|---|---|---|
|His-SYNC2019|QRS CSP SD|20|22|p6 on-treatment results|
|PhysioSync-HF2026|LVEF CSP mean change|9|8|p6 Table2|
|HOT-CRT2023|EQ5D BiVP mean change|0.08|0.07|p8 Table4|
|His-Alternative2021|6MWD CSP N|46|25|p6 Table3 ITT|
|ALTERNATIVE-AF2022|QRS CSP mean|107.7|107.6|p4 Table1 andp5|
|LBBP-RESYNC2022|LVEF endpoint SDs|8.54 /8.69|13.2 /9.4|p7 Figure3A|
|HOT-CRT2023|Echo endpoint N|50 /50|44 /44|p5 follow-up completion; p8 Table4|
|HOT-CRT2023|Threshold N|50 /50|57 /43|p5 Table2 pacing-parameter subheading|
|His-SYNC2019|LVESV sign and units|+22 /+19; treated as volume|-22% /-19%; relative change|p7 on-treatment results|
|CONSYST-CRT2025|LVESV unit and N|volume;67 /67|relative percent;66 /62|p6 Table2 andfootnote|
|LEFT-BUNDLE-CRT2026|LVESV unit|mL|mL/m2|pp8-9 Table2|
|CSP-SYNC2025|All-cause deaths CSP|1|2|p4 Figure1|

See `confirmed_corrections.csv` and workbook notes for population, source uncertainty andtimepoint qualifications.

## Changes needed before pooling

**Shared participants.** CONSYST-CRT Methods explicitly says first70 participants came from LEVEL-AT. Do not count these as independent trials for the same pooled outcome. Source: CONSYST-CRT.pdf p2, Study population.

**Incompatible LVESV units.** His-SYNC and CONSYST report relative percent change; LEFT-BUNDLE reports indexed mL/m2; other trials report mL. Separate outcome sheets preserve this distinction. Source: His-SYNC p7; CONSYST p6 Table2; LEFT-BUNDLE pp8-9 Table2.

**Different composite endpoints.** PhysioSync adds urgent HF visits; CONSYST adds transplantation; CSP-SYNC uses cardiovascular death and worsening HF; HeartSync HFH includes urgent IV-diuretic visits. Do not label all as inpatient HFH or all-cause death. Source: Study definitions and source summaries in row audit.

**Crossover observations.** Lustgarten and ALTERNATIVE-AF repeated treatment measurements are paired. Randomized sequence Ns are not denominators for treatment-period event ORs. Source: Lustgarten pp2-4; ALTERNATIVE-AF pp3-5.

**Outcome N versus group N.** Randomization/table-header N is stored separately from outcome N. Missing observed N is blank, not silently copied from enrollment. Source: HOT-CRT p5; PhysioSync p6; HeartSync p5.

**Model uncertainty is not raw SD.** LBBP-RESYNC LS mean SEs and CSP-SYNC longitudinal-model CIs are preserved. Multiplying model SE bysqrt(N) need not recover patient SD. Study contrasts are provided separately. Source: LBBP-RESYNC p8 Table3; CSP-SYNC pp4-6.

**Medians are not observed means.** Median/IQR values remain median/IQR. No unlabelled median-to-mean conversion has been applied. Source: His-SYNC, CSP-SYNC, LEFT-BUNDLE source tables.

**Change and endpoint SMD.** NYHA and QoL figures mix endpoint and change values. SMDs based on endpoint SDs and change SDs cannot automatically be combined as if equivalent. Harmonize type and direction first. Source: Source measurement_type/scale columns.

**Different pacing thresholds.** Pulse widths, lead-capture versus QRS-correction thresholds, and implant/follow-up times differ. Voltage alone is not fully comparable without these details. Source: His-SYNC Table2; HOT-CRT Table2; other threshold source notes.

**Follow-up extension unavailable.** Older uploaded trial papers do not verify later follow-up outcomes. Six-month alternatives are separate records, not silent corrections to longer-term data. Source: His-Alternative2021; LBBP-RESYNC2022.

**CSP is not uniformly LBBAP.** The forest subgroup called LBBAP contains CSP strategies with HBP, deep septal pacing, crossovers and hybrid pacing. Original subgroup label is retained as figure_subgroup only. Source: LEVEL-AT, CONSYST, HOT-CRT, PhysioSync and LEFT-BUNDLE methods.

**Exact versus rounded.** Reported means/CIs are rounded and adjusted study contrasts may differ from the simple difference of rounded arm means. These are not automatically extraction errors. Source: Study_contrasts sheet.

## Missing information

- **His-Alternative 2021:** Frandsen et al2026 long-term follow-up; DOI10.1016/j.jacep.2026.02.016. Uploaded2021 paper ends at6 months. Long-term forest entries cannot be verified from it.
- **LBBP-RESYNC 2022:** Zou et al2026 four-year follow-up abstract/presentation; HeartRhythm23:S62-S63. Uploaded2022 paper reports no6-month events and randomized20/20. Forest uses22/18 and later events.
- **LECART 2026:** EHRA2026 LECART presentation or full arm-level outcome tables. Press release lacks arm denominators and exact component counts. Rounded primary-composite percentages cannot recover these.
- **LEFT-BUNDLE-CRT 2026:** Online supplementary TablesS3 andS4; unindexed LVESV if needed. Threshold numbers absent. Available LVESV change is indexed in mL/m2, not mL.
- **PhysioSync-HF 2026:** Supplement2 SAP and Supplement3 eTable1/outcome sample sizes. Main paper supplies continuous mean/SD but not individual outcome Ns; threshold forest values not in main paper.
- **CONSYST-CRT 2025:** Supplemental Table1 and separate clinical components/overlap. Main report composite includes transplantation; individual component counts unavailable in supplied PDF.
- **ALTERNATIVE-AF 2022:** Supplemental Tables1-3 and crossover-period denominators/covariance. Need period-specific thresholds, at-risk denominators, and paired uncertainty;25/25 sequence counts are not exposure-period denominators.
- **Lustgarten 2015:** Numerical data behind Figures2-4, paired covariance and vector-specific QRS Ns. Unlabelled graphs do not certify decimal SDs; QoL prose/bar and walking units disagree.
- **HOT-CRT 2023:** Outcome-specific Ns for6-month QRS,walking andQoL. Group heading50/50 is not measured N;44/44 completed follow-up including echo.
- **HeartSync-LBBP 2026:** Observed Ns for last-follow-up continuous outcomes. Table2 heading100/100 denotes randomization; measured last-follow-up N not separately reported.
- **LEVEL-AT 2022:** Six-month measured echo Ns / missing-data handling. Table2 header35/35, but two BiVP deaths and forest LVEF N35/33. Shared cohort with CONSYST must also be handled.
- **CSP-SYNC 2025:** Clarification of mortality timing and raw continuous SDs if arm-based analysis is intended. Figure1 shows two LBBAP deaths; narrative only describes its cardiovascular death. Mixed-model CIs do not provide raw patient SDs.
- **His-SYNC 2019:** Raw mean/SDs or explicit median-conversion plan; randomized allocation data for ITT synthesis. Published source uses medians/IQRs and treatment-received groups16/24.

## Reproducibility

The original forest-input CSVs remain unchanged in `../cochrane_analysis/data`. `extract_sources.py` contains the manually verified,page-referenced extraction; `source_extraction.json` is the resulting record. `build_workbooks.py` writes the Excel/CSV files. `validate_workbooks.R` reads every outcome sheet with`readxl`,checks key source corrections, validates numerical fields and confirms source references.

No corrected pooled forest plot is presented here: the source audit identifies overlapping cohorts andincompatible definitions/statistics that first require an explicit synthesis plan. The earlier plots reproduce the meta-analysis inputs andshould not be treated as source-validated results.

PDFs were used only as source documents andwere not uploaded to GitHub. DOI links/citations andfile hashes identify the sources.
