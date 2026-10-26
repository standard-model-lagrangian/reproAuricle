# Experiment 4: incremental value of PWTA-D over age + generic pulse shape

- ear: E1 delta AUROC -0.093 (perm p 0.663) -> **no evidence of incremental value**
- finger: E1 delta AUROC 0.002 (perm p 0.202) -> **no evidence of incremental value**

| endpoint                    | site   |   n |   n_pos_or_na |   n_with_any_D |   M0_age |   M1_age+generic |   M2_+PWTA_D |   delta_M2_M1 |   p_perm |   null_delta_95pct |   null_delta_median |   p_perm_freedman_lane |   null_fl_delta_median |   M1_spearman |   M2_spearman | adds_value   |
|:----------------------------|:-------|----:|--------------:|---------------:|---------:|-----------------:|-------------:|--------------:|---------:|-------------------:|--------------------:|-----------------------:|-----------------------:|--------------:|--------------:|:-------------|
| E1 HF vs HC, age 28-57      | ear    |  25 |            12 |             15 |    0.617 |            0.716 |        0.623 |        -0.093 |    0.663 |              0.061 |              -0.07  |                  0.531 |                 -0.089 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | ear    |  56 |            16 |             39 |    0.844 |            0.89  |        0.827 |        -0.063 |    0.956 |              0.016 |              -0.026 |                  0.996 |                 -0.026 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | ear    |  16 |           nan |              8 |   -0.215 |           -1.34  |       -2.177 |        -0.836 |    0.321 |              0.526 |              -1.451 |                  0.543 |                 -0.804 |        -0.208 |        -0.118 | False        |
| E1 HF vs HC, age 28-57      | finger |  27 |            14 |             24 |    0.628 |            0.91  |        0.912 |         0.002 |    0.202 |              0.034 |              -0.027 |                  0.593 |                  0.007 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | finger |  67 |            25 |             63 |    0.902 |            0.973 |        0.984 |         0.011 |    0.024 |              0.007 |              -0.008 |                  0.026 |                 -0.003 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | finger |  24 |           nan |             20 |   -0.125 |           -0.561 |       -0.607 |        -0.047 |    0.086 |              0.083 |              -0.649 |                  0.13  |                 -0.435 |        -0.133 |         0.288 | False        |
