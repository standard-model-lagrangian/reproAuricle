"""Cardiac timing references for validating the PPG wave timing (see docs/VALIDATION.md).

Per analysis window, from R-locked ensembles of beats that pass the RR rule:
  heart sounds (Digital_Stethoscope, Earbud_Left/Right)
      S1, S2 = envelope maxima; QS2_ms = R to S2 (aortic closure, end of electromechanical
      systole), S1S2_ms = S2 - S1
  CNAP finger pressure (NIBP, other hand)
      foot (intersecting tangent), systolic peak, dicrotic notch (local minimum, else the
      inflection = max of d2P/dt2), cnap_ET_ms = notch - foot (peripheral ejection time), SBP/DBP/MAP
"""
import numpy as np
from scipy.signal import butter, find_peaks, hilbert, savgol_filter, sosfiltfilt

PRE_MS, POST_MS = 100.0, 1000.0
CNAP_POST_MS = 1700.0  # long enough for foot + one RR at 40 bpm, so MAP is a full cycle
MIN_BEATS = 8
SND_BAND_HZ = (20.0, 200.0)
SND_ENV_LP_HZ = 40.0
SND_ARTEFACT_X = 4.0  # beats with envelope max > 4x the window median of beat maxima are rejected
MIN_SNR = 2.5
MAX_SPLIT_MS = 10.0
CNAP_SG_MS = 31.0
NOTCH_MIN_PROM = 0.5  # mmHg
ET_RANGE_MS = (150.0, 450.0)


def sound_envelope(x, fs):
    sos = butter(4, SND_BAND_HZ, btype="bandpass", fs=fs, output="sos")
    env = np.abs(hilbert(sosfiltfilt(sos, x)))
    return sosfiltfilt(butter(4, SND_ENV_LP_HZ, btype="lowpass", fs=fs, output="sos"), env)


def window_beats(r_peaks, start, stop, n, fs, rr_tol=0.2):
    """R-peak indices of beats in [start, stop) with both adjacent RR within rr_tol of the median."""
    pre, post = int(PRE_MS * fs / 1000), int(POST_MS * fs / 1000)
    k = np.flatnonzero((r_peaks >= start) & (r_peaks < stop))
    k = k[(k > 0) & (k < len(r_peaks) - 1)]
    k = k[(r_peaks[k] - pre >= 0) & (r_peaks[k] + post <= n)]
    if len(k) < 3:
        return np.zeros(0, int), np.nan
    rr_prev = (r_peaks[k] - r_peaks[k - 1]).astype(float)
    rr_next = (r_peaks[k + 1] - r_peaks[k]).astype(float)
    med = np.median(rr_prev)
    ok = (np.abs(rr_prev / med - 1) <= rr_tol) & (np.abs(rr_next / med - 1) <= rr_tol)
    return r_peaks[k[ok]], float(np.median(rr_prev[ok]) * 1000 / fs) if ok.any() else np.nan


def _segments(y, beats, fs, post_ms=POST_MS):
    pre, post = int(PRE_MS * fs / 1000), int(post_ms * fs / 1000)
    t_ms = np.arange(-pre, post) * 1000.0 / fs
    return t_ms, y[beats[:, None] + np.arange(-pre, post)[None, :]]


def _s1_s2(e, t_ms, rr_ms):
    """S1/S2 times from an averaged envelope; returns dict (NaN where not found)."""
    out = dict(S1_ms=np.nan, S2_ms=np.nan, S2_onset_ms=np.nan, s1_snr=np.nan, s2_snr=np.nan)
    m1 = (t_ms >= 0) & (t_ms <= 200)
    i1 = np.flatnonzero(m1)[np.argmax(e[m1])]
    s1_interior = 0 < t_ms[i1] < 200
    lo, hi = max(t_ms[i1] + 150, 220), min(0.75 * rr_ms, 600)
    m2 = (t_ms >= lo) & (t_ms <= hi)
    if m2.sum() < 5:
        return out
    i2 = np.flatnonzero(m2)[np.argmax(e[m2])]
    mb = (t_ms >= t_ms[i2] + 150) & (t_ms <= rr_ms - 50)
    base = np.median(e[mb]) if mb.sum() >= 30 else np.percentile(e, 20)
    if base <= 0:
        return out
    half = base + 0.5 * (e[i2] - base)
    j = i2
    while j > 0 and e[j - 1] >= half and t_ms[j - 1] > lo - 50:
        j -= 1
    out.update(S1_ms=t_ms[i1], S2_ms=t_ms[i2], S2_onset_ms=t_ms[j], s1_snr=e[i1] / base, s2_snr=e[i2] / base,
               s1_interior=s1_interior)
    return out


def heart_sounds(env, beats, rr_ms, fs, prefix):
    nan = np.nan
    keys = ["QS2_ms", "S2_onset_ms", "S1_ms", "S1S2_ms", "s2_snr", "s1_snr", "split_ms", "n", "ok", "s1_ok"]
    out = {f"{prefix}{k}": nan for k in keys}
    out[f"{prefix}ok"] = out[f"{prefix}s1_ok"] = False
    if len(beats) < MIN_BEATS:
        return out
    t_ms, seg = _segments(env, beats, fs)
    mx = seg.max(axis=1)
    seg = seg[mx <= SND_ARTEFACT_X * np.median(mx)]
    if len(seg) < MIN_BEATS:
        return out
    full = _s1_s2(seg.mean(axis=0), t_ms, rr_ms)
    halves = [_s1_s2(seg[i::2].mean(axis=0), t_ms, rr_ms) for i in (0, 1)]
    split = abs(halves[0]["S2_ms"] - halves[1]["S2_ms"])
    out.update({f"{prefix}QS2_ms": full["S2_ms"], f"{prefix}S2_onset_ms": full["S2_onset_ms"],
                f"{prefix}S1_ms": full["S1_ms"], f"{prefix}S1S2_ms": full["S2_ms"] - full["S1_ms"],
                f"{prefix}s2_snr": full["s2_snr"], f"{prefix}s1_snr": full["s1_snr"],
                f"{prefix}split_ms": split, f"{prefix}n": len(seg)})
    out[f"{prefix}ok"] = bool(full["s2_snr"] >= MIN_SNR and split <= MAX_SPLIT_MS)
    out[f"{prefix}s1_ok"] = bool(out[f"{prefix}ok"] and full["s1_snr"] >= MIN_SNR and full.get("s1_interior", False))
    return out


def cnap(p, valid, beats, rr_ms, fs):
    nan = np.nan
    out = dict(cnap_n=0, cnap_foot_ms=nan, cnap_peak_ms=nan, cnap_notch_ms=nan, cnap_ET_ms=nan,
               cnap_notch_type="none", SBP=nan, DBP=nan, MAP=nan, cnap_ok=False)
    if valid is None:  # no CNAP_Annotations channel: validity unknown, so the spec excludes it
        return out
    beats = beats[beats + int(CNAP_POST_MS * fs / 1000) <= len(p)]
    if len(beats) < MIN_BEATS:
        return out
    t_ms, seg = _segments(p, beats, fs, CNAP_POST_MS)
    _, vseg = _segments(valid.astype(float), beats, fs, CNAP_POST_MS)
    seg = seg[(vseg == 1).all(axis=1)]
    out["cnap_n"] = len(seg)
    if len(seg) < MIN_BEATS:
        return out
    P = seg.mean(axis=0)
    w = int(round(CNAP_SG_MS * fs / 1000)) | 1
    dP = savgol_filter(P, w, 3, deriv=1, delta=1.0 / fs)
    d2P = savgol_filter(P, w, 3, deriv=2, delta=1.0 / fs)
    ms = np.flatnonzero((t_ms >= 100) & (t_ms <= 500))
    iM = ms[np.argmax(dP[ms])]
    pre = np.flatnonzero((t_ms >= t_ms[iM] - 250) & (t_ms <= t_ms[iM]))
    i0 = pre[np.argmin(P[pre])]
    if dP[iM] <= 0:
        return out
    foot = t_ms[iM] - (P[iM] - P[i0]) / dP[iM] * 1000.0
    pk = np.flatnonzero((t_ms >= t_ms[iM]) & (t_ms <= t_ms[iM] + 300))
    ip = pk[np.argmax(P[pk])]
    span = np.flatnonzero((t_ms >= t_ms[ip] + 50) & (t_ms <= min(foot + 0.65 * rr_ms, t_ms[-1])))
    out.update(cnap_foot_ms=foot, cnap_peak_ms=t_ms[ip], SBP=P[ip], DBP=P[i0])
    one = (t_ms >= foot) & (t_ms < foot + rr_ms)
    out["MAP"] = float(P[one].mean()) if one.any() else nan
    if len(span) < 5:
        return out
    mins, props = find_peaks(-P[span], prominence=0)
    strong = mins[props["prominences"] >= NOTCH_MIN_PROM]
    if len(strong):
        iN, kind = span[strong[0]], "minimum"
    else:
        pks, _ = find_peaks(d2P[span])
        if not len(pks):
            return out
        iN, kind = span[pks[np.argmax(d2P[span][pks])]], "inflection"
    et = t_ms[iN] - foot
    out.update(cnap_notch_ms=t_ms[iN], cnap_notch_type=kind)
    if ET_RANGE_MS[0] <= et <= ET_RANGE_MS[1]:
        out.update(cnap_ET_ms=et, cnap_ok=True)
    return out
