"""S-wave / D-wave identification on an ensemble-averaged D-only intensity trace and the
diagnostic metrics of Reavette et al. 2024 / Rowland & Weinberg (D-only manuscript).

With the D-only method, dI = dD/dt: the S wave is the positive peak produced by early
ejection and the D wave is the subsequent negative peak produced by late-systolic
deceleration (D-wave intensities are negative with single-variable methods).

PPG-specific choices (not specified in the manuscripts):
- The D wave is taken as a *turning point* (local minimum) of dPPG/dt. Ear/finger PPG decline
  throughout diastole, so the global minimum after S often lies in diastole rather than at
  end-systole. The manuscript itself proposes discounting negative peaks outside a window
  defined relative to the S wave. The carotid S-D interval in the clinical study was
  213-253 +/- ~35 ms.
- Rules (`d_rule`): "window" = deepest distinct trough 120-400 ms after S; the REBOUND_RULES
  anchor D to the dicrotic rebound (the default "rebound_es" adds an end-systolic constraint).
  See docs/METHOD.md §7 and docs/RESULTS.md §1 for the comparison that chose the default.
- A trough/rebound is "distinct" if its prominence is >= D_MIN_PROM_FRAC of SWI. Under the rebound
  rules the rebound carries this test: if no trough before it reaches the threshold, the deepest one is
  taken and still counts as distinct (12% of finger ok windows, no ear windows; docs/METHOD.md §7).
- Because diastolic dPPG/dt is negative, the zero-crossing D-wave energy (DWE) is often
  unbounded. A baseline-independent alternative is also reported: D prominence and the area
  between the trace and the prominence reference level (D_prom, D_area_local, D_sharpness).
"""
import numpy as np
from scipy.signal import find_peaks, peak_widths, savgol_filter

S_SEARCH_MS = (60.0, 550.0)
D_AFTER_S_MS = (120.0, 400.0)
NEXT_BEAT_GUARD_MS = 150.0
D_MIN_PROM_FRAC = 0.05
# Rebound-anchored rules (see REBOUND_RULES)
SHOULDER_SG_MS = 31.0  # smoothing for the higher derivatives used by the shoulder fallback
SHOULDER_PROM_FRAC = 0.05  # shoulder prominence as a fraction of the second-derivative range


def _interp_peak(y, i):
    """Sub-sample vertex of a parabola through y[i-1:i+2]; returns (offset, value)."""
    if 0 < i < len(y) - 1:
        a, b, c = y[i - 1], y[i], y[i + 1]
        den = a - 2 * b + c
        if den != 0:
            off = 0.5 * (a - c) / den
            return off, b - 0.25 * (a - c) * off
    return 0.0, y[i]


def _lobe(y, i, sign, lo, hi):
    """Indices of the contiguous same-sign lobe containing i, limited to [lo, hi]."""
    a = i
    while a - 1 >= lo and sign * y[a - 1] > 0:
        a -= 1
    b = i
    while b + 1 <= hi and sign * y[b + 1] > 0:
        b += 1
    return a, b, (a == lo) or (b == hi)


def _pick_window(d, t_ms, tS, rr_ms, troughs, tprom, thr, d_window_ms):
    """Deepest distinct trough 120-400 ms after S (falls back to the most prominent trough)."""
    lo, hi = tS + d_window_ms[0], min(tS + d_window_ms[1], rr_ms + tS - NEXT_BEAT_GUARD_MS)
    m = (t_ms[troughs] >= lo) & (t_ms[troughs] <= hi)
    c, p = troughs[m], tprom[m]
    if len(c) == 0:
        return None, False, "none"
    strong = p >= thr
    if strong.any():
        return int(c[strong][np.argmin(d[c[strong]])]), True, "window"
    return int(c[np.argmax(p)]), False, "window"


def _rebound(d, t_ms, tS, beat, thr, rebound_ms):
    """Dicrotic rebound: the dPPG/dt peak in `rebound_ms` (after S) with the largest rise from its
    preceding trough. Returns (index or None if no rise >= thr, largest rise of any peak in the span)."""
    peaks, _ = find_peaks(d[beat])
    peaks = beat[peaks]
    rise = np.array([d[p] - d[(peaks[k - 1] if k else beat[0]):p + 1].min() for k, p in enumerate(peaks)])
    span = ((t_ms[peaks] >= tS + rebound_ms[0]) & (t_ms[peaks] <= tS + rebound_ms[1])
            if len(peaks) else np.zeros(0, bool))
    max_rise = float(rise[span].max()) if span.any() else 0.0
    m = span & (rise >= thr) if len(peaks) else span
    return (int(peaks[m][np.argmax(rise[m])]) if m.any() else None), max_rise


def _pick_rebound(d, t_ms, tS, beat, troughs, tprom, thr, fs, rebound_ms, d_min_ms, shoulder=False):
    """D anchored to the dicrotic rebound: a positive bump in dPPG/dt after S.

    The rebound is the bump in `rebound_ms` (after S) with the largest rise from the preceding
    trough. D is the last distinct trough at least `d_min_ms` after S and before the rebound
    (else the deepest one). Anchoring to the rebound picks the trough tied to the dicrotic wave
    when there are several late-systolic troughs (finger), rather than whichever is deepest.

    If there is no rebound (smooth ear pulse) and `shoulder` is set, D is placed where the
    systolic decline flattens most: the local maximum of the second PPG derivative (d(dPPG)/dt).
    This is a "virtual trough": where a trough would be if d(dPPG)/dt reached zero.
    """
    reb, _ = _rebound(d, t_ms, tS, beat, thr, rebound_ms)
    if reb is not None:
        c_mask = (t_ms[troughs] >= tS + d_min_ms) & (troughs < reb)
        c, p = troughs[c_mask], tprom[c_mask]
        if len(c) == 0:
            return None, False, "none"
        strong = np.flatnonzero(p >= thr)
        k = strong[-1] if len(strong) else int(np.argmin(d[c]))
        return int(c[k]), True, "rebound"
    if not shoulder:
        return None, False, "none"
    w = int(round(SHOULDER_SG_MS * fs / 1000)) | 1
    d2 = savgol_filter(d, w, 3, deriv=1, delta=1.0 / fs)
    seg = beat[(t_ms[beat] >= tS + max(d_min_ms, rebound_ms[0] - 50)) & (t_ms[beat] <= tS + rebound_ms[1])]
    if len(seg) < 5:
        return None, False, "none"
    sp, sprops = find_peaks(d2[seg], prominence=0)
    span = d2[beat].max() - d2[beat].min()
    ok = sprops["prominences"] >= SHOULDER_PROM_FRAC * span if len(sp) else np.zeros(0, bool)
    if not ok.any():
        return None, False, "none"
    return int(seg[sp[ok][np.argmax(sprops["prominences"][ok])]]), True, "shoulder"


# name -> (rebound search window after S, earliest D after S, shoulder fallback)
REBOUND_RULES = {
    "rebound": ((150.0, 550.0), 60.0, False),
    "rebound_es": ((200.0, 550.0), 120.0, False),  # end-systolic constraint (excludes mid-systolic dips)
    "rebound_es+shoulder": ((200.0, 550.0), 120.0, True),
}


def pick(d, t_ms, rr_ms, fs, d_window_ms=D_AFTER_S_MS, min_prom_frac=D_MIN_PROM_FRAC, d_rule="window"):
    """Locate S and D waves; returns dict of times (ms after R), intensities and energies."""
    dt_ms = 1000.0 / fs
    out = {"S_found": False, "D_found": False}
    s_lo, s_hi = S_SEARCH_MS[0], min(S_SEARCH_MS[1], 0.8 * rr_ms)
    ms = np.flatnonzero((t_ms >= s_lo) & (t_ms <= s_hi))
    if len(ms) < 3:
        return out
    iS = ms[np.argmax(d[ms])]
    if d[iS] <= 0 or iS in (ms[0], ms[-1]):
        return out
    off, sval = _interp_peak(d, iS)
    tS = t_ms[iS] + off * dt_ms
    a, b, _ = _lobe(d, iS, +1, 0, len(d) - 1)
    out.update(S_found=True, t_S=tS, SWI=sval, SWE=d[a:b + 1].sum() / fs)

    # Current beat: S peak up to a guard before the next upstroke. Prominences are measured only
    # within it. Otherwise the next beat's upstroke would count as the "rebound" and a smooth
    # diastolic decline would look like a distinct D wave.
    beat = np.flatnonzero((t_ms >= tS) & (t_ms <= min(rr_ms + tS - NEXT_BEAT_GUARD_MS, t_ms[-1])))
    if len(beat) < 5:
        return out
    troughs, tprops = find_peaks(-d[beat], prominence=0)
    troughs, tprom = beat[troughs], tprops["prominences"]
    neg = d[troughs] < 0
    troughs, tprom = troughs[neg], tprom[neg]
    thr = min_prom_frac * sval

    # Rebound strength is reported whatever the D rule (continuous D-wave flattening index; the
    # rebound rules call a rebound present when reb_rise_frac >= min_prom_frac)
    reb_ms = REBOUND_RULES[d_rule][0] if d_rule in REBOUND_RULES else REBOUND_RULES["rebound_es"][0]
    reb, max_rise = _rebound(d, t_ms, tS, beat, thr, reb_ms)
    out.update(reb_rise_frac=max_rise / sval, t_reb=(t_ms[reb] + _interp_peak(d, reb)[0] * dt_ms
                                                       if reb is not None else np.nan))

    if d_rule == "window":
        iD, distinct, source = _pick_window(d, t_ms, tS, rr_ms, troughs, tprom, thr, d_window_ms)
    elif d_rule in REBOUND_RULES:
        reb_ms, dmin_ms, shoulder = REBOUND_RULES[d_rule]
        iD, distinct, source = _pick_rebound(d, t_ms, tS, beat, troughs, tprom, thr, fs, reb_ms, dmin_ms, shoulder)
    else:
        raise ValueError(f"unknown d_rule {d_rule!r}")
    if iD is None or d[iD] >= 0:
        return out
    j = np.flatnonzero(troughs == iD)
    prom_D = float(tprom[j[0]]) if len(j) else np.nan
    n_strong = int((tprom >= thr).sum())
    # A shoulder knee is not an extremum of d, so no parabolic refinement there
    off, dval = _interp_peak(d, iD) if source != "shoulder" else (0.0, d[iD])

    # Zero-crossing lobe energy (paper definition), capped at the end of the beat
    a, b, capped = _lobe(d, iD, -1, beat[0], beat[-1])
    area_local = half = np.nan
    if len(j):  # prominence-referenced area: between the trace and the level d[iD] + prominence
        seg, k = -d[beat], iD - beat[0]  # widths use the same beat-limited prominence
        w = peak_widths(seg, [k], rel_height=1.0)
        la, rb = beat[0] + int(np.floor(w[2][0])), beat[0] + int(np.ceil(w[3][0]))
        area_local = np.clip(d[iD] + prom_D - d[la:rb + 1], 0, None).sum() / fs
        half = peak_widths(seg, [k], rel_height=0.5)[0][0] * dt_ms
    out.update(
        D_found=True,
        D_distinct=bool(distinct),
        D_source=source,
        t_D=t_ms[iD] + off * dt_ms,
        DWI=dval,
        DWE=-d[a:b + 1].sum() / fs,  # positive area of the negative lobe
        DWE_capped=bool(capped),
        D_prom=prom_D,
        D_area_local=float(area_local),
        D_halfwidth_ms=float(half),
        n_D_candidates=n_strong,
    )
    return out


def metrics(d, x, t_ms, rr_ms, fs, **pick_kw):
    """All diagnostic metrics for one ensemble; NaN where a wave was not found."""
    p = pick(d, t_ms, rr_ms, fs, **pick_kw)
    hr = 60000.0 / rr_ms
    seg = (t_ms >= 0) & (t_ms < rr_ms)
    amp = float(np.ptp(x[seg])) if seg.any() else np.nan
    m = {"HR": hr, "PPG_amp": amp, "S_found": p["S_found"], "D_found": p["D_found"],
         "D_distinct": p.get("D_distinct", False), "DWE_capped": p.get("DWE_capped", False),
         "D_source": p.get("D_source", "none")}
    nan = np.nan
    m["ECG_S_ms"] = p.get("t_S", nan)
    m["t_D_ms"] = p.get("t_D", nan)
    m["S_D_ms"] = p.get("t_D", nan) - p.get("t_S", nan)
    m["t_reb_ms"] = p.get("t_reb", nan)
    m["reb_rise_frac"] = p.get("reb_rise_frac", nan)
    # SWS = (60 x ECG-S interval) / (S-D interval x HR)  [Reavette 2024 Eq. 4]
    m["SWS"] = 60.0 * (m["ECG_S_ms"] / 1000) / ((m["S_D_ms"] / 1000) * hr)
    for k in ("SWI", "SWE", "DWI", "DWE", "D_prom", "D_area_local", "D_halfwidth_ms", "n_D_candidates"):
        m[k] = p.get(k, nan)
    # PPG has arbitrary gain, so absolute intensities are only comparable after normalising
    # by pulse amplitude (units 1/s); ratios are gain-free.
    m["nSWI"] = m["SWI"] / amp
    m["nDWI"] = m["DWI"] / amp
    m["DWI_over_SWI"] = m["DWI"] / m["SWI"]
    m["DWI_over_DWE"] = -m["DWI"] / m["DWE"] if not m["DWE_capped"] else nan  # D-wave "sharpness"
    m["D_sharpness"] = m["D_prom"] / m["D_area_local"]  # baseline-free analogue (1/s)
    return m
