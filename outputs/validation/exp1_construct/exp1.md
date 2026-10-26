# Experiment 1 [all_20s]

Reference gate: {'R1': True, 'R2': False, 'R3': True, 'R4': False} -> FAIL

- ear: HR-partialled **inconclusive** (beta_D 0.45 [0.19, 0.62], beta_reb 0.31 [-0.10, 0.57], D-reb 0.08 [-0.04, 0.25]); raw: inconclusive (beta_D 0.55 [0.39, 0.70], beta_reb 0.24 [-0.02, 0.47], D-reb 0.23 [0.09, 0.40])
- finger: HR-partialled **inconclusive** (beta_D 0.71 [0.51, 0.84], beta_reb 0.61 [0.42, 0.75], D-reb 0.09 [0.01, 0.18]); raw: inconclusive (beta_D 0.78 [0.68, 0.87], beta_reb 0.60 [0.50, 0.70], D-reb 0.16 [0.09, 0.23])

## reference_validity

| check                                              |   value | detail                                                         |
|:---------------------------------------------------|--------:|:---------------------------------------------------------------|
| R1 PCG S2 QC yield (windows)                       |   0.817 | 102 records with >= 50% ok of 107                              |
| R2 earbud S2 vs PCG S2, within-record beta         |   0.67  | CI 0.55-0.77; rmcorr 0.70; 91 rec / 3113 win; median lag 22 ms |
| R3 QS2 - (Weissler QS2 - 35), session median [HC]  |  -7.822 | IQR -19 to 3 ms, n=76                                          |
| R3 CNAP ET - Weissler LVET, session median [HC]    | -24.531 | IQR -39 to -13 ms, n=75                                        |
| R3 QS2 - (Weissler QS2 - 35), session median [HFC] |  14.15  | IQR -9 to 27 ms, n=27                                          |
| R3 CNAP ET - Weissler LVET, session median [HFC]   | -45.053 | IQR -73 to -34 ms, n=26                                        |
| R4 CNAP ET on PCG QS2, within-record beta          |   0.075 | CI -0.05-0.21; rmcorr 0.04; 99 rec                             |


## tracking

| site   | x          | y                    | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |     r |   r_lo |   r_hi |
|:-------|:-----------|:---------------------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|------:|-------:|-------:|
| ear    | pcg_QS2_ms | t_D_ms               | -         |      67 |       44 |    2512 |  0.555 |     0.389 |     0.696 | 0.492 |  0.334 |  0.646 |
| ear    | pcg_QS2_ms | t_D_ms               | HR_ref    |      67 |       44 |    2512 |  0.453 |     0.187 |     0.616 | 0.383 |  0.133 |  0.598 |
| ear    | pcg_QS2_ms | t_reb_ms             | -         |      70 |       46 |    2754 |  0.243 |    -0.016 |     0.466 | 0.129 | -0.008 |  0.28  |
| ear    | pcg_QS2_ms | t_reb_ms             | HR_ref    |      70 |       46 |    2754 |  0.306 |    -0.096 |     0.573 | 0.139 | -0.035 |  0.318 |
| ear    | pcg_QS2_ms | ECG_S_ms             | -         |      87 |       58 |    4561 |  0.562 |     0.432 |     0.673 | 0.608 |  0.492 |  0.699 |
| ear    | pcg_QS2_ms | ECG_S_ms             | HR_ref    |      87 |       58 |    4561 |  0.576 |     0.356 |     0.724 | 0.518 |  0.322 |  0.664 |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | -         |      67 |       44 |    2512 |  0.322 |     0.064 |     0.534 | 0.226 |  0.042 |  0.413 |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |      67 |       44 |    2512 |  0.374 |    -0     |     0.613 | 0.227 | -0     |  0.444 |
| finger | pcg_QS2_ms | t_D_ms               | -         |     101 |       68 |    4487 |  0.78  |     0.676 |     0.87  | 0.562 |  0.445 |  0.674 |
| finger | pcg_QS2_ms | t_D_ms               | HR_ref    |     101 |       68 |    4487 |  0.709 |     0.505 |     0.84  | 0.416 |  0.259 |  0.561 |
| finger | pcg_QS2_ms | t_reb_ms             | -         |     102 |       69 |    5089 |  0.603 |     0.5   |     0.696 | 0.43  |  0.314 |  0.555 |
| finger | pcg_QS2_ms | t_reb_ms             | HR_ref    |     102 |       69 |    5089 |  0.611 |     0.417 |     0.748 | 0.334 |  0.189 |  0.482 |
| finger | pcg_QS2_ms | ECG_S_ms             | -         |     102 |       69 |    5259 |  0.58  |     0.456 |     0.692 | 0.617 |  0.505 |  0.703 |
| finger | pcg_QS2_ms | ECG_S_ms             | HR_ref    |     102 |       69 |    5259 |  0.568 |     0.33  |     0.736 | 0.509 |  0.295 |  0.659 |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | -         |     101 |       68 |    4487 |  0.624 |     0.507 |     0.716 | 0.511 |  0.384 |  0.63  |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |     101 |       68 |    4487 |  0.623 |     0.413 |     0.756 | 0.411 |  0.24  |  0.565 |


## tracking_diff

| site   | partial   |   diff |   diff_lo |   diff_hi |   n_rec |
|:-------|:----------|-------:|----------:|----------:|--------:|
| ear    | -         |  0.233 |     0.092 |     0.403 |      67 |
| ear    | HR_ref    |  0.079 |    -0.036 |     0.252 |      67 |
| finger | -         |  0.156 |     0.09  |     0.235 |     101 |
| finger | HR_ref    |  0.087 |     0.011 |     0.182 |     101 |


## interval

| site   | x           | y      | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |     r |   r_lo |   r_hi |
|:-------|:------------|:-------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|------:|-------:|-------:|
| ear    | cnap_ET_ms  | S_D_ms | -         |      65 |       42 |    2318 |  0.124 |     0.048 |     0.242 | 0.168 |  0.066 |  0.308 |
| ear    | pcg_S1S2_ms | S_D_ms | -         |      66 |       43 |    2437 |  0.384 |     0.264 |     0.502 | 0.395 |  0.269 |  0.521 |
| ear    | RR_ms       | S_D_ms | -         |      67 |       44 |    2512 |  0.067 |     0.039 |     0.099 | 0.268 |  0.157 |  0.371 |
| finger | cnap_ET_ms  | S_D_ms | -         |      98 |       67 |    3826 |  0.064 |     0.016 |     0.131 | 0.085 |  0.023 |  0.161 |
| finger | pcg_S1S2_ms | S_D_ms | -         |      97 |       64 |    4303 |  0.363 |     0.284 |     0.448 | 0.324 |  0.246 |  0.411 |
| finger | RR_ms       | S_D_ms | -         |     101 |       68 |    4487 |  0.045 |     0.025 |     0.065 | 0.168 |  0.093 |  0.241 |


## interval_between

| site   | pair                             |   rho |     p |   n_sessions |
|:-------|:---------------------------------|------:|------:|-------------:|
| ear    | S-D vs CNAP ET (session medians) | 0.279 | 0.015 |           76 |
| finger | S-D vs CNAP ET (session medians) | 0.359 | 0     |           99 |


## lags

| site       | quantity    |   median |      q25 |     q75 |   n_sessions |
|:-----------|:------------|---------:|---------:|--------:|-------------:|
| ear        | S_lag       |  -73.685 | -101.787 | -45.174 |           89 |
| ear        | D_lag       |  131.861 |   93.134 | 149.968 |           78 |
| ear        | reb_lag     |  231.823 |  205.573 | 258.526 |           82 |
| ear        | reb_minus_D |   95.005 |   79.753 | 107.957 |           78 |
| ear        | S2_to_notch |  173.5   |  147.5   | 191     |          101 |
| finger     | S_lag       |  -69.28  |  -89.892 | -53.243 |          102 |
| finger     | D_lag       |  128.505 |  116.378 | 139.289 |          102 |
| finger     | reb_lag     |  226.056 |  210.57  | 237.352 |          102 |
| finger     | reb_minus_D |   94.232 |   83.812 | 109.877 |          102 |
| finger     | S2_to_notch |  173.5   |  147.5   | 191     |          101 |
| finger-ear | ECG_S_ms    |    2.951 |  -12.328 |  23.125 |           89 |
| finger-ear | t_D_ms      |    5.543 |  -14.553 |  43.474 |           77 |
| finger-ear | t_reb_ms    |   -0.733 |  -22.633 |  73.381 |           80 |


## posthoc_intervals

| site   | x           | y                                     | partial   |   n_rec |   n_subj |   n_win |    beta |   beta_lo |   beta_hi |       r |    r_lo |    r_hi |    diff |   diff_lo |   diff_hi |
|:-------|:------------|:--------------------------------------|:----------|--------:|---------:|--------:|--------:|----------:|----------:|--------:|--------:|--------:|--------:|----------:|----------:|
| ear    | pcg_QS2_ms  | S_D_ms                                | -         |      67 |       44 |    2512 |   0.077 |    -0.042 |     0.245 |   0.07  |  -0.045 |   0.195 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_D_ms                                | -         |      66 |       43 |    2437 |   0.384 |     0.264 |     0.502 |   0.395 |   0.269 |   0.521 | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | S_reb_ms                              | -         |      70 |       46 |    2754 |  -0.234 |    -0.406 |    -0.074 |  -0.118 |  -0.195 |  -0.038 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_reb_ms                              | -         |      69 |       45 |    2672 |   0.12  |    -0.064 |     0.28  |   0.07  |  -0.037 |   0.173 | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |      67 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.077 |    -0.042 |     0.245 |
| finger | pcg_QS2_ms  | S_D_ms                                | -         |     101 |       68 |    4487 |   0.181 |     0.094 |     0.294 |   0.151 |   0.085 |   0.23  | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_D_ms                                | -         |      97 |       64 |    4303 |   0.363 |     0.284 |     0.448 |   0.324 |   0.246 |   0.411 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | S_reb_ms                              | -         |     102 |       69 |    5089 |   0.024 |    -0.035 |     0.09  |   0.02  |  -0.03  |   0.069 | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_reb_ms                              | -         |      98 |       65 |    4879 |   0.168 |     0.095 |     0.243 |   0.154 |   0.086 |   0.234 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |     101 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.181 |     0.094 |     0.294 |


# Experiment 1 [rest_only_20s]

Reference gate: {'R1': True, 'R2': True, 'R3': True, 'R4': False} -> FAIL

- ear: HR-partialled **inconclusive** (beta_D 0.42 [0.26, 0.64], beta_reb -0.03 [-0.24, 0.17], D-reb 0.34 [0.16, 0.55]); raw: inconclusive (beta_D 0.62 [0.49, 0.75], beta_reb 0.02 [-0.24, 0.26], D-reb 0.47 [0.32, 0.65])
- finger: HR-partialled **inconclusive** (beta_D 0.73 [0.51, 0.90], beta_reb 0.54 [0.30, 0.74], D-reb 0.15 [0.06, 0.30]); raw: inconclusive (beta_D 0.85 [0.75, 0.94], beta_reb 0.63 [0.51, 0.74], D-reb 0.19 [0.12, 0.28])

## reference_validity

| check                                              |   value | detail                                                         |
|:---------------------------------------------------|--------:|:---------------------------------------------------------------|
| R1 PCG S2 QC yield (windows)                       |   0.867 | 96 records with >= 50% ok of 100                               |
| R2 earbud S2 vs PCG S2, within-record beta         |   0.841 | CI 0.70-0.97; rmcorr 0.75; 86 rec / 2274 win; median lag 22 ms |
| R3 QS2 - (Weissler QS2 - 35), session median [HC]  |  -9.766 | IQR -22 to 1 ms, n=73                                          |
| R3 CNAP ET - Weissler LVET, session median [HC]    | -24.218 | IQR -39 to -9 ms, n=73                                         |
| R3 QS2 - (Weissler QS2 - 35), session median [HFC] |  12.939 | IQR -14 to 29 ms, n=24                                         |
| R3 CNAP ET - Weissler LVET, session median [HFC]   | -46.129 | IQR -73 to -36 ms, n=23                                        |
| R4 CNAP ET on PCG QS2, within-record beta          |   0.062 | CI -0.09-0.25; rmcorr 0.03; 95 rec                             |


## tracking

| site   | x          | y                    | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |      r |   r_lo |   r_hi |
|:-------|:-----------|:---------------------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|-------:|-------:|-------:|
| ear    | pcg_QS2_ms | t_D_ms               | -         |      57 |       37 |    1727 |  0.618 |     0.487 |     0.751 |  0.546 |  0.412 |  0.708 |
| ear    | pcg_QS2_ms | t_D_ms               | HR_ref    |      57 |       37 |    1727 |  0.423 |     0.262 |     0.641 |  0.33  |  0.209 |  0.517 |
| ear    | pcg_QS2_ms | t_reb_ms             | -         |      60 |       40 |    1871 |  0.019 |    -0.241 |     0.258 |  0.008 | -0.108 |  0.115 |
| ear    | pcg_QS2_ms | t_reb_ms             | HR_ref    |      60 |       40 |    1871 | -0.029 |    -0.24  |     0.175 | -0.009 | -0.08  |  0.057 |
| ear    | pcg_QS2_ms | ECG_S_ms             | -         |      82 |       55 |    3216 |  0.62  |     0.513 |     0.718 |  0.649 |  0.547 |  0.724 |
| ear    | pcg_QS2_ms | ECG_S_ms             | HR_ref    |      82 |       55 |    3216 |  0.632 |     0.427 |     0.794 |  0.51  |  0.34  |  0.66  |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | -         |      57 |       37 |    1727 |  0.144 |    -0.081 |     0.365 |  0.085 | -0.045 |  0.238 |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |      57 |       37 |    1727 |  0.088 |    -0.121 |     0.356 |  0.04  | -0.055 |  0.17  |
| finger | pcg_QS2_ms | t_D_ms               | -         |      94 |       63 |    3239 |  0.852 |     0.748 |     0.937 |  0.601 |  0.492 |  0.708 |
| finger | pcg_QS2_ms | t_D_ms               | HR_ref    |      94 |       63 |    3239 |  0.729 |     0.513 |     0.896 |  0.4   |  0.261 |  0.555 |
| finger | pcg_QS2_ms | t_reb_ms             | -         |      95 |       64 |    3594 |  0.634 |     0.515 |     0.736 |  0.411 |  0.291 |  0.562 |
| finger | pcg_QS2_ms | t_reb_ms             | HR_ref    |      95 |       64 |    3594 |  0.544 |     0.303 |     0.739 |  0.247 |  0.122 |  0.411 |
| finger | pcg_QS2_ms | ECG_S_ms             | -         |      97 |       66 |    3755 |  0.604 |     0.476 |     0.714 |  0.652 |  0.542 |  0.733 |
| finger | pcg_QS2_ms | ECG_S_ms             | HR_ref    |      97 |       66 |    3755 |  0.611 |     0.372 |     0.785 |  0.521 |  0.326 |  0.675 |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | -         |      94 |       63 |    3239 |  0.659 |     0.532 |     0.763 |  0.515 |  0.388 |  0.649 |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |      94 |       63 |    3239 |  0.577 |     0.339 |     0.752 |  0.345 |  0.179 |  0.536 |


## tracking_diff

| site   | partial   |   diff |   diff_lo |   diff_hi |   n_rec |
|:-------|:----------|-------:|----------:|----------:|--------:|
| ear    | -         |  0.474 |     0.325 |     0.653 |      57 |
| ear    | HR_ref    |  0.335 |     0.159 |     0.549 |      57 |
| finger | -         |  0.193 |     0.124 |     0.28  |      94 |
| finger | HR_ref    |  0.152 |     0.061 |     0.296 |      94 |


## interval

| site   | x           | y      | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |     r |   r_lo |   r_hi |
|:-------|:------------|:-------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|------:|-------:|-------:|
| ear    | cnap_ET_ms  | S_D_ms | -         |      55 |       36 |    1620 |  0.05  |     0.006 |     0.133 | 0.101 |  0.013 |  0.245 |
| ear    | pcg_S1S2_ms | S_D_ms | -         |      56 |       36 |    1681 |  0.176 |     0.082 |     0.321 | 0.2   |  0.11  |  0.321 |
| ear    | RR_ms       | S_D_ms | -         |      57 |       37 |    1727 |  0.049 |     0.038 |     0.061 | 0.24  |  0.168 |  0.357 |
| finger | cnap_ET_ms  | S_D_ms | -         |      91 |       62 |    2769 |  0.021 |    -0.015 |     0.07  | 0.033 | -0.027 |  0.1   |
| finger | pcg_S1S2_ms | S_D_ms | -         |      91 |       60 |    3113 |  0.292 |     0.218 |     0.366 | 0.255 |  0.188 |  0.329 |
| finger | RR_ms       | S_D_ms | -         |      94 |       63 |    3239 |  0.061 |     0.045 |     0.078 | 0.227 |  0.161 |  0.303 |


## interval_between

| site   | pair                             |   rho |     p |   n_sessions |
|:-------|:---------------------------------|------:|------:|-------------:|
| ear    | S-D vs CNAP ET (session medians) | 0.249 | 0.047 |           64 |
| finger | S-D vs CNAP ET (session medians) | 0.361 | 0     |           93 |


## lags

| site       | quantity    |   median |      q25 |     q75 |   n_sessions |
|:-----------|:------------|---------:|---------:|--------:|-------------:|
| ear        | S_lag       |  -74.7   | -100.447 | -48.191 |           84 |
| ear        | D_lag       |  134.789 |   86.516 | 151.191 |           67 |
| ear        | reb_lag     |  238.646 |  205.798 | 265.243 |           74 |
| ear        | reb_minus_D |   94.335 |   75.154 | 115.213 |           67 |
| ear        | S2_to_notch |  175.5   |  148.375 | 192.5   |           96 |
| finger     | S_lag       |  -69.57  |  -86.793 | -54.797 |           97 |
| finger     | D_lag       |  130.419 |  116.219 | 139.827 |           95 |
| finger     | reb_lag     |  225.376 |  210.964 | 237.64  |           95 |
| finger     | reb_minus_D |   93.058 |   84.12  | 109.387 |           95 |
| finger     | S2_to_notch |  175.5   |  148.375 | 192.5   |           96 |
| finger-ear | ECG_S_ms    |    1.898 |  -13.392 |  21.192 |           84 |
| finger-ear | t_D_ms      |    3.541 |  -15.734 |  41.713 |           64 |
| finger-ear | t_reb_ms    |   -4.058 |  -25.95  |  75.619 |           71 |


## posthoc_intervals

| site   | x           | y                                     | partial   |   n_rec |   n_subj |   n_win |    beta |   beta_lo |   beta_hi |       r |    r_lo |    r_hi |    diff |   diff_lo |   diff_hi |
|:-------|:------------|:--------------------------------------|:----------|--------:|---------:|--------:|--------:|----------:|----------:|--------:|--------:|--------:|--------:|----------:|----------:|
| ear    | pcg_QS2_ms  | S_D_ms                                | -         |      57 |       37 |    1727 |   0.127 |     0.044 |     0.217 |   0.122 |   0.045 |   0.219 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_D_ms                                | -         |      56 |       36 |    1681 |   0.176 |     0.082 |     0.321 |   0.2   |   0.11  |   0.321 | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | S_reb_ms                              | -         |      60 |       40 |    1871 |  -0.508 |    -0.759 |    -0.265 |  -0.212 |  -0.311 |  -0.111 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_reb_ms                              | -         |      59 |       39 |    1824 |  -0.259 |    -0.411 |    -0.092 |  -0.124 |  -0.209 |  -0.04  | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |      57 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.127 |     0.044 |     0.217 |
| finger | pcg_QS2_ms  | S_D_ms                                | -         |      94 |       63 |    3239 |   0.241 |     0.147 |     0.345 |   0.199 |   0.132 |   0.278 | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_D_ms                                | -         |      91 |       60 |    3113 |   0.292 |     0.218 |     0.366 |   0.255 |   0.188 |   0.329 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | S_reb_ms                              | -         |      95 |       64 |    3594 |   0.029 |    -0.041 |     0.101 |   0.021 |  -0.031 |   0.074 | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_reb_ms                              | -         |      92 |       61 |    3458 |   0.089 |     0.033 |     0.154 |   0.073 |   0.027 |   0.137 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |      94 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.241 |     0.147 |     0.345 |


# Experiment 1 [notch_minimum_only]

Reference gate: {'R1': True, 'R2': False, 'R3': True, 'R4': False} -> FAIL

- ear: HR-partialled **inconclusive** (beta_D 0.45 [0.19, 0.62], beta_reb 0.31 [-0.10, 0.57], D-reb 0.08 [-0.04, 0.25]); raw: inconclusive (beta_D 0.55 [0.39, 0.70], beta_reb 0.24 [-0.02, 0.47], D-reb 0.23 [0.09, 0.40])
- finger: HR-partialled **inconclusive** (beta_D 0.71 [0.51, 0.84], beta_reb 0.61 [0.42, 0.75], D-reb 0.09 [0.01, 0.18]); raw: inconclusive (beta_D 0.78 [0.68, 0.87], beta_reb 0.60 [0.50, 0.70], D-reb 0.16 [0.09, 0.23])

## reference_validity

| check                                              |   value | detail                                                         |
|:---------------------------------------------------|--------:|:---------------------------------------------------------------|
| R1 PCG S2 QC yield (windows)                       |   0.817 | 102 records with >= 50% ok of 107                              |
| R2 earbud S2 vs PCG S2, within-record beta         |   0.67  | CI 0.55-0.77; rmcorr 0.70; 91 rec / 3113 win; median lag 22 ms |
| R3 QS2 - (Weissler QS2 - 35), session median [HC]  |  -7.822 | IQR -19 to 3 ms, n=76                                          |
| R3 CNAP ET - Weissler LVET, session median [HC]    | -21.691 | IQR -31 to -9 ms, n=75                                         |
| R3 QS2 - (Weissler QS2 - 35), session median [HFC] |  14.15  | IQR -9 to 27 ms, n=27                                          |
| R3 CNAP ET - Weissler LVET, session median [HFC]   | -32.594 | IQR -47 to -10 ms, n=22                                        |
| R4 CNAP ET on PCG QS2, within-record beta          |  -0.039 | CI -0.15-0.08; rmcorr -0.03; 91 rec                            |


## tracking

| site   | x          | y                    | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |     r |   r_lo |   r_hi |
|:-------|:-----------|:---------------------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|------:|-------:|-------:|
| ear    | pcg_QS2_ms | t_D_ms               | -         |      67 |       44 |    2512 |  0.555 |     0.389 |     0.696 | 0.492 |  0.334 |  0.646 |
| ear    | pcg_QS2_ms | t_D_ms               | HR_ref    |      67 |       44 |    2512 |  0.453 |     0.187 |     0.616 | 0.383 |  0.133 |  0.598 |
| ear    | pcg_QS2_ms | t_reb_ms             | -         |      70 |       46 |    2754 |  0.243 |    -0.016 |     0.466 | 0.129 | -0.008 |  0.28  |
| ear    | pcg_QS2_ms | t_reb_ms             | HR_ref    |      70 |       46 |    2754 |  0.306 |    -0.096 |     0.573 | 0.139 | -0.035 |  0.318 |
| ear    | pcg_QS2_ms | ECG_S_ms             | -         |      87 |       58 |    4561 |  0.562 |     0.432 |     0.673 | 0.608 |  0.492 |  0.699 |
| ear    | pcg_QS2_ms | ECG_S_ms             | HR_ref    |      87 |       58 |    4561 |  0.576 |     0.356 |     0.724 | 0.518 |  0.322 |  0.664 |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | -         |      67 |       44 |    2512 |  0.322 |     0.064 |     0.534 | 0.226 |  0.042 |  0.413 |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |      67 |       44 |    2512 |  0.374 |    -0     |     0.613 | 0.227 | -0     |  0.444 |
| finger | pcg_QS2_ms | t_D_ms               | -         |     101 |       68 |    4487 |  0.78  |     0.676 |     0.87  | 0.562 |  0.445 |  0.674 |
| finger | pcg_QS2_ms | t_D_ms               | HR_ref    |     101 |       68 |    4487 |  0.709 |     0.505 |     0.84  | 0.416 |  0.259 |  0.561 |
| finger | pcg_QS2_ms | t_reb_ms             | -         |     102 |       69 |    5089 |  0.603 |     0.5   |     0.696 | 0.43  |  0.314 |  0.555 |
| finger | pcg_QS2_ms | t_reb_ms             | HR_ref    |     102 |       69 |    5089 |  0.611 |     0.417 |     0.748 | 0.334 |  0.189 |  0.482 |
| finger | pcg_QS2_ms | ECG_S_ms             | -         |     102 |       69 |    5259 |  0.58  |     0.456 |     0.692 | 0.617 |  0.505 |  0.703 |
| finger | pcg_QS2_ms | ECG_S_ms             | HR_ref    |     102 |       69 |    5259 |  0.568 |     0.33  |     0.736 | 0.509 |  0.295 |  0.659 |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | -         |     101 |       68 |    4487 |  0.624 |     0.507 |     0.716 | 0.511 |  0.384 |  0.63  |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |     101 |       68 |    4487 |  0.623 |     0.413 |     0.756 | 0.411 |  0.24  |  0.565 |


## tracking_diff

| site   | partial   |   diff |   diff_lo |   diff_hi |   n_rec |
|:-------|:----------|-------:|----------:|----------:|--------:|
| ear    | -         |  0.233 |     0.092 |     0.403 |      67 |
| ear    | HR_ref    |  0.079 |    -0.036 |     0.252 |      67 |
| finger | -         |  0.156 |     0.09  |     0.235 |     101 |
| finger | HR_ref    |  0.087 |     0.011 |     0.182 |     101 |


## interval

| site   | x           | y      | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |     r |   r_lo |   r_hi |
|:-------|:------------|:-------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|------:|-------:|-------:|
| ear    | cnap_ET_ms  | S_D_ms | -         |      61 |       38 |    2160 |  0.297 |     0.148 |     0.5   | 0.312 |  0.144 |  0.511 |
| ear    | pcg_S1S2_ms | S_D_ms | -         |      66 |       43 |    2437 |  0.384 |     0.264 |     0.502 | 0.395 |  0.269 |  0.521 |
| ear    | RR_ms       | S_D_ms | -         |      67 |       44 |    2512 |  0.067 |     0.039 |     0.099 | 0.268 |  0.157 |  0.371 |
| finger | cnap_ET_ms  | S_D_ms | -         |      88 |       59 |    3011 |  0.193 |     0.095 |     0.33  | 0.191 |  0.1   |  0.301 |
| finger | pcg_S1S2_ms | S_D_ms | -         |      97 |       64 |    4303 |  0.363 |     0.284 |     0.448 | 0.324 |  0.246 |  0.411 |
| finger | RR_ms       | S_D_ms | -         |     101 |       68 |    4487 |  0.045 |     0.025 |     0.065 | 0.168 |  0.093 |  0.241 |


## interval_between

| site   | pair                             |   rho |     p |   n_sessions |
|:-------|:---------------------------------|------:|------:|-------------:|
| ear    | S-D vs CNAP ET (session medians) | 0.396 | 0.001 |           67 |
| finger | S-D vs CNAP ET (session medians) | 0.478 | 0     |           93 |


## lags

| site       | quantity    |   median |      q25 |     q75 |   n_sessions |
|:-----------|:------------|---------:|---------:|--------:|-------------:|
| ear        | S_lag       |  -73.685 | -101.787 | -45.174 |           89 |
| ear        | D_lag       |  131.861 |   93.134 | 149.968 |           78 |
| ear        | reb_lag     |  231.823 |  205.573 | 258.526 |           82 |
| ear        | reb_minus_D |   95.005 |   79.753 | 107.957 |           78 |
| ear        | S2_to_notch |  181     |  165     | 197     |           97 |
| finger     | S_lag       |  -69.28  |  -89.892 | -53.243 |          102 |
| finger     | D_lag       |  128.505 |  116.378 | 139.289 |          102 |
| finger     | reb_lag     |  226.056 |  210.57  | 237.352 |          102 |
| finger     | reb_minus_D |   94.232 |   83.812 | 109.877 |          102 |
| finger     | S2_to_notch |  181     |  165     | 197     |           97 |
| finger-ear | ECG_S_ms    |    2.951 |  -12.328 |  23.125 |           89 |
| finger-ear | t_D_ms      |    5.543 |  -14.553 |  43.474 |           77 |
| finger-ear | t_reb_ms    |   -0.733 |  -22.633 |  73.381 |           80 |


## posthoc_intervals

| site   | x           | y                                     | partial   |   n_rec |   n_subj |   n_win |    beta |   beta_lo |   beta_hi |       r |    r_lo |    r_hi |    diff |   diff_lo |   diff_hi |
|:-------|:------------|:--------------------------------------|:----------|--------:|---------:|--------:|--------:|----------:|----------:|--------:|--------:|--------:|--------:|----------:|----------:|
| ear    | pcg_QS2_ms  | S_D_ms                                | -         |      67 |       44 |    2512 |   0.077 |    -0.042 |     0.245 |   0.07  |  -0.045 |   0.195 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_D_ms                                | -         |      66 |       43 |    2437 |   0.384 |     0.264 |     0.502 |   0.395 |   0.269 |   0.521 | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | S_reb_ms                              | -         |      70 |       46 |    2754 |  -0.234 |    -0.406 |    -0.074 |  -0.118 |  -0.195 |  -0.038 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_reb_ms                              | -         |      69 |       45 |    2672 |   0.12  |    -0.064 |     0.28  |   0.07  |  -0.037 |   0.173 | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |      67 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.077 |    -0.042 |     0.245 |
| finger | pcg_QS2_ms  | S_D_ms                                | -         |     101 |       68 |    4487 |   0.181 |     0.094 |     0.294 |   0.151 |   0.085 |   0.23  | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_D_ms                                | -         |      97 |       64 |    4303 |   0.363 |     0.284 |     0.448 |   0.324 |   0.246 |   0.411 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | S_reb_ms                              | -         |     102 |       69 |    5089 |   0.024 |    -0.035 |     0.09  |   0.02  |  -0.03  |   0.069 | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_reb_ms                              | -         |      98 |       65 |    4879 |   0.168 |     0.095 |     0.243 |   0.154 |   0.086 |   0.234 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |     101 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.181 |     0.094 |     0.294 |


# Experiment 1 [s2_onset]

Reference gate: {'R1': True, 'R2': True, 'R3': True, 'R4': False} -> FAIL

- ear: HR-partialled **inconclusive** (beta_D 0.58 [0.36, 0.71], beta_reb 0.37 [-0.06, 0.63], D-reb 0.14 [-0.01, 0.36]); raw: inconclusive (beta_D 0.64 [0.50, 0.76], beta_reb 0.28 [0.01, 0.50], D-reb 0.29 [0.13, 0.48])
- finger: HR-partialled **inconclusive** (beta_D 0.78 [0.61, 0.90], beta_reb 0.70 [0.52, 0.81], D-reb 0.09 [0.03, 0.18]); raw: inconclusive (beta_D 0.82 [0.72, 0.90], beta_reb 0.65 [0.54, 0.73], D-reb 0.16 [0.10, 0.23])

## reference_validity

| check                                              |   value | detail                                                         |
|:---------------------------------------------------|--------:|:---------------------------------------------------------------|
| R1 PCG S2 QC yield (windows)                       |   0.817 | 102 records with >= 50% ok of 107                              |
| R2 earbud S2 vs PCG S2, within-record beta         |   0.728 | CI 0.61-0.82; rmcorr 0.75; 91 rec / 3113 win; median lag 35 ms |
| R3 QS2 - (Weissler QS2 - 35), session median [HC]  | -21.329 | IQR -33 to -13 ms, n=76                                        |
| R3 CNAP ET - Weissler LVET, session median [HC]    | -24.531 | IQR -39 to -13 ms, n=75                                        |
| R3 QS2 - (Weissler QS2 - 35), session median [HFC] |  -2.453 | IQR -28 to 14 ms, n=27                                         |
| R3 CNAP ET - Weissler LVET, session median [HFC]   | -45.053 | IQR -73 to -34 ms, n=26                                        |
| R4 CNAP ET on PCG QS2, within-record beta          |   0.085 | CI -0.05-0.23; rmcorr 0.05; 99 rec                             |


## tracking

| site   | x          | y                    | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |     r |   r_lo |   r_hi |
|:-------|:-----------|:---------------------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|------:|-------:|-------:|
| ear    | pcg_QS2_ms | t_D_ms               | -         |      67 |       44 |    2512 |  0.639 |     0.501 |     0.764 | 0.55  |  0.404 |  0.698 |
| ear    | pcg_QS2_ms | t_D_ms               | HR_ref    |      67 |       44 |    2512 |  0.577 |     0.356 |     0.709 | 0.46  |  0.236 |  0.654 |
| ear    | pcg_QS2_ms | t_reb_ms             | -         |      70 |       46 |    2754 |  0.276 |     0.012 |     0.496 | 0.142 |  0.006 |  0.292 |
| ear    | pcg_QS2_ms | t_reb_ms             | HR_ref    |      70 |       46 |    2754 |  0.367 |    -0.06  |     0.634 | 0.157 | -0.019 |  0.337 |
| ear    | pcg_QS2_ms | ECG_S_ms             | -         |      87 |       58 |    4561 |  0.569 |     0.441 |     0.678 | 0.611 |  0.497 |  0.702 |
| ear    | pcg_QS2_ms | ECG_S_ms             | HR_ref    |      87 |       58 |    4561 |  0.607 |     0.386 |     0.748 | 0.532 |  0.328 |  0.676 |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | -         |      67 |       44 |    2512 |  0.351 |     0.094 |     0.57  | 0.24  |  0.061 |  0.435 |
| ear    | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |      67 |       44 |    2512 |  0.433 |     0.053 |     0.68  | 0.249 |  0.025 |  0.474 |
| finger | pcg_QS2_ms | t_D_ms               | -         |     101 |       68 |    4487 |  0.819 |     0.723 |     0.901 | 0.59  |  0.472 |  0.703 |
| finger | pcg_QS2_ms | t_D_ms               | HR_ref    |     101 |       68 |    4487 |  0.784 |     0.611 |     0.895 | 0.457 |  0.303 |  0.602 |
| finger | pcg_QS2_ms | t_reb_ms             | -         |     102 |       69 |    5089 |  0.645 |     0.543 |     0.732 | 0.459 |  0.338 |  0.594 |
| finger | pcg_QS2_ms | t_reb_ms             | HR_ref    |     102 |       69 |    5089 |  0.697 |     0.522 |     0.81  | 0.376 |  0.234 |  0.527 |
| finger | pcg_QS2_ms | ECG_S_ms             | -         |     102 |       69 |    5259 |  0.586 |     0.457 |     0.698 | 0.622 |  0.506 |  0.709 |
| finger | pcg_QS2_ms | ECG_S_ms             | HR_ref    |     102 |       69 |    5259 |  0.594 |     0.339 |     0.756 | 0.528 |  0.296 |  0.679 |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | -         |     101 |       68 |    4487 |  0.659 |     0.544 |     0.747 | 0.54  |  0.409 |  0.662 |
| finger | pcg_QS2_ms | t_reb_ms (D windows) | HR_ref    |     101 |       68 |    4487 |  0.692 |     0.508 |     0.804 | 0.454 |  0.284 |  0.606 |


## tracking_diff

| site   | partial   |   diff |   diff_lo |   diff_hi |   n_rec |
|:-------|:----------|-------:|----------:|----------:|--------:|
| ear    | -         |  0.288 |     0.127 |     0.477 |      67 |
| ear    | HR_ref    |  0.144 |    -0.008 |     0.364 |      67 |
| finger | -         |  0.16  |     0.097 |     0.233 |     101 |
| finger | HR_ref    |  0.092 |     0.03  |     0.179 |     101 |


## interval

| site   | x           | y      | partial   |   n_rec |   n_subj |   n_win |   beta |   beta_lo |   beta_hi |     r |   r_lo |   r_hi |
|:-------|:------------|:-------|:----------|--------:|---------:|--------:|-------:|----------:|----------:|------:|-------:|-------:|
| ear    | cnap_ET_ms  | S_D_ms | -         |      65 |       42 |    2318 |  0.124 |     0.048 |     0.242 | 0.168 |  0.066 |  0.308 |
| ear    | pcg_S1S2_ms | S_D_ms | -         |      66 |       43 |    2437 |  0.384 |     0.264 |     0.502 | 0.395 |  0.269 |  0.521 |
| ear    | RR_ms       | S_D_ms | -         |      67 |       44 |    2512 |  0.067 |     0.039 |     0.099 | 0.268 |  0.157 |  0.371 |
| finger | cnap_ET_ms  | S_D_ms | -         |      98 |       67 |    3826 |  0.064 |     0.016 |     0.131 | 0.085 |  0.023 |  0.161 |
| finger | pcg_S1S2_ms | S_D_ms | -         |      97 |       64 |    4303 |  0.363 |     0.284 |     0.448 | 0.324 |  0.246 |  0.411 |
| finger | RR_ms       | S_D_ms | -         |     101 |       68 |    4487 |  0.045 |     0.025 |     0.065 | 0.168 |  0.093 |  0.241 |


## interval_between

| site   | pair                             |   rho |     p |   n_sessions |
|:-------|:---------------------------------|------:|------:|-------------:|
| ear    | S-D vs CNAP ET (session medians) | 0.279 | 0.015 |           76 |
| finger | S-D vs CNAP ET (session medians) | 0.359 | 0     |           99 |


## lags

| site       | quantity    |   median |     q25 |     q75 |   n_sessions |
|:-----------|:------------|---------:|--------:|--------:|-------------:|
| ear        | S_lag       |  -57.717 | -89.429 | -33.581 |           89 |
| ear        | D_lag       |  143.71  | 118.66  | 163.641 |           78 |
| ear        | reb_lag     |  249.035 | 220.847 | 275.026 |           82 |
| ear        | reb_minus_D |   95.005 |  79.753 | 107.957 |           78 |
| ear        | S2_to_notch |  188.5   | 162     | 204     |          101 |
| finger     | S_lag       |  -52.805 | -71.472 | -40.953 |          102 |
| finger     | D_lag       |  142.948 | 130.37  | 152.764 |          102 |
| finger     | reb_lag     |  237.769 | 225.516 | 250.175 |          102 |
| finger     | reb_minus_D |   94.232 |  83.812 | 109.877 |          102 |
| finger     | S2_to_notch |  188.5   | 162     | 204     |          101 |
| finger-ear | ECG_S_ms    |    2.951 | -12.328 |  23.125 |           89 |
| finger-ear | t_D_ms      |    5.543 | -14.553 |  43.474 |           77 |
| finger-ear | t_reb_ms    |   -0.733 | -22.633 |  73.381 |           80 |


## posthoc_intervals

| site   | x           | y                                     | partial   |   n_rec |   n_subj |   n_win |    beta |   beta_lo |   beta_hi |       r |    r_lo |    r_hi |    diff |   diff_lo |   diff_hi |
|:-------|:------------|:--------------------------------------|:----------|--------:|---------:|--------:|--------:|----------:|----------:|--------:|--------:|--------:|--------:|----------:|----------:|
| ear    | pcg_QS2_ms  | S_D_ms                                | -         |      67 |       44 |    2512 |   0.136 |     0.007 |     0.324 |   0.119 |   0.007 |   0.253 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_D_ms                                | -         |      66 |       43 |    2437 |   0.384 |     0.264 |     0.502 |   0.395 |   0.269 |   0.521 | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | S_reb_ms                              | -         |      70 |       46 |    2754 |  -0.227 |    -0.409 |    -0.051 |  -0.111 |  -0.191 |  -0.026 | nan     |   nan     |   nan     |
| ear    | pcg_S1S2_ms | S_reb_ms                              | -         |      69 |       45 |    2672 |   0.12  |    -0.064 |     0.28  |   0.07  |  -0.037 |   0.173 | nan     |   nan     |   nan     |
| ear    | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |      67 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.136 |     0.007 |     0.324 |
| finger | pcg_QS2_ms  | S_D_ms                                | -         |     101 |       68 |    4487 |   0.211 |     0.119 |     0.328 |   0.176 |   0.109 |   0.254 | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_D_ms                                | -         |      97 |       64 |    4303 |   0.363 |     0.284 |     0.448 |   0.324 |   0.246 |   0.411 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | S_reb_ms                              | -         |     102 |       69 |    5089 |   0.059 |    -0.005 |     0.135 |   0.048 |  -0.004 |   0.104 | nan     |   nan     |   nan     |
| finger | pcg_S1S2_ms | S_reb_ms                              | -         |      98 |       65 |    4879 |   0.168 |     0.095 |     0.243 |   0.154 |   0.086 |   0.234 | nan     |   nan     |   nan     |
| finger | pcg_QS2_ms  | t_D_ms minus ECG_S_ms slopes (paired) | nan       |     101 |      nan |     nan | nan     |   nan     |   nan     | nan     | nan     | nan     |   0.211 |     0.119 |     0.328 |
