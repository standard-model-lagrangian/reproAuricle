"""ECG R-peak detection (timing datum for wave metrics)."""
import neurokit2 as nk
import numpy as np
from scipy.signal import butter, sosfiltfilt


def bandpass(ecg, fs, lo=1.0, hi=25.0):
    """Zero-phase 1-25 Hz band-pass, as used for R-wave identification in Reavette et al. 2024."""
    sos = butter(2, [lo, hi], btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos, ecg)


def polarity(x):
    """+1 if the dominant QRS deflection is positive, else -1."""
    return 1 if np.percentile(x, 99.8) >= -np.percentile(x, 0.2) else -1


def detect_r_peaks(ecg, fs, refine_ms=40):
    """R-peak sample indices on the band-passed, polarity-corrected ECG.

    Candidate beats come from NeuroKit's default detector; each is then moved to the local
    extremum of the band-passed signal within +/- `refine_ms` so the datum is the R apex.
    """
    x = bandpass(ecg, fs)
    pol = polarity(x)
    x = pol * x
    _, info = nk.ecg_peaks(x, sampling_rate=int(fs), method="neurokit")
    cand = np.asarray(info["ECG_R_Peaks"], dtype=int)
    w = int(refine_ms * fs / 1000)
    peaks = []
    for p in cand:
        a, b = max(p - w, 0), min(p + w + 1, len(x))
        peaks.append(a + int(np.argmax(x[a:b])))
    peaks = np.unique(np.asarray(peaks, dtype=int))
    return peaks, pol
