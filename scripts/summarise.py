"""Reliability summary of the extracted wave metrics (output of run_batch.py).

Answers: in how many recordings/windows can the diagnostic features be extracted, and how
repeatable are they (within window, within session, between days, between PPG sites)?
Also checks the physiological response to exercise (cf. D-only manuscript Fig. S8) and gives
exploratory group descriptives.

Usage: python scripts/summarise.py outputs/windows_rest.csv [--sensitivity outputs/sensitivity/*.csv]
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

METRICS = ["ECG_S_ms", "S_D_ms", "SWS", "HR", "nSWI", "nDWI", "DWI_over_SWI", "D_sharpness", "DWI_over_DWE"]
GROUP_ORDER = ["control", "HFrEF", "HFmrEF", "HF_EF>=50", "HF_unknown_EF"]
# Categorical slots in fixed order (reference palette); unknown group in neutral grey
COLOURS = {"control": "#2a78d6", "HFrEF": "#eb6834", "HFmrEF": "#1baf7a", "HF_EF>=50": "#eda100",
           "HF_unknown_EF": "#8a8a85", "PPG_Ear": "#2a78d6", "PPG_Finger": "#eb6834"}
INK, MUTED = "#1f1f1e", "#6b6a64"


def icc_2_1(a, b):
    """ICC(2,1): two-way random effects, absolute agreement, single measurement."""
    x = np.column_stack([a, b])
    n, k = x.shape
    gm = x.mean()
    msr = k * ((x.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((x.mean(axis=0) - gm) ** 2).sum() / (k - 1)
    mse = ((x - x.mean(axis=1, keepdims=True) - x.mean(axis=0, keepdims=True) + gm) ** 2).sum() / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)


def coverage(df):
    rows = []
    for (ch, cohort), g in df.groupby(["channel", "cohort"]):
        per_rec = g.groupby("rid").ok.sum()
        rows.append({"channel": ch, "cohort": cohort, "records": g.rid.nunique(),
                     "records_>=1_ok": int((per_rec >= 1).sum()), "records_>=3_ok": int((per_rec >= 3).sum()),
                     "windows": len(g), "windows_ok_frac": g.ok.mean(),
                     "median_beats_per_ok_window": g[g.ok].n_acc.median()})
    return pd.DataFrame(rows)


def reasons(df):
    r = df.assign(reason=df.reasons.fillna("").str.split(";")).explode("reason")
    r = r[r.reason != ""]
    return r.groupby(["channel", "reason"]).size().unstack(0).fillna(0).astype(int).sort_values("PPG_Ear", ascending=False)


def record_medians(df):
    ok = df[df.ok]
    med = ok.groupby(["channel", "rid"])[METRICS].median()
    info = ok.groupby(["channel", "rid"])[["cohort", "subject", "session", "group", "Age"]].first()
    return med.join(info).join(ok.groupby(["channel", "rid"]).size().rename("n_ok"))


def precision(df, rec):
    ok = df[df.ok]
    rows = []
    for ch, g in ok.groupby("channel"):
        row = {"channel": ch}
        for m, s in (("ECG_S_ms", "split_dECG_S_ms"), ("S_D_ms", "split_dS_D_ms"), ("SWS", "split_dSWS")):
            row[f"split_half_median_{m}"] = g[s].median()
            row[f"split_half_p90_{m}"] = g[s].quantile(0.9)
        for m in ["ECG_S_ms", "S_D_ms", "SWS", "D_sharpness", "DWI_over_SWI"]:
            sd = g.groupby("rid")[m].std()
            row[f"within_session_sd_{m}"] = sd.median()
            row[f"between_record_sd_{m}"] = rec.loc[ch][m].std()
        rows.append(row)
    return pd.DataFrame(rows).set_index("channel").T


def test_retest(rec):
    rows, pairs = [], {}
    for ch in rec.index.get_level_values(0).unique():
        r = rec.loc[ch]
        hc = r[(r.cohort == "HC") & (r.n_ok >= 2)]
        wide = hc.pivot_table(index="subject", columns="session", values=METRICS)
        for m in ["ECG_S_ms", "S_D_ms", "SWS", "HR", "nSWI", "DWI_over_SWI", "D_sharpness"]:
            if (m, 1) not in wide or (m, 2) not in wide:
                continue
            p = wide[[(m, 1), (m, 2)]].dropna()
            pairs[(ch, m)] = p
            rows.append({"channel": ch, "metric": m, "n_subjects": len(p), "ICC(2,1)": icc_2_1(p.iloc[:, 0], p.iloc[:, 1]),
                         "mean_diff_s2_minus_s1": (p.iloc[:, 1] - p.iloc[:, 0]).mean(),
                         "sd_diff": (p.iloc[:, 1] - p.iloc[:, 0]).std()})
    return pd.DataFrame(rows), pairs


def ear_vs_finger(df):
    key = ["rid", "win_start"]
    e = df[(df.channel == "PPG_Ear") & df.ok].set_index(key)
    f = df[(df.channel == "PPG_Finger") & df.ok].set_index(key)
    both = e.index.intersection(f.index)
    rows = []
    for m in ["ECG_S_ms", "t_D_ms", "S_D_ms", "SWS", "DWI_over_SWI", "D_sharpness"]:
        a, b = e.loc[both, m], f.loc[both, m]
        rows.append({"metric": m, "n_windows": len(both), "n_records": both.get_level_values(0).nunique(),
                     "finger_minus_ear_mean": (b - a).mean(), "finger_minus_ear_sd": (b - a).std(),
                     "spearman_r": stats.spearmanr(a, b).statistic})
    return pd.DataFrame(rows), e.loc[both], f.loc[both]


def exercise_effect(df):
    """Paired change from the last rest window before the first exercise bout to the first rest
    window after each bout (both windows must pass QC)."""
    rows = []
    for (ch, rid), g in df[df.ok].groupby(["channel", "rid"]):
        g = g.sort_values("win_start")
        pre = g[(g.next_label == 3) & (g.prev_label != 3)]
        post = g[(g.prev_label == 3) & (g.t_since_prev_s <= 15)]
        for _, p in post.iterrows():
            before = pre[pre.win_start < p.win_start]
            if before.empty:
                continue
            b = before.iloc[-1]
            row = {"channel": ch, "rid": rid, "cohort": p.cohort}
            for m in ["HR", "ECG_S_ms", "t_D_ms", "S_D_ms", "SWS"]:
                row[f"pre_{m}"], row[f"post_{m}"] = b[m], p[m]
            rows.append(row)
    pairs = pd.DataFrame(rows)
    out = []
    for ch, g in pairs.groupby("channel"):
        for m in ["HR", "ECG_S_ms", "t_D_ms", "S_D_ms", "SWS"]:
            d = g[f"post_{m}"] - g[f"pre_{m}"]
            out.append({"channel": ch, "metric": m, "n_pairs": len(d), "n_records": g.rid.nunique(),
                        "median_change": d.median(), "frac_increase": (d > 0).mean(),
                        "wilcoxon_p": stats.wilcoxon(d).pvalue if len(d) >= 6 else np.nan})
    return pd.DataFrame(out), pairs


def groups(rec):
    """Subject-level (mean of session medians) descriptives and control-vs-HFrEF AUROC. Exploratory:
    controls are young healthy volunteers, not age-matched patients."""
    rows = []
    for ch in rec.index.get_level_values(0).unique():
        subj = rec.loc[ch].groupby("subject").agg({**{m: "mean" for m in METRICS}, "group": "first", "Age": "first"})
        for m in ["ECG_S_ms", "S_D_ms", "SWS", "HR", "nSWI", "DWI_over_SWI", "D_sharpness"]:
            row = {"channel": ch, "metric": m}
            for gname in GROUP_ORDER:
                v = subj.loc[subj.group == gname, m].dropna()
                row[f"{gname} (n)"] = len(v)
                row[f"{gname} median"] = v.median()
            c = subj.loc[subj.group == "control", m].dropna()
            h = subj.loc[subj.group == "HFrEF", m].dropna()
            if len(c) and len(h):
                u = stats.mannwhitneyu(h, c)
                row["AUROC HFrEF>control"] = u.statistic / (len(h) * len(c))
                row["MW p"] = u.pvalue
            rows.append(row)
    return pd.DataFrame(rows)


def sensitivity(main, others):
    key = ["rid", "channel", "win_start"]
    m = main.set_index(key)
    rows = []
    for path in others:
        o = pd.read_csv(path).set_index(key)
        both = m.index[m.ok & o.reindex(m.index).ok.fillna(False).astype(bool)]
        d = (o.loc[both, "S_D_ms"] - m.loc[both, "S_D_ms"]).abs()
        rows.append({"variant": os.path.basename(path), "yield_main": m.ok.mean(), "yield_variant": o.ok.mean(),
                     "windows_ok_both": len(both), "frac_|dS_D|>5ms": (d > 5).mean(),
                     "median_|dS_D|_ms": d.median()})
    return pd.DataFrame(rows)


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(True, color="#e4e3dd", lw=0.6)
    ax.set_axisbelow(True)


def figures(pairs_tr, e, f, ex_pairs, rec, out_dir):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    for ch in ("PPG_Ear", "PPG_Finger"):
        if (ch, "SWS") in pairs_tr:
            p = pairs_tr[(ch, "SWS")]
            ax.scatter(p.iloc[:, 0], p.iloc[:, 1], s=36, color=COLOURS[ch], edgecolor="white", lw=1.5,
                       label=f"{ch.split('_')[1]} (n={len(p)})", zorder=3)
    lim = ax.get_xlim()
    ax.plot(lim, lim, color=MUTED, lw=1, ls="--", zorder=1)
    ax.set_xlabel("SWS, session 1 (s)", color=INK)
    ax.set_ylabel("SWS, session 2 (s)", color=INK)
    ax.set_title("Between-day repeatability (healthy cohort)", color=INK, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8)
    ax = axes[1]
    ax.scatter(e.S_D_ms, f.S_D_ms, s=10, color=COLOURS["PPG_Ear"], alpha=0.5, edgecolor="none")
    lim = [min(e.S_D_ms.min(), f.S_D_ms.min()), max(e.S_D_ms.max(), f.S_D_ms.max())]
    ax.plot(lim, lim, color=MUTED, lw=1, ls="--")
    ax.set_xlabel("S-D interval, ear PPG (ms)", color=INK)
    ax.set_ylabel("S-D interval, finger PPG (ms)", color=INK)
    ax.set_title(f"Ear vs finger, same windows (n={len(e)}; reference, not expected to match)",
                 color=INK, fontsize=10, loc="left")
    ax = axes[2]
    g = ex_pairs[ex_pairs.channel == "PPG_Ear"]
    for _, r in g.iterrows():
        ax.plot([0, 1], [r.pre_ECG_S_ms, r.post_ECG_S_ms], color=COLOURS["PPG_Ear"], lw=1, alpha=0.5)
    ax.set_xticks([0, 1], ["before exercise", "≈10 s after exercise"])
    ax.set_ylabel("ECG-S interval, ear PPG (ms)", color=INK)
    ax.set_title(f"Exercise recovery (n={len(g)} pairs)", color=INK, fontsize=10, loc="left")
    for ax in axes:
        _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "reliability.png"), dpi=110)
    plt.close(fig)

    metrics = [("ECG_S_ms", "ECG-S (ms)"), ("S_D_ms", "S-D (ms)"), ("SWS", "SWS (s)"), ("D_sharpness", "D sharpness (1/s)")]
    fig, axes = plt.subplots(2, 4, figsize=(16, 7))
    rng = np.random.default_rng(0)
    for i, ch in enumerate(("PPG_Ear", "PPG_Finger")):
        subj = rec.loc[ch].groupby("subject").agg({**{m: "mean" for m, _ in metrics}, "group": "first"})
        for j, (m, label) in enumerate(metrics):
            ax = axes[i, j]
            for k, gname in enumerate(GROUP_ORDER):
                v = subj.loc[subj.group == gname, m].dropna()
                ax.scatter(k + rng.uniform(-0.15, 0.15, len(v)), v, s=22, color=COLOURS[gname],
                           edgecolor="white", lw=1, zorder=3)
                if len(v):
                    ax.hlines(v.median(), k - 0.3, k + 0.3, color=INK, lw=2, zorder=4)
            ax.set_xticks(range(len(GROUP_ORDER)), [g.replace("HF_unknown_EF", "HF EF?") for g in GROUP_ORDER],
                          rotation=30, fontsize=8)
            ax.set_title(f"{label} - {ch.split('_')[1]}", color=INK, fontsize=10, loc="left")
            _style(ax)
    fig.suptitle("Per-subject means (exploratory; controls are young volunteers, not age-matched)",
                 color=MUTED, fontsize=9, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "groups.png"), dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--sensitivity", nargs="*", default=[])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(a.csv), "summary")
    os.makedirs(out, exist_ok=True)
    df = pd.read_csv(a.csv)
    rec = record_medians(df)

    cov, rsn, prec = coverage(df), reasons(df), precision(df, rec)
    tr, tr_pairs = test_retest(rec)
    ef, e, f = ear_vs_finger(df)
    ex, ex_pairs = exercise_effect(df)
    grp = groups(rec)
    sens = sensitivity(df, a.sensitivity) if a.sensitivity else pd.DataFrame()
    no_ok = df.groupby(["channel", "rid"]).ok.sum().unstack(0)
    no_ok = no_ok[no_ok.PPG_Ear == 0]

    tables = {"coverage": cov, "failure_reasons": rsn, "precision": prec, "test_retest": tr,
              "ear_vs_finger": ef, "exercise_effect": ex, "groups_exploratory": grp,
              "records_without_ok_ear_window": no_ok, "d_wave_sensitivity": sens}
    with open(os.path.join(out, "summary.md"), "w") as fh:
        for name, t in tables.items():
            t.to_csv(os.path.join(out, f"{name}.csv"))
            fh.write(f"## {name}\n\n{t.round(3).to_markdown()}\n\n")
    rec.to_csv(os.path.join(out, "record_medians.csv"))
    figures(tr_pairs, e, f, ex_pairs, rec, out)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    for name, t in tables.items():
        print(f"\n== {name}\n{t.round(3).to_string()}")


if __name__ == "__main__":
    main()
