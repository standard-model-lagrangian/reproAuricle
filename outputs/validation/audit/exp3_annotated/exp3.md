# Experiment 3: D-wave flattening as a feature

Primary: PRIMARY finger reb_rise_frac vs LVEF | age (HFC): rho = -0.300, one-sided p = 0.0825 (two-sided 0.1650), n = 24 -> **weak/inconclusive**

## confounder sensitivity (primary)

| adjustment         |    rho |   p_two_sided |   n |
|:-------------------|-------:|--------------:|----:|
| age + HR           | -0.295 |         0.183 |  24 |
| age + beta-blocker | -0.298 |         0.178 |  24 |
| age + AF history   | -0.253 |         0.256 |  24 |
| age, CRT excluded  | -0.285 |         0.237 |  20 |
| unadjusted         | -0.246 |         0.248 |  24 |

## secondary (Holm)

| test                                                    |    stat |      p |   n |   p_holm |
|:--------------------------------------------------------|--------:|-------:|----:|---------:|
| ear_reb_rise_frac vs LVEF | age (HFC)                   | -0.1948 | 0.4867 |  16 |   1      |
| finger_no_rebound_frac vs LVEF | age (HFC)              |  0.3177 | 0.1396 |  24 |   0.9771 |
| ear_no_rebound_frac vs LVEF | age (HFC)                 |  0.3062 | 0.267  |  16 |   1      |
| ear flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40    |  0.55   | 0.8329 |  13 |   1      |
| finger flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40 |  0.6667 | 0.2255 |  20 |   1      |
| ear flatness AUROC, HF vs HC, age 28-57                 |  0.516  | 0.9134 |  25 |   1      |
| finger flatness AUROC, HF vs HC, age 28-57              |  0.5549 | 0.6446 |  27 |   1      |

## descriptive

| test                                    |     rho |       p |   n |
|:----------------------------------------|--------:|--------:|----:|
| finger_reb_rise_frac vs age within HC   |  -0     |   0.998 |  42 |
| ear_reb_rise_frac vs age within HC      |  -0.056 |   0.732 |  40 |
| finger_no_rebound_frac vs age within HC | nan     | nan     |  42 |
| ear_no_rebound_frac vs age within HC    |   0.007 |   0.967 |  40 |
| ear D_sharpness vs LVEF | age (HFC)     |   0.67  |   0.099 |   8 |
| finger D_sharpness vs LVEF | age (HFC)  |  -0.273 |   0.258 |  20 |

## by group

| group         |   ('ear_reb_rise_frac', 'median') |   ('ear_reb_rise_frac', 'count') |   ('ear_no_rebound_frac', 'median') |   ('ear_no_rebound_frac', 'count') |   ('finger_reb_rise_frac', 'median') |   ('finger_reb_rise_frac', 'count') |   ('finger_no_rebound_frac', 'median') |   ('finger_no_rebound_frac', 'count') |
|:--------------|----------------------------------:|---------------------------------:|------------------------------------:|-----------------------------------:|-------------------------------------:|------------------------------------:|---------------------------------------:|--------------------------------------:|
| HF_EF>=50     |                             0.002 |                                5 |                               1     |                                  5 |                                0.074 |                                   8 |                                  0.468 |                                     8 |
| HF_unknown_EF |                           nan     |                                0 |                             nan     |                                  0 |                                0.237 |                                   1 |                                  0.5   |                                     1 |
| HFmrEF        |                             0.186 |                                3 |                               0     |                                  3 |                                0.346 |                                   4 |                                  0     |                                     4 |
| HFrEF         |                             0.013 |                                8 |                               0.866 |                                  8 |                                0.282 |                                  12 |                                  0     |                                    12 |
| control       |                             0.087 |                               40 |                               0.268 |                                 40 |                                0.244 |                                  42 |                                  0     |                                    42 |
