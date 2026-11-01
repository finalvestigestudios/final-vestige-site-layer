"""R104 synthetic-only Windows toolchain custody phase probe — NEVER a release gate.

Reproduce good synthetic R56 fixture outside checkout, isolate which stage
blocks Windows without revealing private paths, exception messages or file
contents. No accounts, network, binaries, licenses or distribution actions.
"""
from __future__ import annotations

import contextlib
from importlib import metadata
import io
import os
from pathlib import Path
import tempfile

from scripts import toolchain_guard as gate
from report_evidence import prepare_report_path, publish_report


PREFIX = "FVS_R104_TOOLCHAIN:"
PHASES = ("runtime_file",
          "runtime_dev", "runtime_ino", "runtime_mode", "runtime_nlink",
          "runtime_size", "runtime_mtime_ns", "runtime_ctime_ns",
          "distribution_file", "distribution_inventory", "snapshot",
          "evidence_preflight", "evidence_atomic_publish", "capture", "verify")


class SyntheticDistribution:
    def __init__(self, home: Path, name: str):
        self.home = home
        self.version = "1.0.0"
        self.files = [Path(name) / "__init__.py",
                      Path(name + "-1.0.dist-info") / "METADATA"]
        for member in self.files:
            file = home / member
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("# synthetic test fixture\n", encoding="utf-8")

    def locate_file(self, member):
        return self.home / member


def diagnose():
    """Return code-owned static PASS/BLOCKED statuses; never return exceptions."""
    statuses = {}
    def phase(label, operation):
        try:
            # Both the probed library and the Windows runner may emit data.
            # Suppress both Python-level streams before any phase execution.
            with open(os.devnull, "w", encoding="utf-8") as sink:
                with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                    operation()
            statuses[label] = "PASS"
        except Exception:
            # Don't reveal path, exception, fixture text or unexpected details.
            statuses[label] = "BLOCKED"

    with tempfile.TemporaryDirectory(prefix="fvs-r104-toolchain-") as temp:
        home = Path(temp)
        root = home / "checkout"
        root.mkdir()
        installed = home / "site-packages"
        installed.mkdir()
        runtime = home / "python.exe"
        runtime.write_bytes(b"synthetic interpreter; not a valid executable")
        deps = {name: SyntheticDistribution(installed, name)
                for name in ("pyinstaller", "crypto", "hooks")}
        def lookup(name):
            if name not in deps:
                raise metadata.PackageNotFoundError(name)
            return deps[name]

        def snapshot():
            return gate.snapshot(root, lookup=lookup, runtime=runtime)

        # Match the test module's required/optional dependency inventory,
        # without changing any installed toolchain or global module state.
        required, optional = gate.REQUIRED, gate.OPTIONAL
        gate.REQUIRED = ("pyinstaller", "crypto")
        gate.OPTIONAL = ("hooks", "gone")
        try:
            manifest = home / "toolchain-custody.json"
            evidence = home / "standalone-evidence.json"
            phase("runtime_file", lambda: gate._file_record(runtime))
            # Only synthetic pathname-vs-descriptor stat *field agreement*
            # is exposed. Never emit raw metadata, paths or exceptions.
            fd = None
            try:
                path_stat = runtime.lstat()
                fd = os.open(runtime, os.O_RDONLY | getattr(os, "O_BINARY", 0))
                descriptor_stat = os.fstat(fd)
                for name in ("dev", "ino", "mode", "nlink", "size",
                             "mtime_ns", "ctime_ns"):
                    attribute = "st_" + name
                    statuses["runtime_" + name] = (
                        "PASS" if getattr(path_stat, attribute)
                        == getattr(descriptor_stat, attribute) else "BLOCKED")
            except Exception:
                for name in ("dev", "ino", "mode", "nlink", "size",
                             "mtime_ns", "ctime_ns"):
                    statuses["runtime_" + name] = "BLOCKED"
            finally:
                if fd is not None:
                    os.close(fd)
            phase("distribution_file",
                  lambda: gate._file_record(installed / "crypto" / "__init__.py"))
            phase("distribution_inventory",
                  lambda: gate._distribution_record("crypto", root.resolve(), lookup))
            phase("snapshot", snapshot)
            phase("evidence_preflight", lambda: prepare_report_path(evidence, root))
            phase("evidence_atomic_publish",
                  lambda: publish_report(evidence, {"released": False, "synthetic": True}))
            phase("capture",
                  lambda: gate.capture(root, manifest, lookup=lookup, runtime=runtime))
            phase("verify", lambda: gate.check(root, manifest, lookup=lookup, runtime=runtime))
        finally:
            gate.REQUIRED, gate.OPTIONAL = required, optional

    return statuses


def main() -> int:
    try:
        result = diagnose()
    except Exception:
        result = {key: "BLOCKED" for key in PHASES}
    for name in PHASES:
        print(PREFIX + name + "=" + result.get(name, "BLOCKED"))
    print("FVS_R104_RELEASE=HOLD_READ_ONLY_SOURCE_DIAGNOSTIC")
    # A blocked stage is evidence for triage, not permission to skip R57.
    # The separate mandatory CI gate still exits nonzero on test failures.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
