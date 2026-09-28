from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from harness_rig.architecture_gate import (
    ArchitectureGate,
    ArchitectureGateRequest,
    ArchitecturePolicy,
    ArchitectureRule,
    evaluate_architecture,
    load_architecture_policy_file,
)
from harness_rig.authority import DirectAuthority
from harness_rig.gate import GateClaim, GateOutcome
from harness_rig.mutation_gate import MutationCase, run_mutation_case, validate_mutation_map
from harness_rig.playwright_gate import (
    PlaywrightGate,
    PlaywrightGateRequest,
    RequiredScenario,
    RUNTIME_OBSERVATION_SCHEMA,
    RuntimeObservation,
    evaluate_playwright_report,
)


ROOT = Path(__file__).resolve().parents[2]


def run_git(repo: Path, *args: str) -> None:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise AssertionError(p.stderr)


def init_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.name", "Harness Rig M9")
    run_git(repo, "config", "user.email", "m9@example.invalid")
    (repo / ".gitignore").write_text("test-results/\n", encoding="utf-8")
    (repo / "AUTHORITY.md").write_text("authority\n", encoding="utf-8")
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "-m", "initial")
    return repo


def report(title: str = "critical journey", statuses=("passed",), retries=None, project="chromium"):
    if retries is None:
        retries = tuple(range(len(statuses)))
    return {
        "suites": [{
            "title": "web",
            "specs": [{
                "title": title,
                "tests": [{
                    "projectName": project,
                    "results": [
                        {"status": status, "retry": retry, "attachments": []}
                        for status, retry in zip(statuses, retries)
                    ],
                }],
            }],
        }],
        "errors": [],
    }


def runtime(root: Path, *, namespace="m9-data", shared=False, console=(), network=()):
    return RuntimeObservation(
        RUNTIME_OBSERVATION_SCHEMA,
        str(root.resolve()),
        namespace,
        shared,
        tuple(console),
        tuple(network),
    )


class HarnessRigM9GatePlatformTests(unittest.TestCase):
    def test_t01_minimal_common_gate_claim_and_outcome_semantics(self):
        claim = GateClaim.create(
            claim_id="web.checkout",
            kind="web.acceptance",
            gate_id="playwright/test",
        )
        self.assertEqual(claim.schema, "harness-rig/gate-claim/experimental-v1")
        self.assertTrue(claim.required)
        self.assertEqual(
            {f.name for f in fields(claim)},
            {"schema", "claim_id", "kind", "gate_id", "gate_contract_version", "required"},
        )
        passed = GateOutcome.create("PASS", attempt_count=1)
        self.assertEqual(passed.outcome, "PASS")
        with self.assertRaises(ValueError):
            GateOutcome.create("PASS", reasons=("not-clean",))
        with self.assertRaises(ValueError):
            GateOutcome.create("FAIL")
        with self.assertRaises(ValueError):
            GateOutcome.create("MAGIC", reasons=("x",))

    def test_t02_actual_architecture_policy_passes_current_package(self):
        policy = load_architecture_policy_file(ROOT / "governance" / "architecture-policy.json")
        result = evaluate_architecture(ROOT, policy)
        self.assertEqual(result.outcome.outcome, "PASS")
        self.assertGreaterEqual(len(result.checked_files), 7)
        self.assertEqual(result.violations, ())

    def test_v05_deliberate_architecture_violation_is_detected(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-arch-") as td:
            root = Path(td)
            pkg = root / "core"
            pkg.mkdir()
            (pkg / "policy.py").write_text("from harness_rig.openspec import OpenSpecAdapter\n", encoding="utf-8")
            policy = ArchitecturePolicy(
                "harness-rig/architecture-policy/experimental-v1",
                "test-policy",
                (ArchitectureRule(
                    "inward-only",
                    ("core/*.py",),
                    ("harness_rig.openspec",),
                ),),
            )
            result = evaluate_architecture(root, policy)
            self.assertEqual(result.outcome.outcome, "FAIL")
            self.assertEqual(len(result.violations), 1)
            self.assertEqual(result.violations[0].imported, "harness_rig.openspec")

    def test_architecture_rule_with_no_sources_blocks_instead_of_silently_passing(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-arch-empty-") as td:
            policy = ArchitecturePolicy(
                "harness-rig/architecture-policy/experimental-v1",
                "test-policy",
                (ArchitectureRule("missing", ("nothing/*.py",), ("x",)),),
            )
            result = evaluate_architecture(Path(td), policy)
            self.assertEqual(result.outcome.outcome, "BLOCKED")
            self.assertIn("rule-source-missing:missing", result.outcome.reasons)

    def test_architecture_gate_issues_state_bound_receipt(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-arch-receipt-") as td:
            root = Path(td)
            repo = init_repo(root)
            (repo / "core.py").write_text("import json\n", encoding="utf-8")
            policy_path = repo / "architecture.json"
            policy_path.write_text(json.dumps({
                "schema": "harness-rig/architecture-policy/experimental-v1",
                "policy_id": "local",
                "rules": [{
                    "rule_id": "no-os",
                    "source_globs": ["core.py"],
                    "forbidden_import_prefixes": ["subprocess"],
                }],
            }), encoding="utf-8")
            run_git(repo, "add", "-A")
            run_git(repo, "commit", "-m", "architecture")
            policy = load_architecture_policy_file(policy_path)
            claim = GateClaim.create(claim_id="architecture.core", kind="architecture", gate_id="architecture/python-imports")
            result = ArchitectureGate.run(ArchitectureGateRequest(
                repo=repo,
                repository_id="m9-arch",
                authority=DirectAuthority.from_file(repo, "AUTHORITY.md"),
                claim=claim,
                run_id="arch-1",
                producer_id="harness-rig/architecture-gate",
                policy=policy,
                policy_path="architecture.json",
            ))
            self.assertEqual(result.receipt.outcome, "PASS")
            self.assertIsNotNone(result.receipt.certified_state_id)
            self.assertEqual(result.receipt.input_bindings[0].locator, "architecture.json")

    def test_t03_required_playwright_scenario_passes_with_clean_runtime_observation(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-pw-") as td:
            root = Path(td)
            result = evaluate_playwright_report(
                report(),
                required_scenarios=(RequiredScenario("critical", "critical journey", "chromium"),),
                runtime=runtime(root),
                expected_worktree=str(root),
                expected_data_namespace="m9-data",
            )
            self.assertEqual(result.outcome.outcome, "PASS")
            self.assertEqual(result.scenarios[0].status, "PASS")

    def test_v01_required_playwright_skip_cannot_pass(self):
        result = evaluate_playwright_report(
            report(statuses=("skipped",), retries=(0,)),
            required_scenarios=(RequiredScenario("critical", "critical journey"),),
        )
        self.assertEqual(result.outcome.outcome, "FAIL")
        self.assertIn("required-scenario-not-run:critical:skipped", result.outcome.reasons)

    def test_v01_required_playwright_no_test_cannot_pass(self):
        result = evaluate_playwright_report(
            {"suites": [], "errors": []},
            required_scenarios=(RequiredScenario("critical", "critical journey"),),
        )
        self.assertEqual(result.outcome.outcome, "FAIL")
        self.assertIn("required-scenario-missing:critical", result.outcome.reasons)

    def test_v02_flaky_retry_remains_visible_and_is_strict_by_default(self):
        strict = evaluate_playwright_report(
            report(statuses=("failed", "passed"), retries=(0, 1)),
            required_scenarios=(RequiredScenario("critical", "critical journey"),),
        )
        self.assertEqual(strict.scenarios[0].status, "FLAKY")
        self.assertTrue(strict.scenarios[0].flaky)
        self.assertEqual(strict.scenarios[0].retry_indexes, (0, 1))
        self.assertEqual(strict.outcome.outcome, "FAIL")
        relaxed = evaluate_playwright_report(
            report(statuses=("failed", "passed"), retries=(0, 1)),
            required_scenarios=(RequiredScenario("critical", "critical journey"),),
            fail_on_flaky=False,
        )
        self.assertEqual(relaxed.outcome.outcome, "PASS")
        self.assertTrue(relaxed.outcome.flaky)

    def test_v04_wrong_worktree_blocks_web_acceptance(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-pw-a-") as a, tempfile.TemporaryDirectory(prefix="hr-m9-pw-b-") as b:
            result = evaluate_playwright_report(
                report(),
                required_scenarios=(RequiredScenario("critical", "critical journey"),),
                runtime=runtime(Path(a)),
                expected_worktree=b,
            )
        self.assertEqual(result.outcome.outcome, "FAIL")
        self.assertIn("runtime-wrong-worktree", result.outcome.reasons)

    def test_v04_shared_data_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-pw-data-") as td:
            result = evaluate_playwright_report(
                report(),
                required_scenarios=(RequiredScenario("critical", "critical journey"),),
                runtime=runtime(Path(td), shared=True),
            )
        self.assertEqual(result.outcome.outcome, "FAIL")
        self.assertIn("runtime-shared-data", result.outcome.reasons)

    def test_v04_console_and_network_failures_are_explicit(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-pw-signals-") as td:
            result = evaluate_playwright_report(
                report(),
                required_scenarios=(RequiredScenario("critical", "critical journey"),),
                runtime=runtime(Path(td), console=("TypeError",), network=("POST https://unexpected.invalid",)),
            )
        self.assertEqual(result.outcome.outcome, "FAIL")
        self.assertIn("runtime-console-errors", result.outcome.reasons)
        self.assertIn("runtime-unexpected-network", result.outcome.reasons)

    def test_playwright_provider_subprocess_emits_receipt_and_references_native_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-pw-run-") as td:
            root = Path(td)
            repo = init_repo(root)
            runner = repo / "fake_runner.py"
            runner.write_text(
                "import json, os\n"
                "from pathlib import Path\n"
                "root = Path.cwd()\n"
                "report_path = Path(os.environ['PLAYWRIGHT_JSON_OUTPUT_NAME'])\n"
                "trace = root / 'test-results' / 'trace.zip'\n"
                "trace.parent.mkdir(parents=True, exist_ok=True)\n"
                "trace.write_bytes(b'trace')\n"
                "report = {'suites':[{'specs':[{'title':'critical journey','tests':[{'projectName':'chromium','results':[{'status':'passed','retry':0,'attachments':[{'name':'trace','path':str(trace)}]}]}]}]}],'errors':[]}\n"
                "report_path.write_text(json.dumps(report))\n"
                "runtime = {'schema':'harness-rig/playwright-runtime-observation/experimental-v1','worktree_root':str(root.resolve()),'data_namespace':'m9-data','shared_data':False,'console_errors':[],'unexpected_network':[]}\n"
                "(root/'test-results'/'runtime.json').write_text(json.dumps(runtime))\n",
                encoding="utf-8",
            )
            run_git(repo, "add", "-A")
            run_git(repo, "commit", "-m", "runner")
            claim = GateClaim.create(claim_id="web.critical", kind="web.acceptance", gate_id="playwright/test")
            result = PlaywrightGate.run(PlaywrightGateRequest(
                repo=repo,
                repository_id="m9-pw",
                authority=DirectAuthority.from_file(repo, "AUTHORITY.md"),
                claim=claim,
                run_id="pw-1",
                producer_id="harness-rig/playwright-gate",
                argv=(sys.executable, str(runner)),
                report_path="test-results/report.json",
                runtime_observation_path="test-results/runtime.json",
                required_scenarios=(RequiredScenario("critical", "critical journey", "chromium"),),
                expected_worktree=str(repo),
                expected_data_namespace="m9-data",
            ))
            self.assertEqual(result.runner_exit_code, 0)
            self.assertEqual(result.receipt.outcome, "PASS")
            kinds = {artifact.kind for artifact in result.receipt.artifacts}
            self.assertIn("playwright-json-report", kinds)
            self.assertIn("playwright-runtime-observation", kinds)
            self.assertIn("playwright-native-artifact", kinds)

    def test_playwright_provider_forbids_pass_with_no_tests_escape(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-pw-escape-") as td:
            repo = init_repo(Path(td))
            claim = GateClaim.create(claim_id="web.critical", kind="web.acceptance", gate_id="playwright/test")
            with self.assertRaisesRegex(ValueError, "pass-with-no-tests"):
                PlaywrightGate.run(PlaywrightGateRequest(
                    repo=repo,
                    repository_id="m9-pw",
                    authority=DirectAuthority.from_file(repo, "AUTHORITY.md"),
                    claim=claim,
                    run_id="pw-escape",
                    producer_id="harness-rig/playwright-gate",
                    argv=(sys.executable, "runner.py", "--pass-with-no-tests"),
                    report_path="test-results/report.json",
                    required_scenarios=(RequiredScenario("critical", "critical journey"),),
                ))

    def test_v03_healer_oracle_mutation_reopens_authority_even_if_detector_stays_green(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-oracle-") as td:
            root = Path(td)
            (root / "oracle.txt").write_text("expected=secure\n", encoding="utf-8")
            case = MutationCase.create(
                invariant_id="protected-oracle-authority",
                mutant_id="healer-weakens-oracle",
                detector_id="blind-detector",
                relative_path="oracle.txt",
                search="expected=secure",
                replacement="expected=permissive",
                detector_argv=(sys.executable, "-c", "pass"),
                protected_oracle=True,
            )
            result = run_mutation_case(root, case)
            self.assertTrue(result.authority_reopened)
            self.assertNotEqual(result.authority_before_id, result.authority_after_id)
            self.assertEqual(result.mutant_status, "SURVIVED")
            self.assertEqual(result.outcome.outcome, "FAIL")

    def test_t04_mutation_gate_kills_mutant_when_detector_is_sensitive(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-mutant-red-") as td:
            root = Path(td)
            (root / "value.txt").write_text("SAFE\n", encoding="utf-8")
            detector = "from pathlib import Path; import sys; sys.exit(0 if Path('value.txt').read_text().strip() == 'SAFE' else 1)"
            case = MutationCase.create(
                invariant_id="value-remains-safe",
                mutant_id="safe-to-unsafe",
                detector_id="value-detector",
                relative_path="value.txt",
                search="SAFE",
                replacement="UNSAFE",
                detector_argv=(sys.executable, "-c", detector),
            )
            result = run_mutation_case(root, case)
            self.assertEqual(result.baseline.outcome, "PASS")
            self.assertEqual(result.mutant.outcome, "FAIL")
            self.assertEqual(result.mutant_status, "KILLED")
            self.assertEqual(result.outcome.outcome, "PASS")

    def test_v06_mutation_green_survivor_proves_detector_gap(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-mutant-green-") as td:
            root = Path(td)
            (root / "config.txt").write_text("checked=SAFE\nuncovered=STRICT\n", encoding="utf-8")
            detector = "from pathlib import Path; import sys; sys.exit(0 if 'checked=SAFE' in Path('config.txt').read_text() else 1)"
            case = MutationCase.create(
                invariant_id="uncovered-policy-remains-strict",
                mutant_id="strict-to-permissive",
                detector_id="partial-detector",
                relative_path="config.txt",
                search="uncovered=STRICT",
                replacement="uncovered=PERMISSIVE",
                detector_argv=(sys.executable, "-c", detector),
            )
            result = run_mutation_case(root, case)
            self.assertEqual(result.baseline.outcome, "PASS")
            self.assertEqual(result.mutant.outcome, "PASS")
            self.assertEqual(result.mutant_status, "SURVIVED")
            self.assertEqual(result.outcome.outcome, "FAIL")
            self.assertIn("mutant-survived", result.outcome.reasons)

    def test_mutation_gate_blocks_when_baseline_detector_is_not_green(self):
        with tempfile.TemporaryDirectory(prefix="hr-m9-mutant-baseline-") as td:
            root = Path(td)
            (root / "value.txt").write_text("SAFE\n", encoding="utf-8")
            case = MutationCase.create(
                invariant_id="baseline",
                mutant_id="x",
                detector_id="red-baseline",
                relative_path="value.txt",
                search="SAFE",
                replacement="UNSAFE",
                detector_argv=(sys.executable, "-c", "import sys; sys.exit(2)"),
            )
            result = run_mutation_case(root, case)
            self.assertEqual(result.outcome.outcome, "BLOCKED")
            self.assertEqual(result.mutant_status, "NOT_APPLIED")

    def test_t05_mutation_map_requires_unique_mutant_identity(self):
        case = MutationCase.create(
            invariant_id="a",
            mutant_id="same",
            detector_id="d1",
            relative_path="x.txt",
            search="x",
            replacement="y",
            detector_argv=(sys.executable, "-c", "pass"),
        )
        duplicate = MutationCase.create(
            invariant_id="b",
            mutant_id="same",
            detector_id="d2",
            relative_path="y.txt",
            search="x",
            replacement="z",
            detector_argv=(sys.executable, "-c", "pass"),
        )
        with self.assertRaisesRegex(ValueError, "duplicate-mutation-mutant-id"):
            validate_mutation_map((case, duplicate))


if __name__ == "__main__":
    unittest.main()
