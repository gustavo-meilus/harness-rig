#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "prototype"))
sys.path.insert(0, str(ROOT))

from harness_rig.release import (  # noqa: E402
    RELEASE_VERIFICATION_SCHEMA,
    ReleaseError,
    build_release_record,
    dispatch_record_attestation,
    parse_release_record,
    validate_release_candidate,
    verify_release_record,
    write_immutable_release_record,
)


def _markdown_literal(value: object) -> str:
    """Encode candidate-controlled text so Markdown sees no syntax characters."""
    return "".join(
        char if char.isalnum() or char == " " else f"&#x{ord(char):X};"
        for char in str(value)
    )


def render_candidate_summary(record_bytes: bytes) -> str:
    record = parse_release_record(record_bytes)
    lines = [
        "## Release record awaiting approval",
        "",
        f"- Record ID: {_markdown_literal(record.record_id)}",
        f"- Repository: {_markdown_literal(record.repository)} (ID {_markdown_literal(record.repository_id)})",
        f"- Source revision: {_markdown_literal(record.source_revision)}",
        f"- Hosted run / attempt / job: {_markdown_literal(record.hosted_run_id)} / "
        f"{_markdown_literal(record.hosted_run_attempt)} / {_markdown_literal(record.hosted_job_id)}",
        "",
        "The environment reviewer authorizes these artifact hashes:",
        "",
        "| Path | Size | SHA-256 |",
        "| --- | ---: | --- |",
    ]
    for artifact in record.artifacts:
        lines.append(
            f"| {_markdown_literal(artifact.path)} | {_markdown_literal(artifact.size)} | "
            f"{_markdown_literal(artifact.sha256)} |"
        )
    lines.extend(["", "This workflow attests the manifest bytes; it does not build these artifacts."])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build or verify immutable Harness Rig release provenance")
    sub = ap.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--artifact", action="append", required=True)
    rec.add_argument("--source-revision", required=True)
    rec.add_argument("--repository", required=True, help="GitHub OWNER/REPO; never inferred from this checkout")
    rec.add_argument("--run-id", type=int, help="GitHub Actions run ID; omit to write a BLOCKED candidate")
    rec.add_argument("--workflow", required=True)
    rec.add_argument("--created-at", required=True)
    rec.add_argument("--output", required=True)
    att = sub.add_parser("attest", help="submit an eligible candidate to the protected signing workflow")
    att.add_argument("--record", required=True)
    att.add_argument("--repository", required=True, help="Expected GitHub OWNER/REPO")
    ver = sub.add_parser("verify")
    ver.add_argument("--record", required=True)
    ver.add_argument("--artifact-dir", required=True)
    ver.add_argument("--repository", required=True, help="Expected GitHub OWNER/REPO")
    validate = sub.add_parser("validate-candidate", help=argparse.SUPPRESS)
    validate.add_argument("--record", required=True)
    validate.add_argument("--repository", required=True)
    validate.add_argument("--repository-id", type=int, required=True)
    summary = sub.add_parser("candidate-summary", help=argparse.SUPPRESS)
    summary.add_argument("--record", required=True)
    summary.add_argument("--output", required=True)
    ns = ap.parse_args(argv)

    try:
        if ns.command == "record":
            record = build_release_record(
                artifact_paths=[Path(x) for x in ns.artifact],
                source_revision=ns.source_revision,
                repository=ns.repository,
                hosted_run_id=ns.run_id,
                build_workflow_identity=ns.workflow,
                created_at=ns.created_at,
            )
            write_immutable_release_record(Path(ns.output), record)
            print(json.dumps(asdict(record), indent=2, sort_keys=True))
            return 0 if record.status == "CANDIDATE" else 2

        if ns.command == "validate-candidate":
            result = validate_release_candidate(
                parse_release_record(Path(ns.record).read_bytes()), ns.repository, ns.repository_id,
            )
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["record_integrity"] == result["hosted_ci"] == "PASS" else 2

        if ns.command == "candidate-summary":
            summary_path = Path(ns.output)
            with summary_path.open("a", encoding="utf-8") as output:
                output.write(render_candidate_summary(Path(ns.record).read_bytes()))
            print(json.dumps({"status": "SUMMARY_WRITTEN"}))
            return 0

        if ns.command == "attest":
            record_path = Path(ns.record)
            record_bytes = record_path.read_bytes()
            record = parse_release_record(record_bytes)
            result = validate_release_candidate(record, ns.repository)
            if result["record_integrity"] != "PASS" or result["hosted_ci"] != "PASS":
                print(json.dumps(result, indent=2, sort_keys=True))
                return 2
            print(json.dumps({
                "status": "DISPATCHED",
                "repository": ns.repository,
                "workflow": "release-record-attestation.yml",
                "run": dispatch_record_attestation(record_bytes, ns.repository),
            }, indent=2, sort_keys=True))
            return 0

        record_bytes = Path(ns.record).read_bytes()
        result = verify_release_record(record_bytes, Path(ns.artifact_dir), ns.repository)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["outcome"] == "PASS" else (2 if result["outcome"] == "BLOCKED" else 1)
    except (ReleaseError, ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
        outcome = "BLOCKED" if str(exc) in {"release-record-blocked", "unsupported-release-record-schema"} else "FAIL"
        print(json.dumps({"schema": RELEASE_VERIFICATION_SCHEMA, "outcome": outcome, "reasons": [str(exc)]}, indent=2, sort_keys=True))
        return 2 if outcome == "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
