"""Compare derivative filters on the output of run_batch.py.

There is no ground truth for PPG wave timing, so filters are judged on:
  yield      fraction of windows passing all quality checks
  bias       median difference from the reference filter (minimal smoothing) on windows that
             are ok under both, i.e. how much the filter moves turning points / changes ratios
  spread95   95th percentile of |difference| from the reference
  split-half median |odd-beat - even-beat| difference (precision within a window), on the
             windows ok under *every* filter so all filters are scored on the same data
  within-rec median over records of the SD across that record's rest windows (noise + physiology)
  physiology label-blind sanity checks on the ok windows: between-subject SD of record-median S-D,
             fraction of S-D outside 100-350 ms, fraction of S-clean windows with no dicrotic
             rebound (no D wave), and the within-recording S-D vs HR slope (ms/bpm; systolic ~ -0.6
             here, diastole-locked ~ -12)

Usage: python scripts/screen_filters.py outputs/screen/screen_rest.csv [--ref bw:40]
"""
import argparse
import os

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from compare_d_rules import hr_slope  # noqa: E402

TIMING = ["ECG_S_ms", "S_D_ms", "SWS"]
SHAPE = ["nSWI", "DWI_over_SWI", "D_sharpness"]
SPLIT = {"ECG_S_ms": "split_dECG_S_ms", "S_D_ms": "split_dS_D_ms", "SWS": "split_dSWS"}


def screen(df, ref):
    key = ["rid", "channel", "win_start"]
    out, n_common = [], {}
    for ch, g in df.groupby("channel"):
        g = g[g.ppg_flat_frac <= 0.5]
        ok_all = g.groupby(key).ok.all()
        common = set(ok_all[ok_all].index)
        n_common[ch] = len(common)
        r = g[g.spec == ref].set_index(key)
        for spec, s in g.groupby("spec"):
            s = s.set_index(key)
            both = s.index[s.ok & r.reindex(s.index).ok.fillna(False).astype(bool)]
            row = {"channel": ch, "spec": spec, "yield": s.ok.mean(), "n_ok": int(s.ok.sum())}
            for m in TIMING + SHAPE:
                diff = (s.loc[both, m] - r.loc[both, m]).dropna()
                if m in SHAPE:  # relative difference for gain-free shape metrics
                    diff = diff / r.loc[diff.index, m].abs()
                row[f"bias_{m}"] = diff.median()
                row[f"spread95_{m}"] = diff.abs().quantile(0.95)
            sc = s.loc[s.index.isin(common)]
            for m in TIMING:
                row[f"split_{m}"] = sc[SPLIT[m]].median()
            okw = s[s.ok]
            for m in ["S_D_ms", "SWS", "D_sharpness"]:
                row[f"withinrec_sd_{m}"] = okw.groupby("rid")[m].std().median()
            row["records_ok"] = int((s.groupby(level="rid").ok.sum() >= 1).sum())
            row["between_subj_sd_S_D_ms"] = okw.groupby("rid").S_D_ms.median().std()
            row["frac_S_D_outside_100_350"] = ((okw.S_D_ms < 100) | (okw.S_D_ms > 350)).mean()
            s_clean = s[(s.n_acc >= 10) & (s.S_found == True) & (s.split_dECG_S_ms <= 10)]  # noqa: E712
            row["no_rebound_frac"] = (s_clean.D_found != True).mean()  # noqa: E712
            row["HR_slope_S_D"] = hr_slope(okw.reset_index())[0]
            out.append(row)
    return pd.DataFrame(out), n_common


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--ref", default="bw:40")
    a = ap.parse_args()
    df = pd.read_csv(a.csv)
    table, n_common = screen(df, a.ref)
    path = os.path.splitext(a.csv)[0] + "_filter_table.csv"
    table.to_csv(path, index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 50)
    print("windows ok under every filter:", n_common)
    for ch, t in table.groupby("channel"):
        print(f"\n== {ch} (reference {a.ref}; timing in ms, shape metrics as relative difference)")
        cols = ["spec", "yield", "n_ok", "bias_ECG_S_ms", "spread95_ECG_S_ms", "bias_S_D_ms", "spread95_S_D_ms",
                "bias_SWS", "bias_nSWI", "bias_DWI_over_SWI", "bias_D_sharpness", "split_ECG_S_ms",
                "split_S_D_ms", "split_SWS", "withinrec_sd_S_D_ms", "withinrec_sd_SWS", "records_ok",
                "between_subj_sd_S_D_ms", "frac_S_D_outside_100_350", "no_rebound_frac", "HR_slope_S_D"]
        print(t[cols].sort_values("spec").round(3).to_string(index=False))
    print("\nwritten", path)
