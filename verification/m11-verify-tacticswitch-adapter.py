#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent


def run(command: list[str], cwd: pathlib.Path | None = None) -> tuple[int, str, int]:
    started = time.monotonic()
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    elapsed_ms = round((time.monotonic() - started) * 1000)
    return result.returncode, result.stdout + result.stderr, elapsed_ms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", default=str(ROOT / "verification/m11-source-bundles/tacticswitch.bundle"))
    parser.add_argument("--spec", default=str(HERE / "m11-history-import-spec.json"))
    parser.add_argument("--patch", default=str(HERE / "m11-adaptations/tacticswitch-manifest.patch"))
    parser.add_argument("--report")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    source = next(item for item in spec["sources"] if item["id"] == "tacticswitch")
    bundle = pathlib.Path(args.bundle).resolve()
    patch = pathlib.Path(args.patch).resolve()
    patch_hash = hashlib.sha256(patch.read_bytes()).hexdigest()
    report = {
        "schema": "harness-rig/m11-tacticswitch-adapter-verification/v1",
        "source_commit": source["source_commit"],
        "adapter": str(patch),
        "adapter_sha256": patch_hash,
        "result": "BLOCKED",
        "raw_source": {},
        "adapted_copy": {},
        "errors": [],
    }

    with tempfile.TemporaryDirectory(prefix="hr-m11-tacticswitch-adapter-") as temp_dir:
        repo = pathlib.Path(temp_dir) / "tacticswitch"
        rc, output, duration = run(["git", "clone", "--no-checkout", str(bundle), str(repo)])
        if rc:
            report["errors"].append({"step": "clone", "exit_code": rc, "output": output[-4000:]})
        else:
            rc, output, _ = run(["git", "checkout", "--detach", source["source_commit"]], repo)
            if rc:
                report["errors"].append({"step": "checkout", "exit_code": rc, "output": output[-4000:]})
            else:
                head_before = subprocess.check_output(
                    ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
                ).strip()
                rc, output, duration = run(
                    [sys.executable, "scripts/quality_gate.py"], repo
                )
                count_matches = re.findall(r"Ran (\d+) tests?", output)
                report["raw_source"] = {
                    "result": "FAIL" if rc else "PASS",
                    "exit_code": rc,
                    "tests_run": int(count_matches[-1]) if count_matches else None,
                    "expected_stale_manifest_failure": "FAIL: MANIFEST.sha256 is stale" in output,
                    "duration_ms": duration,
                    "output": output[-8000:],
                }
                if rc == 0 or not report["raw_source"]["expected_stale_manifest_failure"]:
                    report["errors"].append(
                        {"step": "raw-source-baseline", "reason": "expected-stale-manifest-failure-not-reproduced"}
                    )
                rc, output, _ = run(["git", "apply", "--check", str(patch)], repo)
                if rc:
                    report["errors"].append({"step": "patch-check", "exit_code": rc, "output": output[-4000:]})
                else:
                    rc, output, _ = run(["git", "apply", str(patch)], repo)
                    if rc:
                        report["errors"].append({"step": "patch-apply", "exit_code": rc, "output": output[-4000:]})
                    else:
                        changed = subprocess.check_output(
                            ["git", "-C", str(repo), "diff", "--name-only"], text=True
                        ).splitlines()
                        if changed != ["MANIFEST.sha256"]:
                            report["errors"].append(
                                {"step": "changed-paths", "expected": ["MANIFEST.sha256"], "actual": changed}
                            )
                        checksum_rc, checksum_output, _ = run(
                            [sys.executable, "scripts/checksums.py", "--verify"], repo
                        )
                        quality_rc, quality_output, quality_ms = run(
                            [sys.executable, "scripts/quality_gate.py"], repo
                        )
                        quality_counts = re.findall(r"Ran (\d+) tests?", quality_output)
                        head_after = subprocess.check_output(
                            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
                        ).strip()
                        report["adapted_copy"] = {
                            "manifest_check": "PASS" if checksum_rc == 0 else "FAIL",
                            "manifest_output": checksum_output[-2000:],
                            "quality_gate": "PASS" if quality_rc == 0 else "FAIL",
                            "tests_run": int(quality_counts[-1]) if quality_counts else None,
                            "duration_ms": quality_ms,
                            "output": quality_output[-8000:],
                            "changed_paths": changed,
                            "source_head_unchanged": head_after == head_before == source["source_commit"],
                        }
                        if checksum_rc:
                            report["errors"].append({"step": "manifest-check", "exit_code": checksum_rc})
                        if quality_rc or report["adapted_copy"]["tests_run"] != 200:
                            report["errors"].append(
                                {"step": "adapted-quality-gate", "exit_code": quality_rc, "tests_run": report["adapted_copy"]["tests_run"]}
                            )
                        if not report["adapted_copy"]["source_head_unchanged"]:
                            report["errors"].append({"step": "source-head", "reason": "source-commit-changed"})

    if not report["errors"]:
        report["result"] = "PASS_ADAPTER_ONLY"
    rendered = json.dumps(report, indent=2)
    if args.report:
        pathlib.Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered if args.json else report["result"])
    return 0 if report["result"] == "PASS_ADAPTER_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
