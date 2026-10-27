"""Per-record pipeline: ECG R peaks -> windows -> PPG derivative -> ensembles -> wave metrics."""
from dataclasses import asdict, dataclass

import numpy as np

from . import ecg, ensemble, io, morphology, ppg, waves
from .windows import make_windows


@dataclass(frozen=True)
class Config:
    window_s: float = 60.0
    min_window_s: float = 30.0
    settle_s: float = 10.0
    labels: tuple = (0,)  # activity labels to analyse (0 = rest)
    hp_hz: float = 0.2
    pre_ms: float = 100.0
    post_ms: float = 800.0
    rr_tol: float = 0.2
    min_corr: float = 0.8
    # Acceptance criteria for a "non-degenerate" window
    min_beats: int = 10
    min_accept_frac: float = 0.6
    max_split_ecg_s_ms: float = 10.0
    max_split_s_d_ms: float = 15.0
    flat_frac_max: float = 0.5
    # D-wave search (see waves.py)
    d_window_ms: tuple = (120.0, 400.0)
    d_min_prom_frac: float = 0.05
    d_rule: str = "rebound_es"  # "window" or a key of waves.REBOUND_RULES (see docs/METHOD.md §7)
    resample: str = ""  # "" = native 1 kHz; "125" or "125:1000" simulate a 125 Hz acquisition (io.resample_record)

    def pick_kw(self):
        return {"d_window_ms": self.d_window_ms, "min_prom_frac": self.d_min_prom_frac, "d_rule": self.d_rule}


def _split_half(ens, fs, cfg):
    """Wave metrics from odd vs even accepted beats -> absolute differences in timing."""
    out = {}
    if ens.n_acc < 6:
        return {"split_dECG_S_ms": np.nan, "split_dS_D_ms": np.nan, "split_dSWS": np.nan}
    halves = [waves.metrics(ens.d_beats[i::2].mean(axis=0), ens.x, ens.t_ms, ens.rr_ms, fs, **cfg.pick_kw())
              for i in (0, 1)]
    for key, name in (("ECG_S_ms", "split_dECG_S_ms"), ("S_D_ms", "split_dS_D_ms"), ("SWS", "split_dSWS")):
        out[name] = abs(halves[0][key] - halves[1][key])
    return out


def _verdict(row, cfg):
    reasons = []
    if row["ppg_flat_frac"] > cfg.flat_frac_max:
        reasons.append("ppg_flat")
    if row["n_acc"] < cfg.min_beats:
        reasons.append("few_beats")
    if row["n_total"] and row["n_acc"] / row["n_total"] < cfg.min_accept_frac:
        reasons.append("low_acceptance")
    if not row.get("S_found"):
        reasons.append("no_S")
    if not row.get("D_found"):
        reasons.append("no_D")
    elif not row.get("D_distinct"):
        reasons.append("D_not_distinct")
    if not row.get("split_dECG_S_ms", np.nan) <= cfg.max_split_ecg_s_ms:
        reasons.append("unstable_S")
    if not row.get("split_dS_D_ms", np.nan) <= cfg.max_split_s_d_ms:
        reasons.append("unstable_D")
    return (len(reasons) == 0), ";".join(reasons)


def process_record(rid, specs=("sg:61:4",), channels=("PPG_Ear",), cfg=Config(), keep_ensembles=False):
    """Return (rows, ensembles). One row per (channel, spec, window)."""
    rec = io.resample_record(io.load_record(rid, channels=("ECG",) + tuple(channels)), cfg.resample)
    fs = rec.fs
    cohort, subject, session = io.parse_rid(rid)
    r_peaks, ecg_pol = ecg.detect_r_peaks(rec.signals["ECG"], fs)
    wins = make_windows(rec.activity, fs, cfg.window_s, cfg.min_window_s, cfg.settle_s, cfg.labels)
    rows, store = [], {}
    for ch in channels:
        if ch not in rec.signals:
            continue
        raw = rec.signals[ch]
        x = ppg.condition(raw, fs, cfg.hp_hz)
        flat = [ppg.flat_fraction(raw[w.start:w.stop], fs) for w in wins]
        for spec in specs:
            d = ppg.derivative(x, fs, spec)
            ens_list = [ensemble.build(d, x, raw, r_peaks, w.start, w.stop, fs, cfg.pre_ms, cfg.post_ms,
                                       cfg.rr_tol, cfg.min_corr) for w in wins]
            # PPG inversion is a property of the sensor placement: decide by majority over windows
            pols = [ensemble.ppg_polarity(e.d, e.t_ms) for e in ens_list if e is not None]
            pol = 1 if sum(pols) >= 0 else -1
            for w, e, ff in zip(wins, ens_list, flat):
                row = dict(rid=rid, cohort=cohort, subject=subject, session=session, channel=ch,
                           spec=spec, win_start=w.start, win_start_s=w.start / fs, win_len_s=(w.stop - w.start) / fs,
                           label=w.label, prev_label=w.prev_label, t_since_prev_s=w.t_since_prev_s,
                           next_label=w.next_label, t_until_next_s=w.t_until_next_s,
                           ecg_polarity=ecg_pol, ppg_polarity=pol, ppg_flat_frac=ff,
                           cnap_invalid_frac=(float(np.mean(rec.cnap_valid[w.start:w.stop] == 0))
                                              if rec.cnap_valid is not None else np.nan),
                           n_total=0, n_rr_ok=0, n_acc=0)
                if e is not None:
                    if pol < 0:
                        e.d, e.x, e.d_beats = -e.d, -e.x, -e.d_beats
                    row.update(n_total=e.n_total, n_rr_ok=e.n_rr_ok, n_acc=e.n_acc,
                               median_corr=e.median_corr, rr_cv=e.rr_cv)
                    row.update(waves.metrics(e.d, e.x, e.t_ms, e.rr_ms, fs, **cfg.pick_kw()))
                    row.update(morphology.features(e.x, e.d, e.t_ms, e.rr_ms, fs, row["ECG_S_ms"]))
                    row.update(_split_half(e, fs, cfg))
                    if keep_ensembles == "beats":  # the whole Ensemble, including accepted beats
                        store[(ch, spec, w.start)] = e
                    elif keep_ensembles:
                        store[(ch, spec, w.start)] = (e.t_ms, e.d, e.x)
                row["ok"], row["reasons"] = _verdict(row, cfg)
                rows.append(row)
    return rows, store


def config_dict(cfg):
    return asdict(cfg)
