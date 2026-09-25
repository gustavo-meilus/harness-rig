#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "prototype"))

from harness_rig.release import (  # noqa: E402
    ReleaseArtifact,
    ReleaseRecord,
    build_release_record,
    verify_release_record,
    write_immutable_release_record,
)


def _load_record(path: Path) -> ReleaseRecord:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ReleaseRecord(
        schema=data["schema"],
        record_id=data["record_id"],
        status=data["status"],
        reasons=tuple(data.get("reasons", [])),
        accepted_source_revision=data["accepted_source_revision"],
        accepted_repository_verdict=data.get("accepted_repository_verdict"),
        build_workflow_identity=data["build_workflow_identity"],
        created_at=data["created_at"],
        artifacts=tuple(ReleaseArtifact(**x) for x in data["artifacts"]),
        attestation_ref=data.get("attestation_ref"),
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build or verify immutable Harness Rig release provenance")
    sub = ap.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--artifact", action="append", required=True)
    rec.add_argument("--source-revision", required=True)
    rec.add_argument("--repository-verdict")
    rec.add_argument("--workflow", required=True)
    rec.add_argument("--created-at", required=True)
    rec.add_argument("--attestation-ref")
    rec.add_argument("--output", required=True)
    ver = sub.add_parser("verify")
    ver.add_argument("--record", required=True)
    ver.add_argument("--artifact-dir", required=True)
    ns = ap.parse_args(argv)

    if ns.command == "record":
        record = build_release_record(
            artifact_paths=[Path(x) for x in ns.artifact],
            accepted_source_revision=ns.source_revision,
            accepted_repository_verdict=ns.repository_verdict,
            build_workflow_identity=ns.workflow,
            created_at=ns.created_at,
            attestation_ref=ns.attestation_ref,
        )
        write_immutable_release_record(Path(ns.output), record)
        print(json.dumps(asdict(record), indent=2, sort_keys=True))
        return 0 if record.status == "PASS" else 2

    record = _load_record(Path(ns.record))
    verify_release_record(record, Path(ns.artifact_dir))
    print(json.dumps({"schema": "harness-rig/release-verification/v1", "record_id": record.record_id, "outcome": "PASS"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
