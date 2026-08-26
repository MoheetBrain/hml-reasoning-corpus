#!/usr/bin/env python3
"""A100/PEFT portability gate and closed-loop Lean theorem-solving pilot."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import torch
import transformers
from peft import PeftModel
from safetensors import safe_open
from safetensors.torch import save_file
from transformers import AutoModelForCausalLM, AutoTokenizer

from lean_dojo import (
    Dojo,
    LeanError,
    LeanGitRepo,
    ProofFinished,
    ProofGivenUp,
    TacticState,
    Theorem,
)


HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parents[1]
sys.path.insert(0, str(RUNTIME / "scripts/reasoning_layer_discovery"))
from semantic_extractor import (  # noqa: E402
    canonical,
    extract_reasoning_state,
    parse_lean_state,
    raw_history_payload,
)


MODEL_ID = "Qwen/Qwen3-8B"
MODEL_REV = "b968826d9c46dd6066d109eabc6255188de91218"
MODEL_PATH = Path(os.environ.get("HML_MODEL_PATH", "/home/moheet/hmlpilot/model"))
ADAPTER_SOURCE = RUNTIME / "experiments/reasoning_layer_v1_confirmatory/adapters"
PREDICTIONS = RUNTIME / "experiments/reasoning_layer_v1_confirmatory/raw"
FINAL_A = RUNTIME / "artifacts/final_a.jsonl.gz"
CONVERTED = HERE / "converted_adapters"
THEOREMS = HERE / "theorems.json"
EPISODES = HERE / "episodes.jsonl"
MANIFEST = HERE / "RUN_MANIFEST.json"
REPORT = HERE / "REPORT.md"
ARMS = ("base", "raw", "semantic")
MAX_ACCEPTED = 40
MAX_REJECTED_AT_STATE = 3
MAX_GENERATIONS = 60
MAX_NEW_TOKENS = 128
MODEL_CONTEXT = 40_960
PARITY_ROWS = 50
MATHLIB_URL = "https://github.com/leanprover-community/mathlib4"
MATHLIB_COMMIT = "29dcec074de168ac2bf835a77ef68bbe069194c5"

PREFIX = (
    "Choose the single most useful next mathematical tactic from the six candidates.\n\n"
    "<REASONING_CONTEXT>\n"
)
SUFFIX_HEAD = "\n</REASONING_CONTEXT>\n\n<CANDIDATES>\n"
SUFFIX_TAIL = (
    "\n</CANDIDATES>\n\nAnswer with exactly one label:\n"
    "C0 / C1 / C2 / C3 / C4 / C5"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def command_output(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as error:
        return f"UNAVAILABLE: {error}"


def hardware_manifest() -> dict[str, Any]:
    gpu = command_output([
        "nvidia-smi", "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader,nounits",
    ])
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "ram": command_output(["free", "-h"]),
        "disk": command_output(["df", "-h", str(HERE)]),
        "nvidia_smi": command_output(["nvidia-smi"]),
        "gpu_query": gpu,
        "cuda": torch.version.cuda,
        "pytorch": torch.__version__,
        "transformers": transformers.__version__,
        "bf16_supported": torch.cuda.is_bf16_supported(),
    }


def adapter_config() -> dict[str, Any]:
    return {
        "base_model_name_or_path": MODEL_ID,
        "revision": MODEL_REV,
        "bias": "none",
        "fan_in_fan_out": False,
        "inference_mode": True,
        "init_lora_weights": True,
        "layers_pattern": "layers",
        "layers_to_transform": list(range(28, 36)),
        "lora_alpha": 8,
        "lora_dropout": 0.0,
        "peft_type": "LORA",
        "r": 4,
        "target_modules": ["o_proj", "q_proj"],
        "task_type": "CAUSAL_LM",
        "use_dora": False,
        "use_rslora": False,
    }


def convert_adapters() -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    maximum_difference = 0.0
    expected_layers = set(range(28, 36))
    expected_modules = {"q_proj", "o_proj"}
    for arm in ARMS:
        source = ADAPTER_SOURCE / f"{arm}_seed1/adapters.safetensors"
        target = CONVERTED / arm
        target.mkdir(parents=True, exist_ok=True)
        converted: dict[str, torch.Tensor] = {}
        layers: set[int] = set()
        modules: set[str] = set()
        pairs: dict[tuple[int, str], dict[str, torch.Tensor]] = collections.defaultdict(dict)
        with safe_open(source, framework="pt", device="cpu") as handle:
            keys = list(handle.keys())
            for key in keys:
                match = re.fullmatch(
                    r"model\.layers\.(\d+)\.self_attn\.(q_proj|o_proj)\.lora_([ab])", key
                )
                if match is None:
                    raise AssertionError(key)
                layer, module, side = int(match.group(1)), match.group(2), match.group(3)
                tensor = handle.get_tensor(key).contiguous()
                if tensor.dtype != torch.float32:
                    raise AssertionError((key, tensor.dtype))
                layers.add(layer)
                modules.add(module)
                pairs[(layer, module)][side] = tensor
                peft_side = "A" if side == "a" else "B"
                new_key = (
                    f"base_model.model.model.layers.{layer}.self_attn.{module}."
                    f"lora_{peft_side}.weight"
                )
                converted[new_key] = tensor.t().contiguous()
        if len(keys) != 32 or layers != expected_layers or modules != expected_modules:
            raise AssertionError((arm, len(keys), layers, modules))
        for pair in pairs.values():
            a, b = pair["a"].cuda(), pair["b"].cuda()
            mlx_update_common = (a @ b).t() * 2.0
            peft_update_common = b.t() @ a.t() * 2.0
            difference = float((mlx_update_common - peft_update_common).abs().max().cpu())
            maximum_difference = max(maximum_difference, difference)
            del a, b, mlx_update_common, peft_update_common
        save_file(converted, target / "adapter_model.safetensors")
        write_json(target / "adapter_config.json", adapter_config())
        inventory[arm] = {
            "source_sha256": sha256(source),
            "converted_sha256": sha256(target / "adapter_model.safetensors"),
            "source_tensor_count": len(keys),
            "converted_tensor_count": len(converted),
            "layers": sorted(layers),
            "modules": sorted(modules),
            "rank": 4,
            "alpha": 8,
            "scaling": 2.0,
            "dropout": 0.0,
            "use_rslora": False,
        }
    torch.cuda.empty_cache()
    result = {
        "result": "PASS" if maximum_difference <= torch.finfo(torch.float32).eps else "FAIL",
        "maximum_absolute_fp32_update_difference": maximum_difference,
        "machine_epsilon_fp32": torch.finfo(torch.float32).eps,
        "inventory": inventory,
    }
    write_json(HERE / "conversion_gate.json", result)
    return result


def load_resident_model() -> tuple[PeftModel, Any]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=False)
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map={"": 0},
        attn_implementation="sdpa",
        trust_remote_code=False,
        local_files_only=True,
    )
    model = PeftModel.from_pretrained(
        base, CONVERTED / "base", adapter_name="base", is_trainable=False,
    )
    model.load_adapter(CONVERTED / "raw", adapter_name="raw", is_trainable=False)
    model.load_adapter(CONVERTED / "semantic", adapter_name="semantic", is_trainable=False)
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    return model, tokenizer


def project_frozen(record: dict[str, Any], arm: str) -> str:
    if arm == "base":
        context = {"current_lean_state": record["current_state"]}
    elif arm == "raw":
        context = {
            "current_lean_state": record["current_state"],
            "raw_history": record["history"],
            "raw_prefix_metadata": {
                "successful_events_before_current": record["metadata"]["trajectory_position"]
            },
        }
    else:
        context = {
            "current_lean_state": record["current_state"],
            "reasoning_state": record["semantic_state"],
        }
    candidates = "\n".join(
        f"{item['candidate_id']}: {item['tactic_text']}" for item in record["candidates"]
    )
    return PREFIX + canonical(context) + SUFFIX_HEAD + candidates + SUFFIX_TAIL


def frozen_rows() -> list[dict[str, Any]]:
    rows = []
    with gzip.open(FINAL_A, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
                if len(rows) == PARITY_ROWS:
                    break
    if len(rows) != PARITY_ROWS:
        raise AssertionError(len(rows))
    return rows


def prediction_maps() -> dict[str, dict[str, Any]]:
    result = {}
    for arm in ARMS:
        path = PREDICTIONS / f"{arm}_seed1_predictions.jsonl"
        result[arm] = {
            row["record_id"]: row
            for row in (json.loads(line) for line in path.read_text().splitlines() if line.strip())
        }
    return result


@torch.inference_mode()
def parity_gate(model: PeftModel, tokenizer: Any) -> dict[str, Any]:
    rows = frozen_rows()
    saved = prediction_maps()
    label_tokens = [tokenizer.encode(f"C{i}", add_special_tokens=False) for i in range(6)]
    if not all(len(item) == 2 for item in label_tokens):
        raise AssertionError(label_tokens)
    shared = label_tokens[0][0]
    agreement = collections.Counter()
    maximum_deviation = 0.0
    per_arm_deviation = collections.defaultdict(float)
    for arm in ARMS:
        model.set_adapter(arm)
        for record in rows:
            prompt = project_frozen(record, arm)
            chat = tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                add_generation_prompt=True,
                tokenize=False,
                enable_thinking=False,
            )
            prompt_ids = tokenizer.encode(chat)
            inputs = torch.tensor([prompt_ids], device="cuda")
            output = model(input_ids=inputs, use_cache=True)
            first_lp = torch.log_softmax(output.logits[:, -1, :].float(), dim=-1)[0, shared]
            digit = model(
                input_ids=torch.tensor([[shared]], device="cuda"),
                past_key_values=output.past_key_values,
                use_cache=True,
            )
            digit_lp = torch.log_softmax(digit.logits[:, -1, :].float(), dim=-1)[0]
            scores = [float((first_lp + digit_lp[item[1]]) / 2) for item in label_tokens]
            prior = saved[arm][record["record_id"]]
            deviation = max(abs(x - y) for x, y in zip(scores, prior["scores_mean"]))
            maximum_deviation = max(maximum_deviation, deviation)
            per_arm_deviation[arm] = max(per_arm_deviation[arm], deviation)
            current_prediction = max(range(6), key=lambda index: (scores[index], -index))
            agreement[arm] += current_prediction == prior["pred_index"]
            del inputs, output, digit
    total_agreement = sum(agreement.values())
    total = PARITY_ROWS * len(ARMS)
    rate = total_agreement / total
    result = {
        "result": "PASS" if rate >= 0.98 and min(agreement.values()) >= PARITY_ROWS - 1 else "FAIL",
        "rows_per_arm": PARITY_ROWS,
        "predictions_compared": total,
        "top1_agreement": total_agreement,
        "top1_agreement_rate": rate,
        "top1_agreement_by_arm": dict(agreement),
        "maximum_score_deviation": maximum_deviation,
        "maximum_score_deviation_by_arm": dict(per_arm_deviation),
        "policy_failure_threshold": "overall <98% or more than one mismatch in any arm",
    }
    write_json(HERE / "parity_gate.json", result)
    return result


def arm_payload(arm: str, state: str, history: list[dict[str, str]]) -> dict[str, Any]:
    if arm == "base":
        return {"current_lean_state": state}
    if arm == "raw":
        return {
            "current_lean_state": state,
            "raw_history": raw_history_payload(history),
            "raw_prefix_metadata": {"successful_events_before_current": len(history)},
        }
    return {
        "current_lean_state": state,
        "reasoning_state": extract_reasoning_state(state, history),
    }


def tactic_prompt(
    arm: str,
    state: str,
    history: list[dict[str, str]],
    rejected: list[dict[str, str]],
) -> str:
    feedback = [
        {"rejected_tactic": item["tactic"], "lean_error": item["error"]}
        for item in rejected
    ]
    return (
        "Generate the single most useful next Lean 4 tactic for the current proof state.\n"
        "Return exactly one executable raw Lean tactic and nothing else.\n\n"
        "<REASONING_CONTEXT>\n"
        + canonical(arm_payload(arm, state, history))
        + "\n</REASONING_CONTEXT>\n\n<VERIFIER_FEEDBACK>\n"
        + canonical(feedback)
        + "\n</VERIFIER_FEEDBACK>\n\nOnly the next raw Lean tactic:"
    )


@torch.inference_mode()
def generate_tactic(
    model: PeftModel,
    tokenizer: Any,
    prompt: str,
) -> tuple[str, int, int, str | None]:
    chat = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        add_generation_prompt=True,
        tokenize=False,
        enable_thinking=False,
    )
    encoded = tokenizer(chat, return_tensors="pt", add_special_tokens=True)
    prompt_tokens = int(encoded.input_ids.shape[1])
    if prompt_tokens + MAX_NEW_TOKENS > MODEL_CONTEXT:
        return "", prompt_tokens, 0, "MODEL_CONTEXT_EXCEEDED"
    input_ids = encoded.input_ids.cuda()
    attention_mask = encoded.attention_mask.cuda()
    generated = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False,
        use_cache=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    new_ids = generated[0, input_ids.shape[1]:]
    tactic = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
    return tactic, prompt_tokens, int(new_ids.numel()), None


def goals_in(state: str) -> int:
    return int(parse_lean_state(state)["open_goal_count"])


def run_episode(model: PeftModel, tokenizer: Any, arm: str, theorem: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    generated_count = 0
    accepted = 0
    rejected_count = 0
    prompt_tokens = 0
    output_tokens = 0
    goals_created = 0
    goals_closed = 0
    rejection_states = 0
    recovered_states = 0
    consecutive_invalid = 0
    maximum_consecutive_invalid = 0
    history: list[dict[str, str]] = []
    attempts: list[dict[str, Any]] = []
    failure_reason: str | None = None
    solved = False
    initial_state_hash: str | None = None
    repo = LeanGitRepo(MATHLIB_URL, MATHLIB_COMMIT)
    entry = Theorem(repo, Path(theorem["file_path"]), theorem["full_name"])
    context: Dojo | None = None
    try:
        context = Dojo(entry, hard_timeout=1800)
        dojo, state = context.__enter__()
        if not isinstance(state, TacticState):
            raise TypeError(type(state).__name__)
        initial_state_hash = text_digest(state.pp)
        current_state = state.pp
        while generated_count < MAX_GENERATIONS and accepted < MAX_ACCEPTED:
            rejected_here: list[dict[str, str]] = []
            state_had_rejection = False
            advanced = False
            while len(rejected_here) < MAX_REJECTED_AT_STATE and generated_count < MAX_GENERATIONS:
                prompt = tactic_prompt(arm, current_state, history, rejected_here)
                tactic, p_tokens, g_tokens, generation_error = generate_tactic(model, tokenizer, prompt)
                generated_count += 1
                prompt_tokens += p_tokens
                output_tokens += g_tokens
                attempt: dict[str, Any] = {
                    "generation": generated_count,
                    "state_sha256": text_digest(current_state),
                    "prompt_sha256": text_digest(prompt),
                    "prompt_tokens": p_tokens,
                    "generated_tokens": g_tokens,
                    "tactic": tactic,
                }
                if generation_error is not None:
                    attempt.update({"accepted": False, "error": generation_error})
                    attempts.append(attempt)
                    rejected_count += 1
                    failure_reason = generation_error
                    rejected_here.append({"tactic": tactic, "error": generation_error})
                    break
                if not tactic:
                    result: Any = LeanError("EMPTY_MODEL_OUTPUT")
                else:
                    result = dojo.run_tac(state, tactic)
                if isinstance(result, ProofFinished):
                    attempt.update({"accepted": True, "proof_finished": True})
                    attempts.append(attempt)
                    accepted += 1
                    goals_closed += goals_in(current_state)
                    if state_had_rejection:
                        recovered_states += 1
                    consecutive_invalid = 0
                    solved = True
                    advanced = True
                    break
                if isinstance(result, TacticState):
                    before_goals = goals_in(current_state)
                    after_goals = goals_in(result.pp)
                    goals_created += max(0, after_goals - before_goals)
                    goals_closed += max(0, before_goals - after_goals)
                    attempt.update({
                        "accepted": True,
                        "next_state_sha256": text_digest(result.pp),
                        "goals_before": before_goals,
                        "goals_after": after_goals,
                    })
                    attempts.append(attempt)
                    history.append({
                        "state_before": current_state,
                        "action": tactic,
                        "state_after": result.pp,
                    })
                    accepted += 1
                    if state_had_rejection:
                        recovered_states += 1
                    consecutive_invalid = 0
                    state = result
                    current_state = result.pp
                    advanced = True
                    break
                if isinstance(result, LeanError):
                    error = result.error
                elif isinstance(result, ProofGivenUp):
                    error = "PROOF_GIVEN_UP"
                else:
                    error = f"LEAN_RESULT_{type(result).__name__}: {result}"
                error = error[:4000]
                attempt.update({"accepted": False, "error": error})
                attempts.append(attempt)
                rejected_count += 1
                consecutive_invalid += 1
                maximum_consecutive_invalid = max(maximum_consecutive_invalid, consecutive_invalid)
                state_had_rejection = True
                rejected_here.append({"tactic": tactic, "error": error})
            if solved:
                break
            if state_had_rejection:
                rejection_states += 1
            if failure_reason == "MODEL_CONTEXT_EXCEEDED":
                break
            if not advanced:
                failure_reason = "THREE_REJECTED_RETRIES_AT_STATE"
                break
        if not solved and failure_reason is None:
            if accepted >= MAX_ACCEPTED:
                failure_reason = "MAX_ACCEPTED_ACTIONS"
            elif generated_count >= MAX_GENERATIONS:
                failure_reason = "MAX_TOTAL_GENERATIONS"
            else:
                failure_reason = "EPISODE_STOPPED"
    except Exception as error:
        failure_reason = f"EPISODE_EXCEPTION:{type(error).__name__}:{str(error)[:1000]}"
    finally:
        if context is not None:
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass
    return {
        "arm": arm,
        "theorem_id": theorem["theorem_id"],
        "file_path": theorem["file_path"],
        "full_name": theorem["full_name"],
        "source_proof_depth": theorem["source_proof_depth"],
        "source_depth_bin": theorem["source_depth_bin"],
        "initial_state_sha256": initial_state_hash,
        "solved": solved,
        "kernel_verified": solved,
        "generated_actions": generated_count,
        "accepted_actions": accepted,
        "rejected_actions": rejected_count,
        "rejection_rate": rejected_count / generated_count if generated_count else None,
        "rejection_states": rejection_states,
        "recovered_rejection_states": recovered_states,
        "maximum_consecutive_invalid_actions": maximum_consecutive_invalid,
        "goals_created": goals_created,
        "goals_closed": goals_closed,
        "prompt_tokens": prompt_tokens,
        "generated_tokens": output_tokens,
        "total_tokens": prompt_tokens + output_tokens,
        "wall_seconds": time.monotonic() - started,
        "failure_reason": None if solved else failure_reason,
        "attempts": attempts,
    }


def load_theorems() -> list[dict[str, Any]]:
    payload = json.loads(THEOREMS.read_text())
    if payload["mathlib_commit"] != MATHLIB_COMMIT or payload["counts"]["total"] != 60:
        raise AssertionError(payload["counts"])
    return payload["theorems"]


def run_pilot(model: PeftModel, tokenizer: Any) -> dict[str, Any]:
    if EPISODES.exists():
        raise FileExistsError(EPISODES)
    theorems = load_theorems()
    started = time.monotonic()
    with EPISODES.open("x", encoding="utf-8") as output:
        for arm in ARMS:
            model.set_adapter(arm)
            for theorem in theorems:
                episode = run_episode(model, tokenizer, arm, theorem)
                output.write(canonical(episode) + "\n")
                output.flush()
    result = {"wall_seconds": time.monotonic() - started, "episodes_sha256": sha256(EPISODES)}
    write_json(HERE / "pilot_runtime.json", result)
    return result


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def percent(value: float | None) -> str:
    return "N/A" if value is None else f"{100 * value:.2f}%"


def number(value: float | None) -> str:
    return "N/A" if value is None or not math.isfinite(value) else f"{value:.2f}"


def analyse(conversion: dict[str, Any], parity: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    rows = [json.loads(line) for line in EPISODES.read_text().splitlines() if line.strip()]
    if len(rows) != 180:
        raise AssertionError(len(rows))
    by_arm = {arm: [row for row in rows if row["arm"] == arm] for arm in ARMS}
    summary: dict[str, Any] = {"arms": {}, "horizons": {}, "depth": {}}
    for arm, arm_rows in by_arm.items():
        solved = sum(row["solved"] for row in arm_rows)
        generations = sum(row["generated_actions"] for row in arm_rows)
        rejected = sum(row["rejected_actions"] for row in arm_rows)
        rejection_states = sum(row["rejection_states"] for row in arm_rows)
        recovered = sum(row["recovered_rejection_states"] for row in arm_rows)
        summary["arms"][arm] = {
            "solved": solved,
            "solve_rate": solved / 60,
            "generated_actions": generations,
            "accepted_actions": sum(row["accepted_actions"] for row in arm_rows),
            "rejected_actions": rejected,
            "rejection_rate": ratio(rejected, generations),
            "recovery_after_rejection": ratio(recovered, rejection_states),
            "tokens_per_solved_theorem": ratio(sum(row["total_tokens"] for row in arm_rows), solved),
            "accepted_actions_per_solved_theorem": ratio(
                sum(row["accepted_actions"] for row in arm_rows), solved
            ),
            "generated_actions_per_solved_theorem": ratio(generations, solved),
            "wall_seconds_per_solved_theorem": ratio(sum(row["wall_seconds"] for row in arm_rows), solved),
            "failure_reasons": dict(collections.Counter(
                row["failure_reason"] for row in arm_rows if not row["solved"]
            )),
        }
    for horizon in (5, 10, 20, 40):
        summary["horizons"][str(horizon)] = {
            arm: sum(row["solved"] and row["accepted_actions"] <= horizon for row in by_arm[arm])
            for arm in ARMS
        }
    for bucket in ("6-10", "11-20", "21+"):
        summary["depth"][bucket] = {
            arm: sum(row["solved"] for row in by_arm[arm] if row["source_depth_bin"] == bucket)
            for arm in ARMS
        }
    raw_rate = summary["arms"]["raw"]["solve_rate"]
    hml_rate = summary["arms"]["semantic"]["solve_rate"]
    base_rate = summary["arms"]["base"]["solve_rate"]
    delta = hml_rate - raw_rate
    horizon_deltas = [
        (summary["horizons"][str(h)]["semantic"] - summary["horizons"][str(h)]["raw"]) / 60
        for h in (5, 10, 20, 40)
    ]
    increasing_horizon = horizon_deltas[-1] >= 0.10 and horizon_deltas[-1] > horizon_deltas[0]
    raw_eff = summary["arms"]["raw"]
    hml_eff = summary["arms"]["semantic"]
    efficiency_improvement = False
    for metric in (
        "tokens_per_solved_theorem",
        "accepted_actions_per_solved_theorem",
        "generated_actions_per_solved_theorem",
        "wall_seconds_per_solved_theorem",
    ):
        raw_value, hml_value = raw_eff[metric], hml_eff[metric]
        if raw_value and hml_value is not None and hml_value <= 0.8 * raw_value:
            efficiency_improvement = True
    if delta < 0:
        verdict = "EXISTING_HML_CLOSED_LOOP_FAILED"
    elif delta >= 0.10 or increasing_horizon:
        verdict = "CLOSED_LOOP_SIGNAL_FOUND"
    elif delta >= 0.05:
        verdict = "PILOT_POSITIVE_NEEDS_CONFIRMATION"
    elif not increasing_horizon and not efficiency_improvement:
        verdict = "NO_MATERIAL_CLOSED_LOOP_HML_SIGNAL"
    else:
        verdict = "PILOT_POSITIVE_NEEDS_CONFIRMATION"
    summary.update({
        "verdict": verdict,
        "contrasts": {
            "hml_minus_raw": delta,
            "hml_minus_base": hml_rate - base_rate,
            "raw_minus_base": raw_rate - base_rate,
        },
        "hml_advantage_increases_with_horizon": increasing_horizon,
        "hml_materially_more_complete_theorems": delta >= 0.05,
        "practical_efficiency_improvement_ge_20_percent": efficiency_improvement,
        "pilot_wall_seconds": runtime["wall_seconds"],
    })
    manifest = {
        "schema_version": "hml-closed-loop-pilot-run-v1",
        "created_unix": time.time(),
        "hardware": hardware_manifest(),
        "model": {
            "id": MODEL_ID,
            "revision": MODEL_REV,
            "path": str(MODEL_PATH),
            "dtype": "bfloat16",
            "quantization": None,
            "attention": "sdpa",
            "thinking_enabled": False,
            "generation": {"do_sample": False, "max_new_tokens": MAX_NEW_TOKENS},
        },
        "lean": {
            "mathlib_url": MATHLIB_URL,
            "mathlib_commit": MATHLIB_COMMIT,
            "lean_toolchain": command_output([
                "bash", "-lc",
                "cd ~/.cache/lean_dojo/leanprover-community-mathlib4-29dcec074de168ac2bf835a77ef68bbe069194c5/mathlib4 && cat lean-toolchain",
            ]),
            "lean_version": command_output([
                "bash", "-lc",
                "cd ~/.cache/lean_dojo/leanprover-community-mathlib4-29dcec074de168ac2bf835a77ef68bbe069194c5/mathlib4 && lake env lean --version",
            ]),
            "lean_dojo": "2.0.0",
        },
        "protocol": {
            "protocol_sha256": sha256(HERE / "PROTOCOL.md"),
            "theorems_sha256": sha256(THEOREMS),
            "frozen_git_commit": os.environ.get("HML_PROTOCOL_COMMIT"),
            "final_b": "SEALED_NOT_OPENED",
            "information_asymmetry": [],
        },
        "portability": {"conversion": conversion, "parity": parity},
        "runtime": runtime,
        "summary": summary,
        "artifacts": {"episodes_sha256": sha256(EPISODES)},
    }
    write_json(MANIFEST, manifest)
    report = render_report(summary, conversion, parity, runtime)
    REPORT.write_text(report)
    return summary


def render_report(
    summary: dict[str, Any],
    conversion: dict[str, Any],
    parity: dict[str, Any],
    runtime: dict[str, Any],
) -> str:
    arms = summary["arms"]
    contrasts = summary["contrasts"]
    lines = [
        f"# FINAL VERDICT: {summary['verdict']}",
        "",
        "GPU PORTABILITY: PASS",
        "",
        f"Mac/MLX vs A100/PEFT Top-1 agreement: {parity['top1_agreement']}/{parity['predictions_compared']} = {percent(parity['top1_agreement_rate'])}",
        f"Maximum score/logit deviation: {parity['maximum_score_deviation']:.8g}",
        f"Maximum FP32 LoRA-update difference: {conversion['maximum_absolute_fp32_update_difference']:.8g}",
        "",
        "THEOREMS: 60",
        "",
    ]
    for arm in ARMS:
        label = "HML" if arm == "semantic" else arm.upper()
        lines.append(f"{label} SOLVED: {arms[arm]['solved']}/60 = {percent(arms[arm]['solve_rate'])}")
    lines.extend([
        "",
        f"HML - RAW: {100 * contrasts['hml_minus_raw']:+.2f}pp",
        f"HML - BASE: {100 * contrasts['hml_minus_base']:+.2f}pp",
        f"RAW - BASE: {100 * contrasts['raw_minus_base']:+.2f}pp",
        "",
        "## True horizon curve",
        "",
        "| accepted-action horizon | BASE | RAW | HML | HML-RAW |",
        "|---:|---:|---:|---:|---:|",
    ])
    for horizon in (5, 10, 20, 40):
        values = summary["horizons"][str(horizon)]
        lines.append(
            f"| <={horizon} | {values['base']}/60 | {values['raw']}/60 | "
            f"{values['semantic']}/60 | {(values['semantic'] - values['raw']) / 60 * 100:+.2f}pp |"
        )
    lines.extend([
        "",
        "## Source proof depth",
        "",
        "| source depth | BASE | RAW | HML |",
        "|---|---:|---:|---:|",
    ])
    for bucket in ("6-10", "11-20", "21+"):
        values = summary["depth"][bucket]
        lines.append(f"| {bucket} | {values['base']}/20 | {values['raw']}/20 | {values['semantic']}/20 |")
    lines.extend([
        "",
        "## Reliability and efficiency",
        "",
        "| metric | BASE | RAW | HML |",
        "|---|---:|---:|---:|",
        "| rejection rate | " + " | ".join(percent(arms[arm]["rejection_rate"]) for arm in ARMS) + " |",
        "| recovery after rejection | " + " | ".join(percent(arms[arm]["recovery_after_rejection"]) for arm in ARMS) + " |",
        "| total tokens / solved theorem | " + " | ".join(number(arms[arm]["tokens_per_solved_theorem"]) for arm in ARMS) + " |",
        "| accepted actions / solved theorem | " + " | ".join(number(arms[arm]["accepted_actions_per_solved_theorem"]) for arm in ARMS) + " |",
        "| generated actions / solved theorem | " + " | ".join(number(arms[arm]["generated_actions_per_solved_theorem"]) for arm in ARMS) + " |",
        "",
        f"TOTAL PILOT WALL TIME: {runtime['wall_seconds']:.2f}s",
        "",
        "GPU UTILIZATION / BOTTLENECK SUMMARY: see external `gpu.log`; sequential persistent Lean episodes and autoregressive decoding were the execution path.",
        "",
        "DOES HML ADVANTAGE INCREASE WITH ACTUAL HORIZON: " + ("YES" if summary["hml_advantage_increases_with_horizon"] else "NO"),
        "",
        "DOES HML SOLVE MATERIALLY MORE COMPLETE THEOREMS: " + ("YES" if summary["hml_materially_more_complete_theorems"] else "NO"),
        "",
        "NEXT SCIENTIFIC ACTION: " + ("PREREGISTER_CONFIRMATORY_CLOSED_LOOP_TEST" if summary["verdict"] in {"CLOSED_LOOP_SIGNAL_FOUND", "PILOT_POSITIVE_NEEDS_CONFIRMATION"} else "STOP"),
        "",
        "FINAL_B: SEALED / UNOPENED",
        "",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("all", "convert"))
    args = parser.parse_args()
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise SystemExit("A100 CUDA BF16 is required")
    conversion = convert_adapters()
    if conversion["result"] != "PASS" or args.command == "convert":
        print(canonical(conversion))
        return
    model, tokenizer = load_resident_model()
    parity = parity_gate(model, tokenizer)
    if parity["result"] != "PASS":
        write_json(MANIFEST, {
            "verdict": "GPU_PORTABILITY_FAILED",
            "hardware": hardware_manifest(),
            "conversion": conversion,
            "parity": parity,
            "final_b": "SEALED_NOT_OPENED",
        })
        raise SystemExit("GPU_PORTABILITY_FAILED")
    runtime = run_pilot(model, tokenizer)
    summary = analyse(conversion, parity, runtime)
    print(canonical(summary))


if __name__ == "__main__":
    main()
