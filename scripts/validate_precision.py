"""Experiment 5 (docs/VALIDATION.md): precision ceiling and power.

Variance components from rest windows of HC with two sessions (method of moments):
  sigma_w^2   pooled within-session variance between windows
  sigma_day^2 from Var(m2 - m1) = 2 sigma_day^2 + sigma_w^2 (1/k1 + 1/k2)
  sigma_b^2   Cov(m1, m2)
Reliability of one session of k windows R(k) = sigma_b^2 / (sigma_b^2 + sigma_day^2 + sigma_w^2/k).
HF scenario: sigma_b,HF^2 = Var_HF(session means) - sigma_day^2 - mean(sigma_w^2/k).
Attenuation rho_obs = rho_true * sqrt(R * R_LVEF), R_LVEF = 0.8 (assumed); Fisher-z sample sizes.

Usage: python scripts/validate_precision.py
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from feature_sweep import s_clean  # noqa: E402

S_FEATS = ["HR", "ECG_S_ms", "nSWI", "reb_rise_frac"]
D_FEATS = ["t_D_ms", "S_D_ms", "SWS", "DWI_over_SWI"]
R_LVEF = 0.8
TARGET_R = 0.8
Z_A, Z_B = stats.norm.ppf(0.975), stats.norm.ppf(0.8)


def n_required(rho_obs):
    return np.inf if rho_obs <= 0 else float(np.ceil(((Z_A + Z_B) / np.arctanh(rho_obs)) ** 2 + 3))


def power(rho_obs, n):
    return float(stats.norm.cdf(np.arctanh(rho_obs) * np.sqrt(max(n - 3, 0)) - Z_A)) if n > 3 else np.nan


def components(w, feat, lvef_subjects):
    w = w.dropna(subset=[feat])
    sess = w.groupby(["cohort", "subject", "session"])[feat].agg(["mean", "var", "size"]).reset_index()
    hc = sess[sess.cohort == "HC"]
    pool = hc[hc["size"] >= 2]
    sw2 = float(((pool["size"] - 1) * pool["var"]).sum() / (pool["size"] - 1).sum())
    piv = hc.pivot_table(index="subject", columns="session", values=["mean", "size"]).dropna()
    m1, m2 = piv[("mean", 1)], piv[("mean", 2)]
    k1, k2 = piv[("size", 1)], piv[("size", 2)]
    sday2 = max(0.0, ((m2 - m1).var() - (sw2 * (1 / k1 + 1 / k2)).mean()) / 2)
    sb2 = max(0.0, float(np.cov(m1, m2)[0, 1]))
    k_med = float(hc["size"].median())
    hf = sess[sess.cohort == "HFC"]
    sb2_hf = max(0.0, hf["mean"].var() - sday2 - (sw2 / hf["size"]).mean()) if len(hf) > 2 else np.nan
    k_hf = float(hf["size"].median()) if len(hf) else np.nan

    def R(sb, k, days=1):
        return sb / (sb + (sday2 + sw2 / k) / days) if sb > 0 else 0.0

    den = sb2 * (1 / TARGET_R - 1) - sday2
    out = {"feature": feat, "n_HC_pairs": len(piv), "k_median": k_med, "sd_within_window": np.sqrt(sw2),
           "sd_day": np.sqrt(sday2), "sd_between_HC": np.sqrt(sb2), "sd_between_HF": np.sqrt(sb2_hf),
           "R_session_HC": R(sb2, k_med), "R_ceiling_HC": sb2 / (sb2 + sday2) if sb2 > 0 else 0.0,
           "k_for_R0.8": (sw2 / den if den > 0 else np.inf),
           "days_for_R0.8": ((sday2 + sw2 / k_med) / (sb2 * (1 / TARGET_R - 1)) if sb2 > 0 else np.inf),
           "R_session_HF": R(sb2_hf, k_hf) if np.isfinite(sb2_hf) else np.nan}
    n_avail = int(hf[hf.subject.isin(lvef_subjects)].subject.nunique())
    out["n_HF_with_LVEF"] = n_avail
    for scen, Rx in (("HC", out["R_session_HC"]), ("HF", out["R_session_HF"])):
        for rt in (0.3, 0.5):
            ro = rt * np.sqrt(max(Rx, 0) * R_LVEF) if np.isfinite(Rx) else np.nan
            out[f"n_req_rho{rt}_{scen}"] = n_required(ro) if np.isfinite(ro) else np.nan
        ro = 0.5 * np.sqrt(max(Rx, 0) * R_LVEF) if np.isfinite(Rx) else np.nan
        out[f"power_rho0.5_{scen}_auricle"] = power(ro, n_avail) if np.isfinite(ro) and ro > 0 else 0.0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", default="outputs/validation/windows_rest.csv")
    ap.add_argument("--out", default="outputs/validation/exp5_precision")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from pwta import io  # noqa: E402
    demo = io.load_demographics()
    lvef_subjects = set(demo.index[demo.LVEF.notna()])
    w = pd.read_csv(a.windows)
    sc, ok = w[s_clean(w)], w[w.ok == True]  # noqa: E712
    rows = []
    for ch in ("PPG_Ear", "PPG_Finger"):
        for f in S_FEATS:
            rows.append({"channel": ch, **components(sc[sc.channel == ch], f, lvef_subjects)})
        for f in D_FEATS:
            rows.append({"channel": ch, **components(ok[ok.channel == ch], f, lvef_subjects)})
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(a.out, "precision_power.csv"), index=False)
    cols1 = ["channel", "feature", "n_HC_pairs", "k_median", "sd_within_window", "sd_day", "sd_between_HC",
             "sd_between_HF", "R_session_HC", "R_ceiling_HC", "k_for_R0.8", "days_for_R0.8", "R_session_HF"]
    cols2 = ["channel", "feature", "n_HF_with_LVEF", "n_req_rho0.3_HC", "n_req_rho0.5_HC", "power_rho0.5_HC_auricle",
             "n_req_rho0.3_HF", "n_req_rho0.5_HF", "power_rho0.5_HF_auricle"]
    md = ["# Experiment 5: precision ceiling and power\n",
          f"R_LVEF assumed {R_LVEF}; sample sizes for two-sided alpha 0.05, 80% power.\n",
          f"## variance components and reliability\n\n{t[cols1].round(3).to_markdown(index=False)}\n",
          f"## attenuation-corrected sample size and Auricle power (LVEF correlation within HF)\n\n"
          f"{t[cols2].round(3).to_markdown(index=False)}\n"]
    with open(os.path.join(a.out, "exp5.md"), "w") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
