#!/usr/bin/env python3
"""Reconstruct Harness Rig milestone Git history from retained verified snapshots.

The resulting commits are intentionally synthetic reconstruction commits. They
preserve verified milestone file states and sequencing; they do not claim to be
original development history.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / ".bootstrap"
MANIFEST_PATH = ROOT / "handoff" / "GIT_HISTORY_RECONSTRUCTION.json"
SYNTHETIC_NAME = "Harness Rig Bootstrap"
SYNTHETIC_EMAIL = "bootstrap@local.invalid"

EXCLUDE_NAMES = {".git", ".bootstrap", "__pycache__", ".pytest_cache"}


class BootstrapError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(*args: str, cwd: Path, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        list(args), cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    if check and proc.returncode != 0:
        raise BootstrapError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout}")
    return proc


def clear_worktree(repo: Path) -> None:
    for child in repo.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def copy_tree(src: Path, dst: Path, *, exclude_payload: bool = False) -> None:
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        if any(part in EXCLUDE_NAMES for part in rel.parts):
            continue
        if exclude_payload and rel.parts and rel.parts[0] == ".bootstrap":
            continue
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(os.readlink(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def extract_snapshot(zip_path: Path, destination: Path, expected_root: str) -> Path:
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        if bad:
            raise BootstrapError(f"corrupt zip member in {zip_path.name}: {bad}")
        zf.extractall(destination)
    root = destination / expected_root
    if not root.is_dir():
        raise BootstrapError(f"snapshot {zip_path.name} missing root {expected_root!r}")
    return root


def commit(repo: Path, subject: str, body: str) -> str:
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": SYNTHETIC_NAME,
        "GIT_AUTHOR_EMAIL": SYNTHETIC_EMAIL,
        "GIT_COMMITTER_NAME": SYNTHETIC_NAME,
        "GIT_COMMITTER_EMAIL": SYNTHETIC_EMAIL,
    })
    run("git", "add", "-A", cwd=repo, env=env)
    status = run("git", "status", "--porcelain", cwd=repo, env=env).stdout.strip()
    if not status:
        raise BootstrapError(f"refusing empty reconstruction commit: {subject}")
    run("git", "commit", "--no-gpg-sign", "-m", subject, "-m", body, cwd=repo, env=env)
    return run("git", "rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()


def tracked_file_map(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in EXCLUDE_NAMES for part in rel.parts):
            continue
        if path.is_dir():
            continue
        if path.is_symlink():
            out[str(rel)] = "symlink:" + os.readlink(path)
        else:
            out[str(rel)] = sha256(path)
    return out


def main() -> int:
    if (ROOT / ".git").exists():
        raise BootstrapError(".git already exists; refusing to overwrite an existing repository")
    if shutil.which("git") is None:
        raise BootstrapError("git executable not found on PATH")
    if not MANIFEST_PATH.exists():
        raise BootstrapError(f"missing reconstruction manifest: {MANIFEST_PATH}")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema") != "harness-rig/git-history-reconstruction/v1":
        raise BootstrapError("unsupported reconstruction manifest schema")

    milestones = manifest.get("milestones")
    if not isinstance(milestones, list) or not milestones:
        raise BootstrapError("reconstruction manifest has no milestones")

    for item in milestones:
        package = PAYLOAD / "snapshots" / item["package"]
        plan = PAYLOAD / "plans" / item["plan"]
        for path, expected in ((package, item["package_sha256"]), (plan, item["plan_sha256"])):
            if not path.exists():
                raise BootstrapError(f"missing bootstrap payload: {path}")
            actual = sha256(path)
            if actual != expected:
                raise BootstrapError(f"SHA-256 mismatch for {path.name}: expected {expected}, got {actual}")

    tmp_parent = ROOT.parent
    tmp = Path(tempfile.mkdtemp(prefix=f".{ROOT.name}-git-bootstrap-", dir=tmp_parent))
    repo = tmp / "repo"
    repo.mkdir()
    commits: list[tuple[str, str]] = []

    try:
        init = run("git", "init", "--initial-branch=main", cwd=repo, check=False)
        if init.returncode != 0:
            # Older Git fallback.
            run("git", "init", cwd=repo)
            run("git", "checkout", "-b", "main", cwd=repo)

        for item in milestones:
            clear_worktree(repo)
            with tempfile.TemporaryDirectory(prefix="hr-snapshot-") as d:
                extracted = extract_snapshot(
                    PAYLOAD / "snapshots" / item["package"], Path(d), manifest["source_root_name"]
                )
                copy_tree(extracted, repo)
            shutil.copy2(PAYLOAD / "plans" / item["plan"], repo / "PROGRESSIVE_REMEDIATION_PLAN.md")
            body = (
                f"Synthetic Harness Rig milestone reconstruction.\n\n"
                f"Milestone: {item['milestone']}\n"
                f"Revision: {item['revision']}\n"
                f"Package-SHA256: {item['package_sha256']}\n"
                f"Plan-SHA256: {item['plan_sha256']}\n"
                "History-Nature: reconstructed-from-verified-snapshot\n"
                "Original-Development-Commit: no\n"
            )
            oid = commit(repo, item["commit_subject"], body)
            commits.append((item["revision"], oid))

        # Final post-r8.10 environment transformation. This does not advance M11.
        clear_worktree(repo)
        copy_tree(ROOT, repo, exclude_payload=True)
        trans = manifest["transformation_commit"]
        body = (
            "Prepare the extracted r8.10 state for a real Git repository and a fresh Codex/OpenSpec context.\n\n"
            "Milestone-Advance: none\n"
            f"Next-Task: {trans['next_task']}\n"
            "Primary-Host-Target: Codex Desktop/CLI\n"
            "Secondary-Host-Target: Claude Code\n"
            "History-Nature: repository-environment-transformation\n"
        )
        oid = commit(repo, trans["subject"], body)
        commits.append(("handoff", oid))

        # Ensure the committed final tree is exactly the extracted handoff tree,
        # excluding ignored reconstruction payload/cache directories.
        source_map = tracked_file_map(ROOT)
        rebuilt_map = tracked_file_map(repo)
        if source_map != rebuilt_map:
            missing = sorted(set(source_map) - set(rebuilt_map))
            extra = sorted(set(rebuilt_map) - set(source_map))
            changed = sorted(k for k in set(source_map) & set(rebuilt_map) if source_map[k] != rebuilt_map[k])
            raise BootstrapError(
                "final tree mismatch after reconstruction\n"
                f"missing={missing[:20]}\nextra={extra[:20]}\nchanged={changed[:20]}"
            )

        if run("git", "status", "--porcelain", cwd=repo).stdout.strip():
            raise BootstrapError("temporary reconstructed repository is not clean")

        shutil.move(str(repo / ".git"), str(ROOT / ".git"))

        final_status = run("git", "status", "--porcelain", cwd=ROOT).stdout.strip()
        if final_status:
            raise BootstrapError(f"installed repository is not clean:\n{final_status}")

        print("Harness Rig Git reconstruction PASS")
        for revision, commit_id in commits:
            print(f"{revision:8s} {commit_id}")
        print("\nSynthetic reconstruction history installed on branch main.")
        print("Next: run python tools/run_all_tests.py, audit the KB, configure real Git identity, then initialize OpenSpec for Codex.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BootstrapError as exc:
        print(f"BOOTSTRAP BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(2)
