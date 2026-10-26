"""Experiment 1 (docs/VALIDATION.md): is the PPG D wave an end-systolic event?

References: PCG S2 (QS2 = R to S2, aortic closure), earbud S2 (reference check), CNAP peripheral
ejection time (foot to dicrotic notch). The PPG dicrotic rebound (t_reb_ms) is the positive control.

Usage: python scripts/validate_construct.py   (defaults: outputs/validation/{windows,reference}_*.csv)
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import s_clean  # noqa: E402
from vstats import paired_slope_diff, within_slope  # noqa: E402

SITES = {"PPG_Ear": "ear", "PPG_Finger": "finger"}
KEY = ["rid", "win_start"]


def weissler(hr, male):
    """Weissler 1968 regressions (ms): QS2 and LVET on HR, by sex."""
    qs2 = np.where(male, 546 - 2.1 * hr, 549 - 2.0 * hr)
    lvet = np.where(male, 413 - 1.7 * hr, 418 - 1.6 * hr)
    return qs2, lvet


def load(windows, reference):
    w = pd.read_csv(windows)
    r = pd.read_csv(reference)
    w["s_clean"] = s_clean(w)
    w["ok"] = w.ok == True  # noqa: E712
    # best earbud per record (higher QC yield) as the second, independent S2 source
    yl = r.groupby("rid")[["ebL_ok", "ebR_ok"]].mean()
    side = np.where(yl.ebL_ok >= yl.ebR_ok, "ebL_", "ebR_")
    r = r.merge(pd.Series(side, index=yl.index, name="eb_side"), left_on="rid", right_index=True)
    for k in ("QS2_ms", "ok"):
        r[f"eb_{k}"] = np.where(r.eb_side == "ebL_", r[f"ebL_{k}"], r[f"ebR_{k}"])
    r["HR_ref"] = 60000.0 / r.RR_ms
    return w, r


def reference_validity(w, r):
    demo = w.drop_duplicates("rid").set_index("rid")[["subject", "cohort", "Gender"]]
    r = r.join(demo, on="rid")
    rows = []
    rec_yield = r.groupby("rid").pcg_ok.mean()
    rows.append({"check": "R1 PCG S2 QC yield (windows)", "value": r.pcg_ok.mean(),
                 "detail": f"{(rec_yield >= 0.5).sum()} records with >= 50% ok of {len(rec_yield)}"})
    both = r[r.pcg_ok & (r.eb_ok == True)]  # noqa: E712
    ws = within_slope(both, "pcg_QS2_ms", "eb_QS2_ms")
    rows.append({"check": "R2 earbud S2 vs PCG S2, within-record beta", "value": ws["beta"],
                 "detail": f"CI {ws['beta_lo']:.2f}-{ws['beta_hi']:.2f}; rmcorr {ws['r']:.2f}; "
                           f"{ws['n_rec']} rec / {ws['n_win']} win; median lag "
                           f"{(both.eb_QS2_ms - both.pcg_QS2_ms).median():.0f} ms"})
    ok = r[r.pcg_ok].copy()
    male = ok.Gender.str.lower().eq("male").to_numpy()
    q, lv = weissler(ok.HR_ref.to_numpy(), male)
    ok["qs2_resid"] = ok.pcg_QS2_ms - (q - 35)
    ok["et_resid"] = ok.cnap_ET_ms.where(ok.cnap_ok) - lv
    sess = ok.groupby(["rid", "cohort"])[["qs2_resid", "et_resid"]].median().reset_index()
    for c, g in sess.groupby("cohort"):
        rows.append({"check": f"R3 QS2 - (Weissler QS2 - 35), session median [{c}]", "value": g.qs2_resid.median(),
                     "detail": f"IQR {g.qs2_resid.quantile(.25):.0f} to {g.qs2_resid.quantile(.75):.0f} ms, n={len(g)}"})
        rows.append({"check": f"R3 CNAP ET - Weissler LVET, session median [{c}]", "value": g.et_resid.median(),
                     "detail": f"IQR {g.et_resid.quantile(.25):.0f} to {g.et_resid.quantile(.75):.0f} ms, n={g.et_resid.notna().sum()}"})
    ws = within_slope(ok[ok.cnap_ok == True], "pcg_QS2_ms", "cnap_ET_ms")  # noqa: E712
    rows.append({"check": "R4 CNAP ET on PCG QS2, within-record beta", "value": ws["beta"],
                 "detail": f"CI {ws['beta_lo']:.2f}-{ws['beta_hi']:.2f}; rmcorr {ws['r']:.2f}; {ws['n_rec']} rec"})
    gate = {
        "R1": r.pcg_ok.mean() >= 0.5 and (rec_yield >= 0.5).sum() >= 50,
        "R2": rows[1]["value"] >= 0.7 and rows[1]["value"] <= 1.3 and within_slope(both, "pcg_QS2_ms", "eb_QS2_ms")["r"] >= 0.6,
        "R3": all(abs(x["value"]) <= (50 if "QS2" in x["check"] else 60) for x in rows if x["check"].startswith("R3")),
        "R4": ws["beta_lo"] > 0,
    }
    return pd.DataFrame(rows), gate


def site_frame(w, r, ch):
    d = w[w.channel == ch].merge(r, on=KEY, suffixes=("", "_ref"))
    d = d[d.pcg_ok]
    return d


def tracking(w, r, partial):
    rows, diffs = [], []
    for ch, site in SITES.items():
        d = site_frame(w, r, ch)
        sets = {"t_D_ms": d[d.ok], "t_reb_ms": d[d.s_clean & d.t_reb_ms.notna()], "ECG_S_ms": d[d.s_clean]}
        for y, g in sets.items():
            for p in ((), partial):
                rows.append({"site": site, **within_slope(g, "pcg_QS2_ms", y, partial=p)})
        dd = d[d.ok]
        for p in ((), partial):
            rows.append({"site": site, **within_slope(dd, "pcg_QS2_ms", "t_reb_ms", partial=p), "y": "t_reb_ms (D windows)"})
            diffs.append({"site": site, "partial": "+".join(p) or "-",
                          **paired_slope_diff(dd, "pcg_QS2_ms", "t_D_ms", "t_reb_ms", partial=p)})
    return pd.DataFrame(rows), pd.DataFrame(diffs)


def decide(track, diffs, partial):
    out = {}
    p = "+".join(partial) or "-"
    for site in SITES.values():
        t = track[(track.site == site) & (track.partial == p)].set_index("y")
        bD, bR = t.loc["t_D_ms"], t.loc["t_reb_ms"]
        dif = diffs[(diffs.site == site) & (diffs.partial == p)].iloc[0]
        if bR.beta_lo >= 0.5 and bD.beta_lo >= 0.5 and dif.diff_lo <= 0 <= dif.diff_hi:  # failed control -> inconclusive
            v = "D tracks end-systole"
        elif bR.beta_lo >= 0.5 and (bD.beta_hi < 0.5 or dif.diff_hi < 0):
            v = "D does not track end-systole"
        else:
            v = "inconclusive"
        out[site] = (v, f"beta_D {bD.beta:.2f} [{bD.beta_lo:.2f}, {bD.beta_hi:.2f}], beta_reb {bR.beta:.2f} "
                        f"[{bR.beta_lo:.2f}, {bR.beta_hi:.2f}], D-reb {dif['diff']:.2f} [{dif.diff_lo:.2f}, {dif.diff_hi:.2f}]")
    return out


def interval(w, r):
    rows, between = [], []
    for ch, site in SITES.items():
        d = site_frame(w, r, ch)
        dd = d[d.ok]
        for x, g in (("cnap_ET_ms", dd[dd.cnap_ok == True]), ("pcg_S1S2_ms", dd[dd.pcg_s1_ok == True]),  # noqa: E712
                     ("RR_ms", dd)):
            rows.append({"site": site, **within_slope(g, x, "S_D_ms")})
        sess = dd[dd.cnap_ok == True].groupby("rid")[["S_D_ms", "cnap_ET_ms", "pcg_QS2_ms"]].median()  # noqa: E712
        rho = stats.spearmanr(sess.S_D_ms, sess.cnap_ET_ms)
        between.append({"site": site, "pair": "S-D vs CNAP ET (session medians)", "rho": rho.statistic,
                        "p": rho.pvalue, "n_sessions": len(sess)})
    return pd.DataFrame(rows), pd.DataFrame(between)


def posthoc(w, r):
    """Post hoc (not in the frozen spec): the S wave tracks S2 about as much as D does, so the
    end-systole-specific part is S-D. H_ES predicts S-D and S-to-rebound to move like ejection time.
    The S-to-rebound interval is the positive control for what slope these references can show."""
    rows = []
    for ch, site in SITES.items():
        d = site_frame(w, r, ch)
        d = d.assign(S_reb_ms=(d.t_reb_ms - d.ECG_S_ms).where(d.s_clean))
        dd, ds = d[d.ok], d[d.s_clean & d.t_reb_ms.notna()]
        for y, g in (("S_D_ms", dd), ("S_reb_ms", ds)):
            for x, gg in (("pcg_QS2_ms", g), ("pcg_S1S2_ms", g[g.pcg_s1_ok == True])):  # noqa: E712
                rows.append({"site": site, **within_slope(gg, x, y)})
        rows.append({"site": site, **paired_slope_diff(dd, "pcg_QS2_ms", "t_D_ms", "ECG_S_ms"),
                     "x": "pcg_QS2_ms", "y": "t_D_ms minus ECG_S_ms slopes (paired)"})
    return pd.DataFrame(rows)


def lags(w, r):
    rows = []
    per = {}
    for ch, site in SITES.items():
        d = site_frame(w, r, ch)
        d = d.assign(S_lag=(d.ECG_S_ms - d.pcg_QS2_ms).where(d.s_clean), D_lag=d.t_D_ms.where(d.ok) - d.pcg_QS2_ms,
                     reb_lag=d.t_reb_ms.where(d.s_clean) - d.pcg_QS2_ms,
                     reb_minus_D=(d.t_reb_ms - d.t_D_ms).where(d.ok),
                     S2_to_notch=(d.cnap_notch_ms - d.pcg_QS2_ms).where(d.cnap_ok == True))  # noqa: E712
        sess = d.groupby("rid")[["S_lag", "D_lag", "reb_lag", "reb_minus_D", "S2_to_notch"]].median()
        for c in sess:
            rows.append({"site": site, "quantity": c, "median": sess[c].median(), "q25": sess[c].quantile(.25),
                         "q75": sess[c].quantile(.75), "n_sessions": sess[c].notna().sum()})
        per[site] = d.set_index(KEY)
    e, f = per["ear"], per["finger"]
    both = e.index.intersection(f.index)
    for col, ok in (("ECG_S_ms", "s_clean"), ("t_D_ms", "ok"), ("t_reb_ms", "s_clean")):
        m = e.loc[both, ok] & f.loc[both, ok]
        diff = (f.loc[both, col] - e.loc[both, col])[m].dropna()
        rows.append({"site": "finger-ear", "quantity": col, "median": diff.median(), "q25": diff.quantile(.25),
                     "q75": diff.quantile(.75), "n_sessions": diff.index.get_level_values(0).nunique()})
    return pd.DataFrame(rows)


def run(windows, reference, tag, out, partial=("HR_ref",), labels=None, notch=None, s2_col=None):
    w, r = load(windows, reference)
    if labels is not None:
        w, r = w[w.label.isin(labels)], r[r.label.isin(labels)]
    if notch:
        r = r.assign(cnap_ok=r.cnap_ok & (r.cnap_notch_type == notch))
    if s2_col:
        r = r.assign(pcg_QS2_ms=r[s2_col])
    val, gate = reference_validity(w, r)
    track, diffs = tracking(w, r, partial)
    dec_p = decide(track, diffs, partial)
    dec_raw = decide(track, diffs, ())
    iv, between = interval(w, r)
    lg = lags(w, r)
    ph = posthoc(w, r)
    tables = [("reference_validity", val), ("tracking", track), ("tracking_diff", diffs), ("interval", iv),
              ("interval_between", between), ("lags", lg), ("posthoc_intervals", ph)]
    for name, t in tables:
        t.to_csv(os.path.join(out, f"{tag}_{name}.csv"), index=False)
    gate = {k: bool(v) for k, v in gate.items()}
    md = [f"# Experiment 1 [{tag}]\n", f"Reference gate: {gate} -> {'PASS' if all(gate.values()) else 'FAIL'}\n"]
    for site in SITES.values():
        md.append(f"- {site}: HR-partialled **{dec_p[site][0]}** ({dec_p[site][1]}); raw: {dec_raw[site][0]} ({dec_raw[site][1]})")
    for name, t in tables:
        md.append(f"\n## {name}\n\n{t.round(3).to_markdown(index=False)}\n")
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="outputs/validation")
    ap.add_argument("--out", default="outputs/validation/exp1_construct")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    W = lambda s: (os.path.join(a.dir, f"windows_{s}.csv"), os.path.join(a.dir, f"reference_{s}.csv"))  # noqa: E731
    parts = [run(*W("all_20s"), "all_20s", a.out),                                   # primary
             run(*W("all_20s"), "rest_only_20s", a.out, labels=[0]),                 # sensitivity
             run(*W("all_20s"), "notch_minimum_only", a.out, notch="minimum"),        # post hoc sensitivity
             run(*W("all_20s"), "s2_onset", a.out, s2_col="pcg_S2_onset_ms")]        # sensitivity
    with open(os.path.join(a.out, "exp1.md"), "w") as f:
        f.write("\n\n".join(parts))
    print("\n".join(p.split("\n## ")[0] for p in parts))


if __name__ == "__main__":
    main()
