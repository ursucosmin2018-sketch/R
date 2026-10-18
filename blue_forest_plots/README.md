# Blue forest plots from the uploaded source-checked Excel files

The R script generates **nine primary outcome PNGs** and **four separately labelled sensitivity PNGs**, each at **300 DPI**. Every plot includes a pooled estimate, 95% confidence interval, study weights and heterogeneity statistics. The blue squares represent study estimates and the dark-blue diamond represents the random-effects pooled estimate.

- [Download the PNG files](blue_forest_plots_pngs.zip)
- [Download the code, input Excel files and results](blue_forest_plots_complete.zip)
- [View all plots](PLOTS.md)
- [R code](make_blue_forest_plots.R)
- [Pooled numerical results](output/pooled_results.csv)
- [Every primary-row inclusion/exclusion decision](output/all_87_primary_row_decisions.csv)
- [Selected source rows and reasons](output/selection_log.csv)

## Run in RStudio

Extract the complete ZIP, open its `blue_forest_plots` folder as an RStudio project, then run:

```r
source("make_blue_forest_plots.R")
```

Or run from a terminal:

```sh
Rscript make_blue_forest_plots.R
# Optional locations:
Rscript make_blue_forest_plots.R path/to/excels path/to/png_output
```

The script uses `meta`, `metafor` and `readxl`; it installs a missing package from CRAN. The nine uploaded outcome workbooks are in `inputs`. All nine match their previous export hashes. The uploaded import script expected 12 workbooks, so this new script handles the nine actually supplied without requiring the three LVESV files.

## Primary analyses

| PNG | Outcome | Estimable studies | Selection |
|---|---|---:|---|
| [01_walk.png](output/01_walk.png) | Six-minute walk distance | 4 | Same-scale MD; independent-arm estimate, reported contrasts and arm-CI estimate |
| [02_nyha.png](output/02_nyha.png) | NYHA functional class | 3 | Numeric class MD, not SMD; paired crossover data omitted |
| [03_qol.png](output/03_qol.png) | EQ-5D utility | 2 | Only comparable EQ-5D utility values; other scales omitted |
| [04_qrs.png](output/04_qrs.png) | QRS duration | 5 | Randomized-allocation estimates; timing and QRS measurement conventions vary |
| [05_lvef.png](output/05_lvef.png) | LVEF change | 7 | Change estimates only, including original study model contrasts |
| [06_threshold.png](output/06_threshold.png) | Pacing threshold | 3 | Six-month randomized comparisons; exploratory voltage MD because pulse widths/modalities differ |
| [07_composite.png](output/07_composite.png) | All-cause death or HF hospitalization | 2 | Strict two-component definition; two additional double-zero studies displayed |
| [08_hhf.png](output/08_hhf.png) | HF hospitalization | 5 | Excludes HeartSync's urgent-visit-inclusive definition; two double-zero studies displayed |
| [09_mortality.png](output/09_mortality.png) | All-cause mortality | 6 | Randomized-allocation counts; two double-zero studies displayed |

## Additional sensitivities

- [10_composite_broad.png](output/10_composite_broad.png): separate, broader all-cause death/HF-event composite including urgent visits; HeartSync and PhysioSync only. This is not the strict primary composite.
- [11_hhf_broad.png](output/11_hhf_broad.png): adds HeartSync's urgent-visit-inclusive HFH definition.
- [12_mortality_as_treated.png](output/12_mortality_as_treated.png): adds His-SYNC treatment-received mortality counts.
- [13_qrs_as_treated.png](output/13_qrs_as_treated.png): adds His-SYNC treatment-received QRS results.

## Statistical methods

**Pooling:** inverse-variance random-effects models, REML heterogeneity estimation, Hartung–Knapp 95% confidence intervals with a variance floor (`method.random.ci="HK"`, `adhoc.hakn.ci="se"`). Study-level CIs use the normal approximation; pooled CIs use the t distribution with k−1 degrees of freedom. With only two studies, pooled intervals can be extremely wide. This is a consequence of the selected uncertainty method, not an image-generation error. Near-zero nonzero OR limits are shown in scientific notation rather than as zero; exact results are in CSV files.

**Continuous outcomes:** mean differences in the original measurement units. Raw independent-arm uncertainty is `sqrt(SD_CSP^2/N_CSP + SD_BiVP^2/N_BiVP)`. Where a workbook supplies an original study contrast, the script uses that estimate and reconstructs its SE from the reported 95% CI using its width divided by `2*qnorm(.975)`. This is an approximation when confidence limits are rounded or based on a different reference distribution; reconstructed displayed CIs can differ slightly from the source's rounded limits. Adjusted/modelled and unadjusted contrasts are combined as an exploratory same-scale synthesis.

For LEFT-BUNDLE-CRT's unmodelled arm mean CIs, the script reconstructs each arm SE using `(upper-lower)/(2*qt(.975,N-1))`, then sums the independent arm variances. These are explicitly labelled **Arm CIs***. No raw patient SD is invented and no median is converted to a mean. The t-quantile assumption and source rounding limit precision.

Final-value and change MDs may be combined when they measure the same construct on the same scale in randomized comparisons; this is done for walking, NYHA, EQ-5D and QRS. LVEF uses changes throughout. No endpoint/change SMDs are mixed. Numeric NYHA class pooling is exploratory because NYHA is ordinal. EQ-5D results do not represent all quality-of-life scales.

**Binary outcomes:** odds ratios for CSP versus BiVP. A 0.5 continuity correction is applied to the four cells of a study's 2×2 table only when a zero cell requires it. Double-zero studies are displayed as not estimable and have zero pooled weight. Follow-up lengths vary and these cumulative odds ratios are not hazard ratios or annualized event rates.

## Source-data decisions

- LEVEL-AT and CONSYST-CRT share 70 participants. The larger CONSYST cohort is used for NYHA, QRS and LVEF. LEVEL-AT is used for verified clinical components and the six-month threshold analysis. **They never enter one pooled model together.** Cohort uniqueness is asserted in the R code, including for alternative worksheets whose cohort labels were less specific.
- Explicit six-month alternatives from the uploaded workbooks are used when appropriate; they are not silently substituted as long-term results. Exact worksheets, timepoints and reasons are recorded in `selection_log.csv`.
- Rows with missing observed sample sizes, missing SDs and no usable published contrast, unlabelled numerical graphs, or medians/IQRs only are omitted. Paired crossover estimates without their paired variance are omitted. Source fields remain unchanged.
- CONSYST's transplant-inclusive composite and CSP-SYNC's cardiovascular-death/worsening-HF composite are excluded from the strict primary composite. Broader HeartSync/PhysioSync composites are analysed separately.
- CSP-SYNC mortality uses the source-checked flowchart count of two CSP deaths; the previously documented narrative omission remains a source limitation.
- HOT-CRT echo changes use 44/44 observed participants. Its lead-based threshold comparison is excluded from the randomized threshold analysis.
- Threshold results are a descriptive, exploratory voltage comparison: the underlying pulse widths and pacing modalities differ. They must not be interpreted as a comparison of capture energy under standardized testing conditions.

The code's selection block is deliberately explicit. `has_inputs=TRUE` alone is not an automatic inclusion rule. Changes to the study selection or model should be reviewed before rerunning the analysis. These plots are an exploratory synthesis of the available verified data, not a reproduction of the earlier meta-analysis's pooled results.

## Validation

All models were checked independently with `metafor`: REML pooled effects and the manually reconstructed Hartung–Knapp intervals agree to within 0.0001 on the analysis scale. All models have unique cohort IDs. All 87 uploaded main-sheet rows have inclusion/exclusion records. PNGs were decoded and visually inspected; source files and output hashes are recorded. See `output/independent_validation.csv` and `output/validation_report.txt`.
