"""R245: bounded >256-module source provenance without relaxing safety gates."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import offline_source_gate as offline
import source_smoke_gate as smoke
import unittest_provenance as provenance


class LargeSuiteCapacityR245(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r245-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.desktop = self.root / "products" / "desktop"
        self.tests = self.desktop / "tests"
        self.package = self.desktop / "fvs_suite"
        self.scripts = self.desktop / "scripts"
        self.launchers = self.desktop / "launchers"
        for directory in (self.tests, self.package, self.scripts, self.launchers):
            directory.mkdir(parents=True)
        (self.package / "engine.py").write_text("# synthetic engine\n", encoding="utf-8")
        for name, _app in smoke.APPS:
            (self.launchers / f"{name}.py").write_text("# fixture launcher\n", encoding="utf-8")

    def make_test_modules(self, count):
        for i in range(count):
            (self.tests / f"test_capacity_{i:04d}.py").write_text(
                "import unittest\nclass Check(unittest.TestCase):\n"
                " def test_pass(self): self.assertTrue(True)\n", encoding="utf-8")

    def summary(self, count):
        return {"schema": "fvs-unittest-provenance-v2", "test_count": count,
                "module_count": count, "skipped_count": 0,
                "test_ids_sha256": "a" * 64, "active_ids_sha256": "a" * 64,
                "skipped_ids_sha256": "0" * 64}

    def test_limits_are_coordinated_and_still_bounded(self):
        self.assertEqual(offline.MAX_TEST_FILES, 512)
        self.assertEqual(provenance.MAX_TEST_MODULES, 512)
        self.assertEqual(smoke.MAX_SOURCE_FILES, 512)
        self.assertLessEqual(provenance.MAX_TEST_CASES, 20000)

    def test_281_real_unittest_modules_have_complete_provenance(self):
        self.make_test_modules(281)
        data = provenance.run(self.root)
        self.assertEqual((data["module_count"], data["test_count"], data["skipped_count"]),
                         (281, 281, 0))
        self.assertEqual(len(data["test_ids_sha256"]), 64)
        self.assertEqual(offline._validated_suite_summary(data), data)
        self.assertNotIn(str(self.root), str(data))

    def test_513_real_unittest_modules_fail_before_discovery(self):
        self.make_test_modules(513)
        with self.assertRaisesRegex(ValueError, "Invalid desktop test module inventory"):
            provenance.run(self.root)

    def test_test_inventory_includes_helpers_above_old_limit(self):
        self.make_test_modules(281)
        (self.tests / "__init__.py").write_text("# helper\n", encoding="utf-8")
        (self.tests / "fixtures.py").write_text("# fixture\n", encoding="utf-8")
        items = offline._test_inventory(self.root)
        self.assertEqual(len(items), 283)
        self.assertEqual(len({item["path"] for item in items}), 283)
        self.assertTrue(all(len(item["sha256"]) == 64 for item in items))

    def test_test_inventory_exact_512_then_513_rejected(self):
        self.make_test_modules(281)
        for i in range(231):
            (self.tests / f"helper_{i:04d}.py").write_text("# synthetic helper\n")
        self.assertEqual(len(offline._test_inventory(self.root)), 512)
        (self.tests / "overflow.py").write_text("# extra\n")
        with self.assertRaisesRegex(ValueError, "Incomplete|unsafe"):
            offline._test_inventory(self.root)

    def test_summary_512_allowed_and_513_or_forged_count_denied(self):
        self.assertEqual(offline._validated_suite_summary(self.summary(281))["module_count"], 281)
        self.assertEqual(offline._validated_suite_summary(self.summary(512))["module_count"], 512)
        with self.assertRaisesRegex(RuntimeError, "counts invalid"):
            offline._validated_suite_summary(self.summary(513))
        forged = self.summary(281)
        forged["module_count"] = True
        with self.assertRaisesRegex(RuntimeError, "counts invalid"):
            offline._validated_suite_summary(forged)

    def test_source_traversal_exact_512_then_513_rejected(self):
        for i in range(512):
            (self.scripts / f"script_{i:04d}.py").write_text("# bounded\n")
        self.assertEqual(len(smoke._package_python_sources(self.scripts)), 512)
        (self.scripts / "extra.py").write_text("# over\n")
        with self.assertRaisesRegex(ValueError, "Incomplete or unsafe"):
            smoke._package_python_sources(self.scripts)

    def test_source_inventory_selected_exact_512_then_513_rejected(self):
        for i in range(505):
            (self.scripts / f"script_{i:04d}.py").write_text("# bounded\n")
        paths = [entry["path"] for entry in smoke.source_inventory(self.root)]
        self.assertEqual(len(paths), 512)  # 505 scripts + 6 launchers + engine
        self.assertEqual(paths, sorted(paths))
        self.assertIn("products/desktop/launchers/ProcureGuardStudioPro.py", paths)
        (self.scripts / "extra.py").write_text("# over\n")
        with self.assertRaisesRegex(ValueError, "Incomplete or unsafe"):
            smoke.source_inventory(self.root)

    def test_large_source_inventory_rejects_mid_smoke_mutation(self):
        for i in range(270):
            (self.scripts / f"script_{i:04d}.py").write_text("# original\n")
        victim = self.scripts / "script_0001.py"
        def mutate(app):
            if app == "policy":
                victim.write_text("# tampered\n")
            return [Path("synthetic.csv")]
        with self.assertRaisesRegex(RuntimeError, "changed"):
            smoke.report_data(self.root, mutate)

    def test_symlink_still_rejected_above_256(self):
        for i in range(270):
            (self.scripts / f"script_{i:04d}.py").write_text("# original\n")
        alias = self.scripts / "link.py"
        try:
            alias.symlink_to(self.scripts / "script_0001.py")
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaisesRegex(ValueError, "Incomplete or unsafe"):
            smoke._package_python_sources(self.scripts)


if __name__ == "__main__":
    unittest.main()
