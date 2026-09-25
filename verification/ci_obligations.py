#!/usr/bin/env python3
"""Deterministic CLI for M7 repository CI obligation evidence."""

from __future__ import annotations

import argparse
import dataclasses
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = ROOT / "prototype"
if str(PROTOTYPE) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE))

from harness_rig.repository_ci import (  # noqa: E402
    CiObligationArtifact,
    CiObligationResult,
    ExpectedResult,
    ObligationSpec,
    RepositoryCiError,
    RepositoryCiPolicy,
    create_ci_result,
    resolve_ci_obligations,
    validate_ci_required,
)


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RepositoryCiError(f"expected-json-object:{path}")
    return value


def load_policy(path: Path) -> RepositoryCiPolicy:
    data = _read_json(path)
    allowed = {"schema", "policy_id", "obligations", "governance_sensitive_paths"}
    if set(data) != allowed or data.get("schema") != "harness-rig/repository-ci-policy/v1":
        raise RepositoryCiError("invalid-policy-shape")
    obligations_raw = data.get("obligations")
    if not isinstance(obligations_raw, list):
        raise RepositoryCiError("invalid-policy-obligations")
    obligations = []
    for item in obligations_raw:
        if not isinstance(item, dict) or set(item) != {"obligation_id", "producer_id", "always_required", "privileged"}:
            raise RepositoryCiError("invalid-obligation-spec")
        obligations.append(ObligationSpec(**item))
    return RepositoryCiPolicy.create(
        policy_id=data["policy_id"],
        obligations=obligations,
        governance_sensitive_paths=data.get("governance_sensitive_paths", []),
    )


def load_artifact(path: Path) -> CiObligationArtifact:
    data = _read_json(path)
    expected = data.pop("expected_results", None)
    if not isinstance(expected, list):
        raise RepositoryCiError("invalid-expected-results")
    data["expected_results"] = tuple(ExpectedResult(**item) for item in expected)
    for key in ("changed_paths", "affected_modules", "mandatory_obligations"):
        if not isinstance(data.get(key), list):
            raise RepositoryCiError(f"invalid-{key}")
        data[key] = tuple(data[key])
    return CiObligationArtifact(**data)


def load_result(path: Path) -> CiObligationResult:
    return CiObligationResult(**_read_json(path))


def _write(path: Path | None, value: object) -> None:
    text = json.dumps(dataclasses.asdict(value), indent=2, sort_keys=True) + "\n"
    if path is None:
        sys.stdout.write(text)
    else:
        path.write_text(text, encoding="utf-8")


def _paths(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def command_resolve(args: argparse.Namespace) -> int:
    artifact = resolve_ci_obligations(
        policy=load_policy(args.policy),
        evaluated_sha=args.evaluated_sha,
        event_name=args.event_name,
        event_subject=args.event_subject,
        trust_mode=args.trust_mode,
        changed_paths=_paths(args.changed_paths_file),
    )
    _write(args.output, artifact)
    return 0


def command_result(args: argparse.Namespace) -> int:
    artifact = load_artifact(args.artifact)
    result = create_ci_result(
        artifact=artifact,
        obligation_id=args.obligation,
        producer_id=args.producer,
        outcome=args.outcome,
        privileged=args.privileged,
    )
    _write(args.output, result)
    return 0


def command_required(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    artifact = load_artifact(args.artifact)
    results = []
    if args.results_dir.is_dir():
        for path in sorted(args.results_dir.glob("*.json")):
            results.append(load_result(path))
    verdict = validate_ci_required(policy=policy, artifact=artifact, results=results)
    _write(args.output, verdict)
    return 0 if verdict.outcome == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve")
    resolve.add_argument("--policy", type=Path, required=True)
    resolve.add_argument("--evaluated-sha", required=True)
    resolve.add_argument("--event-name", required=True)
    resolve.add_argument("--event-subject", required=True)
    resolve.add_argument("--trust-mode", choices=("trusted", "untrusted_fork"), required=True)
    resolve.add_argument("--changed-paths-file", type=Path, required=True)
    resolve.add_argument("--output", type=Path)
    resolve.set_defaults(func=command_resolve)

    result = sub.add_parser("result")
    result.add_argument("--artifact", type=Path, required=True)
    result.add_argument("--obligation", required=True)
    result.add_argument("--producer", required=True)
    result.add_argument("--outcome", choices=("PASS", "FAIL", "SKIPPED", "BLOCKED"), required=True)
    result.add_argument("--privileged", action="store_true")
    result.add_argument("--output", type=Path)
    result.set_defaults(func=command_result)

    required = sub.add_parser("required")
    required.add_argument("--policy", type=Path, required=True)
    required.add_argument("--artifact", type=Path, required=True)
    required.add_argument("--results-dir", type=Path, required=True)
    required.add_argument("--output", type=Path)
    required.set_defaults(func=command_required)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (RepositoryCiError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        sys.stderr.write(f"BLOCKED: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
