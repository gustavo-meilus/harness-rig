from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .authority import DirectAuthority
from .authorization import AuthorizationGrant
from .openspec import OpenSpecAdapter, OpenSpecBlocked, guarded_archive
from .state import capture_state
from .host import LocalProcessHost, qualification_to_json
from .vertical import VerticalSliceRequest, run_vertical_slice


def _direct_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Harness Rig r8.9 direct trust-path test surface")
    ap.add_argument("--repo", required=True)
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
    ap.add_argument("command", nargs=argparse.REMAINDER)
    ns = ap.parse_args(argv)
    command = list(ns.command)
    if command and command[0] == "--":
        command = command[1:]

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
    result = run_vertical_slice(VerticalSliceRequest(
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
    ))
    print(json.dumps({
        "receipt": asdict(result.receipt),
        "verdict": asdict(result.verdict),
    }, indent=2))
    return 0 if result.verdict.outcome == "ACCEPTED" else 2


def _spec_archive_main(argv: list[str]) -> int:
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
    ap.add_argument("--openspec-executable", default="openspec")
    ns = ap.parse_args(argv)

    repo = Path(ns.repo).resolve()
    resource = ns.resource or f"openspec:{ns.change}"
    adapter = OpenSpecAdapter(repo, executable=ns.openspec_executable)

    try:
        authority = adapter.authority_ref(ns.change, subject_ref=ns.subject)
        state = capture_state(repo, ns.repository_id)
    except OpenSpecBlocked as exc:
        print(json.dumps({
            "outcome": "BLOCKED",
            "reasons": list(exc.reasons),
            "mutation": None,
        }, indent=2))
        return 2

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
    print(json.dumps(asdict(result), indent=2))
    return 0 if result.outcome == "PASS" else 2


def _spec_main(argv: list[str]) -> int:
    if not argv:
        print("usage: harness-rig spec archive ...", file=sys.stderr)
        return 2
    command, *rest = argv
    if command == "archive":
        return _spec_archive_main(rest)
    print(f"unknown spec command: {command}", file=sys.stderr)
    return 2


def _doctor_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Run fresh native Harness Rig capability probes")
    ap.add_argument("--host", default="local-subprocess", choices=("local-subprocess",))
    ns = ap.parse_args(argv)
    qualification = LocalProcessHost().qualify()
    print(qualification_to_json(qualification), end="")
    return 0 if qualification.outcome == "PASS" else 2


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "spec":
        return _spec_main(args[1:])
    if args and args[0] == "doctor":
        return _doctor_main(args[1:])
    return _direct_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
