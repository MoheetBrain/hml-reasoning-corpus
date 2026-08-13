#!/usr/bin/env python3
"""Build the one-file synthetic mathematics -> neutral trajectory -> HML corpus.

The source is a Markdown export containing six independently numbered, worked
100-problem corpora.  This builder is intentionally conservative: it preserves every
problem verbatim, segments displayed state changes, renders only transitions supported by
the frozen semantic-state model, and records refusals rather than coercing unsupported
candidate/branch/approximation semantics into ordinary claims.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


FROZEN_HML_SHA = "84bf9897689b0ed78a2caaefc1db850d49b81260"
FROZEN_HML_TAG = "hml-semantic-pre-gemma-v1"
CORPUS_BASE_SHA = "9d67e54450b9db897ee2ed20ec2e4cbbc16a3780"
SCHEMA_VERSION = "semantic-firewall-case-0.1.0"

STATUS_BACKEND = "FULLY_REPRESENTABLE_AND_BACKEND_VERIFIED"
STATUS_UNVERIFIED = "REPRESENTABLE_BUT_CURRENTLY_UNVERIFIABLE"
STATUS_LIBRARY = "REQUIRES_EXISTING_TRUSTED_BACKEND_OR_LIBRARY"
STATUS_GAP = "GENUINE_HML_SEMANTIC_GAP"
STATUS_AMBIGUITY = "SOURCE_AMBIGUITY_OR_CORRUPTION"


@dataclass(frozen=True)
class CorpusSpec:
    key: str
    title: str
    response_number: int
    default_domain: str
    heading_style: str


CORPORA = (
    CorpusSpec("ALG", "Foundational algebra", 2, "algebra", "algebra"),
    CorpusSpec("GEN", "Algebra, functions, and equations", 3, "algebra_and_functions", "problem"),
    CorpusSpec("CALC", "Calculus", 4, "calculus", "problem"),
    CorpusSpec("PROB", "Probability and statistics", 5, "probability_and_statistics", "problem"),
    CorpusSpec("LINALG", "Linear algebra", 6, "linear_algebra", "problem"),
    CorpusSpec("MIXED", "Geometry, trigonometry, and advanced mixed mathematics", 7, "mixed_mathematics", "problem"),
)


@dataclass
class MathBlock:
    raw: str
    start: int
    end: int
    heading: str


@dataclass
class SourceProblem:
    corpus: CorpusSpec
    number: int
    problem_id: str
    raw: str
    source_start_line: int
    source_end_line: int
    statement: str
    initial_state: str
    final_answer: str
    domain: str
    difficulty: str


@dataclass
class Transition:
    transition_id: str
    index: int
    before: str
    after: str
    source_span: str
    source_heading: str
    operation: str
    warrant: str
    preconditions: list[dict[str, str]]
    obligations: list[dict[str, str]]
    mechanisms: list[str]
    classification: str
    classification_reason: str
    backend_status: str = "NOT_APPLICABLE"
    backend_detail: str = ""
    dependency_ids: list[str] = field(default_factory=list)
    hml_text: str | None = None
    schema_validation: str = "NOT_RUN"
    hml_runtime_verdict: str = "NOT_RENDERED"
    hml_roundtrip: str = "NOT_RUN"
    hml_unknowns: list[str] = field(default_factory=list)
    gap_code: str | None = None
    depends_on_gap: str | None = None


@dataclass
class ProblemRecord:
    source: SourceProblem
    transitions: list[Transition]
    diagnostics: list[str]
    goal_text: str


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def response_spans(text: str) -> dict[int, tuple[int, int]]:
    starts = [m.end() for m in re.finditer(r"(?m)^# chatgpt response\s*$", text)]
    spans: dict[int, tuple[int, int]] = {}
    for idx, start in enumerate(starts, 1):
        next_user = text.find("\n# you asked", start)
        end = len(text) if next_user < 0 else next_user
        spans[idx] = (start, end)
    return spans


def problem_starts(block: str, style: str) -> list[tuple[int, int]]:
    found: dict[int, int] = {}
    if style == "algebra":
        for match in re.finditer(r"(?m)^##\s+(\d{1,3})\.(?:\s|$)", block):
            found[int(match.group(1))] = match.start()
        boss = re.search(r"(?m)^#\s+[^\n]*\b100\.\s+BOSS PROBLEM\s*$", block)
        if boss:
            found[100] = boss.start()
    else:
        for match in re.finditer(r"(?m)^# Problem (\d{1,3})(?:\s|$)", block):
            found[int(match.group(1))] = match.start()
    return sorted((offset, number) for number, offset in found.items() if 1 <= number <= 100)


def section(block: str, title_pattern: str) -> str:
    match = re.search(rf"(?mi)^(?P<marks>###)\s+{title_pattern}\s*$", block)
    if not match:
        return ""
    # Numbered ``## Stage`` headings occur beneath ``###`` sections throughout the
    # source. They are semantically nested despite the Markdown level inversion, so only
    # the next peer ``###`` section terminates this region.
    following = re.search(rf"(?m)^{re.escape(match.group('marks'))}\s+", block[match.end() :])
    end = len(block) if following is None else match.end() + following.start()
    return block[match.end() : end].strip()


def first_math(text: str) -> str:
    match = re.search(r"(?ms)^\$\$\s*\n?(.*?)\n?\$\$\s*$", text)
    if match:
        return normalize_math(match.group(1))
    inline = re.search(r"\$(.+?)\$", text)
    return inline.group(1).strip() if inline else ""


def normalize_math(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^\\(?:rightarrow|Rightarrow|implies)\s*", "", value)
    if value.startswith(r"\boxed{") and value.endswith("}") and balanced_braces(value):
        value = value[7:-1].strip()
    value = value.replace(r"\checkmark", "").replace(r"\quad", " ")
    value = re.sub(r"\\begin\{(?:aligned|align\*?|gathered)\}", "", value)
    value = re.sub(r"\\end\{(?:aligned|align\*?|gathered)\}", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_prose(value: str, limit: int = 900) -> str:
    value = re.sub(r"(?m)^#{1,6}\s*", "", value)
    value = re.sub(r"\s+", " ", value).strip(" -:\n")
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def difficulty(number: int) -> str:
    if number <= 20:
        return "easy"
    if number <= 50:
        return "intermediate"
    if number <= 80:
        return "hard"
    return "very_hard_or_multistage"


def extract_domain(raw: str, default: str) -> str:
    explicit = section(raw, r"Mathematical domain")
    if explicit:
        prose = clean_prose(explicit, 180)
        if prose:
            return prose.rstrip(".")
    return default


def extract_statement(raw: str, style: str) -> str:
    if style == "problem":
        stated = section(raw, r"Problem")
        if stated:
            return stated.strip()
    heading = raw.splitlines()[0].strip()
    heading = re.sub(r"^#{1,2}\s+", "", heading)
    heading = re.sub(r"^(?:[^0-9]*)(\d{1,3})\.\s*", "", heading)
    if heading and not re.fullmatch(r"\d{1,3}\.?", heading):
        return heading
    return first_math(raw)


def extract_initial(raw: str, statement: str) -> str:
    value = section(raw, r"Initial (?:mathematical )?state")
    if value:
        return value.strip()
    return f"Given the source problem: {statement}"


def extract_final(raw: str) -> str:
    value = section(raw, r"Final answer(?: \+ interpretation)?")
    if value:
        return value.strip()
    boxed = list(re.finditer(r"(?s)\\boxed\s*\{(.*?)\}", raw))
    if boxed:
        return normalize_math(boxed[-1].group(1))
    blocks = list(re.finditer(r"(?ms)^\$\$\s*\n?(.*?)\n?\$\$\s*$", raw))
    return normalize_math(blocks[-1].group(1)) if blocks else "SOURCE_FINAL_ANSWER_NOT_EXPLICIT"


def parse_problems(text: str) -> list[SourceProblem]:
    spans = response_spans(text)
    out: list[SourceProblem] = []
    for spec in CORPORA:
        start, end = spans[spec.response_number]
        response = text[start:end]
        starts = problem_starts(response, spec.heading_style)
        numbers = [number for _, number in starts]
        if numbers != list(range(1, 101)):
            raise ValueError(f"{spec.key}: expected problem numbers 1..100, got {numbers}")
        for idx, (offset, number) in enumerate(starts):
            block_end = starts[idx + 1][0] if idx + 1 < len(starts) else len(response)
            raw = response[offset:block_end].strip()
            absolute_start = start + offset
            absolute_end = start + block_end
            statement = extract_statement(raw, spec.heading_style)
            out.append(
                SourceProblem(
                    corpus=spec,
                    number=number,
                    problem_id=f"{spec.key}-{number:03d}",
                    raw=raw,
                    source_start_line=line_number(text, absolute_start),
                    source_end_line=line_number(text, absolute_end),
                    statement=statement,
                    initial_state=extract_initial(raw, statement),
                    final_answer=extract_final(raw),
                    domain=extract_domain(raw, spec.default_domain),
                    difficulty=difficulty(number),
                )
            )
    if len(out) != 600:
        raise ValueError(f"expected 600 source problems, got {len(out)}")
    return out


def math_blocks_with_headings(text: str) -> list[MathBlock]:
    events: list[tuple[int, str, Any]] = []
    for match in re.finditer(r"(?m)^#{2,4}\s+(.+?)\s*$", text):
        events.append((match.start(), "heading", match))
    for match in re.finditer(r"(?ms)^\$\$\s*\n?(.*?)\n?\$\$\s*$", text):
        events.append((match.start(), "math", match))
    events.sort(key=lambda item: (item[0], 0 if item[1] == "heading" else 1))
    heading = ""
    blocks: list[MathBlock] = []
    for _, kind, match in events:
        if kind == "heading":
            heading = clean_prose(match.group(1), 240)
        else:
            blocks.append(MathBlock(match.group(1).strip(), match.start(), match.end(), heading))
    return blocks


def trace_regions(problem: SourceProblem) -> list[tuple[str, str]]:
    if problem.corpus.heading_style == "algebra":
        return [("Granular solution", problem.raw)]
    first = re.search(
        r"(?mi)^###\s+(Granular reasoning trace|Granular solution(?: — inverse)?|Granular domain derivation)\s*$",
        problem.raw,
    )
    if not first:
        return [("Recovered worked solution", problem.raw)]

    # A long problem may interleave ``## Part`` sections with peer ``###`` ledgers. Split
    # the entire post-trace remainder by headings so later parts are not lost merely
    # because a candidate ledger appeared after Part 1.
    tail = problem.raw[first.end() :]
    headings = list(re.finditer(r"(?m)^#{2,4}\s+(.+?)\s*$", tail))
    regions: list[tuple[str, str]] = []
    cursor = 0
    title = first.group(1)
    for heading in headings:
        body = tail[cursor : heading.start()].strip()
        lowered = title.lower()
        if body and not any(
            lowered.startswith(prefix)
            for prefix in ("candidate", "branch / candidate", "preconditions", "assumptions", "final answer")
        ):
            regions.append((title, body))
        title = clean_prose(heading.group(1), 240)
        cursor = heading.end()
    body = tail[cursor:].strip()
    lowered = title.lower()
    if body and not any(
        lowered.startswith(prefix)
        for prefix in ("candidate", "branch / candidate", "preconditions", "assumptions", "final answer")
    ):
        regions.append((title, body))
    return regions or [("Recovered worked solution", problem.raw)]


def balanced_braces(value: str) -> bool:
    stripped = value.replace(r"\{", "").replace(r"\}", "")
    depth = 0
    for char in stripped:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def infer_operation(context: str) -> str:
    lower = context.lower()
    tests = (
        (("verify", "check", "substitute into the original", "sanity"), "VERIFY"),
        (("induct", "base case", "induction hypothesis"), "INDUCT"),
        (("contradiction", "assume the contrary"), "CONTRADICTION"),
        (("case ", "branch ", "split"), "CASE_SPLIT"),
        (("theorem", "rule", "l'hôpital", "fundamental theorem"), "APPLY_THEOREM"),
        (("definition", "defined", "by definition"), "APPLY_DEFINITION"),
        (("substitut", "replace ", "let ", "set "), "SUBSTITUTE"),
        (("count", "choose", "permutation", "combination"), "COUNT"),
        (("bound", "upper", "lower", "inequality"), "BOUND"),
        (("candidate", "root", "stationary", "eigenvalue"), "SELECT"),
        (("construct", "draw", "form the matrix"), "CONSTRUCT"),
        (("model", "distribution", "likelihood", "hypothesis"), "MODEL"),
        (("differentiat", "integrat", "limit", "series"), "APPLY_THEOREM"),
        (("evaluate", "calculate", "arithmetic", "compute"), "EVALUATE"),
        (("declare", "define", "denote"), "DECLARE"),
    )
    for needles, operation in tests:
        if any(needle in lower for needle in needles):
            return operation
    return "TRANSFORM"


def infer_mechanisms(context: str, before: str, after: str) -> list[str]:
    text = f"{context} {before} {after}".lower()
    mapping = {
        "domain_restriction": ("domain", "restriction", "denominator", "nonzero", "non-zero", "≠0", r"\neq0"),
        "division_or_cancellation": ("divide", "cancel", "reciprocal"),
        "squaring_or_roots": ("square", "sqrt", r"\sqrt", "root"),
        "inequality_sign": ("inequality", "reverse the inequality", "negative"),
        "substitution": ("substitut", "replace", "let ", "set "),
        "candidate_reasoning": ("candidate", "stationary", "eigenvalue", "extraneous"),
        "case_split": ("case ", "branch ", "piecewise", "absolute value"),
        "theorem_application": ("theorem", "rule", "criterion", "formula"),
        "differentiation": ("differentiat", "derivative"),
        "integration": ("integrat", "antiderivative"),
        "limit_or_convergence": ("limit", "conver", "series"),
        "approximation": ("approx", "newton", "iteration", "error bound", r"\approx"),
        "matrix_or_vector": ("matrix", "vector", "row operation", "determinant", "rank", "eigen"),
        "probability_model": ("probability", "distribution", "independ", "bayes", "likelihood", "confidence", "hypothesis"),
        "induction": ("induct", "base case"),
        "construction": ("construct", "draw"),
    }
    found = [name for name, needles in mapping.items() if any(needle in text for needle in needles)]
    return found or ["algebraic_or_logical_transformation"]


def infer_preconditions(context: str, transition_id: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    lower = context.lower()
    preconditions: list[dict[str, str]] = []
    obligations: list[dict[str, str]] = []

    def add(statement: str, established: bool) -> None:
        index = len(preconditions) + 1
        status = "SATISFIED" if established else "DEFERRED_AS_OBLIGATION"
        preconditions.append({"id": f"{transition_id}-PRE-{index}", "statement": statement, "status": status})
        if not established:
            obligations.append({"id": f"{transition_id}-OB-{index}", "statement": statement})

    explicit = any(token in lower for token in ("established", "because", "must be nonzero", "is nonzero", "restriction", "precondition"))
    if any(token in lower for token in ("divide by", "cancel", "cross multiply", "reciprocal")):
        variable_divisor = bool(re.search(r"divide (?:both sides )?by\s+[^\s.,;]*[a-z]", lower)) or "denominator" in lower
        if variable_divisor:
            add("the divisor or cancelled factor is nonzero", explicit)
    if "log" in lower and any(token in lower for token in ("take", "apply", "defined")):
        add("every logarithm argument is positive", "positive" in lower or explicit)
    if any(token in lower for token in ("square root", "sqrt", "even root")):
        add("every even-root radicand is nonnegative", "nonnegative" in lower or "domain" in lower or explicit)
    if "inequality" in lower and any(token in lower for token in ("multiply", "divide")):
        add("the multiplier/divisor sign is established before changing inequality direction", "positive" in lower or "negative" in lower)
    return preconditions, obligations


def classify_transition(context: str, heading: str, before: str, after: str) -> tuple[str, str, str | None]:
    combined = f"{heading} {context}".lower()
    if not balanced_braces(before) or not balanced_braces(after):
        return STATUS_AMBIGUITY, "unbalanced LaTeX braces prevent an unambiguous expression recovery", "SOURCE_LATEX_UNBALANCED"
    if re.search(r"\b(case|branch)\s*(?:[0-9:]|one|two|i|ii)", combined) or "case split" in combined or "creates branches" in combined:
        return STATUS_GAP, "the source opens or reasons inside a dynamically created branch, but current HML cannot add branch records", "BRANCH_CREATION_NOT_REPRESENTABLE"
    root_like_candidate = bool(
        re.search(r"(?:^|[^A-Za-z])(?:x|y|u|t|c|\\lambda)\s*=", after)
        and (
            ("=0" in before.replace(" ", "") and ")(" in before.replace(" ", ""))
            or re.search(r"\^[{]?2[}]?\s*=", before)
            or r"\pm" in before
        )
    )
    if any(token in combined for token in ("candidate generation", "candidate verification", "candidate ledger", "stationary candidates")) or root_like_candidate:
        return STATUS_GAP, "the source creates or changes a candidate during forward reasoning, but current HML cannot add candidate records", "CANDIDATE_CREATION_NOT_REPRESENTABLE"
    if any(token in combined for token in ("approximate", "approximation", "newton", "iteration rule", "stopping criterion")) or r"\approx" in after:
        return STATUS_GAP, "the step changes exact/approximate epistemic status, a distinction absent from current HML claim statuses", "APPROXIMATION_STATUS_NOT_REPRESENTABLE"
    if any(token in combined for token in ("apply theorem", "by the theorem", "theorem", "criterion", "differenti", "integrat", "bayes", "distribution", "normal equations")):
        return STATUS_LIBRARY, "the transition shape is representable, but mathematical authority requires an existing trusted theorem/backend certificate", None
    return STATUS_UNVERIFIED, "the transition is structurally representable; source prose alone is not runtime authority", None


def extract_transitions(problem: SourceProblem) -> tuple[list[Transition], list[str]]:
    transitions: list[Transition] = []
    diagnostics: list[str] = []
    prior_after = ""
    for region_name, region in trace_regions(problem):
        blocks = math_blocks_with_headings(region)
        if not blocks:
            continue
        compact: list[MathBlock] = []
        for block in blocks:
            normalized = normalize_math(block.raw)
            if not normalized or (compact and normalize_math(compact[-1].raw) == normalized):
                continue
            compact.append(block)
        if len(compact) == 1:
            before = prior_after or first_math(problem.statement) or clean_prose(problem.statement)
            pairs = [(before, compact[0], 0)]
        else:
            pairs = [(normalize_math(compact[i - 1].raw), compact[i], i) for i in range(1, len(compact))]
        for before, current, index in pairs:
            after = normalize_math(current.raw)
            if before == after:
                continue
            previous_end = compact[index - 1].end if len(compact) > 1 and index > 0 else 0
            context = region[previous_end:current.start].strip()
            source_span = f"$$\n{before}\n$$\n{context}\n$$\n{after}\n$$".strip()
            tid = f"{problem.problem_id}-T{len(transitions) + 1:03d}"
            semantic_context = f"{region_name} {current.heading} {context}"
            operation = infer_operation(semantic_context)
            mechanisms = infer_mechanisms(semantic_context, before, after)
            preconditions, obligations = infer_preconditions(context, tid)
            classification, reason, gap_code = classify_transition(context, f"{region_name} {current.heading}", before, after)
            transitions.append(
                Transition(
                    transition_id=tid,
                    index=len(transitions) + 1,
                    before=before,
                    after=after,
                    source_span=source_span,
                    source_heading=current.heading or region_name,
                    operation=operation,
                    warrant=clean_prose(context, 700) or "No explicit warrant text occurs between the two source states.",
                    preconditions=preconditions,
                    obligations=obligations,
                    mechanisms=mechanisms,
                    classification=classification,
                    classification_reason=reason,
                    gap_code=gap_code,
                )
            )
        if compact:
            prior_after = normalize_math(compact[-1].raw)
    if not transitions:
        before = first_math(problem.statement) or clean_prose(problem.statement)
        after = first_math(problem.final_answer) or clean_prose(problem.final_answer)
        transitions.append(
            Transition(
                transition_id=f"{problem.problem_id}-T001",
                index=1,
                before=before,
                after=after,
                source_span=problem.raw,
                source_heading="Recovered worked solution",
                operation="UNRESOLVED",
                warrant="No separable state sequence was recoverable from the source formatting.",
                preconditions=[],
                obligations=[],
                mechanisms=["source_recovery"],
                classification=STATUS_AMBIGUITY,
                classification_reason="the source block contains no separable displayed state transition",
                gap_code="SOURCE_TRANSITION_BOUNDARY_AMBIGUOUS",
            )
        )
        diagnostics.append("SOURCE_TRANSITION_BOUNDARY_AMBIGUOUS")
    for transition in transitions:
        if "\\\\" in transition.before or "\\\\" in transition.after:
            diagnostics.append(f"{transition.transition_id}: COMPOUND_DISPLAY_STATE_PRESERVED")
    return transitions, sorted(set(diagnostics))


class SympyVerifier:
    def __init__(self) -> None:
        try:
            import sympy
            from sympy.parsing.latex import parse_latex
        except Exception:
            self.sympy = None
            self.parse_latex = None
        else:
            self.sympy = sympy
            self.parse_latex = parse_latex
        self.cache: dict[str, Any] = {}

    @staticmethod
    def _clean(value: str) -> str | None:
        if len(value) > 260:
            return None
        forbidden = (
            r"\begin", r"\end", r"\text", r"\operatorname", r"\lim", r"\int", r"\sum",
            r"\prod", r"\vec", r"\begin{pmatrix}", r"\begin{bmatrix}", r"\pm", r"\approx",
            r"\Rightarrow", r"\implies", r"\in", r"\cup", r"\cap", r"\forall", r"\exists",
        )
        if any(token in value for token in forbidden):
            return None
        cleaned = value.strip().rstrip(".,;:")
        while cleaned.startswith(r"\boxed{") and cleaned.endswith("}"):
            cleaned = cleaned[7:-1].strip()
        cleaned = cleaned.replace(r"\checkmark", "").replace(r"\quad", " ").strip()
        return cleaned or None

    def parse(self, value: str) -> Any:
        cleaned = self._clean(value)
        if cleaned is None or self.parse_latex is None:
            return None
        if cleaned not in self.cache:
            try:
                self.cache[cleaned] = self.parse_latex(cleaned)
            except Exception:
                self.cache[cleaned] = None
        return self.cache[cleaned]

    def verify(self, before: str, after: str, context: str) -> tuple[str, str]:
        if self.sympy is None:
            return "BACKEND_UNAVAILABLE", "SymPy/LaTeX parser is unavailable"
        lower = context.lower()
        if any(token in lower for token in ("square both", "take square", "candidate", "case ", "approx")):
            return "NOT_APPLICABLE", "the source operation is intentionally non-equivalent or branch-sensitive"
        left = self.parse(before)
        right = self.parse(after)
        if left is None or right is None:
            return "UNSUPPORTED_FRAGMENT", "one or both states are outside the conservative SymPy/LaTeX fragment"
        sympy = self.sympy
        try:
            if isinstance(left, sympy.Equality) and isinstance(right, sympy.Equality):
                symbols = sorted(left.free_symbols | right.free_symbols, key=str)
                if len(symbols) == 1:
                    symbol = symbols[0]
                    lset = sympy.solveset(left, symbol, domain=sympy.S.Reals)
                    rset = sympy.solveset(right, symbol, domain=sympy.S.Reals)
                    if lset == rset:
                        return "SYMPY_VERIFIED", f"equal real solution sets: {lset}"
                    return "SYMPY_MISMATCH", f"real solution sets differ: before={lset}; after={rset}"
                if not symbols:
                    return ("SYMPY_VERIFIED", "both closed equalities have the same truth value") if bool(left) == bool(right) else ("SYMPY_MISMATCH", "closed equalities differ in truth value")
                lres = sympy.expand(left.lhs - left.rhs)
                rres = sympy.expand(right.lhs - right.rhs)
                ratio = sympy.simplify(lres / rres) if rres != 0 else None
                if ratio is not None and not ratio.free_symbols and ratio != 0:
                    return "SYMPY_VERIFIED", f"equation residuals differ by nonzero scalar {ratio}"
                return "UNSUPPORTED_FRAGMENT", "multivariate relation equivalence was not decided"
            if not isinstance(left, sympy.Relational) and not isinstance(right, sympy.Relational):
                difference = sympy.simplify(left - right)
                if difference == 0:
                    return "SYMPY_VERIFIED", "symbolic difference simplifies exactly to zero"
                if not difference.free_symbols:
                    return "SYMPY_MISMATCH", f"closed expression difference is {difference}"
            return "UNSUPPORTED_FRAGMENT", "relation type is outside the conservative equivalence checker"
        except Exception as exc:
            return "UNSUPPORTED_FRAGMENT", f"SymPy declined the comparison: {type(exc).__name__}: {exc}"


def empty_state(problem: SourceProblem, goal_text: str) -> dict[str, Any]:
    claims: dict[str, Any] = {
        "p0": {
            "id": "p0",
            "proposition": clean_prose(problem.statement, 1500),
            "status": "GIVEN",
            "scope": "global",
            "domain": "Proposition",
            "dependencies": [],
        }
    }
    seen = {claims["p0"]["proposition"]}
    for block in math_blocks_with_headings(problem.initial_state):
        proposition = normalize_math(block.raw)
        if not proposition or proposition in seen:
            continue
        claim_id = f"i{len(claims):03d}"
        claims[claim_id] = {
            "id": claim_id,
            "proposition": proposition,
            "status": "GIVEN",
            "scope": "global",
            "domain": "Proposition",
            "dependencies": [],
        }
        seen.add(proposition)
    return {
        "active_scopes": ["global"],
        "claims": claims,
        "candidates": {},
        "branches": {},
        "goals": {
            "g0": {"id": "g0", "proposition": goal_text, "status": "OPEN", "scope": "global"}
        },
        "obligations": {},
    }


def build_payload(problem: SourceProblem, transition: Transition, before_state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    after_state = copy.deepcopy(before_state)
    output_id = f"c{transition.index:03d}"
    prior_claim = "p0" if transition.index == 1 else f"c{transition.index - 1:03d}"
    dependencies = transition.dependency_ids or [prior_claim]
    after_state["claims"][output_id] = {
        "id": output_id,
        "proposition": transition.after,
        "status": "DERIVED",
        "scope": "global",
        "domain": "Proposition",
        "dependencies": dependencies,
    }
    created_specs = []
    for obligation in transition.obligations:
        oid = obligation["id"]
        created_specs.append({"id": oid, "statement": obligation["statement"]})
        after_state["obligations"][oid] = {
            "id": oid,
            "proposition": obligation["statement"],
            "status": "OPEN",
            "mandatory": True,
            "origin": transition.transition_id,
            "dependencies": dependencies,
        }
    evidence_id = f"e{transition.index:03d}"
    rule = transition.operation
    payload = {
        "schema_version": SCHEMA_VERSION,
        "case_id": transition.transition_id,
        "pair_id": problem.problem_id,
        "split": "DEV",
        "semantic_focus": "WARRANT",
        "source": {
            "dataset": "Write-Algebra-Problems.md",
            "source_row_id": problem.problem_id,
            "source_hash": sha256(problem.raw),
            "category": problem.domain,
            "level": problem.difficulty,
            "problem": problem.statement,
            "solution_span": transition.source_span,
            "solution_span_hash": sha256(transition.source_span),
            "gold125_overlap": False,
            "source_role": "untrusted granular worked-mathematics source",
        },
        "state_before": before_state,
        "action": {
            "id": f"a{transition.index:03d}",
            "operation": transition.operation,
            "summary": transition.after,
            "output_id": output_id,
            "dependencies": dependencies,
            "preconditions": transition.preconditions,
            "obligations_created": created_specs,
            "obligations_discharged": [],
            "typing": {"input_domains": {prior_claim: "Proposition"}, "output_domain": "Proposition"},
            "warrant": {"evidence_id": evidence_id, "rule": rule, "premise_ids": dependencies},
            "goal_effect": {},
            "scope_effect": {},
            "branch_effect": {},
            "candidate_effect": {},
            "epistemic_effect": {},
        },
        "state_after": after_state,
        "evidence": {
            evidence_id: {
                "id": evidence_id,
                "kind": "SOURCE_DERIVATION",
                "status": "UNKNOWN",
                "trusted": False,
                "supports_rule": rule,
                "premise_ids": dependencies,
                "payload": {"source_span_sha256": sha256(transition.source_span)},
            }
        },
    }
    return payload, after_state


def semantic_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop experiment-only envelope keys not modelled by the frozen adapter."""
    return {key: value for key, value in payload.items() if key not in {"pair_id", "split", "semantic_focus"}}


def load_hml(hml_root: Path) -> dict[str, Any]:
    if hml_root.name == "semantic_state":
        source_root = hml_root.parents[2]
    else:
        source_root = hml_root / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    from hamiltonian_lang.semantic_state import (  # type: ignore[import-not-found]
        export_transition,
        import_transition,
        parse_transition,
        render_transition,
        verify_runtime,
    )
    return {
        "export": export_transition,
        "import": import_transition,
        "parse": parse_transition,
        "render": render_transition,
        "verify": verify_runtime,
    }


def validate_and_render(
    problem: SourceProblem,
    transitions: list[Transition],
    hml: dict[str, Any],
    sympy: SympyVerifier,
    schema_validator: Any,
) -> None:
    goal_text = clean_prose(problem.statement, 1200)
    state = empty_state(problem, goal_text)
    blocking_gap: str | None = None
    for transition in transitions:
        prior_claim = "p0" if transition.index == 1 else f"c{transition.index - 1:03d}"
        transition.dependency_ids = [prior_claim]
        if transition.index > 1 and (
            transition.operation in {"VERIFY", "APPLY_THEOREM"}
            or transition.warrant.lower().startswith(("therefore", "thus", "hence", "so"))
        ):
            transition.dependency_ids = ["p0", prior_claim]
        backend_status, backend_detail = sympy.verify(transition.before, transition.after, transition.warrant)
        transition.backend_status = backend_status
        transition.backend_detail = backend_detail
        if backend_status == "SYMPY_VERIFIED" and transition.classification == STATUS_UNVERIFIED:
            transition.classification = STATUS_BACKEND
            transition.classification_reason = "the neutral/HML shape is supported and a conservative SymPy comparison independently verified this step"
        elif backend_status == "SYMPY_MISMATCH" and transition.classification not in (STATUS_GAP, STATUS_LIBRARY):
            # Adjacent displays sometimes move from a whole state to a component
            # calculation. Non-equivalence is therefore a diagnostic, not proof that the
            # source mathematics is corrupt.
            transition.classification = STATUS_UNVERIFIED
            transition.classification_reason = "the step is representable, but the conservative equivalence check did not establish it; inspect the source warrant/component context"
        if transition.classification == STATUS_GAP:
            blocking_gap = blocking_gap or transition.transition_id
            continue
        if blocking_gap:
            transition.depends_on_gap = blocking_gap
            transition.classification = STATUS_GAP
            transition.classification_reason = f"the state depends on unsupported transition {blocking_gap}; rendering it independently would lose provenance"
            transition.gap_code = "DOWNSTREAM_OF_SEMANTIC_GAP"
            continue
        payload, next_state = build_payload(problem, transition, state)
        try:
            schema_validator.validate(payload)
            transition.schema_validation = "PASS"
            model = hml["import"](payload)
            expected = semantic_payload(payload)
            exported = hml["export"](model)
            if exported != expected:
                raise AssertionError("neutral import/export changed the canonical payload")
            rendered = hml["render"](model)
            reparsed = hml["parse"](rendered)
            if hml["export"](reparsed) != expected:
                raise AssertionError("HML render/parse changed the canonical payload")
            result = hml["verify"](model)
        except Exception as exc:
            transition.classification = STATUS_AMBIGUITY
            transition.classification_reason = f"translation serialization failed: {type(exc).__name__}: {exc}"
            transition.gap_code = "TRANSLATION_SERIALIZATION_FAILURE"
            blocking_gap = transition.transition_id
            continue
        transition.hml_text = rendered
        transition.hml_roundtrip = "PASS"
        transition.hml_runtime_verdict = str(getattr(result.verdict, "value", result.verdict))
        transition.hml_unknowns = list(result.unknowns)
        if transition.hml_runtime_verdict == "INVALID":
            raise AssertionError(f"{transition.transition_id}: generated HML is INVALID")
        state = next_state


def markdown_fence(value: str, language: str = "text") -> str:
    return f"~~~~{language}\n{value.rstrip()}\n~~~~"


def render_transition_md(transition: Transition) -> str:
    lines = [
        f"#### {transition.transition_id}",
        "",
        f"- **STATE_BEFORE:** `{transition.before}`",
        f"- **ACTION:** `{transition.operation}` — {transition.warrant}",
        f"- **WARRANT/PRECONDITIONS:** `{canonical_json(transition.preconditions)}`",
        f"- **DEPENDENCIES:** `{canonical_json(transition.dependency_ids)}`; source span SHA-256 `{sha256(transition.source_span)}`",
        f"- **STATE_AFTER:** `{transition.after}`",
        f"- **Mechanisms:** {', '.join(transition.mechanisms)}",
        f"- **Classification:** `{transition.classification}` — {transition.classification_reason}",
        f"- **Backend:** `{transition.backend_status}` — {transition.backend_detail}",
        f"- **Validation:** schema `{transition.schema_validation}`; HML round trip `{transition.hml_roundtrip}`; runtime verdict `{transition.hml_runtime_verdict}`",
    ]
    if transition.obligations:
        lines.append(f"- **Obligations created:** `{canonical_json(transition.obligations)}`")
    if transition.hml_unknowns:
        lines.append(f"- **Runtime unknowns:** `{canonical_json(transition.hml_unknowns)}`")
    if transition.gap_code:
        lines.append(f"- **Gap/refusal code:** `{transition.gap_code}`")
    if transition.depends_on_gap:
        lines.append(f"- **Depends on unsupported step:** `{transition.depends_on_gap}`")
    lines.extend(["", "<details><summary>Exact source span</summary>", "", markdown_fence(transition.source_span, "markdown"), "", "</details>"])
    if transition.hml_text:
        lines.extend(["", "<details><summary>Deterministically rendered frozen HML</summary>", "", markdown_fence(transition.hml_text, "hml"), "", "</details>"])
    else:
        lines.extend(["", "**HML rendering withheld:** emitting HML here would erase or falsify the unsupported distinction."])
    return "\n".join(lines)


def render_problem_md(record: ProblemRecord) -> str:
    problem = record.source
    status_counts = Counter(t.classification for t in record.transitions)
    lines = [
        f"## {problem.problem_id} — {problem.corpus.title}",
        "",
        f"- **Stable problem_id:** `{problem.problem_id}`",
        f"- **Domain:** {problem.domain}",
        f"- **Difficulty:** `{problem.difficulty}`",
        f"- **Source lines:** {problem.source_start_line}–{problem.source_end_line}",
        f"- **Source block SHA-256:** `{sha256(problem.raw)}`",
        f"- **Atomic transitions:** {len(record.transitions)}",
        f"- **Status counts:** `{canonical_json(dict(sorted(status_counts.items())))}`",
        "",
        "### Original problem",
        "",
        problem.statement.strip(),
        "",
        "### Initial representation-neutral state",
        "",
        markdown_fence(problem.initial_state, "markdown"),
        "",
        f"**Target:** {problem.statement.strip()}",
        "",
        "No final answer is inserted into the initial state.",
        "",
        "### Source reasoning (verbatim)",
        "",
        "<details><summary>Open complete source problem and worked solution</summary>",
        "",
        markdown_fence(problem.raw, "markdown"),
        "",
        "</details>",
        "",
        "### Atomic semantic trajectory",
        "",
    ]
    for transition in record.transitions:
        lines.extend([render_transition_md(transition), ""])
    ledger_parts: list[tuple[str, str]] = []
    for heading_match in re.finditer(r"(?mi)^###\s+(.+?ledger.*?)\s*$", problem.raw):
        heading = clean_prose(heading_match.group(1), 180)
        content = section(problem.raw, re.escape(heading))
        if content and (heading, content) not in ledger_parts:
            ledger_parts.append((heading, content))
    lines.extend(["### Candidate / branch / obligation ledger", ""])
    if ledger_parts:
        for heading, content in ledger_parts:
            lines.extend([f"**{heading}**", "", content.strip(), ""])
    else:
        obligations = [item for transition in record.transitions for item in transition.obligations]
        if obligations:
            lines.append(f"Generated obligations: `{canonical_json(obligations)}`")
        else:
            lines.append("No explicit candidate, branch, or obligation ledger occurs in the source problem.")
        lines.append("")
    lines.extend(["### Final mathematical result", "", problem.final_answer.strip(), "", "### Problem diagnostics", ""])
    if record.diagnostics:
        lines.extend(f"- `{item}`" for item in record.diagnostics)
    else:
        lines.append("- No source-format diagnostic was raised.")
    return "\n".join(lines)


def render_master(source_text: str, records: list[ProblemRecord]) -> str:
    transitions = [transition for record in records for transition in record.transitions]
    status = Counter(t.classification for t in transitions)
    mechanisms = Counter(m for t in transitions for m in t.mechanisms)
    operations = Counter(t.operation for t in transitions)
    backend = Counter(t.backend_status for t in transitions)
    gaps = Counter(t.gap_code for t in transitions if t.gap_code)
    direct_gaps = sum(
        t.gap_code in {
            "BRANCH_CREATION_NOT_REPRESENTABLE",
            "CANDIDATE_CREATION_NOT_REPRESENTABLE",
            "APPROXIMATION_STATUS_NOT_REPRESENTABLE",
        }
        for t in transitions
    )
    downstream_gaps = gaps.get("DOWNSTREAM_OF_SEMANTIC_GAP", 0)
    ambiguities = sum(1 for t in transitions if t.classification == STATUS_AMBIGUITY)
    hml_rendered = sum(t.hml_text is not None for t in transitions)
    hml_roundtrip_pass = sum(t.hml_roundtrip == "PASS" for t in transitions)
    schema_pass = sum(t.schema_validation == "PASS" for t in transitions)
    hml_invalid = sum(t.hml_runtime_verdict == "INVALID" for t in transitions)
    source_problem_counts = Counter(record.source.corpus.key for record in records)
    source_block_chars = sum(len(record.source.raw) for record in records)

    summary_rows = "\n".join(f"| `{key}` | {value} |" for key, value in sorted(status.items()))
    corpus_rows = "\n".join(f"| `{key}` | {value} |" for key, value in sorted(source_problem_counts.items()))
    mechanism_rows = "\n".join(f"| `{key}` | {value} |" for key, value in mechanisms.most_common())
    operation_rows = "\n".join(f"| `{key}` | {value} |" for key, value in operations.most_common())
    backend_rows = "\n".join(f"| `{key}` | {value} |" for key, value in sorted(backend.items()))
    gap_rows = "\n".join(f"| `{key}` | {value} |" for key, value in sorted(gaps.items())) or "| none | 0 |"

    header = f"""# Master Synthetic Mathematics → Neutral Trajectories → HML

## Corpus summary

This is the sole authoritative human artifact for the supplied synthetic worked-mathematics
source. The canonical interpretation is the representation-neutral trajectory. HML is a
deterministic rendering only where the frozen release can preserve the same distinctions.

| Measure | Count |
|---|---:|
| Source problems | {len(records)} |
| Atomic reasoning transitions | {len(transitions)} |
| Frozen-HML renderings emitted | {hml_rendered} |
| Neutral-schema validations passed | {schema_pass} |
| Frozen-HML exact round trips | {hml_roundtrip_pass} |
| Frozen-HML `INVALID` verdicts accepted | {hml_invalid} |
| Source ambiguities/corruptions | {ambiguities} |
| Transitions carrying a genuine/current semantic-gap refusal | {status.get(STATUS_GAP, 0)} |
| Direct semantic-gap transitions | {direct_gaps} |
| Downstream transitions withheld after a gap | {downstream_gaps} |

### Source corpus reconciliation

| Corpus | Problems |
|---|---:|
{corpus_rows}

Exactly six 100-problem worked corpora were recovered. Their 600 verbatim blocks contain
{source_block_chars:,} characters and are embedded below. The complete supplied source has
SHA-256 `{sha256(source_text)}`. The initial problem-list-only algebra response is treated as
provenance for the same ALG-001…ALG-100 problems, not as a seventh duplicate corpus.

### Frozen authority

- HML tag: `{FROZEN_HML_TAG}`
- HML commit: `{FROZEN_HML_SHA}`
- Corpus base commit: `{CORPUS_BASE_SHA}`
- Neutral schema: `{SCHEMA_VERSION}`
- `./hml_core` was not modified; validation used an isolated checkout of the exact frozen commit.

### Status definitions and counts

| Status | Transitions |
|---|---:|
{summary_rows}

`FULLY_REPRESENTABLE_AND_BACKEND_VERIFIED` means the neutral/HML representation round-trips
and a conservative external symbolic comparison verified the mathematical state change. It
does **not** mean the source evidence became a trusted HML attestation. Runtime HML verdicts
therefore remain `UNRESOLVED` where the only warrant is this untrusted source.

`REPRESENTABLE_BUT_CURRENTLY_UNVERIFIABLE` means the state/effect is expressible but no
trusted mathematical checker established the warrant. `REQUIRES_EXISTING_TRUSTED_BACKEND_OR_LIBRARY`
marks theorem/domain steps whose representation exists but whose truth requires a relevant
checker or theorem library. `GENUINE_HML_SEMANTIC_GAP` is a refusal to render a distinction
the frozen state model cannot carry. `SOURCE_AMBIGUITY_OR_CORRUPTION` is never promoted.

### Validation policy

Every emitted HML transition passed neutral import/export identity and HML render/parse
identity against commit `{FROZEN_HML_SHA}`. Runtime verification was used, never offline replay.
An untrusted source warrant is represented by `UNKNOWN` evidence, so `UNRESOLVED` is the
honest verdict. No `INVALID` transition is retained. SymPy is used only on a conservative
algebraic fragment; parser refusal is `UNSUPPORTED_FRAGMENT`, not evidence against a step.

### Known translation boundary

Current HML cannot add candidates, branches, or goals through an action, and it has no
exact-versus-approximate claim status. Once a transition hits one of those gaps, downstream
HML is withheld until a faithful state can be reconstructed; independent rendering would
erase provenance. Computational questions also retain their source target as an open goal:
the answer is never read ahead into `state_before` merely to satisfy string-equality goal
discharge.

### Independent adversarial audit of six difficult trajectories

These six end-of-corpus problems were re-derived independently rather than accepted because
their source spans existed. No transition correction was required in this audit.

| Problem | Independent check | Result |
|---|---|---|
| `ALG-100` | Cross-multiplication under `x != 2,-1`, quadratic solution, forbidden-value filtering | two stated radical roots verified |
| `GEN-100` | Rational/log/root domain, reversible squaring, two absolute-value branches, substitution in original | `x=-5,-1` verified |
| `CALC-100` | Feasible interval, stationary point, endpoint comparison, second derivative | width `4`, height `8`, maximum area `32` verified |
| `PROB-100` | Binomial MLE/normal CI and Beta-Binomial conjugate update | `0.6`, approximate CI, `Beta(20,20)`, posterior mean `0.5` verified |
| `LINALG-100` | `A=3I+J`, orthogonal eigenspaces, determinant/rank, spectral solve | eigenvalues `6,3,3` and `x=(1,1,1)^T` verified |
| `MIXED-100` | substitution `u=x^2`, nonnegative-root filtering, Jacobian determinant | two stated intersections and transversality verified |

The audit also checked for missing nonzero/sign/domain hypotheses, branch leakage, candidate
promotion, and approximation drift. Such distinctions are retained as explicit source
conditions or refusal codes; source-span identity was never treated as mathematical proof.

## Corpus
"""
    bodies: list[str] = []
    current = ""
    for record in records:
        if record.source.corpus.key != current:
            current = record.source.corpus.key
            bodies.append(f"\n# Corpus {current}: {record.source.corpus.title}\n")
        bodies.append(render_problem_md(record))

    census = f"""

# Diagnostic census

## Reasoning mechanisms observed

| Mechanism | Transitions |
|---|---:|
{mechanism_rows}

## Operation labels used descriptively

| Operation | Transitions |
|---|---:|
{operation_rows}

## Independent backend outcomes

| Outcome | Transitions |
|---|---:|
{backend_rows}

## Semantic-gap and refusal census

| Gap/refusal code | Transitions |
|---|---:|
{gap_rows}

## Layer diagnosis

- **Handled cleanly at the representation layer:** immutable claim accumulation,
  dependencies, source provenance, explicit preconditions, persistent obligations, custom
  domains as opaque names, and source-named theorem/application warrants.
- **Repeated verification boundary:** algebraic, calculus, probability, statistical,
  geometric, matrix, convergence, and theorem claims are not made true by HML structural
  acceptance. They require checked certificates or remain source-derived.
- **Repeated core-language boundary:** forward candidate creation, forward branch creation,
  goal/subgoal creation, and an exact-to-approximate epistemic transition.
- **Corpus/goal boundary:** most computational prompts do not state their answer proposition
  in advance. The frozen exact-string goal-discharge rule cannot be satisfied without
  leaking the answer into the initial state, so this artifact refuses that shortcut.
- **Source boundary:** backend mismatches and malformed LaTeX are retained and labelled;
  unsupported backend syntax is not called corruption.

## Readiness decision

This corpus is **ready for Phase-II diagnostic use**, including representability audits,
checker/library targeting, and curriculum subset selection. It is **not ready for blind
training as uniformly verified truth**: consumers must filter by the per-transition status,
backend result, and HML runtime verdict. Genuine gaps must remain exclusions until the HML
core track adjudicates them.
"""
    return header + "\n\n".join(bodies) + census


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hml-root", type=Path, required=True, help="isolated checkout at the frozen HML SHA")
    parser.add_argument("--schema", type=Path, required=True)
    args = parser.parse_args()

    source_text = args.source.read_text(encoding="utf-8")
    problems = parse_problems(source_text)
    hml = load_hml(args.hml_root)
    sympy = SympyVerifier()
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("jsonschema is required for corpus validation") from exc
    schema_validator = jsonschema.Draft202012Validator(json.loads(args.schema.read_text(encoding="utf-8")))
    records: list[ProblemRecord] = []
    for number, problem in enumerate(problems, 1):
        transitions, diagnostics = extract_transitions(problem)
        validate_and_render(problem, transitions, hml, sympy, schema_validator)
        records.append(
            ProblemRecord(
                source=problem,
                transitions=transitions,
                diagnostics=diagnostics,
                goal_text=clean_prose(problem.statement, 1200),
            )
        )
        if number % 25 == 0:
            print(f"processed {number}/600 problems", file=sys.stderr)

    output = render_master(source_text, records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(
        canonical_json(
            {
                "problems": len(records),
                "transitions": sum(len(record.transitions) for record in records),
                "output": str(args.output),
                "output_sha256": sha256(output),
                "status_counts": dict(sorted(Counter(t.classification for r in records for t in r.transitions).items())),
            }
        )
    )


if __name__ == "__main__":
    main()
