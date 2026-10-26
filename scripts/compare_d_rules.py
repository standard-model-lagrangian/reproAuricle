"""Compare D-wave picking rules (one run_batch.py output per rule).

There is no ground-truth D timing, and ear and finger PPG are *not* expected to give the same
S-D: the finger is far more peripheral (longer transit, more reflection, different vascular
bed). So rules are judged on criteria intrinsic to each channel. The finger is used only as a
reference for how S-D *changes* within a recording, not for its absolute value.

Intrinsic criteria (per channel):
  yield           fraction of windows / records passing QC
  split-half      within-window precision of S-D (odd vs even beats)
  within-session  median SD of S-D across a recording's rest windows (noise + pick switching)
  between-subject SD of record-median S-D (carotid controls: ~37 ms)
  ICC(2,1)        between-day repeatability, healthy cohort. Note that a *consistently wrong*
                  pick is also repeatable, so ICC alone cannot validate a rule
  HR slope        pooled within-recording slope of S-D on HR (ms/bpm). D is an end-systolic
                  event, so S-D should behave like LV ejection time: about -1.7 ms/bpm (Weissler).
                  A feature locked to diastole scales with RR (about -60000/HR^2, roughly -12 ms/bpm
                  at 70 bpm)
Reaction reference (ear vs finger, same windows):
  change_rho      Spearman correlation of within-recording *deviations* of S-D (ear vs finger),
                  i.e. do both sites move together, regardless of absolute offset
  exercise_sign   fraction of pre->post-exercise pairs where S-D changes in the same direction
                  at ear and finger

Usage: python scripts/compare_d_rules.py outputs/drules/window.csv outputs/drules/rebound_es.csv ...
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from summarise import exercise_effect, record_medians, test_retest  # noqa: E402

KEY = ["rid", "win_start"]


def hr_slope(ok, min_windows=3, min_hr_range=3.0):
    """Pooled within-recording slope of S-D on HR, and the median of per-recording slopes."""
    xs, ys, per = [], [], []
    for _, g in ok.groupby("rid"):
        g = g.dropna(subset=["S_D_ms", "HR"])
        if len(g) < min_windows or np.ptp(g.HR) < min_hr_range:
            continue
        x, y = g.HR - g.HR.mean(), g.S_D_ms - g.S_D_ms.mean()
        xs.append(x)
        ys.append(y)
        per.append(np.polyfit(x, y, 1)[0])
    if not xs:
        return np.nan, np.nan, 0
    x, y = np.concatenate(xs), np.concatenate(ys)
    return float((x * y).sum() / (x * x).sum()), float(np.median(per)), len(per)


def reaction_reference(df):
    e = df[(df.channel == "PPG_Ear") & df.ok].set_index(KEY)
    f = df[(df.channel == "PPG_Finger") & df.ok].set_index(KEY)
    both = e.index.intersection(f.index)
    j = pd.DataFrame({"e": e.loc[both, "S_D_ms"], "f": f.loc[both, "S_D_ms"]}).reset_index()
    j = j[j.groupby("rid").e.transform("size") >= 3]
    dev = j.groupby("rid")[["e", "f"]].transform(lambda s: s - s.mean())
    rho = stats.spearmanr(dev.e, dev.f).statistic if len(dev) > 2 else np.nan
    _, pairs = exercise_effect(df)
    p = pairs.assign(delta=pairs.post_S_D_ms - pairs.pre_S_D_ms).pivot_table(
        index=["rid", "pre_S_D_ms"], columns="channel", values="delta") if len(pairs) else pd.DataFrame()
    # pair ear/finger exercise bouts by record and bout order
    ex = pairs.assign(delta=pairs.post_S_D_ms - pairs.pre_S_D_ms)
    ex["bout"] = ex.groupby(["channel", "rid"]).cumcount()
    w = ex.pivot_table(index=["rid", "bout"], columns="channel", values="delta").dropna()
    sign = (np.sign(w.PPG_Ear) == np.sign(w.PPG_Finger)).mean() if len(w) and "PPG_Ear" in w else np.nan
    return {"change_rho": rho, "change_n_windows": len(dev), "change_n_records": j.rid.nunique(),
            "exercise_sign_agree": sign, "exercise_n_pairs": len(w)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csvs", nargs="+")
    a = ap.parse_args()
    runs = {os.path.splitext(os.path.basename(p))[0]: pd.read_csv(p) for p in a.csvs}

    rows, react = [], []
    for name, df in runs.items():
        rec = record_medians(df)
        tr, _ = test_retest(rec)
        for ch, g in df[df.ppg_flat_frac <= 0.5].groupby("channel"):
            ok = g[g.ok]
            multi = ok.groupby("rid").filter(lambda x: len(x) >= 3)
            slope, med_slope, n_slope = hr_slope(ok)
            row = {"rule": name, "channel": ch, "windows_ok": g.ok.mean(),
                   "records_>=1_ok": int((g.groupby("rid").ok.sum() >= 1).sum()),
                   "split_half_S_D_ms": ok.split_dS_D_ms.median(),
                   "within_session_sd_S_D_ms": multi.groupby("rid").S_D_ms.std().median(),
                   "between_subject_sd_S_D_ms": rec.loc[ch].S_D_ms.std(),
                   "median_S_D_ms": rec.loc[ch].S_D_ms.median(),
                   "HR_slope_ms_per_bpm": slope, "HR_slope_median_per_rec": med_slope, "HR_slope_n_rec": n_slope}
            for m in ["S_D_ms", "SWS", "D_sharpness"]:
                t = tr[(tr.channel == ch) & (tr.metric == m)]
                row[f"ICC_{m}"] = t["ICC(2,1)"].iloc[0] if len(t) else np.nan
            row["ICC_n"] = int(tr[(tr.channel == ch) & (tr.metric == "S_D_ms")].n_subjects.iloc[0])
            rows.append(row)
        react.append({"rule": name, **reaction_reference(df)})

    out = pd.DataFrame(rows)
    rr = pd.DataFrame(react)
    base = os.path.dirname(a.csvs[0])
    out.to_csv(os.path.join(base, "d_rule_comparison.csv"), index=False)
    rr.to_csv(os.path.join(base, "d_rule_reaction_reference.csv"), index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    for ch, t in out.groupby("channel", sort=False):
        print(f"\n== {ch}: intrinsic criteria")
        print(t.drop(columns="channel").round(3).to_string(index=False))
    print("\n== ear vs finger: reaction reference only (changes within a recording, not absolute values)")
    print(rr.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
