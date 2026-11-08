"""R272: packaging CLI import contract under real isolated Python interpreters.

Tests only --help importability, not native Windows executables or release.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = (
    "products/desktop/scripts/offline_source_gate.py",
    "products/desktop/scripts/toolchain_guard.py",
    "products/desktop/scripts/build_input_guard.py",
    "products/desktop/build_inventory.py",
    "products/desktop/release_gate.py",
    "products/desktop/report_attestation.py",
)


class IsolatedPackagingEntryPointTests(unittest.TestCase):
    """Exercise all six private build helper CLIs exactly as -I child processes."""

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.work.cleanup)
        cls.untrusted = Path(cls.work.name)
        # Shadow modules in cwd and PYTHONPATH must not be imported.
        for name in ("candidate_guard", "pe_image_guard", "release_gate",
                     "report_evidence", "source_smoke_gate"):
            (cls.untrusted / (name + ".py")).write_text(
                "raise RuntimeError('R272_UNTRUSTED_IMPORT_SENTINEL')\n", encoding="ascii")

    def check_isolated(self, relpath, *, optimized):
        path = ROOT / relpath
        self.assertTrue(path.is_file(), "Missing mandatory private-build script")
        argv = [sys.executable, "-I"]
        if optimized:
            argv.append("-OO")
        argv.extend((str(path), "--help"))
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.untrusted)
        env["PYTHONNOUSERSITE"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(argv, cwd=self.untrusted, env=env,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=30, check=False)
        # Deliberately avoid displaying stderr: it can contain private paths.
        self.assertEqual(result.returncode, 0,
                         "Isolated packaging entrypoint failed before argparse")
        self.assertIn(b"--help", result.stdout)
        self.assertNotIn(b"R272_UNTRUSTED_IMPORT_SENTINEL", result.stdout)
        self.assertNotIn(b"R272_UNTRUSTED_IMPORT_SENTINEL", result.stderr)


def _make_test(relpath, optimized):
    def check(self):
        self.check_isolated(relpath, optimized=optimized)
    check.__name__ = "test_" + ("optimized" if optimized else "normal") + "_" + Path(relpath).stem
    return check


for _script in SCRIPTS:
    for _optimized in (False, True):
        _test = _make_test(_script, _optimized)
        setattr(IsolatedPackagingEntryPointTests, _test.__name__, _test)

del _script, _optimized, _test

if __name__ == "__main__":
    unittest.main()
