"""Experiment 2 (docs/VALIDATION.md): why the ear loses the dicrotic rebound, and whether a principled
inverse filter recovers it.

  2a  ear vs finger rebound concordance in the same windows
  2b  trait (subject-level) and state (within-record HR / MAP) determinants of the ear rebound
  2c  transfer fit: is the ear pulse a Gaussian-blurred, shifted finger pulse?
  2d  Wiener deconvolution of the ear with a population blur (trained on HC session 1, applied
      ear-only to HC session 2 + HFC), then the unchanged D pick and QC

Usage: python scripts/validate_site_rebound.py
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy import stats
from scipy.ndimage import gaussian_filter1d
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import s_clean  # noqa: E402
from pwta import io, waves  # noqa: E402
from pwta.pipeline import Config, _verdict, process_record  # noqa: E402
from vstats import within_slope  # noqa: E402

CFG = Config()
SPEC = "sg:61:4"
REB_THR = CFG.d_min_prom_frac
SIGMAS_MS = np.arange(0, 62, 2)
SIGMAS_EXT_MS = np.arange(0, 162, 4)  # post hoc: the spec grid saturates at 60 ms
DELTAS_MS = np.arange(-150, 101, 2)
LAMBDAS = [1e-2, 1e-1, 1e-3]  # first = primary (fixed in docs/VALIDATION.md)
KEY = ["rid", "win_start"]


# ---------- 2c: transfer fit ----------
def fit_transfer(t_ms, xe, xf, rr_ms, fs, sigmas=SIGMAS_MS):
    """Best (sigma, delta, R^2) for xe(t) ~ g * G_sigma(xf)(t - delta) + c."""
    idx = np.flatnonzero((t_ms >= 50) & (t_ms <= min(rr_ms - 50, 640)))
    e = xe[idx] - xe[idx].mean()
    ee = e @ e
    shifts = np.round(DELTAS_MS * fs / 1000).astype(int)
    best = (np.nan, np.nan, -np.inf)
    for s in sigmas:
        yf = gaussian_filter1d(xf, s * fs / 1000, mode="nearest") if s else xf
        Y = yf[idx[None, :] - shifts[:, None]]
        Y = Y - Y.mean(axis=1, keepdims=True)
        r2 = (Y @ e) ** 2 / ((Y * Y).sum(axis=1) * ee)
        k = int(np.argmax(r2))
        if r2[k] > best[2]:
            best = (float(s), float(DELTAS_MS[k]), float(r2[k]))
    return best


def _fit_record(rid):
    _, store = process_record(rid, specs=(SPEC,), channels=("PPG_Ear", "PPG_Finger"), cfg=CFG, keep_ensembles="beats")
    out = []
    for (ch, _, ws), e in store.items():
        f = store.get(("PPG_Finger", SPEC, ws))
        if ch != "PPG_Ear" or f is None:
            continue
        fs = 1000.0 / (e.t_ms[1] - e.t_ms[0])
        s, d, r2 = fit_transfer(e.t_ms, e.x, f.x, e.rr_ms, fs)
        s2, d2, r22 = fit_transfer(e.t_ms, e.x, f.x, e.rr_ms, fs, SIGMAS_EXT_MS)
        out.append({"rid": rid, "win_start": ws, "sigma_ms": s, "delta_ms": d, "r2": r2,
                    "sigma_ext_ms": s2, "delta_ext_ms": d2, "r2_ext": r22})
    return out


# ---------- 2d: deconvolution ----------
def deconvolve(a, sigma_ms, lam, fs, pad=300):
    """Wiener inverse of a zero-phase Gaussian blur along the last axis."""
    a = np.atleast_2d(a)
    ap = np.pad(a, ((0, 0), (pad, pad)), mode="reflect")
    n = ap.shape[1]
    f = np.fft.rfftfreq(n, 1.0 / fs)
    H = np.exp(-2 * (np.pi * f * sigma_ms / 1000) ** 2)
    out = np.fft.irfft(np.fft.rfft(ap, axis=1) * (H / (H * H + lam)), n, axis=1)
    return out[:, pad:-pad]


def _metrics_row(d_mean, x_mean, d_beats, e, fs, base):
    m = waves.metrics(d_mean, x_mean, e.t_ms, e.rr_ms, fs, **CFG.pick_kw())
    row = {**base, **m}
    if len(d_beats) >= 6:
        h = [waves.metrics(d_beats[i::2].mean(axis=0), x_mean, e.t_ms, e.rr_ms, fs, **CFG.pick_kw()) for i in (0, 1)]
        row.update(split_dECG_S_ms=abs(h[0]["ECG_S_ms"] - h[1]["ECG_S_ms"]), split_dS_D_ms=abs(h[0]["S_D_ms"] - h[1]["S_D_ms"]))
    else:
        row.update(split_dECG_S_ms=np.nan, split_dS_D_ms=np.nan)
    row["ok"], row["reasons"] = _verdict(row, CFG)
    return row


def _deconv_record(rid, configs):
    rows, store = process_record(rid, specs=(SPEC,), channels=("PPG_Ear",), cfg=CFG, keep_ensembles="beats")
    base_rows = {r["win_start"]: r for r in rows}
    out = []
    for (_, _, ws), e in store.items():
        fs = 1000.0 / (e.t_ms[1] - e.t_ms[0])
        b = base_rows[ws]
        base = {k: b[k] for k in ("rid", "subject", "win_start", "ppg_flat_frac", "n_total", "n_acc")}
        out.append({**_metrics_row(e.d, e.x, e.d_beats, e, fs, base), "config": "baseline", "lam": 0.0, "sigma": 0.0})
        for name, sigma, lam in configs:
            db = deconvolve(e.d_beats, sigma, lam, fs)
            out.append({**_metrics_row(db.mean(axis=0), deconvolve(e.x, sigma, lam, fs)[0], db, e, fs, base),
                        "config": name, "lam": lam, "sigma": sigma})
    return out


def auc(y, x):
    m = ~(np.isnan(x) | np.isnan(y))
    return roc_auc_score(y[m], x[m]) if len(np.unique(y[m])) == 2 else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="outputs/validation")
    ap.add_argument("--out", default="outputs/validation/exp2_site_rebound")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md = ["# Experiment 2: ear vs finger rebound\n"]
    w = pd.read_csv(os.path.join(a.dir, "windows_rest.csv"))
    w["s_clean"] = s_clean(w)
    w["reb"] = w.reb_rise_frac >= REB_THR
    e = w[w.channel == "PPG_Ear"].set_index(KEY)
    f = w[w.channel == "PPG_Finger"].set_index(KEY)
    both = e.index[e.s_clean & f.loc[e.index, "s_clean"]]
    pair = pd.DataFrame({"cohort": e.loc[both, "cohort"], "subject": e.loc[both, "subject"],
                         "ear": e.loc[both, "reb"], "finger": f.loc[both, "reb"]})

    # 2a concordance
    rows = []
    for c, g in [("all", pair), *pair.groupby("cohort")]:
        n11 = int((g.ear & g.finger).sum()); n10 = int((g.ear & ~g.finger).sum())
        n01 = int((~g.ear & g.finger).sum()); n00 = int((~g.ear & ~g.finger).sum())
        p = stats.binomtest(min(n10, n01), n10 + n01, 0.5).pvalue if n10 + n01 else np.nan
        sub = g.groupby("subject")[["ear", "finger"]].mean()
        wil = stats.wilcoxon(sub.finger, sub.ear) if len(sub) > 5 else None
        rows.append({"cohort": c, "n_windows": len(g), "n_subjects": len(sub), "both": n11, "ear_only": n10,
                     "finger_only": n01, "neither": n00, "mcnemar_p": p,
                     "share_discordant_finger_only": n01 / max(1, n01 + n10),
                     "subj_median_ear": sub.ear.median(), "subj_median_finger": sub.finger.median(),
                     "subj_wilcoxon_p": wil.pvalue if wil else np.nan})
    conc = pd.DataFrame(rows)
    md.append(f"## 2a concordance (rest windows S-clean at both sites)\n\n{conc.round(3).to_markdown(index=False)}\n")

    # 2b trait
    demo = io.load_demographics()
    ref = pd.read_csv(os.path.join(a.dir, "reference_rest.csv"))
    mp = ref.groupby("rid").MAP.median()  # MAP does not depend on the notch, so no cnap_ok filter
    es = e[e.s_clean].reset_index()
    rec = es.groupby("rid").agg(subject=("subject", "first"), cohort=("cohort", "first"), ear_reb=("reb", "mean"),
                                ear_rise=("reb_rise_frac", "median"), HR=("HR", "median"), ear_amp=("PPG_amp", "median"))
    fr = f[f.s_clean].groupby("rid").reb.mean().rename("finger_reb")
    rec = rec.join(fr).join(mp.rename("MAP"))
    subj = rec.groupby("subject").agg({"cohort": "first", "ear_reb": "mean", "ear_rise": "mean", "HR": "mean",
                                       "ear_amp": "mean", "finger_reb": "mean", "MAP": "mean"})
    subj = subj.join(demo[["Age", "Gender", "Height (cm)", "Weight (kg)"]])
    subj["male"] = subj.Gender.str.lower().eq("male").astype(float)
    subj["BMI"] = subj["Weight (kg)"] / (subj["Height (cm)"] / 100) ** 2
    sc = pd.read_csv(os.path.join(io.DATA_ROOT, "sensor_coordinates.csv")).set_index("Participant")
    subj["ear_sensor_offset_cm"] = np.hypot(sc.PPG_Ear_X - sc.Left_Ear_X, sc.PPG_Ear_Y - sc.Left_Ear_Y).reindex(subj.index)
    rows = []
    for scope, g in (("all", subj), ("HC", subj[subj.cohort == "HC"]), ("HFC", subj[subj.cohort == "HFC"])):
        for v in ("Age", "male", "Height (cm)", "BMI", "HR", "MAP", "ear_amp", "finger_reb", "ear_sensor_offset_cm"):
            m = g[[v, "ear_reb"]].dropna()
            if len(m) >= 8 and m[v].nunique() > 1:
                r = stats.spearmanr(m[v], m.ear_reb)
                rows.append({"scope": scope, "covariate": v, "rho": r.statistic, "p": r.pvalue, "n": len(m)})
    trait = pd.DataFrame(rows)
    md.append(f"## 2b trait: Spearman of subject ear rebound fraction with covariates\n\n{trait.round(3).to_markdown(index=False)}\n")
    md.append(f"Ear-sensor offset from the ear landmark (HC): median {subj.ear_sensor_offset_cm.median():.2f} cm, "
              f"IQR {subj.ear_sensor_offset_cm.quantile(.25):.2f}-{subj.ear_sensor_offset_cm.quantile(.75):.2f} cm\n")

    # 2b state (within record, 20-s windows incl. manoeuvres)
    w20 = pd.read_csv(os.path.join(a.dir, "windows_all_20s.csv"))
    r20 = pd.read_csv(os.path.join(a.dir, "reference_all_20s.csv"))
    w20 = w20[s_clean(w20)].merge(r20[KEY + ["RR_ms", "MAP", "cnap_ok"]], on=KEY)
    w20["HR_ref"] = 60000 / w20.RR_ms
    rows = []
    for ch, g in w20.groupby("channel"):
        rows.append({"channel": ch, **within_slope(g, "HR_ref", "reb_rise_frac")})
        rows.append({"channel": ch, **within_slope(g, "MAP", "reb_rise_frac")})
        g = g.assign(reb=(g.reb_rise_frac >= REB_THR).astype(float))
        rows.append({"channel": ch, **within_slope(g, "HR_ref", "reb")})
    state = pd.DataFrame(rows)
    md.append(f"## 2b state: within-record slope of rebound strength / presence on HR (per bpm) and MAP (per mmHg)\n\n"
              f"{state.round(4).to_markdown(index=False)}\n")

    # 2c transfer fit
    rids = io.list_records()
    fits = pd.DataFrame([r for res in Parallel(n_jobs=a.jobs)(delayed(_fit_record)(rid) for rid in rids) for r in res])
    fits = fits.merge(pair.reset_index(), on=KEY)
    fits["session"] = fits.rid.str.split("_").str[2].astype(int)
    fits.to_csv(os.path.join(a.out, "transfer_fits.csv"), index=False)
    fr_ = fits[fits.finger]
    win_auc = auc((~fr_.ear).astype(float).to_numpy(), fr_.sigma_ms.to_numpy())
    sub = fr_.groupby("subject").agg(sigma=("sigma_ms", "median"), no_reb=("ear", lambda s: 1 - s.mean()),
                                     r2=("r2", "median"))
    sub_auc = auc((sub.no_reb > 0.5).astype(float).to_numpy(), sub.sigma.to_numpy())
    rho = stats.spearmanr(sub.sigma, sub.no_reb)
    tf = pd.DataFrame([{
        "n_windows": len(fits), "median_R2": fits.r2.median(), "q25_R2": fits.r2.quantile(.25),
        "share_R2_ge_0.95": (fits.r2 >= 0.95).mean(), "median_sigma_ms": fits.sigma_ms.median(),
        "median_delta_ms": fits.delta_ms.median(),
        "sigma_ear_reb (finger reb)": fr_[fr_.ear].sigma_ms.median(),
        "sigma_ear_noreb (finger reb)": fr_[~fr_.ear].sigma_ms.median(),
        "window_AUROC_sigma_for_ear_noreb": win_auc, "subject_AUROC_sigma": sub_auc,
        "subject_spearman_sigma_vs_noreb": rho.statistic, "n_subjects": len(sub)}])
    tf["share_sigma_at_grid_max"] = (fits.sigma_ms == SIGMAS_MS.max()).mean()
    tf["posthoc_ext_median_sigma_ms"] = fits.sigma_ext_ms.median()
    tf["posthoc_ext_median_R2"] = fits.r2_ext.median()
    tf["posthoc_ext_share_at_max"] = (fits.sigma_ext_ms == SIGMAS_EXT_MS.max()).mean()
    tf["posthoc_ext_subject_AUROC"] = auc((sub.no_reb > 0.5).astype(float).to_numpy(),
                                          fr_.groupby("subject").sigma_ext_ms.median().reindex(sub.index).to_numpy())
    smooth = tf.median_R2.iloc[0] >= 0.95
    explains = smooth and sub_auc >= 0.75
    md.append(f"## 2c transfer fit (ear ~ blurred, shifted finger)\n\n{tf.T.round(3).to_markdown()}\n\n"
              f"Decision: ear ≈ smoothed finger: **{smooth}**; smoothing explains rebound loss: **{explains}**\n")

    # 2d deconvolution
    train = fits[(fits.rid.str.startswith("HC")) & (fits.session == 1)]
    sigma_pop = float(train.sigma_ms.median())
    sigma_ext = float(train.sigma_ext_ms.median())
    configs = [(f"spec lam={lam:g}", sigma_pop, lam) for lam in LAMBDAS]
    if sigma_ext != sigma_pop:  # post hoc extended grid; skipped when it gives the same sigma
        configs.append(("posthoc ext-grid lam=0.01", sigma_ext, 1e-2))
    held = [rid for rid in rids if not (rid.startswith("HC") and rid.endswith("_1"))]
    dec = pd.DataFrame([r for res in Parallel(n_jobs=a.jobs)(delayed(_deconv_record)(rid, configs) for rid in held)
                        for r in res])
    dec.to_csv(os.path.join(a.out, "deconvolution_windows.csv"), index=False)
    # baseline must reproduce the pipeline
    chk = dec[dec.config == "baseline"].merge(e.reset_index()[KEY + ["S_D_ms", "ok"]], on=KEY, suffixes=("", "_pipe"))
    reproduces = bool(np.allclose(chk.S_D_ms, chk.S_D_ms_pipe, equal_nan=True) and (chk.ok == chk.ok_pipe).all())
    fin = f.reset_index()[KEY + ["S_D_ms", "ok", "HR"]].rename(columns={"S_D_ms": "fS_D", "ok": "f_ok", "HR": "fHR"})
    base = dec[dec.config == "baseline"].set_index(KEY)
    rows = []
    for name, sigma, lam in configs:
        c = dec[dec.config == name].set_index(KEY)
        c["native"] = base.loc[c.index, "ok"] == True  # noqa: E712
        c["ok"] = c.ok == True  # noqa: E712
        c["rescued"] = c.ok & ~c.native
        c = c.join(fin.set_index(KEY))
        okc = c[c.ok].reset_index()
        slope = within_slope(okc.assign(HR=okc.HR), "HR", "S_D_ms", n_boot=200)["beta"]
        slope0 = within_slope(base[base.ok == True].reset_index(), "HR", "S_D_ms", n_boot=200)["beta"]  # noqa: E712
        j = c[c.ok & (c.f_ok == True)].reset_index()  # noqa: E712
        j = j[j.groupby("rid").S_D_ms.transform("size") >= 3]
        dev = j.groupby("rid")[["S_D_ms", "fS_D"]].transform(lambda s: s - s.mean())
        resc = j.rescued.to_numpy()
        # original (pooled demeaning, native scored on its deconvolved S-D); kept for transparency
        rho_nat_pooled = stats.spearmanr(dev.S_D_ms[j.native.to_numpy()], dev.fS_D[j.native.to_numpy()]).statistic
        rho_res_pooled = stats.spearmanr(dev.S_D_ms[resc], dev.fS_D[resc]).statistic if resc.sum() > 5 else np.nan
        # audit fix: native windows scored on their pipeline S-D, each category demeaned on its own
        c["S_D_base"] = base.loc[c.index, "S_D_ms"]

        def cat_rho(g, col):
            g = g[g.groupby(level="rid")[col].transform("size") >= 3]
            d = g.groupby(level="rid")[[col, "fS_D"]].transform(lambda s: s - s.mean())
            return stats.spearmanr(d[col], d.fS_D).statistic if len(d) > 5 else np.nan, len(d)

        paired = c[c.f_ok == True]  # noqa: E712
        rho_nat, n_nat = cat_rho(paired[paired.native], "S_D_base")
        rho_res, n_res = cat_rho(paired[paired.rescued], "S_D_ms")
        kept = c[c.native & c.ok]
        shift = (kept.S_D_ms - kept.S_D_base).abs()
        resc_c = c[c.rescued]
        dy = c.ok.mean() - c.native.mean()
        # post hoc diagnostics: are rescued D picks like native ones (S-D level, offset to the finger)?
        nat_c = c[c.native & c.ok]
        row = {"config": name, "lambda": lam, "sigma_pop_ms": sigma, "n_held_out_windows": len(c),
               "SD_median_native": nat_c.S_D_base.median(), "SD_median_rescued": resc_c.S_D_ms.median(),
               "finger_minus_ear_SD_native": (nat_c.fS_D - nat_c.S_D_base).median(),
               "finger_minus_ear_SD_rescued": (resc_c.fS_D - resc_c.S_D_ms).median(),
               "yield_baseline": c.native.mean(), "yield_corrected": c.ok.mean(), "yield_gain_pp": 100 * dy,
               "n_rescued": int(c.rescued.sum()), "n_lost": int((c.native & ~c.ok).sum()),
               "split_SD_rescued_median_ms": resc_c.split_dS_D_ms.median(),
               "split_SD_native_median_ms": c[c.native & c.ok].split_dS_D_ms.median(),
               "SD_in_100_350_rescued": resc_c.S_D_ms.between(100, 350).mean(),
               "SD_HR_slope_corrected": slope, "SD_HR_slope_baseline": slope0,
               "rho_with_finger_native": rho_nat, "rho_with_finger_rescued": rho_res,
               "n_native_paired": n_nat, "n_rescued_paired": n_res,
               "rho_native_pooled_original": rho_nat_pooled, "rho_rescued_pooled_original": rho_res_pooled,
               "native_SD_shift_median_ms": shift.median(), "native_SD_shift_gt10ms": (shift > 10).mean()}
        row["rescued"] = bool(dy >= 0.15 and (rho_res >= rho_nat - 0.1) and row["split_SD_rescued_median_ms"] <= 2)
        rows.append(row)
    dt = pd.DataFrame(rows)
    md.append(f"## 2d deconvolution (sigma_pop from HC session 1 = {sigma_pop:.0f} ms; held out = HC session 2 + HFC)\n\n"
              f"Baseline reproduces the pipeline: **{reproduces}**\n\n{dt.T.round(3).to_markdown()}\n\n"
              f"Decision (primary lambda = {LAMBDAS[0]}): rescued = **{dt.rescued.iloc[0]}**\n")
    md[-1] = md[-1].replace(f"(sigma_pop from HC session 1 = {sigma_pop:.0f} ms;",
                            f"(sigma_pop from HC session 1 = {sigma_pop:.0f} ms, post hoc ext grid {sigma_ext:.0f} ms;")
    for name, t in [("concordance", conc), ("trait", trait), ("state", state), ("transfer_summary", tf),
                    ("deconvolution_summary", dt)]:
        t.to_csv(os.path.join(a.out, f"{name}.csv"), index=False)
    subj.to_csv(os.path.join(a.out, "subject_table.csv"))
    with open(os.path.join(a.out, "exp2.md"), "w") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
