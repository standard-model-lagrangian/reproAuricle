"""Cardiac timing references (heart sounds, CNAP) for the same windows run_batch.py analyses.

R peaks and windows are identical to the PPG pipeline (same detector and window settings), so the
output joins to run_batch.py output on (rid, win_start). See pwta/reference.py and docs/VALIDATION.md.

Usage:
  python scripts/run_reference.py --out outputs/validation/reference_rest.csv
  python scripts/run_reference.py --labels 0 1 2 3 4 --window-s 20 --min-window-s 15 --settle-s 5 \
      --out outputs/validation/reference_all_20s.csv
"""
import argparse
import os
import sys
import time
import traceback

import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pwta import ecg, io, reference  # noqa: E402
from pwta.pipeline import Config  # noqa: E402
from pwta.windows import make_windows  # noqa: E402

SOUNDS = {"Digital_Stethoscope": "pcg_", "Earbud_Left": "ebL_", "Earbud_Right": "ebR_"}


def process(rid, cfg):
    rec = io.load_record(rid, channels=("ECG", "NIBP") + tuple(SOUNDS))
    fs = rec.fs
    r_peaks, _ = ecg.detect_r_peaks(rec.signals["ECG"], fs)
    wins = make_windows(rec.activity, fs, cfg.window_s, cfg.min_window_s, cfg.settle_s, cfg.labels)
    env = {ch: reference.sound_envelope(rec.signals[ch], fs) for ch in SOUNDS if ch in rec.signals}
    rows = []
    for w in wins:
        beats, rr_ms = reference.window_beats(r_peaks, w.start, w.stop, rec.n, fs, cfg.rr_tol)
        row = dict(rid=rid, win_start=w.start, label=w.label, n_beats=len(beats), RR_ms=rr_ms)
        for ch, prefix in SOUNDS.items():
            if ch in env:
                row.update(reference.heart_sounds(env[ch], beats, rr_ms, fs, prefix))
        if "NIBP" in rec.signals:
            row.update(reference.cnap(rec.signals["NIBP"], rec.cnap_valid, beats, rr_ms, fs))
        rows.append(row)
    return rows


def _one(rid, cfg):
    try:
        return process(rid, cfg), None
    except Exception:
        return [], (rid, traceback.format_exc())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", nargs="+", type=int, default=[0])
    ap.add_argument("--window-s", type=float, default=Config.window_s)
    ap.add_argument("--min-window-s", type=float, default=Config.min_window_s)
    ap.add_argument("--settle-s", type=float, default=Config.settle_s)
    ap.add_argument("--records", nargs="*")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = Config(labels=tuple(a.labels), window_s=a.window_s, min_window_s=a.min_window_s, settle_s=a.settle_s)
    rids = a.records or io.list_records()
    t0 = time.time()
    res = Parallel(n_jobs=a.jobs, verbose=5)(delayed(_one)(rid, cfg) for rid in rids)
    df = pd.DataFrame([r for rows, _ in res for r in rows])
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    df.to_csv(a.out, index=False)
    print(f"{len(df)} windows from {len(rids)} records in {time.time() - t0:.0f}s -> {a.out}")
    failures = [f for _, f in res if f]
    for rid, tb in failures:
        print(f"FAILED {rid}:\n{tb}")
    if failures:  # the table is written, but downstream stages should not run on a partial table
        sys.exit(f"{len(failures)} record(s) failed")


if __name__ == "__main__":
    main()
