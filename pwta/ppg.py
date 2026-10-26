"""PPG conditioning and the D-only intensity surrogate dI = dD/dt (PPG as a proxy for D).

All filters are zero-phase so that the timing of turning points is not shifted.
Derivative filters are given as spec strings so they can be screened:

    "raw"        central difference only
    "sg:W:O"     Savitzky-Golay first derivative, window W ms (odd), polynomial order O
    "bw:F"       4th-order Butterworth low-pass at F Hz (forward-backward) + central difference
    "gauss:S"    derivative-of-Gaussian, sigma S ms
"""
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, filtfilt, iirnotch, savgol_filter, sosfiltfilt


def condition(x, fs, hp_hz=0.2, mains_hz=(60.0, 120.0)):
    """Remove slow drift (respiration/movement baseline) and North-American mains hum."""
    x = np.asarray(x, dtype=np.float64)
    for f0 in mains_hz:
        if f0 < fs / 2:
            b, a = iirnotch(f0, Q=30.0, fs=fs)
            x = filtfilt(b, a, x)
    if hp_hz:
        sos = butter(2, hp_hz, btype="highpass", fs=fs, output="sos")
        x = sosfiltfilt(sos, x)
    return x


def derivative(x, fs, spec="sg:41:3"):
    kind, *args = spec.split(":")
    if kind == "raw":
        return np.gradient(x) * fs
    if kind == "sg":
        w = int(round(float(args[0]) * fs / 1000)) | 1  # force odd length
        return savgol_filter(x, w, int(args[1]), deriv=1, delta=1.0 / fs)
    if kind == "bw":
        sos = butter(4, float(args[0]), btype="lowpass", fs=fs, output="sos")
        return np.gradient(sosfiltfilt(sos, x)) * fs
    if kind == "gauss":
        return gaussian_filter1d(x, float(args[0]) * fs / 1000, order=1) * fs
    raise ValueError(f"unknown derivative spec {spec!r}")


def flat_fraction(x, fs, p2p_thresh=0.01):
    """Fraction of 1-s blocks whose peak-to-peak is below threshold (dead / unplugged sensor)."""
    n = int(fs)
    blocks = x[: len(x) // n * n].reshape(-1, n)
    return float(np.mean(np.ptp(blocks, axis=1) < p2p_thresh))
