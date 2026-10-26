"""Experiment 4 (docs/VALIDATION.md): do the PWTA D-wave features add anything beyond age plus generic
pulse-wave-analysis features?

Blocks (subject level, rest windows): generic = PAT_foot, ECG-S (pulse arrival to max slope), crest
time, PW50/RR, SDPPG b/a, HR; PWTA-D = S-D, SWS, DWI/SWI, rebound strength.
Endpoints: E1 HF vs HC in the age-overlap subset (primary), E2 HF vs HC (all), E3 LVEF within HFC.
Models M0 age, M1 age + generic, M2 age + generic + PWTA-D; repeated CV; the null for M2 - M1 is
built by permuting the PWTA-D block across subjects.

Usage: python scripts/validate_incremental.py
"""
import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import RepeatedKFold, RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import s_clean  # noqa: E402
from pwta import io  # noqa: E402

warnings.filterwarnings("ignore")
SITES = {"PPG_Ear": "ear", "PPG_Finger": "finger"}
GENERIC = ["PAT_foot_ms", "ECG_S_ms", "CT_ms", "PW50_frac", "b_over_a", "HR"]
PWTA_D = ["S_D_ms", "SWS", "DWI_over_SWI", "reb_rise_frac"]
S_TIER = GENERIC + ["reb_rise_frac"]
AGE_OVERLAP = (28, 57)
N_REP, N_PERM = 20, 500


def subject_table(w):
    sc = w[s_clean(w)]
    ok = w[w.ok == True]  # noqa: E712
    rec = sc.groupby(["channel", "rid"])[S_TIER].median().join(
        ok.groupby(["channel", "rid"])[["S_D_ms", "SWS", "DWI_over_SWI"]].median())
    rec = rec.join(w.groupby(["channel", "rid"]).subject.first())
    subj = rec.reset_index().groupby(["channel", "subject"])[GENERIC + PWTA_D].mean()
    demo = io.load_demographics()
    return subj, demo[["Cohort", "Age", "LVEF"]]


def cv_score(X, y, task, seed=0):
    if task == "clf":
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=N_REP, random_state=seed)
    else:
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=1.0))
        cv = RepeatedKFold(n_splits=5, n_repeats=N_REP, random_state=seed)
    preds = np.full((N_REP, len(y)), np.nan)
    for k, (tr, te) in enumerate(cv.split(X, y)):
        model.fit(X[tr], y[tr])
        preds[k // 5, te] = model.predict_proba(X[te])[:, 1] if task == "clf" else model.predict(X[te])
    if task == "clf":
        return float(np.mean([roc_auc_score(y, p) for p in preds])), np.nan
    return (float(np.mean([r2_score(y, p) for p in preds])),
            float(np.mean([stats.spearmanr(y, p).statistic for p in preds])))


def _perm(X1, Xd, y, task, seed):
    rng = np.random.default_rng(seed)
    return cv_score(np.c_[X1, Xd[rng.permutation(len(Xd))]], y, task)[0]


def _perm_fl(X1, Xd, y, task, seed):
    """Freedman-Lane null (audit fix): permute only the part of PWTA-D that age + generic do not
    explain, so the permuted block keeps its correlation with the base model. Permuting whole rows
    (_perm) turns the block into pure noise, whose null delta sits below zero and biases p down.
    One permutation per missingness pattern keeps the PWTA-D columns' mutual correlation."""
    rng = np.random.default_rng(seed)
    Z = X1.copy()
    med = np.nanmedian(Z, axis=0)
    Z = np.where(np.isnan(Z), med, Z)
    Z = np.c_[np.ones(len(Z)), Z]
    Xp = Xd.copy()
    obs = ~np.isnan(Xd)
    for pattern in {tuple(c) for c in obs.T}:
        rows = np.asarray(pattern)
        cols = [j for j in range(Xd.shape[1]) if tuple(obs[:, j]) == pattern]
        if rows.sum() < 3:
            continue
        perm = rng.permutation(np.flatnonzero(rows))
        for j in cols:
            beta = np.linalg.lstsq(Z[rows], Xd[rows, j], rcond=None)[0]
            fit = Z[rows] @ beta
            res = Xd[rows, j] - fit
            Xp[rows, j] = fit + res[np.searchsorted(np.flatnonzero(rows), perm)]
    return cv_score(np.c_[X1, Xp], y, task)[0]


def evaluate(df, y, task, site, endpoint, jobs):
    g = [f"{site}_{c}" for c in GENERIC]
    p = [f"{site}_{c}" for c in PWTA_D]
    X0 = df[["Age"]].to_numpy(float)
    X1 = df[["Age"] + g].to_numpy(float)
    Xd = df[p].to_numpy(float)
    keep = ~np.isnan(X1[:, 1:]).all(axis=1)  # subjects with any generic feature at this site
    X0, X1, Xd, y = X0[keep], X1[keep], Xd[keep], y[keep]
    m0 = cv_score(X0, y, task)
    m1 = cv_score(X1, y, task)
    m2 = cv_score(np.c_[X1, Xd], y, task)
    null = np.array(Parallel(n_jobs=jobs)(delayed(_perm)(X1, Xd, y, task, s) for s in range(N_PERM)))
    null_fl = np.array(Parallel(n_jobs=jobs)(delayed(_perm_fl)(X1, Xd, y, task, s) for s in range(N_PERM)))
    delta = m2[0] - m1[0]
    p_perm = (1 + np.sum(null - m1[0] >= delta)) / (1 + N_PERM)
    p_fl = (1 + np.sum(null_fl - m1[0] >= delta)) / (1 + N_PERM)
    return {"endpoint": endpoint, "site": site, "n": int(keep.sum()), "n_pos_or_na": int(y.sum()) if task == "clf" else np.nan,
            "n_with_any_D": int((~np.isnan(Xd[:, :3])).any(axis=1).sum()),
            "M0_age": m0[0], "M1_age+generic": m1[0], "M2_+PWTA_D": m2[0], "delta_M2_M1": delta, "p_perm": p_perm,
            "null_delta_95pct": float(np.percentile(null - m1[0], 95)),
            "null_delta_median": float(np.median(null - m1[0])),
            "p_perm_freedman_lane": p_fl, "null_fl_delta_median": float(np.median(null_fl - m1[0])),
            "M1_spearman": m1[1], "M2_spearman": m2[1]}


def posthoc_univariate(t, out):
    """Post hoc (not in the frozen spec): univariate AUROC of each feature in the age-overlap subset, and
    how closely finger DWI/SWI tracks generic pulse width."""
    ov = t[t.Age.between(*AGE_OVERLAP)]
    rows = []
    for site in SITES.values():
        for f in GENERIC + PWTA_D:
            m = ov[[f"{site}_{f}", "HF"]].dropna()
            if m.HF.nunique() == 2:
                auc = roc_auc_score(m.HF, m[f"{site}_{f}"])
                rows.append({"site": site, "feature": f, "block": "PWTA-D" if f in PWTA_D else "generic",
                             "AUROC_HF_higher": auc, "AUROC_best_direction": max(auc, 1 - auc),
                             "n": len(m), "n_HF": int(m.HF.sum())})
    pd.DataFrame(rows).to_csv(os.path.join(out, "posthoc_univariate_age_overlap.csv"), index=False)
    corr = []
    for name, sub in (("all", t), ("age overlap", ov)):
        m = sub[["finger_DWI_over_SWI", "finger_PW50_frac"]].dropna()
        corr.append({"subset": name, "spearman_DWI_over_SWI_vs_PW50": stats.spearmanr(m.iloc[:, 0], m.iloc[:, 1]).statistic,
                     "n": len(m)})
    pd.DataFrame(corr).to_csv(os.path.join(out, "posthoc_dwi_vs_pw50.csv"), index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", default="outputs/validation/windows_rest.csv")
    ap.add_argument("--out", default="outputs/validation/exp4_incremental")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--posthoc-only", action="store_true", help="only the post hoc univariate tables")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    subj, demo = subject_table(pd.read_csv(a.windows))
    wide = subj.unstack(0)
    wide.columns = [f"{SITES[ch]}_{m}" for m, ch in wide.columns]
    t = demo.join(wide, how="inner")
    t["HF"] = (t.Cohort == "HFC").astype(int)
    t.to_csv(os.path.join(a.out, "subject_features.csv"))
    posthoc_univariate(t, a.out)
    if a.posthoc_only:
        return
    rows = []
    for site in SITES.values():
        ov = t[t.Age.between(*AGE_OVERLAP)]
        rows.append(evaluate(ov, ov.HF.to_numpy(), "clf", site, f"E1 HF vs HC, age {AGE_OVERLAP[0]}-{AGE_OVERLAP[1]}", a.jobs))
        rows.append(evaluate(t, t.HF.to_numpy(), "clf", site, "E2 HF vs HC, all", a.jobs))
        hf = t[(t.Cohort == "HFC") & t.LVEF.notna()]
        rows.append(evaluate(hf, hf.LVEF.to_numpy(float), "reg", site, "E3 LVEF within HFC (CV R^2)", a.jobs))
        print(pd.DataFrame(rows[-3:]).round(3).to_string(index=False), flush=True)
    res = pd.DataFrame(rows)
    res["adds_value"] = (res.endpoint.str.startswith("E1") & (res.delta_M2_M1 >= 0.05) & (res.p_perm < 0.05))
    res.to_csv(os.path.join(a.out, "incremental.csv"), index=False)
    e1 = res[res.endpoint.str.startswith("E1")].set_index("site")
    md = ["# Experiment 4: incremental value of PWTA-D over age + generic pulse shape\n",
          *[f"- {s}: E1 delta AUROC {e1.loc[s, 'delta_M2_M1']:.3f} (perm p {e1.loc[s, 'p_perm']:.3f}) -> "
            f"**{'PWTA-D adds value' if e1.loc[s, 'adds_value'] else 'no evidence of incremental value'}**"
            for s in SITES.values()],
          f"\n{res.round(3).to_markdown(index=False)}\n"]
    with open(os.path.join(a.out, "exp4.md"), "w") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
