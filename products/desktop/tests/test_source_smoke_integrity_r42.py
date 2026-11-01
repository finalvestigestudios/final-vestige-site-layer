"""R42: source-only evidence must correspond to the exact six-engine smoke run."""
from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "source_smoke_gate.py"
SPEC = importlib.util.spec_from_file_location("source_smoke_gate_r42", SCRIPT)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
from synthetic_windows_fs_r104 import changed_stat


class SourceSmokeIntegrityR42(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fvs-r42-source-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.package = self.root / "products/desktop/fvs_suite"
        self.launchers = self.root / "products/desktop/launchers"
        self.package.mkdir(parents=True)
        self.launchers.mkdir()
        (self.package / "engine.py").write_bytes(b"# deterministic synthetic engine\n")
        (self.package / "smoke.py").write_bytes(b"# synthetic smoke\n")
        for name, _ in gate.APPS:
            (self.launchers / (name + ".py")).write_bytes(b"# synthetic launcher\n")

    def smoke(self, app):
        return [Path("synthetic.csv")]

    def test_exact_six_app_identifiers_and_premium_names(self):
        self.assertEqual(len(gate.APPS), 6)
        self.assertEqual(len({name for name, _ in gate.APPS}), 6)
        self.assertEqual([p for p, _ in gate.APPS][-2:],
                         ["GrantAuditStudioPro", "ProcureGuardStudioPro"])

    def test_exact_stable_sorted_inventory(self):
        before = gate.source_inventory(self.root)
        self.assertEqual(before, gate.source_inventory(self.root))
        self.assertEqual(len(before), 8)
        self.assertEqual([entry["path"] for entry in before],
                         sorted(entry["path"] for entry in before))
        self.assertTrue(all(len(entry["sha256"]) == 64 for entry in before))

    def test_success_is_explicitly_source_only(self):
        called = []
        def smoke(app):
            called.append(app)
            return [Path("ok.csv")]
        evidence = gate.report_data(self.root, smoke, commit="012345")
        self.assertEqual(called, [app for _, app in gate.APPS])
        self.assertEqual(len(evidence["application_results"]), 6)
        self.assertFalse(evidence["released"])
        self.assertFalse(evidence["qd_approved"])
        self.assertTrue(evidence["all_six_passed"])
        self.assertIn("NOT_WINDOWS_BINARY", evidence["scope"])
        self.assertEqual(evidence["commit"], "012345")

    def test_mutating_engine_during_first_smoke_withholds_evidence(self):
        def smoke(app):
            if app == "ledger":
                (self.package / "engine.py").write_text("# changed\n")
            return [Path("ok.csv")]
        with self.assertRaisesRegex(RuntimeError, "sources changed"):
            gate.report_data(self.root, smoke)

    def test_mutating_launcher_during_last_smoke_withholds_evidence(self):
        def smoke(app):
            if app == "procurement":
                (self.launchers / "GrantAuditStudioPro.py").write_text("# changed\n")
            return [Path("ok.csv")]
        with self.assertRaisesRegex(RuntimeError, "sources changed"):
            gate.report_data(self.root, smoke)

    def test_added_engine_during_smoke_withholds_evidence(self):
        def smoke(app):
            if app == "policy":
                (self.package / "new_engine.py").write_text("# added\n")
            return [Path("ok.csv")]
        with self.assertRaisesRegex(RuntimeError, "sources changed"):
            gate.report_data(self.root, smoke)

    def test_removed_engine_during_smoke_withholds_evidence(self):
        def smoke(app):
            if app == "invoices":
                (self.package / "engine.py").unlink()
            return [Path("ok.csv")]
        with self.assertRaises((ValueError, RuntimeError)):
            gate.report_data(self.root, smoke)

    def test_removed_launcher_during_smoke_withholds_evidence(self):
        def smoke(app):
            if app == "spend":
                (self.launchers / "LedgerDiffLite.py").unlink()
            return [Path("ok.csv")]
        with self.assertRaises((ValueError, RuntimeError)):
            gate.report_data(self.root, smoke)

    def test_missing_launcher_fails_before_any_smoke(self):
        (self.launchers / "PolicyDeltaDesk.py").unlink()
        called = []
        with self.assertRaises(ValueError):
            gate.report_data(self.root, lambda app: called.append(app) or [Path("ok.csv")])
        self.assertEqual(called, [])

    def test_source_symlink_is_rejected(self):
        item = self.package / "smoke.py"
        item.unlink()
        try:
            item.symlink_to(self.package / "engine.py")
        except (OSError, NotImplementedError):
            self.skipTest("OS disallows symlinks")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            gate.source_inventory(self.root)

    def test_hardlink_alias_is_rejected(self):
        item = self.package / "smoke.py"
        item.unlink()
        try:
            os.link(self.package / "engine.py", item)
        except (OSError, NotImplementedError):
            self.skipTest("OS disallows hardlinks")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            gate.source_inventory(self.root)

    def test_symlinked_engine_directory_is_rejected(self):
        alias = self.root / "real-package"
        self.package.rename(alias)
        try:
            self.package.symlink_to(alias, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("OS disallows symlinks")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            gate.source_inventory(self.root)

    def test_bounded_source_rejects_sparse_oversized_file(self):
        with (self.package / "engine.py").open("wb") as stream:
            stream.truncate(gate.MAX_SOURCE_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "oversized"):
            gate.source_inventory(self.root)

    def test_too_many_modules_fails_closed(self):
        for i in range(gate.MAX_SOURCE_FILES):
            (self.package / f"generated_{i:04d}.py").write_bytes(b"x")
        with self.assertRaisesRegex(ValueError, "Incomplete or unsafe"):
            gate.source_inventory(self.root)

    def test_file_replaced_after_lstat_before_open_is_rejected(self):
        if os.name == "nt":
            # Native Windows may refuse unlink for files held elsewhere.
            # Simulate a new descriptor inode after path lstat, validating
            # the real fail-closed identity gate without an OS-dependent race.
            item = self.package / "engine.py"
            real_open, real_fstat = gate.os.open, gate.os.fstat
            target = {"fd": None}
            def observe_open(path, flags, *args, **kwargs):
                fd = real_open(path, flags, *args, **kwargs)
                if Path(path) == item:
                    target["fd"] = fd
                return fd
            def observe_fstat(fd):
                info = real_fstat(fd)
                return changed_stat(info) if target["fd"] == fd else info
            with patch.object(gate.os, "open", side_effect=observe_open):
                with patch.object(gate.os, "fstat", side_effect=observe_fstat):
                    with self.assertRaisesRegex(ValueError, "changed"):
                        gate.source_inventory(self.root)
            self.assertEqual(item.read_bytes(), b"# deterministic synthetic engine\n")
            return
        # POSIX tests an actual unlink/recreate race before opening.

        item = self.package / "engine.py"
        original_open = gate.os.open
        def replace_then_open(path, flags, *args, **kwargs):
            if Path(path) == item:
                item.unlink()
                item.write_bytes(b"# swapped before descriptor\n")
            return original_open(path, flags, *args, **kwargs)
        with patch.object(gate.os, "open", side_effect=replace_then_open):
            with self.assertRaisesRegex(ValueError, "changed"):
                gate.source_inventory(self.root)

    def test_file_mutated_while_reading_is_rejected(self):
        if os.name == "nt":
            # Windows can deny writes while the source descriptor is open.
            # Exercise unchanged production before/after descriptor custody
            # by changing the reported mtime after the first actual read.
            item = self.package / "engine.py"
            real_open = gate.os.open
            real_read = gate.os.read
            real_fstat = gate.os.fstat
            target = {"fd": None, "changed": False}
            def observe_open(path, flags, *args, **kwargs):
                fd = real_open(path, flags, *args, **kwargs)
                if Path(path) == item:
                    target["fd"] = fd
                return fd
            def observe_read(fd, size):
                data = real_read(fd, size)
                if fd == target["fd"]:
                    target["changed"] = True
                return data
            def observe_fstat(fd):
                info = real_fstat(fd)
                if fd == target["fd"] and target["changed"]:
                    return changed_stat(info, "st_mtime_ns")
                return info
            with patch.object(gate.os, "open", side_effect=observe_open):
                with patch.object(gate.os, "read", side_effect=observe_read):
                    with patch.object(gate.os, "fstat", side_effect=observe_fstat):
                        with self.assertRaisesRegex(ValueError, "changed"):
                            gate.source_inventory(self.root)
            self.assertEqual(item.read_bytes(), b"# deterministic synthetic engine\n")
            return
        # POSIX mutates the real file after the first descriptor read.

        item = self.package / "engine.py"
        original_read = gate.os.read
        mutated = False
        def mutate_after_read(fd, size):
            nonlocal mutated
            data = original_read(fd, size)
            if not mutated:
                mutated = True
                item.write_bytes(b"# modified while hashing\n")
            return data
        with patch.object(gate.os, "read", side_effect=mutate_after_read):
            with self.assertRaisesRegex(ValueError, "changed"):
                gate.source_inventory(self.root)

    def test_source_smoke_failure_stops_other_engines(self):
        calls = []
        def fail_second(app):
            calls.append(app)
            if app == "invoices":
                raise RuntimeError("synthetic failure")
            return [Path("ok.csv")]
        with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
            gate.report_data(self.root, fail_second)
        self.assertEqual(calls, ["ledger", "invoices"])

    def test_source_smoke_refuses_empty_result(self):
        with self.assertRaisesRegex(RuntimeError, "no source-smoke outputs"):
            gate.report_data(self.root, lambda app: [] if app == "policy" else [Path("ok.csv")])

    def test_source_smoke_refuses_absolute_and_nested_paths(self):
        for outputs in ([Path("/secrets/report.csv")], [Path("subdir/a.csv")]):
            with self.subTest(outputs=outputs):
                with self.assertRaisesRegex(RuntimeError, "unsafe"):
                    gate.verify_smokes(lambda app: outputs)

    def test_publisher_exclusively_commits_complete_json_outside_checkout(self):
        with tempfile.TemporaryDirectory() as outside:
            dest = Path(outside) / "source-only.json"
            prepared = gate.prepare_report_path(dest, self.root)
            gate.publish_report(prepared, gate.report_data(self.root, self.smoke))
            data = dest.read_text(encoding="utf-8")
            self.assertIn('"all_six_passed": true', data)
            self.assertTrue(data.endswith("\n"))
            self.assertEqual(len(list(Path(outside).iterdir())), 1)
            with self.assertRaises(Exception):
                gate.publish_report(prepared, {"released": True})
            self.assertEqual(dest.read_text(encoding="utf-8"), data)

    def test_publisher_refuses_destination_inside_source_tree(self):
        with self.assertRaisesRegex(Exception, "outside"):
            gate.prepare_report_path(self.root / "products/desktop/fvs_suite/a.json", self.root)

    def test_publisher_rejects_existing_file_before_smoke(self):
        with tempfile.TemporaryDirectory() as outside:
            dest = Path(outside) / "exists.json"
            dest.write_text("previous immutable evidence")
            with self.assertRaisesRegex(Exception, "already exists"):
                gate.prepare_report_path(dest, self.root)
            self.assertEqual(dest.read_text(), "previous immutable evidence")


if __name__ == "__main__":
    unittest.main()
