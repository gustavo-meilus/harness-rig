from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable


class GitError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        env=merged,
    )
    if check and p.returncode != 0:
        raise GitError(
            f"git {' '.join(args)} failed ({p.returncode}): "
            f"{p.stderr.decode('utf-8', 'replace')}"
        )
    return p


def nul_items(data: bytes) -> list[bytes]:
    return [item for item in data.split(b"\0") if item]
