# Results

These are the results of reproducing D-only PWTA on Auricle, before the validation experiments. Every number regenerates with `./reproduce.sh` (stages `core`, `filters`, `drules`, `stratified`, `hf`, `sweep` and `agreement`). How each step works and why is in [METHOD.md](METHOD.md); the validation experiments and the audit are in [VALIDATION.md](VALIDATION.md).

Defaults throughout: derivative `sg:61:4`, D rule `rebound_es`, 60-s rest windows (unless a section says 20-s), and window QC as in METHOD §8.

> **Read with the validation.** Several readings here were later qualified (VALIDATION.md):
> - The finger's HF signal is generic pulse shape, not D-wave timing.
> - Whether the PPG "D" is the end-systolic wave is unconfirmed.
> - Auricle is underpowered for associations with LVEF.

## 1. Evidence for the design choices not specified by the manuscripts

- **Savitzky-Golay parameters.** Screened 15 zero-phase derivative filters against a minimally smoothed reference (`bw:40`).
  - Auricle's PPG has essentially no content above ~15 Hz, so the choice barely matters for timing. At the ear, sg:61:4, sg:41:4, bw:15 and bw:20 all move median ECG-S and S-D by ≤ 0.25 ms, and all give 49–51% ok windows.
  - No smoothing (`raw`) loses almost every ear window: 4% ok, against 51% for sg:61:4. Its split-half precision is 2–3.5× worse.
  - Wide order-2 SG (`sg:101:2`), `gauss:20` and `bw:10` shift ECG-S by 1.5–2.9 ms and shrink nSWI by up to 10% (ear) and 19% (finger).
  - *These numbers come from the screen rerun under the current `rebound_es` D rule (`outputs/screen/`). An earlier screen under the old `window` rule gave the same ranking.*
  - Default is `sg:61:4`; `bw:20` is an equivalent alternative.
  - **Full SG grid** (window 11–151 ms × order 2/4/6, with the `rebound_es` D rule; `outputs/sg_grid/`). For a first derivative, SG orders 2≡3 and 4≡5, so these orders cover the space. The grid was scored only on label-blind criteria.
    - There is a broad plateau: order 2 at 31–61 ms, order 4 at 41–151 ms and order 6 at 61–151 ms all give about the same result. On the ear, that is 49–51% of windows ok, bias under 1 ms, within-session S-D SD of about 6.2 ms, between-subject SD of 20–22 ms, no S-D outside 100–350 ms, and an S-D/HR slope of −0.5 to −0.7 ms/bpm.
    - **Under-smoothing** (11–21 ms, or order 6 below 51 ms) creates spurious troughs. Between-subject S-D SD blows up to 40–51 ms and split-half precision degrades 2–3×.
    - **Over-smoothing** (order 2 at 81 ms or more) shifts ECG-S by 2–5 ms and S-D by up to 14 ms at the finger. It shrinks nSWI by 10–35% and erases small rebounds: the ear windows without a D wave rise from 40% to 63%.
    - No setting recovers a D wave in the roughly 40% of ear windows that lack a rebound; the best gives 38%.
- **D-wave rule.** Four rules were compared (`scripts/compare_d_rules.py`, `outputs/drules/`).
  - There is no ground truth, and ear and finger are **not expected to give the same S-D**: the finger is much more peripheral (longer transit, more reflection, a different vascular bed). So rules are judged on criteria intrinsic to the ear.
  - The finger serves only as a **reaction reference**: do within-recording *changes* in S-D move together at both sites?

  | rule (ear PPG) | windows ok | split-half S-D | within-session SD of S-D | between-subject SD of S-D | S-D vs HR slope (ms/bpm) | ICC S-D / SWS | ear–finger change ρ | exercise ΔS-D same sign |
  |---|---|---|---|---|---|---|---|---|
  | `window`: deepest distinct trough 120–400 ms after S | 73% | 1.3 ms | 8.8 ms | 59 ms | −0.60 | 0.41 / 0.83 | 0.33 | 69% |
  | `rebound`: trough before the largest rebound 150–550 ms after S | 51% | 1.0 ms | 6.2 ms | 25 ms | −0.59 | 0.34 / 0.80 | 0.32 | 68% |
  | **`rebound_es`**: the same, rebound ≥ 200 ms and D ≥ 120 ms after S (end-systolic constraint) | 51% | 1.0 ms | **6.3 ms** | **21 ms** | −0.59 | 0.34 / 0.80 | **0.53** | **82%** |
  | `rebound_es+shoulder`: the same, but if there is no rebound, D = local max of d²PPG/dt² (a "virtual trough") | 65% | 1.3 ms | 10.7 ms | 44 ms | −0.03 | 0.42 / 0.78 | 0.39 | 78% |

  - **On windows that both `window` and `rebound_es` accept, they pick the same trough in 97% of ear windows** (95% finger). The rules differ almost only in *which windows they accept*.
  - The 375 extra ear windows that only `window` accepts are pulses without a dicrotic rebound. Their S-D is long and scattered (median 251 ms, IQR 221–338 ms), and they cause `window`'s larger within-session and between-subject spread.
  - `rebound_es` is the default. It rejects pulses with no identifiable end-systolic D wave rather than guessing, and the D it does report is stable within a session and moves with the finger.
  - `rebound` without the end-systolic constraint picks mid-systolic dips, for example the spike-and-dome pulse of HFC_117, who has hypertrophic cardiomyopathy.
  - The **shoulder fallback is rejected**: it doubles within-session S-D variability and its S-D no longer shortens with HR.
  - **S-D vs HR.** All trough-based rules give about −0.6 ms/bpm within a recording: systolic-like, nowhere near the roughly −12 ms/bpm of a diastole-locked feature. That is smaller than LVET's −1.7 ms/bpm, though rest-window HR ranges are narrow. This criterion rules out the shoulder rule but doesn't separate the trough rules.
  - **ICC is not a validity measure here.** A wrong pick that recurs every day is also repeatable. On the same 22 ear subjects `window` has the higher S-D ICC (0.60 vs 0.34), so between-day ear S-D repeatability is limited either way.
- **Prominence threshold.** Raising the rebound/trough threshold from 5% to 10% of SWI drops yield from 61% to 56% and changes S-D in 0.2% of windows. (The 120–400 ms `--d-window` only applies to the `window` rule.)

## 2. Reproduction results (rest windows, `sg:61:4`, D rule `rebound_es`): `outputs/summary/`

| | ear PPG | finger PPG |
|---|---|---|
| records with ≥ 1 ok window (HC / HFC) | 54/77 · 10/27 | 75/77 · 23/27 |
| windows ok (HC / HFC) | 51% · 22% | 85% · 58% |
| split-half median \|Δ\| ECG-S / S-D / SWS | 0.4 ms / 1.0 ms / 0.006 | 0.4 ms / 1.0 ms / 0.007 |
| within-session SD vs between-record SD, ECG-S | 7 vs 43 ms | 9 vs 28 ms |
| within-session SD vs between-record SD, S-D | 6 vs 21 ms | 9 vs 28 ms |
| between-day ICC(2,1), healthy cohort: ECG-S / S-D / SWS / DWI/SWI / D sharpness | 0.86 / 0.34 / 0.80 / 0.75 / 0.08 (n=22) | 0.70 / 0.36 / 0.56 / 0.82 / 0.46 (n=33) |
| ear vs finger S-D, same window (reference only; the sites are not expected to match) | finger − ear = −14 ± 25 ms; within-recording changes ρ = 0.53 | |

- **S wave / ECG-S: reliably extractable.** It is sub-millisecond within a window and repeatable between days, especially at the ear.
- **D wave: extractable only when the pulse has a dicrotic rebound.**
  - When it has one, D is precise within a window, stable within a session, and moves with the finger's D within a recording.
  - Between-day S-D repeatability is still low (ICC about 0.35). Within-session SD is 6–9 ms against a between-subject SD of only 21–28 ms, so day-to-day physiological change is comparable to the spread between subjects.
  - Many ear pulses (about 40% of windows even in controls) are smooth with no rebound. These are rejected, which costs most of the HF ear data: only 5 HFrEF participants have usable ear D.
  - On the **finger**, a missing rebound looks informative. It occurs in 2% of control windows, 19% of HFrEF and 49% of EF ≥ 50%. That may be the D-wave flattening the trial proposal links to HFpEF, but it is exploratory (n = 8 for EF ≥ 50%, and not age-matched).
- **Exercise recovery (cf. Fig. S8).** About 10 s after light exercise, at both sites:
  - ECG-S **shortens** by about 22 ms in 98–100% of pairs.
  - S-D lengthens by 7–12 ms.
  - HR rises by 4–5 bpm.

  Fig. S8 reported a *delayed* S wave during recovery from exercise, but its protocol and timing differ. The metrics respond consistently, but the direction does not replicate.
- **Exploratory only** (controls are young volunteers, not age-matched):
  - Finger, HFrEF vs control (n = 12 vs 42): SWS AUROC 0.84, ECG-S 0.77, DWI/SWI fully separated (HFrEF relatively larger D).
  - Ear: too few HFrEF participants (5) to say anything.

## 3. Stratified checks: sessions, CNAP mask, rebound, exercise (`scripts/stratified_checks.py`, `outputs/stratified/`)

Design: HC participants were recorded on two different days, HFC participants once. Sessions and exercise bouts of one person are repeated measures, so every test below uses one value per subject. (The pair-level `exercise_effect` table in `outputs/summary/` pseudo-replicates and is superseded by this section.)

- **CNAP mask** (`CNAP_Annotations`: 0 = uncalibrated, calibration or artefact; about 4.5 s every 39 s plus the setup minutes). It is now carried in the window output as `cnap_invalid_frac`. It has no detectable effect on ECG-S, S-D, SWS, rebound presence or the exercise shifts. Finger window yield is lower in heavily masked windows (46% vs 79%), but only 9–12 records have such rest windows. Any NIBP/CNAP analysis must apply the mask.
- **HC day 1 vs day 2 vs averaged** makes no material difference to HF-vs-control AUROCs: finger CV model 0.93 / 0.95 / 0.95, age alone 0.90.
- **Rebound ("notch") presence**, the fraction of S-clean windows with a derivative turning point before a rebound:

  | | ear | finger |
  |---|---|---|
  | HC, day 1 / day 2 (median) | 0.88 / 0.82 | 1.00 / 1.00 |
  | HFC (median); HFrEF / EF ≥ 50% (mean) | 0.25; 0.37 / 0.26 | 1.00; 0.81 / 0.51 |
  | day-1 vs day-2 Spearman (HC) | 0.60 | 0.35 (ceiling) |
  | pre → ≈5–25 s after exercise (HC day 1 / day 2 / HFC) | 0.66→0.45 / 0.46→0.23 / 0.46→0.18 | 1.00→0.88 / 0.96→0.91 / 0.96→0.75 |

  Rebound presence is partly a trait of the person and site, and partly a state: it disappears at higher heart rate after exercise, exactly when the exercise test needs the D wave.
- **Post-exercise shift (cf. D-only manuscript Fig. S8; 20-s windows, change from the last pre-exercise rest window, subject medians):**
  - **ECG-S shortens at both sites, on both days, in HC.** It falls by about 30–36 ms at 5–25 s and recovers to −8 to −11 ms by 2–4 min, without ever becoming a delay. 94–100% of HC subjects show the same sign on both days, though the size of the shift correlates only weakly between days (ρ 0.3–0.4). HFC subjects show a smaller shortening that has gone by 2–4 min.
  - **R-to-D time shortens less than ECG-S, so S-D lengthens** (ear HC day 1: +10 to +15 ms).
  - Fig. S8 reports the opposite direction (S *delayed*, D delayed less) in one subject after a different exercise, at an unstated recovery time; its cited mechanism (Chan-Dewar 2013) concerns recovery from a 40 km ride. Auricle's 1–2 min light exercise and 5–245 s recovery show the expected sympathetic shortening instead. The PoC direction is not reproduced under these conditions, which is not a refutation.
  - The ECG-S shift is the same whether or not a rebound is present (−26 ms in both), so it doesn't depend on the D wave. Ear D-timing shifts are testable in only 4–15 HC subjects per bin.

## 4. HF vs no-HF discrimination (`scripts/classify_hf.py`, `outputs/hf_classification/`)

The comparison is subject level: 27 HFC vs 42 HC. Age alone gives AUROC 0.91, because the controls are much younger (median 23 vs 56 years), so the age-overlap subset (28–57 years, 15 HF vs 13 HC) is the fairer test.

| | all subjects | age 28–57 subset |
|---|---|---|
| age only (CV) | 0.90 | 0.61 |
| finger, pre-specified PWTA features (ECG-S, SWS, S-D, nSWI, D sharpness, no-rebound fraction), CV logistic | **0.95** | **0.88** |
| ear, same features, CV logistic | 0.45 | 0.52 |
| finger SWS alone (univariate) | 0.76 | 0.73 |
| finger DWI/SWI alone (direction chosen post hoc: HF has a relatively larger D wave) | 0.98 | 0.96 |
| finger, all 8 features including DWI/SWI (post hoc), CV | 0.99 | 0.94 |

- **The signal is at the finger, not the ear.** The finger features most likely reflect peripheral arterial ageing and stiffness, plus HF medication (beta-blockers, vasodilators), rather than the central S/D wave timing the method targets.
- **Finger SWS loses most of its signal within males** (AUROC 0.61).
- **In the carotid data, the D/S intensity ratio did not differ between groups** (Table 1).
- These are not estimates of screening performance.
- **Age-robust check (`age_robust_checks.csv`).** Within the HF cohort, age and LVEF are nearly unrelated (ρ = −0.17), so feature–LVEF associations there are not age-driven.
  - Finger S-D shortens with falling LVEF: ρ = 0.58, p = 0.004, n = 22; age-adjusted 0.71. This matches the carotid finding (S-D shorter in HFrEF).
  - Finger SWS rises with falling LVEF: ρ = −0.36, p = 0.10.
  - Ear D sharpness: ρ = 0.63, n = 10.
  - ECG-S shows no LVEF association at either site.

  These are 14 exploratory tests, so treat them as hypothesis-generating.

## 5. Known dataset issues

- Ear PPG is flat or unusable in 20 recordings (`outputs/summary/records_without_ok_ear_window.csv`), 9 of them HFC.
- HC_21_1, HC_27_2 and HFC_141_1 have no rest labels, only exercise and not-applicable, so they produce no windows.
- HC_1_1, HC_38_2, HFC_108_1 and HFC_124_1 have no activity channel. Their windows mix activities (label −1).
- The absolute ECG-S at the ear is about 250–300 ms, against about 120 ms at the carotid. The earlobe adds only about 20 ms of transit time, so most of the gap is probably the PPG device's internal filtering plus Auricle's 10 kHz → 1 kHz resampling. That offset enters ECG-S and therefore SWS, so absolute values are not comparable with the paper.
- Many HF participants have AF (12) or CRT (5). AF beats fail the RR check, so those records yield fewer windows.

## 6. D-only feature sweep: D-only metrics × site × stratum × manoeuvre (`scripts/feature_sweep.py`, `outputs/sweep/`)

```bash
.venv-pwta/bin/python scripts/run_batch.py --labels 0 1 2 3 4 --window-s 20 --min-window-s 15 --settle-s 5 --out outputs/sweep/windows_all_20s.csv
.venv-pwta/bin/python scripts/feature_sweep.py outputs/sweep/windows_all_20s.csv
```

This covers only the ArterioWave D-only metrics: ECG-S, R-D, S-D, SWS, nSWI, nDWI, DWI/SWI and DWI/DWE.
- A feature is extractable in a window when its wave passes QC: S-clean for ECG-S and nSWI, `ok` for the D metrics, and additionally a bounded D lobe for DWI/DWE.
- Rest reliability uses steady rest only (≥ 25 s after a manoeuvre).
- Each manoeuvre repetition (4× breath-hold, 4× Valsalva, 2× exercise, 1× cold pressor) is a trial. Its shift is the manoeuvre window (5–25 s into it) or the first post window (5–25 s after it), minus the last extractable rest window before it.
- The detection threshold is MDC95 = 1.96 × SD of changes between rest windows 20–40 s apart in the same rest segment.
- The outputs are `yield_by_activity`, `rest_reliability`, `rest_icc_between_days`, `rest_noise_mdc`, `shift_summary` (per-trial measurability, % above MDC, subject-median shift, sign consistency across repetitions), `shift_day_reproducibility` and `trials.csv`.

## 7. Ear vs finger agreement by level (`scripts/site_agreement.py`, `outputs/site_agreement/`)

```bash
.venv-pwta/bin/python scripts/site_agreement.py outputs/windows_rest.csv outputs/sweep/windows_all_20s.csv
```

Only windows where a feature is extractable at both sites are paired (the `feature_sweep.py` masks). Each input becomes one table, broken down by level:
- interval: raw paired windows.
- within-session: deviations from the record mean, plus the median per-record ρ.
- session: record medians.
- subject: the mean of a subject's sessions.
- day change: HC day 2 − day 1.

Rest, 60-s windows (`windows_rest.csv`), Spearman ρ, with Lin's CCC where it is shown:

| metric | interval | within-session (median per record) | session ρ / CCC | subject ρ / CCC | day change ρ (same sign) | finger − ear, session level |
|---|---|---|---|---|---|---|
| ECG-S | 0.55 | 0.66 (0.71) | 0.57 / 0.50 | 0.51 / 0.41 | 0.67 (66%) | +8 ± 36 ms |
| S-D | 0.71 | 0.53 (0.72) | 0.75 / 0.44 | 0.77 / 0.48 | 0.37 (59%) | −12 ± 31 ms |
| SWS | 0.66 | 0.57 (0.76) | 0.71 / 0.57 | 0.76 / 0.66 | 0.35 (68%) | +0.17 ± 0.23 |
| R-D | 0.44 | 0.45 (0.61) | 0.51 / 0.44 | 0.56 / 0.41 | 0.52 (73%) | +9 ± 47 ms |
| nSWI, nDWI, DWI/SWI | 0.15–0.38 | 0.25–0.33 | 0.20–0.29 / ≤ 0.24 | 0.26–0.30 / ≤ 0.32 | ≤ 0.25 (≤ 45%) | |

- **The timing metrics rank people similarly at both sites (ρ ≈ 0.5–0.77), but absolute values don't transfer.** The session-level SD of finger − ear (31 ms for S-D, 36 ms for ECG-S) is as large as the between-subject spread.
- **Within a session the sites move together only moderately.** ECG-S tracks best, with equal SDs at both sites. Finger S-D and R-D vary about 1.7× as much as the ear's, so the slope of finger on ear is about 0.5. Some of the ECG-S co-movement comes from the shared R peak and HR rather than independent confirmation.
- **The amplitude metrics are site-specific at every level**, consistent with the finger-only DWI/SWI signal in the HF classification.
- **With manoeuvres included** (`windows_all_20s.csv`), the wider range raises within-session ρ: ECG-S 0.74, S-D 0.57, SWS 0.66, with medians per record of 0.72 / 0.77 / 0.83. The day change in S-D agrees at ρ 0.71, with 79% the same sign.
- **The S-D CCC is sensitive to the 4 records without an activity channel**, whose windows mix activities. Excluding them raises the rest session/subject CCC from 0.44 / 0.48 to 0.55 / 0.72.
- DWI/DWE has too few windows bounded at both sites to interpret (n = 7 records at rest).
