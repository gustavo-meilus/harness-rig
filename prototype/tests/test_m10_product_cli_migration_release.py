from __future__ import annotations

import contextlib
from dataclasses import asdict, replace
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
    dispatch_record_attestation,
    workflow_dispatch_payload,
    verify_release_record,
    write_immutable_release_record,
)
from verification.release_provenance import main as release_provenance_main

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
        self.assertEqual(status["data"]["revision"], "r8.12")
        self.assertEqual(status["data"]["migration"]["history_qualification"], "PENDING_M11")

        rc, verify = self._cli([
            "verify", "--repo", str(self.repo), "--authority", "authority.txt",
            "--run-id", "m10-verify", "--", sys.executable, "-I", "-S", "-c", "pass",
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(verify["schema"], CLI_ENVELOPE_SCHEMA)
        self.assertEqual(verify["outcome"], "PASS")
        self.assertEqual(verify["data"]["receipt"]["outcome"], "PASS")
        self.assertEqual(verify["data"]["scope"], "local-evidence")
        self.assertNotIn("verdict", verify["data"])

    def test_local_verify_and_direct_fail_without_authorized_verdict(self):
        args = ["--repo", str(self.repo), "--authority", "authority.txt",
                "--run-id", "local-fail", "--", sys.executable, "-I", "-S",
                "-c", "raise SystemExit(1)"]
        rc, verify = self._cli(["verify", *args])
        self.assertEqual(rc, 2)
        self.assertEqual(verify["outcome"], "BLOCKED")
        self.assertEqual(verify["data"]["receipt"]["outcome"], "FAIL")
        self.assertNotIn("verdict", verify["data"])
        rc, direct = self._cli(args)
        self.assertEqual(rc, 2)
        self.assertEqual(direct["scope"], "local-evidence")
        self.assertNotIn("verdict", direct)

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
            "--confirm-local-archive",
            "--run-id", "m10-archive", "--now", NOW,
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
            "--run-id", "bad-config",
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

    def _hosted_responses(self, **run_changes):
        run = {
            "id": 1234, "run_attempt": 1, "repository": {"id": 987, "full_name": "owner/repo"},
            "head_sha": "a" * 40, "path": ".github/workflows/ci-required.yml@refs/heads/main",
            "event": "push", "head_branch": "main", "status": "completed", "conclusion": "success",
        }
        run.update(run_changes)
        jobs = {"total_count": 1, "jobs": [{
            "id": 4321, "run_id": 1234, "head_sha": "a" * 40, "name": "ci / required",
            "status": "completed", "conclusion": "success",
        }]}
        return run, jobs

    def _make_release(self, artifact: Path, responses=None):
        if responses is None:
            responses = self._hosted_responses()
        with mock.patch("harness_rig.release._gh_api_json", side_effect=responses):
            return build_release_record(
                artifact_paths=[artifact], source_revision="a" * 40,
                repository="owner/repo", hosted_run_id=1234,
                build_workflow_identity="github-actions:ci-required", created_at=NOW,
            )

    def _verify(self, record, responses, attestation=("PASS", None), repository="owner/repo"):
        path = self.repo / "verify-release.json"
        path.write_text(json.dumps(asdict(record), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record_bytes = path.read_bytes()
        with mock.patch("harness_rig.release._gh_api_json", side_effect=responses), \
                mock.patch("harness_rig.release._verify_record_attestation", return_value=attestation):
            return verify_release_record(record_bytes, self.repo, repository)

    def test_v06_hosted_run_and_required_job_are_rechecked_and_artifact_tampering_is_separate(self):
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"deterministic-build")
        run, jobs = self._hosted_responses()
        record = self._make_release(artifact, [run, jobs])
        self.assertEqual(record.status, "CANDIDATE")
        target = self.repo / "release.json"
        write_immutable_release_record(target, record)
        write_immutable_release_record(target, record)
        result = self._verify(record, [run, jobs])
        self.assertEqual(result["outcome"], "PASS")
        self.assertEqual(result["artifact_integrity"], "PASS")
        self.assertEqual(result["hosted_ci"], "PASS")
        self.assertEqual(result["attestation"], "PASS")
        artifact.write_bytes(b"tampered")
        result = self._verify(record, [run, jobs])
        self.assertEqual(result["outcome"], "FAIL")
        self.assertEqual(result["artifact_integrity"], "FAIL")
        self.assertEqual(result["hosted_ci"], "PASS")
        artifact.write_bytes(b"deterministic-build")
        result = self._verify(record, [ReleaseError("github-api-unavailable")])
        self.assertEqual(result["artifact_integrity"], "PASS")
        self.assertEqual(result["hosted_ci"], "BLOCKED")
        self.assertEqual(result["outcome"], "BLOCKED")

    def test_v06_hosted_acceptance_rejects_repository_sha_workflow_event_branch_and_attempt(self):
        cases = [
            ({"repository": {"id": 987, "full_name": "other/repo"}}, "hosted-repository-mismatch"),
            ({"id": 9999}, "hosted-run-id-mismatch"),
            ({"head_sha": "b" * 40}, "hosted-source-revision-mismatch"),
            ({"path": ".github/workflows/other.yml@refs/heads/main"}, "hosted-workflow-mismatch"),
            ({"event": "workflow_dispatch"}, "hosted-event-mismatch"),
            ({"head_branch": "release"}, "hosted-branch-mismatch"),
            ({"status": "in_progress", "conclusion": None}, "hosted-run-unsuccessful"),
            ({"conclusion": "failure"}, "hosted-run-unsuccessful"),
        ]
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        for changes, expected in cases:
            with self.subTest(expected=expected):
                run, jobs = self._hosted_responses(**changes)
                record = self._make_release(artifact, [run, jobs])
                self.assertEqual(record.status, "BLOCKED")
                self.assertIn(expected, record.reasons)

    def test_v06_hosted_acceptance_rejects_wrong_job_attempt_id_failure_and_duplicates(self):
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        for job_changes, expected in [
            ({"name": "other"}, "hosted-required-job-not-unique"),
            ({"conclusion": "failure"}, "hosted-required-job-unsuccessful"),
            ({"run_id": 99}, "hosted-required-job-binding-mismatch"),
            ({"head_sha": "b" * 40}, "hosted-required-job-binding-mismatch"),
        ]:
            run, jobs = self._hosted_responses()
            jobs["jobs"][0].update(job_changes)
            with self.subTest(expected=expected):
                record = self._make_release(artifact, [run, jobs])
                self.assertEqual(record.status, "BLOCKED")
                self.assertIn(expected, record.reasons)
        run, jobs = self._hosted_responses()
        jobs["total_count"] = 2
        jobs["jobs"].append(dict(jobs["jobs"][0], id=9999))
        record = self._make_release(artifact, [run, jobs])
        self.assertEqual(record.status, "BLOCKED")
        self.assertIn("hosted-required-job-not-unique", record.reasons)

        run, jobs = self._hosted_responses()
        jobs["total_count"] = 0
        record = self._make_release(artifact, [run, jobs])
        self.assertEqual(record.status, "BLOCKED")
        self.assertIn("hosted-jobs-count-mismatch", record.reasons)

    def test_v06_api_unavailable_and_missing_run_make_immutable_blocked_candidates(self):
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        with mock.patch("harness_rig.release._gh_api_json", side_effect=ReleaseError("github-api-unavailable")):
            record = build_release_record(artifact_paths=[artifact], source_revision="a" * 40,
                repository="owner/repo", hosted_run_id=1234, build_workflow_identity="local", created_at=NOW)
        self.assertEqual(record.status, "BLOCKED")
        self.assertIn("github-api-unavailable", record.reasons)
        missing = build_release_record(
            artifact_paths=[artifact], source_revision="a" * 40, repository="owner/repo",
            hosted_run_id=None, build_workflow_identity="local", created_at=NOW,
        )
        self.assertEqual(missing.status, "BLOCKED")
        self.assertIn("hosted-run-unavailable", missing.reasons)

    def test_v06_verifier_rejects_blocked_legacy_and_repository_mismatch_without_network(self):
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        run, jobs = self._hosted_responses()
        record = self._make_release(artifact, [run, jobs])
        blocked = build_release_record(
            artifact_paths=[artifact], source_revision="a" * 40, repository="owner/repo",
            hosted_run_id=None, build_workflow_identity="local", created_at=NOW,
        )
        result = self._verify(blocked, [run, jobs])
        self.assertEqual(result["outcome"], "BLOCKED")
        result = self._verify(record, [run, jobs], repository="different/repo")
        self.assertEqual(result["outcome"], "BLOCKED")
        changed_run, changed_jobs = self._hosted_responses(run_attempt=2)
        result = self._verify(record, [changed_run, changed_jobs])
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertIn("hosted-run-attempt-changed", result["hosted_ci_reasons"])
        from harness_rig.canonical import digest
        from harness_rig.release import _record_material

        wrong_repo_id = replace(record, repository_id=999, record_id="")
        wrong_repo_id = replace(wrong_repo_id, record_id=digest(_record_material(wrong_repo_id)))
        result = self._verify(wrong_repo_id, [run, jobs])
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertIn("hosted-repository-id-mismatch", result["hosted_ci_reasons"])
        wrong_job = replace(record, hosted_job_id=9999, record_id="")
        wrong_job = replace(wrong_job, record_id=digest(_record_material(wrong_job)))
        result = self._verify(wrong_job, [run, jobs])
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertIn("hosted-required-job-id-mismatch", result["hosted_ci_reasons"])
        legacy = replace(record, schema="harness-rig/release-record/v1")
        with self.assertRaisesRegex(ReleaseError, "unsupported-release-record-schema"):
            self._verify(legacy, [run, jobs])
        legacy = replace(record, schema="harness-rig/release-record/v2")
        with self.assertRaisesRegex(ReleaseError, "unsupported-release-record-schema"):
            self._verify(legacy, [run, jobs])
        payload = asdict(record)
        payload["accepted_source_revision"] = payload["source_revision"]
        from harness_rig.release import parse_release_record
        with self.assertRaisesRegex(ReleaseError, "release-record-fields-invalid"):
            parse_release_record(json.dumps(payload).encode("utf-8"))

    def test_v06_cli_requires_explicit_repository_and_reports_separate_results(self):
        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        record_path = self.repo / "release.json"
        run, jobs = self._hosted_responses()
        out = io.StringIO()
        with mock.patch("harness_rig.release._gh_api_json", side_effect=[run, jobs]), contextlib.redirect_stdout(out):
            rc = release_provenance_main([
                "record", "--artifact", str(artifact), "--source-revision", "a" * 40,
                "--repository", "owner/repo", "--run-id", "1234", "--workflow", "test",
                "--created-at", NOW, "--output", str(record_path),
            ])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out.getvalue())["status"], "CANDIDATE")
        out = io.StringIO()
        record_bytes = record_path.read_bytes()
        changed_path_bytes = b'{"different_record": true}\n'
        api_responses = iter([run, jobs])
        verified_bytes = []

        def mutate_path_during_lookup(endpoint):
            record_path.write_bytes(changed_path_bytes)
            return next(api_responses)

        def attest_snapshot(snapshot_bytes, repository):
            verified_bytes.append(snapshot_bytes)
            return "PASS", None

        with mock.patch("harness_rig.release._gh_api_json", side_effect=mutate_path_during_lookup), \
                mock.patch("harness_rig.release._verify_record_attestation", side_effect=attest_snapshot), \
                contextlib.redirect_stdout(out):
            rc = release_provenance_main([
                "verify", "--record", str(record_path), "--artifact-dir", str(self.repo),
                "--repository", "owner/repo",
            ])
        payload = json.loads(out.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["artifact_integrity"], "PASS")
        self.assertEqual(payload["hosted_ci"], "PASS")
        self.assertEqual(payload["attestation"], "PASS")
        self.assertEqual(verified_bytes, [record_bytes])
        self.assertEqual(record_path.read_bytes(), changed_path_bytes)
        record_path.write_bytes(record_bytes)
        legacy = json.loads(record_path.read_text(encoding="utf-8"))
        legacy["schema"] = "harness-rig/release-record/v1"
        record_path.write_text(json.dumps(legacy), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = release_provenance_main([
                "verify", "--record", str(record_path), "--artifact-dir", str(self.repo),
                "--repository", "owner/repo",
            ])
        self.assertEqual(rc, 2)
        self.assertEqual(json.loads(out.getvalue())["outcome"], "BLOCKED")

    def test_v06_recomputed_record_digest_tampering_requires_original_signature(self):
        from harness_rig.canonical import digest
        from harness_rig.release import _record_material

        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"original-artifact")
        run, jobs = self._hosted_responses()
        original = self._make_release(artifact, [run, jobs])
        artifact.write_bytes(b"attacker-changed-artifact")
        changed_artifact = replace(original.artifacts[0], sha256=__import__("hashlib").sha256(artifact.read_bytes()).hexdigest(),
                                   size=artifact.stat().st_size)
        altered = replace(original, artifacts=(changed_artifact,), record_id="")
        altered = replace(altered, record_id=digest(_record_material(altered)))
        result = self._verify(altered, [run, jobs], attestation=("FAIL", "attestation-verification-failed"))
        self.assertEqual(result["artifact_integrity"], "PASS")
        self.assertEqual(result["hosted_ci"], "PASS")
        self.assertEqual(result["attestation"], "FAIL")
        self.assertEqual(result["outcome"], "FAIL")

    def test_v06_attestation_verification_is_scoped_and_fails_closed(self):
        from types import SimpleNamespace
        from harness_rig.release import _verify_record_attestation

        record_bytes = b'{\r\n  "record_id": "snapshot"\r\n}\r\n'
        verified_snapshot = []
        def verify_snapshot(command, **kwargs):
            verified_snapshot.append(Path(command[3]).read_bytes())
            return SimpleNamespace(returncode=0)

        with mock.patch("harness_rig.release.subprocess.run", side_effect=verify_snapshot) as run:
            self.assertEqual(_verify_record_attestation(record_bytes, "owner/repo"), ("PASS", None))
        self.assertEqual(verified_snapshot, [record_bytes])
        command = run.call_args.args[0]
        self.assertIn("--repo", command)
        self.assertIn("owner/repo", command)
        self.assertIn("--signer-workflow", command)
        self.assertIn("github.com/owner/repo/.github/workflows/release-record-attestation.yml", command)
        self.assertIn("--source-ref", command)
        self.assertIn("refs/heads/main", command)
        for rejected_attestation in ("missing", "invalid", "wrong-repository", "wrong-signer", "wrong-source-ref"):
            with self.subTest(attestation=rejected_attestation), \
                    mock.patch("harness_rig.release.subprocess.run", return_value=SimpleNamespace(returncode=1)):
                status, reason = _verify_record_attestation(record_bytes, "owner/repo")
                self.assertEqual((status, reason), ("FAIL", "attestation-verification-failed"))
        with mock.patch("harness_rig.release.subprocess.run", side_effect=OSError("gh missing")):
            status, reason = _verify_record_attestation(record_bytes, "owner/repo")
            self.assertEqual((status, reason), ("BLOCKED", "attestation-verification-unavailable"))

    def test_v06_dispatch_preserves_exact_json_and_rejects_oversize_payload(self):
        from types import SimpleNamespace

        record_bytes = b'{\r\n  "record_id": "x", "note": "caf\xc3\xa9"\r\n}\r\n'
        payload = workflow_dispatch_payload(record_bytes)
        self.assertLessEqual(len(payload), 60000)
        self.assertEqual(json.loads(payload)["record"].encode("utf-8"), record_bytes)
        with self.assertRaisesRegex(ReleaseError, "attestation-dispatch-input-too-large"):
            workflow_dispatch_payload(b" " * 60000)
        path = self.repo / "candidate.json"
        path.write_bytes(record_bytes)
        with mock.patch("harness_rig.release.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=b"run url")) as run:
            self.assertEqual(dispatch_record_attestation(record_bytes, "owner/repo"), "run url")
        self.assertIn("release-record-attestation.yml", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["input"], payload)

    def test_v06_attest_cli_dispatches_only_a_live_valid_candidate(self):
        from types import SimpleNamespace

        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        record = self._make_release(artifact)
        path = self.repo / "candidate.json"
        write_immutable_release_record(path, record)
        record_bytes = path.read_bytes()
        changed_path_bytes = b'{"different_record": true}\n'
        api_responses = iter(self._hosted_responses())

        def mutate_candidate_during_lookup(endpoint):
            path.write_bytes(changed_path_bytes)
            return next(api_responses)

        out = io.StringIO()
        with mock.patch("harness_rig.release._gh_api_json", side_effect=mutate_candidate_during_lookup), \
                mock.patch("harness_rig.release.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=b"https://github.test/run")) as dispatch, \
                contextlib.redirect_stdout(out):
            rc = release_provenance_main(["attest", "--record", str(path), "--repository", "owner/repo"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out.getvalue())["status"], "DISPATCHED")
        self.assertIn("--ref", dispatch.call_args.args[0])
        self.assertEqual(dispatch.call_args.kwargs["input"], workflow_dispatch_payload(record_bytes))
        self.assertEqual(path.read_bytes(), changed_path_bytes)

        blocked = replace(record, status="BLOCKED", reasons=("blocked",))
        blocked_path = self.repo / "blocked.json"
        blocked_path.write_text(json.dumps(asdict(blocked)), encoding="utf-8")
        with mock.patch("harness_rig.release._gh_api_json") as api, \
                mock.patch("harness_rig.release.subprocess.run") as dispatch, \
                contextlib.redirect_stdout(io.StringIO()):
            rc = release_provenance_main(["attest", "--record", str(blocked_path), "--repository", "owner/repo"])
        self.assertEqual(rc, 2)
        api.assert_not_called()
        dispatch.assert_not_called()

    def test_v06_workflow_permissions_environment_and_attest_action(self):
        workflow = (Path(__file__).resolve().parents[2] / ".github/workflows/release-record-attestation.yml").read_text(encoding="utf-8")
        validate_job, sign_job = workflow.split("  attest:", 1)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("environment: release-provenance-attestation", workflow)
        self.assertIn("actions: read", validate_job)
        self.assertNotIn("actions: read", sign_job)
        self.assertIn("contents: read", sign_job)
        self.assertIn("artifact-metadata: write", sign_job)
        self.assertIn("id-token: write", sign_job)
        self.assertIn("attestations: write", sign_job)
        self.assertIn("uses: actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26", workflow)
        self.assertIn("subject-path: .candidate/release-record.json", workflow)
        self.assertIn("needs.validate.outputs.record_sha256", workflow)
        self.assertIn("GITHUB_STEP_SUMMARY", workflow)
        self.assertIn("release_provenance.py candidate-summary", workflow)
        self.assertLess(workflow.index("validate-candidate"), workflow.index("candidate-summary"))
        self.assertLess(workflow.index("validate-candidate"), workflow.index("candidate-summary"))

    def test_v07_release_artifact_metadata_is_validated_before_summary(self):
        from harness_rig.canonical import digest
        from harness_rig.release import _record_material, parse_release_record

        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        run, jobs = self._hosted_responses()
        record = self._make_release(artifact, [run, jobs])
        cases = [
            ({"path": "../candidate.zip"}, "release-artifact-path-invalid"),
            ({"size": True}, "release-artifact-size-invalid"),
            ({"size": -1}, "release-artifact-size-invalid"),
            ({"size": "8 | injected"}, "release-artifact-size-invalid"),
            ({"sha256": "a" * 63 + "z"}, "release-artifact-digest-invalid"),
            ({"sha256": "` | injected"}, "release-artifact-digest-invalid"),
        ]
        for changes, expected in cases:
            with self.subTest(expected=expected, changes=changes):
                changed_artifact = replace(record.artifacts[0], **changes)
                changed = replace(record, artifacts=(changed_artifact,), record_id="")
                changed = replace(changed, record_id=digest(_record_material(changed)))
                with self.assertRaisesRegex(ReleaseError, expected):
                    parse_release_record(json.dumps(asdict(changed)).encode("utf-8"))

    def test_v07_candidate_summary_escapes_markdown_in_record_values(self):
        from harness_rig.canonical import digest
        from harness_rig.release import _record_material, parse_release_record

        artifact = self.repo / "artifact.zip"
        artifact.write_bytes(b"candidate")
        run, jobs = self._hosted_responses()
        record = self._make_release(artifact, [run, jobs])
        changed_artifact = replace(record.artifacts[0], path="[click](x).zip")
        changed = replace(record, artifacts=(changed_artifact,), record_id="")
        changed = replace(changed, record_id=digest(_record_material(changed)))
        record_path = self.repo / "candidate.json"
        record_path.write_text(json.dumps(asdict(changed)), encoding="utf-8")
        output_path = self.repo / "summary.md"
        with contextlib.redirect_stdout(io.StringIO()):
            rc = release_provenance_main([
                "candidate-summary", "--record", str(record_path), "--output", str(output_path),
            ])
        self.assertEqual(rc, 0)
        summary = output_path.read_text(encoding="utf-8")
        self.assertNotIn("[click](x)", summary)
        self.assertIn("&#x5B;click&#x5D;&#x28;x&#x29;&#x2E;zip", summary)
        parsed = parse_release_record(record_path.read_bytes())
        self.assertEqual(parsed.artifacts[0].path, "[click](x).zip")

    def test_migrate_cli_emits_v1_and_keeps_history_qualification_pending_m11(self):
        rc, payload = self._cli(["migrate", "--repo", str(self.repo)])
        self.assertEqual(rc, 0)
        self.assertEqual(payload["schema"], CLI_ENVELOPE_SCHEMA)
        self.assertEqual(payload["data"]["phase"], "COMPLETE")
        self.assertEqual(payload["data"]["history_qualification"], "PENDING_M11")


if __name__ == "__main__":
    unittest.main()
