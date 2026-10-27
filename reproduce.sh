#!/usr/bin/env bash
# Reproduce every result in this repo from the raw Auricle records.
#
#   ./reproduce.sh                       # all stages into outputs/ (~30 min on 6 cores)
#   ./reproduce.sh core drules           # selected stages only
#   OUT=outputs_check ./reproduce.sh     # into another folder, then:
#   .venv-pwta/bin/python scripts/compare_outputs.py outputs outputs_check
#
# Environment (relative paths are from the repo root): PY (interpreter, default .venv-pwta/bin/python), OUT (output
# folder, default outputs; overwriting it replaces the committed results),
# JOBS (parallel workers, default 6; results do not depend on it), AURICLE_ROOT (dataset; default data/<dataset>).
# Stages run in the order given; later stages read earlier outputs.
#   stage       what                                                              needs        minutes (6 cores)
#   core        rest windows (60 s), D prominence sensitivity, summary, plots                   1
#   filters     derivative-filter screen (15 filters), SG grid (28 + reference)                 4
#   drules      the four D-wave rules and their comparison                                      1.5
#   stratified  20-s rest windows; sessions / CNAP / rebound / exercise time course core        0.5
#   hf          HF vs control discrimination and age-robust checks                core        1
#   sweep       20-s windows over all activities; D-only feature sweep                          1
#   agreement   ear vs finger agreement by level                                  core, sweep <0.1
#   validation  pre-registered validation experiments 1-5 (docs/VALIDATION.md)                 6
#   audit       sensitivity reruns and audit checks (VALIDATION, Audit)           validation   13
set -euo pipefail
case ${1:-} in -h|--help) sed -n '2,/^set -euo/p' "$0" | sed '$d; s/^# \{0,1\}//'; exit 0 ;; esac
cd "$(dirname "$0")"
PY=${PY:-.venv-pwta/bin/python}
OUT=${OUT:-outputs}
JOBS=${JOBS:-6}
STAGES=${*:-core filters drules stratified hf sweep agreement validation audit}
W20="--window-s 20 --min-window-s 15 --settle-s 5"
ALL="--labels 0 1 2 3 4"
J="--jobs $JOBS"
log() { printf '\n=== %s  [%s]\n' "$1" "$(date +%H:%M:%S)"; }
need() { for f in "$@"; do [ -e "$f" ] || { echo "missing $f: run the stage that makes it first (see ./reproduce.sh --help)"; exit 1; }; done; }

for stage in $STAGES; do case $stage in
  core|filters|drules|stratified|hf|sweep|agreement|validation|audit) ;;
  *) echo "unknown stage: $stage (see ./reproduce.sh --help)"; exit 1 ;;
esac; done
[ -x "$PY" ] || { echo "no interpreter at $PY: create the venv (README, Reproduce) or set PY=..."; exit 1; }
"$PY" scripts/check_setup.py
mkdir -p "$OUT"

for stage in $STAGES; do case $stage in
core)
  log "core: rest windows"
  "$PY" scripts/run_batch.py $J --out "$OUT/windows_rest.csv"
  "$PY" scripts/run_batch.py $J --d-prom 0.10 --out "$OUT/sensitivity/dprom_010.csv"
  "$PY" scripts/summarise.py "$OUT/windows_rest.csv" --sensitivity "$OUT"/sensitivity/*.csv --out "$OUT/summary" > /dev/null
  "$PY" scripts/plot_record.py HC_2_1 HC_9_1 HC_16_1 HC_34_1 HC_37_1 HFC_102_1 HFC_117_1 HFC_139_1 --out "$OUT/plots"
  ;;
filters)
  log "filters: screen + SG grid"
  "$PY" scripts/run_batch.py $J --specs bw:40 raw sg:21:2 sg:41:2 sg:61:2 sg:101:2 sg:41:4 sg:61:4 sg:101:4 \
      bw:10 bw:15 bw:20 gauss:5 gauss:10 gauss:20 --out "$OUT/screen/screen_rest.csv"
  "$PY" scripts/screen_filters.py "$OUT/screen/screen_rest.csv" > /dev/null
  specs="bw:40"; for w in 11 21 31 41 51 61 81 101 121 151; do for o in 2 4 6; do
    [ "$w" = 11 ] && [ "$o" != 2 ] && continue; specs="$specs sg:$w:$o"; done; done
  "$PY" scripts/run_batch.py $J --specs $specs --out "$OUT/sg_grid/sg_grid_rest.csv"
  "$PY" scripts/screen_filters.py "$OUT/sg_grid/sg_grid_rest.csv" > /dev/null
  ;;
drules)
  log "drules"
  for r in window rebound rebound_es rebound_es+shoulder; do
    "$PY" scripts/run_batch.py $J --d-rule "$r" --out "$OUT/drules/$r.csv"; done
  "$PY" scripts/compare_d_rules.py "$OUT"/drules/{window,rebound,rebound_es,rebound_es+shoulder}.csv > /dev/null
  ;;
stratified)
  log "stratified"
  need "$OUT/windows_rest.csv"
  "$PY" scripts/run_batch.py $J $W20 --out "$OUT/timecourse/windows_rest_20s.csv"
  "$PY" scripts/stratified_checks.py "$OUT/windows_rest.csv" "$OUT/timecourse/windows_rest_20s.csv" --out "$OUT/stratified" > /dev/null
  ;;
hf)
  log "hf classification"
  need "$OUT/windows_rest.csv"
  "$PY" scripts/classify_hf.py "$OUT/windows_rest.csv" --out "$OUT/hf_classification" > /dev/null
  ;;
sweep)
  log "feature sweep"
  "$PY" scripts/run_batch.py $J $ALL $W20 --out "$OUT/sweep/windows_all_20s.csv"
  "$PY" scripts/feature_sweep.py "$OUT/sweep/windows_all_20s.csv" --out "$OUT/sweep" > /dev/null
  ;;
agreement)
  log "site agreement"
  need "$OUT/windows_rest.csv" "$OUT/sweep/windows_all_20s.csv"
  "$PY" scripts/site_agreement.py "$OUT/windows_rest.csv" "$OUT/sweep/windows_all_20s.csv" --out "$OUT/site_agreement"
  ;;
validation)
  log "validation: windows + references"
  V="$OUT/validation"
  "$PY" scripts/run_batch.py $J --out "$V/windows_rest.csv"
  "$PY" scripts/run_batch.py $J $ALL $W20 --out "$V/windows_all_20s.csv"
  "$PY" scripts/run_reference.py $J --out "$V/reference_rest.csv"
  "$PY" scripts/run_reference.py $J $ALL $W20 --out "$V/reference_all_20s.csv"
  log "validation: experiments"
  "$PY" scripts/validate_construct.py --dir "$V" --out "$V/exp1_construct" > /dev/null
  "$PY" scripts/validate_site_rebound.py $J --dir "$V" --out "$V/exp2_site_rebound" > /dev/null
  "$PY" scripts/validate_flattening.py --windows "$V/windows_rest.csv" --out "$V/exp3_flattening" > /dev/null
  "$PY" scripts/validate_incremental.py $J --windows "$V/windows_rest.csv" --out "$V/exp4_incremental" > /dev/null
  "$PY" scripts/validate_precision.py --windows "$V/windows_rest.csv" --out "$V/exp5_precision" > /dev/null
  ;;
audit)
  log "audit: sensitivity reruns"
  V="$OUT/validation"; A="$V/audit"
  need "$V/windows_rest.csv" "$V/windows_all_20s.csv" "$V/reference_rest.csv" "$V/reference_all_20s.csv"
  "$PY" scripts/run_batch.py $J --post-ms 1200 --out "$A/windows_rest_post1200.csv"
  "$PY" scripts/audit_checks.py variants --dir "$V"
  for t in post1200 annotated post1200_annotated steady; do
    "$PY" scripts/validate_flattening.py --windows "$A/windows_rest_$t.csv" --out "$A/exp3_$t" > /dev/null
    "$PY" scripts/validate_precision.py --windows "$A/windows_rest_$t.csv" --out "$A/exp5_$t" > /dev/null
    [ "$t" = steady ] || "$PY" scripts/validate_incremental.py $J --windows "$A/windows_rest_$t.csv" --out "$A/exp4_$t" > /dev/null
  done
  "$PY" scripts/classify_hf.py "$A/windows_rest_annotated.csv" --out "$A/hf_annotated" > /dev/null
  log "audit: checks"
  "$PY" scripts/audit_checks.py checks --dir "$V" > /dev/null
  ;;
esac; done
log "done -> $OUT (${SECONDS}s)"
