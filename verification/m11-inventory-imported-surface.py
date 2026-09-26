#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess

CATEGORIES = {
    "licenses": [r"(^|/)(LICENSE|LICENSE\..*|NOTICE|NOTICE\..*)$"],
    "state": [r"(^|/)\.aiboarding(/|$)", r"state\.json$", r"capabilit"],
    "hooks": [r"(^|/)hooks?(/|$)", r"hook"],
    "host_plugin_manifests": [r"plugin\.json$", r"marketplace\.json$", r"manifest\.json$", r"\.claude-plugin/", r"\.codex"],
    "install_update": [r"(^|/)scripts?/(install|verify_install|migrat|updat)", r"(^|/)INSTALL\.md$"],
    "generated_distribution": [r"(^|/)(templates?|dist|generated)(/|$)", r"MANIFEST\.sha256$"],
    "schemas_contracts": [r"schema", r"contract", r"protocol"],
    "tests_evals": [r"(^|/)(tests?|benchmarks?|fixtures?)(/|$)"],
    "ci": [r"(^|/)\.github/workflows(/|$)"],
    "openspec": [r"(^|/)openspec(/|$)"],
    "agent_roles": [r"(^|/)(agents?|skills?)(/|$)", r"AGENTS\.md$", r"CLAUDE\.md$"],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--prefix", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo = pathlib.Path(args.repo).resolve()
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "-z", "--full-tree", args.commit],
        capture_output=True,
    )
    if result.returncode:
        raise SystemExit(result.stderr.decode(errors="replace"))

    prefix = args.prefix.strip("/")
    paths = []
    gitlinks = []
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        path = raw_path.decode("utf-8", "surrogateescape")
        if prefix and not (path == prefix or path.startswith(prefix + "/")):
            continue
        relative = path[len(prefix) :].lstrip("/") if prefix else path
        paths.append(relative)
        if mode == "160000":
            gitlinks.append({"path": relative, "commit": oid})

    categories = {key: [] for key in CATEGORIES}
    for path in paths:
        for category, patterns in CATEGORIES.items():
            if any(re.search(pattern, path, re.I) for pattern in patterns):
                categories[category].append(path)
    report = {
        "schema": "harness-rig/m11-imported-surface-inventory/v2",
        "commit": args.commit,
        "prefix": prefix or None,
        "path_count": len(paths),
        "categories": categories,
        "gitlinks": gitlinks,
        "all_paths": paths,
    }
    print(json.dumps(report, indent=2) if args.json else f"{len(paths)} paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
