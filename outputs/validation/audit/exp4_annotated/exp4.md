# Experiment 4: incremental value of PWTA-D over age + generic pulse shape

- ear: E1 delta AUROC -0.094 (perm p 0.667) -> **no evidence of incremental value**
- finger: E1 delta AUROC 0.004 (perm p 0.194) -> **no evidence of incremental value**

| endpoint                    | site   |   n |   n_pos_or_na |   n_with_any_D |   M0_age |   M1_age+generic |   M2_+PWTA_D |   delta_M2_M1 |   p_perm |   null_delta_95pct |   null_delta_median |   p_perm_freedman_lane |   null_fl_delta_median |   M1_spearman |   M2_spearman | adds_value   |
|:----------------------------|:-------|----:|--------------:|---------------:|---------:|-----------------:|-------------:|--------------:|---------:|-------------------:|--------------------:|-----------------------:|-----------------------:|--------------:|--------------:|:-------------|
| E1 HF vs HC, age 28-57      | ear    |  25 |            12 |             15 |    0.617 |            0.715 |        0.622 |        -0.094 |    0.667 |              0.06  |              -0.068 |                  0.545 |                 -0.089 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | ear    |  56 |            16 |             39 |    0.844 |            0.89  |        0.827 |        -0.063 |    0.954 |              0.016 |              -0.026 |                  0.996 |                 -0.026 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | ear    |  16 |           nan |              8 |   -0.215 |           -1.338 |       -2.162 |        -0.824 |    0.311 |              0.511 |              -1.448 |                  0.533 |                 -0.806 |        -0.208 |        -0.124 | False        |
| E1 HF vs HC, age 28-57      | finger |  27 |            14 |             24 |    0.628 |            0.908 |        0.913 |         0.004 |    0.194 |              0.037 |              -0.025 |                  0.607 |                  0.009 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | finger |  67 |            25 |             63 |    0.902 |            0.973 |        0.983 |         0.01  |    0.02  |              0.005 |              -0.009 |                  0.03  |                 -0.004 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | finger |  24 |           nan |             20 |   -0.125 |           -0.561 |       -0.6   |        -0.039 |    0.084 |              0.092 |              -0.643 |                  0.132 |                 -0.417 |        -0.133 |         0.291 | False        |
