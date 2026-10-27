"""Final sweep of the D-only (ArterioWave PWTA) wave metrics on Auricle: extractability, reliability and
manoeuvre shifts, per PPG site, stratum (HC day 1 / HC day 2 / HFC) and activity.

Features (D-only manuscript / Reavette 2024, PPG versions):
  ECG_S_ms   R-to-S peak (ECG-S interval)          needs S only
  nSWI       S-wave peak intensity / pulse amplitude   needs S only (PPG gain is arbitrary)
  t_D_ms     R-to-D peak (D delay, cf. Fig. S8)      needs D
  S_D_ms     S-D interval                            needs D
  SWS        60*ECG-S / (S-D * HR)                   needs D
  nDWI       D-wave peak intensity / pulse amplitude   needs D
  DWI_over_SWI  gain-free D/S intensity ratio        needs D
  DWI_over_DWE  D-wave flattening (peak/energy)      needs D and a bounded D lobe

Input: run_batch.py output with 20-s windows over labels 0-4 (settle 5 s).
Usage: python scripts/feature_sweep.py outputs/sweep/windows_all_20s.csv
"""
import argparse
import os

import sys

import numpy as np
import pandas as pd
import wfdb
from joblib import Parallel, delayed
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pwta import io  # noqa: E402
from pwta.windows import segments  # noqa: E402

ACT = {0: "rest", 1: "breath_hold", 2: "valsalva", 3: "exercise", 4: "cold_pressor"}
S_FEATS = ["ECG_S_ms", "nSWI"]
D_FEATS = ["t_D_ms", "S_D_ms", "SWS", "nDWI", "DWI_over_SWI", "DWI_over_DWE"]
FEATS = ["HR"] + S_FEATS + D_FEATS
STEADY_S = 25.0  # rest windows starting >= 25 s after the previous manoeuvre count as steady rest
SPLIT = {"ECG_S_ms": "split_dECG_S_ms", "S_D_ms": "split_dS_D_ms", "SWS": "split_dSWS"}


def _record_segments(rid):
    path = os.path.join(io.DATA_ROOT, "data", rid, rid)
    if "Activity_Annotations" not in wfdb.rdheader(path).sig_name:
        return []
    r = wfdb.rdrecord(path, channel_names=["Activity_Annotations"])
    act = np.rint(r.p_signal[:, 0]).astype(int)
    return [dict(rid=rid, label=lab, start_s=a / r.fs, dur_s=(b - a) / r.fs) for a, b, lab in segments(act)]


def segment_table(jobs=6):
    """Every activity segment of every record (manoeuvre repetitions are counted from this)."""
    res = Parallel(n_jobs=jobs)(delayed(_record_segments)(rid) for rid in io.list_records())
    return pd.DataFrame([x for r in res for x in r])


def s_clean(df):
    n_tot = df.n_total.where(df.n_total > 0)
    return ((df.ppg_flat_frac <= 0.5) & (df.n_acc >= 10) & (df.n_acc / n_tot >= 0.6)
            & (df.S_found == True) & (df.split_dECG_S_ms <= 10))  # noqa: E712


def extractable(df):
    """Per-feature boolean mask: the window yields a trustworthy value of that feature."""
    sc = s_clean(df)
    ok = df.ok == True  # noqa: E712  (S clean + distinct end-systolic D + stable split halves)
    m = {"HR": sc}
    m.update({f: sc for f in S_FEATS})
    m.update({f: ok for f in D_FEATS})
    m["DWI_over_DWE"] = ok & (df.DWE_capped == False)  # noqa: E712
    return pd.DataFrame({f: v & df[f].notna() for f, v in m.items()})


def stratum(df):
    return np.where(df.cohort == "HFC", "HFC", "HC s" + df.session.astype(str))


def icc21(w):
    """ICC(2,1), two-way random, absolute agreement; w = subjects x sessions (complete)."""
    x = w.to_numpy(float)
    n, k = x.shape
    gm = x.mean()
    msr = k * ((x.mean(1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((x.mean(0) - gm) ** 2).sum() / (k - 1)
    mse = ((x - x.mean(1, keepdims=True) - x.mean(0, keepdims=True) + gm) ** 2).sum() / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)


# ---------------------------------------------------------------- rest: coverage and reliability
def steady_rest(df):
    """Rest windows >= STEADY_S after a manoeuvre, or after a record start / not-applicable segment."""
    return df[(df.label == 0) & ((df.t_since_prev_s >= STEADY_S) | (df.prev_label < 0) | (df.prev_label == 9))]


def rest_reliability(df, ex):
    rest = steady_rest(df)
    exr = ex.loc[rest.index]
    n_subj_rec = df.groupby(["channel", "stratum"]).subject.nunique()
    rows = []
    for (ch, st), g in rest.groupby(["channel", "stratum"]):
        e = exr.loc[g.index]
        for f in FEATS:
            v = g[e[f]]
            rec = v.groupby("rid")[f]
            med = rec.median()
            row = dict(channel=ch, stratum=st, feature=f,
                       subjects=n_subj_rec[(ch, st)], subjects_with_value=v.subject.nunique(),
                       window_yield=e[f].mean(), windows=int(e[f].sum()),
                       median=med.median(), between_subject_sd=med.std(),
                       within_session_sd=rec.std().median())
            row["within_over_between"] = row["within_session_sd"] / row["between_subject_sd"]
            row["split_half_median_abs"] = v[SPLIT[f]].median() if f in SPLIT else np.nan
            rows.append(row)
    out = pd.DataFrame(rows)
    # between-day ICC on HC record medians (steady rest)
    icc = []
    hc = rest[rest.cohort == "HC"]
    for ch, g in hc.groupby("channel"):
        e = exr.loc[g.index]
        for f in FEATS:
            w = g[e[f]].groupby(["subject", "session"])[f].median().unstack().dropna()
            if w.shape[1] == 2 and len(w) >= 5:
                icc.append(dict(channel=ch, feature=f, n_subjects_both_days=len(w), icc21=icc21(w[[1, 2]]),
                                day_diff_sd=(w[2] - w[1]).std()))
    return out, pd.DataFrame(icc)


# ---------------------------------------------------------------- noise threshold for shifts
def rest_noise(df, ex):
    """SD of the change between steady-rest windows 1-2 steps (20-40 s) apart in the same rest segment.

    That is the gap between the baseline window and the manoeuvre / post window, so 1.96*SD is the
    smallest change one trial can show above spontaneous drift (MDC95)."""
    rest = steady_rest(df).copy()
    rest["seg"] = (rest.win_start_s - rest.t_since_prev_s).round(1)
    rows = []
    for (ch, grp), g in rest.groupby(["channel", rest.cohort]):
        e = ex.loc[g.index]
        for f in FEATS:
            d = []
            for _, s in g[e[f]].sort_values("win_start_s").groupby(["rid", "seg"]):
                t, v = s.win_start_s.to_numpy(), s[f].to_numpy()
                for lag in (1, 2):
                    ok = np.isclose(t[lag:] - t[:-lag], 20 * lag, atol=1)
                    d.extend((v[lag:] - v[:-lag])[ok])
            d = np.asarray(d)
            rows.append(dict(channel=ch, cohort=grp, feature=f, n_pairs=len(d),
                             sd_diff=d.std(ddof=1) if len(d) > 2 else np.nan))
    out = pd.DataFrame(rows)
    out["mdc95"] = 1.96 * out.sd_diff
    return out


# ---------------------------------------------------------------- manoeuvre trials
def trials(df, ex, segs):
    """One row per (record, site, manoeuvre repetition, feature, phase) with baseline and value."""
    df = df.copy()
    df["seg_start"] = (df.win_start_s - df.t_since_prev_s).round(1)
    rows = []
    segs = segs[segs.label.isin([1, 2, 3, 4])]
    for (rid, ch), g in df.groupby(["rid", "channel"]):
        e = ex.loc[g.index]
        sg = segs[segs.rid == rid].sort_values("start_s")
        for rep_k, s in enumerate(sg.itertuples()):
            s0, s1 = s.start_s, s.start_s + s.dur_s
            rep = int((sg.label.iloc[:rep_k + 1] == s.label).sum())
            pre = g[(g.label == 0) & (g.win_start_s + g.win_len_s <= s0 + 0.5)
                    & (g.win_start_s + g.win_len_s >= s0 - 30)]
            during = g[(g.label == s.label) & np.isclose(g.seg_start, round(s0, 1), atol=0.6)]
            post = g[(g.label == 0) & np.isclose(g.seg_start, round(s1, 1), atol=0.6) & (g.t_since_prev_s <= 5.5)]
            for f in FEATS:
                b = pre[e.loc[pre.index, f]]
                base = b.sort_values("win_start_s")[f].iloc[-1] if len(b) else np.nan
                for phase, w in (("during", during), ("post_5_25s", post)):
                    w0 = w.sort_values("win_start_s").head(1)
                    has_w = len(w0) > 0
                    val = w0[f].iloc[0] if has_w and e.loc[w0.index[0], f] else np.nan
                    rows.append(dict(rid=rid, subject=g.subject.iloc[0], session=g.session.iloc[0],
                                     cohort=g.cohort.iloc[0], stratum=g.stratum.iloc[0], channel=ch,
                                     manoeuvre=ACT[s.label], rep=rep, phase=phase, feature=f,
                                     window_exists=has_w, base=base, value=val, delta=val - base))
    return pd.DataFrame(rows)


def shift_summary(tr, noise):
    tr = tr.merge(noise[["channel", "cohort", "feature", "mdc95"]], on=["channel", "cohort", "feature"])
    tr = tr[tr.window_exists]
    tr["measurable"] = tr.delta.notna()
    tr["detectable"] = tr.measurable & (tr.delta.abs() > tr.mdc95)
    rows = []
    for key, g in tr.groupby(["channel", "manoeuvre", "phase", "feature", "stratum"]):
        m = g[g.measurable]
        subj = m.groupby("subject").delta.median()
        # repetition consistency within a session: share of repetitions agreeing with the session's sign
        cons = []
        for _, r in m.groupby("rid"):
            if len(r) >= 2 and np.median(r.delta) != 0:
                cons.append(np.mean(np.sign(r.delta) == np.sign(np.median(r.delta))))
        p = stats.wilcoxon(subj).pvalue if len(subj) >= 6 and (subj != 0).any() else np.nan
        rows.append(dict(zip(["channel", "manoeuvre", "phase", "feature", "stratum"], key),
                         trials=len(g), trials_measurable=len(m), frac_measurable=len(m) / len(g),
                         subjects_measurable=m.subject.nunique(),
                         frac_trials_above_mdc=m.detectable.mean() if len(m) else np.nan,
                         median_delta=subj.median() if len(subj) else np.nan,
                         frac_subjects_positive=(subj > 0).mean() if len(subj) else np.nan,
                         wilcoxon_p_subjects=p,
                         rep_sign_consistency=np.mean(cons) if cons else np.nan, n_sessions_rep=len(cons)))
    out = pd.DataFrame(rows)
    # between-day reproducibility of each subject's shift (HC, session medians)
    day = []
    hc = tr[(tr.cohort == "HC") & tr.measurable]
    for key, g in hc.groupby(["channel", "manoeuvre", "phase", "feature"]):
        w = g.groupby(["subject", "session"]).delta.median().unstack()
        if w.shape[1] < 2:
            continue
        w = w[[1, 2]].dropna()
        if len(w) < 5:
            continue
        day.append(dict(zip(["channel", "manoeuvre", "phase", "feature"], key), n_subjects_both_days=len(w),
                        same_sign_both_days=(np.sign(w[1]) == np.sign(w[2])).mean(),
                        spearman_day1_day2=stats.spearmanr(w[1], w[2]).statistic))
    return tr, out, pd.DataFrame(day)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("windows")
    ap.add_argument("--segments", default=None, help="segment table (default: rebuilt from the records)")
    ap.add_argument("--out", default="outputs/sweep")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    df = pd.read_csv(a.windows)
    df["stratum"] = stratum(df)
    ex = extractable(df)
    segs = pd.read_csv(a.segments) if a.segments else segment_table(a.jobs)
    os.makedirs(a.out, exist_ok=True)

    # window yield by activity (all windows, not only steady rest)
    yl = (pd.concat([df[["channel", "stratum", "label"]], ex], axis=1)
          .assign(activity=lambda x: x.label.map(ACT)).groupby(["channel", "activity", "stratum"])[FEATS].mean())
    rel, icc = rest_reliability(df, ex)
    noise = rest_noise(df, ex)
    tr = trials(df, ex, segs)
    tr, sh, day = shift_summary(tr, noise)

    for name, t in [("yield_by_activity", yl), ("rest_reliability", rel), ("rest_icc_between_days", icc),
                    ("rest_noise_mdc", noise), ("shift_summary", sh), ("shift_day_reproducibility", day)]:
        t.to_csv(os.path.join(a.out, f"{name}.csv"), index=name == "yield_by_activity")
    tr.to_csv(os.path.join(a.out, "trials.csv"), index=False)
    with open(os.path.join(a.out, "sweep.md"), "w") as f:
        for name, t in [("yield_by_activity", yl.round(2)), ("rest_reliability", rel.round(3)),
                        ("rest_icc_between_days", icc.round(2)), ("rest_noise_mdc", noise.round(3)),
                        ("shift_summary", sh.round(3)), ("shift_day_reproducibility", day.round(2))]:
            f.write(f"## {name}\n\n{t.to_markdown()}\n\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
