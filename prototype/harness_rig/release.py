from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .canonical import digest

RELEASE_RECORD_SCHEMA = "harness-rig/release-record/v1"


class ReleaseError(ValueError):
    pass


@dataclass(frozen=True)
class ReleaseArtifact:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True)
class ReleaseRecord:
    schema: str
    record_id: str
    status: str
    reasons: tuple[str, ...]
    accepted_source_revision: str
    accepted_repository_verdict: str | None
    build_workflow_identity: str
    created_at: str
    artifacts: tuple[ReleaseArtifact, ...]
    attestation_ref: str | None = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _record_material(*, status: str, reasons: tuple[str, ...], accepted_source_revision: str,
                     accepted_repository_verdict: str | None, build_workflow_identity: str,
                     created_at: str, artifacts: tuple[ReleaseArtifact, ...], attestation_ref: str | None) -> dict[str, object]:
    return {
        "schema": RELEASE_RECORD_SCHEMA,
        "status": status,
        "reasons": list(reasons),
        "accepted_source_revision": accepted_source_revision,
        "accepted_repository_verdict": accepted_repository_verdict,
        "build_workflow_identity": build_workflow_identity,
        "created_at": created_at,
        "artifacts": [asdict(a) for a in artifacts],
        "attestation_ref": attestation_ref,
    }


def build_release_record(*, artifact_paths: Iterable[Path], accepted_source_revision: str,
                         accepted_repository_verdict: str | None, build_workflow_identity: str,
                         created_at: str, attestation_ref: str | None = None) -> ReleaseRecord:
    artifacts = tuple(sorted((ReleaseArtifact(p.name, sha256_file(p), p.stat().st_size) for p in artifact_paths), key=lambda x: x.path))
    reasons: list[str] = []
    if not accepted_repository_verdict:
        reasons.append("accepted-repository-verdict-unavailable")
    if not artifacts:
        reasons.append("release-artifacts-empty")
    status = "PASS" if not reasons else "BLOCKED"
    material = _record_material(
        status=status,
        reasons=tuple(reasons),
        accepted_source_revision=accepted_source_revision,
        accepted_repository_verdict=accepted_repository_verdict,
        build_workflow_identity=build_workflow_identity,
        created_at=created_at,
        artifacts=artifacts,
        attestation_ref=attestation_ref,
    )
    return ReleaseRecord(
        schema=RELEASE_RECORD_SCHEMA,
        record_id=digest(material),
        status=status,
        reasons=tuple(reasons),
        accepted_source_revision=accepted_source_revision,
        accepted_repository_verdict=accepted_repository_verdict,
        build_workflow_identity=build_workflow_identity,
        created_at=created_at,
        artifacts=artifacts,
        attestation_ref=attestation_ref,
    )


def verify_release_record(record: ReleaseRecord, base_dir: Path) -> None:
    material = _record_material(
        status=record.status,
        reasons=record.reasons,
        accepted_source_revision=record.accepted_source_revision,
        accepted_repository_verdict=record.accepted_repository_verdict,
        build_workflow_identity=record.build_workflow_identity,
        created_at=record.created_at,
        artifacts=record.artifacts,
        attestation_ref=record.attestation_ref,
    )
    if digest(material) != record.record_id:
        raise ReleaseError("release-record-integrity-failure")
    for artifact in record.artifacts:
        path = base_dir / artifact.path
        if not path.is_file():
            raise ReleaseError(f"release-artifact-missing:{artifact.path}")
        if path.stat().st_size != artifact.size or sha256_file(path) != artifact.sha256:
            raise ReleaseError(f"release-artifact-digest-mismatch:{artifact.path}")


def write_immutable_release_record(path: Path, record: ReleaseRecord) -> None:
    payload = asdict(record)
    payload["reasons"] = list(record.reasons)
    payload["artifacts"] = [asdict(a) for a in record.artifacts]
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() == data:
            return
        raise ReleaseError("immutable-release-record-already-exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        try:
            os.unlink(temp)
        except FileNotFoundError:
            pass
