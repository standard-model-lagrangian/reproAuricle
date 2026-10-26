"""R-peak-aligned beat segmentation, beat rejection and ensemble averaging."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Ensemble:
    t_ms: np.ndarray  # time relative to R peak
    d: np.ndarray  # mean dPPG/dt of accepted beats
    x: np.ndarray  # mean conditioned PPG of accepted beats
    d_beats: np.ndarray  # accepted beats (n_acc x len(t_ms))
    rr_ms: float  # median RR of the window
    rr_cv: float
    n_total: int
    n_rr_ok: int
    n_acc: int
    median_corr: float


def build(d, x, raw, r_peaks, start, stop, fs, pre_ms=100, post_ms=800, rr_tol=0.2,
          min_corr=0.8, corr_span_ms=(0, 600), clip_level=9.99):
    """Ensemble of beats whose R peak lies in [start, stop).

    Beats are rejected if either adjacent RR interval deviates from the window median by
    more than `rr_tol` (ectopics, AF, missed/extra R peaks), if the raw PPG is clipped, or if
    the beat correlates with the window template below `min_corr` (artefact, misalignment).
    Returns None if the window has no usable beats.
    """
    pre, post = int(pre_ms * fs / 1000), int(post_ms * fs / 1000)
    t_ms = np.arange(-pre, post) * 1000.0 / fs
    k = np.flatnonzero((r_peaks >= start) & (r_peaks < stop))
    k = k[(k > 0) & (k < len(r_peaks) - 1)]
    k = k[(r_peaks[k] - pre >= 0) & (r_peaks[k] + post <= len(d))]
    if len(k) < 3:
        return None
    rr_prev = (r_peaks[k] - r_peaks[k - 1]).astype(float)
    rr_next = (r_peaks[k + 1] - r_peaks[k]).astype(float)
    rr_med = np.median(rr_prev)
    ok = (np.abs(rr_prev / rr_med - 1) <= rr_tol) & (np.abs(rr_next / rr_med - 1) <= rr_tol)

    idx = r_peaks[k][:, None] + np.arange(-pre, post)[None, :]
    d_seg, x_seg = d[idx], x[idx]
    ok &= ~np.any(np.abs(raw[idx]) >= clip_level, axis=1)
    n_rr_ok = int(ok.sum())
    if n_rr_ok < 3:
        return None

    span = (t_ms >= corr_span_ms[0]) & (t_ms < corr_span_ms[1])
    template = np.median(d_seg[ok], axis=0)
    for _ in range(2):  # median template first, then refine on the accepted mean
        corr = _rowcorr(d_seg[:, span], template[span])
        acc = ok & (corr >= min_corr)
        if acc.sum() < 3:
            return None
        template = d_seg[acc].mean(axis=0)

    rr_acc = rr_prev[acc]
    return Ensemble(
        t_ms=t_ms,
        d=d_seg[acc].mean(axis=0),
        x=x_seg[acc].mean(axis=0),
        d_beats=d_seg[acc],
        rr_ms=float(np.median(rr_acc) * 1000.0 / fs),
        rr_cv=float(np.std(rr_prev[ok]) / np.mean(rr_prev[ok])),
        n_total=len(k),
        n_rr_ok=n_rr_ok,
        n_acc=int(acc.sum()),
        median_corr=float(np.median(corr[ok])),
    )


def _rowcorr(rows, ref):
    a = rows - rows.mean(axis=1, keepdims=True)
    b = ref - ref.mean()
    den = np.sqrt((a * a).sum(axis=1) * (b * b).sum())
    return np.where(den > 0, (a @ b) / np.where(den > 0, den, 1), 0.0)


def ppg_polarity(ens_d, t_ms, span_ms=(0, 600)):
    """+1 if the steepest excursion after the R peak is positive (upright PPG upstroke)."""
    m = (t_ms >= span_ms[0]) & (t_ms < span_ms[1])
    return 1 if ens_d[m].max() >= -ens_d[m].min() else -1
