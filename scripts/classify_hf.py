"""Heart failure (HFC cohort) vs no heart failure (HC cohort) discrimination from PWTA features.

Subject-level features come from run_batch.py output (current default pipeline). Two QC tiers:
  S-tier  windows with a clean, stable S wave (D not required): ECG-S, nSWI, HR, and the fraction
          of windows with no D wave (`no_rebound_frac`: no rebound, or no trough before it; broader than
          Experiment 3's reb_rise_frac < 0.05)
  D-tier  fully ok windows: S-D, SWS, DWI/SWI, D sharpness
Window medians -> record means -> subject means (healthy subjects have up to two sessions).

Reports:
  1. univariate AUROC (bootstrap 95% CI) per feature and PPG site, oriented in the direction the
     ArterioWave papers predict for HF where one exists
  2. cross-validated logistic regression (repeated stratified 5-fold), per site and combined
  3. age confounding: age-only AUROC, AUROC in the age-overlap subset, and CV age vs age+features
  4. age-robust checks: age dependence of each feature within healthy controls, and association of
     each feature with LVEF *within* the HF cohort (where age and LVEF are nearly uncorrelated),
     raw and age-adjusted (rank partial correlation)

Usage: python scripts/classify_hf.py outputs/windows_rest.csv [--out outputs/hf_classification]
"""
import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
warnings.filterwarnings("ignore", category=RuntimeWarning)

S_FEATURES = ["ECG_S_ms", "nSWI", "HR", "no_rebound_frac"]
D_FEATURES = ["S_D_ms", "SWS", "DWI_over_SWI", "D_sharpness"]
# +1: higher in HF expected, -1: lower in HF expected, 0: no prior from the papers
PRIOR = {"ECG_S_ms": +1, "S_D_ms": -1, "SWS": +1, "nSWI": -1, "no_rebound_frac": +1, "D_sharpness": -1,
         "DWI_over_SWI": 0, "HR": 0, "Age": +1}
SITES = {"PPG_Ear": "ear", "PPG_Finger": "finger"}


def subject_features(df, cfg_split_s=10.0):
    df = df[df.ppg_flat_frac <= 0.5]
    s_ok = ((df.n_acc >= 10) & (df.n_acc / df.n_total.where(df.n_total > 0) >= 0.6)
            & (df.S_found == True) & (df.split_dECG_S_ms <= cfg_split_s))  # noqa: E712
    s = df[s_ok].assign(no_rebound=lambda x: (x.D_found != True).astype(float))  # noqa: E712
    d = df[df.ok == True]  # noqa: E712
    rec_s = s.groupby(["channel", "rid"]).agg(
        ECG_S_ms=("ECG_S_ms", "median"), nSWI=("nSWI", "median"), HR=("HR", "median"),
        no_rebound_frac=("no_rebound", "mean"), subject=("subject", "first"))
    rec_d = d.groupby(["channel", "rid"])[D_FEATURES].median()
    rec = rec_s.join(rec_d, how="left").reset_index()
    subj = rec.groupby(["channel", "subject"])[S_FEATURES + D_FEATURES].mean()
    wide = subj.unstack(0)
    wide.columns = [f"{SITES[ch]}_{m}" for m, ch in wide.columns]
    demo = df.groupby("subject").agg(cohort=("cohort", "first"), Age=("Age", "first"), Gender=("Gender", "first"))
    out = demo.join(wide, how="left")
    out["HF"] = (out.cohort == "HFC").astype(int)
    return out


def auc_ci(y, x, n_boot=2000, seed=0):
    m = ~np.isnan(x)
    y, x = y[m], x[m]
    if len(np.unique(y)) < 2:
        return np.nan, np.nan, np.nan, int(m.sum()), int(y.sum())
    auc = roc_auc_score(y, x)
    rng = np.random.default_rng(seed)
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    boots = []
    for _ in range(n_boot):
        idx = np.r_[rng.choice(pos, len(pos)), rng.choice(neg, len(neg))]
        boots.append(roc_auc_score(y[idx], x[idx]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return auc, lo, hi, len(y), int(y.sum())


def univariate(S, label):
    rows = []
    y = S.HF.values
    for col in [c for c in S.columns if c.split("_", 1)[-1] in PRIOR or c == "Age"]:
        feat = col if col == "Age" else col.split("_", 1)[1]
        sign = PRIOR.get(feat, 0)
        x = S[col].values.astype(float)
        auc, lo, hi, n, npos = auc_ci(y, x if sign >= 0 else -x)
        rows.append({"subset": label, "feature": col, "direction": {1: "HF higher", -1: "HF lower", 0: "HF higher (no prior)"}[sign],
                     "AUROC": auc, "CI_lo": lo, "CI_hi": hi, "n": n, "n_HF": npos})
    return pd.DataFrame(rows)


def cv_auc(S, cols, n_repeats=50, seed=0):
    """Repeated stratified 5-fold CV AUROC. Subjects missing every feature in `cols` are dropped;
    remaining gaps (e.g. no D-tier window) are median-imputed inside each training fold."""
    X = S[cols].values.astype(float)
    keep = ~np.all(np.isnan(X), axis=1)
    X, y = X[keep], S.HF.values[keep]
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=n_repeats, random_state=seed)
    aucs = []
    for rep in range(n_repeats):
        pred = np.zeros(len(y))
        for k, (tr, te) in enumerate(list(cv.split(X, y))[rep * 5:(rep + 1) * 5]):
            model.fit(X[tr], y[tr])
            pred[te] = model.predict_proba(X[te])[:, 1]
        aucs.append(roc_auc_score(y, pred))
    return {"n": int(keep.sum()), "n_HF": int(y.sum()), "cv_AUROC_mean": np.mean(aucs),
            "cv_AUROC_p2.5": np.percentile(aucs, 2.5), "cv_AUROC_p97.5": np.percentile(aucs, 97.5)}


def _partial_spearman(x, y, z):
    d = pd.DataFrame({"x": x, "y": y, "z": z}).dropna()
    if len(d) < 6:
        return np.nan, len(d)
    r = d.rank()
    rx = r.x - np.polyval(np.polyfit(r.z, r.x, 1), r.z)
    ry = r.y - np.polyval(np.polyfit(r.z, r.y, 1), r.z)
    return stats.pearsonr(rx, ry)[0], len(d)


def age_robust(S, lvef):
    hc, hf = S[S.HF == 0], S[S.HF == 1].assign(LVEF=lvef)
    rows = []
    for col in [c for c in S.columns if c.split("_", 1)[0] in ("ear", "finger")]:
        a = hc[[col, "Age"]].dropna()
        b = hf[[col, "LVEF"]].dropna()
        r_ef = stats.spearmanr(b[col], b.LVEF) if len(b) > 5 else None
        pr, n = _partial_spearman(hf[col], hf.LVEF, hf.Age)
        rows.append({"feature": col, "HC_rho_age": stats.spearmanr(a[col], a.Age).statistic if len(a) > 5 else np.nan,
                     "HC_n": len(a), "HF_rho_LVEF": r_ef.statistic if r_ef else np.nan,
                     "HF_p": r_ef.pvalue if r_ef else np.nan, "HF_rho_LVEF_age_adj": pr, "HF_n": n})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(a.csv), "hf_classification")
    os.makedirs(out, exist_ok=True)
    S = subject_features(pd.read_csv(a.csv))
    S.to_csv(os.path.join(out, "subject_features.csv"))

    lo_age, hi_age = S.loc[S.HF == 0, "Age"].quantile(0.5), S.loc[S.HF == 1, "Age"].max()
    overlap = S[(S.Age >= S.loc[S.HF == 1, "Age"].min()) & (S.Age <= S.loc[S.HF == 0, "Age"].max())
                & (S.Age >= 28)]
    uni = pd.concat([univariate(S, "all subjects"), univariate(overlap, "age 28-57 overlap")])
    uni.to_csv(os.path.join(out, "univariate_auroc.csv"), index=False)

    wave = lambda site, feats: [f"{site}_{f}" for f in feats]  # noqa: E731
    pre_spec = ["ECG_S_ms", "SWS", "S_D_ms", "nSWI", "D_sharpness", "no_rebound_frac"]
    models = {
        "finger: pre-specified PWTA features": wave("finger", pre_spec),
        "ear: pre-specified PWTA features": wave("ear", pre_spec),
        "ear+finger: pre-specified PWTA features": wave("ear", pre_spec) + wave("finger", pre_spec),
        "finger: SWS only": ["finger_SWS"],
        "ear: SWS only": ["ear_SWS"],
        "age only": ["Age"],
        "age + finger PWTA": ["Age"] + wave("finger", pre_spec),
        "age + ear PWTA": ["Age"] + wave("ear", pre_spec),
    }
    cv_rows = []
    for subset_name, sub in (("all subjects", S), ("age 28-57 overlap", overlap)):
        for name, cols in models.items():
            cv_rows.append({"subset": subset_name, "model": name, **cv_auc(sub, cols)})
    cvdf = pd.DataFrame(cv_rows)
    cvdf.to_csv(os.path.join(out, "cv_models.csv"), index=False)
    from pwta import io  # local import: keeps the module importable without the package on sys.path
    ar = age_robust(S, io.load_demographics().reindex(S.index)["LVEF"])
    ar.to_csv(os.path.join(out, "age_robust_checks.csv"), index=False)

    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 200)
    print(f"subjects: {len(S)} ({S.HF.sum()} HF, {(S.HF == 0).sum()} HC); "
          f"age HC median {S.loc[S.HF == 0, 'Age'].median():.0f} (max {S.loc[S.HF == 0, 'Age'].max():.0f}), "
          f"HF median {S.loc[S.HF == 1, 'Age'].median():.0f}; overlap subset n={len(overlap)} ({overlap.HF.sum()} HF)")
    print("\n== univariate (subject level)")
    print(uni.sort_values(["subset", "AUROC"], ascending=[True, False]).round(3).to_string(index=False))
    print("\n== cross-validated logistic regression (5-fold x 50)")
    print(cvdf.round(3).to_string(index=False))
    print("\n== age-robust checks (feature vs age in HC; feature vs LVEF within HF)")
    print(ar.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
