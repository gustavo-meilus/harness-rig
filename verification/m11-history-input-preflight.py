#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent


def run(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def inspect_bundle(spec: dict, path: pathlib.Path) -> dict:
    item = {
        "source": spec["id"],
        "path": str(path),
        "kind": "bundle",
        "ok": False,
    }
    if not path.is_file():
        item["reason"] = "missing"
        return item

    item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    rc, output, error = run(["git", "bundle", "list-heads", str(path)])
    item["list_heads_exit"] = rc
    if rc:
        item.update(reason="list-heads-failed", stderr=error.strip())
        return item

    refs = []
    for line in output.splitlines():
        if line.strip():
            oid, ref = line.split(None, 1)
            refs.append({"oid": oid, "ref": ref})
    item["refs"] = refs
    main_oid = next(
        (entry["oid"] for entry in refs if entry["ref"] == spec["source_ref"]),
        None,
    )
    item["source_commit"] = main_oid
    if main_oid != spec["source_commit"]:
        item["reason"] = "source-main-mismatch"
        return item

    with tempfile.TemporaryDirectory(prefix="hr-m11-preflight-") as temp_dir:
        mirror = pathlib.Path(temp_dir) / "source.git"
        rc, _, error = run(["git", "clone", "--mirror", str(path), str(mirror)])
        if rc:
            item.update(reason="mirror-clone-failed", stderr=error.strip())
            return item
        rc, _, error = run(["git", "-C", str(mirror), "fsck", "--full"])
        if rc:
            item.update(reason="fsck-failed", stderr=error.strip())
            return item
        rc, output, _ = run(
            ["git", "-C", str(mirror), "rev-list", "--count", spec["source_ref"]]
        )
        item["main_commit_count"] = int(output.strip()) if rc == 0 else None
        missing = []
        for required_path in spec.get("required_paths", []):
            rc, _, _ = run(
                [
                    "git",
                    "-C",
                    str(mirror),
                    "cat-file",
                    "-e",
                    f"{spec['source_ref']}:{required_path}",
                ]
            )
            if rc:
                missing.append(required_path)
        item["missing_required_paths"] = missing
        if missing:
            item["reason"] = "missing-required-paths"
            return item
        if not item["main_commit_count"]:
            item["reason"] = "main-has-no-commits"
            return item

    item["ok"] = True
    return item


def compare_manifest(items: list[dict], manifest_path: pathlib.Path) -> list[dict]:
    errors = []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {entry["id"]: entry for entry in manifest["sources"]}
    for item in items:
        baseline = expected.get(item["source"])
        if baseline is None:
            errors.append({"source": item["source"], "reason": "missing-manifest-entry"})
            continue
        if item.get("sha256") != baseline.get("sha256"):
            errors.append({"source": item["source"], "reason": "bundle-digest-mismatch"})
        if item.get("refs") != baseline.get("refs"):
            errors.append({"source": item["source"], "reason": "ref-inventory-mismatch"})
    if set(expected) != {item["source"] for item in items}:
        errors.append({"reason": "source-set-mismatch"})
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", help="Bundle directory; defaults to the import spec.")
    parser.add_argument(
        "--spec",
        default=str(HERE / "m11-history-import-spec.json"),
        help="Source pin specification.",
    )
    parser.add_argument(
        "--expected-manifest",
        help="Require bundle digests and refs to match this retained inventory.",
    )
    parser.add_argument("--output", help="Write the machine-readable report to this path.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    spec_path = pathlib.Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    base = pathlib.Path(args.dir).resolve() if args.dir else ROOT / spec["bundle_directory"]
    items = [
        inspect_bundle(source, base / source["bundle"])
        for source in spec["sources"]
    ]
    errors = []
    if args.expected_manifest:
        errors = compare_manifest(items, pathlib.Path(args.expected_manifest).resolve())
    result = "PASS" if all(item.get("ok") for item in items) and not errors else "BLOCKED"
    report = {
        "schema": "harness-rig/m11-history-input-preflight/v3",
        "base": str(base),
        "result": result,
        "sources": items,
        "manifest_errors": errors,
    }
    rendered = json.dumps(report, indent=2)
    if args.output:
        pathlib.Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered if args.json else result)
    return 0 if result == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
