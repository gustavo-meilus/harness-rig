from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .authority import AuthorityRef
from .canonical import digest, sha256_bytes
from .evidence import ArtifactRef, EvidenceReceipt, InputBinding, artifact_path
from .gate import GateClaim, GateOutcome, _now
from .state import capture_state


PLAYWRIGHT_REPORT_SCHEMA = "harness-rig/playwright-evaluation/experimental-v1"
RUNTIME_OBSERVATION_SCHEMA = "harness-rig/playwright-runtime-observation/experimental-v1"


@dataclass(frozen=True)
class RequiredScenario:
    scenario_id: str
    title: str
    project_name: str | None = None


@dataclass(frozen=True)
class ScenarioObservation:
    scenario_id: str
    title: str
    project_name: str | None
    status: str
    attempts: tuple[str, ...]
    retry_indexes: tuple[int, ...]
    flaky: bool


@dataclass(frozen=True)
class RuntimeObservation:
    schema: str
    worktree_root: str
    data_namespace: str
    shared_data: bool
    console_errors: tuple[str, ...]
    unexpected_network: tuple[str, ...]


@dataclass(frozen=True)
class PlaywrightEvaluation:
    schema: str
    outcome: GateOutcome
    scenarios: tuple[ScenarioObservation, ...]
    runtime: RuntimeObservation | None
    report_digest: str


@dataclass(frozen=True)
class PlaywrightGateRequest:
    repo: Path
    repository_id: str
    authority: AuthorityRef
    claim: GateClaim
    run_id: str
    producer_id: str
    argv: tuple[str, ...]
    report_path: str
    required_scenarios: tuple[RequiredScenario, ...]
    runtime_observation_path: str | None = None
    expected_worktree: str | None = None
    expected_data_namespace: str | None = None
    fail_on_flaky: bool = True
    subject_ref: str = "repository"
    expected_executable: str | None = None
    timeout_seconds: float = 120.0


@dataclass(frozen=True)
class PlaywrightGateResult:
    evaluation: PlaywrightEvaluation | None
    receipt: EvidenceReceipt
    runner_exit_code: int | None
    reasons: tuple[str, ...]


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid-playwright-{field}")
    return value


def _validate_required_scenarios(scenarios: tuple[RequiredScenario, ...]) -> None:
    if not scenarios:
        raise ValueError("playwright-required-scenarios-empty")
    seen: set[str] = set()
    for scenario in scenarios:
        _required_string(scenario.scenario_id, "scenario-id")
        _required_string(scenario.title, "scenario-title")
        if scenario.project_name is not None:
            _required_string(scenario.project_name, "project-name")
        if scenario.scenario_id in seen:
            raise ValueError("duplicate-playwright-scenario-id")
        seen.add(scenario.scenario_id)


def load_runtime_observation(data: dict[str, Any]) -> RuntimeObservation:
    expected = {
        "schema", "worktree_root", "data_namespace", "shared_data",
        "console_errors", "unexpected_network",
    }
    if not isinstance(data, dict) or set(data) != expected:
        raise ValueError("invalid-playwright-runtime-observation")
    if data.get("schema") != RUNTIME_OBSERVATION_SCHEMA:
        raise ValueError("unsupported-playwright-runtime-observation-schema")
    if not isinstance(data["shared_data"], bool):
        raise ValueError("invalid-playwright-runtime-shared-data")
    for field in ("console_errors", "unexpected_network"):
        if not isinstance(data[field], list) or any(not isinstance(x, str) for x in data[field]):
            raise ValueError(f"invalid-playwright-runtime-{field.replace('_', '-')}")
    return RuntimeObservation(
        RUNTIME_OBSERVATION_SCHEMA,
        _required_string(data["worktree_root"], "runtime-worktree"),
        _required_string(data["data_namespace"], "runtime-data-namespace"),
        data["shared_data"],
        tuple(data["console_errors"]),
        tuple(data["unexpected_network"]),
    )


def _iter_specs(suites: Any):
    if not isinstance(suites, list):
        return
    for suite in suites:
        if not isinstance(suite, dict):
            continue
        specs = suite.get("specs", [])
        if isinstance(specs, list):
            for spec in specs:
                if isinstance(spec, dict):
                    yield spec
        yield from _iter_specs(suite.get("suites", []))


def _test_project_name(test: dict[str, Any]) -> str | None:
    value = test.get("projectName")
    if isinstance(value, str) and value:
        return value
    value = test.get("projectId")
    if isinstance(value, str) and value:
        return value
    return None


def _scenario_observation(report: dict[str, Any], required: RequiredScenario) -> ScenarioObservation:
    matches: list[dict[str, Any]] = []
    for spec in _iter_specs(report.get("suites", [])):
        if spec.get("title") != required.title:
            continue
        tests = spec.get("tests", [])
        if not isinstance(tests, list):
            continue
        for test in tests:
            if not isinstance(test, dict):
                continue
            project_name = _test_project_name(test)
            if required.project_name is None or project_name == required.project_name:
                matches.append(test)

    if not matches:
        return ScenarioObservation(
            required.scenario_id, required.title, required.project_name,
            "MISSING", (), (), False,
        )

    attempts: list[str] = []
    retry_indexes: list[int] = []
    any_executed = False
    final_statuses: list[str] = []
    flaky = False
    for test in matches:
        results = test.get("results", [])
        if not isinstance(results, list) or not results:
            final_statuses.append("not-run")
            continue
        statuses: list[str] = []
        retries: list[int] = []
        for result in results:
            if not isinstance(result, dict):
                continue
            status = result.get("status")
            status = status if isinstance(status, str) and status else "unknown"
            retry = result.get("retry", 0)
            retry = retry if isinstance(retry, int) and retry >= 0 else 0
            statuses.append(status)
            retries.append(retry)
            attempts.append(status)
            retry_indexes.append(retry)
            if status not in {"skipped"}:
                any_executed = True
        if statuses:
            final_statuses.append(statuses[-1])
            if len(statuses) > 1 or any(r > 0 for r in retries):
                if statuses[-1] == "passed" and any(s != "passed" for s in statuses[:-1]):
                    flaky = True
                elif any(r > 0 for r in retries):
                    flaky = True
        else:
            final_statuses.append("not-run")

    if not any_executed:
        status = "SKIPPED" if any(s == "skipped" for s in attempts) else "NOT_RUN"
    elif any(s not in {"passed", "skipped"} for s in final_statuses):
        status = "FAIL"
    elif all(s == "skipped" for s in final_statuses):
        status = "SKIPPED"
    elif flaky:
        status = "FLAKY"
    else:
        status = "PASS"
    return ScenarioObservation(
        required.scenario_id, required.title, required.project_name,
        status, tuple(attempts), tuple(retry_indexes), flaky,
    )


def evaluate_playwright_report(
    report: dict[str, Any], *,
    required_scenarios: tuple[RequiredScenario, ...],
    runtime: RuntimeObservation | None = None,
    expected_worktree: str | None = None,
    expected_data_namespace: str | None = None,
    fail_on_flaky: bool = True,
) -> PlaywrightEvaluation:
    _validate_required_scenarios(required_scenarios)
    if not isinstance(report, dict) or not isinstance(report.get("suites", []), list):
        raise ValueError("invalid-playwright-json-report")
    if not isinstance(fail_on_flaky, bool):
        raise ValueError("invalid-playwright-fail-on-flaky")

    observations = tuple(_scenario_observation(report, scenario) for scenario in required_scenarios)
    reasons: list[str] = []
    attempt_count = sum(len(obs.attempts) for obs in observations)
    flaky = any(obs.flaky for obs in observations)

    for obs in observations:
        if obs.status == "MISSING":
            reasons.append(f"required-scenario-missing:{obs.scenario_id}")
        elif obs.status in {"SKIPPED", "NOT_RUN"}:
            reasons.append(f"required-scenario-not-run:{obs.scenario_id}:{obs.status.lower()}")
        elif obs.status == "FAIL":
            reasons.append(f"required-scenario-failed:{obs.scenario_id}")
        elif obs.status == "FLAKY" and fail_on_flaky:
            reasons.append(f"required-scenario-flaky:{obs.scenario_id}")

    errors = report.get("errors", [])
    if isinstance(errors, list) and errors:
        reasons.append("playwright-report-errors")

    if runtime is not None:
        if expected_worktree is not None:
            observed = Path(runtime.worktree_root).resolve()
            expected = Path(expected_worktree).resolve()
            if observed != expected:
                reasons.append("runtime-wrong-worktree")
        if runtime.shared_data:
            reasons.append("runtime-shared-data")
        if expected_data_namespace is not None and runtime.data_namespace != expected_data_namespace:
            reasons.append("runtime-data-namespace-mismatch")
        if runtime.console_errors:
            reasons.append("runtime-console-errors")
        if runtime.unexpected_network:
            reasons.append("runtime-unexpected-network")
    elif expected_worktree is not None or expected_data_namespace is not None:
        reasons.append("runtime-observation-missing")

    if reasons:
        # Missing/not-run required scenarios are not infrastructure uncertainty: the
        # declared acceptance scenario was not demonstrated, so the gate fails.
        outcome = GateOutcome.create(
            "FAIL", reasons=tuple(reasons), attempt_count=attempt_count, flaky=flaky
        )
    else:
        outcome = GateOutcome.create("PASS", attempt_count=attempt_count, flaky=flaky)

    material = {
        "schema": PLAYWRIGHT_REPORT_SCHEMA,
        "outcome": asdict(outcome),
        "scenarios": [asdict(obs) for obs in observations],
        "runtime": asdict(runtime) if runtime is not None else None,
    }
    return PlaywrightEvaluation(
        PLAYWRIGHT_REPORT_SCHEMA, outcome, observations, runtime, digest(material)
    )


def _load_json(path: Path, error: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(error) from exc
    if not isinstance(value, dict):
        raise ValueError(error)
    return value


def _contained(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    if root not in [resolved, *resolved.parents]:
        raise ValueError("playwright-artifact-escapes-repository")
    return resolved


def _attachment_artifacts(repo: Path, report: dict[str, Any]) -> tuple[ArtifactRef, ...]:
    seen: set[str] = set()
    artifacts: list[ArtifactRef] = []
    for spec in _iter_specs(report.get("suites", [])):
        tests = spec.get("tests", []) if isinstance(spec, dict) else []
        if not isinstance(tests, list):
            continue
        for test in tests:
            results = test.get("results", []) if isinstance(test, dict) else []
            if not isinstance(results, list):
                continue
            for result in results:
                attachments = result.get("attachments", []) if isinstance(result, dict) else []
                if not isinstance(attachments, list):
                    continue
                for attachment in attachments:
                    if not isinstance(attachment, dict):
                        continue
                    raw_path = attachment.get("path")
                    if not isinstance(raw_path, str) or not raw_path:
                        continue
                    candidate = Path(raw_path)
                    if not candidate.is_absolute():
                        candidate = repo / candidate
                    try:
                        resolved = _contained(repo, candidate)
                    except ValueError:
                        continue
                    if not resolved.is_file():
                        continue
                    rel = resolved.relative_to(repo).as_posix()
                    if rel in seen:
                        continue
                    seen.add(rel)
                    artifacts.append(artifact_path(repo, rel, kind="playwright-native-artifact"))
    return tuple(artifacts)


class PlaywrightGate:
    @staticmethod
    def run(req: PlaywrightGateRequest) -> PlaywrightGateResult:
        if req.claim.kind != "web.acceptance":
            raise ValueError("playwright-gate-claim-kind-mismatch")
        _validate_required_scenarios(req.required_scenarios)
        if not req.argv:
            raise ValueError("playwright-empty-argv")
        if "--pass-with-no-tests" in req.argv:
            raise ValueError("playwright-pass-with-no-tests-forbidden")

        repo = req.repo.resolve()
        report_path = _contained(repo, repo / req.report_path)
        runtime_path = None
        if req.runtime_observation_path is not None:
            runtime_path = _contained(repo, repo / req.runtime_observation_path)
        for path in (report_path, runtime_path):
            if path is not None and path.exists():
                path.unlink()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        if runtime_path is not None:
            runtime_path.parent.mkdir(parents=True, exist_ok=True)

        before = capture_state(repo, req.repository_id)
        started = _now()
        executable = shutil.which(req.argv[0])
        if executable is None:
            receipt = EvidenceReceipt.create(
                claim_id=req.claim.claim_id, subject_ref=req.subject_ref,
                authority_id=req.authority.authority_id,
                state_before_id=before.state_id, state_after_id=before.state_id,
                certified_state_id=None, input_bindings=(), producer_id=req.producer_id,
                run_id=req.run_id, gate_id=req.claim.gate_id,
                gate_contract_version=req.claim.gate_contract_version,
                executable_identity=None, tool_version=None, outcome="BLOCKED",
                started_at=started, finished_at=_now(), artifacts=(),
            )
            return PlaywrightGateResult(None, receipt, None, ("playwright-executable-unavailable",))
        resolved_exe = str(Path(executable).resolve())
        if req.expected_executable is not None and resolved_exe != str(Path(req.expected_executable).resolve()):
            receipt = EvidenceReceipt.create(
                claim_id=req.claim.claim_id, subject_ref=req.subject_ref,
                authority_id=req.authority.authority_id,
                state_before_id=before.state_id, state_after_id=before.state_id,
                certified_state_id=None, input_bindings=(), producer_id=req.producer_id,
                run_id=req.run_id, gate_id=req.claim.gate_id,
                gate_contract_version=req.claim.gate_contract_version,
                executable_identity=resolved_exe, tool_version=None, outcome="BLOCKED",
                started_at=started, finished_at=_now(), artifacts=(),
            )
            return PlaywrightGateResult(None, receipt, None, ("playwright-executable-identity-mismatch",))

        argv = list(req.argv)
        if not any(arg.startswith("--reporter") for arg in argv):
            argv.append("--reporter=json")
        if "--forbid-only" not in argv:
            argv.append("--forbid-only")
        if req.fail_on_flaky and "--fail-on-flaky-tests" not in argv:
            argv.append("--fail-on-flaky-tests")
        argv[0] = resolved_exe
        env = os.environ.copy()
        env["PLAYWRIGHT_JSON_OUTPUT_NAME"] = str(report_path)

        process: subprocess.CompletedProcess[bytes] | None = None
        blocked_reason: str | None = None
        try:
            process = subprocess.run(
                argv, cwd=repo, env=env, capture_output=True, text=False,
                shell=False, timeout=req.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            blocked_reason = "playwright-timeout"
        except OSError:
            blocked_reason = "playwright-launch-unavailable"

        evaluation: PlaywrightEvaluation | None = None
        report: dict[str, Any] | None = None
        runtime: RuntimeObservation | None = None
        if blocked_reason is None:
            if not report_path.is_file():
                blocked_reason = "playwright-report-missing"
            else:
                try:
                    report = _load_json(report_path, "invalid-playwright-json-report")
                    if runtime_path is not None:
                        if not runtime_path.is_file():
                            raise ValueError("playwright-runtime-observation-missing")
                        runtime = load_runtime_observation(
                            _load_json(runtime_path, "invalid-playwright-runtime-observation")
                        )
                    evaluation = evaluate_playwright_report(
                        report,
                        required_scenarios=req.required_scenarios,
                        runtime=runtime,
                        expected_worktree=req.expected_worktree,
                        expected_data_namespace=req.expected_data_namespace,
                        fail_on_flaky=req.fail_on_flaky,
                    )
                except ValueError as exc:
                    blocked_reason = str(exc)

        after = capture_state(repo, req.repository_id)
        artifacts: list[ArtifactRef] = []
        if report_path.is_file():
            artifacts.append(artifact_path(repo, report_path.relative_to(repo).as_posix(), "playwright-json-report"))
        if runtime_path is not None and runtime_path.is_file():
            artifacts.append(artifact_path(repo, runtime_path.relative_to(repo).as_posix(), "playwright-runtime-observation"))
        if report is not None:
            artifacts.extend(_attachment_artifacts(repo, report))
        if process is not None:
            artifacts.append(ArtifactRef("stdout-digest", "inline:stdout", sha256_bytes(process.stdout)))
            artifacts.append(ArtifactRef("stderr-digest", "inline:stderr", sha256_bytes(process.stderr)))

        if after.state_id != before.state_id:
            receipt_outcome = "MUTATED"
        elif blocked_reason is not None:
            receipt_outcome = "BLOCKED"
        elif evaluation is None:
            receipt_outcome = "BLOCKED"
        elif process is not None and process.returncode != 0 and evaluation.outcome.outcome == "PASS":
            receipt_outcome = "FAIL"
        else:
            receipt_outcome = evaluation.outcome.outcome

        bindings: list[InputBinding] = []
        # Required scenario declarations are policy input, but not a repository path;
        # bind them through a deterministic inline digest rather than an escape bag.
        artifacts.append(ArtifactRef(
            "playwright-required-scenarios",
            "inline:required-scenarios",
            digest([asdict(s) for s in req.required_scenarios]),
        ))
        receipt = EvidenceReceipt.create(
            claim_id=req.claim.claim_id,
            subject_ref=req.subject_ref,
            authority_id=req.authority.authority_id,
            state_before_id=before.state_id,
            state_after_id=after.state_id,
            certified_state_id=before.state_id if receipt_outcome == "PASS" else None,
            input_bindings=tuple(bindings),
            producer_id=req.producer_id,
            run_id=req.run_id,
            gate_id=req.claim.gate_id,
            gate_contract_version=req.claim.gate_contract_version,
            executable_identity=resolved_exe,
            tool_version=None,
            outcome=receipt_outcome,
            started_at=started,
            finished_at=_now(),
            artifacts=tuple(artifacts),
        )
        reasons: tuple[str, ...]
        if blocked_reason is not None:
            reasons = (blocked_reason,)
        elif process is not None and process.returncode != 0 and evaluation is not None and evaluation.outcome.outcome == "PASS":
            reasons = (f"playwright-runner-exit:{process.returncode}",)
        elif evaluation is not None:
            reasons = evaluation.outcome.reasons
        else:
            reasons = ("playwright-evaluation-unavailable",)
        return PlaywrightGateResult(
            evaluation, receipt, process.returncode if process is not None else None, reasons
        )
