#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent


def run(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", default=str(ROOT / "verification/m11-source-bundles"))
    parser.add_argument("--upstream-report", default=str(HERE / "m11-upstream-signature-verification.json"))
    parser.add_argument("--report")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    bundle_dir = pathlib.Path(args.bundle_dir).resolve()
    signature_report = json.loads(pathlib.Path(args.upstream_report).read_text(encoding="utf-8"))
    source_bundles = {}
    errors = []
    signature_types = {"pgp": 0, "ssh": 0}
    for source in ("aiboarding", "tacticswitch", "skill-kit"):
        bundle = bundle_dir / f"{source}.bundle"
        temp = tempfile.TemporaryDirectory(prefix=f"hr-m11-sig-{source}-")
        mirror = pathlib.Path(temp.name) / "source.git"
        rc, _, error = run(["git", "clone", "--mirror", str(bundle), str(mirror)])
        if rc:
            errors.append({"source": source, "reason": "bundle-clone-failed", "detail": error.strip()})
        else:
            source_bundles[source] = (temp, mirror)

    upstream_entries = signature_report.get("commits", [])
    if signature_report.get("result") != "PASS" or signature_report.get("failed") != 0:
        errors.append({"reason": "upstream-report-not-pass"})
    if len(upstream_entries) != 25 or signature_report.get("checked") != 25:
        errors.append({"reason": "unexpected-signed-commit-count", "actual": len(upstream_entries)})

    for entry in upstream_entries:
        source = entry.get("source")
        sha = entry.get("sha")
        if entry.get("verified") is not True or entry.get("reason") != "valid":
            errors.append({"source": source, "sha": sha, "reason": "upstream-signature-not-valid"})
            continue
        item = source_bundles.get(source)
        if item is None:
            errors.append({"source": source, "sha": sha, "reason": "source-bundle-unavailable"})
            continue
        _, mirror = item
        rc, _, _ = run(["git", "-C", str(mirror), "cat-file", "-e", f"{sha}^{{commit}}"])
        if rc:
            errors.append({"source": source, "sha": sha, "reason": "verified-commit-absent-from-bundle"})
            continue
        rc, raw, _ = run(["git", "-C", str(mirror), "cat-file", "commit", sha])
        if rc:
            errors.append({"source": source, "sha": sha, "reason": "commit-read-failed"})
            continue
        header = raw.split("\n\n", 1)[0]
        if "gpgsig -----BEGIN PGP SIGNATURE-----" in header:
            signature_types["pgp"] += 1
        elif "gpgsig -----BEGIN SSH SIGNATURE-----" in header:
            signature_types["ssh"] += 1
        else:
            errors.append({"source": source, "sha": sha, "reason": "signature-header-missing-or-unknown"})

    if signature_types != {"pgp": 13, "ssh": 12}:
        errors.append({"reason": "signature-type-count-mismatch", "actual": signature_types})

    tag_counts = {"total": 0, "annotated": 0, "lightweight": 0, "signed": 0}
    for source, (_, mirror) in source_bundles.items():
        rc, output, error = run(
            ["git", "-C", str(mirror), "for-each-ref", "--format=%(objectname)", "refs/tags"]
        )
        if rc:
            errors.append({"source": source, "reason": "tag-ref-list-failed", "detail": error.strip()})
            continue
        for oid in output.splitlines():
            if not oid:
                continue
            tag_counts["total"] += 1
            rc, kind, error = run(["git", "-C", str(mirror), "cat-file", "-t", oid])
            if rc:
                errors.append({"source": source, "tag_object": oid, "reason": "tag-object-missing"})
                continue
            if kind.strip() == "tag":
                tag_counts["annotated"] += 1
                rc, body, _ = run(["git", "-C", str(mirror), "cat-file", "tag", oid])
                if "-----BEGIN PGP SIGNATURE-----" in body or "-----BEGIN SSH SIGNATURE-----" in body:
                    tag_counts["signed"] += 1
            else:
                tag_counts["lightweight"] += 1
    if tag_counts != {"total": 21, "annotated": 13, "lightweight": 8, "signed": 0}:
        errors.append({"reason": "tag-object-count-mismatch", "actual": tag_counts})

    report = {
        "schema": "harness-rig/m11-source-signature-verification/v1",
        "result": "PASS" if not errors else "FAIL",
        "authority": "retained upstream GitHub commit-verification result matched to exact bundled commit IDs and signature headers",
        "upstream_verified_commits": len(upstream_entries),
        "signature_types": signature_types,
        "local_revalidation": "BLOCKED_LOCAL_TRUST_CONFIGURATION; local GPG keyring and SSH allowed-signers file are unavailable",
        "source_tag_objects": tag_counts,
        "errors": errors,
    }
    for temp, _ in source_bundles.values():
        temp.cleanup()
    rendered = json.dumps(report, indent=2)
    if args.report:
        pathlib.Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered if args.json else report["result"])
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
