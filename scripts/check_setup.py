"""Preflight check before ./reproduce.sh: interpreter, package versions, dataset location and completeness.

Exits non-zero with a message saying what to fix. reproduce.sh runs it first.

Usage:
  python scripts/check_setup.py               # quick: files present
  python scripts/check_setup.py --checksums   # also verify SHA256SUMS.txt (reads all ~15 GB)
"""
import argparse
import hashlib
import os
import re
import sys
from importlib import metadata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))


def check_packages():
    """Return problems as strings. Version mismatches are warnings: results were bit-identical across
    pandas 2.3/3.1, but only the pinned set is tested."""
    errors, warnings = [], []
    with open(os.path.join(HERE, "..", "requirements.txt")) as fh:
        pins = [m.groups() for line in fh if (m := re.match(r"^([A-Za-z0-9_.-]+)==(\S+)", line.strip()))]
    for name, want in pins:
        try:
            have = metadata.version(name)
        except metadata.PackageNotFoundError:
            errors.append(f"package {name} not installed (pip install -r requirements.txt)")
            continue
        if have != want:
            warnings.append(f"{name} {have} installed, {want} pinned")
    return errors, warnings


def check_dataset(root, checksums):
    errors = []
    if not os.path.isdir(root):
        return [f"dataset folder not found: {root}\n  download it (data/README.md) or set AURICLE_ROOT"]
    for f in ("RECORDS", "demographics.csv", "sensor_coordinates.csv"):
        if not os.path.isfile(os.path.join(root, f)):
            errors.append(f"missing {f} in {root}")
    if errors:
        return errors
    from pwta import io
    rids = io.list_records(root)
    missing = [rid for rid in rids for ext in (".hea", ".dat")
               if not os.path.isfile(os.path.join(root, "data", rid, rid + ext))]
    if missing:
        errors.append(f"{len(missing)} record files missing, e.g. {missing[:3]} (incomplete download?)")
    if checksums:
        errors += verify_checksums(root)
    return errors


def verify_checksums(root):
    path = os.path.join(root, "SHA256SUMS.txt")
    if not os.path.isfile(path):
        return ["SHA256SUMS.txt not found"]
    bad = []
    with open(path) as fh:
        entries = [line.split(maxsplit=1) for line in fh if line.strip()]
    for i, (digest, name) in enumerate(entries, 1):
        name = name.strip()
        h = hashlib.sha256()
        try:
            with open(os.path.join(root, name), "rb") as f:
                for block in iter(lambda: f.read(1 << 22), b""):
                    h.update(block)
        except FileNotFoundError:
            bad.append(name)
            continue
        if h.hexdigest() != digest:
            bad.append(name)
        print(f"\r  checksums {i}/{len(entries)}", end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)
    return [f"{len(bad)} files fail SHA256SUMS.txt, e.g. {bad[:3]}"] if bad else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checksums", action="store_true", help="verify every file against SHA256SUMS.txt (slow)")
    a = ap.parse_args()
    errors, warnings = [], []
    if sys.version_info < (3, 12):  # numpy 2.5 / scipy 1.18 need 3.12
        errors.append(f"Python {sys.version.split()[0]}: need >= 3.12 (tested on 3.13 and 3.15)")
    e, w = check_packages()
    errors += e
    warnings += w
    if not e:  # pwta.io imports wfdb
        from pwta import io
        root = io.DATA_ROOT
        errors += check_dataset(root, a.checksums)
    else:
        root = "(not checked)"
    print(f"python   {sys.executable} ({sys.version.split()[0]})")
    print(f"dataset  {root}")
    for msg in warnings:
        print(f"WARNING  {msg}")
    for msg in errors:
        print(f"ERROR    {msg}")
    if errors:
        sys.exit(1)
    print("setup ok")


if __name__ == "__main__":
    main()
