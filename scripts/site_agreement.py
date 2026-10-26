"""Ear vs finger agreement of the D-only wave metrics at each level of the data hierarchy.

Only windows where the feature is extractable at both sites are paired (masks from feature_sweep.py).
The sites are not expected to match in absolute value; this quantifies how far one can stand in
for the other for ranking people and for tracking change.

  interval     raw paired windows: Spearman rho, Lin's CCC, finger - ear bias and SD
  within       deviations from the record mean (records with >= 3 paired windows): Spearman rho,
               Pearson r (= repeated-measures correlation), slope of finger on ear, SD at each site;
               plus the median of per-record rho (records with >= 5 paired windows)
  session      per-record medians: rho, CCC, SD of finger - ear
  subject      mean of a subject's session medians: rho, CCC
  day change   HC with both sessions: rho of (day 2 - day 1) ear vs finger, share with the same sign

Usage: python scripts/site_agreement.py outputs/windows_rest.csv outputs/sweep/windows_all_20s.csv
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import FEATS, extractable  # noqa: E402

KEY = ["rid", "subject", "session", "cohort", "win_start"]


def ccc(a, b):
    """Lin's concordance correlation coefficient."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return 2 * np.cov(a, b, bias=True)[0, 1] / (a.var() + b.var() + (a.mean() - b.mean()) ** 2)


def paired(df, ex, m):
    d = df[ex[m]]
    e = d[d.channel == "PPG_Ear"].set_index(KEY)[m]
    f = d[d.channel == "PPG_Finger"].set_index(KEY)[m]
    return pd.DataFrame({"e": e, "f": f}).dropna().reset_index()


def agreement(j):
    r = {"n_win": len(j), "n_rec": j.rid.nunique(), "n_subj": j.subject.nunique(),
         "win_rho": stats.spearmanr(j.e, j.f).statistic, "win_ccc": ccc(j.e, j.f),
         "bias_f_minus_e": (j.f - j.e).mean(), "sd_diff": (j.f - j.e).std()}

    jj = j[j.groupby("rid").e.transform("size") >= 3]
    dev = jj.groupby("rid")[["e", "f"]].transform(lambda s: s - s.mean())
    r.update(within_n_rec=jj.rid.nunique(), within_rho=stats.spearmanr(dev.e, dev.f).statistic,
             within_r=stats.pearsonr(dev.e, dev.f).statistic,
             within_slope_f_on_e=(dev.e * dev.f).sum() / (dev.e ** 2).sum(),
             within_sd_e=dev.e.std(), within_sd_f=dev.f.std())
    per = [stats.spearmanr(g.e, g.f).statistic for _, g in j.groupby("rid") if len(g) >= 5 and g.e.nunique() > 1]
    r.update(per_rec_n=len(per), per_rec_rho_median=np.nanmedian(per) if per else np.nan)

    s = j.groupby(["rid", "subject", "session", "cohort"])[["e", "f"]].median().reset_index()
    r.update(sess_n=len(s), sess_rho=stats.spearmanr(s.e, s.f).statistic, sess_ccc=ccc(s.e, s.f),
             sess_bias=(s.f - s.e).mean(), sess_sd_diff=(s.f - s.e).std())
    u = s.groupby("subject")[["e", "f"]].mean()
    r.update(subj_n=len(u), subj_rho=stats.spearmanr(u.e, u.f).statistic, subj_ccc=ccc(u.e, u.f))

    hc = s[s.cohort == "HC"].pivot_table(index="subject", columns="session", values=["e", "f"]).dropna()
    if len(hc) >= 5:
        de, dfg = hc[("e", 2)] - hc[("e", 1)], hc[("f", 2)] - hc[("f", 1)]
        r.update(day_n=len(hc), day_rho=stats.spearmanr(de, dfg).statistic,
                 day_sign_agree=(np.sign(de) == np.sign(dfg)).mean())
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("windows", nargs="+", help="run_batch.py outputs (each becomes one table)")
    ap.add_argument("--out", default="outputs/site_agreement")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md = []
    for path in a.windows:
        df = pd.read_csv(path)
        ex = extractable(df)
        rows = []
        for m in FEATS:
            j = paired(df, ex, m)
            if len(j) >= 10:
                rows.append({"metric": m, **agreement(j)})
        t = pd.DataFrame(rows).set_index("metric")
        tag = os.path.splitext(os.path.basename(path))[0]
        t.to_csv(os.path.join(a.out, f"{tag}.csv"))
        md.append(f"## {tag}\n\n{t.round(3).to_markdown()}\n\n")
    with open(os.path.join(a.out, "site_agreement.md"), "w") as f:
        f.writelines(md)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
