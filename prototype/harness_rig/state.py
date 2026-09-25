from __future__ import annotations

import os
import stat
from dataclasses import dataclass, asdict
from pathlib import Path

from .canonical import digest, sha256_bytes
from .gitutil import GitError, git, nul_items


@dataclass(frozen=True)
class RevisionIdentity:
    head_oid: str
    head_tree_oid: str | None


@dataclass(frozen=True)
class SubmoduleIdentity:
    path: str
    recorded_gitlink_oid: str
    observed_head_oid: str | None
    content_id: str | None
    status: str


@dataclass(frozen=True)
class StateIdentity:
    schema: str
    repository_id: str
    revision: RevisionIdentity
    index_manifest_digest: str
    tracked_manifest_digest: str
    untracked_nonignored_manifest_digest: str
    submodules: tuple[SubmoduleIdentity, ...]
    content_id: str
    state_id: str


def _logical_entry(path: Path) -> dict:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return {"kind": "deleted"}
    if stat.S_ISLNK(st.st_mode):
        return {
            "kind": "symlink",
            "target": os.readlink(path),
            "mode": stat.S_IMODE(st.st_mode),
        }
    if stat.S_ISREG(st.st_mode):
        return {
            "kind": "file",
            "mode": stat.S_IMODE(st.st_mode),
            "bytes": sha256_bytes(path.read_bytes()),
        }
    if stat.S_ISDIR(st.st_mode):
        return {"kind": "directory", "mode": stat.S_IMODE(st.st_mode)}
    return {"kind": "other", "mode": stat.S_IMODE(st.st_mode)}


def _head(repo: Path) -> RevisionIdentity:
    p = git(repo, "rev-parse", "--verify", "HEAD", check=False)
    if p.returncode != 0:
        return RevisionIdentity("UNBORN", None)
    head = p.stdout.decode().strip()
    tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.decode().strip()
    return RevisionIdentity(head, tree)


def _index_entries(repo: Path) -> tuple[list[dict], dict[str, str]]:
    raw = git(repo, "ls-files", "-s", "-z").stdout
    rows: list[dict] = []
    gitlinks: dict[str, str] = {}
    for rec in nul_items(raw):
        meta, path_b = rec.split(b"\t", 1)
        mode_b, oid_b, stage_b = meta.split()
        path_key = path_b.hex()
        path_display = path_b.decode("utf-8", "surrogateescape")
        row = {
            "path_key": path_key,
            "mode": mode_b.decode(),
            "oid": oid_b.decode(),
            "stage": int(stage_b),
        }
        rows.append(row)
        if mode_b == b"160000":
            gitlinks[path_display] = oid_b.decode()
    rows.sort(key=lambda x: x["path_key"])
    return rows, gitlinks


def _tracked_manifest(repo: Path, gitlinks: dict[str, str]) -> list[dict]:
    raw = git(repo, "ls-files", "-z").stdout
    rows = []
    for path_b in nul_items(raw):
        path_display = path_b.decode("utf-8", "surrogateescape")
        path_key = path_b.hex()
        if path_display in gitlinks:
            rows.append({
                "path_key": path_key,
                "kind": "gitlink",
                "recorded_oid": gitlinks[path_display],
            })
            continue
        rows.append({
            "path_key": path_key,
            "entry": _logical_entry(repo / path_display),
        })
    rows.sort(key=lambda x: x["path_key"])
    return rows


def _untracked_manifest(repo: Path) -> list[dict]:
    raw = git(repo, "ls-files", "--others", "--exclude-standard", "-z").stdout
    rows = []
    for path_b in nul_items(raw):
        path_display = path_b.decode("utf-8", "surrogateescape")
        rows.append({
            "path_key": path_b.hex(),
            "entry": _logical_entry(repo / path_display),
        })
    rows.sort(key=lambda x: x["path_key"])
    return rows


def _submodule_state(repo: Path, path: str, recorded_oid: str) -> SubmoduleIdentity:
    sub = repo / path
    if not sub.exists():
        return SubmoduleIdentity(path, recorded_oid, None, None, "UNINITIALIZED")
    p = git(sub, "rev-parse", "--verify", "HEAD", check=False)
    if p.returncode != 0:
        return SubmoduleIdentity(path, recorded_oid, None, None, "UNREADABLE")
    observed = p.stdout.decode().strip()

    # A nested StateIdentity is too recursive for M3. Use exact nested manifests plus revision,
    # enough to make dirty consumed submodule content visible.
    try:
        index_rows, nested_gitlinks = _index_entries(sub)
        tracked = _tracked_manifest(sub, nested_gitlinks)
        untracked = _untracked_manifest(sub)
        nested_content = digest({
            "revision": observed,
            "index": index_rows,
            "tracked": tracked,
            "untracked": untracked,
        })
        status = "CLEAN" if not git(sub, "status", "--porcelain=v1", "-z").stdout else "DIRTY"
        if observed != recorded_oid and status == "CLEAN":
            status = "HEAD_MISMATCH"
        elif observed != recorded_oid and status == "DIRTY":
            status = "HEAD_MISMATCH_DIRTY"
        return SubmoduleIdentity(path, recorded_oid, observed, nested_content, status)
    except (GitError, OSError):
        return SubmoduleIdentity(path, recorded_oid, observed, None, "UNREADABLE")


def capture_state(repo: Path, repository_id: str = "local-repository") -> StateIdentity:
    repo = repo.resolve()
    if git(repo, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise ValueError(f"not a Git worktree: {repo}")

    revision = _head(repo)
    index_rows, gitlinks = _index_entries(repo)
    tracked_rows = _tracked_manifest(repo, gitlinks)
    untracked_rows = _untracked_manifest(repo)
    submodules = tuple(
        _submodule_state(repo, path, oid)
        for path, oid in sorted(gitlinks.items())
    )

    index_digest = digest(index_rows)
    tracked_digest = digest(tracked_rows)
    untracked_digest = digest(untracked_rows)
    content_id = digest({
        "tracked": tracked_rows,
        "untracked_nonignored": untracked_rows,
        "submodules": [asdict(x) for x in submodules],
    })
    material = {
        "schema": "harness-rig/state-identity/experimental-v1",
        "repository_id": repository_id,
        "revision": asdict(revision),
        "index_manifest_digest": index_digest,
        "tracked_manifest_digest": tracked_digest,
        "untracked_nonignored_manifest_digest": untracked_digest,
        "submodules": [asdict(x) for x in submodules],
        "content_id": content_id,
    }
    return StateIdentity(
        schema=material["schema"],
        repository_id=repository_id,
        revision=revision,
        index_manifest_digest=index_digest,
        tracked_manifest_digest=tracked_digest,
        untracked_nonignored_manifest_digest=untracked_digest,
        submodules=submodules,
        content_id=content_id,
        state_id=digest(material),
    )
