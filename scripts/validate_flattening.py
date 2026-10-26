"""Experiment 3 (docs/VALIDATION.md): D-wave flattening (missing / weak dicrotic rebound) as a feature.

Subject features from S-clean rest windows: reb_rise_frac (continuous rebound strength; lower =
flatter) and no_rebound_frac (share of windows with reb_rise_frac < 0.05), per site. Primary test:
within HFC, finger reb_rise_frac vs LVEF, partial Spearman adjusted for age (one-sided, negative).

Usage: python scripts/validate_flattening.py
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import s_clean  # noqa: E402
from pwta import io  # noqa: E402
from vstats import holm, partial_spearman  # noqa: E402

SITES = {"PPG_Ear": "ear", "PPG_Finger": "finger"}
AGE_OVERLAP = (28, 57)


def present(s):
    return s.notna() & ~s.astype(str).str.strip().str.lower().isin(["absent", "not found", "nan", ""])


def subject_table(w):
    w = w.assign(s_clean=s_clean(w))
    s = w[w.s_clean].assign(no_reb=lambda x: (x.reb_rise_frac < 0.05).astype(float))
    rec = s.groupby(["channel", "rid"]).agg(subject=("subject", "first"), reb_rise_frac=("reb_rise_frac", "median"),
                                            no_rebound_frac=("no_reb", "mean"), HR=("HR", "median"))
    rec = rec.join(w[w.ok == True].groupby(["channel", "rid"]).D_sharpness.median())  # noqa: E712
    subj = rec.reset_index().groupby(["channel", "subject"])[["reb_rise_frac", "no_rebound_frac", "HR", "D_sharpness"]].mean()
    wide = subj.unstack(0)
    wide.columns = [f"{SITES[ch]}_{m}" for m, ch in wide.columns]
    demo = io.load_demographics()
    out = demo[["Cohort", "Age", "LVEF", "group"]].join(wide, how="inner")
    out["beta_blocker"] = present(demo["Beta-adrenoceptor antagonist"]).reindex(out.index).astype(float)
    out["AF"] = (demo["Previous Atrial Fibrillation"].astype(str).str.lower() == "present").reindex(out.index).astype(float)
    out["CRT"] = (demo["Cardiac Resynchronisation Therapy"].astype(str).str.lower() == "present").reindex(out.index)
    out.loc[out.Cohort == "HC", ["beta_blocker", "AF"]] = 0.0
    return out


def auc_test(y, score):
    m = ~np.isnan(score)
    y, score = y[m], score[m]
    if len(np.unique(y)) < 2:
        return np.nan, np.nan, int(m.sum())
    u = stats.mannwhitneyu(score[y == 1], score[y == 0])
    return roc_auc_score(y, score), u.pvalue, int(m.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", default="outputs/validation/windows_rest.csv")
    ap.add_argument("--out", default="outputs/validation/exp3_flattening")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = subject_table(pd.read_csv(a.windows))
    t.to_csv(os.path.join(a.out, "subject_features.csv"))
    hf = t[(t.Cohort == "HFC") & t.LVEF.notna()]

    # primary
    r, p2, n = partial_spearman(hf.finger_reb_rise_frac, hf.LVEF, hf[["Age"]])
    p1 = p2 / 2 if r < 0 else 1 - p2 / 2
    prim = {"test": "PRIMARY finger reb_rise_frac vs LVEF | age (HFC)", "rho": r, "p_one_sided": p1, "p_two_sided": p2, "n": n}

    # confounder sensitivity for the primary
    sens = []
    for label, d, cov in [("age + HR", hf, ["Age", "finger_HR"]), ("age + beta-blocker", hf, ["Age", "beta_blocker"]),
                          ("age + AF history", hf, ["Age", "AF"]), ("age, CRT excluded", hf[~hf.CRT], ["Age"]),
                          ("unadjusted", hf, None)]:
        rr, pp, nn = partial_spearman(d.finger_reb_rise_frac, d.LVEF, d[cov] if cov else None)
        sens.append({"adjustment": label, "rho": rr, "p_two_sided": pp, "n": nn})
    sens = pd.DataFrame(sens)
    adj = sens[sens.adjustment != "unadjusted"]
    if r <= -0.4 and p1 < 0.05 and (adj.rho < 0).all() and (adj.rho.abs() >= 0.3).all():
        verdict = "supportive"
    elif r > -0.2:
        verdict = "not supported"
    else:
        verdict = "weak/inconclusive"

    # secondary family (Holm)
    sec = []
    for f in ("ear_reb_rise_frac", "finger_no_rebound_frac", "ear_no_rebound_frac"):
        rr, pp, nn = partial_spearman(hf[f], hf.LVEF, hf[["Age"]])
        sec.append({"test": f"{f} vs LVEF | age (HFC)", "stat": rr, "p": pp, "n": nn})
    ef = hf[(hf.LVEF >= 50) | (hf.LVEF < 40)]
    for site in SITES.values():
        au, pp, nn = auc_test((ef.LVEF >= 50).astype(int).to_numpy(), -ef[f"{site}_reb_rise_frac"].to_numpy())
        sec.append({"test": f"{site} flatness (-reb_rise_frac) AUROC, EF>=50 vs EF<40", "stat": au, "p": pp, "n": nn})
    ov = t[t.Age.between(*AGE_OVERLAP)]
    for site in SITES.values():
        au, pp, nn = auc_test((ov.Cohort == "HFC").astype(int).to_numpy(), -ov[f"{site}_reb_rise_frac"].to_numpy())
        sec.append({"test": f"{site} flatness AUROC, HF vs HC, age {AGE_OVERLAP[0]}-{AGE_OVERLAP[1]}", "stat": au, "p": pp, "n": nn})
    sec = pd.DataFrame(sec)
    sec["p_holm"] = holm(sec.p.fillna(1.0))

    # descriptive: age dependence within HC, D sharpness vs LVEF, group summaries
    desc = []
    hc = t[t.Cohort == "HC"]
    for f in ("finger_reb_rise_frac", "ear_reb_rise_frac", "finger_no_rebound_frac", "ear_no_rebound_frac"):
        m = hc[["Age", f]].dropna()
        rr = stats.spearmanr(m.Age, m[f])
        desc.append({"test": f"{f} vs age within HC", "rho": rr.statistic, "p": rr.pvalue, "n": len(m)})
    for site in SITES.values():
        rr, pp, nn = partial_spearman(hf[f"{site}_D_sharpness"], hf.LVEF, hf[["Age"]])
        desc.append({"test": f"{site} D_sharpness vs LVEF | age (HFC)", "rho": rr, "p": pp, "n": nn})
    desc = pd.DataFrame(desc)
    grp = t.groupby("group")[[f"{s}_{m}" for s in SITES.values() for m in ("reb_rise_frac", "no_rebound_frac")]].agg(
        ["median", "count"])

    md = ["# Experiment 3: D-wave flattening as a feature\n",
          f"Primary: {prim['test']}: rho = {r:.3f}, one-sided p = {p1:.4f} (two-sided {p2:.4f}), n = {n} -> **{verdict}**\n",
          f"## confounder sensitivity (primary)\n\n{sens.round(3).to_markdown(index=False)}\n",
          f"## secondary (Holm)\n\n{sec.round(4).to_markdown(index=False)}\n",
          f"## descriptive\n\n{desc.round(3).to_markdown(index=False)}\n",
          f"## by group\n\n{grp.round(3).to_markdown()}\n"]
    pd.DataFrame([prim]).to_csv(os.path.join(a.out, "primary.csv"), index=False)
    sens.to_csv(os.path.join(a.out, "sensitivity.csv"), index=False)
    sec.to_csv(os.path.join(a.out, "secondary.csv"), index=False)
    desc.to_csv(os.path.join(a.out, "descriptive.csv"), index=False)
    with open(os.path.join(a.out, "exp3.md"), "w") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
