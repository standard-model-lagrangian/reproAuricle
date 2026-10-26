# Experiment 4: incremental value of PWTA-D over age + generic pulse shape

- ear: E1 delta AUROC -0.109 (perm p 0.868) -> **no evidence of incremental value**
- finger: E1 delta AUROC -0.005 (perm p 0.174) -> **no evidence of incremental value**

| endpoint                    | site   |   n |   n_pos_or_na |   n_with_any_D |   M0_age |   M1_age+generic |   M2_+PWTA_D |   delta_M2_M1 |   p_perm |   null_delta_95pct |   null_delta_median |   p_perm_freedman_lane |   null_fl_delta_median |   M1_spearman |   M2_spearman | adds_value   |
|:----------------------------|:-------|----:|--------------:|---------------:|---------:|-----------------:|-------------:|--------------:|---------:|-------------------:|--------------------:|-----------------------:|-----------------------:|--------------:|--------------:|:-------------|
| E1 HF vs HC, age 28-57      | ear    |  26 |            13 |             17 |    0.572 |            0.661 |        0.552 |        -0.109 |    0.868 |              0.087 |              -0.045 |                  0.976 |                 -0.061 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | ear    |  58 |            18 |             42 |    0.849 |            0.86  |        0.795 |        -0.065 |    0.96  |              0.027 |              -0.028 |                  1     |                 -0.018 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | ear    |  18 |           nan |             10 |   -0.175 |           -1.021 |       -1.98  |        -0.959 |    0.315 |              0.315 |              -1.435 |                  0.75  |                 -0.726 |        -0.101 |         0.033 | False        |
| E1 HF vs HC, age 28-57      | finger |  28 |            15 |             25 |    0.594 |            0.925 |        0.92  |        -0.005 |    0.174 |              0.022 |              -0.037 |                  0.363 |                 -0.013 |       nan     |       nan     | False        |
| E2 HF vs HC, all            | finger |  69 |            27 |             65 |    0.9   |            0.966 |        0.978 |         0.012 |    0.016 |              0.006 |              -0.009 |                  0.036 |                 -0.004 |       nan     |       nan     | False        |
| E3 LVEF within HFC (CV R^2) | finger |  26 |           nan |             22 |   -0.143 |           -0.567 |       -0.513 |         0.054 |    0.06  |              0.074 |              -0.53  |                  0.06  |                 -0.421 |        -0.155 |         0.284 | False        |
