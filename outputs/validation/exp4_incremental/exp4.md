# Experiment 4: incremental value of PWTA-D over age + generic pulse shape

- ear: E1 delta AUROC -0.108 (perm p 0.864) -> **no evidence of incremental value**
- finger: E1 delta AUROC -0.005 (perm p 0.164) -> **no evidence of incremental value**

| endpoint                    | site   |   n |   n_pos_or_na |   n_with_any_D |   M0_age |   M1_age+generic |   M2_+PWTA_D |   delta_M2_M1 |   p_perm |   null_delta_95pct |   null_delta_median |   p_perm_freedman_lane |   null_fl_delta_median |   M1_spearman |   M2_spearman | adds_value   |
|:----------------------------|:-------|----:|--------------:|---------------:|---------:|-----------------:|-------------:|--------------:|---------:|-------------------:|--------------------:|-----------------------:|-----------------------:|--------------:|--------------:|:-------------|
| E1 HF vs HC, age 28-57      | ear    |  26 |            13 |             17 |    0.572 |            0.661 |        0.553 |        -0.108 |    0.864 |              0.087 |              -0.046 |                  0.974 |                 -0.062 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | ear    |  58 |            18 |             42 |    0.849 |            0.86  |        0.795 |        -0.066 |    0.96  |              0.027 |              -0.028 |                  1     |                 -0.018 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | ear    |  18 |           nan |             10 |   -0.175 |           -1.02  |       -1.913 |        -0.893 |    0.305 |              0.311 |              -1.42  |                  0.703 |                 -0.727 |        -0.1   |         0.037 | False        |
| E1 HF vs HC, age 28-57      | finger |  28 |            15 |             25 |    0.594 |            0.925 |        0.92  |        -0.005 |    0.164 |              0.021 |              -0.037 |                  0.367 |                 -0.012 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | finger |  69 |            27 |             65 |    0.9   |            0.963 |        0.978 |         0.014 |    0.012 |              0.006 |              -0.009 |                  0.03  |                 -0.004 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | finger |  26 |           nan |             22 |   -0.143 |           -0.567 |       -0.501 |         0.065 |    0.056 |              0.075 |              -0.542 |                  0.06  |                 -0.413 |        -0.154 |         0.289 | False        |
