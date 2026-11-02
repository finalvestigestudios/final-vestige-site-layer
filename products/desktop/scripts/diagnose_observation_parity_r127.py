"""R127 ephemeral synthetic Windows descriptor/stat parity probe; no user paths.

Only compares metadata and returns boolean outputs. Never reads real evidence,
financial data, executables, client paths, environment names or notes.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        note = root / "synthetic-note.txt"
        note.write_bytes(b"synthetic human observation " * 7)
        before = note.lstat()
        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) |
                 getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(os.open(note, flags), "rb") as source:
            opened = os.fstat(source.fileno())
            raw = source.read(16385)
            completed = os.fstat(source.fileno())
        after = note.lstat()
        attrs = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        print("R127 SYNTHETIC descriptors: " + " ".join(
            name.removeprefix("st_") + "=" +
            ("same" if len({getattr(v, name) for v in
                            (before, opened, completed, after)}) == 1 else "different")
            for name in attrs))
        print("R127 SYNTHETIC body-sized=" + str(len(raw) == before.st_size) +
              " single-linked=" + str(all(v.st_nlink == 1 for v in
                                            (before, opened, completed, after))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
