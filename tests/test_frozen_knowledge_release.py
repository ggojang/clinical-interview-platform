import importlib.util
import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "release" / "build_frozen_knowledge_bundle.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("frozen_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class FrozenKnowledgeReleaseTest(unittest.TestCase):
    def test_bundle_is_hash_locked_and_omits_build_time_content(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "frozen"
            manifest = builder.build(output, None, "2026-07-31T00:00:00Z")
            expected_package_count = len(list((ROOT / "packages" / "generated").glob("*.json")))
            self.assertEqual(expected_package_count, manifest["package_count"])
            self.assertFalse(manifest["contains_patient_responses"])
            self.assertEqual("disabled", manifest["knowledge_update_mode"])
            self.assertFalse((output / "knowledge").exists())
            self.assertFalse((output / "compiler").exists())
            self.assertFalse((output / "sources").exists())
            self.assertTrue((output / "knowledge-api" / "gpt" / "manifest.json").is_file())
            self.assertTrue((output / "packages" / "primary-care-headache-0.1.0.json").is_file())
            for script in (output / "app").glob("*.py"):
                ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            completed = subprocess.run(
                [sys.executable, str(output / "app" / "verify.py")],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("verification PASSED", completed.stdout)

    def test_verifier_rejects_mutation(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "frozen"
            builder.build(output, None, "2026-07-31T00:00:00Z")
            readme = output / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(output / "app" / "verify.py")],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("digest mismatch", completed.stderr)

    def test_zip_is_reproducible_across_output_directory_names(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_zip = root / "first.zip"
            second_zip = root / "second.zip"
            builder.build(root / "one", first_zip, "2026-07-31T00:00:00Z")
            builder.build(root / "another-name", second_zip, "2026-07-31T00:00:00Z")
            self.assertEqual(first_zip.read_bytes(), second_zip.read_bytes())

    def test_snapshot_summary_is_not_patient_state(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "frozen"
            builder.build(output, None, "2026-07-31T00:00:00Z")
            summary = json.loads(
                (output / "knowledge-api" / "snapshot-summary.json").read_text(encoding="utf-8")
            )
            self.assertFalse(summary["contains_patient_responses"])
            self.assertFalse(summary["external_medical_source_access"])
            self.assertFalse(summary["terminology_server_required_at_runtime"])


if __name__ == "__main__":
    unittest.main()
