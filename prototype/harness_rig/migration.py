from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .canonical import digest

MIGRATION_STATE_SCHEMA = "harness-rig/migration-state/v1"
HISTORY_MAP_SCHEMA = "harness-rig/history-map/v1"
MIGRATION_TARGET = "r8.10"
SUPPORTED_UPGRADE_FROM = frozenset({"r8.9"})


class MigrationError(ValueError):
    pass


@dataclass(frozen=True)
class MigrationAssessment:
    outcome: str
    reasons: tuple[str, ...]
    runtime_schema_complete: bool
    history_qualification: str
    legacy_markers: tuple[str, ...]
    duplicate_hooks: tuple[str, ...]


@dataclass(frozen=True)
class MigrationState:
    schema: str
    state_id: str
    from_revision: str
    to_revision: str
    phase: str
    applied_steps: tuple[str, ...]
    history_qualification: str
    rollback_available: bool


LEGACY_MARKERS = (
    ".aiboarding/state.json",
    ".orchestration/tacticswitch-state.json",
    ".harness-rig/state.json",
)
HOOK_MANIFESTS = (
    ".aiboarding/hooks.json",
    ".orchestration/hooks.json",
    ".harness-rig/hooks.json",
)


def _hook_ids(path: Path) -> tuple[str, ...]:
    if not path.exists():
        return ()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError(f"hook-manifest-malformed:{path.as_posix()}") from exc
    hooks = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, list) or not all(isinstance(x, str) and x for x in hooks):
        raise MigrationError(f"hook-manifest-invalid:{path.as_posix()}")
    return tuple(hooks)


def assess_migration(repo: Path) -> MigrationAssessment:
    root = repo.resolve()
    legacy = tuple(rel for rel in LEGACY_MARKERS if (root / rel).exists())
    seen: dict[str, list[str]] = {}
    for rel in HOOK_MANIFESTS:
        for hook_id in _hook_ids(root / rel):
            seen.setdefault(hook_id, []).append(rel)
    duplicates = tuple(sorted(h for h, owners in seen.items() if len(owners) > 1))
    state_path = root / ".harness-rig" / "migration-state.json"
    reasons: list[str] = []
    if legacy:
        reasons.append("legacy-state-present")
    if duplicates:
        reasons.append("duplicate-hook-ownership")
    if state_path.exists():
        state = load_migration_state(state_path)
        if state.phase == "APPLYING":
            reasons.append("interrupted-migration")
        if state.phase == "COMPLETE" and legacy:
            reasons.append("mixed-old-new-state")
    return MigrationAssessment(
        outcome="PASS" if not reasons else "BLOCKED",
        reasons=tuple(reasons),
        runtime_schema_complete=not reasons,
        history_qualification="PENDING_M11",
        legacy_markers=legacy,
        duplicate_hooks=duplicates,
    )


def _state_material(from_revision: str, to_revision: str, phase: str,
                    applied_steps: tuple[str, ...], history_qualification: str,
                    rollback_available: bool) -> dict[str, Any]:
    return {
        "schema": MIGRATION_STATE_SCHEMA,
        "from_revision": from_revision,
        "to_revision": to_revision,
        "phase": phase,
        "applied_steps": list(applied_steps),
        "history_qualification": history_qualification,
        "rollback_available": rollback_available,
    }


def _make_state(from_revision: str, to_revision: str, phase: str,
                applied_steps: tuple[str, ...], history_qualification: str,
                rollback_available: bool) -> MigrationState:
    material = _state_material(from_revision, to_revision, phase, applied_steps, history_qualification, rollback_available)
    return MigrationState(
        schema=MIGRATION_STATE_SCHEMA,
        state_id=digest(material),
        from_revision=from_revision,
        to_revision=to_revision,
        phase=phase,
        applied_steps=applied_steps,
        history_qualification=history_qualification,
        rollback_available=rollback_available,
    )


def load_migration_state(path: Path) -> MigrationState:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError("migration-state-malformed") from exc
    required = {"schema", "state_id", "from_revision", "to_revision", "phase", "applied_steps", "history_qualification", "rollback_available"}
    if not isinstance(data, dict) or set(data) != required:
        raise MigrationError("migration-state-invalid-fields")
    if data["schema"] != MIGRATION_STATE_SCHEMA:
        raise MigrationError(f"migration-state-unsupported-schema:{data['schema']}")
    if data["phase"] not in {"APPLYING", "COMPLETE", "ROLLED_BACK"}:
        raise MigrationError("migration-state-invalid-phase")
    if not isinstance(data["applied_steps"], list) or not all(isinstance(x, str) for x in data["applied_steps"]):
        raise MigrationError("migration-state-invalid-steps")
    state = MigrationState(
        schema=data["schema"], state_id=data["state_id"], from_revision=data["from_revision"], to_revision=data["to_revision"],
        phase=data["phase"], applied_steps=tuple(data["applied_steps"]), history_qualification=data["history_qualification"],
        rollback_available=data["rollback_available"],
    )
    expected = _make_state(state.from_revision, state.to_revision, state.phase, state.applied_steps,
                           state.history_qualification, state.rollback_available)
    if expected.state_id != state.state_id:
        raise MigrationError("migration-state-integrity-failure")
    return state


def _atomic_write(path: Path, data: bytes) -> None:
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


def write_migration_state(path: Path, state: MigrationState) -> None:
    payload = asdict(state)
    payload["applied_steps"] = list(state.applied_steps)
    _atomic_write(path, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def apply_migration(repo: Path, *, from_revision: str = "r8.9", to_revision: str = MIGRATION_TARGET,
                    simulate_interrupt_after_journal: bool = False) -> MigrationState:
    if to_revision != MIGRATION_TARGET:
        raise MigrationError(f"unsupported-migration-target:{to_revision}")
    if from_revision not in SUPPORTED_UPGRADE_FROM:
        raise MigrationError(f"unsupported-migration-source:{from_revision}")
    root = repo.resolve()
    state_path = root / ".harness-rig" / "migration-state.json"
    backup_path = root / ".harness-rig" / "migration-state.previous.json"
    assessment = assess_migration(root)
    if assessment.reasons and assessment.reasons != ("interrupted-migration",):
        raise MigrationError("migration-precondition-blocked:" + ",".join(assessment.reasons))
    if state_path.exists():
        current = load_migration_state(state_path)
        if current.phase == "APPLYING":
            raise MigrationError("interrupted-migration")
        if current.phase == "COMPLETE" and current.to_revision == to_revision:
            return current
        _atomic_write(backup_path, state_path.read_bytes())
    applying = _make_state(from_revision, to_revision, "APPLYING", (), "PENDING_M11", backup_path.exists())
    write_migration_state(state_path, applying)
    if simulate_interrupt_after_journal:
        return applying
    final_assessment = assess_migration(root)
    blocking = tuple(x for x in final_assessment.reasons if x != "interrupted-migration")
    if blocking:
        raise MigrationError("migration-postcondition-blocked:" + ",".join(blocking))
    steps = (
        "source-dispositions-recorded",
        "runtime-ownership-converged",
        "duplicate-hooks-absent",
        "generated-surfaces-single-source",
        "history-qualification-deferred-to-m11",
    )
    complete = _make_state(from_revision, to_revision, "COMPLETE", steps, "PENDING_M11", backup_path.exists())
    write_migration_state(state_path, complete)
    return complete


def rollback_migration(repo: Path) -> MigrationState:
    root = repo.resolve()
    state_path = root / ".harness-rig" / "migration-state.json"
    backup_path = root / ".harness-rig" / "migration-state.previous.json"
    if not state_path.exists():
        raise MigrationError("migration-state-missing")
    current = load_migration_state(state_path)
    if current.phase == "APPLYING":
        raise MigrationError("rollback-from-interrupted-requires-manual-recovery")
    if backup_path.exists():
        previous = load_migration_state(backup_path)
        _atomic_write(state_path, backup_path.read_bytes())
        backup_path.unlink()
        return previous
    rolled = _make_state(current.to_revision, current.from_revision, "ROLLED_BACK", (), "PENDING_M11", False)
    write_migration_state(state_path, rolled)
    return rolled


def lookup_rewritten_commit(mapping_file: Path, old_commit: str) -> str:
    try:
        data = json.loads(mapping_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError("history-map-unreadable") from exc
    if not isinstance(data, dict) or data.get("schema") != HISTORY_MAP_SCHEMA:
        raise MigrationError("history-map-unsupported-schema")
    mappings = data.get("mappings")
    if not isinstance(mappings, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in mappings.items()):
        raise MigrationError("history-map-invalid")
    if old_commit not in mappings:
        raise MigrationError("history-map-commit-not-found")
    return mappings[old_commit]
