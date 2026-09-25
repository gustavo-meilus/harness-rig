from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssuranceRequirement:
    claim_id: str
    gate_id: str
    gate_contract_version: str
    decision_for: str
    require_authorization: bool = True


@dataclass(frozen=True)
class AssurancePlan:
    schema: str
    subject_ref: str
    requirement: AssuranceRequirement

    @classmethod
    def single(cls, *, subject_ref: str, requirement: AssuranceRequirement) -> "AssurancePlan":
        return cls(
            schema="harness-rig/assurance-plan/experimental-v1",
            subject_ref=subject_ref,
            requirement=requirement,
        )
