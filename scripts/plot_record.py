"""Plot window ensembles (dPPG/dt and PPG) with picked S/D waves for one or more records.

Usage: python scripts/plot_record.py HC_2_1 [HFC_117_1 ...] [--spec sg:61:4] [--out outputs/plots]
"""
import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pwta.pipeline import process_record  # noqa: E402

CHANNELS = ("PPG_Ear", "PPG_Finger")


def plot(rid, spec, out_dir):
    rows, store = process_record(rid, specs=(spec,), channels=CHANNELS, keep_ensembles=True)
    fig, axes = plt.subplots(2, len(CHANNELS), figsize=(7 * len(CHANNELS), 7), sharex=True)
    for j, ch in enumerate(CHANNELS):
        ax_d, ax_x = axes[0, j], axes[1, j]
        for row in (r for r in rows if r["channel"] == ch):
            key = (ch, spec, row["win_start"])
            if key not in store:
                continue
            t, d, x = store[key]
            amp = row["PPG_amp"]
            colour = "C0" if row["ok"] else "0.7"
            ax_d.plot(t, d / amp, color=colour, lw=0.8)
            ax_x.plot(t, x / amp, color=colour, lw=0.8)
            if row["S_found"]:
                ax_d.plot(row["ECG_S_ms"], row["SWI"] / amp, "r^", ms=4)
            if row["D_found"]:
                ax_d.plot(row["t_D_ms"], row["DWI"] / amp, "kv", ms=4)
        n_ok = sum(r["ok"] for r in rows if r["channel"] == ch)
        n = sum(r["channel"] == ch for r in rows)
        ax_d.set_title(f"{rid} {ch}  ({n_ok}/{n} windows ok; grey = rejected)")
        ax_d.axhline(0, color="k", lw=0.5)
        ax_d.set_ylabel("dPPG/dt / pulse amplitude (1/s)")
        ax_x.set_ylabel("PPG / pulse amplitude")
        ax_x.set_xlabel("time after ECG R peak (ms)")
    fig.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{rid}_{spec.replace(':', '-')}.png")
    fig.savefig(path, dpi=80)
    plt.close(fig)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("rids", nargs="+")
    ap.add_argument("--spec", default="sg:61:4")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "outputs", "plots"))
    a = ap.parse_args()
    for rid in a.rids:
        print(plot(rid, a.spec, a.out))
