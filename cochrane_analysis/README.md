# Cochrane-style forest plots from the new supplied figures

Six readable outcomes have been recalculated in R and rendered using `meta::forest(layout = "RevMan5")`. These are new analyses of the latest figures, with HBP and LBBAP subgroups. Earlier Excel data and the earlier screenshots are not used.

**Four outcomes are pending a higher-resolution source:** QRS duration, left ventricular ejection fraction, left ventricular end-systolic volume, and pacing threshold. The supplied four-panel image is too small to transcribe all means and SDs reliably. No values have been invented to complete these outcomes.

## Download individual PNG files

Each image is 4800 pixels wide at 300 DPI.

1. [6-minute walk distance](output/01_walk_distance.png)
2. [NYHA functional class](output/02_nyha.png)
3. [Quality of life](output/03_quality_of_life.png)
4. [Composite of HHF or all-cause mortality](output/04_composite_hhf_or_mortality.png)
5. [Hospitalization for heart failure](output/05_hhf.png)
6. [All-cause mortality](output/06_all_cause_mortality.png)

## Verification

The comparison is with **the numbers printed in the supplied figures**, not with the original study publications. No primary-publication PDFs, citations, or DOIs accompanied this request.

- All **51 estimable study effects and their 102 confidence limits** match the displayed values at two decimal places.
- The double-zero LBBP-RESYNC mortality study remains visible and is correctly not estimable with zero weight.
- All **18 subgroup/overall effects and their confidence limits** match the figures at two decimal places.
- All readable study/subgroup weights, I-squared values, tau-squared values, and subgroup-difference tests match at the displayed precision.
- The audit contains **337 numerical matches**, **30 not-estimable/not-applicable entries**, and **three unresolved source readings**. There are no confirmed numerical mismatches among the readable comparisons.

| Outcome | Recalculated overall effect (95% CI) | Figure comparison |
| --- | --- | --- |
| 6-minute walk distance | MD 21.53 [4.33, 38.73] | Match |
| NYHA functional class | SMD -0.27 [-0.47, -0.07] | Match |
| Quality of life | SMD -0.06 [-0.22, 0.11] | Match |
| Composite of HHF or all-cause mortality | OR 0.51 [0.28, 0.93] | Match |
| Hospitalization for heart failure | OR 0.68 [0.36, 1.27] | Match |
| All-cause mortality | OR 0.75 [0.36, 1.58] | Match |

### Three source readings requiring confirmation

The small heterogeneity-p-value text is not readable enough to certify the final digits. The plots display the **calculated** values below. Tentative source readings are preserved, flagged as uncertain, and excluded from match claims.

| Field | Tentative figure reading | R calculation |
| --- | --- | --- |
| Quality of life, HBP heterogeneity p | 0.4068 | 0.4066 |
| Quality of life, overall heterogeneity p | 0.3654 | 0.3652 |
| HHF, LBBAP heterogeneity p | 0.0265 | 0.0276 |

A higher-resolution copy of the first and third figures can settle those readings. A numerical difference cannot be attributed to a publication or to the analysis until the source value is confirmed. The quality-of-life overall tau-squared is reported in the source as **< 0.0001**; the recalculated value satisfies that inequality.

The complete machine-readable comparisons are in [verification.csv](output/verification.csv), with exact [study results](output/study_results.csv) and [pooled results](output/pooled_results.csv).

## Methods

- Inverse-variance random-effects pooling with REML tau-squared estimation, normal/Wald 95% confidence intervals, and separate tau-squared estimates in HBP and LBBAP subgroups.
- Continuous arm order is CSP minus BiVP. Walking distance uses a mean difference and unpooled within-study arm variances. NYHA and quality of life use Hedges' standardized mean difference (`method.smd = "Hedges"`, `exact.smd = TRUE`).
- Binary outcomes use **odds ratios**, CSP versus BiVP. The supplied binary columns are **events and total sample size**. A 0.5 continuity correction is applied to zero-cell studies; double-zero studies are not pooled.
- I-squared uses Cochran's Q, matching these new figures. The subgroup-difference test compares the subgroup random-effects estimates.
- These methods differ from the earlier screenshot reconstruction because the new figures use different data and effect measures.
- Direction labels follow the supplied figures: positive walking-distance and quality-of-life effects favor CSP; negative NYHA effects and ORs below one favor CSP. This does not independently validate the direction of every original quality-of-life scale.

Some continuous rows have values resembling changes from baseline and others resemble follow-up values. Outcome definitions, scales, directions, follow-up times, overlapping cohorts, and any crossover/paired-study analysis need confirmation against original publications before interpreting this as a validated new clinical meta-analysis. Reproducing a figure verifies its arithmetic, not those design choices.

## Run the R code

The current environment uses R 4.5.3 and `meta` 8.5.0. `metafor` and `readxl` are also installed. The script installs `meta` from CRAN if missing.

```bash
Rscript recreate_cochrane_plots.R
```

Or in RStudio with this directory as the working directory:

```r
source("recreate_cochrane_plots.R")
results <- run_analysis("data", "output")
```

The command-line script finds its data directory relative to its own path. Its optional first argument specifies another output directory. Source transcriptions are in `data/`; source readings and unresolved outcomes are explicitly recorded there. The output includes fitted models and R session information.
