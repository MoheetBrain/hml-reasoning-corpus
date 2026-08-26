#!/usr/bin/env python3
"""Train matched generative adapters and run LeanDojo beam search on the A100 VM."""

from __future__ import annotations

import argparse
import collections
import hashlib
import heapq
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from lean_dojo import Dojo, LeanError, LeanGitRepo, ProofFinished, ProofGivenUp, TacticState, Theorem
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from representation import canonical, digest, prompt  # noqa: E402


MODEL_ID = "Qwen/Qwen3-8B"
MODEL_REV = "b968826d9c46dd6066d109eabc6255188de91218"
MODEL_PATH = Path(os.environ.get("HML_MODEL_PATH", "/home/moheet/hmlpilot/model"))
RUNTIME = Path(os.environ.get("LOSSLESS_HML_RUNTIME", "/home/moheet/lossless_hml_runtime"))
DATA = RUNTIME / "data"
CHECKPOINTS = RUNTIME / "checkpoints"
LOGS = RUNTIME / "logs"
URL = "https://github.com/leanprover-community/mathlib4"
COMMIT = "29dcec074de168ac2bf835a77ef68bbe069194c5"
ARMS = ("raw", "lossless_hml")
TRAIN_N = 10_000
GRAD_ACCUM = 2
MAX_NEW_TOKENS = 96
MODEL_CONTEXT = 40_960
BOOTSTRAPS = 10_000
BOOTSTRAP_SEED = 20_260_826


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def command(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as error:
        return f"UNAVAILABLE:{error}"


def load_base() -> tuple[Any, Any]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.bfloat16,
        device_map={"": 0},
        attn_implementation="sdpa",
        local_files_only=True,
        trust_remote_code=False,
    )
    return model, tokenizer


def lora_config() -> LoraConfig:
    return LoraConfig(
        task_type="CAUSAL_LM",
        inference_mode=False,
        r=4,
        lora_alpha=8,
        lora_dropout=0.0,
        target_modules=["q_proj", "o_proj"],
        layers_to_transform=list(range(28, 36)),
        layers_pattern="layers",
        bias="none",
        use_rslora=False,
    )


def tokenize_training(tokenizer: Any, row: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor]:
    user = [{"role": "user", "content": row["prompt"]}]
    prompt_ids = tokenizer.apply_chat_template(
        user, add_generation_prompt=True, tokenize=True, enable_thinking=False, return_dict=False,
    )
    full_ids = tokenizer.apply_chat_template(
        user + [{"role": "assistant", "content": row["completion"]}],
        tokenize=True, enable_thinking=False, return_dict=False,
    )
    if len(full_ids) != row["full_tokens"] or len(prompt_ids) != row["prompt_tokens"]:
        raise AssertionError((row["record_id"], len(full_ids), row["full_tokens"]))
    labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
    return torch.tensor([full_ids], device="cuda"), torch.tensor([labels], device="cuda")


def train(arm: str) -> dict[str, Any]:
    if arm not in ARMS:
        raise ValueError(arm)
    random.seed(1)
    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed_all(1)
    torch.use_deterministic_algorithms(False)
    dataset_path = DATA / f"{arm}_train.jsonl"
    rows = [json.loads(line) for line in dataset_path.read_text().splitlines() if line.strip()]
    if len(rows) != TRAIN_N:
        raise AssertionError(len(rows))
    base, tokenizer = load_base()
    base.config.use_cache = False
    model = get_peft_model(base, lora_config())
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model.train()
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.Adam(trainable, lr=1e-4)
    optimizer.zero_grad(set_to_none=True)
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    telemetry_path = LOGS / f"{arm}_train_telemetry.jsonl"
    losses: list[float] = []
    tokens = 0
    started = time.monotonic()
    with telemetry_path.open("w", encoding="utf-8") as telemetry:
        for index, row in enumerate(rows, 1):
            input_ids, labels = tokenize_training(tokenizer, row)
            attention_mask = torch.ones_like(input_ids)
            output = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels, use_cache=False)
            loss = output.loss
            (loss / GRAD_ACCUM).backward()
            losses.append(float(loss.detach().cpu()))
            tokens += int(input_ids.numel())
            if index % GRAD_ACCUM == 0:
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
            if index == 1 or index % 100 == 0:
                elapsed = time.monotonic() - started
                event = {
                    "microstep": index,
                    "optimizer_updates": index // GRAD_ACCUM,
                    "loss": losses[-1],
                    "mean_recent_loss": statistics.fmean(losses[-100:]),
                    "tokens": tokens,
                    "tokens_per_second": tokens / elapsed,
                    "elapsed_seconds": elapsed,
                    "gpu_peak_gib": torch.cuda.max_memory_allocated() / 2**30,
                }
                telemetry.write(canonical(event) + "\n")
                telemetry.flush()
            del input_ids, labels, attention_mask, output, loss
    if TRAIN_N % GRAD_ACCUM:
        optimizer.step()
    output_dir = CHECKPOINTS / arm
    model.save_pretrained(output_dir, safe_serialization=True)
    wall = time.monotonic() - started
    result = {
        "result": "PASS",
        "arm": arm,
        "rows": len(rows),
        "epochs": 1,
        "microbatch": 1,
        "gradient_accumulation": GRAD_ACCUM,
        "optimizer_updates": len(rows) // GRAD_ACCUM,
        "learning_rate": 1e-4,
        "first_loss": losses[0],
        "final_loss": losses[-1],
        "mean_final_100_loss": statistics.fmean(losses[-100:]),
        "tokens": tokens,
        "wall_seconds": wall,
        "tokens_per_second": tokens / wall,
        "dataset_sha256": sha(dataset_path),
        "adapter_sha256": sha(output_dir / "adapter_model.safetensors"),
        "telemetry_sha256": sha(telemetry_path),
        "model_revision": MODEL_REV,
    }
    write_json(RUNTIME / f"{arm}_train_result.json", result)
    return result


def preflight_theorems(kind: str) -> dict[str, Any]:
    if kind not in ("dev", "eval"):
        raise ValueError(kind)
    candidates = json.loads((DATA / "theorem_candidates.json").read_text())[kind]
    if kind == "dev":
        targets = {"2-5": 24, "6-10": 16, "11-20": 8}
        excluded: set[str] = set()
        output = HERE / "DEV_THEOREMS.json"
    else:
        targets = {"2-5": 40, "6-10": 35, "11-20": 25}
        excluded = {item["theorem_id"] for item in json.loads((HERE / "DEV_THEOREMS.json").read_text())["theorems"]}
        output = HERE / "EVAL_THEOREMS.json"
    repo = LeanGitRepo(URL, COMMIT)
    selected: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for bucket in ("2-5", "6-10", "11-20"):
        count = 0
        for item in candidates[bucket]:
            if item["theorem_id"] in excluded:
                continue
            entry = Theorem(repo, Path(item["file_path"]), item["full_name"])
            context: Dojo | None = None
            try:
                context = Dojo(entry, hard_timeout=180)
                _, state = context.__enter__()
                if not isinstance(state, TacticState):
                    raise TypeError(type(state).__name__)
                frozen = {key: value for key, value in item.items() if key != "selection_key"}
                frozen["live_initial_state_sha256"] = digest(state.pp)
                selected.append(frozen)
                excluded.add(item["theorem_id"])
                count += 1
            except Exception as error:
                failures.append({
                    "theorem_id": item["theorem_id"],
                    "error": f"{type(error).__name__}:{str(error)[:500]}",
                })
            finally:
                if context is not None:
                    try:
                        context.__exit__(None, None, None)
                    except Exception:
                        pass
            if count == targets[bucket]:
                break
        if count != targets[bucket]:
            raise AssertionError((bucket, count, targets[bucket]))
    payload = {
        "schema_version": f"lossless-hml-{kind}-theorems-v1",
        "selection_policy": "hash order followed by model-blind LeanDojo initialization compatibility",
        "mathlib_commit": COMMIT,
        "counts": {"total": sum(targets.values()), **targets},
        "compatibility_failures_before_freeze": failures,
        "source_actions_included": False,
        "theorems": selected,
    }
    write_json(output, payload)
    return payload


def load_inference(arms: tuple[str, ...]) -> tuple[Any, Any]:
    base, tokenizer = load_base()
    model = PeftModel.from_pretrained(base, CHECKPOINTS / arms[0], adapter_name=arms[0], is_trainable=False)
    for arm in arms[1:]:
        model.load_adapter(CHECKPOINTS / arm, adapter_name=arm, is_trainable=False)
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    return model, tokenizer


@torch.inference_mode()
def propose(model: Any, tokenizer: Any, arm: str, state: str, history: list[dict[str, str]], k: int) -> dict[str, Any]:
    user_prompt = prompt(arm, state, history)
    chat = tokenizer.apply_chat_template(
        [{"role": "user", "content": user_prompt}],
        add_generation_prompt=True,
        tokenize=False,
        enable_thinking=False,
    )
    encoded = tokenizer(chat, return_tensors="pt")
    prompt_tokens = int(encoded.input_ids.shape[1])
    if prompt_tokens + MAX_NEW_TOKENS > MODEL_CONTEXT:
        return {"error": "MODEL_CONTEXT_EXCEEDED", "prompt_tokens": prompt_tokens, "candidates": []}
    output = model.generate(
        input_ids=encoded.input_ids.cuda(),
        attention_mask=encoded.attention_mask.cuda(),
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False,
        num_beams=k,
        num_return_sequences=k,
        early_stopping=True,
        return_dict_in_generate=True,
        output_scores=True,
        use_cache=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    prefix = encoded.input_ids.shape[1]
    candidates = []
    seen = set()
    for index, sequence in enumerate(output.sequences):
        tactic = tokenizer.decode(sequence[prefix:], skip_special_tokens=True).strip()
        if tactic in seen:
            continue
        seen.add(tactic)
        candidates.append({
            "tactic": tactic,
            "score": float(output.sequences_scores[index].cpu()),
            "generated_tokens": int(sequence.shape[0] - prefix),
        })
    return {"error": None, "prompt_tokens": prompt_tokens, "candidates": candidates}


def solve_theorem(
    model: Any,
    tokenizer: Any,
    arm: str,
    theorem: dict[str, Any],
    config: dict[str, int],
) -> dict[str, Any]:
    started = time.monotonic()
    repo = LeanGitRepo(URL, COMMIT)
    entry = Theorem(repo, Path(theorem["file_path"]), theorem["full_name"])
    context: Dojo | None = None
    expansions = model_calls = prompt_tokens = generated_tokens = 0
    rejected = accepted_successors = dead_ends = recoveries = rejection_nodes = backtracks = 0
    solved = False
    accepted_actions: int | None = None
    failure_reason: str | None = None
    attempts: list[dict[str, Any]] = []
    try:
        context = Dojo(entry, hard_timeout=3600)
        dojo, initial = context.__enter__()
        if not isinstance(initial, TacticState):
            raise TypeError(type(initial).__name__)
        # Heap entries are (-score, serial, state, state text, exact path history, depth).
        serial = 0
        frontier: list[tuple[float, int, Any, str, list[dict[str, str]], int]] = [
            (0.0, serial, initial, initial.pp, [], 0)
        ]
        seen = {digest(initial.pp)}
        maximum_depth_seen = 0
        while frontier and expansions < config["max_expansions"]:
            neg_score, _, state, state_text, history, depth = heapq.heappop(frontier)
            if depth < maximum_depth_seen:
                backtracks += 1
            if depth >= config["max_depth"]:
                dead_ends += 1
                continue
            result = propose(model, tokenizer, arm, state_text, history, config["candidate_generations"])
            expansions += 1
            model_calls += 1
            prompt_tokens += result["prompt_tokens"]
            if result["error"]:
                dead_ends += 1
                failure_reason = result["error"]
                continue
            valid_here = 0
            rejected_here = 0
            for candidate in result["candidates"]:
                tactic = candidate["tactic"]
                generated_tokens += candidate["generated_tokens"]
                if not tactic:
                    outcome: Any = LeanError("EMPTY_MODEL_OUTPUT")
                else:
                    outcome = dojo.run_tac(state, tactic)
                event = {
                    "state_sha256": digest(state_text),
                    "depth": depth,
                    "tactic": tactic,
                    "model_score": candidate["score"],
                }
                if isinstance(outcome, ProofFinished):
                    accepted_successors += 1
                    valid_here += 1
                    event.update({"accepted": True, "proof_finished": True})
                    attempts.append(event)
                    solved = True
                    accepted_actions = depth + 1
                    break
                if isinstance(outcome, TacticState):
                    accepted_successors += 1
                    valid_here += 1
                    event.update({"accepted": True, "next_state_sha256": digest(outcome.pp)})
                    attempts.append(event)
                    state_id = digest(outcome.pp)
                    if state_id not in seen:
                        seen.add(state_id)
                        serial += 1
                        new_history = history + [{
                            "state_before": state_text,
                            "action": tactic,
                            "state_after": outcome.pp,
                        }]
                        score = -neg_score + candidate["score"]
                        heapq.heappush(frontier, (-score, serial, outcome, outcome.pp, new_history, depth + 1))
                        maximum_depth_seen = max(maximum_depth_seen, depth + 1)
                else:
                    rejected += 1
                    rejected_here += 1
                    error = outcome.error if isinstance(outcome, LeanError) else type(outcome).__name__
                    event.update({"accepted": False, "error": str(error)[:2000]})
                    attempts.append(event)
            if solved:
                break
            if rejected_here:
                rejection_nodes += 1
                if valid_here:
                    recoveries += 1
            if valid_here == 0:
                dead_ends += 1
            if len(frontier) > config["search_width"]:
                frontier = heapq.nsmallest(config["search_width"], frontier)
                heapq.heapify(frontier)
        if not solved and failure_reason is None:
            failure_reason = "FRONTIER_EXHAUSTED" if not frontier else "MAX_EXPANSIONS"
    except Exception as error:
        failure_reason = f"EPISODE_EXCEPTION:{type(error).__name__}:{str(error)[:1000]}"
    finally:
        if context is not None:
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass
    total_tactics = rejected + accepted_successors
    return {
        "arm": arm,
        "theorem_id": theorem["theorem_id"],
        "source_proof_length": theorem["source_proof_length"],
        "source_length_bin": theorem["source_length_bin"],
        "solved": solved,
        "kernel_verified": solved,
        "accepted_actions": accepted_actions,
        "search_expansions": expansions,
        "model_calls": model_calls,
        "prompt_tokens": prompt_tokens,
        "generated_tokens": generated_tokens,
        "total_tokens": prompt_tokens + generated_tokens,
        "tactics_verified": total_tactics,
        "accepted_successors": accepted_successors,
        "successful_successors_per_expanded_state": accepted_successors / expansions if expansions else None,
        "rejected_tactics": rejected,
        "rejection_rate": rejected / total_tactics if total_tactics else None,
        "rejection_nodes": rejection_nodes,
        "recovered_rejection_nodes": recoveries,
        "recovery_rate": recoveries / rejection_nodes if rejection_nodes else None,
        "dead_ends": dead_ends,
        "dead_end_rate": dead_ends / expansions if expansions else None,
        "backtracks": backtracks,
        "wall_seconds": time.monotonic() - started,
        "failure_reason": None if solved else failure_reason,
        "attempts": attempts,
    }


def run_set(kind: str, arms: tuple[str, ...], config: dict[str, int], output: Path) -> dict[str, Any]:
    theorem_file = HERE / ("DEV_THEOREMS.json" if kind == "dev" else "EVAL_THEOREMS.json")
    theorems = json.loads(theorem_file.read_text())["theorems"]
    model, tokenizer = load_inference(arms)
    started = time.monotonic()
    with output.open("w", encoding="utf-8") as handle:
        for arm in arms:
            model.set_adapter(arm)
            for theorem in theorems:
                episode = solve_theorem(model, tokenizer, arm, theorem, config)
                handle.write(canonical(episode) + "\n")
                handle.flush()
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    result = {
        "kind": kind,
        "config": config,
        "arms": {
            arm: {
                "theorems": sum(row["arm"] == arm for row in rows),
                "solved": sum(row["arm"] == arm and row["solved"] for row in rows),
            }
            for arm in arms
        },
        "wall_seconds": time.monotonic() - started,
        "episodes_sha256": sha(output),
    }
    return result


def calibrate(config: dict[str, int]) -> dict[str, Any]:
    output = RUNTIME / f"calibration_exp{config['max_expansions']}.jsonl"
    result = run_set("dev", ("raw",), config, output)
    rate = result["arms"]["raw"]["solved"] / result["arms"]["raw"]["theorems"]
    result["raw_solve_rate"] = rate
    result["episodes_path"] = str(output)
    write_json(RUNTIME / f"calibration_exp{config['max_expansions']}_result.json", result)
    return result


def bootstrap_delta(raw: list[bool], hml: list[bool]) -> list[float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    data = np.asarray(hml, dtype=float) - np.asarray(raw, dtype=float)
    n = len(data)
    draws = np.empty(BOOTSTRAPS)
    for index in range(BOOTSTRAPS):
        draws[index] = data[rng.integers(0, n, n)].mean()
    return [float(value) for value in np.percentile(draws, (2.5, 97.5))]


def summarize_evaluation(config: dict[str, int]) -> dict[str, Any]:
    rows = [json.loads(line) for line in (HERE / "episodes.jsonl").read_text().splitlines() if line.strip()]
    by_arm = {arm: [row for row in rows if row["arm"] == arm] for arm in ARMS}
    ids = [row["theorem_id"] for row in by_arm["raw"]]
    maps = {arm: {row["theorem_id"]: row for row in by_arm[arm]} for arm in ARMS}
    n = len(ids)
    raw_solved = [maps["raw"][theorem]["solved"] for theorem in ids]
    hml_solved = [maps["lossless_hml"][theorem]["solved"] for theorem in ids]
    summary: dict[str, Any] = {"n": n, "arms": {}, "horizons": {}, "expansion_horizons": {}}
    for arm, arm_rows in by_arm.items():
        solved = sum(row["solved"] for row in arm_rows)
        total_tactics = sum(row["tactics_verified"] for row in arm_rows)
        rejection_nodes = sum(row["rejection_nodes"] for row in arm_rows)
        summary["arms"][arm] = {
            "solved": solved,
            "solve_rate": solved / n,
            "rejection_rate": sum(row["rejected_tactics"] for row in arm_rows) / total_tactics if total_tactics else None,
            "recovery_rate": sum(row["recovered_rejection_nodes"] for row in arm_rows) / rejection_nodes if rejection_nodes else None,
            "successful_successors_per_expanded_state": sum(row["accepted_successors"] for row in arm_rows) / sum(row["search_expansions"] for row in arm_rows),
            "dead_end_rate": sum(row["dead_ends"] for row in arm_rows) / sum(row["search_expansions"] for row in arm_rows),
            "backtracks": sum(row["backtracks"] for row in arm_rows),
            "search_expansions_per_solved": sum(row["search_expansions"] for row in arm_rows) / solved if solved else None,
            "accepted_actions_per_solved": sum((row["accepted_actions"] or 0) for row in arm_rows if row["solved"]) / solved if solved else None,
            "model_calls_per_solved": sum(row["model_calls"] for row in arm_rows) / solved if solved else None,
            "tokens_per_solved": sum(row["total_tokens"] for row in arm_rows) / solved if solved else None,
            "wall_seconds_per_solved": sum(row["wall_seconds"] for row in arm_rows) / solved if solved else None,
            "mean_input_tokens": statistics.fmean(row["prompt_tokens"] / row["model_calls"] for row in arm_rows if row["model_calls"]),
            "p95_input_tokens": float(np.percentile([row["prompt_tokens"] / row["model_calls"] for row in arm_rows if row["model_calls"]], 95)),
            "max_mean_episode_input_tokens": max(row["prompt_tokens"] / row["model_calls"] for row in arm_rows if row["model_calls"]),
        }
    for horizon in (5, 10, 20, 40):
        summary["horizons"][str(horizon)] = {
            arm: sum(row["solved"] and row["accepted_actions"] <= horizon for row in by_arm[arm])
            for arm in ARMS
        }
    for horizon in (10, 25, 50, 100):
        summary["expansion_horizons"][str(horizon)] = {
            arm: sum(row["solved"] and row["search_expansions"] <= horizon for row in by_arm[arm])
            for arm in ARMS
        }
    raw_rate = summary["arms"]["raw"]["solve_rate"]
    hml_rate = summary["arms"]["lossless_hml"]["solve_rate"]
    delta = hml_rate - raw_rate
    ci = bootstrap_delta(raw_solved, hml_solved)
    token_ratio = summary["arms"]["lossless_hml"]["mean_input_tokens"] / summary["arms"]["raw"]["mean_input_tokens"]
    horizon_deltas = [
        (summary["horizons"][str(h)]["lossless_hml"] - summary["horizons"][str(h)]["raw"]) / n
        for h in (5, 10, 20, 40)
    ]
    increasing = horizon_deltas[-1] >= 0.05 and horizon_deltas[-1] > horizon_deltas[0]
    efficiency = False
    for metric in ("search_expansions_per_solved", "model_calls_per_solved", "tokens_per_solved", "wall_seconds_per_solved"):
        raw_value = summary["arms"]["raw"][metric]
        hml_value = summary["arms"]["lossless_hml"][metric]
        if raw_value and hml_value is not None and hml_value <= 0.8 * raw_value:
            efficiency = True
    if delta <= 0:
        verdict = "HANDCRAFTED_HML_REPRESENTATION_RESEARCH_TERMINATED"
    elif delta >= 0.10 and ci[0] > 0:
        verdict = "LOSSLESS_HML_SIGNAL_FOUND"
    elif delta >= 0.05 or efficiency or increasing:
        verdict = "LOSSLESS_HML_POSITIVE_NEEDS_CONFIRMATION"
    else:
        verdict = "HANDCRAFTED_HML_REPRESENTATION_RESEARCH_TERMINATED"
    summary.update({
        "delta": delta,
        "paired_ci95": ci,
        "token_ratio": token_ratio,
        "advantage_grows_with_horizon": increasing,
        "efficiency_improvement_ge20": efficiency,
        "verdict": verdict,
        "solver_config": config,
    })
    return summary


def report(summary: dict[str, Any], calibration: dict[str, Any]) -> None:
    training = {arm: json.loads((RUNTIME / f"{arm}_train_result.json").read_text()) for arm in ARMS}
    manifest = {
        "schema_version": "lossless-hml-final-run-v1",
        "hardware": {
            "hostname": platform.node(), "cpu_count": os.cpu_count(),
            "gpu": command(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
            "cuda": torch.version.cuda, "pytorch": torch.__version__,
        },
        "model": {"id": MODEL_ID, "revision": MODEL_REV, "dtype": "bfloat16", "quantization": None},
        "lean": {
            "mathlib_commit": COMMIT,
            "toolchain": "leanprover/lean4:v4.10.0-rc1",
            "lean_dojo": "2.0.0",
        },
        "training": training,
        "calibration": calibration,
        "summary": summary,
        "artifacts": {
            "episodes_sha256": sha(HERE / "episodes.jsonl"),
            "eval_theorems_sha256": sha(HERE / "EVAL_THEOREMS.json"),
            "protocol_sha256": sha(HERE / "PROTOCOL.md"),
        },
        "final_b": "SEALED_NOT_OPENED",
    }
    write_json(HERE / "RUN_MANIFEST.json", manifest)
    arms = summary["arms"]
    n = summary["n"]
    lines = [
        f"# FINAL VERDICT: {summary['verdict']}", "",
        f"RAW development solve rate after calibration: {calibration['arms']['raw']['solved']}/{calibration['arms']['raw']['theorems']} = {calibration['raw_solve_rate']:.2%}", "",
        "## Calibrated solver", "",
        f"- Search width: {summary['solver_config']['search_width']}",
        f"- Candidate generations/state: {summary['solver_config']['candidate_generations']}",
        f"- Max expansions: {summary['solver_config']['max_expansions']}",
        f"- Max depth: {summary['solver_config']['max_depth']}", "",
        f"RAW 10K training: complete in {training['raw']['wall_seconds']:.2f}s",
        f"LOSSLESS_HML 10K training: complete in {training['lossless_hml']['wall_seconds']:.2f}s", "",
        f"Evaluation theorems: {n}",
        f"RAW solved: {arms['raw']['solved']}/{n} = {arms['raw']['solve_rate']:.2%}",
        f"LOSSLESS_HML solved: {arms['lossless_hml']['solved']}/{n} = {arms['lossless_hml']['solve_rate']:.2%}",
        f"Delta: {summary['delta']*100:+.2f}pp",
        f"95% paired CI: [{summary['paired_ci95'][0]*100:+.2f}, {summary['paired_ci95'][1]*100:+.2f}]pp", "",
        "## Horizon", "",
        "| accepted actions | RAW | LOSSLESS_HML |", "|---:|---:|---:|",
    ]
    for horizon in (5, 10, 20, 40):
        values = summary["horizons"][str(horizon)]
        lines.append(f"| <={horizon} | {values['raw']}/{n} | {values['lossless_hml']}/{n} |")
    lines.extend(["", "## Reliability and economics", "", "| metric | RAW | LOSSLESS_HML |", "|---|---:|---:|"])
    for label, metric in (
        ("Rejection rate", "rejection_rate"), ("Recovery rate", "recovery_rate"),
        ("Expansions / solved", "search_expansions_per_solved"), ("Tokens / solved", "tokens_per_solved"),
        ("Mean input tokens", "mean_input_tokens"), ("p95 input tokens", "p95_input_tokens"),
    ):
        values = [arms[arm][metric] for arm in ARMS]
        rendered = ["N/A" if value is None else f"{value:.4f}" for value in values]
        lines.append(f"| {label} | {rendered[0]} | {rendered[1]} |")
    lines.extend([
        "", f"Input-token ratio LOSSLESS_HML/RAW: {summary['token_ratio']:.4f}",
        f"Advantage grows with horizon: {'YES' if summary['advantage_grows_with_horizon'] else 'NO'}",
        f"Lossless HML materially beats RAW: {'YES' if summary['delta'] >= .05 else 'NO'}", "",
        "FINAL_B: SEALED / UNOPENED", "",
    ])
    (HERE / "REPORT.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    train_parser = sub.add_parser("train"); train_parser.add_argument("--arm", choices=ARMS, required=True)
    preflight_parser = sub.add_parser("preflight"); preflight_parser.add_argument("--kind", choices=("dev", "eval"), required=True)
    calibrate_parser = sub.add_parser("calibrate"); calibrate_parser.add_argument("--max-expansions", type=int, required=True)
    evaluate_parser = sub.add_parser("evaluate"); evaluate_parser.add_argument("--max-expansions", type=int, required=True)
    report_parser = sub.add_parser("report"); report_parser.add_argument("--max-expansions", type=int, required=True); report_parser.add_argument("--calibration-result", required=True)
    args = parser.parse_args()
    if args.command == "train":
        print(canonical(train(args.arm)))
    elif args.command == "preflight":
        print(canonical(preflight_theorems(args.kind)))
    elif args.command == "calibrate":
        config = {"search_width": 4, "candidate_generations": 4, "max_expansions": args.max_expansions, "max_depth": 40}
        print(canonical(calibrate(config)))
    elif args.command == "evaluate":
        config = {"search_width": 4, "candidate_generations": 4, "max_expansions": args.max_expansions, "max_depth": 40}
        result = run_set("eval", ARMS, config, HERE / "episodes.jsonl")
        write_json(RUNTIME / "evaluation_runtime.json", result)
        print(canonical(result))
    else:
        config = {"search_width": 4, "candidate_generations": 4, "max_expansions": args.max_expansions, "max_depth": 40}
        summary = summarize_evaluation(config)
        calibration = json.loads(Path(args.calibration_result).read_text())
        report(summary, calibration)
        print(canonical(summary))


if __name__ == "__main__":
    main()
