#!/usr/bin/env bash
# EXP_REP_VALIDITY_V1 -- A100 Stage 1 driver (mission §26, §27).
#
# Everything verifiable is verified before the GPU is started, and the GPU is stopped again
# as soon as artifacts are back. Idle A100 time is the single easiest way to spend money on
# this project without buying information.
#
# Usage:
#   ./run_gpu_experiment.sh EXP_REP_VALIDITY_V1 [--probe linear|mlp] [--keep-gpu]
set -euo pipefail

EXPERIMENT="${1:-EXP_REP_VALIDITY_V1}"
shift || true
PROBE="linear"
KEEP_GPU=0
SMOKE_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --probe) PROBE="$2"; shift 2 ;;
    --keep-gpu) KEEP_GPU=1; shift ;;
    --smoke-only) SMOKE_ONLY=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

ZONE="europe-west4-a"
INSTANCE="a100"
PROJECT="project-08679972-d14a-4025-94f"
REMOTE_DIR="~/max_ev_representation_v1"
MODEL="Qwen/Qwen3-8B"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="experiments/max_ev_representation_v1"
DATA_DIR="$REPO/$EXP_DIR/dataset/v1"
RESULTS_DIR="$REPO/$EXP_DIR/results/stage1"
LOG_DIR="$REPO/$EXP_DIR/results/logs"
mkdir -p "$RESULTS_DIR" "$LOG_DIR"
LOG="$LOG_DIR/${EXPERIMENT}_${PROBE}.log"

say() { printf '\n=== %s ===\n' "$1" | tee -a "$LOG"; }

say "1/8 local state"
git -C "$REPO" rev-parse --abbrev-ref HEAD | tee -a "$LOG"
git -C "$REPO" rev-parse HEAD | tee -a "$LOG"
if [ -n "$(git -C "$REPO" status --porcelain -- "$EXP_DIR")" ]; then
  echo "WARNING: experiment tree has uncommitted changes; the run manifest will record this." \
    | tee -a "$LOG"
fi

say "2/8 dataset integrity"
python3 - "$DATA_DIR" <<'PY' | tee -a "$LOG"
import hashlib, json, sys
from pathlib import Path
d = Path(sys.argv[1])
manifest = json.loads((d / "MANIFEST.json").read_text())
bad = 0
for split, meta in sorted(manifest["splits"].items()):
    got = hashlib.sha256((d / f"{split}.jsonl.gz").read_bytes()).hexdigest()
    ok = got == meta["sha256"]
    bad += not ok
    print(f"  {split:22s} {'OK ' if ok else 'MISMATCH'} {got[:16]} rows={meta['rows']}")
print(f"  dataset_version={manifest['dataset_version']} total_rows="
      f"{sum(m['rows'] for m in manifest['splits'].values())}")
sys.exit(1 if bad else 0)
PY

say "3/8 renderer identity"
FROZEN_REPO="/Users/moheet/Documents/ChatGPT/hamiltonian-lang-final-signal"
EXPECTED_RENDERER="b011511e72572608eb7836d3b8a1a6bb794c890d"
ACTUAL_RENDERER="$(git -C "$FROZEN_REPO" rev-parse HEAD)"
echo "  expected $EXPECTED_RENDERER" | tee -a "$LOG"
echo "  actual   $ACTUAL_RENDERER" | tee -a "$LOG"
[ "$ACTUAL_RENDERER" = "$EXPECTED_RENDERER" ] || { echo "renderer commit mismatch" | tee -a "$LOG"; exit 1; }
shasum -a 256 "$FROZEN_REPO/src/hamiltonian_lang/semantic_state/view.py" | tee -a "$LOG"

say "4/8 start GPU"
STATUS="$(gcloud compute instances describe "$INSTANCE" --zone "$ZONE" --project "$PROJECT" \
  --format='value(status)')"
echo "  status: $STATUS" | tee -a "$LOG"
if [ "$STATUS" != "RUNNING" ]; then
  gcloud compute instances start "$INSTANCE" --zone "$ZONE" --project "$PROJECT" | tee -a "$LOG"
fi
GPU_START="$(date +%s)"
for i in $(seq 1 30); do
  if gcloud compute ssh --zone "$ZONE" "$INSTANCE" --project "$PROJECT" \
       --command "true" >/dev/null 2>&1; then break; fi
  echo "  waiting for ssh ($i) ..." | tee -a "$LOG"
done

ssh_run() { gcloud compute ssh --zone "$ZONE" "$INSTANCE" --project "$PROJECT" --command "$1"; }

say "5/8 sync code and data"
ssh_run "mkdir -p $REMOTE_DIR" | tee -a "$LOG"
TARBALL="/tmp/${EXPERIMENT}_payload.tar.gz"
tar -czf "$TARBALL" -C "$REPO" \
  "$EXP_DIR/__init__.py" "$EXP_DIR/arms" "$EXP_DIR/canon" "$EXP_DIR/mutate" \
  "$EXP_DIR/audit" "$EXP_DIR/dataset" "$EXP_DIR/harness"
gcloud compute scp --zone "$ZONE" --project "$PROJECT" "$TARBALL" "$INSTANCE:$REMOTE_DIR/" \
  | tee -a "$LOG"
# The frozen renderer travels with the payload: the HML arm is only meaningful at b011511.
FROZEN_TARBALL="/tmp/${EXPERIMENT}_frozen.tar.gz"
tar -czf "$FROZEN_TARBALL" -C "$FROZEN_REPO" src/hamiltonian_lang
gcloud compute scp --zone "$ZONE" --project "$PROJECT" "$FROZEN_TARBALL" "$INSTANCE:$REMOTE_DIR/" \
  | tee -a "$LOG"
ssh_run "cd $REMOTE_DIR && tar -xzf $(basename "$TARBALL") && tar -xzf $(basename "$FROZEN_TARBALL")" \
  | tee -a "$LOG"

say "6/8 remote environment"
ssh_run "python3 -c 'import torch;print(\"torch\",torch.__version__,torch.version.cuda,torch.cuda.is_available())'" \
  | tee -a "$LOG"
ssh_run "python3 -m pip install --quiet --upgrade 'transformers>=4.51' 'accelerate' 'numpy' 2>&1 | tail -3" \
  | tee -a "$LOG"
ssh_run "nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader" | tee -a "$LOG"

say "7/8 smoke test (32 items per split, real model)"
ssh_run "cd $REMOTE_DIR && PYTHONPATH=.:src python3 -m $EXP_DIR.harness.stage1 \
  --data $EXP_DIR/dataset/v1 --out $EXP_DIR/results/stage1 --model $MODEL \
  --device cuda --smoke 32 --seeds 0 --probe linear 2>&1 | tail -40" | tee -a "$LOG"

if [ "$SMOKE_ONLY" -eq 1 ]; then
  say "smoke-only requested; skipping the full run"
else
  say "8/8 full Stage 1 ($PROBE probe)"
  ssh_run "cd $REMOTE_DIR && PYTHONPATH=.:src python3 -m $EXP_DIR.harness.stage1 \
    --data $EXP_DIR/dataset/v1 --out $EXP_DIR/results/stage1 --model $MODEL \
    --device cuda --seeds 0 1 2 --probe $PROBE 2>&1 | tail -60" | tee -a "$LOG"
fi

say "artifacts back"
gcloud compute scp --zone "$ZONE" --project "$PROJECT" --recurse \
  "$INSTANCE:$REMOTE_DIR/$EXP_DIR/results/stage1/*" "$RESULTS_DIR/" | tee -a "$LOG"

GPU_SECONDS=$(( $(date +%s) - GPU_START ))
printf '\nGPU wall seconds: %s (%.2f h)\n' "$GPU_SECONDS" \
  "$(python3 -c "print($GPU_SECONDS/3600)")" | tee -a "$LOG"

if [ "$KEEP_GPU" -eq 0 ]; then
  say "stopping GPU"
  gcloud compute instances stop "$INSTANCE" --zone "$ZONE" --project "$PROJECT" \
    --discard-local-ssd=false | tee -a "$LOG"
  gcloud compute instances describe "$INSTANCE" --zone "$ZONE" --project "$PROJECT" \
    --format='value(status)' | tee -a "$LOG"
else
  echo "GPU left running by request (--keep-gpu). Stop it with:" | tee -a "$LOG"
  echo "  gcloud compute instances stop $INSTANCE --zone $ZONE --project $PROJECT --discard-local-ssd=false" \
    | tee -a "$LOG"
fi

say "done"
echo "log:     $LOG"
echo "results: $RESULTS_DIR"
