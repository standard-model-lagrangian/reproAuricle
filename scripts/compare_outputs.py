"""Compare a reproduced output folder with the committed outputs/: every CSV and Markdown file is
identical, numerically close (within --rtol/--atol), or different.

Only files present in both folders are compared; a file in just one is listed. The large per-window tables
are not committed, so they appear as "only in B" when comparing a fresh run against outputs/.
Exits 1 if any shared file differs.

Usage:
  OUT=outputs_check ./reproduce.sh core
  python scripts/compare_outputs.py outputs outputs_check
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd


def compare_csv(pa, pb, rtol, atol):
    a, b = pd.read_csv(pa, low_memory=False), pd.read_csv(pb, low_memory=False)
    if list(a.columns) != list(b.columns):
        return "different", f"columns differ: +{[c for c in b if c not in a]} -{[c for c in a if c not in b]}"
    if a.shape != b.shape:
        return "different", f"shape {a.shape} vs {b.shape}"
    if a.equals(b):
        return "identical", ""
    worst, bad = 0.0, []
    for c in a.columns:
        x, y = a[c], b[c]
        if x.equals(y):
            continue
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            xf, yf = x.to_numpy(float), y.to_numpy(float)
            nan_mismatch = int((np.isnan(xf) != np.isnan(yf)).sum())
            both = ~np.isnan(xf) & ~np.isnan(yf)
            d = np.abs(xf[both] - yf[both])
            worst = max(worst, float(d.max(initial=0)))
            if nan_mismatch or not np.allclose(xf[both], yf[both], rtol=rtol, atol=atol):
                bad.append(f"{c} (max |d| {d.max(initial=0):.3g}, NaN mismatches {nan_mismatch})")
        elif (x.astype(str) != y.astype(str)).any():
            bad.append(f"{c} ({int((x.astype(str) != y.astype(str)).sum())} values)")
    if bad:
        return "different", "; ".join(bad[:6])
    return "close", f"max |d| {worst:.3g}"


def files(root):
    return {os.path.relpath(os.path.join(d, f), root)
            for d, _, fs in os.walk(root) for f in fs if f.endswith((".csv", ".md"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a", help="reference folder, e.g. outputs")
    ap.add_argument("b", help="reproduced folder")
    ap.add_argument("--rtol", type=float, default=1e-9)
    ap.add_argument("--atol", type=float, default=1e-12)
    ap.add_argument("--verbose", action="store_true", help="list identical files too")
    a = ap.parse_args()
    fa, fb = files(a.a), files(a.b)
    rows = []
    for rel in sorted(fa & fb):
        pa, pb = os.path.join(a.a, rel), os.path.join(a.b, rel)
        if rel.endswith(".csv"):
            status, detail = compare_csv(pa, pb, a.rtol, a.atol)
        else:
            with open(pa) as x, open(pb) as y:
                status, detail = ("identical", "") if x.read() == y.read() else ("different", "text differs")
        rows.append((status, rel, detail))
    rows += [("only in A", rel, "") for rel in sorted(fa - fb)]
    rows += [("only in B", rel, "") for rel in sorted(fb - fa)]
    counts = pd.Series([r[0] for r in rows]).value_counts()
    print(counts.to_string(), "\n")
    for status, rel, detail in rows:
        if a.verbose or status not in ("identical", "only in A"):
            print(f"{status:10s} {rel}  {detail}")
    sys.exit(1 if any(r[0] == "different" for r in rows) else 0)


if __name__ == "__main__":
    main()
