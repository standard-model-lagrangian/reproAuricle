"""Audit of the validation experiments (docs/VALIDATION.md, section Audit), as one reproducible script.

  variants   write the window-table variants used for sensitivity reruns:
               windows_rest_annotated.csv          rest windows without the 4 unannotated records
               windows_rest_post1200_annotated.csv same, from the 1200-ms-ensemble run
               windows_rest_steady.csv             annotated rest windows starting >= 25 s after a manoeuvre
  checks     run every audit check and write one CSV per check (plus two figures) to the audit folder:
               window_integrity      1:1 joins, overlaps, label mixing (checked against raw annotations)
               truncation            800-ms ensemble: rebound-span and PW50 truncation, 800 vs 1200 ms
               reference_hr_slopes   within-record slopes on HR of PCG/CNAP fiducials vs Weissler
               s1_cross_sensor       S1/S2 agreement stethoscope vs earbuds (is S1 timing real?)
               slope_bounds          Exp 1 slopes: OLS vs reverse-regression bound
               rebound_vs_hr         ear/finger rebound presence by HR bin, slope below 100 bpm
               cv_leakage            Exp 4 CV pipeline with permuted labels (expect AUROC ~0.5)
               variance_sim          Exp 5 variance-component estimator on simulated data
               sensitivity_summary   Exp 3/4/5 headline numbers across window variants
               fig_cnap_fiducials.png, fig_pcg_s1_s2.png   visual checks on random windows

Usage (after the validation runs and the audit reruns in reproduce.sh):
  python scripts/audit_checks.py variants [--dir outputs/validation]
  python scripts/audit_checks.py checks   [--dir outputs/validation]
"""
import argparse
import os
import sys
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wfdb
from scipy.signal import savgol_filter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import STEADY_S, s_clean  # noqa: E402
from pwta import ecg, io, reference  # noqa: E402
from vstats import record_sums, within_slope  # noqa: E402

warnings.filterwarnings("ignore")
KEY = ["rid", "win_start"]


def subj(df):
    return df.assign(subject=df.rid.str.rsplit("_", n=1).str[0])


# ---------------------------------------------------------------- variants
def variants(d, a):
    w = pd.read_csv(f"{d}/windows_rest.csv")
    w[w.label == 0].to_csv(f"{a}/windows_rest_annotated.csv", index=False)
    w[(w.label == 0) & (w.t_since_prev_s >= STEADY_S)].to_csv(f"{a}/windows_rest_steady.csv", index=False)
    p = pd.read_csv(f"{a}/windows_rest_post1200.csv")
    p[p.label == 0].to_csv(f"{a}/windows_rest_post1200_annotated.csv", index=False)
    print("variants written to", a)


# ---------------------------------------------------------------- checks
def window_integrity(d):
    rows = []
    for tag in ("rest", "all_20s"):
        w = pd.read_csv(f"{d}/windows_{tag}.csv").drop_duplicates(KEY)
        r = pd.read_csv(f"{d}/reference_{tag}.csv")
        m = w.merge(r, on=KEY, how="outer", indicator=True)
        overl = 0
        for _, g in w.groupby("rid"):
            g = g.sort_values("win_start")
            end = g.win_start + (g.win_len_s * 1000).round().astype(int)
            overl += int((g.win_start.values[1:] < end.values[:-1]).sum())
        mixed = checked = 0
        for rid, g in w.groupby("rid"):
            path = os.path.join(io.DATA_ROOT, "data", rid, rid)
            if "Activity_Annotations" not in wfdb.rdheader(path).sig_name:
                continue
            act = np.rint(wfdb.rdrecord(path, channel_names=["Activity_Annotations"]).p_signal[:, 0]).astype(int)
            for x in g.itertuples():
                seg = act[x.win_start: x.win_start + int(round(x.win_len_s * 1000))]
                checked += 1
                mixed += int(len(np.unique(seg)) != 1 or seg[0] != x.label)
        rows.append({"windows": tag, "n_ppg": len(w), "n_ref": len(r), "matched": int((m._merge == "both").sum()),
                     "label_mismatch": int((m.label_x != m.label_y).sum()), "overlapping": overl,
                     "annotated_windows_checked": checked, "spanning_two_labels": mixed,
                     "unannotated_windows": int((w.label == -1).sum()),
                     "unannotated_records": " ".join(sorted(w[w.label == -1].rid.unique()))})
    return pd.DataFrame(rows)


def truncation(d, a):
    rows = []
    w8, w12 = (pd.read_csv(p) for p in (f"{d}/windows_rest.csv", f"{a}/windows_rest_post1200.csv"))
    K = KEY + ["channel"]
    j = w8[s_clean(w8)].set_index(K).join(w12[s_clean(w12)].set_index(K), rsuffix="_1200", how="inner")
    for ch, g in j.groupby(level="channel"):
        rr = 60000 / g.HR
        nr8, nr12 = g.reb_rise_frac < 0.05, g.reb_rise_frac_1200 < 0.05
        for lo, hi in ((0, 60), (60, 70), (70, 80), (80, 90), (90, 250), (0, 250)):
            m = g.HR.between(lo, hi, inclusive="right")
            rows.append({"channel": ch, "HR_bin": f"{lo}-{hi}" if hi < 250 else ("all" if lo == 0 else f">{lo}"),
                         "n": int(m.sum()),
                         "rebound_span_cut_by_800ms_end": float((g.ECG_S_ms + 550 > 799)[m].mean()),
                         "no_rebound_800": float(nr8[m].mean()), "no_rebound_1200": float(nr12[m].mean()),
                         "rebound_flips_no_to_yes": int((nr8 & ~nr12)[m].sum()),
                         "PW50_missing_800": float(g.PW50_frac[m].isna().mean()),
                         "PW50_missing_1200": float(g.PW50_frac_1200[m].isna().mean()),
                         "median_RR_ms": float(rr[m].median())})
    return pd.DataFrame(rows)


def reference_hr_slopes(d):
    r = subj(pd.read_csv(f"{d}/reference_all_20s.csv"))
    r["HR"] = 60000 / r.RR_ms
    r["S2_to_notch"] = r.cnap_notch_ms - r.pcg_QS2_ms
    q, c, s1 = r[r.pcg_ok], r[r.cnap_ok == True], r[r.pcg_s1_ok == True]  # noqa: E712
    rows = []
    for name, g, y, weissler in [("PCG QS2", q, "pcg_QS2_ms", "-2.0 to -2.1"), ("PCG S1", s1, "pcg_S1_ms", "~ -0.4 (PEP)"),
                                 ("PCG S1-S2", s1, "pcg_S1S2_ms", "-1.6 to -1.7 (LVET)"),
                                 ("CNAP ET", c, "cnap_ET_ms", "-1.6 to -1.7 (LVET)"), ("CNAP foot", c, "cnap_foot_ms", ""),
                                 ("CNAP notch", c, "cnap_notch_ms", ""),
                                 ("CNAP ET, minimum notches", c[c.cnap_notch_type == "minimum"], "cnap_ET_ms", "")]:
        s = within_slope(g, "HR", y, n_boot=500)
        rows.append({"fiducial": name, "slope_ms_per_bpm": s["beta"], "lo": s["beta_lo"], "hi": s["beta_hi"],
                     "rmcorr": s["r"], "n_rec": s["n_rec"], "expected (Weissler)": weissler})
    rows.append({"fiducial": "within-record SD, S2 to CNAP notch (ms)", "slope_ms_per_bpm": c.groupby("rid").S2_to_notch.std().median()})
    rows.append({"fiducial": "within-record SD, PCG QS2 (ms)", "slope_ms_per_bpm": q.groupby("rid").pcg_QS2_ms.std().median()})
    rows.append({"fiducial": "S2 split-half noise SD (ms)", "slope_ms_per_bpm": q.pcg_split_ms.mean() * np.sqrt(np.pi / 2) / 2})
    rows.append({"fiducial": "share of QS2 on its search ceiling", "slope_ms_per_bpm": float((q.pcg_QS2_ms >= np.minimum(0.75 * q.RR_ms, 600) - 5).mean())})
    rows.append({"fiducial": "share of windows with HR > 120 bpm", "slope_ms_per_bpm": float((r.HR > 120).mean())})
    return pd.DataFrame(rows)


def s1_cross_sensor(d):
    r = subj(pd.read_csv(f"{d}/reference_all_20s.csv"))
    rows = []
    for side in ("ebL_", "ebR_"):
        g = r[(r.pcg_s1_ok == True) & (r[f"{side}s1_ok"] == True)]  # noqa: E712
        for x, y in (("pcg_S1_ms", f"{side}S1_ms"), ("pcg_QS2_ms", f"{side}QS2_ms"), ("pcg_S1S2_ms", f"{side}S1S2_ms")):
            s = within_slope(g, x, y, n_boot=300)
            rows.append({"pcg": x, "earbud": y, "rmcorr": s["r"], "n_rec": s["n_rec"], "n_win": s["n_win"]})
    return pd.DataFrame(rows)


def slope_bounds(d):
    w = pd.read_csv(f"{d}/windows_all_20s.csv")
    r = pd.read_csv(f"{d}/reference_all_20s.csv")
    rows = []
    for ch in ("PPG_Ear", "PPG_Finger"):
        g = w[(w.channel == ch) & (w.ok == True)].merge(r, on=KEY, suffixes=("", "_r"))  # noqa: E712
        g = g[g.pcg_ok]
        for x, y, gg in (("pcg_QS2_ms", "t_D_ms", g), ("pcg_S1S2_ms", "S_D_ms", g[g.pcg_s1_ok == True]),  # noqa: E712
                         ("pcg_QS2_ms", "S_D_ms", g)):
            s = record_sums(gg, x, y)
            rows.append({"channel": ch, "y": y, "x": x, "ols": s.sxy.sum() / s.sxx.sum(),
                         "reverse_bound": s.syy.sum() / s.sxy.sum(),
                         "rmcorr": s.sxy.sum() / np.sqrt(s.sxx.sum() * s.syy.sum())})
    return pd.DataFrame(rows)


def rebound_vs_hr(d):
    w = pd.read_csv(f"{d}/windows_all_20s.csv")
    w = w[s_clean(w)].assign(reb=lambda x: (x.reb_rise_frac >= 0.05).astype(float))
    rows = []
    for ch, g in w.groupby("channel"):
        for lo, hi in ((0, 70), (70, 85), (85, 100), (100, 115), (115, 250)):
            m = g.HR.between(lo, hi, inclusive="right")
            rows.append({"channel": ch, "HR_bin": f"{lo}-{hi}", "n": int(m.sum()), "rebound_present": g.reb[m].mean()})
        for label, gg in (("all HR", g), ("HR < 100", g[g.HR < 100])):
            s = within_slope(gg, "HR", "reb", n_boot=500)
            rows.append({"channel": ch, "HR_bin": f"within-record slope per bpm, {label}", "n": s["n_win"],
                         "rebound_present": s["beta"], "lo": s["beta_lo"], "hi": s["beta_hi"]})
    return pd.DataFrame(rows)


def cv_leakage(d):
    import validate_incremental as vi
    t = pd.read_csv(f"{d}/exp4_incremental/subject_features.csv", index_col=0)
    ov = t[t.Age.between(*vi.AGE_OVERLAP)]
    X = ov[["Age"] + [f"finger_{c}" for c in vi.GENERIC + vi.PWTA_D]].to_numpy(float)
    rng = np.random.default_rng(0)
    n_rep = vi.N_REP
    vi.N_REP = 5
    aucs = [vi.cv_score(X, rng.permutation(ov.HF.to_numpy()), "clf", seed=s)[0] for s in range(40)]
    vi.N_REP = n_rep
    return pd.DataFrame([{"test": "E1 finger M2 features, permuted HF labels (40 x 5x5-fold)",
                          "mean_AUROC": np.mean(aucs), "sd_AUROC": np.std(aucs), "expected": 0.5}])


def variance_sim():
    import validate_precision as vp
    rng = np.random.default_rng(1)
    sb, sd, sw = 10.0, 15.0, 12.0
    rows = []
    for s in range(300):
        b = rng.normal(0, sb)
        for sess in (1, 2):
            day = rng.normal(0, sd)
            for _ in range(rng.integers(8, 20)):
                rows.append({"cohort": "HC", "subject": f"S{s}", "session": sess, "x": b + day + rng.normal(0, sw)})
    for s in range(300):
        b, day = rng.normal(0, 2 * sb), rng.normal(0, sd)
        for _ in range(12):
            rows.append({"cohort": "HFC", "subject": f"H{s}", "session": 1, "x": b + day + rng.normal(0, sw)})
    o = vp.components(pd.DataFrame(rows), "x", set())
    k = o["k_median"]
    return pd.DataFrame([{"quantity": q, "estimated": o[c], "true": t} for q, c, t in [
        ("sd_within_window", "sd_within_window", sw), ("sd_day", "sd_day", sd), ("sd_between_HC", "sd_between_HC", sb),
        ("sd_between_HF", "sd_between_HF", 2 * sb),
        ("R_session_HC", "R_session_HC", sb ** 2 / (sb ** 2 + sd ** 2 + sw ** 2 / k))]])


def sensitivity_summary(d, a):
    rows = []
    for tag in ("primary", "post1200", "annotated", "post1200_annotated", "steady"):
        p = (lambda e, full: f"{d}/{full}") if tag == "primary" else (lambda e, full, t=tag: f"{a}/{e}_{t}")
        row = {"variant": tag}
        f3 = p("exp3", "exp3_flattening") + "/primary.csv"
        if os.path.exists(f3):
            x = pd.read_csv(f3).iloc[0]
            row.update(exp3_rho=x.rho, exp3_p_one_sided=x.p_one_sided, exp3_n=x.n)
        f4 = p("exp4", "exp4_incremental") + "/incremental.csv"
        if os.path.exists(f4):
            e1 = pd.read_csv(f4)
            e1 = e1[e1.endpoint.str.startswith("E1")].set_index("site")
            row.update(E1_finger_M1=e1.loc["finger", "M1_age+generic"], E1_finger_delta=e1.loc["finger", "delta_M2_M1"],
                       E1_ear_delta=e1.loc["ear", "delta_M2_M1"])
        f5 = p("exp5", "exp5_precision") + "/precision_power.csv"
        if os.path.exists(f5):
            x = pd.read_csv(f5).set_index(["channel", "feature"])
            row.update(R_SD_ear=x.loc[("PPG_Ear", "S_D_ms"), "R_session_HC"], R_SD_finger=x.loc[("PPG_Finger", "S_D_ms"), "R_session_HC"],
                       R_ECGS_ear=x.loc[("PPG_Ear", "ECG_S_ms"), "R_session_HC"],
                       power_SD_finger_HF=x.loc[("PPG_Finger", "S_D_ms"), "power_rho0.5_HF_auricle"])
        rows.append(row)
    return pd.DataFrame(rows)


def _ensemble(rec_cache, rid, win_start):
    if rid not in rec_cache:
        rec = io.load_record(rid, channels=("ECG", "NIBP", "Digital_Stethoscope"))
        rp, _ = ecg.detect_r_peaks(rec.signals["ECG"], rec.fs)
        rec_cache[rid] = (rec, rp, reference.sound_envelope(rec.signals["Digital_Stethoscope"], rec.fs))
    return rec_cache[rid]


def figures(d, a):
    r = pd.read_csv(f"{d}/reference_all_20s.csv")
    cache = {}
    c = r[r.cnap_ok == True]  # noqa: E712
    pick = pd.concat([c[c.cnap_notch_type == "minimum"].sample(6, random_state=1),
                      c[c.cnap_notch_type == "inflection"].sample(6, random_state=2)])
    fig, axs = plt.subplots(4, 3, figsize=(15, 13))
    for ax, x in zip(axs.ravel(), pick.itertuples()):
        rec, rp, env = _ensemble(cache, x.rid, x.win_start)
        stop = x.win_start + 20 * int(rec.fs)
        beats, _ = reference.window_beats(rp, x.win_start, stop, rec.n, rec.fs)
        beats = beats[beats + int(reference.CNAP_POST_MS) <= rec.n]
        t, seg = reference._segments(rec.signals["NIBP"], beats, rec.fs, reference.CNAP_POST_MS)
        _, v = reference._segments(rec.cnap_valid.astype(float), beats, rec.fs, reference.CNAP_POST_MS)
        P = seg[(v == 1).all(1)].mean(0)
        _, es = reference._segments(env, beats, rec.fs, reference.CNAP_POST_MS)
        ax.plot(t, P, "k")
        ax2 = ax.twinx()
        ax2.plot(t, es.mean(0), color="tab:orange", alpha=.5)
        for col, colour in (("cnap_foot_ms", "b"), ("cnap_peak_ms", "m"), ("cnap_notch_ms", "r"), ("pcg_QS2_ms", "tab:orange")):
            ax.axvline(getattr(x, col), color=colour, ls="--")
        ax.set_xlim(-100, 1200)
        ax.set_title(f"{x.rid} label {x.label} HR {60000 / x.RR_ms:.0f} {x.cnap_notch_type} ET {x.cnap_ET_ms:.0f}", fontsize=9)
    fig.suptitle("CNAP ensemble (black) with foot/peak/notch (blue/magenta/red) and PCG envelope + S2 (orange)", fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{a}/fig_cnap_fiducials.png", dpi=70)
    plt.close(fig)

    q = r[r.pcg_ok].assign(HR=lambda x: 60000 / x.RR_ms)
    pick = pd.concat([q[q.HR > 100].sample(4, random_state=3), q[q.pcg_s2_snr < 3.5].sample(4, random_state=4),
                      q[q.rid.str.startswith("HFC")].sample(4, random_state=5)])
    fig, axs = plt.subplots(4, 3, figsize=(15, 11))
    for ax, x in zip(axs.T.ravel(), pick.itertuples()):
        rec, rp, env = _ensemble(cache, x.rid, x.win_start)
        beats, _ = reference.window_beats(rp, x.win_start, x.win_start + 20 * int(rec.fs), rec.n, rec.fs)
        t, seg = reference._segments(env, beats, rec.fs)
        mx = seg.max(1)
        ax.plot(t, seg[mx <= reference.SND_ARTEFACT_X * np.median(mx)].mean(0), "k")
        ax.axvline(x.pcg_S1_ms, color="b", ls="--")
        ax.axvline(x.pcg_QS2_ms, color="r", ls="--")
        ax.axvline(x.RR_ms, color="gray", lw=3, alpha=.3)
        ax.set_title(f"{x.rid} label {x.label} HR {x.HR:.0f} SNR {x.pcg_s2_snr:.1f} split {x.pcg_split_ms:.0f}", fontsize=9)
    fig.suptitle("PCG envelope ensembles: S1 (blue), S2 (red), next R (grey); columns = HR > 100, low SNR, HF", fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{a}/fig_pcg_s1_s2.png", dpi=70)
    plt.close(fig)


def checks(d, a):
    import validate_construct as vc
    os.makedirs(f"{a}/exp1_annotated", exist_ok=True)
    vc.run(f"{d}/windows_all_20s.csv", f"{d}/reference_all_20s.csv", "annotated_only", f"{a}/exp1_annotated",
           labels=[0, 1, 2, 3, 4])
    tables = {"window_integrity": window_integrity(d), "truncation": truncation(d, a),
              "reference_hr_slopes": reference_hr_slopes(d), "s1_cross_sensor": s1_cross_sensor(d),
              "slope_bounds": slope_bounds(d), "rebound_vs_hr": rebound_vs_hr(d), "cv_leakage": cv_leakage(d),
              "variance_sim": variance_sim(), "sensitivity_summary": sensitivity_summary(d, a)}
    with open(f"{a}/audit.md", "w") as fh:
        for name, t in tables.items():
            t.to_csv(f"{a}/{name}.csv", index=False)
            fh.write(f"## {name}\n\n{t.round(4).to_markdown(index=False)}\n\n")
    figures(d, a)
    print(open(f"{a}/audit.md").read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["variants", "checks"])
    ap.add_argument("--dir", default="outputs/validation")
    a = ap.parse_args()
    audit = os.path.join(a.dir, "audit")
    os.makedirs(audit, exist_ok=True)
    (variants if a.what == "variants" else checks)(a.dir, audit)


if __name__ == "__main__":
    main()
