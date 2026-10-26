# Method and design decisions

This document explains every processing step: what it does, why it was chosen, what it assumes, and how the choice was checked. The ArterioWave papers (Rowland & Weinberg, D-only manuscript; Reavette et al. 2024, AJP-Heart) define the wave model but leave most signal-processing choices open. The decisions below fill those gaps. Unless a step says otherwise, each choice was judged only on **label-blind** criteria: yield, precision, stability and physiology. None was tuned on HF-vs-control labels.

- Numbers quoted as evidence are in [RESULTS.md](RESULTS.md).
- The validation experiments and the audit are in [VALIDATION.md](VALIDATION.md).

## 1. The idea being reproduced

ArterioWave's "D-only" method computes wave intensity from vessel **diameter** alone: dI = dD/dt. From that:
- The **S wave** is the positive peak produced by early ejection.
- The **D wave** is the later negative peak produced by late-systolic deceleration, at end-systole, shortly before aortic valve closure.
- Timing metrics are measured from the ECG R peak: ECG-S, S-D, and SWS = 60·ECG-S / (S-D·HR) (Reavette 2024, Eq. 4).
- Intensity metrics are SWI, DWI and the D/S ratio.

**Our substitution:** PPG stands in for diameter D, so dPPG/dt is the intensity surrogate. Two sites are available in Auricle:
- **ear PPG**: the target, because a wearable ear sensor is the goal;
- **finger PPG**: used only as a *reaction reference*. The finger is more peripheral (longer transit, more reflection, a different vascular bed), so its absolute S-D is not expected to match the ear's. Only *changes* within a recording are compared.

**Central assumption, tested in Experiment 1 and still unconfirmed:** the late-systolic dPPG/dt trough at a peripheral site is the transit-shifted ArterioWave D wave.

## 2. Data (`pwta/io.py`)

- **Dataset:** PhysioNet Auricle 1.0.0: 107 WFDB records, 1 kHz, 42 healthy controls (HC, mostly two sessions on different days) and 28 people with heart failure (HFC, one session).
- **Channels used:** ECG, PPG_Ear, PPG_Finger, Activity_Annotations, CNAP_Annotations. Validation additionally uses Digital_Stethoscope, Earbud_Left/Right and NIBP (continuous CNAP finger pressure).
- **Record list:** taken from `RECORDS`. The `data/` folder also contains a stray copy of HC_20_2 inside HC_19_2, which is ignored.
- **LVEF groups:** HFrEF < 40%, HFmrEF 40–49%, EF ≥ 50%. LVEF is parsed from text such as "25.00%", and "NOT FOUND" becomes missing.
- **Caveats carried through everything:**
  - Controls are young (median 23 vs 56 years).
  - 12 HF participants have AF and 5 have CRT.
  - About 20 records have a flat or unusable ear PPG.
  - 4 records have no activity channel.

## 3. Analysis windows (`pwta/windows.py`)

| decision | value | why / assumption |
|---|---|---|
| Activity | rest (label 0) for most analyses; labels 0–4 for manoeuvre analyses | Rest gives a stable state; the manoeuvres (breath-hold, Valsalva, exercise, cold pressor) give within-person variation |
| Settle time | skip the first 10 s of a segment (60-s windows) or 5 s (20-s windows) | Avoids the transient straight after a manoeuvre. The audit showed that 57% of rest windows still start 10–24 s after a manoeuvre, so `feature_sweep.py` and the steady-rest audit variant use ≥ 25 s |
| Window length | 60 s, keeping a trailing remainder ≥ 30 s; or 20 s, remainder ≥ 15 s | 60 s gives a stable ensemble (median 50–65 accepted beats per ok window); 20 s resolves time courses |
| Unannotated records | HC_1_1, HC_38_2, HFC_108_1, HFC_124_1 are tiled after a 5-min setup and labelled −1 | They would otherwise be lost, but their windows mix activities. All validation conclusions were rerun without them (audit) |

## 4. ECG R peaks: the timing datum (`pwta/ecg.py`)

- **Band-pass:** 1–25 Hz Butterworth, order 2, **zero-phase** (as in Reavette 2024). Zero-phase so the datum isn't delayed.
- **Polarity:** set automatically from the 99.8th vs 0.2th percentile, because lead orientation varies.
- **Detection:** NeuroKit's default detector, then each peak is moved to the band-passed apex within ±40 ms. The R apex, not the QRS onset, is the datum. This adds a roughly constant offset (about 35 ms) relative to ECG-onset-based literature intervals such as QS2.

## 5. PPG conditioning and derivative (`pwta/ppg.py`)

- **Notch:** 60 and 120 Hz notch filters (Q = 30). This assumes 60 Hz mains, as in the code; it is harmless if no hum is present.
- **High-pass:** 0.2 Hz, order 2, zero-phase. It removes respiratory and movement baseline drift while keeping pulse morphology.
- **Derivative:** a zero-phase filter given as a spec string: `raw`, `sg:W:O` (Savitzky-Golay window W ms, order O), `bw:F` (Butterworth low-pass at F Hz + central difference) or `gauss:S`.
  - **Default `sg:61:4`:** chosen from a 15-filter screen and a 29-setting SG grid on label-blind criteria.
  - Auricle's PPG has essentially no content above about 15 Hz, so there is a broad plateau where timing changes by < 1 ms.
  - Under-smoothing (≤ 21 ms) creates spurious troughs; over-smoothing (order 2, ≥ 81 ms) shifts timing and erases small rebounds.
  - For a first derivative, SG orders 2 ≡ 3 and 4 ≡ 5, so orders 2, 4 and 6 cover the space.
- **Flat detection:** a 1-s block with peak-to-peak below 0.01 counts as flat. A window with more than 50% flat blocks is unusable (dead or unplugged sensor).

## 6. Beat ensembles (`pwta/ensemble.py`)

Ensemble averaging of R-locked beats is the method's core. It replaces beat-by-beat fiducials, which are too noisy for PPG.

| decision | value | why / assumption |
|---|---|---|
| Beat span | −100 to +800 ms around R | Covers the systolic upstroke, the D wave and the rebound at normal HR. **Limitation (audit):** at HR < 75 bpm the rebound search span and the pulse-width search are cut by the 800-ms end. Rebound detection is unaffected (12 of 3044 windows change at 1200 ms), but PW50 is censored in slow-HR windows. `run_batch.py --post-ms` exposes the length |
| RR rule | reject a beat if the previous or next RR deviates > 20% from the window median | Removes ectopics, AF irregularity and detection errors. AF records therefore yield fewer windows |
| Clipping | reject a beat if the raw PPG reaches ±9.99 | This is the PPG's output limit |
| Template correlation | reject a beat whose dPPG/dt correlates < 0.8 with the template over 0–600 ms; two passes (median template, then mean of accepted) | Removes motion artefact and misalignment without biasing toward any wave shape |
| PPG polarity | majority vote over the record's windows of the sign of the steepest post-R excursion | Sensor inversion is a property of the placement, not of a window |

## 7. Wave picking and metrics (`pwta/waves.py`)

- **S wave:** the maximum of dPPG/dt between 60 and min(550 ms, 0.8·RR) after R, refined by a parabola to sub-sample precision. It must be positive and interior to the search window.
- **Beat limit:** the region from S to RR + t_S − 150 ms (the next-beat guard). Prominences are measured only within it, so the next beat's upstroke can't masquerade as a rebound.
  - **Limitation (audit):** above about 100 bpm the guard shrinks the rebound search span, which lowers rebound detection there.
- **D wave, rule `rebound_es` (default):** anchored to the dicrotic rebound.
  - The rebound is the dPPG/dt peak 200–550 ms after S with the largest rise (≥ 5% of SWI) from its preceding trough.
  - D is the last trough with prominence ≥ 5% of SWI that lies ≥ 120 ms after S and before the rebound. If there is no rebound, there is no D.
  - **Why:** PPG declines through all of diastole, so the deepest trough is often diastolic. Anchoring to the rebound picks the trough tied to the dicrotic wave. The ≥ 120 ms and ≥ 200 ms limits are an *end-systolic constraint* that excludes mid-systolic dips, such as the spike-and-dome pulse of a participant with hypertrophic cardiomyopathy (HFC_117).
  - **Alternatives compared** (RESULTS: D-wave rule): `window` (the deepest trough 120–400 ms after S), `rebound` (no end-systolic constraint) and `rebound_es+shoulder` (a virtual trough when there is no rebound). The rules agree on 97% of the windows that both accept and differ mainly in *which* windows they accept.
    - `rebound_es` gives the smallest within- and between-subject scatter and the best ear–finger co-movement.
    - The shoulder fallback was rejected because it doubles scatter and loses the systolic HR dependence.
  - **Thresholds:** a 5% prominence threshold; at 10%, S-D changes in 0.2% of windows.
- **Metrics:**

| metric | definition | notes |
|---|---|---|
| `ECG_S_ms` | R to S | Equivalent to a pulse arrival time to max upslope. Contains the PPG device's internal delay: absolute values (~250–300 ms) are not comparable with the carotid ~120 ms |
| `t_D_ms`, `S_D_ms` | R to D, S to D | S-D cancels shared transit and device delay *if* the S and D waves travel the same path |
| `SWS` | 60·ECG-S / (S-D·HR) | Reavette 2024, Eq. 4 |
| `SWI`, `DWI` | dPPG/dt at S, D | PPG gain is arbitrary, so only normalised forms are compared |
| `nSWI`, `nDWI` | SWI or DWI ÷ pulse amplitude (1/s) | Gain-free |
| `DWI_over_SWI` | DWI / SWI | Gain-free D/S intensity ratio |
| `DWE`, `DWI_over_DWE` | area of the negative lobe at D, zero-crossing definition | Often unbounded because diastolic dPPG/dt stays negative; NaN when capped |
| `D_sharpness` | D prominence ÷ prominence-referenced area | Baseline-free D-flattening metric |
| `t_reb_ms`, `reb_rise_frac` | time of the rebound; largest rebound rise ÷ SWI (0 if none) | Continuous rebound strength or flattening index; "rebound present" means ≥ 0.05 |

## 8. Window QC (`pwta/pipeline.py`)

**S-clean windows** feed the S-only features (ECG-S, nSWI, HR, rebound strength). A window is S-clean if:
- the PPG is flat in at most 50% of it;
- at least 10 beats are accepted;
- at least 60% of beats are accepted;
- S is found;
- odd-beat and even-beat ensembles agree on ECG-S within 10 ms.

**Ok windows** feed the D features. A window is ok if it is S-clean, a distinct D is found, and the odd-beat and even-beat ensembles agree on S-D within 15 ms. The split-half check makes each window prove its own precision instead of relying on a global noise model.

## 9. Generic pulse features (`pwta/morphology.py`)

These standard pulse-wave-analysis features make no use of the ArterioWave wave model. They are the comparator for "does PWTA add anything?" (Experiment 4).
- `PAT_foot_ms`: the foot by the intersecting tangent.
- `CT_ms`: crest time.
- `PW50_frac`: pulse width at 50% amplitude ÷ RR.
- `b_over_a`: the SDPPG b/a ratio.

They are computed on the ensemble pulse, so they inherit the 800-ms censoring of PW50 noted in section 6.

## 10. Cardiac timing references (`pwta/reference.py`, validation only)

These use the same R peaks and windows as the PPG pipeline, so the tables join one-to-one on (rid, win_start).
- **Heart sounds** (stethoscope; earbuds as an independent check):
  - 20–200 Hz band-pass, Hilbert envelope, 40 Hz low-pass.
  - Beats whose envelope maximum is > 4× the window median are rejected (speech, movement).
  - S1 = the envelope maximum 0–200 ms after R, which must be an interior peak.
  - S2 = the maximum in [max(S1 + 150, 220), min(0.75·RR, 600)] ms. QS2 = R to S2, marking aortic valve closure.
  - QC: SNR ≥ 2.5 against the diastolic baseline, and odd vs even beats within 10 ms.
  - **Limits:** S2 can't be found above about 140 bpm (the 220-ms floor). Within-record S1 timing is of uncertain validity (audit).
- **CNAP finger pressure:**
  - Only beats fully inside CNAP-valid samples are used. A record with no CNAP annotation channel is excluded.
  - Foot by the intersecting tangent; dicrotic notch = the first pressure minimum with prominence ≥ 0.5 mmHg, otherwise the d²P/dt² inflection; ET = notch − foot.
  - MAP is taken over one full cycle (a 1700-ms segment).
  - **Result:** CNAP ET did not behave like LVET. It doesn't shorten with HR, and the S2-to-notch delay varies by 37 ms within a record. It was not usable as a reference.
- **SCG (accelerometer) not used:** the sensor axis orientation is undocumented, and the AO/AC points would themselves need validation.

## 11. Statistics conventions (`scripts/vstats.py` and the analysis scripts)

- **Repeated measures are never treated as independent.**
  - Window medians are aggregated to a record (session), then sessions to a subject mean, for subject-level tests.
  - HC sessions on different days are pairs, and manoeuvre repetitions are trials within a session.
- **Within-record relations:** pooled slopes after demeaning per record (optionally residualised on HR). Repeated-measures correlation is the Pearson r of the record-demeaned values. 95% CIs come from a **cluster bootstrap over subjects**, 2000 replicates.
- **Reliability:** ICC(2,1) between days; variance components (window, day, subject) for reliability as a function of the number of windows and days (Experiment 5).
- **Classification:** subject-level, repeated stratified 5-fold CV logistic regression (L2) with median imputation and scaling *inside folds*.
  - Incremental value is tested with a Freedman–Lane permutation null, which permutes only the part of the added block that the base model doesn't explain.
  - The HF-vs-control age-overlap subset is 28–57 years. The upper bound is the oldest control. The lower bound of 28 is a fixed cut, set in `classify_hf.py` before the validation and not tuned on outcomes, that removes the bulk of the young controls (median 23). That leaves 13 HC and 15 HF.
- **Multiplicity:** primary tests were pre-registered in VALIDATION.md, and secondary families are Holm-corrected. Anything not pre-registered is labelled post hoc.
