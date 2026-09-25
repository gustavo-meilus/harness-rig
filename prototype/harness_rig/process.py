from __future__ import annotations

import os
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ProcessResult:
    outcome: str
    returncode: int | None
    stdout: bytes
    stderr: bytes
    reason: str | None = None


def _terminate_tree(proc: subprocess.Popen[bytes], grace_seconds: float = 0.5) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        # The OS owns final reap semantics at this point; the process-group kill
        # has already been issued and no retry loop is useful here.
        pass


def run_process(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout_seconds: float,
) -> ProcessResult:
    """Run one argv-based process with bounded timeout and child-tree cleanup."""
    try:
        proc = subprocess.Popen(
            list(argv),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            shell=False,
            start_new_session=(os.name == "posix"),
        )
    except OSError as exc:
        return ProcessResult("BLOCKED", None, b"", str(exc).encode("utf-8", "replace"), "launch-failed")

    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        _terminate_tree(proc)
        stdout, stderr = proc.communicate()
        return ProcessResult("TIMEOUT", proc.returncode, stdout, stderr, "timeout")
    except KeyboardInterrupt:
        _terminate_tree(proc)
        try:
            proc.communicate(timeout=0.2)
        except Exception:
            pass
        raise

    return ProcessResult(
        "PASS" if proc.returncode == 0 else "FAIL",
        proc.returncode,
        stdout,
        stderr,
        None,
    )
