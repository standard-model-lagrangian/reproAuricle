# reproAuricle: D-only wave timing (ArterioWave PWTA) on ear and finger PPG

This repo reproduces the ArterioWave **"D-only" Pseudo Wave Timing Analysis** (Rowland & Weinberg, D-only manuscript; Reavette et al. 2024, *AJP-Heart*) on the PhysioNet **Auricle** dataset. It asks whether the method's wave-timing metrics can be extracted from a wearable **ear PPG** + ECG, and whether they carry diagnostic information about heart failure. PPG stands in for vessel diameter, so dPPG/dt is the wave-intensity surrogate:
- the **S wave** is its early-systolic peak;
- the **D wave** is its late-systolic trough;
- the ECG R peak is the timing datum.

The finger PPG recorded alongside the ear serves as a reference.

## Findings

| question | answer | where |
|---|---|---|
| Can the metrics be extracted from the ear? | **The S-wave metrics, yes** (ECG-S, SWS: sub-millisecond precision, and more repeatable between days at the ear than at the finger). **The D wave, mostly not where it matters:** found in about half of control windows but rarely in HF (5 HFrEF participants usable). | [RESULTS §2](docs/RESULTS.md) |
| Why does the ear lose the D wave? | **The site's haemodynamics, not the sensor.** 99% of ear–finger disagreements are "finger has a dicrotic rebound, ear doesn't". The rebound is more common in taller people and rarer at higher blood pressure. Ordinary filter choices barely matter. A fitted inverse filter (deconvolution) recovers some ear D waves, but fragilely. | [VALIDATION Exp 2](docs/VALIDATION.md) |
| Is the PPG "D" the ArterioWave end-systolic wave? | **Unconfirmed.** It is a systolic-phase event and not tied to diastole. Against the heart-sound S2 its timing moves mostly in common with the S wave, and S-D moves little with S2 (slopes 0.08–0.18). The pressure (CNAP) reference failed. | [VALIDATION Exp 1](docs/VALIDATION.md) |
| Diagnostic value for HF? | **Nothing beyond generic pulse shape.** The finger's HF discrimination (AUROC 0.93 in the age-overlap subset, 28–57 years) comes from standard pulse features; the D-wave features add −0.005. The ear features carry no signal. | [VALIDATION Exp 4](docs/VALIDATION.md) |
| Is a missing rebound ("D-wave flattening") a signal? | **Weak.** ρ = −0.28 with LVEF (p = 0.09), concentrated in the 8 participants with EF ≥ 50%. | [VALIDATION Exp 3](docs/VALIDATION.md) |
| Can Auricle settle these questions? | **No.** S-D varies more from day to day than it differs between healthy people (one-session reliability 0.31–0.40). Detecting a true ρ = 0.5 between S-D and LVEF needs about 50 (ear) to 84 (finger) HF participants with a usable S-D; Auricle has 10 and 22, so its power is 19–27%. | [VALIDATION Exp 5](docs/VALIDATION.md) |

**In short:** the PPG translation of ArterioWave does not hold up on Auricle. This is not a test of the method on its native modality (carotid ultrasound). Auricle is also too small to show diagnostic value in either direction.

All validation experiments were **pre-registered** (spec and decision rules frozen before running), then **audited** by an independent code review and empirical checks. The audit fixed 7 issues and documented 8; no verdict changed ([VALIDATION § Audit](docs/VALIDATION.md#audit)).

## Reproduce

Needs Python ≥ 3.12 (tested on 3.13 and 3.15), about 15 GB for the dataset and 150 MB for the full outputs.

```bash
git clone https://github.com/standard-model-lagrangian/reproAuricle && cd reproAuricle
python3 -m venv .venv-pwta && .venv-pwta/bin/pip install -r requirements.txt
# dataset: see data/README.md (PhysioNet Auricle 1.0.0, open access), or set AURICLE_ROOT=/path/to/it
.venv-pwta/bin/python scripts/check_setup.py   # checks packages and that all 107 records are present
./reproduce.sh --help                          # stages, timings, environment variables
```

To check the committed results, regenerate into a separate folder and compare:

```bash
OUT=outputs_check ./reproduce.sh               # everything, ~30 min on 6 cores (JOBS=... to change)
.venv-pwta/bin/python scripts/compare_outputs.py outputs outputs_check
```

A single stage is enough for a quick check: `OUT=outputs_check ./reproduce.sh core` takes about a minute. Stages that build on earlier ones stop with a message if their inputs are missing. Running `./reproduce.sh` without `OUT` overwrites the committed `outputs/`.

Everything is deterministic: fixed seeds and no randomness in signal processing. The committed `outputs/` come from a clean run, and a second full run from raw data (`OUT=… ./reproduce.sh`, then `compare_outputs.py`) reproduced all 179 compared tables identically. Results were also identical under Python 3.13 (stage `core`) and under pandas 3.1.

## How it fits together

```
raw WFDB records (1 kHz) ─▶ pwta/io.py ─▶ windows.py (rest / manoeuvre windows)
   ECG ─▶ ecg.py (R peaks = timing datum)
   PPG ─▶ ppg.py (notch, high-pass, zero-phase derivative) ─▶ ensemble.py (R-locked beats, rejection, averaging)
       ─▶ waves.py (S, rebound, D; metrics) + morphology.py (generic pulse features) ─▶ pipeline.py (QC) ─▶ one row per window
   PCG / earbuds / CNAP ─▶ reference.py (S1, S2, CNAP foot/notch; validation only) ─▶ one row per window
per-window tables ─▶ scripts/* (aggregation to record → subject, statistics) ─▶ outputs/**/*.csv, *.md, *.png
```

| stage | scripts | outputs | documented in |
|---|---|---|---|
| `core` | `run_batch.py`, `summarise.py`, `plot_record.py` | `outputs/windows_rest.csv`, `summary/`, `sensitivity/`, `plots/` | RESULTS §2, §5 |
| `filters` | `run_batch.py --specs …`, `screen_filters.py` | `screen/`, `sg_grid/` | METHOD §5, RESULTS §1 |
| `drules` | `run_batch.py --d-rule …`, `compare_d_rules.py` | `drules/` | METHOD §7, RESULTS §1 |
| `stratified` | `stratified_checks.py` | `timecourse/`, `stratified/` | RESULTS §3 |
| `hf` | `classify_hf.py` | `hf_classification/` | RESULTS §4 |
| `sweep` | `feature_sweep.py` | `sweep/` | RESULTS §6 |
| `agreement` | `site_agreement.py` | `site_agreement/` | RESULTS §7 |
| `validation` | `run_batch.py`, `run_reference.py`, `validate_construct.py`, `validate_site_rebound.py`, `validate_flattening.py`, `validate_incremental.py`, `validate_precision.py` (+ `vstats.py`) | `validation/exp1…exp5/` | VALIDATION |
| `audit` | `run_batch.py --post-ms 1200`, `audit_checks.py` (+ reruns of Exp 3–5 on window variants) | `validation/audit/` | VALIDATION § Audit |

## Repository layout

```
pwta/                 signal-processing package (each module documents its choices; see docs/METHOD.md)
scripts/              one script per analysis; each has a docstring with purpose, inputs and usage
  check_setup.py      preflight: Python, pinned packages, dataset present (reproduce.sh runs it first)
  compare_outputs.py  diff a regenerated output folder against the committed outputs/
docs/METHOD.md        every processing step: what, why, assumptions, how it was checked
docs/RESULTS.md       reproduction results (extraction, reliability, rules/filters, HF, sweep, site agreement)
docs/VALIDATION.md    pre-registered validation experiments 1–5, results, and the audit
outputs/              committed result tables (.csv/.md) and figures; large per-window tables are regenerated
data/README.md        how to obtain the dataset
reproduce.sh          runs every stage in order
```

**Conventions worth knowing before reading results:**
- A window is **ok** if it passes the full QC: S and D found, and split-half stable. D is anchored to a dicrotic rebound of at least 5% of the S-wave intensity (METHOD §7–8).
- A window is **S-clean** if it passes the QC without the D requirements; S-only features use these windows.
- Repeated measures are never pooled as independent: windows go to records, records to subjects.
- HC participants have two sessions on different days; HF participants have one.
- Four records have no activity channel; their windows (label −1) mix activities but are kept in the rest analyses. Dropping them changes no conclusion (VALIDATION, Audit item 2).
- Controls are much younger than HF participants, so HF-vs-control contrasts are confounded by age (and by AF, CRT and medication). See METHOD §2 and §11.

## Attribution

- **Data:** Auricle: A Multimodal Wearable Sensing Dataset for Cardiovascular and Hemodynamic Assessment, v1.0.0, PhysioNet, https://doi.org/10.13026/swme-vp69 (ODC-By). Please cite the dataset and PhysioNet (Goldberger et al., 2000) when using these results.
- **Method:** Reavette R.M. et al. (2024), *American Journal of Physiology-Heart and Circulatory Physiology*; Rowland & Weinberg, D-only (ArterioWave) manuscript.
