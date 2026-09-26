from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from harness_rig.acceptance import evaluate_acceptance, verdict_applicable_to
from harness_rig.assurance import AssurancePlan, AssuranceRequirement
from harness_rig.authority import DirectAuthority
from harness_rig.authorization import AuthorizationGrant, validate_grant
from harness_rig.gate import CommandGate, GateRequest
from harness_rig.security import PathBoundaryError, resolve_protected_path
from harness_rig.state import capture_state
from harness_rig.vertical import VerticalSliceRequest, run_vertical_slice


NOW = "2026-09-25T12:00:00Z"
ISSUED = "2026-09-25T11:00:00Z"
FUTURE = "2026-09-25T13:00:00Z"
PAST = "2026-09-25T11:30:00Z"


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
    )
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {p.stderr}")
    return p


class RepoFixture:
    def __init__(self, root: Path):
        self.root = root
        self.repo = root/"repo"
        self.repo.mkdir()
        run_git(self.repo, "init", "-b", "main")
        run_git(self.repo, "config", "user.name", "Harness Rig Test")
        run_git(self.repo, "config", "user.email", "harness-rig@example.invalid")
        (self.repo/"AUTHORITY.md").write_text("authority v1\n", encoding="utf-8")
        (self.repo/"app.txt").write_text("hello\n", encoding="utf-8")
        run_git(self.repo, "add", "-A")
        run_git(self.repo, "commit", "-m", "initial")

    def commit_all(self, message: str):
        run_git(self.repo, "add", "-A")
        run_git(self.repo, "commit", "-m", message)


class HarnessRigM3Tests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.td = tempfile.TemporaryDirectory(prefix="hr-m3-")
        self.base = Path(self.td.name)
        self.fx = RepoFixture(self.base)
        self.repo = self.fx.repo

    def tearDown(self):
        self.td.cleanup()

    def authority(self):
        return DirectAuthority.from_file(self.repo, "AUTHORITY.md", "repository")

    def requirement(self, *, version="experimental-v1", decision="merge"):
        return AssurancePlan.single(
            subject_ref="repository",
            requirement=AssuranceRequirement(
                claim_id="project.command",
                gate_id="command/test",
                gate_contract_version=version,
                decision_for=decision,
                require_authorization=True,
            ),
        )

    def grant(self, *, state=None, authority=None, principal="local-controller",
              action="merge", expires=FUTURE):
        state = state or capture_state(self.repo, "test-repo")
        authority = authority or self.authority()
        return AuthorizationGrant.issue(
            issuer="local-authority",
            principal=principal,
            action=action,
            resource="repository",
            authority_id=authority.authority_id,
            state_id=state.state_id,
            subject_ref="repository",
            issued_at=ISSUED,
            expires_at=expires,
        )

    def receipt(self, *, run_id="run-1", argv=None, input_paths=(), artifact_paths=(),
                expected_executable=None, authority=None):
        authority = authority or self.authority()
        if argv is None:
            argv = (sys.executable, "-S", "-c", "print('ok')")
        return CommandGate.run(GateRequest(
            repo=self.repo,
            repository_id="test-repo",
            claim_id="project.command",
            subject_ref="repository",
            authority=authority,
            run_id=run_id,
            producer_id="test-producer",
            argv=argv,
            input_paths=input_paths,
            artifact_paths=artifact_paths,
            expected_executable=expected_executable,
        ))

    def accept(self, receipt, *, run_id="run-1", grant=None, authority=None,
               state=None, plan=None, principal="local-controller"):
        authority = authority or self.authority()
        state = state or capture_state(self.repo, "test-repo")
        if grant is None:
            grant = self.grant(state=state, authority=authority, principal=principal)
        return evaluate_acceptance(
            repo=self.repo,
            authority=authority,
            current_state=state,
            plan=plan or self.requirement(),
            receipt=receipt,
            grant=grant,
            principal=principal,
            run_id=run_id,
            now=NOW,
            trusted_issuers={"local-authority"},
            resource="repository",
        )

    # Happy path proves the actual M3 vertical slice.
    def test_vertical_slice_happy_path(self):
        authority = self.authority()
        state = capture_state(self.repo, "test-repo")
        grant = self.grant(state=state, authority=authority)
        result = run_vertical_slice(VerticalSliceRequest(
            repo=self.repo,
            repository_id="test-repo",
            authority_path="AUTHORITY.md",
            subject_ref="repository",
            claim_id="project.command",
            argv=(sys.executable, "-S", "-c", "print('vertical')"),
            run_id="vertical-1",
            producer_id="test-producer",
            principal="local-controller",
            decision_for="merge",
            resource="repository",
            now=NOW,
            grant=grant,
        ))
        self.assertEqual(result.topology.formation, "direct-single-process")
        self.assertEqual(result.receipt.outcome, "PASS")
        self.assertEqual(result.verdict.outcome, "ACCEPTED")
        self.assertEqual(result.verdict.decision_for, "merge")

    def test_command_timeout_blocks(self):
        authority = self.authority()
        receipt = CommandGate.run(GateRequest(
            repo=self.repo,
            repository_id="test-repo",
            claim_id="project.command",
            subject_ref="repository",
            authority=authority,
            run_id="run-timeout",
            producer_id="test-producer",
            argv=(sys.executable, "-S", "-c", "import time; time.sleep(1)"),
            timeout_seconds=0.05,
        ))
        self.assertEqual(receipt.outcome, "BLOCKED")

    # M1-F01
    def test_f01_commit_during_session_changes_state_even_when_clean(self):
        before = capture_state(self.repo, "test-repo")
        (self.repo/"app.txt").write_text("changed\n", encoding="utf-8")
        self.fx.commit_all("session change")
        self.assertEqual(run_git(self.repo, "status", "--porcelain").stdout, "")
        after = capture_state(self.repo, "test-repo")
        self.assertNotEqual(before.state_id, after.state_id)
        self.assertNotEqual(before.revision.head_oid, after.revision.head_oid)

    # M1-F02
    def test_f02_verifier_mutation_becomes_mutated_not_pass(self):
        code = "from pathlib import Path; Path('app.txt').write_text('mutated\\n')"
        receipt = self.receipt(argv=(sys.executable, "-S", "-c", code))
        self.assertEqual(receipt.outcome, "MUTATED")
        self.assertIsNone(receipt.certified_state_id)

    # M1-F03
    def test_f03_identical_content_new_revision_keeps_content_id_but_changes_state(self):
        before = capture_state(self.repo, "test-repo")
        run_git(self.repo, "commit", "--allow-empty", "-m", "metadata-only revision")
        after = capture_state(self.repo, "test-repo")
        self.assertEqual(before.content_id, after.content_id)
        self.assertNotEqual(before.revision.head_oid, after.revision.head_oid)
        self.assertNotEqual(before.state_id, after.state_id)

    # M1-F04
    def test_f04_staged_only_edit_changes_index_identity(self):
        before = capture_state(self.repo, "test-repo")
        (self.repo/"app.txt").write_text("staged\n", encoding="utf-8")
        run_git(self.repo, "add", "app.txt")
        after = capture_state(self.repo, "test-repo")
        self.assertNotEqual(before.index_manifest_digest, after.index_manifest_digest)
        self.assertNotEqual(before.state_id, after.state_id)

    # M1-F05
    def test_f05_dirty_consumed_submodule_changes_state(self):
        sub = self.base/"sub"
        sub.mkdir()
        run_git(sub, "init", "-b", "main")
        run_git(sub, "config", "user.name", "Sub Test")
        run_git(sub, "config", "user.email", "sub@example.invalid")
        (sub/"lib.txt").write_text("v1\n")
        run_git(sub, "add", "-A")
        run_git(sub, "commit", "-m", "sub initial")

        p = subprocess.run(
            ["git", "-C", str(self.repo), "-c", "protocol.file.allow=always",
             "submodule", "add", str(sub), "vendor/sub"],
            text=True, capture_output=True,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        self.fx.commit_all("add submodule")

        before = capture_state(self.repo, "test-repo")
        (self.repo/"vendor/sub/lib.txt").write_text("dirty\n")
        after = capture_state(self.repo, "test-repo")
        self.assertNotEqual(before.state_id, after.state_id)
        self.assertIn("DIRTY", after.submodules[0].status)

    # M1-F06
    def test_f06_ignored_consumed_input_stales_receipt_without_source_state_change(self):
        (self.repo/".gitignore").write_text("runtime.flag\n")
        self.fx.commit_all("ignore runtime input")
        (self.repo/"runtime.flag").write_text("A\n")
        before = capture_state(self.repo, "test-repo")
        authority = self.authority()
        receipt = self.receipt(input_paths=("runtime.flag",), authority=authority)
        self.assertEqual(receipt.outcome, "PASS")
        grant = self.grant(state=before, authority=authority)
        (self.repo/"runtime.flag").write_text("B\n")
        after = capture_state(self.repo, "test-repo")
        self.assertEqual(before.state_id, after.state_id)
        verdict = self.accept(receipt, state=after, grant=grant, authority=authority)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertTrue(any(x.startswith("input-binding-stale") for x in verdict.reasons))

    # M1-F07
    def test_f07_expired_grant_blocks_acceptance(self):
        receipt = self.receipt()
        state = capture_state(self.repo, "test-repo")
        authority = self.authority()
        expired = self.grant(state=state, authority=authority, expires=PAST)
        verdict = self.accept(receipt, state=state, authority=authority, grant=expired)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("authorization-invalid:expired", verdict.reasons)

    # M1-F08
    def test_f08_state_bound_grant_invalid_after_state_change(self):
        authority = self.authority()
        s0 = capture_state(self.repo, "test-repo")
        grant = self.grant(state=s0, authority=authority)
        (self.repo/"app.txt").write_text("new state\n")
        s1 = capture_state(self.repo, "test-repo")
        gv = validate_grant(
            grant,
            principal="local-controller",
            action="merge",
            resource="repository",
            authority_id=authority.authority_id,
            state_id=s1.state_id,
            subject_ref="repository",
            now=NOW,
            trusted_issuers={"local-authority"},
        )
        self.assertEqual(gv.outcome, "INVALID")
        self.assertEqual(gv.reason, "state-binding-mismatch")

    # M1-F09
    def test_f09_nondelegable_grant_rejected_for_other_principal(self):
        authority = self.authority()
        state = capture_state(self.repo, "test-repo")
        grant = self.grant(state=state, authority=authority, principal="p1")
        gv = validate_grant(
            grant,
            principal="p2",
            action="merge",
            resource="repository",
            authority_id=authority.authority_id,
            state_id=state.state_id,
            subject_ref="repository",
            now=NOW,
            trusted_issuers={"local-authority"},
        )
        self.assertEqual(gv.outcome, "INVALID")
        self.assertEqual(gv.reason, "principal-mismatch-nondelegable")

    # M1-F10
    def test_f10_receipt_from_other_run_rejected(self):
        receipt = self.receipt(run_id="run-a")
        state = capture_state(self.repo, "test-repo")
        authority = self.authority()
        grant = self.grant(state=state, authority=authority)
        verdict = self.accept(
            receipt, run_id="run-b", state=state, authority=authority, grant=grant
        )
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("wrong-run-or-replay", verdict.reasons)

    # M1-F11
    def test_f11_outdated_gate_contract_rejected(self):
        receipt = self.receipt()
        state = capture_state(self.repo, "test-repo")
        authority = self.authority()
        plan = self.requirement(version="experimental-v2")
        grant = self.grant(state=state, authority=authority)
        verdict = self.accept(receipt, state=state, authority=authority, grant=grant, plan=plan)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("gate-contract-mismatch", verdict.reasons)

    # M1-F12
    def test_f12_mutated_referenced_artifact_rejected(self):
        (self.repo/".gitignore").write_text("artifact.log\n")
        self.fx.commit_all("ignore artifact")
        (self.repo/"artifact.log").write_text("evidence v1\n")
        authority = self.authority()
        state = capture_state(self.repo, "test-repo")
        receipt = self.receipt(artifact_paths=("artifact.log",), authority=authority)
        grant = self.grant(state=state, authority=authority)
        (self.repo/"artifact.log").write_text("tampered\n")
        state2 = capture_state(self.repo, "test-repo")
        self.assertEqual(state.state_id, state2.state_id)
        verdict = self.accept(receipt, state=state2, authority=authority, grant=grant)
        self.assertEqual(verdict.outcome, "REWORK")
        self.assertTrue(any(x.startswith("artifact-integrity-failure") for x in verdict.reasons))

    # M1-F13
    def test_f13_merge_verdict_not_applicable_to_deploy(self):
        receipt = self.receipt()
        state = capture_state(self.repo, "test-repo")
        authority = self.authority()
        grant = self.grant(state=state, authority=authority)
        verdict = self.accept(receipt, state=state, authority=authority, grant=grant)
        self.assertEqual(verdict.outcome, "ACCEPTED")
        self.assertTrue(verdict_applicable_to(verdict, "merge"))
        self.assertFalse(verdict_applicable_to(verdict, "deploy"))

    # M1-F14
    def test_f14_parent_traversal_rejected(self):
        with self.assertRaises(PathBoundaryError):
            resolve_protected_path(self.repo, "../escape.txt")

    # M1-F15
    def test_f15_link_escape_rejected(self):
        outside = self.base/"outside"
        outside.mkdir()
        link = self.repo/"protected-link"
        try:
            os.symlink(outside, link, target_is_directory=True)
        except OSError as exc:
            if os.name != "nt" or getattr(exc, "winerror", None) != 1314:
                raise
            result = subprocess.run(
                ["cmd", "/d", "/c", "mklink", "/J", str(link), str(outside)],
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(
                result.returncode, 0, (result.stdout or "") + (result.stderr or "")
            )
        with self.assertRaises(PathBoundaryError):
            resolve_protected_path(self.repo, "protected-link/secret.txt")

    # M1-F16
    def test_f16_wrong_executable_from_path_blocks_gate(self):
        fakebin = self.base/"fakebin"
        fakebin.mkdir()
        fake = fakebin/"python3"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)

        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(fakebin) + os.pathsep + old_path
        try:
            receipt = self.receipt(
                argv=("python3", "-c", "print('should not trust')"),
                expected_executable=sys.executable,
            )
        finally:
            os.environ["PATH"] = old_path
        self.assertEqual(receipt.outcome, "BLOCKED")

    # Additional M3-V02
    def test_not_run_gate_cannot_be_accepted(self):
        authority = self.authority()
        state = capture_state(self.repo, "test-repo")
        receipt = CommandGate.run(GateRequest(
            repo=self.repo,
            repository_id="test-repo",
            claim_id="project.command",
            subject_ref="repository",
            authority=authority,
            run_id="run-1",
            producer_id="test-producer",
            argv=None,
        ))
        self.assertEqual(receipt.outcome, "NOT_RUN")
        grant = self.grant(state=state, authority=authority)
        verdict = self.accept(receipt, state=state, authority=authority, grant=grant)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("required-gate-not_run", verdict.reasons)

    # Additional M3-V03 state freshness
    def test_source_state_change_invalidates_receipt(self):
        receipt = self.receipt()
        authority = self.authority()
        old_state = capture_state(self.repo, "test-repo")
        old_grant = self.grant(state=old_state, authority=authority)
        (self.repo/"app.txt").write_text("changed after receipt\n")
        current = capture_state(self.repo, "test-repo")
        verdict = self.accept(receipt, state=current, authority=authority, grant=old_grant)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("state-stale-or-not-certified", verdict.reasons)

    # Additional M3-V03 authority freshness isolated from repository state.
    def test_authority_change_invalidates_receipt(self):
        # Make authority ignored, then commit the ignore rule and remove tracked authority.
        run_git(self.repo, "rm", "--cached", "AUTHORITY.md")
        (self.repo/".gitignore").write_text("AUTHORITY.md\n")
        self.fx.commit_all("authority is direct external-style input")
        (self.repo/"AUTHORITY.md").write_text("authority v1\n")
        authority_v1 = self.authority()
        state = capture_state(self.repo, "test-repo")
        receipt = self.receipt(authority=authority_v1)
        grant = self.grant(state=state, authority=authority_v1)
        (self.repo/"AUTHORITY.md").write_text("authority v2\n")
        authority_v2 = self.authority()
        state2 = capture_state(self.repo, "test-repo")
        self.assertEqual(state.state_id, state2.state_id)
        verdict = self.accept(receipt, state=state2, authority=authority_v2, grant=grant)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("authority-stale", verdict.reasons)

    # M3-V05
    def test_missing_authorization_blocks(self):
        receipt = self.receipt()
        state = capture_state(self.repo, "test-repo")
        authority = self.authority()
        verdict = evaluate_acceptance(
            repo=self.repo,
            authority=authority,
            current_state=state,
            plan=self.requirement(),
            receipt=receipt,
            grant=None,
            principal="local-controller",
            run_id="run-1",
            now=NOW,
            trusted_issuers={"local-authority"},
            resource="repository",
        )
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("authorization-unverifiable:missing-grant", verdict.reasons)


if __name__ == "__main__":
    unittest.main(verbosity=2)
