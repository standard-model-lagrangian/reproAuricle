"""Stratified re-checks of the D-wave rebound ("notch") and the post-exercise timing shift.

Design facts this respects:
  - HC participants were recorded on two different days (sessions 1 and 2); HFC participants once.
    Sessions of one person are repeated measures, never independent samples.
  - Exercise bouts within a session (2 in HC, 2 in HFC) are also repeated measures.
  - CNAP_Annotations == 0 marks CNAP calibration / uncalibrated periods (CNAP channels only per the
    dataset; tested here for any effect on ECG/PPG features).
All tests are done on per-subject values (one number per person), separately per PPG site.

Inputs: run_batch.py output with 60-s windows (rebound presence, CNAP) and 20-s windows (exercise
time course; settle 5 s, so the first post-exercise window starts 5 s after exercise ends).

Usage: python scripts/stratified_checks.py outputs/windows_rest.csv outputs/timecourse/windows_rest_20s.csv
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

COLOURS = {"HC s1": "#2a78d6", "HC s2": "#1baf7a", "HFC": "#eb6834"}
INK, MUTED = "#1f1f1e", "#6b6a64"
POST_BINS = [(5, 25), (25, 45), (45, 65), (65, 125), (125, 245)]


def s_clean(df):
    """Windows with a clean, stable S wave (D not required)."""
    n_tot = df.n_total.where(df.n_total > 0)
    return ((df.ppg_flat_frac <= 0.5) & (df.n_acc >= 10) & (df.n_acc / n_tot >= 0.6)
            & (df.S_found == True) & (df.split_dECG_S_ms <= 10))  # noqa: E712


def stratum(row):
    return "HFC" if row.cohort == "HFC" else f"HC s{int(row.session)}"


def wilcoxon_p(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    return stats.wilcoxon(x).pvalue if len(x) >= 6 and np.any(x != 0) else np.nan


# ---------------------------------------------------------------- rebound presence
def rebound_presence(df):
    s = df[s_clean(df)].assign(rebound=lambda x: (x.D_found == True).astype(float),  # noqa: E712
                               cnap_bad=lambda x: x.cnap_invalid_frac > 0.25)
    s["stratum"] = s.apply(stratum, axis=1)
    rec = s.groupby(["channel", "rid"]).agg(rebound=("rebound", "mean"), subject=("subject", "first"),
                                            session=("session", "first"), cohort=("cohort", "first"),
                                            group=("group", "first"), stratum=("stratum", "first"))
    by_stratum = rec.groupby(["channel", "stratum"]).rebound.agg(["size", "median", "mean"])
    by_group = rec[rec.session == 1].groupby(["channel", "group"]).rebound.agg(["size", "median", "mean"])
    # between-day reproducibility of rebound presence (HC subjects with both sessions)
    rep = []
    for ch, g in rec[rec.cohort == "HC"].groupby(level=0):
        w = g.pivot_table(index="subject", columns="session", values="rebound").dropna()
        rep.append({"channel": ch, "n_subjects": len(w), "spearman_day1_day2": stats.spearmanr(w[1], w[2]).statistic,
                    "mean_abs_change": (w[2] - w[1]).abs().mean()})
    # CNAP: within-record rebound rate in CNAP-invalid-heavy vs other windows
    cn = s[s.cnap_invalid_frac.notna()].groupby(["channel", "rid", "cnap_bad"]).rebound.mean().unstack("cnap_bad").dropna()
    cnap = cn.groupby(level=0).apply(lambda t: pd.Series({
        "n_records": len(t), "rebound_cnap_ok": t[False].mean(), "rebound_cnap_invalid": t[True].mean(),
        "wilcoxon_p": wilcoxon_p(t[True] - t[False])}))
    return by_stratum, by_group, pd.DataFrame(rep), cnap


# ---------------------------------------------------------------- CNAP effect on timing
def cnap_timing(df):
    ok = df[s_clean(df) & df.cnap_invalid_frac.notna()].assign(cnap_bad=lambda x: x.cnap_invalid_frac > 0.25)
    rows = []
    for (ch, m) in [(c, m) for c in ok.channel.unique() for m in ["ECG_S_ms", "S_D_ms", "SWS"]]:
        g = ok[ok.channel == ch]
        if m != "ECG_S_ms":
            g = g[g.ok == True]  # noqa: E712
        t = g.groupby(["rid", "cnap_bad"])[m].median().unstack().dropna()
        d = t[True] - t[False]
        rows.append({"channel": ch, "metric": m, "n_records": len(t), "median_diff_invalid_minus_ok": d.median(),
                     "wilcoxon_p": wilcoxon_p(d)})
    yield_ = df[(df.ppg_flat_frac <= 0.5) & df.cnap_invalid_frac.notna()].assign(cnap_bad=lambda x: x.cnap_invalid_frac > 0.25).groupby(
        ["channel", "cnap_bad"]).ok.mean().unstack()
    return pd.DataFrame(rows), yield_


# ---------------------------------------------------------------- exercise time course
def exercise_pairs(df):
    """Change from the last clean pre-exercise rest window (before the first bout) to each
    post-exercise rest window, labelled by time since exercise end."""
    sc = df[s_clean(df)].copy()
    rows = []
    for (ch, rid), g in sc.groupby(["channel", "rid"]):
        g = g.sort_values("win_start")
        pre = g[(g.next_label == 3) & (g.prev_label != 3)]
        post = g[g.prev_label == 3]
        if pre.empty or post.empty:
            continue
        # bout index: post windows belonging to the same rest segment share prev_label==3 and
        # increasing t_since_prev_s; a new bout starts when t_since_prev_s resets
        bout = (post.t_since_prev_s.diff().fillna(-1) < 0).cumsum()
        for (_, p), b in zip(post.iterrows(), bout):
            before = pre[pre.win_start < p.win_start]
            if before.empty:
                continue
            q = before.iloc[-1]
            row = {"channel": ch, "rid": rid, "subject": p.subject, "session": p.session, "cohort": p.cohort,
                   "bout": int(b), "t_post_s": p.t_since_prev_s, "cnap_bad": (p.cnap_invalid_frac > 0.25) if pd.notna(p.cnap_invalid_frac) else np.nan,
                   "rebound_pre": q.D_found == True, "rebound_post": p.D_found == True}  # noqa: E712
            row["d_HR"] = p.HR - q.HR
            row["d_ECG_S_ms"] = p.ECG_S_ms - q.ECG_S_ms
            both_ok = (p.ok == True) and (q.ok == True)  # noqa: E712
            for m in ["t_D_ms", "S_D_ms", "SWS"]:
                row[f"d_{m}"] = p[m] - q[m] if both_ok else np.nan
            rows.append(row)
    ex = pd.DataFrame(rows)
    if ex.empty:
        raise SystemExit("no exercise pairs in these windows (are the records annotated?)")
    ex["stratum"] = ex.apply(stratum, axis=1)
    ex["t_bin"] = pd.cut(ex.t_post_s, [a for a, _ in POST_BINS] + [POST_BINS[-1][1]], right=False,
                         labels=[f"{a}-{b}s" for a, b in POST_BINS])
    return ex


def subject_level(ex, by):
    """One value per subject (mean over sessions and bouts within the cell), then Wilcoxon vs 0."""
    out = []
    for keys, g in ex.groupby(by, observed=True):
        subj = g.groupby("subject")[["d_HR", "d_ECG_S_ms", "d_t_D_ms", "d_S_D_ms", "d_SWS"]].mean()
        row = dict(zip(by, keys if isinstance(keys, tuple) else (keys,)))
        row["n_subjects"] = len(subj)
        for m in ["d_HR", "d_ECG_S_ms", "d_t_D_ms", "d_S_D_ms", "d_SWS"]:
            v = subj[m].dropna()
            row[f"{m}_median"] = v.median()
            row[f"{m}_n"] = len(v)
            row[f"{m}_frac_pos"] = (v > 0).mean() if len(v) else np.nan
            row[f"{m}_p"] = wilcoxon_p(v)
        out.append(row)
    return pd.DataFrame(out)


def day_reproducibility(ex, t_bin="5-25s"):
    """Does the same HC person show the same early post-exercise shift on both days?"""
    e = ex[(ex.cohort == "HC") & (ex.t_bin == t_bin)]
    rows = []
    for ch, g in e.groupby("channel"):
        for m in ["d_ECG_S_ms", "d_t_D_ms", "d_S_D_ms"]:
            w = g.groupby(["subject", "session"])[m].mean().unstack().dropna()
            if len(w) < 5:
                continue
            rows.append({"channel": ch, "metric": m, "n_subjects": len(w),
                         "spearman_day1_day2": stats.spearmanr(w[1], w[2]).statistic,
                         "same_sign_both_days": (np.sign(w[1]) == np.sign(w[2])).mean(),
                         "median_day1": w[1].median(), "median_day2": w[2].median()})
    return pd.DataFrame(rows)


def figure(ex, out_dir):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6), sharex=True)
    order = [f"{a}-{b}s" for a, b in POST_BINS]
    for ax, (m, lab) in zip(axes, [("d_ECG_S_ms", "Δ ECG-S (ms)"), ("d_t_D_ms", "Δ R-to-D time (ms)"),
                                   ("d_HR", "Δ heart rate (bpm)")]):
        for k, st in enumerate(COLOURS):
            g = ex[(ex.channel == "PPG_Ear") & (ex.stratum == st)]
            med, lo, hi = [], [], []
            for b in order:
                v = g[g.t_bin == b].groupby("subject")[m].mean().dropna()
                med.append(v.median() if len(v) >= 3 else np.nan)
                lo.append(v.quantile(0.25) if len(v) >= 3 else np.nan)
                hi.append(v.quantile(0.75) if len(v) >= 3 else np.nan)
            x = np.arange(len(order)) + (k - 1) * 0.12
            ax.errorbar(x, med, yerr=[np.subtract(med, lo), np.subtract(hi, med)], fmt="o-", ms=6, lw=2,
                        capsize=0, color=COLOURS[st], label=st, mfc=COLOURS[st], mec="white", mew=1.5)
        ax.axhline(0, color=MUTED, lw=1)
        ax.set_xticks(range(len(order)), order, fontsize=8)
        ax.set_xlabel("time since end of exercise", color=INK)
        ax.set_title(f"{lab}, ear PPG (subject medians, IQR)", color=INK, fontsize=10, loc="left")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.grid(True, color="#e4e3dd", lw=0.6)
        ax.tick_params(colors=MUTED, labelsize=8)
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "exercise_timecourse_ear.png"), dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("windows60")
    ap.add_argument("windows20")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(a.windows60), "stratified")
    os.makedirs(out, exist_ok=True)
    w60, w20 = pd.read_csv(a.windows60), pd.read_csv(a.windows20)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)

    by_stratum, by_group, rep, cnap_reb = rebound_presence(w60)
    cnap_t, cnap_yield = cnap_timing(w60)
    ex = exercise_pairs(w20)
    tc = subject_level(ex, ["channel", "stratum", "t_bin"])
    early = ex[ex.t_bin == "5-25s"]
    by_reb = subject_level(early.assign(reb=early.rebound_pre & early.rebound_post), ["channel", "reb"])
    by_cnap = subject_level(early, ["channel", "cnap_bad"])
    days = day_reproducibility(ex)
    reb_change = early.groupby(["channel", "stratum"]).agg(rebound_pre=("rebound_pre", "mean"),
                                                         rebound_post=("rebound_post", "mean"), n_pairs=("rid", "size"))

    tables = {"rebound_by_stratum": by_stratum, "rebound_by_group_session1": by_group,
              "rebound_day_reproducibility": rep, "rebound_vs_cnap": cnap_reb, "timing_vs_cnap": cnap_t,
              "yield_vs_cnap": cnap_yield, "exercise_timecourse": tc, "exercise_early_by_rebound": by_reb,
              "exercise_early_by_cnap": by_cnap, "exercise_day_reproducibility": days,
              "rebound_pre_vs_post_exercise": reb_change}
    with open(os.path.join(out, "stratified.md"), "w") as fh:
        for name, t in tables.items():
            t.to_csv(os.path.join(out, f"{name}.csv"))
            fh.write(f"## {name}\n\n{t.round(3).to_markdown()}\n\n")
    figure(ex, out)
    show = ["channel", "stratum", "t_bin", "n_subjects", "d_HR_median", "d_ECG_S_ms_median", "d_ECG_S_ms_frac_pos",
            "d_ECG_S_ms_p", "d_t_D_ms_n", "d_t_D_ms_median", "d_t_D_ms_p", "d_S_D_ms_median", "d_S_D_ms_p"]
    for name, t in tables.items():
        if name == "exercise_timecourse":
            t = t[show]
        print(f"\n== {name}\n{t.round(3).to_string()}")


if __name__ == "__main__":
    main()
