#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
WINDOWS_GIT_PATH = [
    r"C:\Program Files\Git\bin",
    r"C:\Program Files\Git\usr\bin",
    r"C:\Program Files\Git\mingw64\libexec\git-core",
]


def call(command: list[str], cwd: pathlib.Path = ROOT, env: dict | None = None) -> tuple[int, dict]:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    try:
        evidence = json.loads(result.stdout)
    except json.JSONDecodeError:
        evidence = {"stdout": result.stdout, "stderr": result.stderr}
    return result.returncode, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repo", default=str(ROOT))
    parser.add_argument("--import-commit", required=True)
    parser.add_argument(
        "--legacy-checks",
        default=str(HERE / "m11-legacy-check-config.json"),
    )
    parser.add_argument(
        "--expected-manifest",
        default=str(HERE / "m11-source-bundle-manifest.json"),
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    target = pathlib.Path(args.target_repo).resolve()
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    if os.name == "nt":
        env["PATH"] = os.pathsep.join(WINDOWS_GIT_PATH + [env.get("PATH", "")])

    spec = json.loads((HERE / "m11-history-import-spec.json").read_text(encoding="utf-8"))
    checks = json.loads(pathlib.Path(args.legacy_checks).read_text(encoding="utf-8"))
    report = {"schema": "harness-rig/m11-verification-gate/v2", "result": "PASS", "checks": {}}

    def record(key: str, command: list[str], cwd: pathlib.Path = target) -> None:
        code, evidence = call(command, cwd=cwd, env=env)
        report["checks"][key] = {"exit_code": code, "evidence": evidence}
        if code == 2:
            report["result"] = "BLOCKED"
        elif code and report["result"] != "BLOCKED":
            report["result"] = "FAIL"

    record(
        "source-bundles",
        [sys.executable, str(HERE / "m11-history-input-preflight.py"),
         "--expected-manifest", args.expected_manifest, "--json"],
    )
    record(
        "source-signatures-and-tags",
        [sys.executable, str(HERE / "m11-verify-source-signatures.py"), "--json"],
    )

    submodules = []
    for source in spec["sources"]:
        path = target / source["target_prefix"]
        try:
            head = subprocess.check_output(
                ["git", "-C", str(path), "rev-parse", "HEAD"], text=True, env=env
            ).strip()
            status = subprocess.check_output(
                ["git", "-C", str(path), "status", "--porcelain", "--untracked-files=all"],
                text=True,
                env=env,
            ).strip()
            url = subprocess.check_output(
                ["git", "-C", str(path), "remote", "get-url", "origin"],
                text=True,
                env=env,
            ).strip()
            ok = head == source["source_commit"] and not status and url == source["repository"]
            submodules.append(
                {"source": source["id"], "head": head, "clean": not status, "url": url, "result": "PASS" if ok else "FAIL"}
            )
            if not ok and report["result"] != "BLOCKED":
                report["result"] = "FAIL"
        except (OSError, subprocess.CalledProcessError) as error:
            submodules.append({"source": source["id"], "result": "BLOCKED", "detail": str(error)})
            report["result"] = "BLOCKED"
    report["checks"]["source-submodules"] = {"exit_code": 0 if all(x["result"] == "PASS" for x in submodules) else 2, "evidence": submodules}

    record(
        "import-only",
        [sys.executable, str(HERE / "m11-verify-import-only.py"),
         "--repo", str(target), "--commit", args.import_commit, "--json"],
    )
    record(
        "tacticswitch-adapter",
        [sys.executable, str(HERE / "m11-verify-tacticswitch-adapter.py"), "--json"],
    )

    legacy_results = []
    for source, config in checks.items():
        code, evidence = call(
            [sys.executable, str(HERE / "m11-run-legacy-checks.py"),
             "--repo", str(target / config["repo"]), "--checks", str(HERE / config["checks"]), "--json"],
            cwd=target,
            env=env,
        )
        legacy_results.append({"source": source, "exit_code": code, "evidence": evidence})
        if code == 2:
            report["result"] = "BLOCKED"
        elif code and report["result"] != "BLOCKED":
            report["result"] = "FAIL"
    report["checks"]["legacy-checks"] = {"exit_code": 0 if all(x["exit_code"] == 0 for x in legacy_results) else 1, "evidence": legacy_results}

    surfaces = []
    for source in spec["sources"]:
        code, evidence = call(
            [sys.executable, str(HERE / "m11-inventory-imported-surface.py"),
             "--repo", str(target / source["target_prefix"]),
             "--commit", source["source_commit"], "--json"],
            cwd=target,
            env=env,
        )
        surfaces.append({"source": source["id"], "exit_code": code, "evidence": evidence})
        if code and report["result"] != "BLOCKED":
            report["result"] = "FAIL"
    report["checks"]["source-surfaces"] = {"exit_code": 0 if all(x["exit_code"] == 0 for x in surfaces) else 1, "evidence": surfaces}

    rendered = json.dumps(report, indent=2)
    print(rendered if args.json else report["result"])
    return 0 if report["result"] == "PASS" else (2 if report["result"] == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
