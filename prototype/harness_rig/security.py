from __future__ import annotations

from pathlib import Path


class PathBoundaryError(ValueError):
    pass


def resolve_protected_path(root: Path, relative_path: str, *, allow_symlinks: bool = False) -> Path:
    root = root.resolve()
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise PathBoundaryError("absolute-path")
    if any(part == ".." for part in candidate.parts):
        raise PathBoundaryError("parent-traversal")

    current = root
    parts = [p for p in candidate.parts if p not in ("", ".")]
    for part in parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if current.is_symlink() and not allow_symlinks:
                raise PathBoundaryError("symlink-not-allowed")
            resolved = current.resolve()
            if root not in [resolved, *resolved.parents]:
                raise PathBoundaryError("path-escapes-root")
    resolved_final = current.resolve(strict=False)
    if root not in [resolved_final, *resolved_final.parents]:
        raise PathBoundaryError("path-escapes-root")
    return resolved_final
