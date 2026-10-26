"""Statistics shared by the validate_*.py scripts (conventions in docs/VALIDATION.md).

Within-record slope: X and Y are demeaned per record (optionally residualised on covariates within
the record first) and pooled: beta = sum(dx*dy) / sum(dx^2). CIs come from a cluster bootstrap over
subjects; records are kept whole, so the record-level sums are resampled.
"""
import numpy as np
import pandas as pd
from scipy import stats

N_BOOT = 2000


def record_sums(df, x, y, partial=(), group="rid", cluster="subject", min_n=4):
    """Per-record sums of the demeaned (and covariate-residualised) X and Y."""
    rows = []
    for rid, g in df.dropna(subset=[x, y, *partial]).groupby(group):
        if len(g) < min_n:
            continue
        X, Y = g[x].to_numpy(float), g[y].to_numpy(float)
        X, Y = X - X.mean(), Y - Y.mean()
        if partial:
            Z = g[list(partial)].to_numpy(float)
            Z = np.c_[np.ones(len(Z)), Z - Z.mean(axis=0)]
            if np.linalg.matrix_rank(Z) < Z.shape[1]:
                continue
            X = X - Z @ np.linalg.lstsq(Z, X, rcond=None)[0]
            Y = Y - Z @ np.linalg.lstsq(Z, Y, rcond=None)[0]
        rows.append({group: rid, cluster: g[cluster].iloc[0], "n": len(g),
                     "sxx": X @ X, "syy": Y @ Y, "sxy": X @ Y})
    return pd.DataFrame(rows)


def _beta_r(s):
    return s.sxy.sum() / s.sxx.sum(), s.sxy.sum() / np.sqrt(s.sxx.sum() * s.syy.sum())


def within_slope(df, x, y, partial=(), cluster="subject", min_n=4, n_boot=N_BOOT, seed=0):
    """Pooled within-record slope and rmcorr with cluster-bootstrap 95% CIs."""
    s = record_sums(df, x, y, partial, cluster=cluster, min_n=min_n)
    out = {"x": x, "y": y, "partial": "+".join(partial) or "-", "n_rec": len(s),
           "n_subj": s[cluster].nunique() if len(s) else 0, "n_win": int(s.n.sum()) if len(s) else 0}
    if len(s) < 3 or s.sxx.sum() == 0:
        return {**out, "beta": np.nan, "beta_lo": np.nan, "beta_hi": np.nan, "r": np.nan, "r_lo": np.nan, "r_hi": np.nan}
    b, r = _beta_r(s)
    S = s.groupby(cluster)[["sxx", "syy", "sxy"]].sum().to_numpy()
    idx = np.random.default_rng(seed).integers(0, len(S), (n_boot, len(S)))
    sxx, syy, sxy = S[idx].sum(axis=1).T
    with np.errstate(invalid="ignore", divide="ignore"):
        boots = np.c_[sxy / sxx, sxy / np.sqrt(sxx * syy)]
    lo, hi = np.nanpercentile(boots, [2.5, 97.5], axis=0)
    return {**out, "beta": b, "beta_lo": lo[0], "beta_hi": hi[0], "r": r, "r_lo": lo[1], "r_hi": hi[1]}


def paired_slope_diff(df, x, y1, y2, partial=(), cluster="subject", min_n=4, n_boot=N_BOOT, seed=0):
    """beta(y1 ~ x) - beta(y2 ~ x) on the same windows, with a paired cluster-bootstrap CI."""
    d = df.dropna(subset=[x, y1, y2, *partial])
    s1 = record_sums(d, x, y1, partial, cluster=cluster, min_n=min_n)
    s2 = record_sums(d, x, y2, partial, cluster=cluster, min_n=min_n)
    if len(s1) < 3:
        return {"diff": np.nan, "diff_lo": np.nan, "diff_hi": np.nan, "n_rec": len(s1)}
    s = s1.merge(s2[["rid", "sxy"]], on="rid", suffixes=("", "2"))
    est = (s.sxy.sum() - s.sxy2.sum()) / s.sxx.sum()
    S = s.groupby(cluster)[["sxx", "sxy", "sxy2"]].sum().to_numpy()
    idx = np.random.default_rng(seed).integers(0, len(S), (n_boot, len(S)))
    sxx, sxy, sxy2 = S[idx].sum(axis=1).T
    boots = (sxy - sxy2) / sxx
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"diff": est, "diff_lo": lo, "diff_hi": hi, "n_rec": len(s)}


def partial_spearman(x, y, covars=None):
    """Spearman correlation of x and y adjusted for covariates (Pearson r of rank residuals)."""
    d = pd.concat([pd.Series(x, name="x").reset_index(drop=True), pd.Series(y, name="y").reset_index(drop=True)]
                  + ([pd.DataFrame(covars).reset_index(drop=True)] if covars is not None else []), axis=1).dropna()
    n = len(d)
    if n < 5:
        return np.nan, np.nan, n
    R = d.rank()
    Z = np.c_[np.ones(n), R.drop(columns=["x", "y"]).to_numpy(float)]
    rx = R.x - Z @ np.linalg.lstsq(Z, R.x, rcond=None)[0]
    ry = R.y - Z @ np.linalg.lstsq(Z, R.y, rcond=None)[0]
    r = float(np.corrcoef(rx, ry)[0, 1])
    df = n - 2 - (Z.shape[1] - 1)
    t = r * np.sqrt(df / max(1e-12, 1 - r * r))
    return r, float(2 * stats.t.sf(abs(t), df)), n


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(1.0, run)
    return adj
