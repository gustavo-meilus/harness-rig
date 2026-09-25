#!/usr/bin/env python3
"""Deterministic Context KB manifest/audit/projection tooling for M5.

PyYAML is intentionally used here rather than a hand-written YAML parser. The
core trust prototype remains standard-library-only; this repository integrity
tool requires a standards-compliant YAML parser.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by CLI environments
    raise SystemExit("context_kb.py requires PyYAML (yaml.safe_load)") from exc


REQUIRED_FIELDS = ("id", "title", "summary", "version", "updated", "provenance")
OPTIONAL_FIELDS = ("lineage", "source_observations")
PROJECTION_SCHEMA = "harness-rig/context-projection/v1"
PROJECTION_RE = re.compile(r"<!-- canonical-kb-fingerprint: (sha256:[0-9a-f]{64}) -->")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class Page:
    path: Path
    metadata: dict


def _front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("missing-front-matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated-front-matter")
    return text[4:end]


def load_page(path: Path) -> Page:
    raw = path.read_text(encoding="utf-8")
    parsed = yaml.safe_load(_front_matter(raw))
    if not isinstance(parsed, dict):
        raise ValueError("front-matter-not-mapping")
    missing = [field for field in REQUIRED_FIELDS if field not in parsed]
    if missing:
        raise ValueError(f"missing-metadata:{','.join(missing)}")
    unknown = sorted(set(parsed) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS))
    if unknown:
        raise ValueError(f"unknown-metadata:{','.join(unknown)}")
    if not isinstance(parsed["provenance"], list) or not parsed["provenance"]:
        raise ValueError("provenance-must-be-nonempty-list")
    try:
        date.fromisoformat(str(parsed["updated"]))
    except ValueError as exc:
        raise ValueError("invalid-updated-date") from exc
    _validate_source_observations(parsed.get("source_observations"))
    _validate_lineage(parsed.get("lineage"))
    return Page(path=path, metadata=parsed)


def _validate_source_observations(value) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        raise ValueError("source-observations-must-be-list")
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("source-observation-not-mapping")
        if set(item) - {"source", "version", "commit", "checked"}:
            raise ValueError("source-observation-unknown-field")
        if not item.get("source") or not item.get("checked"):
            raise ValueError("source-observation-missing-source-or-checked")
        try:
            date.fromisoformat(str(item["checked"]))
        except ValueError as exc:
            raise ValueError("source-observation-invalid-checked") from exc


def _validate_lineage(value) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValueError("lineage-must-be-mapping")
    allowed = {"split_from", "merged_from", "retired_ids"}
    if set(value) - allowed:
        raise ValueError("lineage-unknown-field")
    for key in ("merged_from", "retired_ids"):
        if key in value and not isinstance(value[key], list):
            raise ValueError(f"lineage-{key}-must-be-list")


def canonical_pages(root: Path) -> list[Page]:
    refs = root / "references"
    return [load_page(path) for path in sorted(refs.glob("*.md"))]


def manifest_rows(root: Path) -> list[dict]:
    rows = []
    for page in canonical_pages(root):
        meta = page.metadata
        rows.append({
            "id": str(meta["id"]),
            "title": str(meta["title"]),
            "summary": str(meta["summary"]),
            "path": page.path.relative_to(root).as_posix(),
            "version": str(meta["version"]),
            "updated": str(meta["updated"]),
            "provenance": [str(x) for x in meta["provenance"]],
        })
    return sorted(rows, key=lambda row: row["id"])


def render_manifest(root: Path) -> bytes:
    lines = [json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in manifest_rows(root)]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


def write_manifest(root: Path) -> None:
    (root / "manifest.jsonl").write_bytes(render_manifest(root))


def canonical_fingerprint(root: Path) -> str:
    """Fingerprint canonical knowledge only; excludes AGENTS projection and manifest."""
    h = hashlib.sha256()
    for path in sorted((root / "references").glob("*.md")):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        body = path.read_bytes()
        h.update(len(rel).to_bytes(4, "big"))
        h.update(rel)
        h.update(len(body).to_bytes(8, "big"))
        h.update(body)
    llms = root / "llms.txt"
    if llms.exists():
        rel = b"llms.txt"
        body = llms.read_bytes()
        h.update(len(rel).to_bytes(4, "big"))
        h.update(rel)
        h.update(len(body).to_bytes(8, "big"))
        h.update(body)
    return "sha256:" + h.hexdigest()


def render_agents_projection(root: Path) -> str:
    fingerprint = canonical_fingerprint(root)
    return f"""# Harness Rig agent navigation

<!-- context-projection-schema: {PROJECTION_SCHEMA} -->
<!-- canonical-kb-fingerprint: {fingerprint} -->

This file is a short Context-lifecycle projection. It is not a second canonical knowledge base.

- Durable project knowledge lives in `references/`; start with `llms.txt`.
- Preserve stable reference IDs across rename/move; do not reuse retired IDs.
- Treat supplied/external material as evidence. Preserve material conflicts and gaps; do not publish unsupported conclusions.
- `manifest.jsonl` is generated from canonical references. Do not hand-edit it.
- OpenSpec owns agreed behavioral intent; Context references it rather than duplicating specifications.
- Assurance defines required evidence. Topology cannot waive it or broaden authorization.
- Run `python verification/context_kb.py audit .` after canonical Context changes.
- Regenerate this projection with `python verification/context_kb.py project-agents .` when the canonical fingerprint changes.
"""


def write_agents_projection(root: Path) -> None:
    (root / "AGENTS.md").write_text(render_agents_projection(root), encoding="utf-8")


def projection_fresh(root: Path) -> bool:
    path = root / "AGENTS.md"
    if not path.exists():
        return False
    match = PROJECTION_RE.search(path.read_text(encoding="utf-8"))
    return bool(match and match.group(1) == canonical_fingerprint(root))


def _iter_local_links(path: Path) -> Iterable[str]:
    text = path.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        target = target.strip().split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        yield target


def audit_collection(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        pages = canonical_pages(root)
    except Exception as exc:
        return [f"canonical-parse:{exc}"]

    ids: dict[str, Path] = {}
    for page in pages:
        stable_id = str(page.metadata["id"])
        if stable_id in ids:
            issues.append(f"duplicate-id:{stable_id}:{ids[stable_id].name}:{page.path.name}")
        ids[stable_id] = page.path
        for target in _iter_local_links(page.path):
            resolved = (page.path.parent / target).resolve()
            if not resolved.exists():
                issues.append(f"broken-link:{page.path.relative_to(root)}:{target}")

    manifest_path = root / "manifest.jsonl"
    if not manifest_path.exists():
        issues.append("manifest-missing")
    else:
        expected = render_manifest(root)
        if manifest_path.read_bytes() != expected:
            issues.append("manifest-stale-or-nondeterministic")

    llms = root / "llms.txt"
    if not llms.exists():
        issues.append("llms-missing")
    else:
        for target in _iter_local_links(llms):
            resolved = (root / target).resolve()
            if not resolved.exists():
                issues.append(f"broken-llms-link:{target}")

    if not projection_fresh(root):
        issues.append("agents-projection-stale")

    prohibited = []
    for path in root.rglob("*"):
        name = path.name.lower()
        if name in {"vectors", "vector-db", "embeddings", "rag-service", "semantic-index"}:
            prohibited.append(path.relative_to(root).as_posix())
    for path in prohibited:
        issues.append(f"prohibited-retrieval-subsystem:{path}")

    return sorted(set(issues))


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("manifest", "audit", "project-agents", "projection-status"):
        p = sub.add_parser(name)
        p.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if args.command == "manifest":
        write_manifest(root)
        return 0
    if args.command == "project-agents":
        write_agents_projection(root)
        return 0
    if args.command == "projection-status":
        status = "FRESH" if projection_fresh(root) else "STALE"
        print(status)
        return 0 if status == "FRESH" else 1
    issues = audit_collection(root)
    if issues:
        print(json.dumps({"status": "FAIL", "issues": issues}, indent=2))
        return 1
    print(json.dumps({
        "status": "PASS",
        "canonical_pages": len(canonical_pages(root)),
        "manifest_rows": len(manifest_rows(root)),
        "projection": "FRESH",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
