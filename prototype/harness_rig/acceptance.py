from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

from .assurance import AssurancePlan
from .authority import AuthorityRef
from .authorization import AuthorizationGrant, validate_grant
from .canonical import digest, file_digest
from .evidence import EvidenceReceipt
from .state import StateIdentity


@dataclass(frozen=True)
class AcceptanceVerdict:
    schema: str
    verdict_id: str
    subject_ref: str
    decision_for: str
    policy_ref: str
    authority_id: str
    state_id: str
    evidence_receipts: tuple[str, ...]
    authorization_grants: tuple[str, ...]
    outcome: str
    reasons: tuple[str, ...]
    verdict_digest: str


def _verdict(
    *,
    subject_ref: str,
    decision_for: str,
    policy_ref: str,
    authority_id: str,
    state_id: str,
    receipts: tuple[EvidenceReceipt, ...],
    grants: tuple[AuthorizationGrant, ...],
    outcome: str,
    reasons: list[str],
) -> AcceptanceVerdict:
    material = {
        "schema": "harness-rig/acceptance-verdict/experimental-v1",
        "subject_ref": subject_ref,
        "decision_for": decision_for,
        "policy_ref": policy_ref,
        "authority_id": authority_id,
        "state_id": state_id,
        "evidence_receipts": [r.receipt_id for r in receipts],
        "authorization_grants": [g.grant_id for g in grants],
        "outcome": outcome,
        "reasons": reasons,
    }
    vid = digest({"verdict": material})
    return AcceptanceVerdict(
        verdict_id=vid,
        verdict_digest=digest({"verdict_id": vid, **material}),
        **{**material,
           "evidence_receipts": tuple(material["evidence_receipts"]),
           "authorization_grants": tuple(material["authorization_grants"]),
           "reasons": tuple(reasons)}
    )


def evaluate_acceptance(
    *,
    repo: Path,
    authority: AuthorityRef,
    current_state: StateIdentity,
    plan: AssurancePlan,
    receipt: EvidenceReceipt | None,
    grant: AuthorizationGrant | None,
    principal: str,
    run_id: str,
    now: str,
    trusted_issuers: set[str],
    resource: str,
    policy_ref: str = "direct-assurance/experimental-v1",
) -> AcceptanceVerdict:
    reasons: list[str] = []
    req = plan.requirement

    if authority.subject_ref != plan.subject_ref:
        reasons.append("authority-subject-mismatch")

    if receipt is None:
        reasons.append("missing-required-receipt")
    else:
        if receipt.recompute_digest() != receipt.receipt_digest:
            reasons.append("receipt-integrity-failure")
        if receipt.claim_id != req.claim_id:
            reasons.append("claim-mismatch")
        if receipt.subject_ref != plan.subject_ref:
            reasons.append("receipt-subject-mismatch")
        if receipt.authority_id != authority.authority_id:
            reasons.append("authority-stale")
        if receipt.certified_state_id != current_state.state_id:
            reasons.append("state-stale-or-not-certified")
        if receipt.gate_id != req.gate_id:
            reasons.append("gate-id-mismatch")
        if receipt.gate_contract_version != req.gate_contract_version:
            reasons.append("gate-contract-mismatch")
        if receipt.run_id != run_id:
            reasons.append("wrong-run-or-replay")
        if receipt.outcome != "PASS":
            reasons.append(f"required-gate-{receipt.outcome.lower()}")

        for binding in receipt.input_bindings:
            if binding.kind == "path":
                path = (repo / binding.locator).resolve()
                if not path.is_file() or file_digest(path) != binding.digest:
                    reasons.append(f"input-binding-stale:{binding.locator}")

        for artifact in receipt.artifacts:
            if artifact.locator.startswith("inline:"):
                continue
            path = (repo / artifact.locator).resolve()
            if not path.is_file() or file_digest(path) != artifact.digest:
                reasons.append(f"artifact-integrity-failure:{artifact.locator}")

    grant_valid = None
    if req.require_authorization:
        grant_valid = validate_grant(
            grant,
            principal=principal,
            action=req.decision_for,
            resource=resource,
            authority_id=authority.authority_id,
            state_id=current_state.state_id,
            subject_ref=plan.subject_ref,
            now=now,
            trusted_issuers=trusted_issuers,
        )
        if grant_valid.outcome != "VALID":
            reasons.append(f"authorization-{grant_valid.outcome.lower()}:{grant_valid.reason}")

    if reasons:
        # A proven bad gate/receipt is REWORK; inability/missing authorization/evidence is BLOCKED.
        deterministic_false = any(
            r.startswith(("required-gate-fail", "artifact-integrity-failure", "receipt-integrity-failure"))
            for r in reasons
        )
        outcome = "REWORK" if deterministic_false else "BLOCKED"
    else:
        outcome = "ACCEPTED"

    return _verdict(
        subject_ref=plan.subject_ref,
        decision_for=req.decision_for,
        policy_ref=policy_ref,
        authority_id=authority.authority_id,
        state_id=current_state.state_id,
        receipts=tuple([receipt] if receipt is not None else []),
        grants=tuple([grant] if grant is not None else []),
        outcome=outcome,
        reasons=reasons,
    )


def verdict_applicable_to(verdict: AcceptanceVerdict, decision_for: str) -> bool:
    return verdict.outcome == "ACCEPTED" and verdict.decision_for == decision_for
