from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .authority import DirectAuthority
from .authorization import AuthorizationGrant
from .host import LocalProcessHost, qualification_to_json
from .migration import MigrationError, apply_migration, assess_migration, rollback_migration
from .openspec import OpenSpecAdapter, OpenSpecBlocked, guarded_archive
from .product import (
    CONFIG_SCHEMA,
    EXIT_BLOCKED,
    EXIT_CANCELLED,
    EXIT_INVALID,
    ProductError,
    envelope,
    load_effective_config,
    project_config_path,
)
from .state import capture_state
from .vertical import VerticalSliceRequest, run_vertical_slice


def _print_envelope(env) -> int:
    print(env.to_json(), end="")
    return env.exit_code


def _config_for(repo: Path, ns: argparse.Namespace):
    overrides = {
        "timeout_seconds": getattr(ns, "timeout_seconds", None),
        "openspec_executable": getattr(ns, "openspec_executable", None),
        "noninteractive": getattr(ns, "noninteractive", None),
    }
    return load_effective_config(repo, cli=overrides)


def _direct_result(ns: argparse.Namespace, command: list[str]):
    repo = Path(ns.repo).resolve()
    authority = DirectAuthority.from_file(repo, ns.authority, ns.subject)
    state = capture_state(repo)
    grant = AuthorizationGrant.issue(
        issuer="local-authority",
        principal=ns.principal,
        action=ns.decision_for,
        resource=ns.resource,
        authority_id=authority.authority_id,
        state_id=state.state_id,
        subject_ref=ns.subject,
        issued_at=ns.issued_at,
        expires_at=ns.expires_at,
    )
    return run_vertical_slice(VerticalSliceRequest(
        repo=repo,
        repository_id="local-repository",
        authority_path=ns.authority,
        subject_ref=ns.subject,
        claim_id=ns.claim,
        argv=tuple(command) if command else None,
        run_id=ns.run_id,
        producer_id="local-cli",
        principal=ns.principal,
        decision_for=ns.decision_for,
        resource=ns.resource,
        now=ns.now,
        grant=grant,
        timeout_seconds=getattr(ns, "timeout_seconds", None) or 30.0,
    ))


def _add_verify_args(ap: argparse.ArgumentParser, *, require_repo: bool = True) -> None:
    ap.add_argument("--repo", required=require_repo)
    ap.add_argument("--authority", required=True)
    ap.add_argument("--subject", default="repository")
    ap.add_argument("--claim", default="project.command")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--principal", default="local-controller")
    ap.add_argument("--decision-for", default="merge")
    ap.add_argument("--resource", default="repository")
    ap.add_argument("--now", required=True)
    ap.add_argument("--issued-at", required=True)
    ap.add_argument("--expires-at")
    ap.add_argument("--timeout-seconds", type=float)
    ap.add_argument("command", nargs=argparse.REMAINDER)


def _direct_main(argv: list[str]) -> int:
    """r8.9 raw-JSON compatibility path; product callers should use `verify`."""
    ap = argparse.ArgumentParser(description="Harness Rig direct trust-path compatibility surface")
    _add_verify_args(ap)
    ns = ap.parse_args(argv)
    command = list(ns.command)
    if command and command[0] == "--":
        command = command[1:]
    result = _direct_result(ns, command)
    print(json.dumps({"receipt": asdict(result.receipt), "verdict": asdict(result.verdict)}, indent=2))
    return 0 if result.verdict.outcome == "ACCEPTED" else 2


def _verify_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Run the direct trust path and emit the M10 machine envelope")
    _add_verify_args(ap)
    ns = ap.parse_args(argv)
    repo = Path(ns.repo).resolve()
    try:
        config = _config_for(repo, ns)
    except ProductError as exc:
        return _print_envelope(envelope("verify", "BLOCKED", reasons=(str(exc),)))
    ns.timeout_seconds = ns.timeout_seconds or config.timeout_seconds
    command = list(ns.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        return _print_envelope(envelope("verify", "BLOCKED", reasons=("verification-command-required",)))
    try:
        result = _direct_result(ns, command)
    except KeyboardInterrupt:
        return _print_envelope(envelope("verify", "CANCELLED", reasons=("cancelled",)))
    data = {"receipt": asdict(result.receipt), "verdict": asdict(result.verdict)}
    outcome = "PASS" if result.verdict.outcome == "ACCEPTED" else "BLOCKED"
    reasons = () if outcome == "PASS" else (f"acceptance:{result.verdict.outcome}", f"gate:{result.receipt.outcome}")
    return _print_envelope(envelope("verify", outcome, data=data, reasons=reasons))


def _spec_archive_main(argv: list[str], *, enveloped: bool = False) -> int:
    ap = argparse.ArgumentParser(description="Guard an OpenSpec archive transition")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--change", required=True)
    ap.add_argument("--subject", default="repository")
    ap.add_argument("--repository-id", default="local-repository")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--principal", default="local-controller")
    ap.add_argument("--resource")
    ap.add_argument("--now", required=True)
    ap.add_argument("--issued-at", required=True)
    ap.add_argument("--expires-at")
    ap.add_argument("--openspec-executable")
    ap.add_argument("--timeout-seconds", type=float)
    ns = ap.parse_args(argv)

    repo = Path(ns.repo).resolve()
    try:
        config = _config_for(repo, ns)
    except ProductError as exc:
        if enveloped:
            return _print_envelope(envelope("spec archive", "BLOCKED", reasons=(str(exc),)))
        print(json.dumps({"outcome": "BLOCKED", "reasons": [str(exc)], "mutation": None}, indent=2))
        return EXIT_BLOCKED
    resource = ns.resource or f"openspec:{ns.change}"
    adapter = OpenSpecAdapter(repo, executable=config.openspec_executable)
    adapter.timeout_seconds = ns.timeout_seconds or config.timeout_seconds

    try:
        authority = adapter.authority_ref(ns.change, subject_ref=ns.subject)
        state = capture_state(repo, ns.repository_id)
    except OpenSpecBlocked as exc:
        if enveloped:
            return _print_envelope(envelope("spec archive", "BLOCKED", reasons=tuple(exc.reasons)))
        print(json.dumps({"outcome": "BLOCKED", "reasons": list(exc.reasons), "mutation": None}, indent=2))
        return EXIT_BLOCKED

    grant = AuthorizationGrant.issue(
        issuer="local-authority",
        principal=ns.principal,
        action="spec_archive",
        resource=resource,
        authority_id=authority.authority_id,
        state_id=state.state_id,
        subject_ref=ns.subject,
        issued_at=ns.issued_at,
        expires_at=ns.expires_at,
    )
    result = guarded_archive(
        adapter,
        repository_id=ns.repository_id,
        change=ns.change,
        subject_ref=ns.subject,
        principal=ns.principal,
        resource=resource,
        grant=grant,
        run_id=ns.run_id,
        now=ns.now,
        trusted_issuers={"local-authority"},
    )
    data = asdict(result)
    if enveloped:
        outcome = "PASS" if result.outcome == "PASS" else "BLOCKED"
        return _print_envelope(envelope("spec archive", outcome, data=data, reasons=tuple(result.reasons)))
    print(json.dumps(data, indent=2))
    return 0 if result.outcome == "PASS" else EXIT_BLOCKED


def _spec_status_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Report bounded OpenSpec readiness")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--change", required=True)
    ap.add_argument("--openspec-executable")
    ap.add_argument("--timeout-seconds", type=float)
    ap.add_argument("--require-tasks-complete", action="store_true")
    ns = ap.parse_args(argv)
    repo = Path(ns.repo).resolve()
    try:
        config = _config_for(repo, ns)
    except ProductError as exc:
        return _print_envelope(envelope("spec status", "BLOCKED", reasons=(str(exc),)))
    adapter = OpenSpecAdapter(repo, executable=config.openspec_executable)
    adapter.timeout_seconds = ns.timeout_seconds or config.timeout_seconds
    health = adapter.health(ns.change, require_tasks_complete=ns.require_tasks_complete)
    outcome = "PASS" if health.outcome == "PASS" else "BLOCKED"
    return _print_envelope(envelope("spec status", outcome, data=asdict(health), reasons=tuple(health.reasons)))


def _spec_main(argv: list[str]) -> int:
    if not argv:
        return _print_envelope(envelope("spec", "INVALID", reasons=("spec-subcommand-required",)))
    command, *rest = argv
    if command == "archive":
        enveloped = False
        if "--json-v1" in rest:
            rest = [x for x in rest if x != "--json-v1"]
            enveloped = True
        return _spec_archive_main(rest, enveloped=enveloped)
    if command == "status":
        return _spec_status_main(rest)
    return _print_envelope(envelope("spec", "INVALID", reasons=(f"unknown-spec-command:{command}",)))


def _doctor_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Run fresh native Harness Rig capability probes")
    ap.add_argument("--host", default="local-subprocess", choices=("local-subprocess",))
    ap.add_argument("--json-v1", action="store_true")
    ns = ap.parse_args(argv)
    qualification = LocalProcessHost().qualify()
    if ns.json_v1:
        data = json.loads(qualification_to_json(qualification))
        outcome = "PASS" if qualification.outcome == "PASS" else "BLOCKED"
        return _print_envelope(envelope("doctor", outcome, data=data, reasons=tuple(qualification.reasons)))
    # r8.8/r8.9 compatibility shape.
    print(qualification_to_json(qualification), end="")
    return 0 if qualification.outcome == "PASS" else EXIT_BLOCKED


def _init_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Initialize the minimal Harness Rig project configuration")
    ap.add_argument("--repo", default=".")
    ns = ap.parse_args(argv)
    repo = Path(ns.repo).resolve()
    path = project_config_path(repo)
    desired = json.dumps({
        "schema": CONFIG_SCHEMA,
        "noninteractive": True,
        "timeout_seconds": 30.0,
        "openspec_executable": "openspec",
    }, indent=2, sort_keys=True) + "\n"
    if path.exists():
        try:
            current = path.read_text(encoding="utf-8")
        except OSError as exc:
            return _print_envelope(envelope("init", "BLOCKED", reasons=(f"config-unreadable:{exc.__class__.__name__}",)))
        if current != desired:
            return _print_envelope(envelope("init", "BLOCKED", reasons=("project-config-already-exists",)))
        return _print_envelope(envelope("init", "PASS", data={"config": str(path), "created": False}))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(desired, encoding="utf-8")
    return _print_envelope(envelope("init", "PASS", data={"config": str(path), "created": True}))


def _status_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Report Harness Rig product/config/migration status")
    ap.add_argument("--repo", default=".")
    ns = ap.parse_args(argv)
    repo = Path(ns.repo).resolve()
    try:
        config = load_effective_config(repo)
        assessment = assess_migration(repo)
    except (ProductError, MigrationError) as exc:
        return _print_envelope(envelope("status", "BLOCKED", reasons=(str(exc),)))
    data: dict[str, Any] = {
        "revision": "r8.10",
        "config": asdict(config),
        "migration": asdict(assessment),
    }
    outcome = "PASS" if assessment.outcome == "PASS" else "BLOCKED"
    return _print_envelope(envelope("status", outcome, data=data, reasons=assessment.reasons))


def _migrate_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Apply or rollback the bounded Harness Rig project migration state")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--from-revision", default="r8.9")
    ap.add_argument("--to-revision", default="r8.10")
    ap.add_argument("--rollback", action="store_true")
    ns = ap.parse_args(argv)
    repo = Path(ns.repo).resolve()
    try:
        load_effective_config(repo)
        state = rollback_migration(repo) if ns.rollback else apply_migration(
            repo, from_revision=ns.from_revision, to_revision=ns.to_revision
        )
    except (ProductError, MigrationError) as exc:
        return _print_envelope(envelope("migrate", "BLOCKED", reasons=(str(exc),)))
    return _print_envelope(envelope("migrate", "PASS", data=asdict(state)))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return _print_envelope(envelope("harness-rig", "INVALID", reasons=("command-required",)))
    try:
        command, *rest = args
        if command == "init":
            return _init_main(rest)
        if command == "doctor":
            return _doctor_main(rest)
        if command == "spec":
            return _spec_main(rest)
        if command == "verify":
            return _verify_main(rest)
        if command == "status":
            return _status_main(rest)
        if command == "migrate":
            return _migrate_main(rest)
        # r8.9 compatibility: direct invocation began with --repo rather than a verb.
        if command.startswith("-"):
            return _direct_main(args)
        return _print_envelope(envelope(command, "INVALID", reasons=(f"unknown-command:{command}",)))
    except KeyboardInterrupt:
        return _print_envelope(envelope(args[0], "CANCELLED", reasons=("cancelled",)))
    except SystemExit:
        raise
    except Exception as exc:
        return _print_envelope(envelope(args[0], "ERROR", reasons=(f"internal-error:{exc.__class__.__name__}",)))


if __name__ == "__main__":
    raise SystemExit(main())
