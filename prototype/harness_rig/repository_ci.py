"""M7 deterministic repository-CI obligation and required-verdict semantics.

This module is application-level CI evidence, not a Stable core trust contract.
It deliberately models only the information needed to prove that every mandatory
repository obligation ran for the same GitHub event subject and evaluated SHA.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable, Mapping

from .canonical import digest


POLICY_SCHEMA = "harness-rig/repository-ci-policy/v1"
OBLIGATION_SCHEMA = "harness-rig/ci-obligation-artifact/experimental-v1"
RESULT_SCHEMA = "harness-rig/ci-obligation-result/experimental-v1"
VERDICT_SCHEMA = "harness-rig/ci-required-verdict/experimental-v1"

_ALLOWED_EVENTS = frozenset({"pull_request", "push", "workflow_dispatch", "merge_group"})
_ALLOWED_TRUST_MODES = frozenset({"trusted", "untrusted_fork"})
_SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")


class RepositoryCiError(ValueError):
    """Raised when repository-CI evidence is malformed or incompatible."""


@dataclass(frozen=True)
class ObligationSpec:
    obligation_id: str
    producer_id: str
    always_required: bool
    privileged: bool = False


@dataclass(frozen=True)
class RepositoryCiPolicy:
    schema: str
    policy_id: str
    obligations: tuple[ObligationSpec, ...]
    governance_sensitive_paths: tuple[str, ...]

    @classmethod
    def create(
        cls,
        *,
        policy_id: str,
        obligations: Iterable[ObligationSpec],
        governance_sensitive_paths: Iterable[str],
    ) -> "RepositoryCiPolicy":
        obligations_tuple = tuple(obligations)
        sensitive_tuple = tuple(sorted(set(_normalize_path(p) for p in governance_sensitive_paths)))
        if not policy_id:
            raise RepositoryCiError("missing-policy-id")
        ids = [x.obligation_id for x in obligations_tuple]
        producers = [x.producer_id for x in obligations_tuple]
        if not obligations_tuple or len(set(ids)) != len(ids):
            raise RepositoryCiError("invalid-obligation-ids")
        if any(not item for item in ids + producers):
            raise RepositoryCiError("empty-obligation-or-producer")
        if "ordinary" not in ids or "kb-integrity" not in ids or "governance" not in ids:
            raise RepositoryCiError("missing-required-policy-obligation")
        return cls(POLICY_SCHEMA, policy_id, obligations_tuple, sensitive_tuple)

    def digest(self) -> str:
        return digest({"schema": self.schema, "policy_id": self.policy_id,
                       "obligations": [asdict(x) for x in self.obligations],
                       "governance_sensitive_paths": list(self.governance_sensitive_paths)})

    def spec(self, obligation_id: str) -> ObligationSpec:
        for spec in self.obligations:
            if spec.obligation_id == obligation_id:
                return spec
        raise RepositoryCiError(f"unknown-obligation:{obligation_id}")


@dataclass(frozen=True)
class ExpectedResult:
    obligation_id: str
    producer_id: str
    result_key: str
    privileged: bool


@dataclass(frozen=True)
class CiObligationArtifact:
    schema: str
    artifact_id: str
    policy_id: str
    policy_digest: str
    evaluated_sha: str
    event_name: str
    event_subject: str
    trust_mode: str
    changed_paths: tuple[str, ...]
    affected_modules: tuple[str, ...]
    mandatory_obligations: tuple[str, ...]
    expected_results: tuple[ExpectedResult, ...]

    def recompute_id(self) -> str:
        return digest({"artifact": _artifact_material(self)})


@dataclass(frozen=True)
class CiObligationResult:
    schema: str
    result_id: str
    obligation_id: str
    result_key: str
    evaluated_sha: str
    event_name: str
    event_subject: str
    producer_id: str
    outcome: str
    privileged: bool

    def recompute_id(self) -> str:
        return digest({"result": _result_material(self)})


@dataclass(frozen=True)
class CiRequiredVerdict:
    schema: str
    evaluated_sha: str
    event_name: str
    event_subject: str
    outcome: str
    accepted_results: tuple[str, ...]
    reasons: tuple[str, ...]
    verdict_id: str


def _normalize_path(path: str) -> str:
    value = str(path).replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    if not value or value.startswith("/") or ".." in value.split("/"):
        raise RepositoryCiError(f"invalid-repository-path:{path!r}")
    return value.rstrip("/")


def _validate_subject(evaluated_sha: str, event_name: str, event_subject: str, trust_mode: str) -> None:
    if not _SHA_RE.fullmatch(evaluated_sha):
        raise RepositoryCiError("invalid-evaluated-sha")
    if event_name not in _ALLOWED_EVENTS:
        raise RepositoryCiError(f"unsupported-event:{event_name}")
    if not event_subject:
        raise RepositoryCiError("missing-event-subject")
    if trust_mode not in _ALLOWED_TRUST_MODES:
        raise RepositoryCiError(f"unsupported-trust-mode:{trust_mode}")


def _path_matches(path: str, rule: str) -> bool:
    return path == rule or path.startswith(rule + "/") or (rule.endswith("/") and path.startswith(rule))


def _is_governance_sensitive(path: str, policy: RepositoryCiPolicy) -> bool:
    return any(_path_matches(path, rule) for rule in policy.governance_sensitive_paths)


def _affected_modules(paths: tuple[str, ...]) -> tuple[str, ...]:
    modules: set[str] = set()
    for path in paths:
        if path.startswith("prototype/"):
            modules.add("prototype")
        if path.startswith("references/") or path in {"llms.txt", "manifest.jsonl", "AGENTS.md"}:
            modules.add("knowledge")
        if path.startswith("verification/"):
            modules.add("verification")
        if path.startswith(".github/"):
            modules.add("github")
        if path.startswith("governance/"):
            modules.add("governance")
        if not any(path.startswith(prefix) for prefix in ("prototype/", "references/", "verification/", ".github/", "governance/")) and path not in {"llms.txt", "manifest.jsonl", "AGENTS.md"}:
            modules.add("repository")
    return tuple(sorted(modules or {"repository"}))


def _mandatory_obligations(policy: RepositoryCiPolicy, paths: tuple[str, ...]) -> tuple[str, ...]:
    required = {spec.obligation_id for spec in policy.obligations if spec.always_required}
    if any(_is_governance_sensitive(path, policy) for path in paths):
        required.add("governance")
    return tuple(sorted(required))


def _result_key(*, policy_digest: str, obligation_id: str, producer_id: str, evaluated_sha: str,
                event_name: str, event_subject: str) -> str:
    return digest({
        "policy_digest": policy_digest,
        "obligation_id": obligation_id,
        "producer_id": producer_id,
        "evaluated_sha": evaluated_sha,
        "event_name": event_name,
        "event_subject": event_subject,
    })


def resolve_ci_obligations(
    *,
    policy: RepositoryCiPolicy,
    evaluated_sha: str,
    event_name: str,
    event_subject: str,
    trust_mode: str,
    changed_paths: Iterable[str],
) -> CiObligationArtifact:
    _validate_subject(evaluated_sha, event_name, event_subject, trust_mode)
    if policy.schema != POLICY_SCHEMA:
        raise RepositoryCiError(f"unsupported-policy-schema:{policy.schema}")
    paths = tuple(sorted(set(_normalize_path(path) for path in changed_paths)))
    mandatory = _mandatory_obligations(policy, paths)
    policy_digest = policy.digest()
    expected = tuple(
        ExpectedResult(
            obligation_id=obligation_id,
            producer_id=policy.spec(obligation_id).producer_id,
            result_key=_result_key(
                policy_digest=policy_digest,
                obligation_id=obligation_id,
                producer_id=policy.spec(obligation_id).producer_id,
                evaluated_sha=evaluated_sha,
                event_name=event_name,
                event_subject=event_subject,
            ),
            privileged=policy.spec(obligation_id).privileged,
        )
        for obligation_id in mandatory
    )
    material = {
        "schema": OBLIGATION_SCHEMA,
        "policy_id": policy.policy_id,
        "policy_digest": policy_digest,
        "evaluated_sha": evaluated_sha,
        "event_name": event_name,
        "event_subject": event_subject,
        "trust_mode": trust_mode,
        "changed_paths": list(paths),
        "affected_modules": list(_affected_modules(paths)),
        "mandatory_obligations": list(mandatory),
        "expected_results": [asdict(x) for x in expected],
    }
    return CiObligationArtifact(artifact_id=digest({"artifact": material}), **{
        **material,
        "changed_paths": tuple(material["changed_paths"]),
        "affected_modules": tuple(material["affected_modules"]),
        "mandatory_obligations": tuple(material["mandatory_obligations"]),
        "expected_results": expected,
    })


def _artifact_material(artifact: CiObligationArtifact) -> dict[str, object]:
    return {
        "schema": artifact.schema,
        "policy_id": artifact.policy_id,
        "policy_digest": artifact.policy_digest,
        "evaluated_sha": artifact.evaluated_sha,
        "event_name": artifact.event_name,
        "event_subject": artifact.event_subject,
        "trust_mode": artifact.trust_mode,
        "changed_paths": list(artifact.changed_paths),
        "affected_modules": list(artifact.affected_modules),
        "mandatory_obligations": list(artifact.mandatory_obligations),
        "expected_results": [asdict(x) for x in artifact.expected_results],
    }


def create_ci_result(
    *,
    artifact: CiObligationArtifact,
    obligation_id: str,
    producer_id: str,
    outcome: str,
    privileged: bool = False,
) -> CiObligationResult:
    expected = next((x for x in artifact.expected_results if x.obligation_id == obligation_id), None)
    result_key = expected.result_key if expected is not None and expected.producer_id == producer_id else _result_key(
        policy_digest=artifact.policy_digest,
        obligation_id=obligation_id,
        producer_id=producer_id,
        evaluated_sha=artifact.evaluated_sha,
        event_name=artifact.event_name,
        event_subject=artifact.event_subject,
    )
    material = {
        "schema": RESULT_SCHEMA,
        "obligation_id": obligation_id,
        "result_key": result_key,
        "evaluated_sha": artifact.evaluated_sha,
        "event_name": artifact.event_name,
        "event_subject": artifact.event_subject,
        "producer_id": producer_id,
        "outcome": outcome,
        "privileged": bool(privileged),
    }
    return CiObligationResult(result_id=digest({"result": material}), **material)


def _result_material(result: CiObligationResult) -> dict[str, object]:
    return {
        "schema": result.schema,
        "obligation_id": result.obligation_id,
        "result_key": result.result_key,
        "evaluated_sha": result.evaluated_sha,
        "event_name": result.event_name,
        "event_subject": result.event_subject,
        "producer_id": result.producer_id,
        "outcome": result.outcome,
        "privileged": result.privileged,
    }


def validate_ci_required(
    *,
    policy: RepositoryCiPolicy,
    artifact: CiObligationArtifact,
    results: Iterable[CiObligationResult],
) -> CiRequiredVerdict:
    reasons: list[str] = []
    accepted: list[str] = []

    if artifact.schema != OBLIGATION_SCHEMA or artifact.recompute_id() != artifact.artifact_id:
        reasons.append("obligation-artifact-integrity-failure")
    if artifact.policy_id != policy.policy_id or artifact.policy_digest != policy.digest():
        reasons.append("policy-identity-mismatch")

    try:
        expected_artifact = resolve_ci_obligations(
            policy=policy,
            evaluated_sha=artifact.evaluated_sha,
            event_name=artifact.event_name,
            event_subject=artifact.event_subject,
            trust_mode=artifact.trust_mode,
            changed_paths=artifact.changed_paths,
        )
        if artifact.affected_modules != expected_artifact.affected_modules:
            reasons.append("affected-modules-mismatch")
        if artifact.mandatory_obligations != expected_artifact.mandatory_obligations:
            reasons.append("mandatory-obligations-mismatch")
        if artifact.expected_results != expected_artifact.expected_results:
            reasons.append("expected-results-mismatch")
    except RepositoryCiError as exc:
        reasons.append(f"obligation-artifact-invalid:{exc}")

    result_list = tuple(results)
    by_obligation: dict[str, list[CiObligationResult]] = {}
    for result in result_list:
        by_obligation.setdefault(result.obligation_id, []).append(result)
        if result.schema != RESULT_SCHEMA or result.recompute_id() != result.result_id:
            reasons.append(f"result-integrity-failure:{result.obligation_id}")

    mandatory = set(artifact.mandatory_obligations)
    for result in result_list:
        if result.obligation_id not in mandatory:
            reasons.append(f"unexpected-result:{result.obligation_id}")

    expected_by_id: Mapping[str, ExpectedResult] = {x.obligation_id: x for x in artifact.expected_results}
    for obligation_id in artifact.mandatory_obligations:
        matches = by_obligation.get(obligation_id, [])
        if not matches:
            reasons.append(f"missing-result:{obligation_id}")
            continue
        if len(matches) != 1:
            reasons.append(f"duplicate-result:{obligation_id}")
            continue
        result = matches[0]
        expected = expected_by_id.get(obligation_id)
        if expected is None:
            reasons.append(f"missing-expected-result:{obligation_id}")
            continue
        if result.evaluated_sha != artifact.evaluated_sha:
            reasons.append(f"wrong-sha:{obligation_id}")
        if result.event_name != artifact.event_name:
            reasons.append(f"wrong-event:{obligation_id}")
        if result.event_subject != artifact.event_subject:
            reasons.append(f"wrong-subject:{obligation_id}")
        if result.producer_id != expected.producer_id:
            reasons.append(f"wrong-producer:{obligation_id}")
        if result.result_key != expected.result_key:
            reasons.append(f"wrong-result-identity:{obligation_id}")
        if result.outcome != "PASS":
            reasons.append(f"mandatory-result-{result.outcome.lower()}:{obligation_id}")
        if result.privileged != expected.privileged:
            reasons.append(f"privilege-shape-mismatch:{obligation_id}")
        if artifact.trust_mode == "untrusted_fork" and result.privileged:
            reasons.append(f"privileged-result-in-untrusted-fork:{obligation_id}")
        if not any(reason.endswith(f":{obligation_id}") for reason in reasons):
            accepted.append(result.result_id)

    outcome = "PASS" if not reasons else "BLOCKED"
    material = {
        "schema": VERDICT_SCHEMA,
        "evaluated_sha": artifact.evaluated_sha,
        "event_name": artifact.event_name,
        "event_subject": artifact.event_subject,
        "outcome": outcome,
        "accepted_results": sorted(accepted),
        "reasons": reasons,
    }
    return CiRequiredVerdict(
        verdict_id=digest({"verdict": material}),
        **{**material, "accepted_results": tuple(material["accepted_results"]), "reasons": tuple(reasons)},
    )
