## window_integrity

| windows   |   n_ppg |   n_ref |   matched |   label_mismatch |   overlapping |   annotated_windows_checked |   spanning_two_labels |   unannotated_windows | unannotated_records                |
|:----------|--------:|--------:|----------:|-----------------:|--------------:|----------------------------:|----------------------:|----------------------:|:-----------------------------------|
| rest      |    1814 |    1814 |      1814 |                0 |             0 |                        1721 |                     0 |                    93 | HC_1_1 HC_38_2 HFC_108_1 HFC_124_1 |
| all_20s   |    7062 |    7062 |      7062 |                0 |             0 |                        6783 |                     0 |                   279 | HC_1_1 HC_38_2 HFC_108_1 HFC_124_1 |

## truncation

| channel    | HR_bin   |    n |   rebound_span_cut_by_800ms_end |   no_rebound_800 |   no_rebound_1200 |   rebound_flips_no_to_yes |   PW50_missing_800 |   PW50_missing_1200 |   median_RR_ms |
|:-----------|:---------|-----:|--------------------------------:|-----------------:|------------------:|--------------------------:|-------------------:|--------------------:|---------------:|
| PPG_Ear    | 0-60     |  153 |                          0.634  |           0.451  |            0.451  |                         0 |             0      |                   0 |        1106    |
| PPG_Ear    | 60-70    |  265 |                          0.566  |           0.3585 |            0.3472 |                         3 |             0.0679 |                   0 |         908.5  |
| PPG_Ear    | 70-80    |  491 |                          0.7821 |           0.4501 |            0.442  |                         4 |             0.0489 |                   0 |         799    |
| PPG_Ear    | 80-90    |  314 |                          0.7898 |           0.3758 |            0.3726 |                         1 |             0      |                   0 |         714.25 |
| PPG_Ear    | >90      |  183 |                          0.5628 |           0.377  |            0.377  |                         0 |             0      |                   0 |         639    |
| PPG_Ear    | all      | 1406 |                          0.6984 |           0.4068 |            0.4011 |                         8 |             0.0299 |                   0 |         796.25 |
| PPG_Finger | 0-60     |  193 |                          0.9326 |           0.1347 |            0.1347 |                         0 |             0.3264 |                   0 |        1116    |
| PPG_Finger | 60-70    |  307 |                          0.8893 |           0.0945 |            0.0912 |                         1 |             0.0847 |                   0 |         904    |
| PPG_Finger | 70-80    |  559 |                          0.8784 |           0.0429 |            0.0394 |                         2 |             0.034  |                   0 |         797.5  |
| PPG_Finger | 80-90    |  384 |                          0.8203 |           0.0651 |            0.0625 |                         1 |             0.0026 |                   0 |         712.75 |
| PPG_Finger | >90      |  188 |                          0.6383 |           0.0106 |            0.0106 |                         0 |             0      |                   0 |         635.5  |
| PPG_Finger | all      | 1631 |                          0.8455 |           0.065  |            0.0625 |                         4 |             0.0668 |                   0 |         795.5  |

## reference_hr_slopes

| fiducial                                |   slope_ms_per_bpm |       lo |       hi |   rmcorr |   n_rec | expected (Weissler)   |
|:----------------------------------------|-------------------:|---------:|---------:|---------:|--------:|:----------------------|
| PCG QS2                                 |            -1.3138 |  -1.4218 |  -1.2112 |  -0.6323 |     103 | -2.0 to -2.1          |
| PCG S1                                  |            -0.0851 |  -0.2421 |   0.08   |  -0.0504 |     101 | ~ -0.4 (PEP)          |
| PCG S1-S2                               |            -1.2544 |  -1.4186 |  -1.0867 |  -0.56   |     101 | -1.6 to -1.7 (LVET)   |
| CNAP ET                                 |            -0.02   |  -0.2741 |   0.2266 |  -0.0061 |     100 | -1.6 to -1.7 (LVET)   |
| CNAP foot                               |            -0.7443 |  -0.899  |  -0.5782 |  -0.3577 |     100 |                       |
| CNAP notch                              |            -0.7643 |  -1.0743 |  -0.4309 |  -0.2086 |     100 |                       |
| CNAP ET, minimum notches                |             0.3403 |   0.1466 |   0.5755 |   0.1278 |      93 |                       |
| within-record SD, S2 to CNAP notch (ms) |            36.7808 | nan      | nan      | nan      |     nan | nan                   |
| within-record SD, PCG QS2 (ms)          |            14.6525 | nan      | nan      | nan      |     nan | nan                   |
| S2 split-half noise SD (ms)             |             0.9335 | nan      | nan      | nan      |     nan | nan                   |
| share of QS2 on its search ceiling      |             0.0003 | nan      | nan      | nan      |     nan | nan                   |
| share of windows with HR > 120 bpm      |             0.0126 | nan      | nan      | nan      |     nan | nan                   |

## s1_cross_sensor

| pcg         | earbud      |   rmcorr |   n_rec |   n_win |
|:------------|:------------|---------:|--------:|--------:|
| pcg_S1_ms   | ebL_S1_ms   |   0.0856 |      67 |    1469 |
| pcg_QS2_ms  | ebL_QS2_ms  |   0.5492 |      67 |    1469 |
| pcg_S1S2_ms | ebL_S1S2_ms |   0.2876 |      67 |    1469 |
| pcg_S1_ms   | ebR_S1_ms   |   0.123  |      69 |    1587 |
| pcg_QS2_ms  | ebR_QS2_ms  |   0.6508 |      69 |    1587 |
| pcg_S1S2_ms | ebR_S1S2_ms |   0.3707 |      69 |    1587 |

## slope_bounds

| channel    | y      | x           |    ols |   reverse_bound |   rmcorr |
|:-----------|:-------|:------------|-------:|----------------:|---------:|
| PPG_Ear    | t_D_ms | pcg_QS2_ms  | 0.5549 |          2.2958 |   0.4916 |
| PPG_Ear    | S_D_ms | pcg_S1S2_ms | 0.3839 |          2.4586 |   0.3951 |
| PPG_Ear    | S_D_ms | pcg_QS2_ms  | 0.0771 |         15.9242 |   0.0696 |
| PPG_Finger | t_D_ms | pcg_QS2_ms  | 0.7802 |          2.4701 |   0.562  |
| PPG_Finger | S_D_ms | pcg_S1S2_ms | 0.3633 |          3.4718 |   0.3235 |
| PPG_Finger | S_D_ms | pcg_QS2_ms  | 0.1813 |          7.9326 |   0.1512 |

## rebound_vs_hr

| channel    | HR_bin                                |    n |   rebound_present |       lo |       hi |
|:-----------|:--------------------------------------|-----:|------------------:|---------:|---------:|
| PPG_Ear    | 0-70                                  | 1424 |            0.5962 | nan      | nan      |
| PPG_Ear    | 70-85                                 | 2295 |            0.5969 | nan      | nan      |
| PPG_Ear    | 85-100                                | 1100 |            0.67   | nan      | nan      |
| PPG_Ear    | 100-115                               |  277 |            0.3791 | nan      | nan      |
| PPG_Ear    | 115-250                               |   58 |            0.0862 | nan      | nan      |
| PPG_Ear    | within-record slope per bpm, all HR   | 5150 |           -0.0058 |  -0.0096 |  -0.0014 |
| PPG_Ear    | within-record slope per bpm, HR < 100 | 4811 |            0.0013 |  -0.0025 |   0.0046 |
| PPG_Finger | 0-70                                  | 1708 |            0.9245 | nan      | nan      |
| PPG_Finger | 70-85                                 | 2641 |            0.9712 | nan      | nan      |
| PPG_Finger | 85-100                                | 1278 |            0.9695 | nan      | nan      |
| PPG_Finger | 100-115                               |  314 |            0.9873 | nan      | nan      |
| PPG_Finger | 115-250                               |   81 |            0.8642 | nan      | nan      |
| PPG_Finger | within-record slope per bpm, all HR   | 6022 |           -0.0007 |  -0.0017 |   0.0004 |
| PPG_Finger | within-record slope per bpm, HR < 100 | 5620 |            0.0005 |   0      |   0.001  |

## cv_leakage

| test                                                      |   mean_AUROC |   sd_AUROC |   expected |
|:----------------------------------------------------------|-------------:|-----------:|-----------:|
| E1 finger M2 features, permuted HF labels (40 x 5x5-fold) |       0.4868 |     0.1247 |        0.5 |

## variance_sim

| quantity         |   estimated |    true |
|:-----------------|------------:|--------:|
| sd_within_window |     11.9951 | 12      |
| sd_day           |     15.3038 | 15      |
| sd_between_HC    |      9.5066 | 10      |
| sd_between_HF    |     17.7037 | 20      |
| R_session_HC     |      0.2693 |  0.2976 |

## sensitivity_summary

| variant            |   exp3_rho |   exp3_p_one_sided |   exp3_n |   E1_finger_M1 |   E1_finger_delta |   E1_ear_delta |   R_SD_ear |   R_SD_finger |   R_ECGS_ear |   power_SD_finger_HF |
|:-------------------|-----------:|-------------------:|---------:|---------------:|------------------:|---------------:|-----------:|--------------:|-------------:|---------------------:|
| primary            |    -0.2755 |             0.0913 |       26 |         0.9249 |           -0.0046 |        -0.1083 |     0.3141 |        0.3882 |       0.6854 |               0.2741 |
| post1200           |    -0.2695 |             0.0963 |       26 |         0.9246 |           -0.0046 |        -0.1086 |     0.3127 |        0.3919 |       0.6854 |               0.2793 |
| annotated          |    -0.2995 |             0.0825 |       24 |         0.9082 |            0.0044 |        -0.0936 |     0.2755 |        0.3764 |       0.7776 |               0.2575 |
| post1200_annotated |    -0.2919 |             0.0883 |       24 |         0.9104 |            0.0019 |        -0.0929 |     0.2739 |        0.3801 |       0.7776 |               0.2623 |
| steady             |    -0.2988 |             0.083  |       24 |       nan      |          nan      |       nan      |     0.4013 |        0.3878 |       0.8101 |               0.2457 |

