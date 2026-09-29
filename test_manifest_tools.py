import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "Tools"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("build_manifest", TOOLS / "build_manifest.py")
verifier = load_module("verify_manifest", TOOLS / "verify_manifest.py")


class ManifestToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "package"
        (self.root / "Documentation").mkdir(parents=True)
        (self.root / "Canon").mkdir()
        shutil.copy2(ROOT / "Documentation" / "manifest.schema.json", self.root / "Documentation" / "manifest.schema.json")
        (self.root / "Canon" / "sample.txt").write_text("canon payload\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def build(self):
        manifest, files = builder.build_manifest(self.root, None)
        errors = builder.validate_manifest(manifest, self.root / "Documentation" / "manifest.schema.json")
        self.assertEqual(errors, [])
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        checksum = builder.sha256(manifest_path)
        (self.root / "Documentation" / "manifest.sha256").write_text(f"{checksum}  manifest.json\n", encoding="utf-8")
        return files

    def test_builder_creates_file_entry(self):
        files = self.build()
        self.assertIn("Canon/sample.txt", files)
        manifest = json.loads((self.root / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["file_count"], len(manifest["files"]))

    def test_verifier_passes_valid_package(self):
        self.build()
        report = verifier.verify(self.root, strict=True)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["checks"]["manifest_checksum"], "PASS")

    def test_verifier_detects_payload_hash_mismatch(self):
        self.build()
        (self.root / "Canon" / "sample.txt").write_text("tampered\n", encoding="utf-8")
        report = verifier.verify(self.root, strict=True)
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["exit_code"], 30)  # size changes before hash comparison
        self.assertTrue(report["failed_files"])

    def test_verifier_detects_manifest_checksum_mismatch(self):
        self.build()
        manifest_path = self.root / "manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["status"]["cci"] = 95
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        report = verifier.verify(self.root, strict=True)
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["exit_code"], 32)

    def test_builder_excludes_manifest_and_checksum(self):
        self.build()
        manifest, files = builder.build_manifest(self.root, None)
        self.assertNotIn("manifest.json", files)
        self.assertNotIn("Documentation/manifest.sha256", files)


if __name__ == "__main__":
    unittest.main()
