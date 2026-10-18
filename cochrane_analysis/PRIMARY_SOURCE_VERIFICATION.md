# Source verification status

## Completed: supplied meta-analysis

Karakasis P et al., Europace 2026;28:euag170, doi:10.1093/europace/euag170. The uploaded `cspmeta.pdf` was read, including its methods, Tables/Figures, reference list, and data-availability statement.

- Figures 1-3 on pages 6-8: 893 numeric study-table cells were extracted and compared with the CSVs. All arm data match. Three reference labels were corrected; derived estimates did not change.
- Figure 3 confirms the disputed QRS CSP SD of 20.00, LVEF CSP mean of 9.00, and threshold BiVP mean of 0.68.
- Pages 11-12 identify the source citations. The verification checklist now records 15 cited reports for 13 trials, including two follow-up reports.
- Page 11 states that underlying data are available on reasonable request to the corresponding author. The PDF does not contain the original trial reports or a complete underlying extraction dataset.

## Pending: original trial reports and supplements

No original trial publication has yet been accessed or numerically verified. Requests to research sites still fail at the environment proxy with `403 Forbidden`, including after a turn-scoped network permission grant. The saved research-domain configuration draft requires activation through environment settings and Publish. The draft now includes the journal hosts identified from the bibliography.

Priority reports for resolving the main discrepancies:

1. **His-SYNC (reference 35):** Upadhyay GA et al. On-treatment comparison between corrective His bundle pacing and biventricular pacing for cardiac resynchronization: a secondary analysis of the His-SYNC pilot trial. *Heart Rhythm*. 2019;16:1797-1807. Verify the QRS CSP SD and the analysis population.
2. **PhysioSync-HF (reference 31):** Zimerman A et al. Conduction system vs biventricular pacing in heart failure: the PhysioSync-HF randomized clinical trial. *JAMA Cardiology*. 2026;11:360-368. Verify both LVEF arm means and whether they are changes or follow-up values.
3. **LEFT-BUNDLE-CRT (reference 15):** Cano O et al. Left bundle branch area vs biventricular pacing for cardiac resynchronization therapy: the LEFT-BUNDLE-CRT trial. *European Heart Journal*. Published April 14, 2026. [doi:10.1093/eurheartj/ehag225](https://doi.org/10.1093/eurheartj/ehag225). Verify the pacing-threshold means, timing, and denominators.

The complete checklist, including His-Alternative, CSP-SYNC, LBBP-RESYNC, and Lustgarten, is [primary_source_verification.csv](data/primary_source_verification.csv). The meta-analysis cites an ESC press release for LECART (reference 29), and a conference abstract for the LBBP-RESYNC four-year follow-up (reference 38); these are not full trial reports.

## Current plots

All ten PNGs are calculations from the arm data printed in the supplied PDF. They have been compared with that PDF. They are **not yet verified against the original trial publications**, and no guessed corrections have been substituted. Seven overall effect/CI pairs reproduce the figure; QRS, LVEF, and threshold differ. The full statistical comparison is in [verification_report.md](output/verification_report.md).

Next steps are to obtain the original reports and supplements (or activate research-site access), record a table/page citation for each verified input, make only source-supported corrections, rerun the analyses, and update the files.
