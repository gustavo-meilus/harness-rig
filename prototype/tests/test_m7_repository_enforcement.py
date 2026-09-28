from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RepositoryWorkflowTests(unittest.TestCase):
    def test_required_job_uses_native_results_for_every_event(self):
        workflow = (ROOT / ".github/workflows/ci-required.yml").read_text(encoding="utf-8")
        for event in ("pull_request:", "push:", "workflow_dispatch:", "merge_group:"):
            self.assertIn(event, workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertIn("needs: [ordinary, kb_integrity]", workflow)
        self.assertIn("if: ${{ always() }}", workflow)
        self.assertIn("needs.ordinary.result", workflow)
        self.assertIn("needs.kb_integrity.result", workflow)
        self.assertEqual(workflow.count('test "$ORDINARY_RESULT" = success'), 1)
        self.assertEqual(workflow.count('test "$KB_RESULT" = success'), 1)
        self.assertNotIn("ci_obligations", workflow)
        self.assertNotIn("secrets.", workflow)

    def test_actions_use_full_commit_ids(self):
        for path in (ROOT / ".github/workflows").glob("*.yml"):
            workflow = path.read_text(encoding="utf-8")
            for action, revision in re.findall(r"\buses:\s+([\w./-]+)@([^\s#]+)", workflow):
                with self.subTest(path=path.name, action=action):
                    self.assertRegex(revision, r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
