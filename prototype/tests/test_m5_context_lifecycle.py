from __future__ import annotations

import importlib.util
import tempfile
import unittest
import sys
from pathlib import Path

from harness_rig.context import (
    CONFLICT,
    FRESH,
    STALE,
    SUPPORTED,
    UNKNOWN,
    UNSUPPORTED,
    SourceClaim,
    SourceObservation,
    StableIdError,
    StableIdRegistry,
    reconcile_claim,
    source_freshness,
)


KB_ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = KB_ROOT / "verification" / "context_kb.py"
SPEC = importlib.util.spec_from_file_location("context_kb_tool", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot-load-context-kb-tool")
context_kb = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = context_kb
SPEC.loader.exec_module(context_kb)


def write_page(root: Path, name: str, stable_id: str, *, body: str = "# Topic\n", extra: str = "") -> Path:
    refs = root / "references"
    refs.mkdir(parents=True, exist_ok=True)
    path = refs / name
    path.write_text(
        "---\n"
        f"id: {stable_id}\n"
        f"title: {stable_id}\n"
        "summary: Fixture page.\n"
        "version: fixture-v1\n"
        "updated: '2026-09-25'\n"
        "provenance:\n"
        "- fixture\n"
        f"{extra}"
        "---\n"
        f"{body}",
        encoding="utf-8",
    )
    return path


class HarnessRigM5ContextTests(unittest.TestCase):
    # M5-T02 / M5-V01
    def test_rename_or_move_preserves_stable_id(self):
        registry = StableIdRegistry({"topic-a": "references/a.md"})
        registry.rename_or_move("topic-a", "references/renamed.md")
        self.assertEqual(registry.active, {"topic-a": "references/renamed.md"})

    def test_split_keeps_old_id_on_primary_and_requires_new_ids_for_other_topics(self):
        registry = StableIdRegistry({"topic-a": "references/a.md"})
        registry.split(
            "topic-a",
            primary_path="references/a-primary.md",
            additional={"topic-b": "references/b.md"},
        )
        self.assertEqual(registry.active["topic-a"], "references/a-primary.md")
        self.assertEqual(registry.active["topic-b"], "references/b.md")

    def test_merge_retires_absorbed_id_and_retired_ids_cannot_be_reused(self):
        registry = StableIdRegistry({"topic-a": "references/a.md", "topic-b": "references/b.md"})
        registry.merge("topic-a", ["topic-b"], survivor_path="references/merged.md")
        self.assertEqual(registry.active, {"topic-a": "references/merged.md"})
        self.assertIn("topic-b", registry.retired)
        with self.assertRaisesRegex(StableIdError, "retired-id-reuse"):
            registry.register("topic-b", "references/unrelated.md")

    def test_retired_id_non_reuse(self):
        registry = StableIdRegistry({"topic-a": "references/a.md"})
        registry.retire("topic-a")
        with self.assertRaisesRegex(StableIdError, "retired-id-reuse"):
            registry.register("topic-a", "references/new-topic.md")

    # M5-T03 / M5-V02
    def test_external_version_advance_marks_source_stale(self):
        recorded = SourceObservation("tool", "2026-09-24", version="1.0.0")
        observed = SourceObservation("tool", "2026-09-25", version="1.1.0")
        self.assertEqual(source_freshness(recorded, observed), STALE)

    def test_matching_source_identity_is_fresh_and_missing_identity_is_unknown(self):
        recorded = SourceObservation("repo", "2026-09-24", commit="abc123")
        same = SourceObservation("repo", "2026-09-25", commit="abc123")
        unknown = SourceObservation("repo", "2026-09-25")
        self.assertEqual(source_freshness(recorded, same), FRESH)
        self.assertEqual(source_freshness(recorded, unknown), UNKNOWN)

    # M5-T04 / M5-V03
    def test_reconciliation_accepts_only_supported_conclusion_and_preserves_gaps(self):
        result = reconcile_claim(
            "feature-x",
            "enabled",
            [SourceClaim("source-a", "feature-x", "enabled"), SourceClaim("source-b", "feature-x", None)],
        )
        self.assertEqual(result.status, SUPPORTED)
        self.assertTrue(result.publishable)
        self.assertEqual(result.gaps, ("source-b",))

    def test_reconciliation_preserves_conflicting_source_values(self):
        result = reconcile_claim(
            "feature-x",
            "enabled",
            [SourceClaim("source-a", "feature-x", "enabled"), SourceClaim("source-b", "feature-x", "disabled")],
        )
        self.assertEqual(result.status, CONFLICT)
        self.assertFalse(result.publishable)
        self.assertEqual(result.conflicting_values, ("disabled", "enabled"))

    def test_reconciliation_rejects_unsupported_conclusion(self):
        missing = reconcile_claim("feature-x", "enabled", [])
        contradicted = reconcile_claim(
            "feature-x", "enabled", [SourceClaim("source-a", "feature-x", "disabled")]
        )
        self.assertEqual(missing.status, UNSUPPORTED)
        self.assertEqual(contradicted.status, UNSUPPORTED)
        self.assertFalse(missing.publishable)
        self.assertFalse(contradicted.publishable)

    # M5-T05 / M5-V04
    def test_canonical_change_makes_agents_projection_stale(self):
        with tempfile.TemporaryDirectory(prefix="hr-m5-projection-") as td:
            root = Path(td)
            write_page(root, "a.md", "topic-a")
            (root / "llms.txt").write_text("# Index\n- [A](references/a.md)\n", encoding="utf-8")
            context_kb.write_manifest(root)
            context_kb.write_agents_projection(root)
            self.assertTrue(context_kb.projection_fresh(root))
            with (root / "references" / "a.md").open("a", encoding="utf-8") as fh:
                fh.write("\nMaterial canonical change.\n")
            self.assertFalse(context_kb.projection_fresh(root))

    def test_projection_only_change_does_not_change_canonical_fingerprint(self):
        with tempfile.TemporaryDirectory(prefix="hr-m5-projection-") as td:
            root = Path(td)
            write_page(root, "a.md", "topic-a")
            (root / "llms.txt").write_text("# Index\n- [A](references/a.md)\n", encoding="utf-8")
            before = context_kb.canonical_fingerprint(root)
            context_kb.write_agents_projection(root)
            (root / "AGENTS.md").write_text(
                (root / "AGENTS.md").read_text(encoding="utf-8") + "\nProjection-only note.\n",
                encoding="utf-8",
            )
            after = context_kb.canonical_fingerprint(root)
            self.assertEqual(before, after)

    def test_canonical_fingerprint_is_independent_of_text_line_endings(self):
        with tempfile.TemporaryDirectory(prefix="hr-m5-line-endings-") as td:
            root = Path(td)
            page = write_page(root, "a.md", "topic-a")
            llms = root / "llms.txt"
            llms.write_text("# Index\n- [A](references/a.md)\n", encoding="utf-8")
            original = {
                path: path.read_bytes().replace(b"\r\n", b"\n")
                for path in (page, llms)
            }

            for path, body in original.items():
                path.write_bytes(body)
            lf_fingerprint = context_kb.canonical_fingerprint(root)

            for path, body in original.items():
                path.write_bytes(body.replace(b"\n", b"\r\n"))
            crlf_fingerprint = context_kb.canonical_fingerprint(root)

            self.assertEqual(lf_fingerprint, crlf_fingerprint)

    # M5-T05 / M5-V05
    def test_manifest_generation_is_deterministic_by_stable_id(self):
        with tempfile.TemporaryDirectory(prefix="hr-m5-manifest-") as td:
            root = Path(td)
            write_page(root, "z.md", "topic-z")
            write_page(root, "a.md", "topic-a")
            (root / "llms.txt").write_text("# Index\n", encoding="utf-8")
            first = context_kb.render_manifest(root)
            second = context_kb.render_manifest(root)
            self.assertEqual(first, second)
            self.assertLess(first.find(b'"topic-a"'), first.find(b'"topic-z"'))

    def test_whole_collection_audit_detects_duplicate_id_broken_link_and_stale_manifest(self):
        with tempfile.TemporaryDirectory(prefix="hr-m5-audit-") as td:
            root = Path(td)
            write_page(root, "a.md", "topic-a", body="# A\n[Missing](missing.md)\n")
            write_page(root, "b.md", "topic-a")
            (root / "llms.txt").write_text("# Index\n- [A](references/a.md)\n", encoding="utf-8")
            (root / "manifest.jsonl").write_text("{}\n", encoding="utf-8")
            context_kb.write_agents_projection(root)
            issues = context_kb.audit_collection(root)
            self.assertTrue(any(i.startswith("duplicate-id:topic-a") for i in issues))
            self.assertTrue(any(i.startswith("broken-link:") for i in issues))
            self.assertIn("manifest-stale-or-nondeterministic", issues)

    def test_actual_r85_collection_audits_clean_and_has_no_retrieval_subsystem(self):
        issues = context_kb.audit_collection(KB_ROOT)
        self.assertEqual(issues, [])
        names = {p.name.lower() for p in KB_ROOT.rglob("*")}
        self.assertTrue({"vectors", "vector-db", "embeddings", "rag-service", "semantic-index"}.isdisjoint(names))


if __name__ == "__main__":
    unittest.main()
