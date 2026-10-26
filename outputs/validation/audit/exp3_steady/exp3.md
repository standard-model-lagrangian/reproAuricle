# Experiment 3: D-wave flattening as a feature

Primary: PRIMARY finger reb_rise_frac vs LVEF | age (HFC): rho = -0.299, one-sided p = 0.0830 (two-sided 0.1660), n = 24 -> **weak/inconclusive**

## confounder sensitivity (primary)

| adjustment         |    rho |   p_two_sided |   n |
|:-------------------|-------:|--------------:|----:|
| age + HR           | -0.296 |         0.18  |  24 |
| age + beta-blocker | -0.293 |         0.186 |  24 |
| age + AF history   | -0.224 |         0.315 |  24 |
| age, CRT excluded  | -0.321 |         0.18  |  20 |
| unadjusted         | -0.264 |         0.212 |  24 |

## secondary (Holm)

| test                                                    |    stat |      p |   n |   p_holm |
|:--------------------------------------------------------|--------:|-------:|----:|---------:|
| ear_reb_rise_frac vs LVEF | age (HFC)                   | -0.1948 | 0.4867 |  16 |   1      |
| finger_no_rebound_frac vs LVEF | age (HFC)              |  0.4479 | 0.0321 |  24 |   0.2247 |
| ear_no_rebound_frac vs LVEF | age (HFC)                 |  0.3512 | 0.1993 |  16 |   1      |
| ear flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40    |  0.55   | 0.8329 |  13 |   1      |
| finger flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40 |  0.6667 | 0.2282 |  20 |   1      |
| ear flatness AUROC, HF vs HC, age 28-57                 |  0.5385 | 0.7648 |  25 |   1      |
| finger flatness AUROC, HF vs HC, age 28-57              |  0.544  | 0.7157 |  27 |   1      |

## descriptive

| test                                    |     rho |       p |   n |
|:----------------------------------------|--------:|--------:|----:|
| finger_reb_rise_frac vs age within HC   |   0.045 |   0.776 |  42 |
| ear_reb_rise_frac vs age within HC      |  -0.056 |   0.732 |  40 |
| finger_no_rebound_frac vs age within HC | nan     | nan     |  42 |
| ear_no_rebound_frac vs age within HC    |   0.059 |   0.718 |  40 |
| ear D_sharpness vs LVEF | age (HFC)     |   0.643 |   0.119 |   8 |
| finger D_sharpness vs LVEF | age (HFC)  |  -0.392 |   0.097 |  20 |

## by group

| group         |   ('ear_reb_rise_frac', 'median') |   ('ear_reb_rise_frac', 'count') |   ('ear_no_rebound_frac', 'median') |   ('ear_no_rebound_frac', 'count') |   ('finger_reb_rise_frac', 'median') |   ('finger_reb_rise_frac', 'count') |   ('finger_no_rebound_frac', 'median') |   ('finger_no_rebound_frac', 'count') |
|:--------------|----------------------------------:|---------------------------------:|------------------------------------:|-----------------------------------:|-------------------------------------:|------------------------------------:|---------------------------------------:|--------------------------------------:|
| HF_EF>=50     |                             0.002 |                                5 |                               1     |                                  5 |                                0.145 |                                   8 |                                  0.333 |                                     8 |
| HF_unknown_EF |                           nan     |                                0 |                             nan     |                                  0 |                                0.493 |                                   1 |                                  0.333 |                                     1 |
| HFmrEF        |                             0.194 |                                3 |                               0     |                                  3 |                                0.28  |                                   4 |                                  0     |                                     4 |
| HFrEF         |                             0.013 |                                8 |                               0.792 |                                  8 |                                0.264 |                                  12 |                                  0     |                                    12 |
| control       |                             0.09  |                               40 |                               0.177 |                                 40 |                                0.248 |                                  42 |                                  0     |                                    42 |
