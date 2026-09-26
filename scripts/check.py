#!/usr/bin/env python3
"""Run the repository's canonical verification checks."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONUTF8"] = "1"
CHECKS = (
    (sys.executable, str(ROOT / "tools" / "run_all_tests.py")),
    (sys.executable, str(ROOT / "verification" / "context_kb.py"), "audit", "."),
    (sys.executable, str(ROOT / "verification" / "context_kb.py"), "projection-status", "."),
    ("git", "diff", "--check"),
)

failure = 0
for command in CHECKS:
    result = subprocess.run(command, cwd=ROOT, env=ENV)
    if result.returncode and not failure:
        failure = result.returncode

raise SystemExit(failure)
