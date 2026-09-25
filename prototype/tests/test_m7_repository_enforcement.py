from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness_rig.repository_ci import (
    CiObligationResult,
    ObligationSpec,
    RepositoryCiPolicy,
    create_ci_result,
    resolve_ci_obligations,
    validate_ci_required,
)


ROOT = Path(__file__).resolve().parents[2]
SHA = "a" * 40
OTHER_SHA = "b" * 40


def policy(*, privileged_ordinary: bool = False) -> RepositoryCiPolicy:
    return RepositoryCiPolicy.create(
        policy_id="harness-rig/repository-ci/r8.7-test",
        obligations=(
            ObligationSpec("ordinary", "harness-rig/ci/ordinary-v1", True, privileged_ordinary),
            ObligationSpec("kb-integrity", "harness-rig/ci/kb-integrity-v1", True, False),
            ObligationSpec("governance", "harness-rig/ci/governance-v1", False, False),
        ),
        governance_sensitive_paths=(
            ".github/workflows",
            "governance",
            "verification/ci_obligations.py",
            "prototype/harness_rig/repository_ci.py",
        ),
    )


def artifact(*, paths=("prototype/harness_rig/cli.py",), event="pull_request", subject="pull_request:17", trust="trusted", sha=SHA, p=None):
    return resolve_ci_obligations(
        policy=p or policy(),
        evaluated_sha=sha,
        event_name=event,
        event_subject=subject,
        trust_mode=trust,
        changed_paths=paths,
    )


def passing_results(a, p=None):
    p = p or policy()
    return tuple(
        create_ci_result(
            artifact=a,
            obligation_id=item.obligation_id,
            producer_id=item.producer_id,
            outcome="PASS",
            privileged=item.privileged,
        )
        for item in a.expected_results
    )


class HarnessRigM7RepositoryTests(unittest.TestCase):
    def test_t01_obligation_artifact_binds_revision_modules_and_expected_result_identities(self):
        a = artifact(paths=("prototype/harness_rig/cli.py", "references/roadmap.md"))
        self.assertEqual(a.evaluated_sha, SHA)
        self.assertEqual(a.affected_modules, ("knowledge", "prototype"))
        self.assertEqual(a.mandatory_obligations, ("kb-integrity", "ordinary"))
        self.assertEqual({x.obligation_id for x in a.expected_results}, set(a.mandatory_obligations))
        self.assertEqual(a.recompute_id(), a.artifact_id)

    def test_v01_prerequisite_failure_is_explicitly_blocked_not_hidden_by_aggregator(self):
        p = policy()
        a = artifact(p=p)
        results = list(passing_results(a, p))
        ordinary = next(x for x in results if x.obligation_id == "ordinary")
        results[results.index(ordinary)] = create_ci_result(
            artifact=a,
            obligation_id="ordinary",
            producer_id="harness-rig/ci/ordinary-v1",
            outcome="FAIL",
        )
        verdict = validate_ci_required(policy=p, artifact=a, results=results)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("mandatory-result-fail:ordinary", verdict.reasons)

    def test_v02_skipped_or_missing_mandatory_job_is_detected(self):
        p = policy()
        a = artifact(p=p)
        skipped = (
            create_ci_result(artifact=a, obligation_id="ordinary", producer_id="harness-rig/ci/ordinary-v1", outcome="SKIPPED"),
            create_ci_result(artifact=a, obligation_id="kb-integrity", producer_id="harness-rig/ci/kb-integrity-v1", outcome="PASS"),
        )
        verdict = validate_ci_required(policy=p, artifact=a, results=skipped)
        self.assertIn("mandatory-result-skipped:ordinary", verdict.reasons)
        missing = validate_ci_required(policy=p, artifact=a, results=skipped[1:])
        self.assertIn("missing-result:ordinary", missing.reasons)

    def test_v03_merge_group_subject_is_first_class_and_same_sha_results_pass(self):
        p = policy()
        a = artifact(event="merge_group", subject="merge_group:gh-readonly-queue/main/pr-17", p=p)
        self.assertEqual(a.event_name, "merge_group")
        self.assertEqual(validate_ci_required(policy=p, artifact=a, results=passing_results(a, p)).outcome, "PASS")

    def test_v04_untrusted_fork_cannot_satisfy_required_with_privileged_result(self):
        p = policy(privileged_ordinary=True)
        a = artifact(trust="untrusted_fork", p=p)
        verdict = validate_ci_required(policy=p, artifact=a, results=passing_results(a, p))
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("privileged-result-in-untrusted-fork:ordinary", verdict.reasons)

    def test_v05_resolver_or_workflow_self_modification_requires_governance_result(self):
        p = policy()
        for changed in ("prototype/harness_rig/repository_ci.py", ".github/workflows/ci-required.yml"):
            with self.subTest(changed=changed):
                a = artifact(paths=(changed,), p=p)
                self.assertIn("governance", a.mandatory_obligations)
                without_governance = tuple(x for x in passing_results(a, p) if x.obligation_id != "governance")
                verdict = validate_ci_required(policy=p, artifact=a, results=without_governance)
                self.assertIn("missing-result:governance", verdict.reasons)

    def test_v05_wrong_sha_fails_closed(self):
        p = policy()
        a = artifact(p=p)
        wrong = artifact(sha=OTHER_SHA, p=p)
        results = list(passing_results(a, p))
        bad = create_ci_result(artifact=wrong, obligation_id="ordinary", producer_id="harness-rig/ci/ordinary-v1", outcome="PASS")
        results = [bad if x.obligation_id == "ordinary" else x for x in results]
        verdict = validate_ci_required(policy=p, artifact=a, results=results)
        self.assertIn("wrong-sha:ordinary", verdict.reasons)
        self.assertIn("wrong-result-identity:ordinary", verdict.reasons)

    def test_v05_wrong_producer_and_event_fail_closed(self):
        p = policy()
        a = artifact(p=p)
        wrong_producer = create_ci_result(artifact=a, obligation_id="ordinary", producer_id="lookalike/ci", outcome="PASS")
        good_kb = create_ci_result(artifact=a, obligation_id="kb-integrity", producer_id="harness-rig/ci/kb-integrity-v1", outcome="PASS")
        verdict = validate_ci_required(policy=p, artifact=a, results=(wrong_producer, good_kb))
        self.assertIn("wrong-producer:ordinary", verdict.reasons)
        self.assertIn("wrong-result-identity:ordinary", verdict.reasons)

        other_event = artifact(event="push", subject="push:refs/heads/main", p=p)
        wrong_event_result = create_ci_result(artifact=other_event, obligation_id="ordinary", producer_id="harness-rig/ci/ordinary-v1", outcome="PASS")
        verdict = validate_ci_required(policy=p, artifact=a, results=(wrong_event_result, good_kb))
        self.assertIn("wrong-event:ordinary", verdict.reasons)

    def test_artifact_tamper_or_policy_change_fails_closed(self):
        p = policy()
        a = artifact(p=p)
        tampered = dataclasses.replace(a, mandatory_obligations=("ordinary",))
        verdict = validate_ci_required(policy=p, artifact=tampered, results=())
        self.assertIn("obligation-artifact-integrity-failure", verdict.reasons)
        self.assertIn("mandatory-obligations-mismatch", verdict.reasons)

        p2 = RepositoryCiPolicy.create(
            policy_id=p.policy_id + "-changed",
            obligations=p.obligations,
            governance_sensitive_paths=p.governance_sensitive_paths,
        )
        verdict = validate_ci_required(policy=p2, artifact=a, results=passing_results(a, p))
        self.assertIn("policy-identity-mismatch", verdict.reasons)

    def test_duplicate_and_unexpected_results_fail_closed(self):
        p = policy()
        a = artifact(p=p)
        results = list(passing_results(a, p))
        results.append(results[0])
        verdict = validate_ci_required(policy=p, artifact=a, results=results)
        self.assertTrue(any(r.startswith("duplicate-result:") for r in verdict.reasons))

        extra = CiObligationResult(
            schema=results[0].schema,
            result_id="sha256:" + "0" * 64,
            obligation_id="not-required",
            result_key="sha256:" + "1" * 64,
            evaluated_sha=SHA,
            event_name=a.event_name,
            event_subject=a.event_subject,
            producer_id="unknown",
            outcome="PASS",
            privileged=False,
        )
        verdict = validate_ci_required(policy=p, artifact=a, results=tuple(passing_results(a, p)) + (extra,))
        self.assertIn("unexpected-result:not-required", verdict.reasons)

    def test_generated_kb_inputs_remain_covered_by_kb_integrity_obligation(self):
        p = policy()
        for changed in ("references/roadmap.md", "manifest.jsonl", "llms.txt"):
            with self.subTest(changed=changed):
                a = artifact(paths=(changed,), p=p)
                self.assertIn("knowledge", a.affected_modules)
                self.assertIn("kb-integrity", a.mandatory_obligations)

    def test_repository_policy_marks_ci_policy_oracles_and_tests_governance_sensitive(self):
        policy_data = json.loads((ROOT / "governance" / "ci-policy.json").read_text(encoding="utf-8"))
        sensitive = set(policy_data["governance_sensitive_paths"])
        for required in (
            ".github/workflows",
            "governance",
            "verification/ci_obligations.py",
            "prototype/harness_rig/repository_ci.py",
            "prototype/harness_rig/acceptance.py",
            "prototype/harness_rig/authorization.py",
            "prototype/harness_rig/state.py",
            "prototype/tests",
        ):
            self.assertIn(required, sensitive)
        enforcement = json.loads((ROOT / "governance" / "github-enforcement-requirements.json").read_text(encoding="utf-8"))
        self.assertEqual(enforcement["required_repository_verdict"]["check_name"], "ci / required")
        self.assertFalse(enforcement["fork_pull_request"]["privileged_actions_allowed"])
        self.assertFalse(enforcement["fork_pull_request"]["pull_request_target_for_untrusted_code"])
        self.assertEqual(enforcement["qualification"], "local-contract-only-until-installed-repository-settings-are-observed")

    def test_workflow_contract_runs_required_after_failures_supports_merge_queue_and_has_no_privileged_pr_target(self):
        text = (ROOT / ".github" / "workflows" / "ci-required.yml").read_text(encoding="utf-8")
        self.assertIn("merge_group:", text)
        self.assertIn("name: ci / required", text)
        self.assertIn("needs: [resolve, ordinary, kb_integrity, governance]", text)
        self.assertIn("if: ${{ always() }}", text)
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("secrets.", text)
        self.assertIn("verification/ci_obligations.py required", text)

    def test_cli_emits_and_validates_obligation_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            changed = tmp / "changed.txt"
            changed.write_text("prototype/harness_rig/cli.py\n", encoding="utf-8")
            artifact_path = tmp / "artifact.json"
            policy_path = ROOT / "governance" / "ci-policy.json"
            tool = ROOT / "verification" / "ci_obligations.py"
            subprocess.run([
                sys.executable, str(tool), "resolve",
                "--policy", str(policy_path),
                "--evaluated-sha", SHA,
                "--event-name", "pull_request",
                "--event-subject", "pull_request:17",
                "--trust-mode", "trusted",
                "--changed-paths-file", str(changed),
                "--output", str(artifact_path),
            ], check=True)
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "harness-rig/ci-obligation-artifact/experimental-v1")
            results = tmp / "results"
            results.mkdir()
            for obligation, producer in (("ordinary", "harness-rig/ci/ordinary-v1"), ("kb-integrity", "harness-rig/ci/kb-integrity-v1")):
                subprocess.run([
                    sys.executable, str(tool), "result",
                    "--artifact", str(artifact_path),
                    "--obligation", obligation,
                    "--producer", producer,
                    "--outcome", "PASS",
                    "--output", str(results / f"{obligation}.json"),
                ], check=True)
            verdict = tmp / "verdict.json"
            subprocess.run([
                sys.executable, str(tool), "required",
                "--policy", str(policy_path),
                "--artifact", str(artifact_path),
                "--results-dir", str(results),
                "--output", str(verdict),
            ], check=True)
            self.assertEqual(json.loads(verdict.read_text(encoding="utf-8"))["outcome"], "PASS")


if __name__ == "__main__":
    unittest.main()
