# Experiment 3: D-wave flattening as a feature

Primary: PRIMARY finger reb_rise_frac vs LVEF | age (HFC): rho = -0.292, one-sided p = 0.0883 (two-sided 0.1765), n = 24 -> **weak/inconclusive**

## confounder sensitivity (primary)

| adjustment         |    rho |   p_two_sided |   n |
|:-------------------|-------:|--------------:|----:|
| age + HR           | -0.288 |         0.193 |  24 |
| age + beta-blocker | -0.29  |         0.19  |  24 |
| age + AF history   | -0.251 |         0.259 |  24 |
| age, CRT excluded  | -0.284 |         0.239 |  20 |
| unadjusted         | -0.242 |         0.255 |  24 |

## secondary (Holm)

| test                                                    |    stat |      p |   n |   p_holm |
|:--------------------------------------------------------|--------:|-------:|----:|---------:|
| ear_reb_rise_frac vs LVEF | age (HFC)                   | -0.2275 | 0.4148 |  16 |        1 |
| finger_no_rebound_frac vs LVEF | age (HFC)              |  0.3068 | 0.1544 |  24 |        1 |
| ear_no_rebound_frac vs LVEF | age (HFC)                 |  0.2785 | 0.3148 |  16 |        1 |
| ear flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40    |  0.575  | 0.7242 |  13 |        1 |
| finger flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40 |  0.6667 | 0.2255 |  20 |        1 |
| ear flatness AUROC, HF vs HC, age 28-57                 |  0.516  | 0.9134 |  25 |        1 |
| finger flatness AUROC, HF vs HC, age 28-57              |  0.544  | 0.7157 |  27 |        1 |

## descriptive

| test                                    |     rho |       p |   n |
|:----------------------------------------|--------:|--------:|----:|
| finger_reb_rise_frac vs age within HC   |  -0     |   0.998 |  42 |
| ear_reb_rise_frac vs age within HC      |  -0.056 |   0.732 |  40 |
| finger_no_rebound_frac vs age within HC | nan     | nan     |  42 |
| ear_no_rebound_frac vs age within HC    |   0.006 |   0.973 |  40 |
| ear D_sharpness vs LVEF | age (HFC)     |   0.55  |   0.201 |   8 |
| finger D_sharpness vs LVEF | age (HFC)  |  -0.098 |   0.689 |  20 |

## by group

| group         |   ('ear_reb_rise_frac', 'median') |   ('ear_reb_rise_frac', 'count') |   ('ear_no_rebound_frac', 'median') |   ('ear_no_rebound_frac', 'count') |   ('finger_reb_rise_frac', 'median') |   ('finger_reb_rise_frac', 'count') |   ('finger_no_rebound_frac', 'median') |   ('finger_no_rebound_frac', 'count') |
|:--------------|----------------------------------:|---------------------------------:|------------------------------------:|-----------------------------------:|-------------------------------------:|------------------------------------:|---------------------------------------:|--------------------------------------:|
| HF_EF>=50     |                             0.002 |                                5 |                               0.941 |                                  5 |                                0.084 |                                   8 |                                  0.433 |                                     8 |
| HF_unknown_EF |                           nan     |                                0 |                             nan     |                                  0 |                                0.237 |                                   1 |                                  0.5   |                                     1 |
| HFmrEF        |                             0.186 |                                3 |                               0     |                                  3 |                                0.345 |                                   4 |                                  0     |                                     4 |
| HFrEF         |                             0.022 |                                8 |                               0.746 |                                  8 |                                0.285 |                                  12 |                                  0     |                                    12 |
| control       |                             0.087 |                               40 |                               0.268 |                                 40 |                                0.244 |                                  42 |                                  0     |                                    42 |
