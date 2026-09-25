from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .authority import AuthorityRef
from .canonical import digest
from .evidence import ArtifactRef, EvidenceReceipt, InputBinding, bind_path
from .gate import GateClaim, GateOutcome, _now
from .state import capture_state


ARCHITECTURE_POLICY_SCHEMA = "harness-rig/architecture-policy/experimental-v1"
ARCHITECTURE_REPORT_SCHEMA = "harness-rig/architecture-report/experimental-v1"


@dataclass(frozen=True)
class ArchitectureRule:
    rule_id: str
    source_globs: tuple[str, ...]
    forbidden_import_prefixes: tuple[str, ...]


@dataclass(frozen=True)
class ArchitecturePolicy:
    schema: str
    policy_id: str
    rules: tuple[ArchitectureRule, ...]

    def policy_digest(self) -> str:
        return digest(asdict(self))


@dataclass(frozen=True)
class ArchitectureViolation:
    rule_id: str
    source_path: str
    line: int
    imported: str
    forbidden_prefix: str


@dataclass(frozen=True)
class ArchitectureEvaluation:
    schema: str
    policy_id: str
    policy_digest: str
    outcome: GateOutcome
    checked_files: tuple[str, ...]
    violations: tuple[ArchitectureViolation, ...]
    report_digest: str


@dataclass(frozen=True)
class ArchitectureGateRequest:
    repo: Path
    repository_id: str
    authority: AuthorityRef
    claim: GateClaim
    run_id: str
    producer_id: str
    policy: ArchitecturePolicy
    policy_path: str | None = None
    subject_ref: str = "repository"


@dataclass(frozen=True)
class ArchitectureGateResult:
    evaluation: ArchitectureEvaluation
    receipt: EvidenceReceipt


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid-architecture-policy-{field}")
    return value


def load_architecture_policy(data: dict[str, Any]) -> ArchitecturePolicy:
    if not isinstance(data, dict) or set(data) != {"schema", "policy_id", "rules"}:
        raise ValueError("invalid-architecture-policy")
    if data.get("schema") != ARCHITECTURE_POLICY_SCHEMA:
        raise ValueError("unsupported-architecture-policy-schema")
    policy_id = _required_string(data["policy_id"], "policy-id")
    raw_rules = data["rules"]
    if not isinstance(raw_rules, list) or not raw_rules:
        raise ValueError("invalid-architecture-policy-rules")
    rules: list[ArchitectureRule] = []
    seen: set[str] = set()
    for raw in raw_rules:
        if not isinstance(raw, dict) or set(raw) != {"rule_id", "source_globs", "forbidden_import_prefixes"}:
            raise ValueError("invalid-architecture-policy-rule")
        rule_id = _required_string(raw["rule_id"], "rule-id")
        if rule_id in seen:
            raise ValueError("duplicate-architecture-rule-id")
        seen.add(rule_id)
        source_globs = raw["source_globs"]
        forbidden = raw["forbidden_import_prefixes"]
        if not isinstance(source_globs, list) or not source_globs:
            raise ValueError("invalid-architecture-rule-source-globs")
        if not isinstance(forbidden, list) or not forbidden:
            raise ValueError("invalid-architecture-rule-forbidden-imports")
        source_tuple = tuple(_required_string(x, "source-glob") for x in source_globs)
        forbidden_tuple = tuple(_required_string(x, "forbidden-import") for x in forbidden)
        rules.append(ArchitectureRule(rule_id, source_tuple, forbidden_tuple))
    return ArchitecturePolicy(ARCHITECTURE_POLICY_SCHEMA, policy_id, tuple(rules))


def load_architecture_policy_file(path: Path) -> ArchitecturePolicy:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("unreadable-architecture-policy") from exc
    return load_architecture_policy(data)


def _normalized_imports(source: str, path: str) -> tuple[tuple[int, str], ...]:
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        raise ValueError(f"architecture-source-parse-error:{path}:{exc.lineno or 0}") from exc
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level
            module = node.module or ""
            imports.append((node.lineno, prefix + module))
    return tuple(imports)


def _matches_prefix(imported: str, prefix: str) -> bool:
    return imported == prefix or imported.startswith(prefix + ".")


def evaluate_architecture(repo: Path, policy: ArchitecturePolicy) -> ArchitectureEvaluation:
    root = repo.resolve()
    checked: set[str] = set()
    violations: list[ArchitectureViolation] = []
    reasons: list[str] = []

    for rule in policy.rules:
        matched: set[Path] = set()
        for pattern in rule.source_globs:
            for path in root.glob(pattern):
                if path.is_file() and path.suffix == ".py":
                    matched.add(path.resolve())
        if not matched:
            reasons.append(f"rule-source-missing:{rule.rule_id}")
            continue
        for path in sorted(matched):
            if root not in [path, *path.parents]:
                reasons.append(f"rule-source-escaped:{rule.rule_id}")
                continue
            rel = path.relative_to(root).as_posix()
            checked.add(rel)
            try:
                imports = _normalized_imports(path.read_text(encoding="utf-8"), rel)
            except (OSError, UnicodeError, ValueError) as exc:
                reasons.append(str(exc))
                continue
            for line, imported in imports:
                for forbidden in rule.forbidden_import_prefixes:
                    if _matches_prefix(imported, forbidden):
                        violations.append(ArchitectureViolation(
                            rule.rule_id, rel, line, imported, forbidden
                        ))

    if reasons:
        outcome = GateOutcome.create("BLOCKED", reasons=tuple(sorted(set(reasons))))
    elif violations:
        outcome = GateOutcome.create(
            "FAIL",
            reasons=tuple(
                f"architecture-violation:{v.rule_id}:{v.source_path}:{v.line}:{v.imported}"
                for v in violations
            ),
        )
    else:
        outcome = GateOutcome.create("PASS")

    material = {
        "schema": ARCHITECTURE_REPORT_SCHEMA,
        "policy_id": policy.policy_id,
        "policy_digest": policy.policy_digest(),
        "outcome": asdict(outcome),
        "checked_files": sorted(checked),
        "violations": [asdict(v) for v in violations],
    }
    return ArchitectureEvaluation(
        schema=ARCHITECTURE_REPORT_SCHEMA,
        policy_id=policy.policy_id,
        policy_digest=policy.policy_digest(),
        outcome=outcome,
        checked_files=tuple(sorted(checked)),
        violations=tuple(violations),
        report_digest=digest(material),
    )


class ArchitectureGate:
    @staticmethod
    def run(req: ArchitectureGateRequest) -> ArchitectureGateResult:
        if req.claim.kind != "architecture":
            raise ValueError("architecture-gate-claim-kind-mismatch")
        root = req.repo.resolve()
        before = capture_state(root, req.repository_id)
        started = _now()
        evaluation = evaluate_architecture(root, req.policy)
        after = capture_state(root, req.repository_id)
        outcome = evaluation.outcome.outcome
        if after.state_id != before.state_id:
            outcome = "MUTATED"
        bindings: tuple[InputBinding, ...] = ()
        if req.policy_path is not None:
            bindings = (bind_path(root, req.policy_path),)
        artifacts = (
            ArtifactRef("architecture-report-digest", "inline:architecture-report", evaluation.report_digest),
        )
        receipt = EvidenceReceipt.create(
            claim_id=req.claim.claim_id,
            subject_ref=req.subject_ref,
            authority_id=req.authority.authority_id,
            state_before_id=before.state_id,
            state_after_id=after.state_id,
            certified_state_id=before.state_id if outcome == "PASS" else None,
            input_bindings=bindings,
            producer_id=req.producer_id,
            run_id=req.run_id,
            gate_id=req.claim.gate_id,
            gate_contract_version=req.claim.gate_contract_version,
            executable_identity=None,
            tool_version=None,
            outcome=outcome,
            started_at=started,
            finished_at=_now(),
            artifacts=artifacts,
        )
        return ArchitectureGateResult(evaluation, receipt)
