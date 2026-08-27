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

# Overridable: the original a2-ultragpu-1g in europe-west4-a became unobtainable
# (ZONE_RESOURCE_POOL_EXHAUSTED across every A100 zone probed), so the run moved to an
# A100-40GB in us-central1-b. Qwen3-8B in bf16 is ~16GB of weights, so 40GB is ample.
ZONE="${GPU_ZONE:-us-central1-b}"
INSTANCE="${GPU_INSTANCE:-a100-40}"
PROJECT="project-08679972-d14a-4025-94f"
REMOTE_DIR="~/max_ev_representation_v1"
MODEL="Qwen/Qwen3-8B"
# hidden_states returns one tensor per layer, so the activation footprint scales with
# layers x batch_tokens. 8192 keeps that comfortable on a 40GB card.
BATCH_TOKENS="${BATCH_TOKENS:-8192}"
# Immutable HF commit. Never run science against a floating branch: an upstream reupload
# would silently change the experiment. Also the revision the 50K corpus was preflighted on.
MODEL_REVISION="b968826d9c46dd6066d109eabc6255188de91218"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="experiments/max_ev_representation_v1"
MODULE="experiments.max_ev_representation_v1"   # dotted form; EXP_DIR is the path form
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

say "3/8 counterfactual split isolation (hard gate)"
PYTHONPATH="$REPO" python3 -c "
import json,sys
sys.path.insert(0,'$REPO')
from experiments.max_ev_representation_v1.audit.counterfactual_splits import audit_splits
a=audit_splits('$DATA_DIR').to_dict()
for k in ('families_total','source_families_total','cross_split_family_leaks',
          'cross_split_source_family_leaks','exact_duplicate_leaks','near_duplicate_leaks'):
    print(f'  {k:34s} {a[k]}')
print('  verdict', a['verdict'])
sys.exit(0 if a['verdict']=='PASS' else 1)
" | tee -a "$LOG"

say "3b/8 renderer identity"
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
# A stopped A100 is not a reserved A100. Releasing capacity can mean not getting it back:
# the first attempt after our own stop returned ZONE_RESOURCE_POOL_EXHAUSTED for
# a2-ultragpu-1g in this zone. Stockouts usually clear in minutes, so retry rather than
# abandoning the run -- and report each attempt, because a silent retry loop is
# indistinguishable from a hang.
START_ATTEMPTS="${START_ATTEMPTS:-20}"
START_INTERVAL="${START_INTERVAL:-180}"
if [ "$STATUS" != "RUNNING" ]; then
  started_ok=0
  for attempt in $(seq 1 "$START_ATTEMPTS"); do
    if gcloud compute instances start "$INSTANCE" --zone "$ZONE" --project "$PROJECT" \
         >>"$LOG" 2>&1; then
      echo "  start attempt $attempt: OK" | tee -a "$LOG"
      started_ok=1
      break
    fi
    if grep -q "ZONE_RESOURCE_POOL_EXHAUSTED\|STOCKOUT" "$LOG"; then
      echo "  start attempt $attempt/$START_ATTEMPTS: zone stockout, retrying in ${START_INTERVAL}s" \
        | tee -a "$LOG"
    else
      echo "  start attempt $attempt/$START_ATTEMPTS failed for a non-capacity reason; see log" \
        | tee -a "$LOG"
    fi
    sleep "$START_INTERVAL"
  done
  if [ "$started_ok" -ne 1 ]; then
    echo "GPU_UNAVAILABLE: could not start $INSTANCE in $ZONE after $START_ATTEMPTS attempts." \
      | tee -a "$LOG"
    echo "Nothing was spent. CPU artifacts are complete and the run can be resumed unchanged." \
      | tee -a "$LOG"
    exit 3
  fi
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
# The frozen renderer is NOT shipped. Stage 1 consumes rendered text and never renders or
# parses, so the GPU needs no hamiltonian_lang (whose StrEnum requires 3.11; the image has
# 3.10). Renderer identity is verified locally in step 3, where it is what actually matters.
ssh_run "cd $REMOTE_DIR && tar -xzf $(basename "$TARBALL")" | tee -a "$LOG"

say "6/8 remote environment"
ssh_run "python3 -c 'import torch;print(\"torch\",torch.__version__,torch.version.cuda,torch.cuda.is_available())'" \
  | tee -a "$LOG"
ssh_run "python3 -m pip install --quiet --upgrade 'transformers>=4.51' 'accelerate' 'numpy' 2>&1 | tail -3" \
  | tee -a "$LOG"
# Upgrading transformers drags torchaudio/torchvision forward with it, and the Deep Learning
# image pins torch. The result is an ABI break -- torchaudio 2.11 against torch 2.9.1 fails
# with "undefined symbol: torch_library_impl" the moment transformers touches it. Neither is
# needed for a text model, so remove them rather than downgrade the transformers that Qwen3
# requires.
ssh_run "sudo python3 -m pip uninstall -y torchaudio torchvision 2>&1 | tail -2" | tee -a "$LOG"
ssh_run "python3 -c 'from transformers import AutoModel; import torch; print(\"import path OK, cuda\", torch.cuda.is_available())'" \
  | tee -a "$LOG"
ssh_run "nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader" | tee -a "$LOG"

say "7/8 smoke test (32 items per split, real model)"
ssh_run "cd $REMOTE_DIR && PYTHONPATH=. python3 -m $MODULE.harness.stage1 \
  --data $EXP_DIR/dataset/v1 --out $EXP_DIR/results/stage1 --model $MODEL --revision $MODEL_REVISION \
  --device cuda --batch-tokens $BATCH_TOKENS --smoke 32 --seeds 0 --probe linear 2>&1 | tail -40" | tee -a "$LOG"

if [ "$SMOKE_ONLY" -eq 1 ]; then
  say "smoke-only requested; skipping the full run"
else
  say "8/8 full Stage 1 ($PROBE probe)"
  ssh_run "cd $REMOTE_DIR && PYTHONPATH=. python3 -m $MODULE.harness.stage1 \
    --data $EXP_DIR/dataset/v1 --out $EXP_DIR/results/stage1 --model $MODEL --revision $MODEL_REVISION \
    --cache $EXP_DIR/cache --device cuda --batch-tokens $BATCH_TOKENS --seeds 0 1 2 --probe $PROBE 2>&1 | tail -80" | tee -a "$LOG"
fi

say "artifacts back (results + feature cache)"
gcloud compute scp --zone "$ZONE" --project "$PROJECT" --recurse \
  "$INSTANCE:$REMOTE_DIR/$EXP_DIR/results/stage1" "$RESULTS_DIR/" | tee -a "$LOG"
# The cache is why Stage 2 will be nearly GPU-free; leaving it on a stopped VM wastes that.
mkdir -p "$REPO/$EXP_DIR/cache"
gcloud compute scp --zone "$ZONE" --project "$PROJECT" --recurse \
  "$INSTANCE:$REMOTE_DIR/$EXP_DIR/cache" "$REPO/$EXP_DIR/" 2>&1 | tail -3 | tee -a "$LOG" || \
  echo "  (no cache produced)" | tee -a "$LOG"

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
