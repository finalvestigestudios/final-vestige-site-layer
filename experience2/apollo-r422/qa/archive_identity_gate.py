#!/usr/bin/env python3
"""Compare actual local QA archive source bytes to pinned GitHub HEAD blob identities.

Exit 0 means artifact/HEAD identity only; exit 2 on any missing/mismatched/
added source. Never equate identity with staging accessibility, sales, or release.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, BadZipFile

ROOT = Path(__file__).resolve().parent


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def inspect(archive: Path, expected: dict) -> dict:
    """Inspect source entries only; QA/ log/screenshot entries are evidence, not code."""
    mismatches = []
    seen = set()
    with ZipFile(archive) as z:
        for member in z.infolist():
            path = member.filename
            if member.is_dir():
                continue
            if path.startswith("QA/"):
                continue
            if path in seen:
                mismatches.append({"path": path, "status": "DUPLICATE_ENTRY"})
                continue
            seen.add(path)
            if path.startswith("/") or ".." in Path(path).parts or "\\" in path:
                mismatches.append({"path": path, "status": "UNSAFE_PATH"})
                continue
            if path not in expected:
                mismatches.append({"path": path, "status": "UNREVIEWED_SOURCE"})
                continue
            observed = git_blob(z.read(member))
            if observed != expected[path]:
                mismatches.append({"path": path, "status": "SOURCE_DRIFT", "expected_blob": expected[path], "observed_blob": observed})
        for path in expected:
            if path not in seen:
                mismatches.append({"path": path, "status": "MISSING_SOURCE"})
    return {"result": "PASS" if not mismatches else "HOLD", "source_entries": len(seen), "expected_entries": len(expected), "findings": sorted(mismatches, key=lambda x: (x['path'], x['status']))}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--release", choices=["r417", "r421"], required=True)
    p.add_argument("--archive", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args(argv)
    manifest = json.loads((ROOT / "manifest.json").read_text())
    record = manifest["reviewed"][a.release]
    try:
        result = inspect(a.archive, record["files"])
    except (OSError, BadZipFile, ValueError, RuntimeError) as e:
        result = {"result": "HOLD", "findings": [{"status": "ARTIFACT_UNREADABLE", "detail": type(e).__name__}]}
    result.update({"release": a.release, "github_head": record["commit"], "pr": record["pr"], "assertion": "ARTIFACT_SOURCE_TO_GITHUB_BLOBS_ONLY", "production": "HARD_HOLD"})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(f"{a.release}: {result['result']}; {len(result['findings'])} discrepancies; production HARD_HOLD")
    return 0 if result["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
