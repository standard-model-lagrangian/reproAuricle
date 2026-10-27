"""Generic pulse-wave-analysis features of the ensemble PPG pulse (no ArterioWave wave model).

These are the standard morphology features PPG ageing/stiffness studies use. They serve as the
"generic" comparator block when asking whether the PWTA D-wave features add anything.

  PAT_foot_ms  R to pulse foot (intersecting tangent: tangent at max dPPG/dt meets the
               pre-upstroke minimum)
  CT_ms        crest time, foot to systolic peak
  PW50_frac    pulse width at 50% amplitude / RR
  b_over_a     SDPPG b/a: a = maximum of d2PPG/dt2 from 50 ms before the foot to S (must be > 0),
               b = minimum from a to S + 100 ms
"""
import numpy as np
from scipy.signal import savgol_filter

SDPPG_SG_MS = 31.0


def features(x, d, t_ms, rr_ms, fs, t_S):
    nan = np.nan
    out = {"PAT_foot_ms": nan, "CT_ms": nan, "PW50_frac": nan, "b_over_a": nan}
    if t_S is None or not np.isfinite(t_S):
        return out
    iS = int(np.argmin(np.abs(t_ms - t_S)))
    pre = np.flatnonzero((t_ms >= t_S - 250) & (t_ms <= t_S))
    if len(pre) < 3 or d[iS] <= 0:
        return out
    i0 = pre[np.argmin(x[pre])]
    foot = t_S - (x[iS] - x[i0]) / d[iS] * 1000.0
    out["PAT_foot_ms"] = foot

    pk = np.flatnonzero((t_ms >= t_S) & (t_ms <= min(t_S + 300, foot + rr_ms)))
    if len(pk) < 3:
        return out
    ip = pk[np.argmax(x[pk])]
    out["CT_ms"] = t_ms[ip] - foot

    level = x[i0] + 0.5 * (x[ip] - x[i0])
    rise = np.flatnonzero((t_ms >= t_ms[i0]) & (t_ms <= t_ms[ip]) & (x >= level))
    fall = np.flatnonzero((t_ms > t_ms[ip]) & (t_ms <= foot + rr_ms) & (x < level))
    if len(rise) and len(fall):
        out["PW50_frac"] = (t_ms[fall[0]] - t_ms[rise[0]]) / rr_ms

    w = int(round(SDPPG_SG_MS * fs / 1000)) | 1
    d2 = savgol_filter(d, w, 3, deriv=1, delta=1.0 / fs)
    sa = np.flatnonzero((t_ms >= foot - 50) & (t_ms <= t_S))
    if len(sa) >= 3:
        ia = sa[np.argmax(d2[sa])]
        sb = np.flatnonzero((t_ms >= t_ms[ia]) & (t_ms <= t_S + 100))
        if d2[ia] > 0 and len(sb) >= 3:
            out["b_over_a"] = d2[sb].min() / d2[ia]
    return out
