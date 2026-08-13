"""Parse the 600-problem master artifact into structured transition records.

The artifact is the authoritative human-readable output of the frozen-HML rendering run; the
neutral records for *withheld* transitions were never emitted, so the markdown is the only
place their classification survives. This module reads it and nothing else writes to it.

Two kinds of record come out:

* every transition's classification, gap code and recorded validation — 3,978 of them;
* the deterministically rendered frozen HML for the 3,167 that were emitted, verbatim, which
  is what makes a real regression measurement possible rather than a sampled one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_HEADING = re.compile(r"^#### ([A-Z]+-\d+-T\d+)\s*$")
_PROBLEM = re.compile(r"^## ([A-Z]+-\d+) — ")
_FIELD = re.compile(r"^- \*\*([^:*]+):\*\* (.*)$")
_HML_OPEN = re.compile(r"^~{3,}hml\s*$")
_MD_OPEN = re.compile(r"^~{3,}markdown\s*$")
_FENCE = re.compile(r"^~{3,}\s*$")
_CODE = re.compile(r"`([A-Z_0-9]+)`")
_SPAN_SUMMARY = "<details><summary>Exact source span</summary>"
_SOLUTION_SUMMARY = "<details><summary>Open complete source problem and worked solution</summary>"
_SPAN_SHA = re.compile(r"source span SHA-256 `([0-9a-f]{64})`")

#: The three direct-gap codes the corpus reports, and the count each should have.
DIRECT_GAP_CODES = {
    "CANDIDATE_CREATION_NOT_REPRESENTABLE": 192,
    "BRANCH_CREATION_NOT_REPRESENTABLE": 168,
    "APPROXIMATION_STATUS_NOT_REPRESENTABLE": 63,
}
DOWNSTREAM_CODE = "DOWNSTREAM_OF_SEMANTIC_GAP"


@dataclass
class Problem:
    """One source problem: its statement, its target, and its verbatim worked solution."""

    id: str
    original_problem: str = ""
    target: str = ""
    domain: str = ""
    difficulty: str = ""
    source_block: str | None = None
    source_block_sha: str | None = None


@dataclass
class Record:
    id: str
    problem_id: str
    state_before: str = ""
    state_after: str = ""
    action: str = ""
    dependencies: str = ""
    classification: str = ""
    gap_code: str | None = None
    depends_on_unsupported: str | None = None
    validation: str = ""
    hml: str | None = None
    #: The verbatim worked-solution text this transition was read from. **The source.**
    source_span: str | None = None
    #: The SHA-256 the artifact publishes for that span. Recomputing it over
    #: :attr:`source_span` is what proves a rederivation consumed the real bytes rather than
    #: a plausible reconstruction of them.
    source_span_sha: str | None = None
    raw: dict[str, str] = field(default_factory=dict)

    @property
    def dependency_ids(self) -> list[str]:
        """The claim/candidate ids the step cites, read out of the rendered field.

        The field is rendered as ``["p0"]``; the trailing source-span text is provenance and is
        not part of the list, so this reads only up to the closing bracket.
        """
        m = re.match(r"\s*`?\[(.*?)\]", self.dependencies)
        if not m:
            return []
        return re.findall(r'"([^"]+)"', m.group(1))

    @property
    def operation(self) -> str:
        m = re.match(r"\s*`([A-Z_]+)`", self.action)
        return m.group(1) if m else "STEP"

    @property
    def summary(self) -> str:
        parts = self.action.split("—", 1)
        return parts[1].strip() if len(parts) == 2 else ""

    @property
    def runtime_verdict(self) -> str | None:
        m = re.search(r"runtime verdict `([A-Z_]+)`", self.validation)
        return m.group(1) if m else None


def _clean(value: str) -> str:
    """Strip the artifact's backtick emphasis from a scalar field."""
    return value.strip().strip("`").strip()


def parse(path: Path) -> list[Record]:
    return _parse(path)[0]


def parse_problems(path: Path) -> dict[str, Problem]:
    return _parse(path)[1]


def _parse(path: Path) -> tuple[list[Record], dict[str, Problem]]:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    records: list[Record] = []
    problems: dict[str, Problem] = {}
    current: Record | None = None
    problem: Problem | None = None
    hml: list[str] | None = None
    markdown: list[str] | None = None
    #: What the next ``~~~~markdown`` fence is: a transition's source span, a problem's
    #: verbatim solution, or neither. Tracked because the artifact uses the same fence for
    #: all three and only the preceding ``<details>`` summary tells them apart.
    pending: str | None = None
    section: str | None = None

    for line in lines:
        if hml is not None:
            if _FENCE.match(line):
                assert current is not None
                current.hml = "\n".join(hml)
                hml = None
            else:
                hml.append(line)
            continue
        if markdown is not None:
            if _FENCE.match(line):
                body = "\n".join(markdown)
                if pending == "span" and current is not None:
                    current.source_span = body
                elif pending == "solution" and problem is not None:
                    problem.source_block = body
                markdown = None
                pending = None
            else:
                markdown.append(line)
            continue

        heading = _HEADING.match(line)
        if heading:
            tid = heading.group(1)
            current = Record(id=tid, problem_id=tid.rsplit("-T", 1)[0])
            records.append(current)
            section = None
            continue

        pheading = _PROBLEM.match(line)
        if pheading:
            problem = Problem(id=pheading.group(1))
            problems[problem.id] = problem
            current = None
            section = None
            continue

        if line.startswith("### "):
            section = line[4:].strip()
            continue

        if line.strip() == _SPAN_SUMMARY:
            pending = "span"
            continue
        if line.strip() == _SOLUTION_SUMMARY:
            pending = "solution"
            continue

        if _HML_OPEN.match(line):
            hml = []
            continue
        if _MD_OPEN.match(line):
            markdown = []
            continue

        field_match = _FIELD.match(line)
        if not field_match:
            if (
                problem is not None
                and current is None
                and section == "Original problem"
                and line.strip()
            ):
                problem.original_problem = problem.original_problem or line.strip()
            continue
        name, value = field_match.group(1), field_match.group(2)

        if current is None:
            if problem is None:
                continue
            if name == "Domain":
                problem.domain = _clean(value)
            elif name == "Difficulty":
                problem.difficulty = _clean(value)
            elif name == "Source block SHA-256":
                problem.source_block_sha = _clean(value)
            elif name == "Target":
                problem.target = _clean(value)
            continue

        current.raw[name] = value
        if name == "STATE_BEFORE":
            current.state_before = _clean(value)
        elif name == "STATE_AFTER":
            current.state_after = _clean(value)
        elif name == "ACTION":
            current.action = value
        elif name == "DEPENDENCIES":
            current.dependencies = value
            m = _SPAN_SHA.search(value)
            current.source_span_sha = m.group(1) if m else None
        elif name == "Classification":
            current.classification = _clean(value.split("—", 1)[0])
        elif name == "Validation":
            current.validation = value
        elif name == "Gap/refusal code":
            m = _CODE.search(value)
            current.gap_code = m.group(1) if m else None
        elif name == "Depends on unsupported step":
            current.depends_on_unsupported = _clean(value)

    return records, problems


def direct_gaps(records: list[Record]) -> list[Record]:
    return [r for r in records if r.gap_code in DIRECT_GAP_CODES]


def downstream(records: list[Record]) -> list[Record]:
    return [r for r in records if r.gap_code == DOWNSTREAM_CODE]


def rendered(records: list[Record]) -> list[Record]:
    return [r for r in records if r.hml]
