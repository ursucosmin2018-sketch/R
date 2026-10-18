> **Primary-source audit now available:** [Source-checked Excel workbooks and audit](../verified_study_data/README.md). The plots in this folder reproduce the meta-analysis figure inputs. The primary-source audit identifies corrections, overlapping cohorts and incompatible endpoints; these plots are not a corrected, source-validated synthesis.

# Cochrane-style forest plots from the new supplied figures

All **ten outcomes** have been recalculated in R and rendered using `meta::forest(layout = "RevMan5")`. These are new analyses of the latest figures, with HBP and LBBAP subgroups. Earlier Excel data and the earlier screenshots are not used.

**All figure inputs have been checked against the supplied meta-analysis PDF. Original-trial verification remains pending access to those reports.** See [verification status](PRIMARY_SOURCE_VERIFICATION.md). The comparisons below currently cover the supplied figures only.

The higher-resolution four-panel image supplied the four remaining outcomes. The plots use the **arm values transcribed from the figures**. Calculated QRS, LVEF, and threshold results differ from some results printed beside those values; the differences are documented below.

## Download individual PNG files

Each image is 4800 pixels wide at 300 DPI. [Download all ten plots, R code, data, and reports](cochrane_plots_code_and_data.zip).

1. [6-minute walk distance](output/01_walk_distance.png)
2. [NYHA functional class](output/02_nyha.png)
3. [Quality of life](output/03_quality_of_life.png)
4. [Composite of HHF or all-cause mortality](output/04_composite_hhf_or_mortality.png)
5. [Hospitalization for heart failure](output/05_hhf.png)
6. [All-cause mortality](output/06_all_cause_mortality.png)
7. [QRS duration](output/07_qrs_duration.png)
8. [Left ventricular ejection fraction](output/08_lvef.png)
9. [Left ventricular end-systolic volume](output/09_lvesv.png)
10. [Pacing threshold](output/10_pacing_threshold.png)

## Verification

Verification compares calculations with **the numbers printed in the supplied figures**, as requested. The first six outcomes and LVESV reproduce the figure's overall effect and confidence interval at two decimal places. QRS, LVEF, and threshold differ when calculated from the transcribed arm data.

| Outcome | Figure overall effect (95% CI) | R calculation from arm data (95% CI) |
| --- | --- | --- |
| 6-minute walk distance | MD 21.53 [4.33, 38.73] | MD 21.53 [4.33, 38.73] |
| NYHA | SMD -0.27 [-0.47, -0.07] | SMD -0.27 [-0.47, -0.07] |
| Quality of life | SMD -0.06 [-0.22, 0.11] | SMD -0.06 [-0.22, 0.11] |
| HHF or all-cause mortality | OR 0.51 [0.28, 0.93] | OR 0.51 [0.28, 0.93] |
| HHF | OR 0.68 [0.36, 1.27] | OR 0.68 [0.36, 1.27] |
| All-cause mortality | OR 0.75 [0.36, 1.58] | OR 0.75 [0.36, 1.58] |
| QRS duration | MD -10.94 [-17.55, -4.34] | MD -11.01 [-17.68, -4.34] |
| LVEF | MD 1.14 [-0.95, 3.24] | MD 1.24 [-0.77, 3.26] |
| LVESV | MD -3.32 [-8.32, 1.68] | MD -3.32 [-8.32, 1.68] |
| Pacing threshold | MD -0.08 [-0.36, 0.20] | MD -0.09 [-0.36, 0.19] |

### Main discrepancies to resolve

The uploaded PDF (Figure 3, page 8) confirms all three highlighted input cells below. These are inconsistencies within the supplied meta-analysis, rather than errors reading those three cells from the image. The original trial reports are still needed to determine which inputs should be used in a corrected clinical analysis. No hypothetical replacement values have been applied.

1. **QRS, His-SYNC 2019:** CSP is transcribed as n = 16, mean = 125, **SD = 20**; BiVP is n = 24, mean = 164, SD = 25. The mean difference is -39 and its normal 95% CI is **[-53.00, -25.00]**. The figure reports **[-53.71, -24.29]**. A diagnostic calculation with CSP SD = 22 reproduces the reported CI and QRS pooled results, but that hypothetical value is not substituted into the data.
2. **LVEF, PhysioSync-HF 2026:** the means are transcribed as CSP **9.00** and BiVP 12.00. Their difference is **-3.00**, with CI **[-6.28, 0.28]**. The figure reports **-4.00 [-7.28, -0.72]**. This changes the pooled result and heterogeneity.
3. **Threshold, LEFT-BUNDLE-CRT 2026:** the means are transcribed as CSP 0.78 and BiVP **0.68**. Their difference is **0.10**, with CI **[-0.03, 0.23]**. The figure reports **0.12 [-0.01, 0.25]**. Additional smaller threshold differences are recorded in the full audit.

The three affected PNGs explicitly state that they were calculated from printed means, SDs, and sample sizes and that some results differ from the source.

- [Generated verification report](output/verification_report.md): all ten overall comparisons and audit counts by outcome.
- [Every comparison](output/verification.csv): exact calculated values, transcribed references, precision, and result.
- [Numerical differences only](output/differences_from_figures.csv): includes consequences for study weights, subgroup estimates, and heterogeneity.
- [Study results](output/study_results.csv) and [pooled results](output/pooled_results.csv).

Strict differences in the final digits of heterogeneity estimates or p-values can arise from rounded source inputs or software details; they are not automatically evidence of a substantive analytical error. The mean-difference arithmetic and larger QRS CI discrepancy warrant checking the underlying inputs. Inequalities such as p < 0.0001 are checked as inequalities.

### PDF audit and additional discrepancies

The PDF text layer allowed a check of **893 numeric study-table cells** in Figures 1-3 (pages 6-8). All **512 arm-data cells** agreed with the image transcriptions. Three comparison-reference cells were corrected: the CSP-SYNC QRS upper CI is printed as **5.51**, the LBBP-RESYNC LVESV effect as **-22.18**, and the Lustgarten LVEF upper CI as **6.28**. Those corrections affect the comparison report, not the R calculations. See [PDF transcription audit](output/pdf_transcription_audit.csv).

The PDF also resolves the earlier unclear heterogeneity labels:

| Source label | Printed PDF value | Recalculated value |
| --- | --- | --- |
| Quality of life, HBP heterogeneity p | 0.4068 | 0.4066 |
| Quality of life, overall heterogeneity p | 0.3254 | 0.3652 |
| Quality of life, overall tau-squared | 0.0001 | approximately 0.000000606 |
| HHF, LBBAP heterogeneity p | 0.0276 | 0.0276 |
| LVESV, HBP heterogeneity p | 0.9958 | 0.8958 |

For example, CSP-SYNC's QRS arm data yield **-1.00 [-10.51, 8.51]**, whereas Figure 3A prints **-1.00 [-10.51, 5.51]**. LBBP-RESYNC's LVESV means give **-77.74 - (-55.58) = -22.16**, whereas Figure 3C prints **-22.18**. The LVESV pooled estimate nevertheless agrees at two decimals. See the complete audit for further small differences.

The audit now has no unreadable reference values. Differences are recorded rather than changing the data to force agreement. In particular, confirming text in a meta-analysis is not equivalent to verifying the original trials.

Source: Karakasis P, Vlachos K, Siontis KC, et al. *Conduction system vs. biventricular pacing in heart failure with reduced ejection fraction: a meta-analysis of randomized controlled trials.* Europace. 2026;28:euag170. [doi:10.1093/europace/euag170](https://doi.org/10.1093/europace/euag170). Supplied file: `cspmeta.pdf`, 13 pages; SHA-256 `b00e985be0401d6832a84b0b00251865ee95a1c369b9d17fc51f38c72f69122a`.

## Methods

- Inverse-variance random-effects pooling with REML tau-squared estimation, normal/Wald 95% confidence intervals, and separate tau-squared estimates in HBP and LBBAP subgroups.
- Continuous arm order is CSP minus BiVP. Walking distance, QRS, LVEF, LVESV, and threshold use mean differences and unpooled within-study arm variances. NYHA and quality of life use Hedges' standardized mean difference (`method.smd = "Hedges"`, `exact.smd = TRUE`).
- Binary outcomes use **odds ratios**, CSP versus BiVP. The supplied binary columns are **events and total sample size**. A 0.5 continuity correction is applied to zero-cell studies; double-zero studies are not pooled.
- I-squared uses Cochran's Q, matching these new figures. The subgroup-difference test compares the subgroup random-effects estimates.
- These methods differ from the earlier screenshot reconstruction because the new figures use different data and effect measures.
- Direction labels follow the supplied figures: positive walking-distance, quality-of-life, and LVEF effects favor CSP; negative NYHA, QRS, LVESV, and threshold effects and ORs below one favor CSP. This does not independently validate the direction of every original quality-of-life scale.

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

A warning about source mismatches is expected and documented in the exported report. It does not mean that R failed to generate the plots.
