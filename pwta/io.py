"""Loading Auricle WFDB records and session metadata."""
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
import wfdb
from scipy.signal import resample_poly

# PhysioNet Auricle 1.0.0. Set AURICLE_ROOT, or place (or symlink) the dataset folder under data/.
DATASET_DIR = "auricle-a-multimodal-wearable-sensing-dataset-for-cardiovascular-and-hemodynamic-assessment-1.0.0"
DATA_ROOT = os.environ.get(
    "AURICLE_ROOT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", DATASET_DIR))

ACTIVITY = {0: "rest", 1: "breath_hold", 2: "valsalva", 3: "exercise", 4: "cold_pressor", 9: "not_applicable"}
NO_ANNOTATION = -1  # four records have no Activity_Annotations channel


@dataclass
class Record:
    rid: str
    fs: float
    signals: dict  # channel name -> float64 array (physical units)
    activity: np.ndarray  # int label per sample, NO_ANNOTATION if absent
    cnap_valid: np.ndarray | None = None  # CNAP_Annotations mask (1 = CNAP data valid), None if absent

    @property
    def n(self):
        return len(self.activity)


def list_records(root=DATA_ROOT):
    """Record ids from RECORDS (the data/ folder also holds a stray copy of HC_20_2 inside HC_19_2)."""
    with open(os.path.join(root, "RECORDS")) as f:
        return [line.strip().split("/")[0] for line in f if line.strip()]


def parse_rid(rid):
    cohort, subject, session = rid.split("_")
    return cohort, f"{cohort}_{subject}", int(session)


def load_record(rid, channels=("ECG", "PPG_Ear", "PPG_Finger"), root=DATA_ROOT):
    path = os.path.join(root, "data", rid, rid)
    names = wfdb.rdheader(path).sig_name
    wanted = [c for c in channels if c in names]
    has_act = "Activity_Annotations" in names
    has_cnap = "CNAP_Annotations" in names
    extra = (["Activity_Annotations"] if has_act else []) + (["CNAP_Annotations"] if has_cnap else [])
    rec = wfdb.rdrecord(path, channel_names=wanted + extra)
    sig = {name: rec.p_signal[:, i].astype(np.float64) for i, name in enumerate(rec.sig_name)}
    if has_act:
        activity = np.rint(sig.pop("Activity_Annotations")).astype(int)
    else:
        activity = np.full(rec.sig_len, NO_ANNOTATION, dtype=int)
    # 0 marks CNAP calibration / uncalibrated / artefact periods. Per the dataset it applies to the
    # CNAP-derived channels only, but it is carried along so its relevance can be tested.
    cnap = np.rint(sig.pop("CNAP_Annotations")).astype(np.int8) if has_cnap else None
    return Record(rid, float(rec.fs), sig, activity, cnap)


def resample_record(rec, spec):
    """Simulate a lower acquisition rate (e.g. MIMIC's 125 Hz). `spec` is "F" or "F:G".

    "F": anti-aliased polyphase decimation of every signal to F Hz; the label channels are
    subsampled. The pipeline then runs at F Hz.
    "F:G": decimate to F Hz, then interpolate back up to G Hz (band-limited reconstruction, what one
    would do before analysing low-rate data). Labels stay on the original grid when G equals the
    original rate, so windows match the native run exactly.
    """
    if not spec:
        return rec
    lo, *hi = (int(v) for v in str(spec).split(":"))
    fs0 = int(round(rec.fs))
    if fs0 % lo:
        raise ValueError(f"{fs0} Hz is not an integer multiple of {lo} Hz")
    q = fs0 // lo
    sig = {k: resample_poly(v, 1, q) for k, v in rec.signals.items()}
    act, cnap, fs = rec.activity[::q], (rec.cnap_valid[::q] if rec.cnap_valid is not None else None), float(lo)
    if hi:
        up = hi[0] // lo
        n = len(rec.activity) if hi[0] == fs0 else len(act) * up
        sig = {k: resample_poly(v, up, 1)[:n] for k, v in sig.items()}
        if hi[0] == fs0:
            act, cnap = rec.activity, rec.cnap_valid
        else:
            act = np.repeat(act, up)[:n]
            cnap = np.repeat(cnap, up)[:n] if cnap is not None else None
        fs = float(hi[0])
    return Record(rec.rid, fs, sig, act, cnap)


def load_demographics(root=DATA_ROOT):
    df = pd.read_csv(os.path.join(root, "demographics.csv"))
    lvef = pd.to_numeric(df["LV ejection fraction"].astype(str).str.rstrip("%"), errors="coerce")
    df["LVEF"] = lvef
    group = np.where(df["Cohort"] == "HC", "control", "HF_unknown_EF")
    group = np.where(lvef < 40, "HFrEF", group)
    group = np.where((lvef >= 40) & (lvef < 50), "HFmrEF", group)
    group = np.where(lvef >= 50, "HF_EF>=50", group)
    df["group"] = group
    return df.set_index("ID")
