from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from harness_rig.authority import DirectAuthorityProvider
from harness_rig.cli import main as cli_main
import harness_rig.openspec as openspec_module
from harness_rig.openspec import OpenSpecAdapter, OpenSpecBlocked, guarded_archive


CHANGE = "add-api-limit"
NOW = "2026-09-25T12:00:00Z"


FAKE_OPEN_SPEC = r'''#!/usr/bin/env python3
import json
import shutil
import sys
from pathlib import Path

STATE_PATH = Path(__STATE_PATH__)

def load():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

def save(state):
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

def emit(payload, code=0):
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(code)

def arg_value(args, flag):
    try:
        return args[args.index(flag) + 1]
    except (ValueError, IndexError):
        return None

state = load()
root = Path(state["root"])
args = sys.argv[1:]
if args == ["--version"]:
    print("OpenSpec " + state.get("version", "1.13.2"))
    raise SystemExit(0)

if not args:
    raise SystemExit(1)

if args[0] == "doctor":
    payload = {
        "root": {
            "path": str(root),
            "source": state.get("root_source", "nearest"),
            "healthy": state.get("doctor_healthy", True),
            "status": state.get("doctor_root_status", []),
        },
        "store": None,
        "references": [],
        "status": state.get("doctor_status", []),
    }
    emit(payload, state.get("doctor_exit", 0))

if args[0] == "status":
    change = arg_value(args, "--change")
    if not state.get("active", True) or change != state["change"]:
        emit({"status": [{"severity": "error", "code": "change_not_found", "message": "missing"}]}, 1)
    artifacts = state["artifacts"]
    planning_complete = all(a["status"] in {"done", "skipped"} for a in artifacts)
    emit({
        "changeName": change,
        "schemaName": state.get("schema", "spec-driven"),
        "changeRoot": str(root / "openspec" / "changes" / change),
        "artifactPaths": {a["id"]: {"outputPath": a.get("outputPath"), "resolvedOutputPath": a.get("outputPath"), "existingOutputPaths": a.get("paths", [])} for a in artifacts},
        "nextSteps": [],
        "actionContext": {"mode": "repo-local", "sourceOfTruth": "repo", "planningArtifacts": [a["id"] for a in artifacts], "linkedContext": [], "allowedEditRoots": [str(root)], "requiresAffectedAreaSelection": False, "constraints": []},
        "isPlanningComplete": planning_complete,
        "isComplete": planning_complete,
        "applyRequires": ["tasks"],
        "artifacts": [{"id": a["id"], "outputPath": a.get("outputPath"), "status": a["status"], "requires": a.get("requires", [])} for a in artifacts],
        "root": {"path": str(root), "source": state.get("root_source", "nearest")},
    })

if args[0] == "validate":
    valid = state.get("validate_valid", True)
    emit({
        "items": [{"id": state["change"], "type": "change", "valid": valid, "issues": [] if valid else [{"level": "ERROR", "path": "proposal.md", "message": "invalid"}]}],
        "summary": {"totals": {"items": 1, "passed": 1 if valid else 0, "failed": 0 if valid else 1}, "byType": {"change": {"items": 1, "passed": 1 if valid else 0, "failed": 0 if valid else 1}}},
        "version": "1.0",
        "root": {"path": str(root), "source": state.get("root_source", "nearest")},
    }, 0 if valid else 1)

if args[0] == "instructions":
    kind = args[1]
    change = arg_value(args, "--change")
    if not state.get("active", True) or change != state["change"]:
        emit({"status": [{"severity": "error", "code": "change_not_found", "message": "missing"}]}, 1)
    if kind == "apply":
        tasks_path = root / "openspec" / "changes" / change / "tasks.md"
        total = 0
        complete = 0
        if tasks_path.is_file():
            for line in tasks_path.read_text(encoding="utf-8").splitlines():
                if "- [" in line:
                    total += 1
                    if "- [x]" in line.lower():
                        complete += 1
        remaining = total - complete
        emit({
            "changeName": change,
            "changeDir": str(root / "openspec" / "changes" / change),
            "schemaName": state.get("schema", "spec-driven"),
            "contextFiles": {a["id"]: a.get("paths", []) for a in state["artifacts"] if a["status"] == "done"},
            "progress": {"total": total, "complete": complete, "remaining": remaining},
            "tasks": [],
            "state": "all_done" if remaining == 0 else "ready",
            "instruction": "Apply the change.",
            "context": state.get("context"),
            "operationGuidance": state.get("apply_guidance"),
            "root": {"path": str(root), "source": state.get("root_source", "nearest")},
        })
    if kind == "archive":
        emit({
            "changeName": change,
            "context": state.get("context"),
            "operationGuidance": state.get("archive_guidance"),
            "root": {"path": str(root), "source": state.get("root_source", "nearest")},
        })
    artifact = next((a for a in state["artifacts"] if a["id"] == kind), None)
    if artifact is None:
        emit({"status": [{"severity": "error", "code": "artifact_not_found", "message": "missing"}]}, 1)
    emit({
        "changeName": change,
        "artifactId": kind,
        "schemaName": state.get("schema", "spec-driven"),
        "changeDir": str(root / "openspec" / "changes" / change),
        "outputPath": artifact.get("outputPath"),
        "resolvedOutputPath": artifact.get("outputPath"),
        "existingOutputPaths": artifact.get("paths", []),
        "description": kind,
        "instruction": "Write artifact",
        "context": state.get("context"),
        "rules": state.get("rules", {}).get(kind),
        "references": state.get("references", {}).get(kind),
        "skipped": True if artifact["status"] == "skipped" else None,
        "template": "",
        "dependencies": [],
        "unlocks": [],
        "root": {"path": str(root), "source": state.get("root_source", "nearest")},
    })

if args[0] == "show":
    item = args[1]
    item_type = arg_value(args, "--type")
    if item_type == "change":
        if not state.get("active", True) or item != state["change"]:
            emit({"status": [{"severity": "error", "code": "change_not_found", "message": "missing"}]}, 1)
        emit({
            "id": item,
            "title": "Fixture change",
            "deltaCount": len(state.get("deltas", [])),
            "deltas": state.get("deltas", []),
            "root": {"path": str(root), "source": state.get("root_source", "nearest")},
        })
    if item_type == "spec":
        store = arg_value(args, "--store")
        if store:
            payload = state.get("referenced_specs", {}).get(store, {}).get(item)
        else:
            payload = state.get("main_specs", {}).get(item)
        if payload is None:
            emit({"status": [{"severity": "error", "code": "unknown_spec", "message": "missing"}]}, 1)
        output = dict(payload)
        output["root"] = {"path": str(root), "source": "store" if store else state.get("root_source", "nearest"), **({"store_id": store} if store else {})}
        emit(output)

if args[0] == "list":
    changes = [{"name": state["change"], "completedTasks": 1, "totalTasks": 1, "lastModified": "now", "status": "complete"}] if state.get("active", True) else []
    emit({"changes": changes, "root": {"path": str(root), "source": state.get("root_source", "nearest")}})

if args[0] == "archive":
    mode = state.get("archive_mode", "success")
    change = args[1]
    if mode == "partial-fail":
        (root / "partial-archive-mutation.txt").write_text("partial\n", encoding="utf-8")
        emit({"archive": None, "root": {"path": str(root), "source": "nearest"}, "status": [{"severity": "error", "code": "archive_error", "message": "partial failure"}]}, 1)
    if mode == "mismatch":
        emit({"archive": {"change": change, "archivedAs": "2026-09-25-" + change, "path": str(root / "missing-archive"), "specsUpdated": True}, "root": {"path": str(root), "source": "nearest"}})
    source = root / "openspec" / "changes" / change
    target = root / "openspec" / "changes" / "archive" / ("2026-09-25-" + change)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(source), str(target))
    state["active"] = False
    state["main_specs"] = state.get("post_specs", state.get("main_specs", {}))
    save(state)
    emit({"archive": {"change": change, "archivedAs": "2026-09-25-" + change, "path": str(target), "specsUpdated": bool(state.get("deltas"))}, "root": {"path": str(root), "source": "nearest"}})

emit({"status": [{"severity": "error", "code": "unsupported", "message": "unsupported"}]}, 1)
'''


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def default_spec(text: str = "The API SHALL rate limit requests.") -> dict:
    return {
        "id": "api",
        "title": "api",
        "overview": "API behavior",
        "requirementCount": 1,
        "requirements": [{"text": text, "scenarios": [{"rawText": "- **WHEN** request\n- **THEN** limited"}]}],
        "metadata": {"version": "1.0.0", "format": "openspec"},
    }



class FixtureAdapter(OpenSpecAdapter):
    """Exercise the real adapter logic without process-startup cost in unit tests."""

    def __init__(self, fixture: "OpenSpecFixture") -> None:
        super().__init__(fixture.root, executable="in-process-openspec")
        self.fixture = fixture

    def available(self) -> bool:
        return True

    def _version(self) -> str | None:
        return self.fixture.state.get("version")

    def _result(self, code: int, payload=None, stderr: str = ""):
        return openspec_module._CommandResult(code, payload, stderr)

    def _run(self, *args: str):
        state = self.fixture.state
        root = self.fixture.root
        args = list(args)
        if not args:
            return self._result(1)
        if args[0] == "doctor":
            return self._result(state.get("doctor_exit", 0), {
                "root": {
                    "path": str(root),
                    "source": state.get("root_source", "nearest"),
                    "healthy": state.get("doctor_healthy", True),
                    "status": state.get("doctor_root_status", []),
                },
                "store": None,
                "references": [],
                "status": state.get("doctor_status", []),
            })
        if args[0] == "status":
            if not state.get("active", True):
                return self._result(1, {"status": [{"severity": "error", "code": "change_not_found"}]})
            artifacts = state["artifacts"]
            complete = all(a["status"] in {"done", "skipped"} for a in artifacts)
            return self._result(0, {
                "changeName": state["change"],
                "schemaName": state.get("schema", "spec-driven"),
                "isPlanningComplete": complete,
                "isComplete": complete,
                "artifacts": [{"id": a["id"], "outputPath": a.get("outputPath"), "status": a["status"], "requires": a.get("requires", [])} for a in artifacts],
                "root": {"path": str(root), "source": state.get("root_source", "nearest")},
            })
        if args[0] == "validate":
            valid = state.get("validate_valid", True)
            return self._result(0 if valid else 1, {
                "items": [{"id": state["change"], "type": "change", "valid": valid, "issues": []}],
                "summary": {"totals": {"items": 1, "passed": 1 if valid else 0, "failed": 0 if valid else 1}},
                "version": "1.0",
                "root": {"path": str(root), "source": state.get("root_source", "nearest")},
            })
        if args[0] == "instructions":
            kind = args[1]
            if not state.get("active", True):
                return self._result(1, {"status": [{"severity": "error", "code": "change_not_found"}]})
            if kind == "apply":
                tasks_path = root / "openspec" / "changes" / state["change"] / "tasks.md"
                total = complete = 0
                if tasks_path.is_file():
                    for line in tasks_path.read_text(encoding="utf-8").splitlines():
                        if "- [" in line:
                            total += 1
                            if "- [x]" in line.lower():
                                complete += 1
                return self._result(0, {
                    "changeName": state["change"],
                    "changeDir": str(root / "openspec" / "changes" / state["change"]),
                    "schemaName": state.get("schema", "spec-driven"),
                    "contextFiles": {a["id"]: a.get("paths", []) for a in state["artifacts"] if a["status"] == "done"},
                    "progress": {"total": total, "complete": complete, "remaining": total - complete},
                    "tasks": [],
                    "state": "all_done" if total == complete else "ready",
                    "instruction": "Apply the change.",
                    "context": state.get("context"),
                    "operationGuidance": state.get("apply_guidance"),
                    "root": {"path": str(root), "source": state.get("root_source", "nearest")},
                })
            if kind == "archive":
                return self._result(0, {
                    "changeName": state["change"],
                    "context": state.get("context"),
                    "operationGuidance": state.get("archive_guidance"),
                    "root": {"path": str(root), "source": state.get("root_source", "nearest")},
                })
            artifact = next((a for a in state["artifacts"] if a["id"] == kind), None)
            if artifact is None:
                return self._result(1, {"status": [{"severity": "error", "code": "artifact_not_found"}]})
            return self._result(0, {
                "changeName": state["change"],
                "artifactId": kind,
                "schemaName": state.get("schema", "spec-driven"),
                "changeDir": str(root / "openspec" / "changes" / state["change"]),
                "outputPath": artifact.get("outputPath"),
                "resolvedOutputPath": artifact.get("outputPath"),
                "existingOutputPaths": artifact.get("paths", []),
                "description": kind,
                "instruction": "Write artifact",
                "context": state.get("context"),
                "rules": state.get("rules", {}).get(kind),
                "references": state.get("references", {}).get(kind),
                "skipped": True if artifact["status"] == "skipped" else None,
                "template": "",
                "dependencies": [],
                "unlocks": [],
                "root": {"path": str(root), "source": state.get("root_source", "nearest")},
            })
        if args[0] == "show":
            item = args[1]
            item_type = args[args.index("--type") + 1]
            if item_type == "change":
                if not state.get("active", True):
                    return self._result(1, {"status": [{"severity": "error", "code": "change_not_found"}]})
                return self._result(0, {"id": item, "title": "Fixture change", "deltaCount": len(state.get("deltas", [])), "deltas": state.get("deltas", []), "root": {"path": str(root), "source": state.get("root_source", "nearest")}})
            store = args[args.index("--store") + 1] if "--store" in args else None
            payload = state.get("referenced_specs", {}).get(store, {}).get(item) if store else state.get("main_specs", {}).get(item)
            if payload is None:
                return self._result(1, {"status": [{"severity": "error", "code": "unknown_spec"}]})
            return self._result(0, dict(payload))
        if args[0] == "list":
            changes = [{"name": state["change"]}] if state.get("active", True) else []
            return self._result(0, {"changes": changes, "root": {"path": str(root), "source": state.get("root_source", "nearest")}})
        if args[0] == "archive":
            mode = state.get("archive_mode", "success")
            if mode == "partial-fail":
                (root / "partial-archive-mutation.txt").write_text("partial\n", encoding="utf-8")
                return self._result(1, {"archive": None, "status": [{"severity": "error", "code": "archive_error"}]})
            if mode == "mismatch":
                return self._result(0, {"archive": {"change": state["change"], "archivedAs": "2026-09-25-" + state["change"], "path": str(root / "missing-archive"), "specsUpdated": True}})
            source = root / "openspec" / "changes" / state["change"]
            target = root / "openspec" / "changes" / "archive" / ("2026-09-25-" + state["change"])
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                import shutil
                shutil.rmtree(target)
            import shutil
            shutil.move(str(source), str(target))
            state["active"] = False
            state["main_specs"] = state.get("post_specs", state.get("main_specs", {}))
            return self._result(0, {"archive": {"change": state["change"], "archivedAs": "2026-09-25-" + state["change"], "path": str(target), "specsUpdated": bool(state.get("deltas"))}})
        return self._result(1, {"status": [{"severity": "error", "code": "unsupported"}]})


class OpenSpecFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="hr-m6-")
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.state_path = Path(self.tmp.name) / "openspec-state.json"
        self.exe = Path(self.tmp.name) / "openspec"
        run(self.root, "init", "-q")
        run(self.root, "config", "user.email", "test@example.invalid")
        run(self.root, "config", "user.name", "Harness Rig Test")
        change = self.root / "openspec" / "changes" / CHANGE
        (change / "specs" / "api").mkdir(parents=True)
        (self.root / "openspec" / "specs" / "api").mkdir(parents=True)
        (self.root / "openspec" / "config.yaml").write_text("schema: spec-driven\ncontext: fixture\n", encoding="utf-8")
        (change / ".openspec.yaml").write_text("schema: spec-driven\ncreated: 2026-09-25\n", encoding="utf-8")
        (change / "proposal.md").write_text("# Proposal\nAdd rate limiting.\n", encoding="utf-8")
        (change / "specs" / "api" / "spec.md").write_text("## ADDED Requirements\nRate limit.\n", encoding="utf-8")
        (change / "design.md").write_text("# Design\nUse token buckets.\n", encoding="utf-8")
        (change / "tasks.md").write_text("# Tasks\n- [x] Implement\n", encoding="utf-8")
        (self.root / "openspec" / "specs" / "api" / "spec.md").write_text("# API\nOld behavior.\n", encoding="utf-8")
        (self.root / "authority.txt").write_text("direct intent\n", encoding="utf-8")
        run(self.root, "add", ".")
        run(self.root, "commit", "-qm", "fixture")

        self.state = {
            "root": str(self.root),
            "root_source": "nearest",
            "change": CHANGE,
            "version": "1.13.2",
            "doctor_healthy": True,
            "schema": "spec-driven",
            "active": True,
            "validate_valid": True,
            "context": "Use repository conventions.",
            "apply_guidance": ["Apply conservatively."],
            "archive_guidance": ["Preserve history."],
            "artifacts": [
                {"id": "proposal", "outputPath": f"openspec/changes/{CHANGE}/proposal.md", "paths": [str(change / "proposal.md")], "status": "done", "requires": []},
                {"id": "specs", "outputPath": f"openspec/changes/{CHANGE}/specs/**/*.md", "paths": [str(change / "specs" / "api" / "spec.md")], "status": "done", "requires": ["proposal"]},
                {"id": "design", "outputPath": f"openspec/changes/{CHANGE}/design.md", "paths": [str(change / "design.md")], "status": "done", "requires": ["proposal", "specs"]},
                {"id": "tasks", "outputPath": f"openspec/changes/{CHANGE}/tasks.md", "paths": [str(change / "tasks.md")], "status": "done", "requires": ["design"]},
            ],
            "rules": {"proposal": ["Name affected capability."], "specs": ["Include scenarios."], "design": ["State tradeoffs."], "tasks": ["Keep tasks small."]},
            "references": {},
            "deltas": [{"spec": "api", "operation": "ADDED", "description": "Add rate limit"}],
            "main_specs": {"api": default_spec("The API SHALL retain old behavior.")},
            "post_specs": {"api": default_spec("The API SHALL rate limit requests.")},
            "referenced_specs": {},
            "archive_mode": "success",
        }
        self.save()
        self.exe.write_text(FAKE_OPEN_SPEC.replace("__STATE_PATH__", repr(str(self.state_path))), encoding="utf-8")
        self.exe.chmod(self.exe.stat().st_mode | stat.S_IXUSR)

    def save(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2, sort_keys=True), encoding="utf-8")

    def reload(self) -> None:
        self.state = json.loads(self.state_path.read_text(encoding="utf-8"))

    def adapter(self) -> OpenSpecAdapter:
        return FixtureAdapter(self)

    def close(self) -> None:
        self.tmp.cleanup()


class HarnessRigM6OpenSpecTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = OpenSpecFixture()

    def tearDown(self) -> None:
        self.fx.close()

    # M6-T01 / M6-V01 / M6-V02
    def test_base_harness_works_without_openspec_and_required_workflow_blocks(self):
        direct = DirectAuthorityProvider.resolve(self.fx.root, "authority.txt", "repository")
        self.assertTrue(direct.authority_id.startswith("sha256:"))
        missing = OpenSpecAdapter(self.fx.root, executable="definitely-not-an-openspec-binary")
        health = missing.health(CHANGE)
        self.assertEqual(health.outcome, "BLOCKED")
        self.assertIn("openspec-unavailable", health.reasons)

        present_but_stalled = OpenSpecAdapter(self.fx.root, executable="openspec")
        with mock.patch.object(present_but_stalled, "_resolved_executable", return_value="/fake/openspec"), \
             mock.patch.object(openspec_module.subprocess, "run", side_effect=subprocess.TimeoutExpired(["openspec"], 1)):
            health = present_but_stalled.health(CHANGE)
        self.assertEqual(health.outcome, "BLOCKED")
        self.assertIn("openspec-version-unreadable", health.reasons)
        self.assertIn("doctor-command-failed", health.reasons)

    def test_supported_version_and_effective_health_pass(self):
        health = self.fx.adapter().health(CHANGE, require_tasks_complete=True)
        self.assertEqual(health.outcome, "PASS")
        self.assertEqual(health.version, "1.13.2")
        self.assertTrue(health.planning_complete)
        self.assertTrue(health.tasks_complete)

    # M6-T02/T03 / M6-V03
    def test_default_authority_profile_ignores_tasks_and_incidental_metadata_but_binds_behavior(self):
        adapter = self.fx.adapter()
        baseline = adapter.authority_ref(CHANGE, subject_ref="repository").authority_id
        change_dir = self.fx.root / "openspec" / "changes" / CHANGE

        (change_dir / "tasks.md").write_text("# Tasks\n- [x] Implement\n- [x] Document\n", encoding="utf-8")
        self.assertEqual(adapter.authority_ref(CHANGE, subject_ref="repository").authority_id, baseline)
        (change_dir / "tasks.md").write_text("# Tasks\n- [x] Implement\n", encoding="utf-8")

        (change_dir / ".openspec.yaml").write_text("schema: spec-driven\ncreated: 2026-09-26\n", encoding="utf-8")
        self.assertEqual(adapter.authority_ref(CHANGE, subject_ref="repository").authority_id, baseline)

        for relative, text in [
            ("proposal.md", "# Proposal\nDifferent scope.\n"),
            ("specs/api/spec.md", "## ADDED Requirements\nDifferent behavior.\n"),
            ("design.md", "# Design\nDifferent constraint.\n"),
        ]:
            path = change_dir / relative
            original = path.read_text(encoding="utf-8")
            path.write_text(text, encoding="utf-8")
            self.assertNotEqual(adapter.authority_ref(CHANGE, subject_ref="repository").authority_id, baseline, relative)
            path.write_text(original, encoding="utf-8")

    def test_effective_context_and_rules_are_authority_bearing_but_engine_version_is_not(self):
        adapter = self.fx.adapter()
        baseline = adapter.authority_ref(CHANGE, subject_ref="repository").authority_id
        self.fx.state["context"] = "Different project constraint."
        self.fx.save()
        self.assertNotEqual(adapter.authority_ref(CHANGE, subject_ref="repository").authority_id, baseline)

        self.fx.state["context"] = "Use repository conventions."
        self.fx.state["version"] = "1.13.3"
        self.fx.save()
        compatible = FixtureAdapter(self.fx)
        compatible.compatible_versions = frozenset({"1.13.2", "1.13.3"})
        self.assertEqual(compatible.authority_ref(CHANGE, subject_ref="repository").authority_id, baseline)

    def test_custom_artifact_graph_is_consumed_without_freezing_default_paths(self):
        change = self.fx.root / "openspec" / "changes" / CHANGE
        scope = change / "scope.md"
        behavior = change / "behavior" / "contract.md"
        behavior.parent.mkdir(exist_ok=True)
        scope.write_text("# Scope\nBounded change.\n", encoding="utf-8")
        behavior.write_text("# Behavior\nObservable contract.\n", encoding="utf-8")
        self.fx.state["schema"] = "custom-flow"
        self.fx.state["artifacts"] = [
            {"id": "scope", "outputPath": str(scope.relative_to(self.fx.root)), "paths": [str(scope)], "status": "done", "requires": []},
            {"id": "behavior", "outputPath": str(behavior.relative_to(self.fx.root)), "paths": [str(behavior)], "status": "done", "requires": ["scope"]},
            {"id": "tasks", "outputPath": f"openspec/changes/{CHANGE}/tasks.md", "paths": [str(change / "tasks.md")], "status": "done", "requires": ["behavior"]},
        ]
        self.fx.state["rules"] = {"scope": ["Bound scope."], "behavior": ["Specify outcomes."], "tasks": []}
        self.fx.save()
        adapter = self.fx.adapter()
        baseline = adapter.authority_ref(CHANGE, subject_ref="repository").authority_id
        behavior.write_text("# Behavior\nChanged observable contract.\n", encoding="utf-8")
        self.assertNotEqual(adapter.authority_ref(CHANGE, subject_ref="repository").authority_id, baseline)

    def test_skip_specs_is_supported_without_treating_skip_as_verification_bypass(self):
        self.fx.state["deltas"] = []
        for artifact in self.fx.state["artifacts"]:
            if artifact["id"] == "specs":
                artifact["status"] = "skipped"
                artifact["paths"] = []
        self.fx.save()
        snapshot = self.fx.adapter().authority_snapshot(CHANGE, subject_ref="repository")
        self.assertEqual(snapshot.affected_specs, ())
        self.assertEqual(self.fx.adapter().health(CHANGE).outcome, "PASS")

    # M6-T04 / M6-V04
    def test_authority_bearing_referenced_spec_is_hashed_and_change_invalidates_authority(self):
        self.fx.state["references"] = {
            "proposal": [{"store_id": "shared", "specs": [{"id": "platform", "summary": "shared"}], "status": []}]
        }
        self.fx.state["referenced_specs"] = {
            "shared": {"platform": {**default_spec("Shared platform SHALL provide auth."), "id": "platform", "title": "platform"}}
        }
        self.fx.save()
        adapter = self.fx.adapter()
        baseline = adapter.authority_ref(CHANGE, subject_ref="repository").authority_id
        self.fx.state["referenced_specs"]["shared"]["platform"]["requirements"][0]["text"] = "Shared platform SHALL provide stronger auth."
        self.fx.save()
        self.assertNotEqual(adapter.authority_ref(CHANGE, subject_ref="repository").authority_id, baseline)

    def test_unresolved_authority_reference_blocks_but_tasks_only_reference_does_not(self):
        unresolved = [{"store_id": "shared", "status": [{"severity": "warning", "code": "reference_unresolved", "message": "missing"}]}]
        self.fx.state["references"] = {"proposal": unresolved}
        self.fx.save()
        with self.assertRaisesRegex(OpenSpecBlocked, "reference:reference_unresolved"):
            self.fx.adapter().authority_ref(CHANGE, subject_ref="repository")

        self.fx.state["references"] = {"tasks": unresolved}
        self.fx.save()
        self.assertTrue(self.fx.adapter().authority_ref(CHANGE, subject_ref="repository").authority_id.startswith("sha256:"))

    # M6-T05 / M6-V04
    def test_malformed_effective_rules_and_strict_validation_failure_block(self):
        self.fx.state["rules"]["proposal"] = {"not": "a-list"}
        self.fx.save()
        health = self.fx.adapter().health(CHANGE)
        self.assertEqual(health.outcome, "BLOCKED")
        self.assertTrue(any("invalid-effective-rules:proposal" in reason for reason in health.reasons))

        self.fx.state["rules"]["proposal"] = ["Name affected capability."]
        self.fx.state["validate_valid"] = False
        self.fx.save()
        health = self.fx.adapter().health(CHANGE)
        self.assertEqual(health.outcome, "BLOCKED")
        self.assertIn("strict-validation-failed", health.reasons)

    def test_unhealthy_root_and_unsupported_primary_store_fail_closed(self):
        self.fx.state["doctor_healthy"] = False
        self.fx.save()
        self.assertEqual(self.fx.adapter().health(CHANGE).outcome, "BLOCKED")
        self.fx.state["doctor_healthy"] = True
        self.fx.state["root_source"] = "store"
        self.fx.save()
        health = self.fx.adapter().health(CHANGE)
        self.assertEqual(health.outcome, "BLOCKED")
        self.assertTrue(any(reason.startswith("unsupported-primary-root-source") for reason in health.reasons))

    # M6-T06 / M6-V05 / M6-V06
    def test_guarded_archive_success_records_transition_and_rechecks_final_authority_state(self):
        adapter = self.fx.adapter()
        result = guarded_archive(
            adapter,
            repository_id="fixture-repo",
            change=CHANGE,
            subject_ref="repository",
            run_id="m6-archive",
            now=NOW,
            confirmed=True,
        )
        self.assertEqual(result.outcome, "PASS")
        self.assertEqual(result.pre_check.outcome, "PASS")
        self.assertEqual(result.mutation.outcome, "PASS")
        self.assertEqual(result.transition_receipt.outcome, "PASS")
        self.assertNotEqual(result.state_before.state_id, result.state_after.state_id)
        self.assertNotEqual(result.authority_before.authority_id, result.authority_after.authority_id)
        self.assertEqual(result.post_recheck.outcome, "BLOCKED")
        self.assertIn("authority-stale", result.post_recheck.reasons)
        self.assertIn("state-stale-or-not-certified", result.post_recheck.reasons)

    def test_archive_partial_mutation_and_postcondition_mismatch_block(self):
        for mode, expected in [("partial-fail", "archive-command-failed"), ("mismatch", "archive-path-postcondition-failed")]:
            with self.subTest(mode=mode):
                if mode != "partial-fail":
                    self.fx.close()
                    self.fx = OpenSpecFixture()
                self.fx.state["archive_mode"] = mode
                self.fx.save()
                adapter = self.fx.adapter()
                result = guarded_archive(
                    adapter,
                    repository_id="fixture-repo",
                    change=CHANGE,
                    subject_ref="repository",
                    run_id=f"m6-{mode}",
                    now=NOW,
                    confirmed=True,
                )
                self.assertEqual(result.outcome, "BLOCKED")
                self.assertIn(expected, result.reasons)
                self.assertEqual(result.transition_receipt.outcome, "BLOCKED")

    def test_required_semantic_coherence_failure_blocks_without_mutation(self):
        adapter = self.fx.adapter()
        result = guarded_archive(
            adapter,
            repository_id="fixture-repo",
            change=CHANGE,
            subject_ref="repository",
            run_id="m6-semantic",
            now=NOW,
            confirmed=True,
            semantic_review="FAIL",
        )
        self.assertEqual(result.outcome, "BLOCKED")
        self.assertIn("semantic-coherence-failed", result.reasons)
        self.assertEqual(result.pre_receipt.outcome, "BLOCKED")
        self.assertTrue(self.fx.state.get("active", True))

    def test_archive_requires_explicit_local_confirmation(self):
        adapter = self.fx.adapter()
        result = guarded_archive(
            adapter,
            repository_id="fixture-repo",
            change=CHANGE,
            subject_ref="repository",
            run_id="m6-no-grant",
            now=NOW,
        )
        self.assertEqual(result.outcome, "BLOCKED")
        self.assertIn("local-archive-confirmation-required", result.reasons)
        self.assertIsNone(result.pre_check)
        self.assertTrue(self.fx.state.get("active", True))

    def test_external_cli_invocation_is_argv_based_and_never_uses_shell(self):
        adapter = OpenSpecAdapter(self.fx.root, executable="openspec")
        completed = subprocess.CompletedProcess(["/fake/openspec"], 0, b"{}\n", b"")
        with mock.patch.object(adapter, "_resolved_executable", return_value="/fake/openspec"), \
             mock.patch("harness_rig.openspec.subprocess.run", return_value=completed) as runner:
            result = adapter._run("doctor", "--json")
        self.assertEqual(result.returncode, 0)
        args, kwargs = runner.call_args
        self.assertEqual(args[0], ["/fake/openspec", "doctor", "--json"])
        self.assertIs(kwargs["shell"], False)
        self.assertIs(kwargs["stdin"], subprocess.DEVNULL)

    def test_cli_exposes_guarded_spec_archive(self):
        output = io.StringIO()
        with mock.patch("harness_rig.cli.OpenSpecAdapter", side_effect=lambda repo, executable="openspec": FixtureAdapter(self.fx)):
            with contextlib.redirect_stdout(output):
                code = cli_main([
                "spec", "archive",
                "--repo", str(self.fx.root),
                "--change", CHANGE,
                "--repository-id", "fixture-repo",
                "--run-id", "m6-cli",
                "--confirm-local-archive",
                "--now", NOW,
                "--openspec-executable", str(self.fx.exe),
                ])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["outcome"], "PASS")
        self.assertEqual(payload["post_recheck"]["outcome"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
