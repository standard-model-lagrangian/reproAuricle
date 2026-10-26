# Experiment 2: ear vs finger rebound

## 2a concordance (rest windows S-clean at both sites)

| cohort   |   n_windows |   n_subjects |   both |   ear_only |   finger_only |   neither |   mcnemar_p |   share_discordant_finger_only |   subj_median_ear |   subj_median_finger |   subj_wilcoxon_p |
|:---------|------------:|-------------:|-------:|-----------:|--------------:|----------:|------------:|-------------------------------:|------------------:|---------------------:|------------------:|
| all      |        1353 |           58 |    801 |          4 |           500 |        48 |           0 |                          0.992 |             0.611 |                    1 |             0     |
| HC       |        1094 |           40 |    694 |          0 |           400 |         0 |           0 |                          1     |             0.704 |                    1 |             0     |
| HFC      |         259 |           18 |    107 |          4 |           100 |        48 |           0 |                          0.962 |             0.218 |                    1 |             0.007 |

## 2b trait: Spearman of subject ear rebound fraction with covariates

| scope   | covariate            |    rho |     p |   n |
|:--------|:---------------------|-------:|------:|----:|
| all     | Age                  | -0.205 | 0.123 |  58 |
| all     | male                 |  0.243 | 0.066 |  58 |
| all     | Height (cm)          |  0.313 | 0.017 |  58 |
| all     | BMI                  |  0.091 | 0.498 |  58 |
| all     | HR                   | -0.065 | 0.626 |  58 |
| all     | MAP                  | -0.261 | 0.048 |  58 |
| all     | ear_amp              |  0.218 | 0.101 |  58 |
| all     | finger_reb           |  0.275 | 0.037 |  58 |
| all     | ear_sensor_offset_cm | -0.146 | 0.425 |  32 |
| HC      | Age                  |  0.013 | 0.937 |  40 |
| HC      | male                 |  0.252 | 0.116 |  40 |
| HC      | Height (cm)          |  0.497 | 0.001 |  40 |
| HC      | BMI                  |  0.232 | 0.15  |  40 |
| HC      | HR                   | -0.056 | 0.729 |  40 |
| HC      | MAP                  | -0.372 | 0.018 |  40 |
| HC      | ear_amp              |  0.251 | 0.118 |  40 |
| HC      | ear_sensor_offset_cm | -0.146 | 0.425 |  32 |
| HFC     | Age                  | -0.387 | 0.113 |  18 |
| HFC     | male                 |  0.239 | 0.34  |  18 |
| HFC     | Height (cm)          | -0.004 | 0.987 |  18 |
| HFC     | BMI                  | -0.222 | 0.376 |  18 |
| HFC     | HR                   | -0.252 | 0.313 |  18 |
| HFC     | MAP                  | -0.188 | 0.455 |  18 |
| HFC     | ear_amp              |  0.082 | 0.747 |  18 |
| HFC     | finger_reb           |  0.406 | 0.094 |  18 |

Ear-sensor offset from the ear landmark (HC): median 0.54 cm, IQR 0.52-0.65 cm

## 2b state: within-record slope of rebound strength / presence on HR (per bpm) and MAP (per mmHg)

| channel    | x      | y             | partial   |   n_rec |   n_subj |   n_win |    beta |   beta_lo |   beta_hi |       r |    r_lo |    r_hi |
|:-----------|:-------|:--------------|:----------|--------:|---------:|--------:|--------:|----------:|----------:|--------:|--------:|--------:|
| PPG_Ear    | HR_ref | reb_rise_frac | -         |      88 |       59 |    5150 |  0.0004 |   -0.0005 |    0.0016 |  0.0496 | -0.0595 |  0.1715 |
| PPG_Ear    | MAP    | reb_rise_frac | -         |      87 |       59 |    4990 | -0.0019 |   -0.0029 |   -0.0012 | -0.2005 | -0.2617 | -0.142  |
| PPG_Ear    | HR_ref | reb           | -         |      88 |       59 |    5150 | -0.0058 |   -0.0097 |   -0.0015 | -0.163  | -0.272  | -0.0409 |
| PPG_Finger | HR_ref | reb_rise_frac | -         |     103 |       70 |    6022 |  0.0017 |    0.0005 |    0.003  |  0.1317 |  0.0394 |  0.2203 |
| PPG_Finger | MAP    | reb_rise_frac | -         |     101 |       69 |    5801 | -0.0013 |   -0.0022 |   -0.0004 | -0.0926 | -0.1514 | -0.0341 |
| PPG_Finger | HR_ref | reb           | -         |     103 |       70 |    6022 | -0.0006 |   -0.0017 |    0.0004 | -0.0457 | -0.1288 |  0.0251 |

## 2c transfer fit (ear ~ blurred, shifted finger)

|                                  |        0 |
|:---------------------------------|---------:|
| n_windows                        | 1353     |
| median_R2                        |    0.985 |
| q25_R2                           |    0.967 |
| share_R2_ge_0.95                 |    0.851 |
| median_sigma_ms                  |   60     |
| median_delta_ms                  |    2     |
| sigma_ear_reb (finger reb)       |   60     |
| sigma_ear_noreb (finger reb)     |   60     |
| window_AUROC_sigma_for_ear_noreb |    0.645 |
| subject_AUROC_sigma              |    0.616 |
| subject_spearman_sigma_vs_noreb  |    0.404 |
| n_subjects                       |   55     |
| share_sigma_at_grid_max          |    0.613 |
| posthoc_ext_median_sigma_ms      |   64     |
| posthoc_ext_median_R2            |    0.989 |
| posthoc_ext_share_at_max         |    0     |
| posthoc_ext_subject_AUROC        |    0.66  |

Decision: ear ≈ smoothed finger: **True**; smoothing explains rebound loss: **False**

## 2d deconvolution (sigma_pop from HC session 1 = 60 ms, post hoc ext grid 60 ms; held out = HC session 2 + HFC)

Baseline reproduces the pipeline: **True**

|                             | 0                   | 1                   | 2                   |
|:----------------------------|:--------------------|:--------------------|:--------------------|
| config                      | spec lam=0.01       | spec lam=0.1        | spec lam=0.001      |
| lambda                      | 0.01                | 0.1                 | 0.001               |
| sigma_pop_ms                | 60.0                | 60.0                | 60.0                |
| n_held_out_windows          | 898                 | 898                 | 898                 |
| SD_median_native            | 204.271509242661    | 202.19726770101465  | 203.1797879289823   |
| SD_median_rescued           | 218.13815856327386  | 184.34307585189174  | 210.63988851308272  |
| finger_minus_ear_SD_native  | -9.942794851712904  | -9.898099531329649  | -9.352804298075128  |
| finger_minus_ear_SD_rescued | -7.579752537156224  | 11.498733028405297  | -1.849642294844557  |
| yield_baseline              | 0.44320712694877507 | 0.44320712694877507 | 0.44320712694877507 |
| yield_corrected             | 0.7884187082405345  | 0.6469933184855234  | 0.8596881959910914  |
| yield_gain_pp               | 34.521158129175944  | 20.378619153674837  | 41.64810690423163   |
| n_rescued                   | 344                 | 198                 | 377                 |
| n_lost                      | 34                  | 15                  | 3                   |
| split_SD_rescued_median_ms  | 1.5360650240105542  | 1.0546165520231057  | 0.8321673050392633  |
| split_SD_native_median_ms   | 0.8593092972326843  | 0.7078510893627197  | 0.49825657126626766 |
| SD_in_100_350_rescued       | 0.752906976744186   | 0.9949494949494949  | 0.9893899204244032  |
| SD_HR_slope_corrected       | -1.3474793404251324 | -0.4602039527097153 | 0.24685109048066323 |
| SD_HR_slope_baseline        | -0.8443024468211184 | -0.8443024468211184 | -0.8443024468211184 |
| rho_with_finger_native      | 0.44698528276876426 | 0.44698528276876426 | 0.44698528276876426 |
| rho_with_finger_rescued     | 0.20178602082856487 | 0.4343333925084325  | 0.36637139698756754 |
| n_native_paired             | 341                 | 341                 | 341                 |
| n_rescued_paired            | 256                 | 130                 | 291                 |
| rho_native_pooled_original  | 0.3379353226735729  | 0.38077430404110585 | 0.2628081812902414  |
| rho_rescued_pooled_original | 0.22432612225997686 | 0.4887725490822829  | 0.42293492149912776 |
| native_SD_shift_median_ms   | 15.031007639687232  | 24.12384944057939   | 7.563414976964623   |
| native_SD_shift_gt10ms      | 0.6291208791208791  | 0.8825065274151436  | 0.389873417721519   |
| rescued                     | False               | True                | True                |

Decision (primary lambda = 0.01): rescued = **False**
