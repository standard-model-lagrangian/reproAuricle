# Validation experiments for D-only PWTA on Auricle

The spec was written and frozen on 2026-10-26, before any of these analyses were run. The decision rules below are fixed in advance so results can't steer the criteria. Results are added at the end of each section and summarised in [Results](#results).

The five experiments answer the questions left open by the reproduction ([RESULTS.md](RESULTS.md)):

| # | question | why it matters |
|---|---|---|
| 1 | Is the PPG "D wave" an end-systolic event at all? | Construct validity. No result so far shows that the dPPG/dt trough is the ArterioWave D wave. |
| 2 | Why does the ear lose the rebound when the finger keeps it, and can a principled filter recover it? | Decides between "different sensor or filter" and "different site". |
| 3 | Is a missing rebound (D-wave flattening) itself a signal? | The pipeline currently discards those windows, and the finger hints that they track EF. |
| 4 | Do the PWTA D features add anything beyond age plus generic pulse-shape features? | Without this, the finger's HF discrimination isn't evidence for ArterioWave. |
| 5 | What do the measurement error and sample size allow Auricle to show at all? | It sets how much negative results can be read into, and how large MIMIC or other datasets need to be. |

## Shared infrastructure

**Windows.** Two window sets, both using the default pipeline (`sg:61:4`, `rebound_es`, the same QC):
- `rest`: 60-s rest windows, as in `outputs/windows_rest.csv`.
- `all_20s`: 20-s windows over labels 0–4, settle 5 s, minimum 15 s, as in `outputs/sweep/`.

Both are regenerated into `outputs/validation/` so they carry the new columns. The existing columns must be bit-identical to the earlier outputs, and this is checked.

**New PPG columns** (`waves.py`; nothing existing changes):
- `t_reb_ms`: the time after R of the dicrotic rebound the D rule anchors to (a peak of dPPG/dt). NaN if there is none.
- `reb_rise_frac`: the largest rise of any dPPG/dt peak 200–550 ms after S from its preceding trough, divided by SWI. It is 0 if there is no peak. This is a continuous **rebound strength / flattening index**: the D rule's "rebound present" is `reb_rise_frac ≥ 0.05`.

**New morphology columns** (`pwta/morphology.py`): standard pulse-wave-analysis features that make no use of the ArterioWave wave model. They are computed on the ensemble PPG pulse `x` and its derivatives.
- `PAT_foot_ms`: R to the pulse foot, by the intersecting tangent (tangent at max dPPG/dt meets the pre-upstroke minimum).
- `CT_ms`: crest time, foot to systolic peak.
- `PW50_frac`: pulse width at 50% amplitude, divided by RR.
- `b_over_a`: second-derivative (SDPPG) b/a ratio. a = the first positive peak of d²PPG/dt² before S; b = the following minimum.

**Reference fiducials** (`pwta/reference.py`, `scripts/run_reference.py`): one row per window, keyed by `(rid, win_start)`. R peaks and windows are identical to the PPG pipeline: same detector, same `make_windows` call. Beats are the R-locked beats in the window that pass the ±20% RR rule.
- **Phonocardiogram (PCG, `Digital_Stethoscope`)** gives the primary end-systolic reference.
  - **Envelope:** 20–200 Hz zero-phase band-pass (4th order), Hilbert envelope, 40 Hz low-pass. Beats whose envelope maximum is more than 4× the window median of beat maxima are rejected (speech, movement). The remaining envelopes are averaged.
  - **S1:** envelope maximum 0–200 ms after R.
  - **S2** (aortic closure, A2-dominated): envelope maximum in [max(S1 + 150, 220), min(0.75·RR, 600)] ms. The output `QS2_ms` is R to the S2 envelope peak.
  - **S2 onset:** the 50% crossing of the S2 peak on its rising side, reported for sensitivity.
  - **QC:** SNR = S2 peak ÷ median envelope in [S2 + 150, RR − 50] ms ≥ 2.5; odd-vs-even-beat S2 within 10 ms; ≥ 8 beats.
  - `S1S2_ms` = S2 − S1 (an LVET proxy that includes isovolumic contraction). S1 has its own QC, SNR ≥ 2.5, and is often weak.
- **In-ear audio (`Earbud_Left`, `Earbud_Right`):** the same S2 algorithm. It is used only as an independent check of the PCG S2 (reference validity).
- **CNAP pressure (`NIBP`, finger of the other hand):**
  - Only beats fully inside CNAP-valid samples (`CNAP_Annotations` = 1) are used; at least 8 beats.
  - The ensemble pressure gives `SBP`, `DBP` and `MAP`, the last as the mean over one RR.
  - **Foot:** intersecting tangent at max dP/dt, searched 100–500 ms after R.
  - **Dicrotic notch:** the first local minimum of P between the systolic peak + 50 ms and foot + 0.65·RR, if its prominence is ≥ 0.5 mmHg. Otherwise the largest positive peak of d²P/dt² in the same span (inflection).
  - `cnap_ET_ms` = notch − foot, the ejection time at the periphery. It is kept only if 150–450 ms. `cnap_notch_type` records which detector was used.
- **SCG (accelerometer) is not used.** Sensor orientation varies by participant, which channel is the dorso-ventral axis is not documented, and AO/AC annotation on SCG would need its own validation. The PCG gives the end-systolic timing (S2) more directly.

**Statistics conventions.**
- **Within-record slope** (written β): the pooled slope after demeaning X and Y per record, Σdx·dy / Σdx². Only records with ≥ 4 paired windows count. "HR-partialled" means X and Y are first residualised on HR within each record.
- **Confidence intervals:** cluster bootstrap over **subjects**, 2000 replicates, percentile 95% CI.
- **rmcorr:** Pearson correlation of the record-demeaned values.
- **Subject-level tests:** one value per subject (the mean over sessions).
- **Partial Spearman:** Pearson correlation of rank residuals.

## Experiment 1: is the D wave end-systolic? (`scripts/validate_construct.py`, `outputs/validation/exp1_construct/`)

**Model.** In carotid wave-intensity analysis, the D (forward decompression) wave is produced by LV relaxation in late systole and peaks shortly before aortic valve closure (AVC). At a peripheral PPG site, every cardiac event arrives after a transit time τ. So under **H_ES** ("the PPG D is the transit-shifted end-systolic wave"):
- R-D ≈ R-AVC − δ + τ.
- The dicrotic rebound (the dicrotic wave's upstroke) ≈ R-AVC + ε + τ.
- S-D ≈ LVET − const, because τ cancels if the S and D waves travel the same path.

The PCG S2 marks AVC, so QS2 = R to S2.

**Data:** `all_20s` windows (rest plus manoeuvres give the within-record range), joined to the reference fiducials. Sensitivity analysis: rest windows only.

**Step 0: reference validity (gate).** If the gate fails, Experiment 1 is inconclusive.
- (R1) PCG S2 passes QC in ≥ 50% of windows, in ≥ 50 records.
- (R2) PCG vs earbud S2 (whichever earbud has the higher QC yield per record): within-record rmcorr ≥ 0.6 and β within [0.7, 1.3].
- (R3) Plausibility: the session-median `QS2_ms` sits within ±50 ms of Weissler's QS2(HR, sex) − 35 ms (the Q-to-R offset). The CNAP ET median sits within ±60 ms of Weissler's LVET(HR, sex). This is reported per cohort.
- (R4) Two independent LVET proxies agree: within-record β of `cnap_ET_ms` on `QS2_ms` > 0, with the lower CI > 0.

**Step 1: tracking (primary).** For each site:
- **Primary:** β_D = within-record slope of `t_D_ms` (R-D) on `QS2_ms`, HR-partialled. It is also reported raw.
- **Positive control:** β_reb = the same for `t_reb_ms`. The rebound is anatomically tied to valve closure.
- **Anchor:** β_S = the same for `ECG_S_ms`. The S wave is early-systolic and should track S2 less.
- **Decision (per site):**
  - **"D tracks end-systole"** if the lower CI of β_D is ≥ 0.5 and the paired-bootstrap CI of β_D − β_reb includes 0.
  - **"D does not track end-systole"** if β_reb's lower CI is ≥ 0.5, but β_D's upper CI is < 0.5 or the CI of β_D − β_reb is entirely below 0.
  - **Inconclusive** otherwise, including when the positive control fails.

**Step 2: interval (transit-cancelled).** Within-record β of `S_D_ms` on `cnap_ET_ms` and on `S1S2_ms`. H_ES predicts β ≈ 1 (CI overlapping [0.6, 1.4]).
- **Contrast:** the β of `S_D_ms` on RR (a diastole-locked feature would give a large positive β; a systolic one a small β), HR not partialled.
- **Between-subject:** Spearman correlation of the session medians of S-D with CNAP ET.

**Step 3: absolute lags (descriptive).**
- D lag = R-D − QS2 and rebound lag = R-rebound − QS2 per site.
- Rebound − D and the finger-minus-ear difference of each lag. A shared path predicts finger − ear lags that are about equal for S, D and rebound.

## Experiment 2: why the ear loses the rebound, and whether a filter can recover it (`scripts/validate_site_rebound.py`, `outputs/validation/exp2_site_rebound/`)

**2a. Concordance.** In rest windows that are S-clean at both sites, a 2×2 table of rebound presence (`reb_rise_frac ≥ 0.05`), ear vs finger, by cohort. Exact McNemar test. "Site-specific loss" means the discordant windows are dominated by finger-yes / ear-no.

**2b. Determinants.**
- **Trait (subject level, rest):** Spearman correlation of the ear rebound fraction with age, sex, height, BMI, HR, MAP (CNAP), ear PPG amplitude (`PPG_amp`), the finger rebound fraction and, for HC only, the ear-sensor placement offset (the distance between `PPG_Ear` and the `Left_Ear` landmark in `sensor_coordinates.csv`).
- **State (within subject, `all_20s`):** within-subject slope of ear `reb_rise_frac` on HR and on MAP (both record-demeaned), with a cluster-bootstrap CI.

**2c. Is the ear pulse a smoothed finger pulse?** In paired rest windows, the ear ensemble pulse is fitted as `x_ear(t) ≈ g·G_σ(x_finger)(t − Δ) + c`, where G_σ is a zero-phase Gaussian blur. The grid is σ ∈ {0, 2, 4, …, 60} ms and Δ ∈ [−150, +100] ms, with g and c by least squares, fitted over [R + 50 ms, R + RR − 50 ms].
- Outputs: the best σ, Δ and R² per window.
- Test: is σ larger in ear windows without a rebound (finger rebound present) than in ear windows with one? Window-level and subject-level AUROC.
- **Decision:**
  - **"Ear ≈ smoothed finger"** if the median R² ≥ 0.95.
  - **"Smoothing explains the rebound loss"** if, additionally, the subject-level AUROC of σ for no rebound is ≥ 0.75.

**2d. Principled inverse filter.** This is the ear-only test of the "different sensor, screen more filters" argument.
- **Fit:** σ_pop = the median best σ over HC session-1 windows (training).
- **Apply:** to all other windows (held out: HC session 2 and HFC), deconvolve the ear ensemble pulse with a Wiener inverse of G_σpop: H/(H² + λ), λ = 10⁻² (fixed in advance; 10⁻¹ and 10⁻³ as sensitivity). Then take the same SG derivative and run the D pick on the result. The finger is not used by the corrected ear.
- **Baseline:** the same ensemble-level path without deconvolution, which should reproduce the pipeline's values.
- **Outcomes (held-out windows):**
  - D-wave yield (`rebound_es` D found and distinct, with S-clean).
  - Split-half |ΔS-D|.
  - The fraction of S-D values in 100–350 ms.
  - The within-record S-D slope on HR.
  - Within-record ρ of ear S-D with finger S-D, separately for windows rescued by deconvolution and windows with a native rebound.
- **Decision: "rescued"** only if all three hold:
  - yield rises by ≥ 15 percentage points;
  - the rescued windows' within-record ρ with the finger is ≥ the native windows' ρ − 0.1;
  - the median split-half |ΔS-D| of the rescued windows is ≤ 2 ms.

## Experiment 3: D-wave flattening as a feature (`scripts/validate_flattening.py`, `outputs/validation/exp3_flattening/`)

**Features** (rest windows that are S-clean, subject level = the mean of session medians):
- `reb_rise_frac` (continuous; lower = flatter) and `no_rebound_frac` (the share of windows with `reb_rise_frac < 0.05`), at both sites.
- `D_sharpness` from fully ok windows, for comparison.

**Primary hypothesis** (from the trial proposal's link of D-wave flattening to HFpEF, and the finger's no-rebound shares of 19% in HFrEF vs 49% in EF ≥ 50%): within the HF cohort, finger `reb_rise_frac` falls as LVEF rises. The test is a one-sided partial Spearman adjusted for age. A two-sided p is reported.

**Secondary tests** (Holm-corrected as one family):
1. The same at the ear.
2. `no_rebound_frac` vs LVEF at each site.
3. AUROC for EF ≥ 50% vs EF < 40%, at each site.
4. HF vs HC AUROC in the age-overlap subset (28–57 years).

**Confounder sensitivity** for the primary test: adjust for age + HR, age + beta-blocker (yes/no), age + AF history; exclude CRT. Also the age dependence of each feature within HC, to show how strongly age alone moves it.

**Decision: "supportive"** if the primary partial ρ ≤ −0.4 with p < 0.05, and every sensitivity analysis keeps the sign with |ρ| ≥ 0.3. "Not supported" if ρ > −0.2. Otherwise "weak/inconclusive".

## Experiment 4: incremental value over age and generic pulse shape (`scripts/validate_incremental.py`, `outputs/validation/exp4_incremental/`)

**Feature blocks** (subject level, rest; S-tier windows for S-only features, ok windows for D features):
- **Generic** (standard pulse-wave analysis, no ArterioWave model): `PAT_foot_ms`, `ECG_S_ms` (the pulse arrival time to max slope), `CT_ms`, `PW50_frac`, `b_over_a`, `HR`.
- **PWTA-D:** `S_D_ms`, `SWS`, `DWI_over_SWI`, `reb_rise_frac`.

**Endpoints:**
- E1: HF vs HC in the age-overlap subset (28–57 years). This is the primary endpoint.
- E2: HF vs HC across all subjects.
- E3: LVEF within HFC.

**Models** per site:
- M0 = age; M1 = age + generic; M2 = age + generic + PWTA-D.
- Classification: L2 logistic regression (C = 1), standardised, with median imputation inside each fold. Repeated stratified 5-fold, 20 repeats.
- LVEF: ridge regression (α = 1) with repeated 5-fold, 20 repeats. Metrics are CV R² and the Spearman correlation of predictions with LVEF.

**Test.** ΔAUROC (M2 − M1), and ΔR² for E3. The null is built by permuting the PWTA-D block across subjects (500 permutations), which keeps the block's correlation structure while breaking its link to the outcome.

**Decision: "PWTA-D adds value at site X"** if ΔAUROC ≥ 0.05 with a permutation p < 0.05 on E1. Otherwise "no evidence of incremental value" (with n ≈ 28, this is weak evidence of absence; see Experiment 5).

## Experiment 5: precision ceiling and power (`scripts/validate_precision.py`, `outputs/validation/exp5_precision/`)

**Variance components** per feature × site, from rest windows of HC with both sessions:
- σ_w² = the pooled within-session variance between windows.
- σ_day² from Var(m₂ − m₁) = 2σ_day² + σ_w²(1/k₁ + 1/k₂).
- σ_b² = Cov(m₁, m₂), where m is a session mean of k windows.
- If an estimate comes out negative, it is set to 0.

**Reliability** of a single-session mean of k windows: R(k) = σ_b² / (σ_b² + σ_day² + σ_w²/k). This is reported at the median k, along with the ceiling R(∞), the k needed for R = 0.8 (if it can be reached), and the number of separate days D needed for R = 0.8 with k = median.

**HF scenario.** HC are young and homogeneous, so σ_b² may be small. σ_b,HF² = Var_HF(session means) − σ_day² − σ_w²/k̄, assuming the within-subject components carry over from HC.

**Attenuation and sample size.**
- ρ_obs = ρ_true·√(R_x·R_LVEF), with R_LVEF = 0.8 assumed for echocardiographic EF.
- The n needed for ρ_true ∈ {0.3, 0.5} (two-sided α = 0.05, 80% power, Fisher z).
- The power Auricle actually has for ρ_true = 0.5 with the HF subjects that have both LVEF and the feature.
- This is computed under both the HC and the HF σ_b scenarios.

## Results

The decision rules above were not changed. Anything not in the frozen spec is labelled **post hoc**.

Run: `./reproduce.sh validation audit`. It runs these steps:

```bash
.venv-pwta/bin/python scripts/run_batch.py --out outputs/validation/windows_rest.csv
.venv-pwta/bin/python scripts/run_batch.py --labels 0 1 2 3 4 --window-s 20 --min-window-s 15 --settle-s 5 --out outputs/validation/windows_all_20s.csv
.venv-pwta/bin/python scripts/run_reference.py --out outputs/validation/reference_rest.csv
.venv-pwta/bin/python scripts/run_reference.py --labels 0 1 2 3 4 --window-s 20 --min-window-s 15 --settle-s 5 --out outputs/validation/reference_all_20s.csv
.venv-pwta/bin/python scripts/validate_construct.py      # exp 1
.venv-pwta/bin/python scripts/validate_site_rebound.py   # exp 2
.venv-pwta/bin/python scripts/validate_flattening.py     # exp 3
.venv-pwta/bin/python scripts/validate_incremental.py    # exp 4 (permutations; the slowest step)
.venv-pwta/bin/python scripts/validate_precision.py      # exp 5
# audit: 1200-ms rerun, window variants, sensitivity reruns, then scripts/audit_checks.py checks
```

The regenerated window tables match the earlier outputs bit for bit in every existing column.

| # | verdict (frozen rule) | one-line reading |
|---|---|---|
| 1 | **inconclusive** (reference gate failed: CNAP ET does not track S2) | D is a systolic-phase event and not diastole-locked. Whether S-D follows ejection time 1:1 can't be decided. Its S1–S2 slope of 0.37 may be attenuated by S1 timing error (audit: unresolved), and S-D moves little with QS2 (0.08–0.18). It cannot be confirmed as the end-systolic wave. The rebound positive control also fails. |
| 2 | ear ≈ smoothed finger: **yes**. Smoothing explains which windows lose the rebound: **no**. Deconvolution rescues the ear D: **no** (primary λ; the two sensitivity λs pass) | The rebound loss is site-specific and haemodynamic (height, MAP), not sensor noise. Deconvolution is a real but fragile lead, not a reason for a broad filter screen. |
| 3 | **weak/inconclusive** | Finger flattening sits in the EF ≥ 50% group (n = 8). There is no monotone LVEF gradient (ρ = −0.28, p = 0.09). |
| 4 | **no evidence of incremental value** at either site | At the finger, age + generic pulse shape already gives AUROC 0.93 in the age-overlap subset. PWTA-D adds −0.005. No model predicts LVEF out of sample. |
| 5 | (descriptive) | Day-to-day variation caps single-session reliability. S-D would need 6–9 separate days to reach 0.8. Auricle has 10–27% power for a true ρ = 0.5 between S-D and LVEF. |

### Experiment 1: is D end-systolic? (`outputs/validation/exp1_construct/exp1.md`)

**Reference gate: fails** on R4 (and on R2 when manoeuvres are included).

| check | result | pass? |
|---|---|---|
| R1 PCG S2 QC yield | 82% of 20-s windows; 102/107 records ≥ 50% | yes |
| R2 earbud S2 vs PCG S2 | β 0.67 [0.55, 0.77], rmcorr 0.70 (all windows); β 0.84 [0.70, 0.97], rmcorr 0.75 (rest only). The earbud lags by 22 ms | borderline: fails with manoeuvres, passes at rest |
| R3 plausibility | QS2 − (Weissler − 35 ms): HC −8, HFC +14 ms. CNAP ET − Weissler LVET: HC −24, HFC −45 ms | yes |
| R4 CNAP ET vs QS2 within record | β 0.07 [−0.05, 0.21], rmcorr 0.04 (0.06 at rest; −0.04 using true-minimum notches only). CNAP ET also doesn't shorten with HR (−0.02 ms/bpm, against about −1.7 for LVET) | **no** |

**What the gate means.**
- The PCG S2 is a sound reference: it is found almost everywhere, sits where Weissler predicts, and agrees with the independent in-ear S2.
- The CNAP ejection time is not a usable reference. Its foot-to-notch interval doesn't follow S2 within a recording, even when only true notch minima are used. So the CNAP interval tests below can't be interpreted.

**Tracking (pre-registered; HR-partialled within-record slope on QS2, `all_20s`).**

| site | β_D (R-D) | β_reb (rebound, positive control) | β_S (ECG-S, anchor) | β_D − β_reb | rule outcome |
|---|---|---|---|---|---|
| ear | 0.45 [0.19, 0.62] | 0.31 [−0.10, 0.57] | 0.58 [0.36, 0.72] | 0.08 [−0.04, 0.25] | inconclusive: positive control fails |
| finger | 0.71 [0.51, 0.84] | 0.61 [0.42, 0.75] | 0.57 [0.33, 0.74] | 0.09 [0.01, 0.18] | inconclusive: D tracks S2 *more* than the rebound, a case the rule didn't cover |

- Raw slopes, rest-only windows and S2 onset instead of S2 peak give the same pattern: finger β_D 0.73–0.85, ear 0.42–0.64.

**Interval (transit-cancelled), within-record β of S-D.**

| x | ear | finger |
|---|---|---|
| S1–S2 interval | 0.38 [0.26, 0.50] | 0.36 [0.28, 0.45] |
| CNAP ET | 0.12 [0.05, 0.24] | 0.06 [0.02, 0.13] |
| RR | 0.07 [0.04, 0.10] | 0.05 [0.02, 0.06] |

The CNAP ET row is uninterpretable because the reference failed.

**Post hoc checks.**
- **S-D on QS2:** ear 0.08 [−0.04, 0.24], finger 0.18 [0.09, 0.29].
- **S-to-rebound interval** on QS2: ear −0.23, finger 0.02. On S1–S2: ear 0.11, finger 0.16.

**Absolute lags (session medians, ms after S2).**
- S wave −70.
- D wave +130 at both sites.
- Rebound +230.
- CNAP notch +174.
- Finger − ear arrival: S +3, D +6, rebound −1.

**Reading.**
- All three PPG events (S, D, rebound) shift with S2 by half to three-quarters of its change, and S shifts as much as the rebound. Most of this co-movement is therefore common-mode: pre-ejection period, transit time and sympathetic state, which move every event together.
- The end-systole-specific part is S-D. Its observed slope on the S1–S2 interval is about 0.37 at both sites. **Audit:** whether this slope is attenuated by S1 timing error is unresolved; two checks disagree (see [Audit](#audit)). The earlier claim that "the CI excludes 1" is therefore downgraded from a finding to a lean.
- S-D on QS2, which is free of reference noise, is 0.08 (ear) and 0.18 (finger). What H_ES predicts here depends on the unmeasured share of QS2 changes due to pre-ejection period. ECG-S tracks QS2 at about 0.57, which suggests that LVET's share, and so the H_ES prediction, is at least around 0.4. That is a hint, not a test. S-D is clearly not diastole-locked (RR slope ≈ 0.05).
- The absolute lags are consistent with D peaking about 45 ms before the transit-shifted valve closure, assuming a common S2-to-site delay of about 175 ms.
- The rebound positive control fails too. So the limit may lie in the references (no direct LVET: S1–S2 includes isovolumic contraction, and CNAP ET is unusable), not only in D.
- **Bottom line:** D behaves like a systolic-phase event that partly follows ejection time. Auricle can't confirm that it *is* the end-systolic wave. That needs a direct LVET reference, such as an aortic flow or ultrasound (the carotid trial data) or a validated SCG AC point.

### Experiment 2: why the ear loses the rebound (`outputs/validation/exp2_site_rebound/exp2.md`)

**2a. Concordance (rest windows S-clean at both sites).**

| | windows | both | ear only | finger only | neither | subject median ear / finger |
|---|---|---|---|---|---|---|
| HC | 1094 | 694 | 0 | 400 | 0 | 0.70 / 1.00 |
| HFC | 259 | 107 | 4 | 100 | 48 | 0.22 / 1.00 |

99% of discordant windows have a rebound at the finger and none at the ear (McNemar p ≈ 0). The loss is site-specific.

**2b. Determinants.**
- **Trait:** the ear rebound fraction rises with **height** (HC ρ 0.50, p 0.001; all 0.31) and falls with **MAP** (HC ρ −0.37, p 0.02; all −0.26). It is unrelated to age within HC, sex, BMI, HR or ear PPG amplitude.
- **Sensor offset** is uninformative: the `PPG_Ear` coordinate sits a near-constant 0.5–0.65 cm from the ear landmark and appears to be derived from it.
- **State, within record:** higher MAP weakens the ear rebound (rmcorr −0.20 [−0.26, −0.14]; finger −0.09).
- **Audit:** the apparent fall in rebound presence with HR (−0.6 percentage points/bpm) comes entirely from windows above 100 bpm. There, the next-beat guard shrinks the rebound search span. Below 100 bpm the slope is +0.13 pp/bpm [−0.23, +0.47], so there is no HR effect.
- **Reading:** a taller body (later wave reflection) and lower pressure (slower PWV) keep the dicrotic wave separate. This points to wave-reflection timing, which is haemodynamics, not sensor or filter.

**2c. Transfer fit.**
- The ear pulse is closely described as a time-aligned (median Δ 2 ms), heavily blurred finger pulse: median R² 0.985, 85% of windows ≥ 0.95.
- The blur is large, σ ≈ 60 ms. This hit the 60 ms grid edge in 61% of windows; the post hoc grid up to 160 ms gives a median of 64 ms.
- The blur barely separates ear windows that have a rebound from those that don't: window AUROC 0.65, subject AUROC 0.62 (0.66 post hoc).
- **Reading:** smoothing explains the shape difference between sites, not which windows lose the rebound.
- **Audit:** the fit window was capped at R + 640 ms, against the spec's R + RR − 50, so that shifted finger samples stay inside the 800-ms ensemble. This is a deviation from the spec. Refitting with 1200-ms ensembles and the spec window gives median R² 0.976, 77% ≥ 0.95 and subject AUROC 0.60. The decisions don't change.

**2d. Wiener deconvolution** (σ_pop = 60 ms from HC session 1; held out: HC session 2 + HFC, 898 ear windows; the baseline reproduces the pipeline exactly).

| λ | D yield (base → corrected) | rescued | split-half S-D, rescued | S-D 100–350 ms, rescued | S-D/HR slope (ms/bpm) | ρ with finger: native / rescued | rule |
|---|---|---|---|---|---|---|---|
| **0.01 (primary)** | 44% → 79% (+35 pp) | 344 | 1.5 ms | 75% | −1.35 (baseline −0.84) | 0.45 / 0.20 | **not rescued** (ρ criterion of ≥ 0.35 missed) |
| 0.1 | 44% → 65% (+20 pp) | 198 | 1.1 ms | 99% | −0.46 | 0.45 / 0.43 | rescued |
| 0.001 | 44% → 86% (+42 pp) | 377 | 0.8 ms | 99% | **+0.25** | 0.45 / 0.37 | rescued |

- **Audit fix:** native windows are now scored on their pipeline S-D, and each category is demeaned on its own. Originally native windows were scored on their deconvolved S-D, which put native ρ at 0.34 / 0.38 / 0.26 and lowered the bar. The verdicts are unchanged.
- **Audit finding:** deconvolution also moves the D in windows that already had one, by a median of 15 / 24 / 8 ms (63% / 88% / 39% move more than 10 ms). So the corrected trace often picks a different trough, not the same D more often. This adds to the fragility.
- In windows where the D is rescued, the finger − ear S-D offset is similar to native windows (−8 vs −10 ms at λ = 0.01).
- **Reading:**
  - A single, physically motivated inverse filter, trained on one session and applied ear-only, creates a stable D in a third or more of the ear windows that had none. Those D waves roughly follow the finger.
  - But the pre-registered λ narrowly fails, and properties change with λ. At λ = 0.001 the S-D-vs-HR slope even has the wrong sign. So which trough gets picked depends on the regularisation.
  - This is the one form of the "different sensor, try other filters" argument with real support. It is a model-based deconvolution that would need an external D reference to set λ and a held-out test, **not** a broad filter screen. The 15-filter screen and the SG grid had already shown that ordinary smoothing choices don't matter.

### Experiment 3: flattening as a feature (`outputs/validation/exp3_flattening/exp3.md`)

**Primary result.** Finger `reb_rise_frac` vs LVEF within HF, adjusted for age: ρ = −0.28, one-sided p = 0.09, n = 26 → **weak/inconclusive**. It is stable under adjustment (−0.23 to −0.27 with HR, beta-blocker, AF, or CRT excluded).

**Secondary tests:** every Holm-adjusted p is 1.
- EF ≥ 50 vs EF < 40: finger AUROC 0.68 (p 0.18), ear 0.58.
- HF vs HC in the age-overlap subset: 0.53 at both sites.

| median `reb_rise_frac` | finger | ear |
|---|---|---|
| controls | 0.24 | 0.09 |
| HFrEF (n = 14 / 10) | 0.31 | 0.02 |
| HFmrEF (4 / 3) | 0.35 | 0.19 |
| EF ≥ 50% (8 / 5) | **0.07** | 0.00 |

**Reading.**
- The finger flattening is concentrated in the EF ≥ 50% group, while HFrEF is no flatter than controls. So it is a group effect in 8 people, not an LVEF gradient. It is consistent with the HFpEF hypothesis, but underpowered (Experiment 5).
- Flattening is unrelated to age within HC, though HC only spans ages 19–57.
- At the ear, flattening is everywhere and so has no contrast.
- *Descriptive:* ear D sharpness vs LVEF adjusted for age gives ρ 0.73 (n = 10), in line with the earlier 0.63.

### Experiment 4: incremental value (`outputs/validation/exp4_incremental/exp4.md`)

CV AUROC (E1, E2) or CV R² (E3), with 20 × 5-fold repeats and 500 permutations of the PWTA-D block. Two p-values are given:
- the spec's row permutation of the PWTA-D block (perm p);
- **audit:** the Freedman–Lane permutation of the PWTA-D residuals after regressing on age + generic (FL p).

The row permutation also breaks the block's correlation with the generic features, so its null Δ sits below zero (median −0.01 to −0.05) and its p-values are biased low. Freedman–Lane is the correct null for "adds nothing beyond generic".

| endpoint | site | n (HF) | M0 age | M1 + generic | M2 + PWTA-D | Δ M2 − M1 | perm p | FL p |
|---|---|---|---|---|---|---|---|---|
| **E1 HF vs HC, age 28–57** | finger | 28 (15) | 0.59 | **0.93** | 0.92 | −0.005 | 0.16 | 0.37 |
| | ear | 26 (13) | 0.57 | 0.66 | 0.55 | −0.11 | 0.86 | 0.97 |
| E2 HF vs HC, all | finger | 69 (27) | 0.90 | 0.96 | 0.98 | +0.014 | 0.01 | 0.03 |
| | ear | 58 (18) | 0.85 | 0.86 | 0.80 | −0.07 | 0.96 | 1.00 |
| E3 LVEF within HFC (CV R²) | finger | 26 | −0.14 | −0.57 | −0.50 | +0.07 | 0.06 | 0.06 |
| | ear | 18 | −0.18 | −1.02 | −1.91 | −0.89 | 0.31 | 0.70 |

**Decision:** no evidence of incremental value at either site.
- On E2 the finger gains +0.014 (FL p 0.03). That is a statistically detectable but tiny gain near the ceiling, below the 0.05 effect threshold.
- No model has a positive CV R² for LVEF. With 18–26 subjects, LVEF can't be predicted out of sample from any block.

**Post hoc, univariate AUROC in the age-overlap subset** (`posthoc_univariate_age_overlap.csv`). At the finger, the generic **PW50/RR** separates HF from HC almost as well as anything else: AUROC 0.92 (HF pulses are narrower). The best single PWTA feature is **DWI/SWI**, at 0.96 (direction chosen post hoc), but it correlates with PW50/RR (ρ 0.64 in this subset, 0.76 overall). It is largely the same pulse-narrowing information under another name.

**Reading.** The finger's HF signal is generic pulse morphology: a narrower pulse and earlier arrival, which age, stiffness and medication would all produce. The ArterioWave D-wave features don't add to it in Auricle. With 28 subjects in the primary subset, this is weak evidence of absence (Experiment 5), not proof.

### Experiment 5: precision ceiling and power (`outputs/validation/exp5_precision/exp5.md`)

| feature | one-session R (HC spread) ear / finger | ceiling R(∞) ear / finger | separate days for R = 0.8, ear / finger | R with HF spread, ear / finger | n for true ρ = 0.5 with LVEF (HF scenario), ear / finger | Auricle power for ρ = 0.5, ear / finger |
|---|---|---|---|---|---|---|
| ECG-S | 0.69 / 0.56 | 0.69 / 0.57 | 1.8 / 3.2 | 0.85 / 0.82 | 44 / 46 | 40% / 54% |
| S-D | **0.31 / 0.39** | 0.32 / 0.40 | **8.7 / 6.3** | 0.76 / 0.46 | 50 / 84 | **19% / 27%** |
| SWS | 0.80 / 0.61 | 0.81 / 0.63 | 1.0 / 2.5 | 0.96 / 0.77 | 39 / 49 | 24% / 44% |
| DWI/SWI | 0.75 / 0.86 | 0.76 / 0.87 | 1.3 / 0.7 | 0.88 / 0.87 | 43 / 44 | 22% / 49% |
| reb_rise_frac | 0.71 / 0.79 | 0.72 / 0.80 | 1.7 / 1.1 | 0.82 / 0.92 | 46 / 41 | 38% / 59% |

**Reading.**
- **Audit, steady rest only** (windows ≥ 25 s after a manoeuvre, 686 of 1814): reliability is somewhat higher (ear S-D 0.40, ear ECG-S 0.81, finger S-D 0.39). S-D still needs about 6 days to reach 0.8, and Auricle's power for ρ = 0.5 stays at 16–25%. About 57% of rest windows start 10–24 s after a manoeuvre, so the all-rest numbers include some recovery transient.
- The ceiling R(∞) ≈ one-session R: more windows per session wouldn't help. Day-to-day biological variation is the limit, and for S-D it is larger than the spread between healthy subjects.
- With HF-like spread, reliability improves, but detecting a true ρ = 0.5 with LVEF still needs about 40–85 HF participants with usable features. Auricle has 10 (ear D) to 26 (finger S-tier).
- For ρ = 0.3, the needed n is 111–477.
- Negative or weak within-HF results in Auricle, including Experiment 3, are therefore weak evidence of absence.
- MIMIC-scale cohorts (hundreds) are the right size, provided the features survive 125 Hz sampling.

## Audit

The audit was done on 2026-10-26, after the results above, in two independent passes:
- a code review by a fresh reader, who was given the code and the spec but not the conclusions;
- empirical checks against the data.

Every suspected issue was confirmed by rerunning. Sensitivity reruns and every audit check (`scripts/audit_checks.py`) are in `outputs/validation/audit/`.

**Net effect: no pre-registered verdict changed.** Three readings are weakened:
- the Experiment 1 "S1–S2 CI excludes 1" claim;
- the Experiment 2 HR effect;
- the Experiment 4 E2 p-value.

One reading is strengthened: deconvolution moves existing D picks, which adds to its fragility.

### Checked and correct
- **Windows:**
  - No overlaps.
  - No window spans two activity labels (1384 spot-checked against the raw annotations).
  - The settle times are respected.
  - PPG and reference tables join 1:1 on (rid, win_start) with matching labels.
  - New columns leave existing columns bit-identical.
- **Heart sounds:**
  - PCG S2 was visually confirmed on random windows, including 143 bpm, SNR near threshold, and HF records.
  - S2 lands on its search bounds in < 0.1% of windows.
  - Split-half S2 noise is about 1 ms, against a within-record SD of 17.5 ms.
  - QS2 shortens with HR at −1.3 ms/bpm within record.
- **Leakage:**
  - Experiment 4 imputation and scaling run inside CV folds.
  - With permuted labels, CV AUROC is 0.49 ± 0.13.
  - No outcome information enters any feature.
  - Experiment 2d trains σ only on HC session 1, and the corrected ear never uses the finger.
- **Statistics:**
  - The variance-component estimator recovers simulated values.
  - Holm, partial Spearman (df = n − 2 − k), the Fisher-z sample size and power, the subject-cluster bootstrap and the paired bootstrap were all checked by hand.
  - The Experiment 1 and Experiment 3 decision code matches the spec.
  - The transfer-fit Δ sign and the Gaussian transfer function are correct.
  - The deconvolution baseline reproduces the pipeline.

### Fixed (code changed, affected experiments rerun)

| issue | where | effect of fix |
|---|---|---|
| 2d "native" windows were scored on their *deconvolved* S-D, and demeaning pooled native and rescued windows | `validate_site_rebound.py` | native ρ 0.34 → 0.45; rescued 0.20 / 0.43 / 0.37; verdicts unchanged |
| Experiment 4 row permutation made the PWTA-D block behave like noise (null Δ < 0, p biased low) | `validate_incremental.py` | Freedman–Lane null added; E1 finger p 0.16 → 0.37; E2 finger 0.01 → 0.03; verdicts unchanged |
| HC_1_1 has no `CNAP_Annotations`, and its CNAP beats were used unmasked (against the spec) | `reference.py` | excluded |
| MAP was averaged over a cycle truncated at 1000 ms in 64% of rest windows (+1.2 mmHg bias, correlated with RR), and was needlessly filtered on notch success | `reference.py`, `validate_site_rebound.py` | full-cycle CNAP segments (1700 ms); HC trait ρ −0.39 → −0.37 |
| S1 accepted at the edge of its search window (1.4% of S1-ok windows) | `reference.py` | `s1_ok` requires an interior peak; S1-ok yield 78.5% → 77.5%; S1–S2 slopes unchanged |
| Experiment 1 "tracks end-systole" branch didn't require the positive control, as the spec does | `validate_construct.py` | fixed; not triggered by the data |
| S lag not restricted to S-clean windows | `validate_construct.py` | −73.6 → −73.7 ms |

### Documented, not changed (sensitivity runs instead)

**1. 800-ms ensemble truncation.**
- The rebound search (S + 200 to 550 ms) is cut by the ensemble end in 70–85% of windows. But at 1200 ms, rebound presence changes in only 12 of 3044 S-clean windows. The finger's loss of rebound at slow HR is real.
- PW50 was censored in 6.7% of finger windows, all low-HR controls.
- At 1200 ms: Experiment 3 ρ −0.27, Experiment 4 E1 Δ −0.005, Experiment 5 unchanged.
- The pipeline default is kept; `run_batch.py --post-ms` was added.

**2. Unannotated records counted as rest.** The 4 records without an activity channel (HC_1_1, HC_38_2, HFC_108_1, HFC_124_1) have mixed-activity windows: 93 rest and 279 20-s windows. Excluding them:
- Experiment 1 and Experiment 2a are unchanged.
- Experiment 3 ρ −0.30 (n 24).
- Experiment 4 E1 Δ +0.004.
- Experiment 5 S-D reliability 0.28 / 0.38.

**3. Post-manoeuvre transients in rest windows.** See the steady-rest result under Experiment 5: reliability rises somewhat, conclusions unchanged.

**4. Ear rebound vs HR.** The effect is confined to windows above 100 bpm, where the next-beat guard shrinks the search span. The 2b text is qualified accordingly.

**5. Transfer-fit window.** It was capped at 640 ms, a deviation from the spec. A refit with the spec window leaves the decisions unchanged.

**6. S1 timing reliability: unresolved.**
- **Against attenuation:** beat-to-beat noise is small (split-half reliability of S1–S2 ≈ 0.94).
- **For attenuation:**
  - Within a record, S1 agrees only weakly between stethoscope and earbuds (rmcorr 0.20–0.28, against 0.63–0.72 for S2).
  - S1 timing doesn't move with HR.
  - A systematic window-to-window shift that is stable within a window wouldn't show up in split-half. An example is the envelope peak switching between the mitral and tricuspid components.
- **Against attenuation:** the earbud is itself noisy, so the weak S1 agreement may be its error.
- If S1 has such error, the S-D on S1–S2 slope (0.37) is a lower bound. The QS2-based S-D slope (0.08–0.18) is unaffected.

**7. Hardcoded limits.**
- The S2 search floor of 220 ms makes S2 unfindable above about 140 bpm (1.3% of windows are above 120 bpm).
- The 35-ms Q-to-R offset in R3 is too short for wide-QRS/CRT patients; R3 is a coarse plausibility check.
- The CNAP notch falls back to the d²P/dt² inflection in 24% of windows, and notch timing is noisy: within-record SD of S2 to notch is 37 ms, against 15 ms for QS2.
- The transfer-fit R² is a squared correlation, so an inverted fit (g < 0) isn't excluded.

**8. "Held out" in 2d means held-out sessions, not subjects.** HC session 2 belongs to the same people as the training session 1. σ_pop is a single scalar at the grid edge (60 ms), so leakage is negligible.
