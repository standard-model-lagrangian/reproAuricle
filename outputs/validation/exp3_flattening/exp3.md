# Experiment 3: D-wave flattening as a feature

Primary: PRIMARY finger reb_rise_frac vs LVEF | age (HFC): rho = -0.275, one-sided p = 0.0913 (two-sided 0.1826), n = 26 -> **weak/inconclusive**

## confounder sensitivity (primary)

| adjustment         |    rho |   p_two_sided |   n |
|:-------------------|-------:|--------------:|----:|
| age + HR           | -0.269 |         0.203 |  26 |
| age + beta-blocker | -0.271 |         0.2   |  26 |
| age + AF history   | -0.229 |         0.282 |  26 |
| age, CRT excluded  | -0.271 |         0.235 |  22 |
| unadjusted         | -0.224 |         0.271 |  26 |

## secondary (Holm)

| test                                                    |    stat |      p |   n |   p_holm |
|:--------------------------------------------------------|--------:|-------:|----:|---------:|
| ear_reb_rise_frac vs LVEF | age (HFC)                   | -0.1034 | 0.693  |  18 |        1 |
| finger_no_rebound_frac vs LVEF | age (HFC)              |  0.2647 | 0.2011 |  26 |        1 |
| ear_no_rebound_frac vs LVEF | age (HFC)                 |  0.1741 | 0.5038 |  18 |        1 |
| ear flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40    |  0.58   | 0.6787 |  15 |        1 |
| finger flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40 |  0.6786 | 0.1789 |  22 |        1 |
| ear flatness AUROC, HF vs HC, age 28-57                 |  0.5533 | 0.6629 |  26 |        1 |
| finger flatness AUROC, HF vs HC, age 28-57              |  0.5282 | 0.8177 |  28 |        1 |

## descriptive

| test                                    |     rho |       p |   n |
|:----------------------------------------|--------:|--------:|----:|
| finger_reb_rise_frac vs age within HC   |  -0     |   0.998 |  42 |
| ear_reb_rise_frac vs age within HC      |  -0.029 |   0.858 |  40 |
| finger_no_rebound_frac vs age within HC | nan     | nan     |  42 |
| ear_no_rebound_frac vs age within HC    |  -0.013 |   0.937 |  40 |
| ear D_sharpness vs LVEF | age (HFC)     |   0.727 |   0.026 |  10 |
| finger D_sharpness vs LVEF | age (HFC)  |  -0.343 |   0.128 |  22 |

## by group

| group         |   ('ear_reb_rise_frac', 'median') |   ('ear_reb_rise_frac', 'count') |   ('ear_no_rebound_frac', 'median') |   ('ear_no_rebound_frac', 'count') |   ('finger_reb_rise_frac', 'median') |   ('finger_reb_rise_frac', 'count') |   ('finger_no_rebound_frac', 'median') |   ('finger_no_rebound_frac', 'count') |
|:--------------|----------------------------------:|---------------------------------:|------------------------------------:|-----------------------------------:|-------------------------------------:|------------------------------------:|---------------------------------------:|--------------------------------------:|
| HF_EF>=50     |                             0.002 |                                5 |                               1     |                                  5 |                                0.074 |                                   8 |                                  0.468 |                                     8 |
| HF_unknown_EF |                           nan     |                                0 |                             nan     |                                  0 |                                0.237 |                                   1 |                                  0.5   |                                     1 |
| HFmrEF        |                             0.186 |                                3 |                               0     |                                  3 |                                0.346 |                                   4 |                                  0     |                                     4 |
| HFrEF         |                             0.018 |                               10 |                               0.817 |                                 10 |                                0.314 |                                  14 |                                  0     |                                    14 |
| control       |                             0.087 |                               40 |                               0.268 |                                 40 |                                0.244 |                                  42 |                                  0     |                                    42 |
