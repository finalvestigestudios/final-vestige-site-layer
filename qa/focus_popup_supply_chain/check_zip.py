"""Offline, fail-closed identity check for the *reviewed* FV Focus Popup ZIP.

Never installs, unpacks to disk, executes PHP, or accesses WordPress.
A passing ZIP check does NOT prove those bytes are installed or that signup works.
"""
import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path

ROOT = "fv-focus-popup/"
PINS = {
    "fv-focus-popup.php": "19ca40e54cd3aae9e434a34f6f83f2dcb28039d6",
    "focus-popup.html": "81bb038297e53ce92f7b75bf9f348d71c06af5c5",
    "focus-popup.css": "ce8b5a9a6e3352281d8a1b6bd45b4b02dd655500",
    "focus-popup.js": "5fdd7bebbca75d3cf6b167f8d4070f6364c675e2",
}
VERSION = "0.1.1"
MAX_ARCHIVE = 10 * 1024 * 1024
MAX_UNCOMPRESSED = 256 * 1024
MAX_FILE = 128 * 1024


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def inspect(path, pins=PINS, version=VERSION):
    """Return deterministic findings; empty means archive equals pinned source only."""
    path = Path(path)
    issues = []
    if not path.is_file() or path.stat().st_size > MAX_ARCHIVE:
        return ["missing_or_oversize_archive"]
    try:
        with zipfile.ZipFile(path) as archive:
            records = archive.infolist()
            names = [x.filename for x in records]
            if len(names) != len(set(names)):
                issues.append("duplicate_entry")
            wanted = {ROOT + name for name in pins}
            actual = {name for name in names if name != ROOT}
            if actual != wanted:
                issues.append("unexpected_or_missing_file")
            if sum(x.file_size for x in records) > MAX_UNCOMPRESSED:
                issues.append("uncompressed_limit_exceeded")
            if any(x.file_size > MAX_FILE for x in records):
                issues.append("file_limit_exceeded")
            for entry in records:
                name = entry.filename
                mode = (entry.external_attr >> 16) & 0xffff
                if (name != ROOT and name not in wanted) or "\\" in name or name.startswith("/") or ".." in name.split("/"):
                    issues.append("unsafe_path_or_extra_file")
                if stat.S_IFMT(mode) == stat.S_IFLNK:
                    issues.append("symlink_forbidden")
                if entry.flag_bits & 1:
                    issues.append("encrypted_entry")
                if entry.file_size and entry.file_size > 200 * max(entry.compress_size, 1):
                    issues.append("excessive_compression_ratio")
            if issues:
                return sorted(set(issues))
            for name, expected in pins.items():
                data = archive.read(ROOT + name)
                if git_blob(data) != expected:
                    issues.append("blob_mismatch:" + name)
                if name == "fv-focus-popup.php":
                    match = re.search(rb"(?m)^\s*\*\s*Version:\s*([^\r\n]+)", data)
                    if not match or match.group(1).strip().decode("ascii", "replace") != version:
                        issues.append("plugin_version_mismatch")
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        return ["unreadable_archive:" + type(exc).__name__]
    return sorted(set(issues))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", help="Original review or independently exported installed plugin ZIP")
    args = parser.parse_args()
    findings = inspect(args.zip)
    print(json.dumps({"archive": Path(args.zip).name, "source_identity": "MATCH" if not findings else "HOLD", "findings": findings,
                      "production_verified": False, "newsletter_verified": False}, indent=2))
    return 0 if not findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
