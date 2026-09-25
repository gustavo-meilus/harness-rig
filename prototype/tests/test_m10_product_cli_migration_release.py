from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from harness_rig.cli import main as cli_main
from harness_rig.migration import (
    HISTORY_MAP_SCHEMA,
    MigrationError,
    apply_migration,
    assess_migration,
    load_migration_state,
    lookup_rewritten_commit,
    rollback_migration,
)
from harness_rig.process import run_process
from harness_rig.product import (
    CLI_ENVELOPE_SCHEMA,
    CONFIG_SCHEMA,
    ProductError,
    load_cli_envelope,
    load_effective_config,
)
from harness_rig.release import (
    ReleaseError,
    build_release_record,
    verify_release_record,
    write_immutable_release_record,
)

NOW = "2026-09-25T16:00:00Z"


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class HarnessRigM10Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.repo = Path(self.td.name)
        run_git(self.repo, "init")
        run_git(self.repo, "config", "user.name", "Harness Rig M10")
        run_git(self.repo, "config", "user.email", "m10@example.invalid")
        (self.repo / "authority.txt").write_text("approved behavior\n", encoding="utf-8")
        run_git(self.repo, "add", "authority.txt")
        run_git(self.repo, "commit", "-m", "baseline")
        self.empty_home = self.repo / "home"
        self.empty_home.mkdir()

    def tearDown(self) -> None:
        self.td.cleanup()

    def _cli(self, argv: list[str]) -> tuple[int, dict]:
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"HOME": str(self.empty_home), "XDG_CONFIG_HOME": str(self.empty_home / "xdg")}, clear=False):
            with contextlib.redirect_stdout(out):
                rc = cli_main(argv)
        return rc, json.loads(out.getvalue())

    def test_t01_compact_init_status_verify_machine_surface(self):
        rc, init = self._cli(["init", "--repo", str(self.repo)])
        self.assertEqual(rc, 0)
        self.assertEqual(init["schema"], CLI_ENVELOPE_SCHEMA)
        self.assertEqual(init["command"], "init")
        self.assertEqual(init["outcome"], "PASS")

        rc, status = self._cli(["status", "--repo", str(self.repo)])
        self.assertEqual(rc, 0)
        self.assertEqual(status["data"]["revision"], "r8.10")
        self.assertEqual(status["data"]["migration"]["history_qualification"], "PENDING_M11")

        rc, verify = self._cli([
            "verify", "--repo", str(self.repo), "--authority", "authority.txt",
            "--run-id", "m10-verify", "--now", NOW, "--issued-at", "2026-09-25T15:00:00Z",
            "--expires-at", "2026-09-25T17:00:00Z", "--", sys.executable, "-I", "-S", "-c", "pass",
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(verify["schema"], CLI_ENVELOPE_SCHEMA)
        self.assertEqual(verify["outcome"], "PASS")
        self.assertEqual(verify["data"]["receipt"]["outcome"], "PASS")
        self.assertEqual(verify["data"]["verdict"]["outcome"], "ACCEPTED")

    def test_t02_versioned_envelope_and_r89_backward_compatibility(self):
        v1 = {
            "schema": CLI_ENVELOPE_SCHEMA, "command": "status", "outcome": "PASS", "exit_code": 0,
            "data": {"x": 1}, "reasons": [], "compatibility": None,
        }
        loaded = load_cli_envelope(v1)
        self.assertEqual(loaded.command, "status")

        legacy_direct = {"receipt": {"outcome": "PASS"}, "verdict": {"outcome": "ACCEPTED"}}
        migrated = load_cli_envelope(legacy_direct)
        self.assertEqual(migrated.compatibility, "r8.9/direct-json")
        self.assertEqual(migrated.outcome, "PASS")

        legacy_archive = {
            "outcome": "BLOCKED", "reasons": ["x"], "authority_before": None, "state_before": {},
            "pre_receipt": None, "pre_verdict": None, "mutation": None, "authority_after": None,
            "state_after": {}, "transition_receipt": None, "post_recheck_verdict": None,
        }
        migrated_archive = load_cli_envelope(legacy_archive)
        self.assertEqual(migrated_archive.compatibility, "r8.9/spec-archive-json")
        self.assertEqual(migrated_archive.outcome, "BLOCKED")

        with self.assertRaises(ProductError):
            load_cli_envelope({"schema": "harness-rig/cli-envelope/v2"})

    def test_t02_doctor_v1_machine_envelope_is_opt_in_without_breaking_old_shape(self):
        rc, doctor = self._cli(["doctor", "--json-v1"])
        self.assertEqual(rc, 0)
        self.assertEqual(doctor["schema"], CLI_ENVELOPE_SCHEMA)
        self.assertEqual(doctor["command"], "doctor")
        self.assertEqual(doctor["data"]["schema"], "harness-rig/host-qualification/v1")

    def test_v01_noninteractive_spec_status_and_archive_unavailable_block(self):
        rc, status = self._cli([
            "spec", "status", "--repo", str(self.repo), "--change", "missing",
            "--openspec-executable", "definitely-not-openspec-m10",
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(status["outcome"], "BLOCKED")
        self.assertIn("openspec-unavailable", status["reasons"])

        rc, archive = self._cli([
            "spec", "archive", "--json-v1", "--repo", str(self.repo), "--change", "missing",
            "--run-id", "m10-archive", "--now", NOW, "--issued-at", "2026-09-25T15:00:00Z",
            "--openspec-executable", "definitely-not-openspec-m10",
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(archive["outcome"], "BLOCKED")
        self.assertIn("openspec-unavailable", archive["reasons"])

    def test_t03_config_precedence_defaults_global_project_cli(self):
        xdg = self.repo / "xdg"
        global_path = xdg / "harness-rig" / "config.json"
        global_path.parent.mkdir(parents=True)
        global_path.write_text(json.dumps({
            "schema": CONFIG_SCHEMA, "timeout_seconds": 10, "openspec_executable": "global-openspec"
        }), encoding="utf-8")
        project_path = self.repo / ".harness-rig" / "config.json"
        project_path.parent.mkdir()
        project_path.write_text(json.dumps({
            "schema": CONFIG_SCHEMA, "timeout_seconds": 20, "openspec_executable": "project-openspec"
        }), encoding="utf-8")
        cfg = load_effective_config(
            self.repo,
            cli={"timeout_seconds": 25},
            env={"XDG_CONFIG_HOME": str(xdg)},
            home=self.empty_home,
        )
        self.assertEqual(cfg.timeout_seconds, 25)
        self.assertEqual(cfg.openspec_executable, "project-openspec")
        self.assertEqual(cfg.sources[0], "defaults")
        self.assertTrue(any(x.startswith("global:") for x in cfg.sources))
        self.assertTrue(any(x.startswith("project:") for x in cfg.sources))
        self.assertEqual(cfg.sources[-1], "cli")

    def test_v02_malformed_project_config_fails_before_verifier_runs(self):
        p = self.repo / ".harness-rig" / "config.json"
        p.parent.mkdir()
        p.write_text("{bad", encoding="utf-8")
        sentinel = self.repo / "ran.txt"
        rc, payload = self._cli([
            "verify", "--repo", str(self.repo), "--authority", "authority.txt",
            "--run-id", "bad-config", "--now", NOW, "--issued-at", "2026-09-25T15:00:00Z",
            "--", sys.executable, "-c", f"from pathlib import Path; Path({str(sentinel)!r}).write_text('ran')",
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(payload["outcome"], "BLOCKED")
        self.assertFalse(sentinel.exists())
        self.assertTrue(payload["reasons"][0].startswith("project-config-malformed"))

    def test_v02_global_config_cannot_define_or_weaken_repository_policy(self):
        xdg = self.repo / "xdg"
        gp = xdg / "harness-rig" / "config.json"
        gp.parent.mkdir(parents=True)
        gp.write_text(json.dumps({"schema": CONFIG_SCHEMA, "policy": {"require_repository_verdict": False}}), encoding="utf-8")
        with self.assertRaisesRegex(ProductError, "global-policy-override-forbidden"):
            load_effective_config(self.repo, env={"XDG_CONFIG_HOME": str(xdg)}, home=self.empty_home)

    def test_v03_timeout_cleans_descendant_process_group(self):
        sentinel = self.repo / "late.txt"
        child = (
            "import subprocess,sys,time; "
            f"subprocess.Popen([sys.executable,'-c',\"import time; from pathlib import Path; time.sleep(0.8); Path({str(sentinel)!r}).write_text('late')\"]); "
            "time.sleep(5)"
        )
        result = run_process([sys.executable, "-c", child], cwd=self.repo, timeout_seconds=0.1)
        self.assertEqual(result.outcome, "TIMEOUT")
        time.sleep(1.0)
        self.assertFalse(sentinel.exists())

    def test_v03_keyboard_interrupt_runs_cleanup_before_reraising(self):
        class FakeProc:
            pid = 999999
            returncode = None
            calls = 0
            def communicate(self, timeout=None):
                self.calls += 1
                if self.calls == 1:
                    raise KeyboardInterrupt()
                return (b"", b"")
            def poll(self):
                return None
            def wait(self, timeout=None):
                self.returncode = -15
                return self.returncode
        fake = FakeProc()
        with mock.patch("harness_rig.process.subprocess.Popen", return_value=fake), \
             mock.patch("harness_rig.process._terminate_tree") as cleanup:
            with self.assertRaises(KeyboardInterrupt):
                run_process(["x"], cwd=self.repo, timeout_seconds=1)
        cleanup.assert_called_once_with(fake)

    def test_v04_interrupted_migration_is_persisted_and_next_apply_blocks(self):
        state = apply_migration(self.repo, simulate_interrupt_after_journal=True)
        self.assertEqual(state.phase, "APPLYING")
        with self.assertRaisesRegex(MigrationError, "interrupted-migration"):
            apply_migration(self.repo)
        assessment = assess_migration(self.repo)
        self.assertIn("interrupted-migration", assessment.reasons)

    def test_v04_mixed_old_new_state_blocks(self):
        state = apply_migration(self.repo)
        self.assertEqual(state.phase, "COMPLETE")
        legacy = self.repo / ".aiboarding" / "state.json"
        legacy.parent.mkdir()
        legacy.write_text("{}", encoding="utf-8")
        assessment = assess_migration(self.repo)
        self.assertEqual(assessment.outcome, "BLOCKED")
        self.assertIn("mixed-old-new-state", assessment.reasons)

    def test_v04_duplicate_hook_ownership_blocks(self):
        for rel in (".aiboarding/hooks.json", ".harness-rig/hooks.json"):
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"hooks": ["post-verify"]}), encoding="utf-8")
        assessment = assess_migration(self.repo)
        self.assertEqual(assessment.outcome, "BLOCKED")
        self.assertEqual(assessment.duplicate_hooks, ("post-verify",))

    def test_v05_supported_upgrade_and_rollback_are_explicit_unknown_downgrade_blocks(self):
        state = apply_migration(self.repo)
        self.assertEqual(state.from_revision, "r8.9")
        self.assertEqual(state.to_revision, "r8.10")
        rolled = rollback_migration(self.repo)
        self.assertEqual(rolled.phase, "ROLLED_BACK")
        self.assertEqual(rolled.from_revision, "r8.10")
        self.assertEqual(rolled.to_revision, "r8.9")
        with self.assertRaisesRegex(MigrationError, "unsupported-migration-target"):
            apply_migration(self.repo, from_revision="r8.10", to_revision="r8.9")

    def test_v05_unknown_migration_schema_fails_closed(self):
        path = self.repo / ".harness-rig" / "migration-state.json"
        path.parent.mkdir()
        path.write_text(json.dumps({"schema": "harness-rig/migration-state/v2"}), encoding="utf-8")
        with self.assertRaises(MigrationError):
            load_migration_state(path)

    def test_v05_synthetic_old_to_new_commit_lookup_is_deterministic(self):
        path = self.repo / "map.json"
        path.write_text(json.dumps({
            "schema": HISTORY_MAP_SCHEMA,
            "source": "synthetic",
            "mappings": {"a" * 40: "b" * 40},
        }), encoding="utf-8")
        self.assertEqual(lookup_rewritten_commit(path, "a" * 40), "b" * 40)
        with self.assertRaisesRegex(MigrationError, "commit-not-found"):
            lookup_rewritten_commit(path, "c" * 40)

    def test_v06_release_record_binds_build_to_artifact_and_detects_tamper(self):
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"deterministic-build")
        record = build_release_record(
            artifact_paths=[artifact], accepted_source_revision="abc123",
            accepted_repository_verdict="ci-required:verdict-1",
            build_workflow_identity="github-actions:ci-required@deadbeef",
            created_at=NOW,
        )
        self.assertEqual(record.status, "PASS")
        verify_release_record(record, self.repo)
        target = self.repo / "release.json"
        write_immutable_release_record(target, record)
        write_immutable_release_record(target, record)
        artifact.write_bytes(b"tampered")
        with self.assertRaisesRegex(ReleaseError, "digest-mismatch"):
            verify_release_record(record, self.repo)

    def test_v06_release_without_accepted_repository_verdict_is_blocked_not_fabricated(self):
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        record = build_release_record(
            artifact_paths=[artifact], accepted_source_revision="abc123",
            accepted_repository_verdict=None,
            build_workflow_identity="local-build:m10",
            created_at=NOW,
        )
        self.assertEqual(record.status, "BLOCKED")
        self.assertIn("accepted-repository-verdict-unavailable", record.reasons)

    def test_migrate_cli_emits_v1_and_keeps_history_qualification_pending_m11(self):
        rc, payload = self._cli(["migrate", "--repo", str(self.repo)])
        self.assertEqual(rc, 0)
        self.assertEqual(payload["schema"], CLI_ENVELOPE_SCHEMA)
        self.assertEqual(payload["data"]["phase"], "COMPLETE")
        self.assertEqual(payload["data"]["history_qualification"], "PENDING_M11")


if __name__ == "__main__":
    unittest.main()
