from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

from .authority import DirectAuthority
from .canonical import digest, sha256_bytes
from .gate import GateOutcome


MUTATION_CASE_SCHEMA = "harness-rig/mutation-case/experimental-v1"
MUTATION_RESULT_SCHEMA = "harness-rig/mutation-result/experimental-v1"


@dataclass(frozen=True)
class MutationCase:
    schema: str
    invariant_id: str
    mutant_id: str
    detector_id: str
    relative_path: str
    search: str
    replacement: str
    detector_argv: tuple[str, ...]
    protected_oracle: bool = False

    @classmethod
    def create(
        cls, *, invariant_id: str, mutant_id: str, detector_id: str,
        relative_path: str, search: str, replacement: str,
        detector_argv: tuple[str, ...], protected_oracle: bool = False,
    ) -> "MutationCase":
        values = (invariant_id, mutant_id, detector_id, relative_path, search)
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError("invalid-mutation-case")
        path = Path(relative_path)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("mutation-path-escapes-root")
        if not isinstance(replacement, str):
            raise ValueError("invalid-mutation-replacement")
        if not detector_argv or any(not isinstance(x, str) or not x for x in detector_argv):
            raise ValueError("invalid-mutation-detector-argv")
        if not isinstance(protected_oracle, bool):
            raise ValueError("invalid-mutation-protected-oracle")
        return cls(
            MUTATION_CASE_SCHEMA, invariant_id, mutant_id, detector_id,
            relative_path.replace("\\", "/"), search, replacement,
            tuple(detector_argv), protected_oracle,
        )


@dataclass(frozen=True)
class DetectorRun:
    outcome: str
    exit_code: int | None
    stdout_digest: str | None
    stderr_digest: str | None
    reason: str | None


@dataclass(frozen=True)
class MutationResult:
    schema: str
    invariant_id: str
    mutant_id: str
    detector_id: str
    outcome: GateOutcome
    mutant_status: str
    baseline: DetectorRun
    mutant: DetectorRun | None
    source_before_digest: str | None
    source_after_digest: str | None
    authority_before_id: str | None
    authority_after_id: str | None
    authority_reopened: bool
    result_digest: str


def validate_mutation_map(cases: tuple[MutationCase, ...]) -> None:
    if not cases:
        raise ValueError("mutation-map-empty")
    seen_mutants: set[str] = set()
    for case in cases:
        if case.schema != MUTATION_CASE_SCHEMA:
            raise ValueError("unsupported-mutation-case-schema")
        if case.mutant_id in seen_mutants:
            raise ValueError("duplicate-mutation-mutant-id")
        seen_mutants.add(case.mutant_id)


def _run_detector(argv: tuple[str, ...], cwd: Path, timeout_seconds: float) -> DetectorRun:
    executable = shutil.which(argv[0])
    if executable is None:
        return DetectorRun("BLOCKED", None, None, None, "detector-executable-unavailable")
    resolved = str(Path(executable).resolve())
    try:
        p = subprocess.run(
            [resolved, *argv[1:]], cwd=cwd, capture_output=True, text=False,
            shell=False, timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return DetectorRun("BLOCKED", None, None, None, "detector-timeout")
    except OSError:
        return DetectorRun("BLOCKED", None, None, None, "detector-launch-unavailable")
    return DetectorRun(
        "PASS" if p.returncode == 0 else "FAIL",
        p.returncode,
        sha256_bytes(p.stdout),
        sha256_bytes(p.stderr),
        None,
    )


def run_mutation_case(repo: Path, case: MutationCase, *, timeout_seconds: float = 30.0) -> MutationResult:
    if case.schema != MUTATION_CASE_SCHEMA:
        raise ValueError("unsupported-mutation-case-schema")
    root = repo.resolve()
    source = (root / case.relative_path).resolve()
    if root not in [source, *source.parents]:
        raise ValueError("mutation-path-escapes-root")
    if not source.is_file():
        baseline = DetectorRun("BLOCKED", None, None, None, "mutation-source-missing")
        outcome = GateOutcome.create("BLOCKED", reasons=("mutation-source-missing",))
        return _result(case, outcome, "NOT_APPLIED", baseline, None, None, None, None, None)

    baseline = _run_detector(case.detector_argv, root, timeout_seconds)
    if baseline.outcome != "PASS":
        reason = baseline.reason or f"baseline-detector-exit:{baseline.exit_code}"
        outcome = GateOutcome.create("BLOCKED", reasons=(reason,), attempt_count=1)
        before_digest = sha256_bytes(source.read_bytes())
        return _result(case, outcome, "NOT_APPLIED", baseline, None, before_digest, None, None, None)

    source_before_digest = sha256_bytes(source.read_bytes())
    authority_before_id = None
    if case.protected_oracle:
        authority_before_id = DirectAuthority.from_file(root, case.relative_path, "protected-oracle").authority_id

    with tempfile.TemporaryDirectory(prefix="harness-rig-mutant-") as td:
        mutant_root = Path(td) / "repo"
        shutil.copytree(root, mutant_root, symlinks=True)
        mutant_source = mutant_root / case.relative_path
        try:
            text = mutant_source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            outcome = GateOutcome.create("BLOCKED", reasons=("mutation-source-unreadable",), attempt_count=1)
            return _result(
                case, outcome, "NOT_APPLIED", baseline, None,
                source_before_digest, None, authority_before_id, None,
            )
        count = text.count(case.search)
        if count != 1:
            outcome = GateOutcome.create(
                "BLOCKED", reasons=(f"mutation-search-count:{count}",), attempt_count=1
            )
            return _result(
                case, outcome, "NOT_APPLIED", baseline, None,
                source_before_digest, None, authority_before_id, None,
            )
        mutant_source.write_text(text.replace(case.search, case.replacement, 1), encoding="utf-8")
        source_after_digest = sha256_bytes(mutant_source.read_bytes())
        authority_after_id = None
        if case.protected_oracle:
            authority_after_id = DirectAuthority.from_file(
                mutant_root, case.relative_path, "protected-oracle"
            ).authority_id
        mutant = _run_detector(case.detector_argv, mutant_root, timeout_seconds)

    authority_reopened = bool(
        case.protected_oracle
        and authority_before_id is not None
        and authority_after_id is not None
        and authority_before_id != authority_after_id
    )
    if mutant.outcome == "BLOCKED":
        reason = mutant.reason or "mutant-detector-blocked"
        outcome = GateOutcome.create("BLOCKED", reasons=(reason,), attempt_count=2)
        mutant_status = "UNKNOWN"
    elif mutant.outcome == "FAIL":
        outcome = GateOutcome.create("PASS", attempt_count=2)
        mutant_status = "KILLED"
    else:
        outcome = GateOutcome.create(
            "FAIL", reasons=("mutant-survived",), attempt_count=2
        )
        mutant_status = "SURVIVED"

    return _result(
        case, outcome, mutant_status, baseline, mutant,
        source_before_digest, source_after_digest,
        authority_before_id, authority_after_id,
        authority_reopened=authority_reopened,
    )


def _result(
    case: MutationCase,
    outcome: GateOutcome,
    mutant_status: str,
    baseline: DetectorRun,
    mutant: DetectorRun | None,
    source_before_digest: str | None,
    source_after_digest: str | None,
    authority_before_id: str | None,
    authority_after_id: str | None,
    authority_reopened: bool = False,
) -> MutationResult:
    material = {
        "schema": MUTATION_RESULT_SCHEMA,
        "invariant_id": case.invariant_id,
        "mutant_id": case.mutant_id,
        "detector_id": case.detector_id,
        "outcome": asdict(outcome),
        "mutant_status": mutant_status,
        "baseline": asdict(baseline),
        "mutant": asdict(mutant) if mutant is not None else None,
        "source_before_digest": source_before_digest,
        "source_after_digest": source_after_digest,
        "authority_before_id": authority_before_id,
        "authority_after_id": authority_after_id,
        "authority_reopened": authority_reopened,
    }
    return MutationResult(
        MUTATION_RESULT_SCHEMA,
        case.invariant_id,
        case.mutant_id,
        case.detector_id,
        outcome,
        mutant_status,
        baseline,
        mutant,
        source_before_digest,
        source_after_digest,
        authority_before_id,
        authority_after_id,
        authority_reopened,
        digest(material),
    )
