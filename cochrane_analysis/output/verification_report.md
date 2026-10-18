# Comparison with the supplied forest plots

Calculated from the printed arm data using the methods documented in README.md. The comparison scope is the supplied figures.

Original-trial verification is tracked separately in [source verification status](../PRIMARY_SOURCE_VERIFICATION.md).

| Outcome | Figure overall estimate (95% CI) | R overall estimate (95% CI) | Effect and CI match at printed precision |
| --- | --- | --- | --- |
| 6-minute walk distance | MD 21.53 [4.33, 38.73] | MD 21.53 [4.33, 38.73] | Yes |
| NYHA functional class | SMD -0.27 [-0.47, -0.07] | SMD -0.27 [-0.47, -0.07] | Yes |
| Quality of life | SMD -0.06 [-0.22, 0.11] | SMD -0.06 [-0.22, 0.11] | Yes |
| Composite of HHF or all-cause mortality | OR 0.51 [0.28, 0.93] | OR 0.51 [0.28, 0.93] | Yes |
| Hospitalization for heart failure | OR 0.68 [0.36, 1.27] | OR 0.68 [0.36, 1.27] | Yes |
| All-cause mortality | OR 0.75 [0.36, 1.58] | OR 0.75 [0.36, 1.58] | Yes |
| QRS duration | MD -10.94 [-17.55, -4.34] | MD -11.01 [-17.68, -4.34] | No |
| Left ventricular ejection fraction | MD 1.14 [-0.95, 3.24] | MD 1.24 [-0.77, 3.26] | No |
| Left ventricular end-systolic volume | MD -3.32 [-8.32, 1.68] | MD -3.32 [-8.32, 1.68] | Yes |
| Pacing threshold | MD -0.08 [-0.36, 0.20] | MD -0.09 [-0.36, 0.19] | No |

## Audit counts

- match: 528
- mismatch: 80
- not_estimable_or_not_applicable: 46

The full audit is verification.csv; differences_from_figures.csv contains only strict numerical mismatches.

A mismatch means that calculations from the displayed inputs differ at the displayed output precision. Rounded inputs or software differences may explain very small discrepancies. Two inconsistent mean differences and the QRS confidence-interval discrepancy are detailed in README.md.

## Differences by outcome

| Outcome | Matches | Numerical differences | Unresolved source readings | Not applicable |
| --- | ---: | ---: | ---: | ---: |
| 6-minute walk distance | 51 | 0 | 0 | 4 |
| NYHA functional class | 51 | 0 | 0 | 4 |
| Quality of life | 44 | 3 | 0 | 4 |
| Composite of HHF or all-cause mortality | 56 | 0 | 0 | 7 |
| Hospitalization for heart failure | 67 | 0 | 0 | 4 |
| All-cause mortality | 68 | 0 | 0 | 7 |
| QRS duration | 54 | 17 | 0 | 4 |
| Left ventricular ejection fraction | 40 | 31 | 0 | 4 |
| Left ventricular end-systolic volume | 57 | 2 | 0 | 4 |
| Pacing threshold | 40 | 27 | 0 | 4 |
