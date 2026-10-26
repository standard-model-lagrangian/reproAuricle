"""Run the PWTA pipeline over all Auricle records in parallel and write one row per window.

Usage:
  python scripts/run_batch.py --out outputs/windows.csv
  python scripts/run_batch.py --specs raw sg:21:2 bw:15 --channels PPG_Ear PPG_Finger --out outputs/screen.csv
"""
import argparse
import json
import os
import sys
import time
import traceback

import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pwta import io  # noqa: E402
from pwta.pipeline import Config, config_dict, process_record  # noqa: E402


def _one(rid, specs, channels, cfg):
    try:
        rows, _ = process_record(rid, specs=specs, channels=channels, cfg=cfg)
        return rows, None
    except Exception:  # keep the batch going; report failures at the end
        return [], (rid, traceback.format_exc())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", nargs="+", default=["sg:61:4"])
    ap.add_argument("--channels", nargs="+", default=["PPG_Ear", "PPG_Finger"])
    ap.add_argument("--labels", nargs="+", type=int, default=[0])
    ap.add_argument("--records", nargs="*", help="subset of record ids (default: all in RECORDS)")
    ap.add_argument("--d-window", nargs=2, type=float, default=list(Config.d_window_ms),
                    help="D-wave search window after S (ms)")
    ap.add_argument("--d-prom", type=float, default=Config.d_min_prom_frac,
                    help="min D prominence as a fraction of SWI")
    ap.add_argument("--d-rule", default=Config.d_rule,
                    choices=["window", "rebound", "rebound_es", "rebound_es+shoulder"])
    ap.add_argument("--window-s", type=float, default=Config.window_s)
    ap.add_argument("--min-window-s", type=float, default=Config.min_window_s)
    ap.add_argument("--settle-s", type=float, default=Config.settle_s)
    ap.add_argument("--post-ms", type=float, default=Config.post_ms, help="ensemble length after R (ms)")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cfg = Config(labels=tuple(a.labels), window_s=a.window_s, min_window_s=a.min_window_s, settle_s=a.settle_s,
                 d_window_ms=tuple(a.d_window), d_min_prom_frac=a.d_prom, d_rule=a.d_rule, post_ms=a.post_ms)
    rids = a.records or io.list_records()
    t0 = time.time()
    results = Parallel(n_jobs=a.jobs, verbose=5)(
        delayed(_one)(rid, tuple(a.specs), tuple(a.channels), cfg) for rid in rids)
    rows = [r for res, _ in results for r in res]
    failures = [f for _, f in results if f]

    df = pd.DataFrame(rows)
    demo = io.load_demographics()
    df = df.merge(demo[["Age", "Gender", "LVEF", "group"]], left_on="subject", right_index=True, how="left")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    df.to_csv(a.out, index=False)
    with open(os.path.splitext(a.out)[0] + "_config.json", "w") as f:
        json.dump({"config": config_dict(cfg), "specs": a.specs, "channels": a.channels,
                   "n_records": len(rids), "failures": failures}, f, indent=2)
    print(f"{len(df)} window rows from {len(rids)} records in {time.time() - t0:.0f}s -> {a.out}")
    for rid, tb in failures:
        print(f"FAILED {rid}:\n{tb}")


if __name__ == "__main__":
    main()
