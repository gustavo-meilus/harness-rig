from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .authority import DirectAuthority
from .authorization import AuthorizationGrant
from .state import capture_state
from .vertical import VerticalSliceRequest, run_vertical_slice


def main() -> int:
    ap = argparse.ArgumentParser(description="Harness Rig r8.4 direct trust-path test surface")
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
    ns = ap.parse_args()
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


if __name__ == "__main__":
    raise SystemExit(main())
