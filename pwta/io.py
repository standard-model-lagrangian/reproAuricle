"""Loading Auricle WFDB records and session metadata."""
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
import wfdb

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
