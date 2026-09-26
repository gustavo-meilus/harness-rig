#!/usr/bin/env python3
"""Run retained Harness Rig milestone tests in isolated subprocesses.

Each module writes to a temporary file rather than a PIPE. Some adversarial
fixtures intentionally spawn descendants; file-backed capture prevents an
unrelated descendant that inherited stdout from holding the parent runner's
pipe open after the unittest process itself has exited.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "prototype.tests.test_m3_vertical_slice",
    "prototype.tests.test_m4_core_promotion",
    "prototype.tests.test_m5_context_lifecycle",
    "prototype.tests.test_m6_openspec_spec_engine",
    "prototype.tests.test_m7_repository_enforcement",
    "prototype.tests.test_m8_host_capability",
    "prototype.tests.test_m9_gate_platform",
    "prototype.tests.test_m10_product_cli_migration_release",
    "prototype.tests.test_m11_source_native",
]
RAN_RE = re.compile(r"Ran (\d+) tests? in ")


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "prototype")
    env.setdefault("TERM", "dumb")
    failures: list[str] = []
    total = 0

    for module in MODULES:
        print(f"RUN  {module}", flush=True)
        with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as output:
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "unittest", module, "-v"],
                    cwd=ROOT,
                    env=env,
                    timeout=180,
                    check=False,
                    text=True,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            except subprocess.TimeoutExpired:
                output.seek(0)
                print(f"BLOCKED {module}: timeout", file=sys.stderr)
                print(output.read(), file=sys.stderr)
                failures.append(f"{module}:timeout")
                continue
            output.flush()
            output.seek(0)
            text = output.read()

        match = RAN_RE.search(text)
        count = int(match.group(1)) if match else 0
        total += count
        if proc.returncode == 0 and "\nOK" in text:
            print(f"PASS {module}: {count} tests", flush=True)
        else:
            print(f"FAIL {module}: exit={proc.returncode}", file=sys.stderr)
            print(text, file=sys.stderr)
            failures.append(f"{module}:exit={proc.returncode}")

    if failures:
        print("\nHarness Rig regression FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Harness Rig regression PASS: {total} tests across {len(MODULES)} milestone modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
