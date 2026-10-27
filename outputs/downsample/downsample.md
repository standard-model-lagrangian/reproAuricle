# PWTA features at 125 Hz vs native 1 kHz

## yield

| variant   | channel    | cohort   |   windows |   s_clean_native |   s_clean_variant |   ok_native |   ok_variant |   ok_kept |   ok_gained |   s_clean_kept |
|:----------|:-----------|:---------|----------:|-----------------:|------------------:|------------:|-------------:|----------:|------------:|---------------:|
| 125       | PPG_Ear    | HC       |      1346 |            0.842 |             0.842 |       0.508 |        0.484 |     0.933 |       0.021 |          0.996 |
| 125       | PPG_Ear    | HFC      |       467 |            0.582 |             0.587 |       0.221 |        0.221 |     0.961 |       0.011 |          0.985 |
| 125       | PPG_Finger | HC       |      1346 |            0.913 |             0.911 |       0.854 |        0.848 |     0.976 |       0.107 |          0.993 |
| 125       | PPG_Finger | HFC      |       467 |            0.874 |             0.859 |       0.582 |        0.563 |     0.941 |       0.036 |          0.978 |
| 125up     | PPG_Ear    | HC       |      1347 |            0.842 |             0.843 |       0.509 |        0.488 |     0.945 |       0.017 |          1     |
| 125up     | PPG_Ear    | HFC      |       467 |            0.582 |             0.574 |       0.221 |        0.212 |     0.932 |       0.008 |          0.982 |
| 125up     | PPG_Finger | HC       |      1347 |            0.913 |             0.913 |       0.854 |        0.846 |     0.989 |       0.01  |          1     |
| 125up     | PPG_Finger | HFC      |       467 |            0.874 |             0.872 |       0.582 |        0.576 |     0.985 |       0.005 |          0.998 |

## fidelity

| variant   | channel    | feature       | tier    |   windows_both |   bias |   median_abs_diff |   p95_abs_diff |   native_within_session_sd |   p95_abs_diff_over_within_sd |   records |   record_spearman |
|:----------|:-----------|:--------------|:--------|---------------:|-------:|------------------:|---------------:|---------------------------:|------------------------------:|----------:|------------------:|
| 125       | PPG_Ear    | HR            | s_clean |           1396 |  0     |             0.178 |          0.583 |                      3.86  |                         0.151 |        87 |             0.999 |
| 125       | PPG_Ear    | ECG_S_ms      | s_clean |           1396 |  0.318 |             0.466 |          1.587 |                      8.97  |                         0.177 |        87 |             0.999 |
| 125       | PPG_Ear    | nSWI          | s_clean |           1396 | -0.002 |             0.006 |          0.067 |                      0.277 |                         0.24  |        87 |             0.999 |
| 125       | PPG_Ear    | reb_rise_frac | s_clean |           1396 | -0     |             0.001 |          0.018 |                      0.034 |                         0.522 |        87 |             0.98  |
| 125       | PPG_Ear    | PAT_foot_ms   | s_clean |           1396 |  0.182 |             1.896 |          4.2   |                      7.648 |                         0.549 |        87 |             0.998 |
| 125       | PPG_Ear    | CT_ms         | s_clean |           1396 | -0.14  |             2.46  |          6.718 |                      8.333 |                         0.806 |        87 |             0.995 |
| 125       | PPG_Ear    | PW50_frac     | s_clean |           1345 |  0     |             0.003 |          0.009 |                      0.02  |                         0.456 |        87 |             0.996 |
| 125       | PPG_Ear    | b_over_a      | s_clean |           1396 | -0.003 |             0.005 |          0.026 |                      0.047 |                         0.561 |        87 |             0.996 |
| 125       | PPG_Ear    | t_D_ms        | ok      |            737 |  0.251 |             0.417 |          1.619 |                      6.938 |                         0.233 |        63 |             0.995 |
| 125       | PPG_Ear    | S_D_ms        | ok      |            737 | -0.029 |             0.257 |          1.266 |                      6.151 |                         0.206 |        63 |             0.977 |
| 125       | PPG_Ear    | SWS           | ok      |            737 |  0.001 |             0.003 |          0.012 |                      0.075 |                         0.167 |        63 |             0.989 |
| 125       | PPG_Ear    | nDWI          | ok      |            737 |  0.002 |             0.004 |          0.038 |                      0.28  |                         0.136 |        63 |             0.987 |
| 125       | PPG_Ear    | DWI_over_SWI  | ok      |            737 |  0     |             0     |          0.003 |                      0.024 |                         0.146 |        63 |             0.992 |
| 125       | PPG_Ear    | D_sharpness   | ok      |            737 |  0.01  |             0.081 |          0.648 |                      1.957 |                         0.331 |        63 |             0.951 |
| 125       | PPG_Finger | HR            | s_clean |           1620 |  0     |             0.187 |          0.583 |                      3.599 |                         0.162 |       102 |             1     |
| 125       | PPG_Finger | ECG_S_ms      | s_clean |           1620 |  0.312 |             0.42  |          1.298 |                      9.038 |                         0.144 |       102 |             0.977 |
| 125       | PPG_Finger | nSWI          | s_clean |           1620 | -0.031 |             0.033 |          0.102 |                      0.607 |                         0.168 |       102 |             0.999 |
| 125       | PPG_Finger | reb_rise_frac | s_clean |           1620 | -0     |             0.001 |          0.008 |                      0.042 |                         0.185 |       102 |             0.988 |
| 125       | PPG_Finger | PAT_foot_ms   | s_clean |           1620 |  0.227 |             1.929 |          4.104 |                      8.488 |                         0.483 |       102 |             0.975 |
| 125       | PPG_Finger | CT_ms         | s_clean |           1620 |  0.102 |             2.368 |          6.211 |                      7.743 |                         0.802 |       102 |             0.997 |
| 125       | PPG_Finger | PW50_frac     | s_clean |           1492 | -0     |             0.003 |          0.01  |                      0.025 |                         0.377 |       102 |             0.997 |
| 125       | PPG_Finger | b_over_a      | s_clean |           1620 | -0.008 |             0.009 |          0.023 |                      0.049 |                         0.457 |       102 |             0.998 |
| 125       | PPG_Finger | t_D_ms        | ok      |           1377 | -0.02  |             0.482 |          1.871 |                     10.897 |                         0.172 |        98 |             0.992 |
| 125       | PPG_Finger | S_D_ms        | ok      |           1377 | -0.328 |             0.409 |          1.709 |                      8.673 |                         0.197 |        98 |             0.998 |
| 125       | PPG_Finger | SWS           | ok      |           1377 |  0.004 |             0.005 |          0.016 |                      0.092 |                         0.171 |        98 |             0.991 |
| 125       | PPG_Finger | nDWI          | ok      |           1377 |  0.004 |             0.009 |          0.053 |                      0.383 |                         0.139 |        98 |             0.999 |
| 125       | PPG_Finger | DWI_over_SWI  | ok      |           1377 | -0     |             0.001 |          0.004 |                      0.028 |                         0.142 |        98 |             0.999 |
| 125       | PPG_Finger | D_sharpness   | ok      |           1377 | -0.007 |             0.044 |          1.627 |                      1.634 |                         0.996 |        98 |             0.994 |
| 125up     | PPG_Ear    | HR            | s_clean |           1401 |  0     |             0     |          0.05  |                      3.86  |                         0.013 |        87 |             1     |
| 125up     | PPG_Ear    | ECG_S_ms      | s_clean |           1401 | -0.001 |             0.105 |          1.185 |                      8.97  |                         0.132 |        87 |             1     |
| 125up     | PPG_Ear    | nSWI          | s_clean |           1401 |  0.005 |             0.005 |          0.017 |                      0.277 |                         0.061 |        87 |             1     |
| 125up     | PPG_Ear    | reb_rise_frac | s_clean |           1401 |  0     |             0     |          0.021 |                      0.034 |                         0.615 |        87 |             0.977 |
| 125up     | PPG_Ear    | PAT_foot_ms   | s_clean |           1401 |  0.048 |             0.127 |          0.813 |                      7.648 |                         0.106 |        87 |             1     |
| 125up     | PPG_Ear    | CT_ms         | s_clean |           1401 | -0.056 |             0.95  |          3.231 |                      8.333 |                         0.388 |        87 |             0.999 |
| 125up     | PPG_Ear    | PW50_frac     | s_clean |           1359 |  0     |             0     |          0.001 |                      0.02  |                         0.067 |        87 |             1     |
| 125up     | PPG_Ear    | b_over_a      | s_clean |           1401 |  0     |             0     |          0.006 |                      0.047 |                         0.13  |        87 |             0.999 |
| 125up     | PPG_Ear    | t_D_ms        | ok      |            743 | -0.049 |             0.218 |          1.727 |                      6.938 |                         0.249 |        62 |             0.982 |
| 125up     | PPG_Ear    | S_D_ms        | ok      |            743 | -0.058 |             0.233 |          2.024 |                      6.151 |                         0.329 |        62 |             0.899 |
| 125up     | PPG_Ear    | SWS           | ok      |            743 |  0     |             0.001 |          0.013 |                      0.075 |                         0.175 |        62 |             0.963 |
| 125up     | PPG_Ear    | nDWI          | ok      |            743 | -0.001 |             0.002 |          0.015 |                      0.28  |                         0.055 |        62 |             0.994 |
| 125up     | PPG_Ear    | DWI_over_SWI  | ok      |            743 |  0     |             0     |          0.001 |                      0.024 |                         0.063 |        62 |             0.994 |
| 125up     | PPG_Ear    | D_sharpness   | ok      |            743 | -0.002 |             0.01  |          0.091 |                      1.957 |                         0.046 |        62 |             0.979 |
| 125up     | PPG_Finger | HR            | s_clean |           1637 |  0     |             0     |          0.042 |                      3.599 |                         0.012 |       102 |             1     |
| 125up     | PPG_Finger | ECG_S_ms      | s_clean |           1637 |  0.008 |             0.029 |          0.164 |                      9.038 |                         0.018 |       102 |             1     |
| 125up     | PPG_Finger | nSWI          | s_clean |           1637 |  0.005 |             0.005 |          0.015 |                      0.607 |                         0.024 |       102 |             1     |
| 125up     | PPG_Finger | reb_rise_frac | s_clean |           1637 |  0     |             0     |          0.001 |                      0.042 |                         0.015 |       102 |             0.998 |
| 125up     | PPG_Finger | PAT_foot_ms   | s_clean |           1637 |  0.041 |             0.061 |          0.555 |                      8.488 |                         0.065 |       102 |             1     |
| 125up     | PPG_Finger | CT_ms         | s_clean |           1637 | -0.047 |             0.143 |          2.056 |                      7.743 |                         0.266 |       102 |             0.999 |
| 125up     | PPG_Finger | PW50_frac     | s_clean |           1526 |  0     |             0     |          0.001 |                      0.025 |                         0.057 |       102 |             1     |
| 125up     | PPG_Finger | b_over_a      | s_clean |           1637 | -0     |             0     |          0.001 |                      0.049 |                         0.015 |       102 |             0.999 |
| 125up     | PPG_Finger | t_D_ms        | ok      |           1405 | -0.006 |             0.092 |          0.706 |                     10.897 |                         0.065 |        98 |             0.996 |
| 125up     | PPG_Finger | S_D_ms        | ok      |           1405 | -0.015 |             0.09  |          0.714 |                      8.673 |                         0.082 |        98 |             0.998 |
| 125up     | PPG_Finger | SWS           | ok      |           1405 |  0     |             0.001 |          0.005 |                      0.092 |                         0.056 |        98 |             1     |
| 125up     | PPG_Finger | nDWI          | ok      |           1405 | -0.001 |             0.001 |          0.006 |                      0.383 |                         0.015 |        98 |             0.999 |
| 125up     | PPG_Finger | DWI_over_SWI  | ok      |           1405 |  0     |             0     |          0     |                      0.028 |                         0.014 |        98 |             1     |
| 125up     | PPG_Finger | D_sharpness   | ok      |           1405 | -0.005 |             0.007 |          0.114 |                      1.634 |                         0.07  |        98 |             0.996 |

## precision

| variant   | channel    | feature   |   split_half_median_abs |   windows |
|:----------|:-----------|:----------|------------------------:|----------:|
| native    | PPG_Ear    | ECG_S_ms  |                   0.545 |      1406 |
| native    | PPG_Ear    | S_D_ms    |                   1.013 |       788 |
| native    | PPG_Ear    | SWS       |                   0.006 |       788 |
| native    | PPG_Finger | ECG_S_ms  |                   0.416 |      1638 |
| native    | PPG_Finger | S_D_ms    |                   0.997 |      1422 |
| native    | PPG_Finger | SWS       |                   0.007 |      1422 |
| 125       | PPG_Ear    | ECG_S_ms  |                   0.715 |      1408 |
| 125       | PPG_Ear    | S_D_ms    |                   0.834 |       756 |
| 125       | PPG_Ear    | SWS       |                   0.006 |       756 |
| 125       | PPG_Finger | ECG_S_ms  |                   0.69  |      1628 |
| 125       | PPG_Finger | S_D_ms    |                   0.995 |      1406 |
| 125       | PPG_Finger | SWS       |                   0.007 |      1406 |
| 125up     | PPG_Ear    | ECG_S_ms  |                   0.508 |      1404 |
| 125up     | PPG_Ear    | S_D_ms    |                   0.922 |       757 |
| 125up     | PPG_Ear    | SWS       |                   0.006 |       757 |
| 125up     | PPG_Finger | ECG_S_ms  |                   0.422 |      1637 |
| 125up     | PPG_Finger | S_D_ms    |                   1.017 |      1408 |
| 125up     | PPG_Finger | SWS       |                   0.007 |      1408 |

## reliability

| channel    | feature       |   125 |   125up |   native |
|:-----------|:--------------|------:|--------:|---------:|
| PPG_Ear    | CT_ms         | 0.525 |   0.519 |    0.514 |
| PPG_Ear    | DWI_over_SWI  | 0.747 |   0.739 |    0.746 |
| PPG_Ear    | D_sharpness   | 0.193 |   0.034 |    0.077 |
| PPG_Ear    | ECG_S_ms      | 0.592 |   0.593 |    0.591 |
| PPG_Ear    | HR            | 0.643 |   0.65  |    0.654 |
| PPG_Ear    | PAT_foot_ms   | 0.541 |   0.531 |    0.532 |
| PPG_Ear    | PW50_frac     | 0.56  |   0.538 |    0.54  |
| PPG_Ear    | SWS           | 0.723 |   0.809 |    0.797 |
| PPG_Ear    | S_D_ms        | 0.09  |   0.601 |    0.341 |
| PPG_Ear    | b_over_a      | 0.64  |   0.663 |    0.663 |
| PPG_Ear    | nDWI          | 0.522 |   0.514 |    0.515 |
| PPG_Ear    | nSWI          | 0.598 |   0.608 |    0.608 |
| PPG_Ear    | reb_rise_frac | 0.701 |   0.707 |    0.716 |
| PPG_Ear    | t_D_ms        | 0.389 |   0.726 |    0.591 |
| PPG_Finger | CT_ms         | 0.573 |   0.54  |    0.55  |
| PPG_Finger | DWI_over_SWI  | 0.817 |   0.814 |    0.819 |
| PPG_Finger | D_sharpness   | 0.537 |   0.47  |    0.457 |
| PPG_Finger | ECG_S_ms      | 0.504 |   0.688 |    0.689 |
| PPG_Finger | HR            | 0.617 |   0.619 |    0.619 |
| PPG_Finger | PAT_foot_ms   | 0.55  |   0.735 |    0.735 |
| PPG_Finger | PW50_frac     | 0.705 |   0.716 |    0.719 |
| PPG_Finger | SWS           | 0.561 |   0.545 |    0.555 |
| PPG_Finger | S_D_ms        | 0.369 |   0.347 |    0.355 |
| PPG_Finger | b_over_a      | 0.617 |   0.603 |    0.602 |
| PPG_Finger | nDWI          | 0.739 |   0.725 |    0.736 |
| PPG_Finger | nSWI          | 0.613 |   0.595 |    0.6   |
| PPG_Finger | reb_rise_frac | 0.767 |   0.775 |    0.775 |
| PPG_Finger | t_D_ms        | 0.226 |   0.244 |    0.256 |

## reliability_matched

| channel    | feature       |   n_subjects |   125 |   125up |   native |
|:-----------|:--------------|-------------:|------:|--------:|---------:|
| PPG_Ear    | CT_ms         |           29 | 0.525 |   0.521 |    0.515 |
| PPG_Ear    | DWI_over_SWI  |           21 | 0.814 |   0.812 |    0.814 |
| PPG_Ear    | D_sharpness   |           21 | 0.188 |   0.122 |    0.122 |
| PPG_Ear    | ECG_S_ms      |           29 | 0.591 |   0.588 |    0.586 |
| PPG_Ear    | HR            |           29 | 0.647 |   0.652 |    0.653 |
| PPG_Ear    | PAT_foot_ms   |           29 | 0.541 |   0.528 |    0.531 |
| PPG_Ear    | PW50_frac     |           29 | 0.559 |   0.562 |    0.564 |
| PPG_Ear    | SWS           |           21 | 0.813 |   0.813 |    0.814 |
| PPG_Ear    | S_D_ms        |           21 | 0.603 |   0.599 |    0.614 |
| PPG_Ear    | b_over_a      |           29 | 0.64  |   0.633 |    0.632 |
| PPG_Ear    | nDWI          |           21 | 0.503 |   0.506 |    0.505 |
| PPG_Ear    | nSWI          |           29 | 0.598 |   0.603 |    0.602 |
| PPG_Ear    | reb_rise_frac |           29 | 0.705 |   0.712 |    0.715 |
| PPG_Ear    | t_D_ms        |           21 | 0.758 |   0.755 |    0.755 |
| PPG_Finger | CT_ms         |           33 | 0.571 |   0.541 |    0.553 |
| PPG_Finger | DWI_over_SWI  |           33 | 0.81  |   0.81  |    0.811 |
| PPG_Finger | D_sharpness   |           33 | 0.54  |   0.524 |    0.52  |
| PPG_Finger | ECG_S_ms      |           33 | 0.692 |   0.682 |    0.683 |
| PPG_Finger | HR            |           33 | 0.612 |   0.612 |    0.611 |
| PPG_Finger | PAT_foot_ms   |           33 | 0.725 |   0.731 |    0.73  |
| PPG_Finger | PW50_frac     |           33 | 0.705 |   0.709 |    0.712 |
| PPG_Finger | SWS           |           33 | 0.564 |   0.547 |    0.554 |
| PPG_Finger | S_D_ms        |           33 | 0.36  |   0.343 |    0.348 |
| PPG_Finger | b_over_a      |           33 | 0.607 |   0.597 |    0.596 |
| PPG_Finger | nDWI          |           33 | 0.724 |   0.723 |    0.723 |
| PPG_Finger | nSWI          |           33 | 0.607 |   0.6   |    0.605 |
| PPG_Finger | reb_rise_frac |           33 | 0.766 |   0.776 |    0.775 |
| PPG_Finger | t_D_ms        |           33 | 0.262 |   0.246 |    0.248 |
