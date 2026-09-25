from __future__ import annotations

import os
import stat
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .canonical import digest, is_sha256_digest, sha256_bytes
from .gitutil import GitError, git, nul_items


STATE_IDENTITY_SCHEMA = "harness-rig/state-identity/v1"
LEGACY_STATE_IDENTITY_SCHEMA = "harness-rig/state-identity/experimental-v1"


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
    """Stable exact Git-worktree state identity.

    The shared value is deterministic and serializable. capture_state is the
    current Git worktree capture implementation; other state domains must not
    smuggle provider data into this schema.
    """

    schema: str
    repository_id: str
    revision: RevisionIdentity
    index_manifest_digest: str
    tracked_manifest_digest: str
    untracked_nonignored_manifest_digest: str
    submodules: tuple[SubmoduleIdentity, ...]
    content_id: str
    state_id: str

    def recompute_state_id(self) -> str:
        return digest(_state_material(self, schema=self.schema))


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

    # A nested StateIdentity would be recursive. Exact nested manifests plus
    # revision are sufficient to make dirty consumed submodule content visible.
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


def _state_material(state: StateIdentity, *, schema: str) -> dict[str, Any]:
    return {
        "schema": schema,
        "repository_id": state.repository_id,
        "revision": asdict(state.revision),
        "index_manifest_digest": state.index_manifest_digest,
        "tracked_manifest_digest": state.tracked_manifest_digest,
        "untracked_nonignored_manifest_digest": state.untracked_nonignored_manifest_digest,
        "submodules": [asdict(x) for x in state.submodules],
        "content_id": state.content_id,
    }


def _build_state_identity(
    *,
    repository_id: str,
    revision: RevisionIdentity,
    index_manifest_digest: str,
    tracked_manifest_digest: str,
    untracked_nonignored_manifest_digest: str,
    submodules: tuple[SubmoduleIdentity, ...],
    content_id: str,
) -> StateIdentity:
    provisional = StateIdentity(
        schema=STATE_IDENTITY_SCHEMA,
        repository_id=repository_id,
        revision=revision,
        index_manifest_digest=index_manifest_digest,
        tracked_manifest_digest=tracked_manifest_digest,
        untracked_nonignored_manifest_digest=untracked_nonignored_manifest_digest,
        submodules=submodules,
        content_id=content_id,
        state_id="",
    )
    return StateIdentity(
        **{**asdict(provisional), "revision": revision, "submodules": submodules,
           "state_id": digest(_state_material(provisional, schema=STATE_IDENTITY_SCHEMA))}
    )


def capture_state(repo: Path, repository_id: str = "local-repository") -> StateIdentity:
    repo = repo.resolve()
    if git(repo, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise ValueError(f"not a Git worktree: {repo}")
    if not isinstance(repository_id, str) or not repository_id:
        raise ValueError("invalid-repository-id")

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
    return _build_state_identity(
        repository_id=repository_id,
        revision=revision,
        index_manifest_digest=index_digest,
        tracked_manifest_digest=tracked_digest,
        untracked_nonignored_manifest_digest=untracked_digest,
        submodules=submodules,
        content_id=content_id,
    )


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid-state-identity-{field}")
    return value


def _required_digest(value: Any, field: str) -> str:
    value = _required_string(value, field)
    if not is_sha256_digest(value):
        raise ValueError(f"invalid-state-identity-{field}")
    return value


def _load_revision(data: Any) -> RevisionIdentity:
    if not isinstance(data, dict) or set(data) != {"head_oid", "head_tree_oid"}:
        raise ValueError("invalid-state-identity-revision")
    head_oid = _required_string(data["head_oid"], "head-oid")
    head_tree_oid = data["head_tree_oid"]
    if head_tree_oid is not None:
        head_tree_oid = _required_string(head_tree_oid, "head-tree-oid")
    return RevisionIdentity(head_oid, head_tree_oid)


def _load_submodule(data: Any) -> SubmoduleIdentity:
    fields = {"path", "recorded_gitlink_oid", "observed_head_oid", "content_id", "status"}
    if not isinstance(data, dict) or set(data) != fields:
        raise ValueError("invalid-state-identity-submodule")
    observed = data["observed_head_oid"]
    if observed is not None:
        observed = _required_string(observed, "submodule-observed-head")
    content_id = data["content_id"]
    if content_id is not None:
        content_id = _required_digest(content_id, "submodule-content-id")
    return SubmoduleIdentity(
        path=_required_string(data["path"], "submodule-path"),
        recorded_gitlink_oid=_required_string(data["recorded_gitlink_oid"], "submodule-recorded-oid"),
        observed_head_oid=observed,
        content_id=content_id,
        status=_required_string(data["status"], "submodule-status"),
    )


def load_state_identity(data: dict[str, Any]) -> StateIdentity:
    """Load stable v1 or deterministically migrate M3 experimental v1.

    Migration verifies the old state_id first, then recomputes state_id under the
    stable schema. Unknown schemas, extra fields, or integrity mismatches fail.
    """

    if not isinstance(data, dict):
        raise ValueError("invalid-state-identity")
    fields = {
        "schema", "repository_id", "revision", "index_manifest_digest",
        "tracked_manifest_digest", "untracked_nonignored_manifest_digest",
        "submodules", "content_id", "state_id",
    }
    if set(data) != fields:
        raise ValueError("invalid-state-identity-fields")
    schema = data.get("schema")
    if schema not in {STATE_IDENTITY_SCHEMA, LEGACY_STATE_IDENTITY_SCHEMA}:
        raise ValueError("unsupported-state-identity-schema")

    revision = _load_revision(data["revision"])
    raw_submodules = data["submodules"]
    if not isinstance(raw_submodules, (list, tuple)):
        raise ValueError("invalid-state-identity-submodules")
    submodules = tuple(_load_submodule(x) for x in raw_submodules)
    state = StateIdentity(
        schema=schema,
        repository_id=_required_string(data["repository_id"], "repository-id"),
        revision=revision,
        index_manifest_digest=_required_digest(data["index_manifest_digest"], "index-manifest-digest"),
        tracked_manifest_digest=_required_digest(data["tracked_manifest_digest"], "tracked-manifest-digest"),
        untracked_nonignored_manifest_digest=_required_digest(
            data["untracked_nonignored_manifest_digest"], "untracked-manifest-digest"
        ),
        submodules=submodules,
        content_id=_required_digest(data["content_id"], "content-id"),
        state_id=_required_digest(data["state_id"], "state-id"),
    )
    if digest(_state_material(state, schema=schema)) != state.state_id:
        raise ValueError("invalid-state-identity-integrity")
    if schema == STATE_IDENTITY_SCHEMA:
        return state

    return _build_state_identity(
        repository_id=state.repository_id,
        revision=state.revision,
        index_manifest_digest=state.index_manifest_digest,
        tracked_manifest_digest=state.tracked_manifest_digest,
        untracked_nonignored_manifest_digest=state.untracked_nonignored_manifest_digest,
        submodules=state.submodules,
        content_id=state.content_id,
    )
