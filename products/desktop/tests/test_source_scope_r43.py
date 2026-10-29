"""R43 source-only evidence: close omitted Python dependencies and unsafe directories."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "source_smoke_gate.py"
SPEC = importlib.util.spec_from_file_location("source_smoke_gate_r43", SCRIPT)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class SourceScopeR43(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r43-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.desktop = self.root / "products" / "desktop"
        self.package = self.desktop / "fvs_suite"
        self.scripts = self.desktop / "scripts"
        self.launchers = self.desktop / "launchers"
        for directory in (self.package, self.scripts, self.launchers):
            directory.mkdir(parents=True)
        self.engine = self.package / "engine.py"
        self.engine.write_text("# local engine\n", encoding="utf-8")
        for app, _ in gate.APPS:
            (self.launchers / f"{app}.py").write_text("# approved launcher\n", encoding="utf-8")

    @staticmethod
    def smoke(_: str):
        return [Path("synthetic.csv")]

    def paths(self):
        return {item["path"] for item in gate.source_inventory(self.root)}

    def assert_mid_smoke_change_blocked(self, path, *, mode="change"):
        def mutate(app):
            if app == "policy":
                if mode == "change":
                    path.write_text("# mutated\n", encoding="utf-8")
                elif mode == "delete":
                    path.unlink()
                elif mode == "create":
                    path.write_text("# injected\n", encoding="utf-8")
            return self.smoke(app)
        with self.assertRaises((RuntimeError, ValueError)):
            gate.report_data(self.root, mutate)

    def test_includes_top_level_python_helper(self):
        p = self.desktop / "report_evidence.py"
        p.write_text("# publisher\n")
        self.assertIn("products/desktop/report_evidence.py", self.paths())

    def test_includes_script_python_helper(self):
        p = self.scripts / "source_smoke_gate.py"
        p.write_text("# source gate\n")
        self.assertIn("products/desktop/scripts/source_smoke_gate.py", self.paths())

    def test_includes_nested_engine_python_module(self):
        p = self.package / "vendor" / "rules.py"
        p.parent.mkdir()
        p.write_text("# private rule\n")
        self.assertIn("products/desktop/fvs_suite/vendor/rules.py", self.paths())

    def test_nested_module_changed_during_smoke_withholds_evidence(self):
        p = self.package / "helpers" / "rules.py"
        p.parent.mkdir()
        p.write_text("# first\n")
        self.assert_mid_smoke_change_blocked(p)

    def test_nested_module_added_during_smoke_withholds_evidence(self):
        p = self.package / "rules_new.py"
        self.assert_mid_smoke_change_blocked(p, mode="create")

    def test_nested_module_deleted_during_smoke_withholds_evidence(self):
        p = self.package / "nested" / "calc.py"
        p.parent.mkdir()
        p.write_text("# calc\n")
        self.assert_mid_smoke_change_blocked(p, mode="delete")

    def test_root_helper_changed_during_smoke_withholds_evidence(self):
        p = self.desktop / "report_evidence.py"
        p.write_text("# original\n")
        self.assert_mid_smoke_change_blocked(p)

    def test_root_helper_deleted_during_smoke_withholds_evidence(self):
        p = self.desktop / "report_evidence.py"
        p.write_text("# original\n")
        self.assert_mid_smoke_change_blocked(p, mode="delete")

    def test_script_helper_changed_during_smoke_withholds_evidence(self):
        p = self.scripts / "source_smoke_gate.py"
        p.write_text("# original\n")
        self.assert_mid_smoke_change_blocked(p)

    def test_script_helper_created_during_smoke_withholds_evidence(self):
        p = self.scripts / "surprise.py"
        self.assert_mid_smoke_change_blocked(p, mode="create")

    def test_unexpected_launcher_python_is_rejected(self):
        (self.launchers / "Unauthorized.py").write_text("# unwanted\n")
        with self.assertRaisesRegex(ValueError, "unsafe|Incomplete"):
            gate.source_inventory(self.root)

    def test_extra_launcher_during_smoke_withholds_evidence(self):
        self.assert_mid_smoke_change_blocked(self.launchers / "Unauthorized.py", mode="create")

    def test_symlinked_nested_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "module"
            external.mkdir()
            (external / "injected.py").write_text("# unexpected\n")
            alias = self.package / "nested"
            try:
                alias.symlink_to(external, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaisesRegex(ValueError, "unsafe|Incomplete"):
                gate.source_inventory(self.root)

    def test_symlinked_nested_python_module_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            source = Path(outside) / "malicious.py"
            source.write_text("# injected\n")
            alias = self.package / "nested.py"
            try:
                alias.symlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaises(ValueError):
                gate.source_inventory(self.root)

    def test_symlinked_products_ancestor_is_rejected(self):
        original = self.root / "products"
        replacement = self.root / "real-products"
        original.rename(replacement)
        try:
            original.symlink_to(replacement, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(ValueError):
            gate.source_inventory(self.root)

    def test_symlinked_desktop_ancestor_is_rejected(self):
        original = self.root / "products" / "desktop"
        replacement = self.root / "products" / "real-desktop"
        original.rename(replacement)
        try:
            original.symlink_to(replacement, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(ValueError):
            gate.source_inventory(self.root)

    def test_symlinked_optional_scripts_directory_is_rejected(self):
        original = self.scripts
        replacement = self.desktop / "real-scripts"
        original.rename(replacement)
        try:
            original.symlink_to(replacement, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(ValueError):
            gate.source_inventory(self.root)

    def test_hardlinked_nested_python_file_is_rejected(self):
        directory = self.package / "deep"
        directory.mkdir()
        try:
            os.link(self.engine, directory / "alias.py")
        except (OSError, NotImplementedError):
            self.skipTest("hardlink creation unavailable")
        with self.assertRaises(ValueError):
            gate.source_inventory(self.root)

    def test_missing_optional_scripts_dir_preserves_r42_fixture_compatibility(self):
        self.scripts.rmdir()
        self.assertEqual(len(gate.source_inventory(self.root)), 7)

    def test_inventory_is_stable_sorted_and_content_bound(self):
        nested = self.package / "addons"
        nested.mkdir()
        (nested / "math.py").write_bytes(b"# money precision uses Decimal\n")
        (self.desktop / "report_evidence.py").write_bytes(b"# evidence\n")
        (self.scripts / "source_smoke_gate.py").write_bytes(b"# inventory\n")
        expected = gate.source_inventory(self.root)
        self.assertEqual(expected, gate.source_inventory(self.root))
        self.assertEqual([x["path"] for x in expected], sorted(x["path"] for x in expected))
        path = "products/desktop/fvs_suite/addons/math.py"
        self.assertEqual(next(x["sha256"] for x in expected if x["path"] == path),
                         hashlib.sha256(b"# money precision uses Decimal\n").hexdigest())
        self.assertFalse(gate.report_data(self.root, self.smoke)["qd_approved"])

    def test_same_byte_inode_swap_during_smoke_withholds_evidence(self):
        original = self.engine.read_bytes()
        def replace_during_smoke(app):
            if app == "policy":
                self.engine.unlink()
                self.engine.write_bytes(original)
            return self.smoke(app)
        with self.assertRaisesRegex(RuntimeError, "sources changed"):
            gate.report_data(self.root, replace_during_smoke)

    def test_touching_source_metadata_during_smoke_withholds_evidence(self):
        def touch_during_smoke(app):
            if app == "policy":
                info = self.engine.stat()
                os.utime(self.engine, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000_000))
            return self.smoke(app)
        with self.assertRaisesRegex(RuntimeError, "sources changed"):
            gate.report_data(self.root, touch_during_smoke)

    def test_private_metadata_not_written_to_public_source_manifest(self):
        manifest = gate.report_data(self.root, self.smoke)["source_inventory"]
        self.assertEqual(set(manifest[0]), {"path", "sha256"})

    def test_non_python_docs_and_cache_are_not_hashed(self):
        (self.scripts / "README.md").write_text("# docs\n")
        (self.package / "__pycache__").mkdir()
        (self.package / "__pycache__" / "engine.cpython-313.pyc").write_bytes(b"cache")
        paths = self.paths()
        self.assertEqual(len(paths), 7)
        self.assertTrue(all(p.endswith(".py") for p in paths))

    def test_python_module_count_is_bounded_across_helper_directories(self):
        for i in range(gate.MAX_SOURCE_FILES):
            (self.scripts / f"helper_{i:04d}.py").write_bytes(b"# utility\n")
        with self.assertRaises(ValueError):
            gate.source_inventory(self.root)

    def test_python_paths_remain_relative_for_unicode_subpackage(self):
        deep = self.package / "café"
        deep.mkdir()
        (deep / "règles.py").write_bytes(b"# deterministic rules\n")
        self.assertIn("products/desktop/fvs_suite/café/règles.py", self.paths())


if __name__ == "__main__":
    unittest.main()
