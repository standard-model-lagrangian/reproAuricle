"""Do the PWTA features survive a 125 Hz acquisition (MIMIC waveform rate)?

Compares run_batch.py output at the native 1 kHz with runs on the same records decimated to 125 Hz
(`--resample 125`: the pipeline runs at 125 Hz) and decimated then interpolated back to 1 kHz
(`--resample 125:1000`: band-limited reconstruction before analysis). Windows are matched on
(rid, channel, window start rounded to 1 s).

Reports, per site and variant:
  yield        S-clean and ok fractions; how often a window keeps its native ok / S-clean verdict
  fidelity     per feature, on windows that pass the feature's tier under both: median difference
               (bias), median and 95th-percentile |difference|, |difference| relative to the native
               within-session SD, and the Spearman of record medians against native
  precision    median split-half |odd - even| for ECG-S, S-D, SWS
  reliability  HC between-day ICC(2,1) of record medians, each variant on its own QC
  reliability_matched  the same, restricted to windows that pass the feature's tier in every run, so
               differences come from the values alone, not from windows flipping QC verdicts

Usage:
  python scripts/downsample_check.py outputs/windows_rest.csv \
      outputs/downsample/windows_rest_125.csv outputs/downsample/windows_rest_125up.csv --out outputs/downsample
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import icc21, s_clean  # noqa: E402

S_TIER = ["HR", "ECG_S_ms", "nSWI", "reb_rise_frac", "PAT_foot_ms", "CT_ms", "PW50_frac", "b_over_a"]
D_TIER = ["t_D_ms", "S_D_ms", "SWS", "nDWI", "DWI_over_SWI", "D_sharpness"]
SPLIT = {"ECG_S_ms": "split_dECG_S_ms", "S_D_ms": "split_dS_D_ms", "SWS": "split_dSWS"}
KEY = ["rid", "channel", "t0"]


def load(path):
    w = pd.read_csv(path, low_memory=False)
    w["t0"] = w.win_start_s.round().astype(int)
    w["s_clean"] = s_clean(w)
    w["ok"] = w.ok == True  # noqa: E712
    return w


def tier(feature):
    return "ok" if feature in D_TIER else "s_clean"


def yield_table(nat, var, name):
    j = nat.set_index(KEY)[["ok", "s_clean", "cohort"]].join(
        var.set_index(KEY)[["ok", "s_clean"]], rsuffix="_v", how="inner")
    rows = []
    for (ch, coh), g in j.groupby(["channel", "cohort"]):
        rows.append({"variant": name, "channel": ch, "cohort": coh, "windows": len(g),
                     "s_clean_native": g.s_clean.mean(), "s_clean_variant": g.s_clean_v.mean(),
                     "ok_native": g.ok.mean(), "ok_variant": g.ok_v.mean(),
                     "ok_kept": g.ok_v[g.ok].mean(), "ok_gained": g.ok_v[~g.ok].mean(),
                     "s_clean_kept": g.s_clean_v[g.s_clean].mean()})
    return rows


def fidelity_table(nat, var, name):
    rows = []
    for ch in sorted(nat.channel.unique()):
        a, b = nat[nat.channel == ch].set_index(KEY), var[var.channel == ch].set_index(KEY)
        for f in S_TIER + D_TIER:
            t = tier(f)
            both = a.index[a[t]].intersection(b.index[b[t]])
            d = (b.loc[both, f] - a.loc[both, f]).dropna()
            within = a[a[t]].groupby("rid")[f].std().median()
            ra = a[a[t]].groupby("rid")[f].median()
            rb = b[b[t]].groupby("rid")[f].median()
            r = pd.concat([ra, rb], axis=1, keys=["a", "b"]).dropna()
            rows.append({"variant": name, "channel": ch, "feature": f, "tier": t, "windows_both": len(d),
                         "bias": d.median(), "median_abs_diff": d.abs().median(),
                         "p95_abs_diff": d.abs().quantile(0.95),
                         "native_within_session_sd": within,
                         "p95_abs_diff_over_within_sd": d.abs().quantile(0.95) / within,
                         "records": len(r),
                         "record_spearman": stats.spearmanr(r.a, r.b).statistic if len(r) > 2 else np.nan})
    return rows


def precision_table(w, name):
    rows = []
    for ch, g in w.groupby("channel"):
        for f, col in SPLIT.items():
            sel = g[g[tier(f)]]
            rows.append({"variant": name, "channel": ch, "feature": f, "split_half_median_abs": sel[col].median(),
                         "windows": int(sel[col].notna().sum())})
    return rows


def reliability_table(w, name, keep=None):
    """keep: optional {feature: index of (rid, channel, t0)} restricting the windows used."""
    rows = []
    hc = w[w.cohort == "HC"]
    for ch, g in hc.groupby("channel"):
        for f in S_TIER + D_TIER:
            sel = g[g[tier(f)]]
            if keep is not None:
                sel = sel[sel.set_index(KEY).index.isin(keep[f])]
            m = sel.groupby(["subject", "session"])[f].median().unstack()
            m = m[[c for c in (1, 2) if c in m]].dropna()
            if m.shape[1] == 2 and len(m) >= 5:
                rows.append({"variant": name, "channel": ch, "feature": f, "n_subjects": len(m),
                             "icc21_between_days": icc21(m)})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("native")
    ap.add_argument("variants", nargs="+")
    ap.add_argument("--out", default="outputs/downsample")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    nat = load(a.native)
    names = {p: os.path.splitext(os.path.basename(p))[0].replace("windows_rest_", "") for p in a.variants}
    runs = {"native": nat, **{name: load(p) for p, name in names.items()}}
    keep = {}
    for f in S_TIER + D_TIER:
        idx = None
        for w in runs.values():
            i = w.set_index(KEY).index[w[tier(f)].to_numpy() & w[f].notna().to_numpy()]
            idx = i if idx is None else idx.intersection(i)
        keep[f] = idx
    ys, fs, ps, rs, rm = [], [], [], [], []
    for name, var in runs.items():
        if name != "native":
            ys += yield_table(nat, var, name)
            fs += fidelity_table(nat, var, name)
        ps += precision_table(var, name)
        rs += reliability_table(var, name)
        rm += reliability_table(var, name, keep)
    tables = {"yield": pd.DataFrame(ys), "fidelity": pd.DataFrame(fs), "precision": pd.DataFrame(ps),
              "reliability": pd.DataFrame(rs).pivot_table(index=["channel", "feature"], columns="variant",
                                                         values="icc21_between_days").reset_index(),
              "reliability_matched": pd.DataFrame(rm).pivot_table(
                  index=["channel", "feature", "n_subjects"], columns="variant",
                  values="icc21_between_days").reset_index()}
    md = ["# PWTA features at 125 Hz vs native 1 kHz\n"]
    for k, t in tables.items():
        t.to_csv(os.path.join(a.out, f"{k}.csv"), index=False)
        md.append(f"## {k}\n\n{t.round(3).to_markdown(index=False)}\n")
    with open(os.path.join(a.out, "downsample.md"), "w") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
