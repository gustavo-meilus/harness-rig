from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .acceptance import evaluate_acceptance
from .assurance import AssurancePlan, AssuranceRequirement
from .authority import AUTHORITY_REF_SCHEMA, AuthorityRef
from .canonical import digest, sha256_bytes
from .evidence import ArtifactRef, EvidenceReceipt
from .spec_engine import SPEC_ENGINE_SCHEMA, SpecArchiveMutation, SpecEngineHealth
from .state import StateIdentity, capture_state


OPEN_SPEC_COMPATIBLE_VERSIONS = frozenset({"1.13.2"})
OPEN_SPEC_PROVIDER = "openspec/v1"
OPEN_SPEC_AUTHORITY_PROFILE = "harness-rig/openspec-authority-profile/v1"
OPEN_SPEC_GATE_CONTRACT = "experimental-v1"
_TASK_ARTIFACT_IDS = frozenset({"tasks"})


class OpenSpecError(RuntimeError):
    pass


class OpenSpecBlocked(OpenSpecError):
    def __init__(self, *reasons: str):
        self.reasons = tuple(reasons) or ("openspec-blocked",)
        super().__init__(";".join(self.reasons))


@dataclass(frozen=True)
class OpenSpecAuthoritySnapshot:
    authority: AuthorityRef
    root_identity: str
    schema_name: str
    change: str
    authority_artifacts: tuple[str, ...]
    referenced_specs: tuple[str, ...]
    affected_specs: tuple[str, ...]
    fingerprint_material_digest: str


@dataclass(frozen=True)
class GuardedArchiveResult:
    outcome: str
    reasons: tuple[str, ...]
    authority_before: AuthorityRef | None
    state_before: StateIdentity
    pre_receipt: EvidenceReceipt | None
    pre_check: EvidenceCheck | None
    mutation: SpecArchiveMutation | None
    authority_after: AuthorityRef | None
    state_after: StateIdentity
    transition_receipt: EvidenceReceipt | None
    post_recheck: EvidenceCheck | None


@dataclass(frozen=True)
class EvidenceCheck:
    outcome: str
    reasons: tuple[str, ...]


@dataclass
class _Inspection:
    health: SpecEngineHealth
    root: dict[str, Any] | None
    status: dict[str, Any] | None
    apply: dict[str, Any] | None
    archive_inputs: dict[str, Any] | None
    artifact_instructions: dict[str, dict[str, Any]]


@dataclass
class _CommandResult:
    returncode: int
    payload: Any | None
    stderr: str


class OpenSpecAdapter:
    """Bounded adapter to OpenSpec 1.13.2 machine-readable CLI surfaces.

    The adapter deliberately does not parse OpenSpec YAML/Markdown semantics or
    reproduce archive logic. It consumes current public JSON contracts and
    hashes provider-native artifacts by reference/content.
    """

    engine = "openspec"

    def __init__(
        self,
        repo: Path,
        *,
        executable: str = "openspec",
        timeout_seconds: float = 20.0,
        compatible_versions: frozenset[str] = OPEN_SPEC_COMPATIBLE_VERSIONS,
    ) -> None:
        self.repo = repo.resolve()
        self.executable = executable
        self.timeout_seconds = timeout_seconds
        self.compatible_versions = compatible_versions

    def _resolved_executable(self) -> str | None:
        candidate = Path(self.executable)
        if candidate.parent != Path(".") or candidate.is_absolute():
            path = candidate.expanduser().resolve()
            return str(path) if path.is_file() else None
        return shutil.which(self.executable)

    def available(self) -> bool:
        return self._resolved_executable() is not None

    def _run(self, *args: str) -> _CommandResult:
        executable = self._resolved_executable()
        if executable is None:
            return _CommandResult(127, None, "openspec executable unavailable")
        try:
            completed = subprocess.run(
                [executable, *args],
                cwd=self.repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                shell=False,
                check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return _CommandResult(126, None, str(exc))
        stdout = completed.stdout.decode("utf-8", "replace").strip()
        payload: Any | None = None
        if stdout:
            try:
                payload = json.loads(stdout)
            except json.JSONDecodeError:
                payload = None
        return _CommandResult(
            completed.returncode,
            payload,
            completed.stderr.decode("utf-8", "replace"),
        )

    def _version(self) -> str | None:
        executable = self._resolved_executable()
        if executable is None:
            return None
        try:
            completed = subprocess.run(
                [executable, "--version"],
                cwd=self.repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                shell=False,
                check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if completed.returncode != 0:
            return None
        text = (completed.stdout + b" " + completed.stderr).decode("utf-8", "replace")
        match = re.search(r"(?<!\d)(\d+\.\d+\.\d+)(?!\d)", text)
        return match.group(1) if match else None

    @staticmethod
    def _diagnostic_reasons(payload: Any, prefix: str) -> list[str]:
        if not isinstance(payload, dict):
            return [f"{prefix}-invalid-json-shape"]
        reasons: list[str] = []
        for diagnostic in payload.get("status", []):
            if not isinstance(diagnostic, dict):
                reasons.append(f"{prefix}-invalid-diagnostic")
                continue
            if diagnostic.get("severity") == "error":
                reasons.append(f"{prefix}:{diagnostic.get('code', 'error')}")
        return reasons

    @staticmethod
    def _validate_text_or_absent(value: Any, field: str, reasons: list[str]) -> None:
        if value is not None and not isinstance(value, str):
            reasons.append(f"invalid-effective-{field}")

    @staticmethod
    def _validate_string_list_or_absent(value: Any, field: str, reasons: list[str]) -> None:
        if value is None:
            return
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            reasons.append(f"invalid-effective-{field}")

    def _root_identity(self, root: Any, reasons: list[str]) -> str | None:
        if not isinstance(root, dict):
            reasons.append("invalid-root-output")
            return None
        source = root.get("source")
        path_text = root.get("path")
        if not isinstance(source, str) or not isinstance(path_text, str) or not path_text:
            reasons.append("invalid-root-output")
            return None
        if source != "nearest":
            reasons.append(f"unsupported-primary-root-source:{source}")
            return None
        observed = Path(path_text).resolve()
        if observed != self.repo:
            reasons.append("openspec-root-repository-mismatch")
            return None
        return "repo-local"

    def _inspect(self, change: str, *, require_tasks_complete: bool) -> _Inspection:
        reasons: list[str] = []
        if not self.available():
            health = SpecEngineHealth(
                SPEC_ENGINE_SCHEMA, self.engine, None, change, None, None,
                False, False, "BLOCKED", ("openspec-unavailable",),
            )
            return _Inspection(health, None, None, None, None, {})

        version = self._version()
        if version is None:
            reasons.append("openspec-version-unreadable")
        elif version not in self.compatible_versions:
            reasons.append(f"openspec-version-unsupported:{version}")

        doctor_result = self._run("doctor", "--json")
        doctor = doctor_result.payload
        reasons.extend(self._diagnostic_reasons(doctor, "doctor"))
        root: dict[str, Any] | None = doctor.get("root") if isinstance(doctor, dict) else None
        if doctor_result.returncode != 0:
            reasons.append("doctor-command-failed")
        if not isinstance(root, dict) or root.get("healthy") is not True:
            reasons.append("openspec-root-unhealthy")
        elif any(
            isinstance(d, dict) and d.get("severity") == "error"
            for d in root.get("status", [])
        ):
            reasons.append("openspec-root-error")
        root_identity = self._root_identity(root, reasons) if isinstance(root, dict) else None

        status_result = self._run("status", "--change", change, "--json")
        status = status_result.payload if isinstance(status_result.payload, dict) else None
        if status_result.returncode != 0 or status is None:
            reasons.append("status-command-failed")
        schema_name = status.get("schemaName") if status else None
        if status is not None:
            if status.get("changeName") != change:
                reasons.append("status-change-mismatch")
            if not isinstance(schema_name, str) or not schema_name:
                reasons.append("invalid-schema-name")
            artifacts = status.get("artifacts")
            if not isinstance(artifacts, list):
                reasons.append("invalid-artifact-graph")
            planning_complete = status.get("isPlanningComplete") is True
            if not planning_complete:
                reasons.append("planning-incomplete")
        else:
            artifacts = []
            planning_complete = False

        validate_result = self._run("validate", change, "--type", "change", "--strict", "--json")
        validation = validate_result.payload if isinstance(validate_result.payload, dict) else None
        if validation is None:
            reasons.append("strict-validation-invalid-output")
        else:
            totals = validation.get("summary", {}).get("totals", {}) if isinstance(validation.get("summary"), dict) else {}
            items = validation.get("items")
            valid_item = (
                isinstance(items, list)
                and any(isinstance(item, dict) and item.get("id") == change and item.get("valid") is True for item in items)
            )
            if validate_result.returncode != 0 or totals.get("failed") != 0 or not valid_item:
                reasons.append("strict-validation-failed")

        apply_result = self._run("instructions", "apply", "--change", change, "--json")
        apply = apply_result.payload if isinstance(apply_result.payload, dict) else None
        if apply_result.returncode != 0 or apply is None:
            reasons.append("apply-instructions-failed")
            tasks_complete = False
        else:
            self._validate_text_or_absent(apply.get("context"), "context", reasons)
            self._validate_string_list_or_absent(apply.get("operationGuidance"), "operation-guidance", reasons)
            if apply.get("state") == "blocked":
                reasons.append("apply-instructions-blocked")
            progress = apply.get("progress")
            tasks_complete = (
                isinstance(progress, dict)
                and isinstance(progress.get("remaining"), int)
                and progress.get("remaining") == 0
            )
            if require_tasks_complete and not tasks_complete:
                reasons.append("tasks-incomplete")

        archive_result = self._run("instructions", "archive", "--change", change, "--json")
        archive_inputs = archive_result.payload if isinstance(archive_result.payload, dict) else None
        if archive_result.returncode != 0 or archive_inputs is None:
            reasons.append("archive-instructions-failed")
        else:
            self._validate_text_or_absent(archive_inputs.get("context"), "archive-context", reasons)
            self._validate_string_list_or_absent(
                archive_inputs.get("operationGuidance"), "archive-operation-guidance", reasons
            )

        artifact_instructions: dict[str, dict[str, Any]] = {}
        if isinstance(artifacts, list):
            for artifact in artifacts:
                if not isinstance(artifact, dict) or not isinstance(artifact.get("id"), str):
                    reasons.append("invalid-artifact-entry")
                    continue
                artifact_id = artifact["id"]
                artifact_status = artifact.get("status")
                if artifact_status not in {"done", "skipped", "ready", "blocked"}:
                    reasons.append(f"invalid-artifact-status:{artifact_id}")
                    continue
                if artifact_status not in {"done", "skipped"}:
                    continue
                instruction_result = self._run(
                    "instructions", artifact_id, "--change", change, "--json"
                )
                instruction = (
                    instruction_result.payload
                    if isinstance(instruction_result.payload, dict)
                    else None
                )
                if instruction_result.returncode != 0 or instruction is None:
                    reasons.append(f"artifact-instructions-failed:{artifact_id}")
                    continue
                if instruction.get("artifactId") != artifact_id:
                    reasons.append(f"artifact-instructions-mismatch:{artifact_id}")
                self._validate_text_or_absent(instruction.get("context"), f"context:{artifact_id}", reasons)
                rules = instruction.get("rules")
                self._validate_string_list_or_absent(rules, f"rules:{artifact_id}", reasons)
                references = instruction.get("references")
                if references is not None and not isinstance(references, list):
                    reasons.append(f"invalid-references:{artifact_id}")
                artifact_instructions[artifact_id] = instruction

        health = SpecEngineHealth(
            schema=SPEC_ENGINE_SCHEMA,
            engine=self.engine,
            version=version,
            change=change,
            root_identity=root_identity,
            schema_name=schema_name if isinstance(schema_name, str) else None,
            planning_complete=planning_complete,
            tasks_complete=tasks_complete,
            outcome="PASS" if not reasons else "BLOCKED",
            reasons=tuple(dict.fromkeys(reasons)),
        )
        return _Inspection(health, root, status, apply, archive_inputs, artifact_instructions)

    def health(self, change: str, *, require_tasks_complete: bool = False) -> SpecEngineHealth:
        return self._inspect(change, require_tasks_complete=require_tasks_complete).health

    def _authority_artifact_ids(self, status: dict[str, Any]) -> tuple[str, ...]:
        result: list[str] = []
        for artifact in status.get("artifacts", []):
            if not isinstance(artifact, dict):
                continue
            artifact_id = artifact.get("id")
            if not isinstance(artifact_id, str) or artifact_id in _TASK_ARTIFACT_IDS:
                continue
            if artifact.get("status") in {"done", "skipped"}:
                result.append(artifact_id)
        return tuple(result)

    def _path_material(self, instruction: dict[str, Any], artifact_id: str) -> list[dict[str, str]]:
        paths = instruction.get("existingOutputPaths")
        if not isinstance(paths, list):
            output = instruction.get("resolvedOutputPath") or instruction.get("outputPath")
            paths = [output] if isinstance(output, str) and output else []
        material: list[dict[str, str]] = []
        for path_text in paths:
            if not isinstance(path_text, str) or not path_text:
                raise OpenSpecBlocked(f"invalid-artifact-path:{artifact_id}")
            path = Path(path_text)
            if not path.is_absolute():
                path = self.repo / path
            path = path.resolve()
            if self.repo not in [path, *path.parents]:
                raise OpenSpecBlocked(f"artifact-path-escape:{artifact_id}")
            if not path.is_file():
                raise OpenSpecBlocked(f"artifact-missing:{artifact_id}")
            material.append({
                "path": path.relative_to(self.repo).as_posix(),
                "digest": sha256_bytes(path.read_bytes()),
            })
        material.sort(key=lambda row: row["path"])
        return material

    @staticmethod
    def _reference_failures(reference: dict[str, Any]) -> list[str]:
        failures: list[str] = []
        for diagnostic in reference.get("status", []):
            if not isinstance(diagnostic, dict):
                failures.append("reference-invalid-diagnostic")
                continue
            code = diagnostic.get("code", "unknown")
            if diagnostic.get("severity") in {"error", "warning"}:
                failures.append(f"reference:{code}")
        return failures

    @staticmethod
    def _semantic_spec_payload(payload: dict[str, Any]) -> dict[str, Any]:
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        return {
            "id": payload.get("id"),
            "title": payload.get("title"),
            "overview": payload.get("overview"),
            "requirementCount": payload.get("requirementCount"),
            "requirements": payload.get("requirements"),
            "metadata": {
                "version": metadata.get("version"),
                "format": metadata.get("format"),
            },
        }

    def _resolved_reference_material(
        self,
        authority_artifacts: tuple[str, ...],
        instructions: dict[str, dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
        required: dict[tuple[str, str], dict[str, Any]] = {}
        for artifact_id in authority_artifacts:
            instruction = instructions.get(artifact_id, {})
            references = instruction.get("references", [])
            if references is None:
                references = []
            for reference in references:
                if not isinstance(reference, dict):
                    raise OpenSpecBlocked(f"invalid-reference-entry:{artifact_id}")
                failures = self._reference_failures(reference)
                if failures:
                    raise OpenSpecBlocked(*failures)
                store_id = reference.get("store_id")
                specs = reference.get("specs")
                if not isinstance(store_id, str) or not store_id:
                    raise OpenSpecBlocked("reference-missing-store-id")
                if not isinstance(specs, list) or not specs:
                    raise OpenSpecBlocked(f"reference-without-specs:{store_id}")
                for spec in specs:
                    if not isinstance(spec, dict) or not isinstance(spec.get("id"), str):
                        raise OpenSpecBlocked(f"invalid-reference-spec:{store_id}")
                    spec_id = spec["id"]
                    required[(store_id, spec_id)] = {"store_id": store_id, "spec_id": spec_id}

        material: list[dict[str, Any]] = []
        names: list[str] = []
        for store_id, spec_id in sorted(required):
            result = self._run("show", spec_id, "--type", "spec", "--store", store_id, "--json")
            if result.returncode != 0 or not isinstance(result.payload, dict):
                raise OpenSpecBlocked(f"reference-show-failed:{store_id}:{spec_id}")
            semantic = self._semantic_spec_payload(result.payload)
            if semantic["id"] != spec_id or not isinstance(semantic["requirements"], list):
                raise OpenSpecBlocked(f"reference-invalid-spec:{store_id}:{spec_id}")
            material.append({"store_id": store_id, "spec": semantic})
            names.append(f"{store_id}:{spec_id}")
        return material, tuple(names)

    def authority_snapshot(self, change: str, *, subject_ref: str) -> OpenSpecAuthoritySnapshot:
        inspection = self._inspect(change, require_tasks_complete=False)
        if inspection.health.outcome != "PASS":
            raise OpenSpecBlocked(*inspection.health.reasons)
        assert inspection.status is not None
        assert inspection.apply is not None
        assert inspection.health.root_identity is not None
        assert inspection.health.schema_name is not None

        authority_artifacts = self._authority_artifact_ids(inspection.status)
        artifact_material: list[dict[str, Any]] = []
        rules_material: dict[str, list[str]] = {}
        skipped: list[str] = []
        graph: list[dict[str, Any]] = []

        for artifact in inspection.status.get("artifacts", []):
            if not isinstance(artifact, dict) or not isinstance(artifact.get("id"), str):
                continue
            artifact_id = artifact["id"]
            graph.append({
                "id": artifact_id,
                "outputPath": artifact.get("outputPath"),
                "requires": artifact.get("requires", []),
                "skipped": artifact.get("status") == "skipped",
            })
            if artifact.get("status") == "skipped":
                skipped.append(artifact_id)

        for artifact_id in authority_artifacts:
            instruction = inspection.artifact_instructions.get(artifact_id)
            if instruction is None:
                raise OpenSpecBlocked(f"missing-artifact-instructions:{artifact_id}")
            if instruction.get("skipped") is True:
                continue
            paths = self._path_material(instruction, artifact_id)
            artifact_material.append({"id": artifact_id, "files": paths})
            rules = instruction.get("rules")
            if rules:
                rules_material[artifact_id] = list(rules)

        reference_material, reference_names = self._resolved_reference_material(
            authority_artifacts, inspection.artifact_instructions
        )

        show_change = self._run("show", change, "--type", "change", "--json")
        if show_change.returncode != 0 or not isinstance(show_change.payload, dict):
            raise OpenSpecBlocked("change-show-failed")
        deltas = show_change.payload.get("deltas")
        if not isinstance(deltas, list):
            raise OpenSpecBlocked("change-show-invalid-deltas")
        affected_specs = tuple(sorted({
            delta.get("spec")
            for delta in deltas
            if isinstance(delta, dict) and isinstance(delta.get("spec"), str)
        }))

        context = inspection.apply.get("context")
        material = {
            "profile": OPEN_SPEC_AUTHORITY_PROFILE,
            "root_identity": inspection.health.root_identity,
            "change": change,
            "schema_name": inspection.health.schema_name,
            "artifact_graph": sorted(graph, key=lambda row: row["id"]),
            "authority_artifacts": sorted(artifact_material, key=lambda row: row["id"]),
            "skipped_artifacts": sorted(skipped),
            "effective_context": context,
            "artifact_rules": rules_material,
            "referenced_specs": reference_material,
        }
        authority_id = digest(material)
        authority = AuthorityRef(
            schema=AUTHORITY_REF_SCHEMA,
            provider=OPEN_SPEC_PROVIDER,
            subject_ref=subject_ref,
            authority_id=authority_id,
        )
        return OpenSpecAuthoritySnapshot(
            authority=authority,
            root_identity=inspection.health.root_identity,
            schema_name=inspection.health.schema_name,
            change=change,
            authority_artifacts=authority_artifacts,
            referenced_specs=reference_names,
            affected_specs=affected_specs,
            fingerprint_material_digest=digest(material),
        )

    def authority_ref(self, change: str, *, subject_ref: str) -> AuthorityRef:
        return self.authority_snapshot(change, subject_ref=subject_ref).authority

    def archive(self, change: str) -> SpecArchiveMutation:
        health = self.health(change, require_tasks_complete=True)
        if health.outcome != "PASS":
            return SpecArchiveMutation(
                self.engine, change, "BLOCKED", health.reasons, None, None
            )

        result = self._run("archive", change, "--yes", "--json")
        payload = result.payload if isinstance(result.payload, dict) else None
        if result.returncode != 0 or payload is None or not isinstance(payload.get("archive"), dict):
            reasons = ["archive-command-failed"]
            reasons.extend(self._diagnostic_reasons(payload, "archive"))
            return SpecArchiveMutation(
                self.engine, change, "BLOCKED", tuple(dict.fromkeys(reasons)), None, None
            )

        archive = payload["archive"]
        reasons: list[str] = []
        if archive.get("change") != change:
            reasons.append("archive-change-mismatch")
        archived_path = archive.get("path")
        if not isinstance(archived_path, str) or not archived_path:
            reasons.append("archive-path-missing")
        else:
            path = Path(archived_path)
            if not path.is_absolute():
                path = self.repo / path
            if not path.resolve().is_dir():
                reasons.append("archive-path-postcondition-failed")

        list_result = self._run("list", "--json")
        if list_result.returncode != 0 or not isinstance(list_result.payload, dict):
            reasons.append("archive-list-postcondition-unreadable")
        else:
            changes = list_result.payload.get("changes")
            if not isinstance(changes, list):
                reasons.append("archive-list-postcondition-invalid")
            elif any(isinstance(item, dict) and item.get("name") == change for item in changes):
                reasons.append("archive-change-still-active")

        return SpecArchiveMutation(
            engine=self.engine,
            change=change,
            outcome="PASS" if not reasons else "BLOCKED",
            reasons=tuple(reasons),
            archived_path=archived_path if isinstance(archived_path, str) else None,
            specs_updated=archive.get("specsUpdated") if isinstance(archive.get("specsUpdated"), bool) else None,
        )

    def post_archive_authority(
        self,
        *,
        change: str,
        subject_ref: str,
        affected_specs: tuple[str, ...],
    ) -> AuthorityRef:
        specs: list[dict[str, Any]] = []
        for spec_id in affected_specs:
            result = self._run("show", spec_id, "--type", "spec", "--json")
            if result.returncode != 0 or not isinstance(result.payload, dict):
                raise OpenSpecBlocked(f"post-archive-spec-unreadable:{spec_id}")
            semantic = self._semantic_spec_payload(result.payload)
            if semantic["id"] != spec_id or not isinstance(semantic["requirements"], list):
                raise OpenSpecBlocked(f"post-archive-spec-invalid:{spec_id}")
            specs.append(semantic)
        material = {
            "profile": OPEN_SPEC_AUTHORITY_PROFILE,
            "phase": "post-archive",
            "root_identity": "repo-local",
            "change": change,
            "affected_specs": specs,
        }
        return AuthorityRef(
            schema=AUTHORITY_REF_SCHEMA,
            provider=OPEN_SPEC_PROVIDER,
            subject_ref=subject_ref,
            authority_id=digest(material),
        )


def _readiness_receipt(
    *,
    authority: AuthorityRef,
    state: StateIdentity,
    health: SpecEngineHealth,
    semantic_review: str,
    run_id: str,
    now: str,
) -> EvidenceReceipt:
    semantic_ok = semantic_review in {"NOT_REQUIRED", "PASS"}
    outcome = "PASS" if health.outcome == "PASS" and semantic_ok else "BLOCKED"
    artifact_digest = digest({
        "openspec_health": asdict(health),
        "semantic_review": semantic_review,
    })
    return EvidenceReceipt.create(
        claim_id="authority.openspec.archive-ready",
        subject_ref=authority.subject_ref,
        authority_id=authority.authority_id,
        state_before_id=state.state_id,
        state_after_id=state.state_id,
        certified_state_id=state.state_id if outcome == "PASS" else None,
        input_bindings=(),
        producer_id="openspec-adapter/1.13.2",
        run_id=run_id,
        gate_id="openspec/readiness",
        gate_contract_version=OPEN_SPEC_GATE_CONTRACT,
        executable_identity=None,
        tool_version=health.version,
        outcome=outcome,
        started_at=now,
        finished_at=now,
        artifacts=(ArtifactRef("openspec-native", f"inline:openspec-health:{artifact_digest}", artifact_digest),),
    )


def _transition_receipt(
    *,
    authority: AuthorityRef,
    state_before: StateIdentity,
    state_after: StateIdentity,
    mutation: SpecArchiveMutation,
    run_id: str,
    now: str,
) -> EvidenceReceipt:
    artifact_digest = digest({"openspec_archive": asdict(mutation)})
    return EvidenceReceipt.create(
        claim_id="authority.openspec.archive-transition",
        subject_ref=authority.subject_ref,
        authority_id=authority.authority_id,
        state_before_id=state_before.state_id,
        state_after_id=state_after.state_id,
        certified_state_id=state_after.state_id if mutation.outcome == "PASS" else None,
        input_bindings=(),
        producer_id="openspec-adapter/1.13.2",
        run_id=f"{run_id}:transition",
        gate_id="openspec/archive",
        gate_contract_version=OPEN_SPEC_GATE_CONTRACT,
        executable_identity=None,
        tool_version="1.13.2",
        outcome="PASS" if mutation.outcome == "PASS" else "BLOCKED",
        started_at=now,
        finished_at=now,
        artifacts=(ArtifactRef("openspec-native", f"inline:openspec-archive:{artifact_digest}", artifact_digest),),
    )


def guarded_archive(
    adapter: OpenSpecAdapter,
    *,
    repository_id: str,
    change: str,
    subject_ref: str,
    run_id: str,
    now: str,
    confirmed: bool = False,
    semantic_review: str = "NOT_REQUIRED",
) -> GuardedArchiveResult:
    state_before = capture_state(adapter.repo, repository_id)
    if not confirmed:
        return GuardedArchiveResult(
            "BLOCKED", ("local-archive-confirmation-required",), None, state_before,
            None, None, None, None, state_before, None, None,
        )
    try:
        snapshot = adapter.authority_snapshot(change, subject_ref=subject_ref)
    except OpenSpecBlocked as exc:
        state_after = capture_state(adapter.repo, repository_id)
        return GuardedArchiveResult(
            "BLOCKED", exc.reasons, None, state_before, None, None, None,
            None, state_after, None, None,
        )

    health = adapter.health(change, require_tasks_complete=True)
    semantic_reasons: tuple[str, ...] = ()
    if semantic_review == "FAIL":
        semantic_reasons = ("semantic-coherence-failed",)
    elif semantic_review not in {"NOT_REQUIRED", "PASS"}:
        semantic_reasons = ("semantic-coherence-unknown",)
    pre_receipt = _readiness_receipt(
        authority=snapshot.authority,
        state=state_before,
        health=health,
        semantic_review=semantic_review,
        run_id=run_id,
        now=now,
    )
    requirement = AssuranceRequirement(
        claim_id="authority.openspec.archive-ready",
        gate_id="openspec/readiness",
        gate_contract_version=OPEN_SPEC_GATE_CONTRACT,
        decision_for="spec_archive",
        require_authorization=False,
    )
    plan = AssurancePlan.single(subject_ref=subject_ref, requirement=requirement)
    pre_verdict = evaluate_acceptance(
        repo=adapter.repo,
        authority=snapshot.authority,
        current_state=state_before,
        plan=plan,
        receipt=pre_receipt,
        grant=None,
        principal="local-operator",
        run_id=run_id,
        now=now,
        trusted_issuers=set(),
        resource=f"openspec:{change}",
        policy_ref="openspec-archive/experimental-v1",
    )
    pre_check = EvidenceCheck("PASS" if pre_verdict.outcome == "ACCEPTED" else "BLOCKED", pre_verdict.reasons)
    if pre_check.outcome != "PASS":
        state_after = capture_state(adapter.repo, repository_id)
        combined_reasons = tuple(dict.fromkeys((*semantic_reasons, *pre_verdict.reasons)))
        return GuardedArchiveResult(
            "BLOCKED", combined_reasons, snapshot.authority, state_before,
            pre_receipt, pre_check, None, None, state_after, None, None,
        )

    mutation = adapter.archive(change)
    state_after = capture_state(adapter.repo, repository_id)
    if mutation.outcome != "PASS":
        transition = _transition_receipt(
            authority=snapshot.authority,
            state_before=state_before,
            state_after=state_after,
            mutation=mutation,
            run_id=run_id,
            now=now,
        )
        return GuardedArchiveResult(
            "BLOCKED", mutation.reasons, snapshot.authority, state_before,
            pre_receipt, pre_check, mutation, None, state_after, transition, None,
        )

    try:
        authority_after = adapter.post_archive_authority(
            change=change,
            subject_ref=subject_ref,
            affected_specs=snapshot.affected_specs,
        )
    except OpenSpecBlocked as exc:
        transition = _transition_receipt(
            authority=snapshot.authority,
            state_before=state_before,
            state_after=state_after,
            mutation=SpecArchiveMutation(
                mutation.engine, mutation.change, "BLOCKED", exc.reasons,
                mutation.archived_path, mutation.specs_updated,
            ),
            run_id=run_id,
            now=now,
        )
        return GuardedArchiveResult(
            "BLOCKED", exc.reasons, snapshot.authority, state_before,
            pre_receipt, pre_check, mutation, None, state_after, transition, None,
        )

    transition = _transition_receipt(
        authority=authority_after,
        state_before=state_before,
        state_after=state_after,
        mutation=mutation,
        run_id=run_id,
        now=now,
    )

    post_recheck = evaluate_acceptance(
        repo=adapter.repo,
        authority=authority_after,
        current_state=state_after,
        plan=plan,
        receipt=pre_receipt,
        grant=None,
        principal="local-operator",
        run_id=run_id,
        now=now,
        trusted_issuers=set(),
        resource=f"openspec:{change}",
        policy_ref="openspec-archive/post-transition-recheck/experimental-v1",
    )
    post_check = EvidenceCheck("PASS" if post_recheck.outcome == "ACCEPTED" else "BLOCKED", post_recheck.reasons)
    if post_check.outcome == "PASS":
        return GuardedArchiveResult(
            "BLOCKED", ("post-archive-stale-preconditions-accepted",), snapshot.authority,
            state_before, pre_receipt, pre_check, mutation, authority_after,
            state_after, transition, post_check,
        )

    return GuardedArchiveResult(
        "PASS", (), snapshot.authority, state_before, pre_receipt, pre_check,
        mutation, authority_after, state_after, transition, post_check,
    )
