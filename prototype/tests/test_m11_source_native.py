from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IMPORT_CHECK = ROOT / "verification" / "m11-verify-import-only.py"
BUNDLE_CHECK = ROOT / "verification" / "m11-history-input-preflight.py"


def run(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


class M11SourceNativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="hr-m11-native-")
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def init_repo(self, path: Path, name: str) -> None:
        path.mkdir()
        run(path, "init", "-b", "main")
        run(path, "config", "user.name", name)
        run(path, "config", "user.email", f"{name}@example.invalid")

    def make_spec(self, source_commit: str) -> Path:
        spec_path = self.root / "spec.json"
        spec_path.write_text(
            json.dumps(
                {
                    "sources": [
                        {
                            "id": "aiboarding",
                            "repository": "https://example.invalid/aiboarding.git",
                            "source_commit": source_commit,
                            "target_prefix": "legacy/aiboarding",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return spec_path

    def make_import_commit(self, extra_path: bool = False, extra_module: bool = False) -> tuple[Path, str, str]:
        source = self.root / "source"
        self.init_repo(source, "source")
        (source / "source.txt").write_text("source\n", encoding="utf-8")
        run(source, "add", "source.txt")
        run(source, "commit", "-m", "source")
        source_commit = run(source, "rev-parse", "HEAD")

        repo = self.root / "target"
        self.init_repo(repo, "target")
        (repo / "README.md").write_text("target\n", encoding="utf-8")
        run(repo, "add", "README.md")
        run(repo, "commit", "-m", "base")
        modules = (
            '[submodule "aiboarding"]\n'
            "\tpath = legacy/aiboarding\n"
            "\turl = https://example.invalid/aiboarding.git\n",
        )[0]
        if extra_module:
            modules += (
                '[submodule "unapproved"]\n'
                "\tpath = legacy/unapproved\n"
                "\turl = https://example.invalid/unapproved.git\n"
            )
        (repo / ".gitmodules").write_text(modules, encoding="utf-8")
        run(repo, "add", ".gitmodules")
        run(
            repo,
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{source_commit},legacy/aiboarding",
        )
        if extra_path:
            (repo / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
            run(repo, "add", "unexpected.txt")
        run(repo, "commit", "-m", "import source gitlink")
        return repo, run(repo, "rev-parse", "HEAD"), source_commit

    def verify_import(self, repo: Path, commit: str, spec: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(IMPORT_CHECK),
                "--repo",
                str(repo),
                "--commit",
                commit,
                "--spec",
                str(spec),
                "--json",
            ],
            text=True,
            capture_output=True,
        )

    def test_import_only_accepts_exact_source_gitlink(self) -> None:
        repo, commit, source_commit = self.make_import_commit()
        result = self.verify_import(repo, commit, self.make_spec(source_commit))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"], "PASS")

    def test_import_only_rejects_unrelated_path(self) -> None:
        repo, commit, source_commit = self.make_import_commit(extra_path=True)
        result = self.verify_import(repo, commit, self.make_spec(source_commit))
        self.assertEqual(result.returncode, 1)
        self.assertIn("changed-path-set", result.stdout)

    def test_import_only_rejects_wrong_gitlink_sha(self) -> None:
        repo, commit, source_commit = self.make_import_commit()
        wrong_source = self.root / "wrong-source"
        self.init_repo(wrong_source, "wrong")
        (wrong_source / "source.txt").write_text("different\n", encoding="utf-8")
        run(wrong_source, "add", "source.txt")
        run(wrong_source, "commit", "-m", "wrong")
        result = self.verify_import(repo, commit, self.make_spec(run(wrong_source, "rev-parse", "HEAD")))
        self.assertEqual(result.returncode, 1)
        self.assertIn("gitlink-mismatch", result.stdout)
        self.assertNotEqual(source_commit, run(wrong_source, "rev-parse", "HEAD"))

    def test_import_only_rejects_unapproved_gitmodules_entry(self) -> None:
        repo, commit, source_commit = self.make_import_commit(extra_module=True)
        result = self.verify_import(repo, commit, self.make_spec(source_commit))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unapproved-gitmodules-entry", result.stdout)

    def test_import_only_accepts_all_three_exact_pins_in_one_commit(self) -> None:
        repos = self.root / "sources"
        repos.mkdir()
        sources = []
        modules = []
        for source_id, prefix in (
            ("aiboarding", "legacy/aiboarding"),
            ("tacticswitch", "legacy/tacticswitch"),
            ("skill-kit", "legacy/skill-kit"),
        ):
            source = repos / source_id
            self.init_repo(source, source_id)
            (source / "source.txt").write_text(source_id + "\n", encoding="utf-8")
            run(source, "add", "source.txt")
            run(source, "commit", "-m", "source")
            source_commit = run(source, "rev-parse", "HEAD")
            sources.append(
                {
                    "id": source_id,
                    "repository": f"https://example.invalid/{source_id}.git",
                    "source_commit": source_commit,
                    "target_prefix": prefix,
                }
            )
            modules.append(
                f'[submodule "{source_id}"]\n'
                f"\tpath = {prefix}\n"
                f"\turl = https://example.invalid/{source_id}.git\n"
            )

        repo = self.root / "aggregate-target"
        self.init_repo(repo, "aggregate")
        (repo / "README.md").write_text("target\n", encoding="utf-8")
        run(repo, "add", "README.md")
        run(repo, "commit", "-m", "base")
        (repo / ".gitmodules").write_text("\n".join(modules), encoding="utf-8")
        run(repo, "add", ".gitmodules")
        for source in sources:
            run(
                repo,
                "update-index",
                "--add",
                "--cacheinfo",
                f"160000,{source['source_commit']},{source['target_prefix']}",
            )
        run(repo, "commit", "-m", "import source gitlinks")
        spec = self.root / "aggregate-spec.json"
        spec.write_text(json.dumps({"sources": sources}), encoding="utf-8")
        result = self.verify_import(repo, run(repo, "rev-parse", "HEAD"), spec)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"], "PASS")

    def test_bundle_preflight_checks_digest_and_complete_ref_list(self) -> None:
        source = self.root / "bundle-source"
        self.init_repo(source, "bundle")
        (source / "source.txt").write_text("bundle\n", encoding="utf-8")
        run(source, "add", "source.txt")
        run(source, "commit", "-m", "bundle")
        source_commit = run(source, "rev-parse", "HEAD")
        bundle_dir = self.root / "bundles"
        bundle_dir.mkdir()
        bundle = bundle_dir / "aiboarding.bundle"
        run(source, "bundle", "create", str(bundle), "--all")
        refs = [
            {"oid": line.split(None, 1)[0], "ref": line.split(None, 1)[1]}
            for line in run(source, "bundle", "list-heads", str(bundle)).splitlines()
        ]
        spec = {
            "bundle_directory": "bundles",
            "sources": [
                {
                    "id": "aiboarding",
                    "bundle": bundle.name,
                    "source_ref": "refs/heads/main",
                    "source_commit": source_commit,
                    "required_paths": [],
                }
            ],
        }
        spec_path = self.root / "spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "sources": [
                        {
                            "id": "aiboarding",
                            "sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
                            "refs": refs,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                str(BUNDLE_CHECK),
                "--dir",
                str(bundle_dir),
                "--spec",
                str(spec_path),
                "--expected-manifest",
                str(manifest_path),
                "--json",
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["sources"][0]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(BUNDLE_CHECK),
                "--dir",
                str(bundle_dir),
                "--spec",
                str(spec_path),
                "--expected-manifest",
                str(manifest_path),
                "--json",
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("bundle-digest-mismatch", result.stdout)


if __name__ == "__main__":
    unittest.main()
