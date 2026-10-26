# Experiment 3: D-wave flattening as a feature

Primary: PRIMARY finger reb_rise_frac vs LVEF | age (HFC): rho = -0.270, one-sided p = 0.0963 (two-sided 0.1926), n = 26 -> **weak/inconclusive**

## confounder sensitivity (primary)

| adjustment         |    rho |   p_two_sided |   n |
|:-------------------|-------:|--------------:|----:|
| age + HR           | -0.265 |         0.211 |  26 |
| age + beta-blocker | -0.265 |         0.21  |  26 |
| age + AF history   | -0.228 |         0.284 |  26 |
| age, CRT excluded  | -0.27  |         0.236 |  22 |
| unadjusted         | -0.221 |         0.278 |  26 |

## secondary (Holm)

| test                                                    |    stat |      p |   n |   p_holm |
|:--------------------------------------------------------|--------:|-------:|----:|---------:|
| ear_reb_rise_frac vs LVEF | age (HFC)                   | -0.1395 | 0.5934 |  18 |        1 |
| finger_no_rebound_frac vs LVEF | age (HFC)              |  0.2565 | 0.2158 |  26 |        1 |
| ear_no_rebound_frac vs LVEF | age (HFC)                 |  0.1717 | 0.51   |  18 |        1 |
| ear flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40    |  0.6    | 0.5941 |  15 |        1 |
| finger flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40 |  0.6786 | 0.1789 |  22 |        1 |
| ear flatness AUROC, HF vs HC, age 28-57                 |  0.5533 | 0.6629 |  26 |        1 |
| finger flatness AUROC, HF vs HC, age 28-57              |  0.5179 | 0.89   |  28 |        1 |

## descriptive

| test                                    |     rho |       p |   n |
|:----------------------------------------|--------:|--------:|----:|
| finger_reb_rise_frac vs age within HC   |  -0     |   0.998 |  42 |
| ear_reb_rise_frac vs age within HC      |  -0.029 |   0.858 |  40 |
| finger_no_rebound_frac vs age within HC | nan     | nan     |  42 |
| ear_no_rebound_frac vs age within HC    |  -0.014 |   0.931 |  40 |
| ear D_sharpness vs LVEF | age (HFC)     |   0.498 |   0.172 |  10 |
| finger D_sharpness vs LVEF | age (HFC)  |  -0.152 |   0.512 |  22 |

## by group

| group         |   ('ear_reb_rise_frac', 'median') |   ('ear_reb_rise_frac', 'count') |   ('ear_no_rebound_frac', 'median') |   ('ear_no_rebound_frac', 'count') |   ('finger_reb_rise_frac', 'median') |   ('finger_reb_rise_frac', 'count') |   ('finger_no_rebound_frac', 'median') |   ('finger_no_rebound_frac', 'count') |
|:--------------|----------------------------------:|---------------------------------:|------------------------------------:|-----------------------------------:|-------------------------------------:|------------------------------------:|---------------------------------------:|--------------------------------------:|
| HF_EF>=50     |                             0.002 |                                5 |                               0.941 |                                  5 |                                0.084 |                                   8 |                                  0.433 |                                     8 |
| HF_unknown_EF |                           nan     |                                0 |                             nan     |                                  0 |                                0.237 |                                   1 |                                  0.5   |                                     1 |
| HFmrEF        |                             0.186 |                                3 |                               0     |                                  3 |                                0.345 |                                   4 |                                  0     |                                     4 |
| HFrEF         |                             0.028 |                               10 |                               0.718 |                                 10 |                                0.314 |                                  14 |                                  0     |                                    14 |
| control       |                             0.087 |                               40 |                               0.268 |                                 40 |                                0.244 |                                  42 |                                  0     |                                    42 |
