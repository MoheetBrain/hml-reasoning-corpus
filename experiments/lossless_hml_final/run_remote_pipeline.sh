#!/usr/bin/env bash
set -u

export PATH="/home/moheet/.elan/bin:/home/moheet/.local/bin:${PATH}"
export CACHE_DIR="/home/moheet/.cache/lean_dojo"
export HML_MODEL_PATH="/home/moheet/hmlpilot/model"
export LOSSLESS_HML_RUNTIME="/home/moheet/lossless_hml_runtime"

runtime="${LOSSLESS_HML_RUNTIME}"
code_dir="${runtime}/code/lossless_hml_final"
logs="${runtime}/logs"
status="${runtime}/pipeline_status.json"

mkdir -p "${logs}"
cd "${code_dir}" || exit 90

write_status() {
  local stage="$1"
  local state="$2"
  local detail="${3:-}"
  python3 - "${status}" "${stage}" "${state}" "${detail}" <<'PY'
import datetime
import json
import pathlib
import sys

path, stage, state, detail = sys.argv[1:]
pathlib.Path(path).write_text(json.dumps({
    "updated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "stage": stage,
    "state": state,
    "detail": detail,
}, sort_keys=True, indent=2) + "\n")
PY
}

wait_for_exit_file() {
  local path="$1"
  while [[ ! -f "${path}" ]]; do
    sleep 30
  done
  [[ "$(tr -d '[:space:]' < "${path}")" == "0" ]]
}

run_stage() {
  local stage="$1"
  shift
  write_status "${stage}" "running"
  "$@" > "${logs}/${stage}.log" 2>&1
  local rc=$?
  printf '%s\n' "${rc}" > "${runtime}/${stage}.exit"
  if [[ ${rc} -ne 0 ]]; then
    write_status "${stage}" "failed" "exit=${rc}"
    exit "${rc}"
  fi
  write_status "${stage}" "complete"
}

write_status "raw_train" "waiting_for_existing_stage"
if ! wait_for_exit_file "${logs}/raw_train.exit"; then
  write_status "raw_train" "failed" "existing training session failed"
  exit 10
fi

write_status "dev_preflight" "waiting_for_existing_stage"
if ! wait_for_exit_file "${logs}/dev_preflight.exit"; then
  write_status "dev_preflight" "failed" "existing preflight session failed"
  exit 11
fi

run_stage "calibration_exp60" python3 run_experiment.py calibrate --max-expansions 60
calibration_result="${runtime}/calibration_exp60_result.json"
calibration_expansions=60
calibration_rate="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["raw_solve_rate"])' "${calibration_result}")"

if python3 -c 'import sys; raise SystemExit(0 if float(sys.argv[1]) < 0.10 else 1)' "${calibration_rate}"; then
  write_status "calibration" "solver_not_calibrated" "raw_solve_rate=${calibration_rate}"
  printf '%s\n' "SOLVER_NOT_CALIBRATED" > "${runtime}/SOLVER_NOT_CALIBRATED"
  exit 12
fi

if python3 -c 'import sys; raise SystemExit(0 if float(sys.argv[1]) < 0.20 else 1)' "${calibration_rate}"; then
  run_stage "calibration_exp100" python3 run_experiment.py calibrate --max-expansions 100
  calibration_result="${runtime}/calibration_exp100_result.json"
  calibration_expansions=100
  calibration_rate="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["raw_solve_rate"])' "${calibration_result}")"
elif python3 -c 'import sys; raise SystemExit(0 if float(sys.argv[1]) > 0.50 else 1)' "${calibration_rate}"; then
  run_stage "calibration_exp25" python3 run_experiment.py calibrate --max-expansions 25
  calibration_result="${runtime}/calibration_exp25_result.json"
  calibration_expansions=25
  calibration_rate="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["raw_solve_rate"])' "${calibration_result}")"
fi

if python3 -c 'import sys; raise SystemExit(0 if float(sys.argv[1]) < 0.20 else 1)' "${calibration_rate}"; then
  write_status "calibration" "solver_not_calibrated" "raw_solve_rate=${calibration_rate}"
  printf '%s\n' "SOLVER_NOT_CALIBRATED" > "${runtime}/SOLVER_NOT_CALIBRATED"
  exit 13
fi

write_status "calibration" "complete" "raw_solve_rate=${calibration_rate};max_expansions=${calibration_expansions}"
run_stage "lossless_hml_train" python3 run_experiment.py train --arm lossless_hml
run_stage "eval_preflight" python3 run_experiment.py preflight --kind eval
run_stage "evaluation" python3 run_experiment.py evaluate --max-expansions "${calibration_expansions}"
run_stage "report" python3 run_experiment.py report --max-expansions "${calibration_expansions}" --calibration-result "${calibration_result}"
write_status "pipeline" "complete" "max_expansions=${calibration_expansions}"
