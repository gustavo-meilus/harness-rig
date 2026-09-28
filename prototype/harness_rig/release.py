from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable

from .canonical import digest

RELEASE_RECORD_SCHEMA = "harness-rig/release-record/v2"
RELEASE_VERIFICATION_SCHEMA = "harness-rig/release-verification/v2"
REQUIRED_WORKFLOW = ".github/workflows/ci-required.yml"
REQUIRED_JOB = "ci / required"
ATTESTATION_WORKFLOW = ".github/workflows/release-record-attestation.yml"


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
    build_workflow_identity: str
    created_at: str
    artifacts: tuple[ReleaseArtifact, ...]
    repository: str
    repository_id: int | None
    hosted_run_id: int | None
    hosted_run_attempt: int | None
    hosted_job_id: int | None


def _validate_artifact_metadata(path: object, sha256: object, size: object) -> ReleaseArtifact:
    reserved_names = {
        "CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if (not isinstance(path, str) or not path or path in {".", ".."}
            or "/" in path or "\\" in path or not path.isprintable()
            or any(char in '<>:"|?*' for char in path) or path.endswith((" ", "."))
            or path.split(".", 1)[0].upper() in reserved_names):
        raise ReleaseError("release-artifact-path-invalid")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ReleaseError("release-artifact-size-invalid")
    if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ReleaseError("release-artifact-digest-invalid")
    return ReleaseArtifact(path=path, sha256=sha256, size=size)


def parse_release_record(record_bytes: bytes) -> ReleaseRecord:
    data = json.loads(record_bytes.decode("utf-8"))
    if not isinstance(data, dict):
        raise ReleaseError("release-record-invalid")
    if data.get("schema") == "harness-rig/release-record/v1":
        raise ReleaseError("unsupported-release-record-schema")
    if data.get("schema") != RELEASE_RECORD_SCHEMA:
        raise ReleaseError("unsupported-release-record-schema")
    if not isinstance(data.get("record_id"), str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", data["record_id"]):
        raise ReleaseError("release-record-id-invalid")
    if not isinstance(data.get("status"), str) or data["status"] not in {"CANDIDATE", "BLOCKED"}:
        raise ReleaseError("release-record-status-invalid")
    reasons = data.get("reasons", [])
    if not isinstance(reasons, list) or not all(isinstance(reason, str) for reason in reasons):
        raise ReleaseError("release-record-reasons-invalid")
    source_revision = data.get("accepted_source_revision")
    if not isinstance(source_revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", source_revision):
        raise ReleaseError("invalid-source-revision")
    if not isinstance(data.get("repository"), str):
        raise ReleaseError("invalid-repository-identity")
    _validate_repository(data["repository"])
    for field in ("repository_id", "hosted_run_id", "hosted_run_attempt", "hosted_job_id"):
        value = data.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 1):
            raise ReleaseError(f"release-record-{field.replace('_', '-')}-invalid")
    for field in ("build_workflow_identity", "created_at"):
        if not isinstance(data.get(field), str):
            raise ReleaseError(f"release-record-{field.replace('_', '-')}-invalid")
    artifact_data = data.get("artifacts")
    if not isinstance(artifact_data, list):
        raise ReleaseError("release-record-artifacts-invalid")
    artifacts: list[ReleaseArtifact] = []
    for artifact in artifact_data:
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256", "size"}:
            raise ReleaseError("release-record-artifact-invalid")
        artifacts.append(_validate_artifact_metadata(
            artifact["path"], artifact["sha256"], artifact["size"],
        ))
    return ReleaseRecord(
        schema=data["schema"], record_id=data["record_id"], status=data["status"],
        reasons=tuple(reasons), accepted_source_revision=source_revision,
        build_workflow_identity=data["build_workflow_identity"], created_at=data["created_at"],
        artifacts=tuple(artifacts),
        repository=data["repository"], repository_id=data.get("repository_id"),
        hosted_run_id=data.get("hosted_run_id"), hosted_run_attempt=data.get("hosted_run_attempt"),
        hosted_job_id=data.get("hosted_job_id"),
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _record_material(record: ReleaseRecord) -> dict[str, object]:
    return {
        "schema": record.schema,
        "status": record.status,
        "reasons": list(record.reasons),
        "accepted_source_revision": record.accepted_source_revision,
        "build_workflow_identity": record.build_workflow_identity,
        "created_at": record.created_at,
        "artifacts": [asdict(a) for a in record.artifacts],
        "repository": record.repository,
        "repository_id": record.repository_id,
        "hosted_run_id": record.hosted_run_id,
        "hosted_run_attempt": record.hosted_run_attempt,
        "hosted_job_id": record.hosted_job_id,
    }


def _validate_repository(repository: str) -> tuple[str, str]:
    parts = repository.split("/")
    if len(parts) != 2 or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", p) for p in parts):
        raise ReleaseError("invalid-repository-identity")
    return parts[0], parts[1]


def _gh_api_json(endpoint: str) -> dict:
    try:
        proc = subprocess.run(
            ["gh", "api", "--hostname", "github.com", endpoint], capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReleaseError("github-api-unavailable") from exc
    if proc.returncode:
        # Keep CLI output free of any credential or environment details in stderr.
        raise ReleaseError("github-api-unavailable")
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ReleaseError("github-api-invalid-response") from exc
    if not isinstance(result, dict):
        raise ReleaseError("github-api-invalid-response")
    return result


def _hosted_lookup(repository: str, run_id: int, source_revision: str) -> tuple[dict, dict]:
    owner, repo = _validate_repository(repository)
    if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id < 1:
        raise ReleaseError("invalid-hosted-run-id")
    run = _gh_api_json(f"repos/{owner}/{repo}/actions/runs/{run_id}")
    attempt = run.get("run_attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise ReleaseError("hosted-run-attempt-unavailable")
    jobs = _gh_api_json(f"repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100")
    job_list = jobs.get("jobs")
    if not isinstance(job_list, list) or not all(isinstance(job, dict) for job in job_list):
        raise ReleaseError("github-api-invalid-response")
    total_count = jobs.get("total_count")
    if isinstance(total_count, bool) or not isinstance(total_count, int) or total_count != len(job_list):
        raise ReleaseError("hosted-jobs-count-mismatch")
    matches = [job for job in job_list if job.get("name") == REQUIRED_JOB]
    job = matches[0] if len(matches) == 1 else {}
    return run, {"attempt": attempt, "matches": matches, "job": job, "jobs_total": jobs["total_count"]}


def _hosted_reasons(repository: str, source_revision: str, run: dict, job_data: dict,
                    *, expected_repository_id: int | None = None,
                    expected_run_id: int | None = None, expected_attempt: int | None = None,
                    expected_job_id: int | None = None) -> tuple[str, ...]:
    reasons: list[str] = []
    repo_data = run.get("repository") if isinstance(run.get("repository"), dict) else {}
    if str(repo_data.get("full_name", "")).casefold() != repository.casefold():
        reasons.append("hosted-repository-mismatch")
    repo_id = repo_data.get("id")
    if (isinstance(repo_id, bool) or not isinstance(repo_id, int) or
            (expected_repository_id is not None and (isinstance(expected_repository_id, bool) or not isinstance(expected_repository_id, int) or repo_id != expected_repository_id))):
        reasons.append("hosted-repository-id-mismatch")
    run_id = run.get("id")
    if isinstance(run_id, bool) or not isinstance(run_id, int) or (expected_run_id is not None and run_id != expected_run_id):
        reasons.append("hosted-run-id-mismatch")
    if expected_attempt is not None and job_data.get("attempt") != expected_attempt:
        reasons.append("hosted-run-attempt-changed")
    if run.get("head_sha") != source_revision:
        reasons.append("hosted-source-revision-mismatch")
    path = run.get("path", "").split("@", 1)[0] if isinstance(run.get("path"), str) else ""
    if path != REQUIRED_WORKFLOW:
        reasons.append("hosted-workflow-mismatch")
    if run.get("event") != "push":
        reasons.append("hosted-event-mismatch")
    if run.get("head_branch") != "main":
        reasons.append("hosted-branch-mismatch")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        reasons.append("hosted-run-unsuccessful")
    matches = job_data.get("matches", [])
    if len(matches) != 1:
        reasons.append("hosted-required-job-not-unique")
    job = job_data.get("job", {})
    job_id = job.get("id")
    if (isinstance(job_id, bool) or not isinstance(job_id, int) or
            (expected_job_id is not None and (isinstance(expected_job_id, bool) or not isinstance(expected_job_id, int) or job_id != expected_job_id))):
        reasons.append("hosted-required-job-id-mismatch")
    if job.get("run_id") != run_id or job.get("head_sha") != source_revision:
        reasons.append("hosted-required-job-binding-mismatch")
    if job.get("status") != "completed" or job.get("conclusion") != "success":
        reasons.append("hosted-required-job-unsuccessful")
    return tuple(dict.fromkeys(reasons))


def _blocked_hosted_reasons(repository: str, run_id: int | None, source_revision: str) -> tuple[int | None, int | None, int | None, int | None, tuple[str, ...]]:
    if run_id is None:
        return None, None, None, None, ("hosted-run-unavailable",)
    try:
        run, job_data = _hosted_lookup(repository, run_id, source_revision)
    except ReleaseError as exc:
        return None, None, None, None, (str(exc),)
    repo_data = run.get("repository") if isinstance(run.get("repository"), dict) else {}
    job = job_data.get("job", {})
    reasons = _hosted_reasons(repository, source_revision, run, job_data, expected_run_id=run_id)
    return (repo_data.get("id") if isinstance(repo_data.get("id"), int) and not isinstance(repo_data.get("id"), bool) else None,
            run_id, job_data["attempt"], job.get("id") if isinstance(job.get("id"), int) and not isinstance(job.get("id"), bool) else None, reasons)


def build_release_record(*, artifact_paths: Iterable[Path], accepted_source_revision: str,
                         repository: str, hosted_run_id: int | None,
                         build_workflow_identity: str, created_at: str) -> ReleaseRecord:
    _validate_repository(repository)
    if not re.fullmatch(r"[0-9a-fA-F]{40}", accepted_source_revision):
        raise ReleaseError("invalid-source-revision")
    artifacts = tuple(sorted((_validate_artifact_metadata(p.name, sha256_file(p), p.stat().st_size)
                              for p in artifact_paths), key=lambda x: x.path))
    reasons: list[str] = []
    repository_id = run_id = run_attempt = job_id = None
    if hosted_run_id is None:
        hosted_reasons = ("hosted-run-unavailable",)
    else:
        repository_id, run_id, run_attempt, job_id, hosted_reasons = _blocked_hosted_reasons(
            repository, hosted_run_id, accepted_source_revision
        )
    reasons.extend(hosted_reasons)
    if not artifacts:
        reasons.append("release-artifacts-empty")
    status = "CANDIDATE" if not reasons else "BLOCKED"
    record = ReleaseRecord(
        schema=RELEASE_RECORD_SCHEMA, record_id="", status=status, reasons=tuple(reasons),
        accepted_source_revision=accepted_source_revision, build_workflow_identity=build_workflow_identity,
        created_at=created_at, artifacts=artifacts, repository=repository,
        repository_id=repository_id, hosted_run_id=run_id, hosted_run_attempt=run_attempt,
        hosted_job_id=job_id,
    )
    return replace(record, record_id=digest(_record_material(record)))


def _record_integrity_reasons(record: ReleaseRecord) -> list[str]:
    reasons: list[str] = []
    if record.schema != RELEASE_RECORD_SCHEMA:
        reasons.append("unsupported-release-record-schema")
    elif digest(_record_material(record)) != record.record_id:
        reasons.append("release-record-integrity-failure")
    return reasons


def validate_release_candidate(record: ReleaseRecord, expected_repository: str,
                               expected_repository_id: int | None = None) -> dict[str, object]:
    """Validate candidate metadata and live CI before the protected signing job."""
    _validate_repository(expected_repository)
    integrity_reasons = _record_integrity_reasons(record)
    if not isinstance(record.repository, str) or record.repository.casefold() != expected_repository.casefold():
        integrity_reasons.append("hosted-repository-mismatch")
    if expected_repository_id is not None and (
            isinstance(expected_repository_id, bool) or not isinstance(expected_repository_id, int)
            or record.repository_id != expected_repository_id):
        integrity_reasons.append("hosted-repository-id-mismatch")
    hosted_reasons: list[str] = []
    if record.status != "CANDIDATE" or record.reasons:
        hosted_reasons.append("release-record-not-eligible-candidate")
    if not integrity_reasons and not hosted_reasons:
        if None in (record.repository_id, record.hosted_run_id, record.hosted_run_attempt, record.hosted_job_id):
            hosted_reasons.append("hosted-run-binding-unavailable")
        else:
            try:
                run, job_data = _hosted_lookup(expected_repository, record.hosted_run_id, record.accepted_source_revision)
                hosted_reasons.extend(_hosted_reasons(
                    expected_repository, record.accepted_source_revision, run, job_data,
                    expected_repository_id=record.repository_id, expected_run_id=record.hosted_run_id,
                    expected_attempt=record.hosted_run_attempt, expected_job_id=record.hosted_job_id,
                ))
            except ReleaseError as exc:
                hosted_reasons.append(str(exc))
    return {
        "record_integrity": "PASS" if not integrity_reasons else "FAIL",
        "record_reasons": list(dict.fromkeys(integrity_reasons)),
        "hosted_ci": "PASS" if not hosted_reasons and not integrity_reasons else "BLOCKED",
        "hosted_ci_reasons": list(dict.fromkeys(hosted_reasons)),
    }


def _verify_record_attestation(record_bytes: bytes, repository: str) -> tuple[str, str | None]:
    owner, repo = _validate_repository(repository)
    try:
        with tempfile.TemporaryDirectory(prefix="harness-release-attestation-") as temp_dir:
            snapshot = Path(temp_dir) / "release-record.json"
            snapshot.write_bytes(record_bytes)
            proc = subprocess.run(
                ["gh", "attestation", "verify", str(snapshot), "--repo", repository,
                 "--signer-workflow", f"github.com/{owner}/{repo}/{ATTESTATION_WORKFLOW}",
                 "--source-ref", "refs/heads/main"],
                capture_output=True, text=True, timeout=60, check=False,
            )
    except (OSError, subprocess.TimeoutExpired):
        return "BLOCKED", "attestation-verification-unavailable"
    if proc.returncode:
        return "FAIL", "attestation-verification-failed"
    return "PASS", None


def verify_release_record(record_bytes: bytes, base_dir: Path,
                          expected_repository: str) -> dict[str, object]:
    record = parse_release_record(record_bytes)
    _validate_repository(expected_repository)
    integrity_reasons = _record_integrity_reasons(record)
    if not record.artifacts:
        integrity_reasons.append("release-artifacts-empty")
    for artifact in record.artifacts:
        path = base_dir / artifact.path
        if path.name != artifact.path or path.is_symlink():
            integrity_reasons.append(f"release-artifact-path-invalid:{artifact.path}")
        elif not path.is_file():
            integrity_reasons.append(f"release-artifact-missing:{artifact.path}")
        elif path.stat().st_size != artifact.size or sha256_file(path) != artifact.sha256:
            integrity_reasons.append(f"release-artifact-digest-mismatch:{artifact.path}")
    integrity = "PASS" if not integrity_reasons else "FAIL"
    candidate = validate_release_candidate(record, expected_repository)
    hosted_reasons = list(candidate["hosted_ci_reasons"])
    hosted_reasons.extend(candidate["record_reasons"])
    hosted = candidate["hosted_ci"]
    attestation = "BLOCKED"
    attestation_reason = "record-integrity-required-before-attestation-check"
    if integrity == "PASS":
        attestation, attestation_reason = _verify_record_attestation(record_bytes, expected_repository)
    outcome = "PASS" if integrity == hosted == attestation == "PASS" else (
        "FAIL" if integrity == "FAIL" or attestation == "FAIL" else "BLOCKED")
    return {
        "schema": RELEASE_VERIFICATION_SCHEMA, "record_id": record.record_id,
        "artifact_integrity": integrity, "artifact_reasons": integrity_reasons,
        "hosted_ci": hosted, "hosted_ci_reasons": list(dict.fromkeys(hosted_reasons)),
        "attestation": attestation,
        "attestation_reasons": [] if attestation_reason is None else [attestation_reason],
        "outcome": outcome,
    }


def workflow_dispatch_payload(record_bytes: bytes) -> bytes:
    try:
        record_text = record_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReleaseError("release-record-not-utf8") from exc
    payload = json.dumps({"record": record_text}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(payload) > 60_000:
        raise ReleaseError("attestation-dispatch-input-too-large")
    return payload


def dispatch_record_attestation(record_bytes: bytes, repository: str) -> str:
    payload = workflow_dispatch_payload(record_bytes)
    _validate_repository(repository)
    try:
        proc = subprocess.run(
            ["gh", "workflow", "run", Path(ATTESTATION_WORKFLOW).name,
             "--repo", repository, "--ref", "main", "--json"],
            input=payload, capture_output=True, timeout=60, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReleaseError("attestation-dispatch-unavailable") from exc
    if proc.returncode:
        raise ReleaseError("attestation-dispatch-failed")
    return proc.stdout.decode("utf-8", errors="replace").strip()


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
