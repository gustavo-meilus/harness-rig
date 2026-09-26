#!/usr/bin/env python3
from __future__ import annotations

import argparse
import configparser
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent


def run(repo: pathlib.Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.stdout


def gitmodules(repo: pathlib.Path, commit: str) -> dict[str, tuple[str, str]]:
    try:
        content = run(repo, "show", f"{commit}:.gitmodules").decode("utf-8")
    except RuntimeError:
        return {}
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.read_string(content)
    entries = {}
    for section in parser.sections():
        if not section.lower().startswith("submodule "):
            raise ValueError(f"unexpected .gitmodules section: {section}")
        path = parser.get(section, "path", fallback=None)
        url = parser.get(section, "url", fallback=None)
        if not path or not url or path in entries:
            raise ValueError(f"invalid or duplicate .gitmodules path: {path}")
        entries[path] = (section, url)
    return entries


def tree_entry(repo: pathlib.Path, commit: str, path: str) -> tuple[str, str, str] | None:
    output = run(repo, "ls-tree", commit, "--", path).decode("utf-8", "surrogateescape")
    if not output.strip():
        return None
    metadata, actual_path = output.rstrip("\n").split("\t", 1)
    mode, kind, oid = metadata.split()
    if actual_path != path:
        return None
    return mode, kind, oid


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--spec", default=str(HERE / "m11-history-import-spec.json")
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo = pathlib.Path(args.repo).resolve()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    errors = []
    commit = args.commit
    parents = run(repo, "show", "-s", "--format=%P", commit).decode().split()
    if len(parents) != 1:
        errors.append({"kind": "parent-count", "expected": 1, "actual": len(parents)})
    else:
        parent = parents[0]
        changed = run(
            repo, "diff-tree", "--root", "-r", "--name-only", "--no-commit-id",
            parent, commit,
        ).decode("utf-8", "surrogateescape").splitlines()
        expected_paths = {".gitmodules"} | {
            source["target_prefix"] for source in spec["sources"]
        }
        if set(changed) != expected_paths:
            errors.append(
                {"kind": "changed-path-set", "expected": sorted(expected_paths), "actual": sorted(changed)}
            )

        before = gitmodules(repo, parent)
        after = gitmodules(repo, commit)
        allowed = {item["target_prefix"]: item for item in spec["sources"]}
        bad_entries = []
        for path, (_, url) in after.items():
            expected = allowed.get(path)
            if expected is None or url != expected["repository"]:
                bad_entries.append(path)
        if bad_entries:
            errors.append({"kind": "unapproved-gitmodules-entry", "paths": bad_entries})
        changed_modules = {
            path
            for path in set(before) | set(after)
            if before.get(path) != after.get(path)
        }
        if changed_modules != set(allowed):
            errors.append(
                {"kind": "gitmodules-change-set", "expected": sorted(allowed), "actual": sorted(changed_modules)}
            )
        for source in spec["sources"]:
            path = source["target_prefix"]
            if path in before:
                errors.append({"kind": "source-already-present-in-parent", "path": path})
            entry = tree_entry(repo, commit, path)
            expected_oid = source["source_commit"]
            if entry != ("160000", "commit", expected_oid):
                errors.append(
                    {
                        "kind": "gitlink-mismatch",
                        "path": path,
                        "expected": {"mode": "160000", "type": "commit", "oid": expected_oid},
                        "actual": None if entry is None else {"mode": entry[0], "type": entry[1], "oid": entry[2]},
                    }
                )

    report = {
        "schema": "harness-rig/m11-import-only-verification/v2",
        "result": "PASS" if not errors else "FAIL",
        "commit": commit,
        "sources": [source["id"] for source in spec["sources"]],
        "errors": errors,
    }
    print(json.dumps(report, indent=2) if args.json else report["result"])
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
