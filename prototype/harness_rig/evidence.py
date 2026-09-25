from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .canonical import canonical_json_bytes, digest, file_digest


@dataclass(frozen=True)
class InputBinding:
    kind: str
    locator: str
    digest: str


@dataclass(frozen=True)
class ArtifactRef:
    kind: str
    locator: str
    digest: str


@dataclass(frozen=True)
class EvidenceReceipt:
    schema: str
    receipt_id: str
    claim_id: str
    subject_ref: str
    authority_id: str
    state_before_id: str
    state_after_id: str
    certified_state_id: str | None
    input_bindings: tuple[InputBinding, ...]
    producer_id: str
    run_id: str
    gate_id: str
    gate_contract_version: str
    executable_identity: str | None
    tool_version: str | None
    outcome: str
    started_at: str
    finished_at: str
    artifacts: tuple[ArtifactRef, ...]
    receipt_digest: str

    @classmethod
    def create(cls, **kwargs: Any) -> "EvidenceReceipt":
        base = {
            "schema": "harness-rig/evidence-receipt/experimental-v1",
            **kwargs,
        }
        no_ids = {
            **base,
            "input_bindings": [asdict(x) for x in base.get("input_bindings", ())],
            "artifacts": [asdict(x) for x in base.get("artifacts", ())],
        }
        receipt_id = digest({"receipt": no_ids})
        receipt_digest = digest({"receipt_id": receipt_id, **no_ids})
        return cls(receipt_id=receipt_id, receipt_digest=receipt_digest, **base)

    def recompute_digest(self) -> str:
        material = {
            "schema": self.schema,
            "claim_id": self.claim_id,
            "subject_ref": self.subject_ref,
            "authority_id": self.authority_id,
            "state_before_id": self.state_before_id,
            "state_after_id": self.state_after_id,
            "certified_state_id": self.certified_state_id,
            "input_bindings": [asdict(x) for x in self.input_bindings],
            "producer_id": self.producer_id,
            "run_id": self.run_id,
            "gate_id": self.gate_id,
            "gate_contract_version": self.gate_contract_version,
            "executable_identity": self.executable_identity,
            "tool_version": self.tool_version,
            "outcome": self.outcome,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "artifacts": [asdict(x) for x in self.artifacts],
        }
        rid = digest({"receipt": material})
        if rid != self.receipt_id:
            return "INVALID"
        return digest({"receipt_id": rid, **material})


def bind_path(root: Path, relative_path: str) -> InputBinding:
    path = (root / relative_path).resolve()
    return InputBinding("path", relative_path.replace("\\", "/"), file_digest(path))


def artifact_path(root: Path, relative_path: str, kind: str = "file") -> ArtifactRef:
    path = (root / relative_path).resolve()
    return ArtifactRef(kind, relative_path.replace("\\", "/"), file_digest(path))
