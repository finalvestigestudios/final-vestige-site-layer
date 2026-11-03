#!/usr/bin/env python3
"""R104 private offline export custody: byte-exact reviewer packet round-trip.

No network, CMS, source edits, publishing, approval ingestion or QD promotion.
Manifest hashes are inventory checks, NOT signatures or source verification.
Independently replay the original seven-cluster corpus before every operation.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent.resolve()
sys.path.insert(0, str(ROOT / "tools"))
import build
import r102_author_scoped_collision_workorder as r102
import r103_collision_offline_reviewer_handoff as r103

SCHEMA = "r104-exact-offline-review-export-custody-v1"
HOLD = "HOLD"
REVIEW = "NOT_REVIEWED"
MANIFEST = "r104-private-custody-manifest-HOLD.json"
EXPORTS = (
    ("r103-private-review-HOLD.html", "html"),
    ("r103-source-variants-NOT-VERIFIED.csv", "SOURCE_VARIANT"),
    ("r103-source-citations-NOT-VERIFIED.csv", "CITATION_OCCURRENCE"),
    ("r103-summary-HOLD.json", "summary"),
)
MAX_FILE_BYTES = 32 * 1024 * 1024


class Gate(ValueError):
    """Input or source drift: keep the entire release on HOLD."""


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Gate(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def original_packet() -> dict:
    """A caller-supplied sealed report is never its own trust anchor."""
    first = r102.workorder(build.Library())
    independent = r102.workorder(build.Library())
    return r103.packet(first, independent)


def create_payload(workorder: dict) -> dict[str, bytes]:
    # An amended/resealed input packet cannot establish its own provenance.
    # Reconstruct from the actual authored sources before rendering any bytes.
    need(workorder == original_packet(),
         "R103 reviewer workorder differs from independently replayed sources")
    need(workorder.get("schema") == r103.SCHEMA
         and workorder.get("release_state") == HOLD
         and workorder.get("may_publish") is False
         and workorder.get("may_merge") is False
         and workorder.get("human_source_and_claim_review") == REVIEW
         and workorder.get("qualified_safety_review") == REVIEW
         and workorder.get("independent_QD") == REVIEW
         and workorder.get("browser_and_wordpress_QA") == REVIEW
         and workorder.get("literal_url_groups") == 30
         and workorder.get("original_35_articles_1_buildable_tool") is True
         and workorder.get("missing_planned_tools") == 5,
         "source inventory, human review or publication HOLD changed")
    need(r102.digest({k: v for k, v in workorder.items()
                      if k != "sha256_seal"}) == workorder.get("sha256_seal"),
         "R103 untrusted report digest")
    content = {
        EXPORTS[0][0]: r103.html_text(workorder),
        EXPORTS[1][0]: r103.csv_text(workorder, "SOURCE_VARIANT"),
        EXPORTS[2][0]: r103.csv_text(workorder, "CITATION_OCCURRENCE"),
        EXPORTS[3][0]: json.dumps(
            {k: v for k, v in workorder.items() if k != "groups"},
            indent=2, sort_keys=True) + "\n",
    }
    payload = {name: value.encode("utf-8") for name, value in content.items()}
    need(set(payload) == {name for name, _ in EXPORTS}
         and all(0 < len(data) <= MAX_FILE_BYTES for data in payload.values()),
         "missing or oversized source/citation export")

    records = []
    for name, _kind in EXPORTS:
        records.append({"name": name, "byte_count": len(payload[name]),
                        "sha256": sha(payload[name])})
    groups = [{"group_number": g["group_number"],
               "literal_url_sha256": r102.digest(g["literal_url_NOT_VERIFIED"]),
               "original_group_sha256": g["group_sha256"],
               "variant_count": g["variant_count"],
               "citation_occurrences": g["citation_occurrences"]}
              for g in workorder["groups"]]
    need(len(groups) == 30 and [g["group_number"] for g in groups] == list(range(1, 31)),
         "incomplete original shared-URL group roster")
    manifest = {
        "schema": SCHEMA, "issue": 136,
        "release_state": HOLD, "may_merge": False, "may_publish": False,
        "human_source_review": REVIEW, "human_claim_review": REVIEW,
        "qualified_safety_review": REVIEW, "independent_QD": REVIEW,
        "browser_and_wordpress_QA": REVIEW,
        "sha256_is_not_a_signature_or_human_attestation": True,
        "r102_corpus_sha256": workorder["r102_corpus_sha256"],
        "r103_export_packet_sha256": workorder["sha256_seal"],
        "original_article_drafts": 35, "complete_tool_drafts": 1,
        "unfinished_tools": 5, "unreviewed_literal_url_groups": 30,
        "source_variant_rows": workorder["variant_rows"],
        "collision_citation_occurrences": workorder["collision_citation_occurrences"],
        "exports": records, "groups": groups,
    }
    manifest["sha256_seal"] = r102.digest(manifest)
    payload[MANIFEST] = (r102.canonical(manifest) + "\n").encode("utf-8")
    return payload


def safe_directory(raw: str) -> Path:
    directory = Path(raw)
    need(not directory.is_symlink() and directory.is_dir(),
         "missing directory or symlink directory refused")
    resolved = directory.resolve(strict=True)
    need(resolved != REPOSITORY and REPOSITORY not in resolved.parents,
         "review exports must stay entirely outside the repository")
    return resolved


def verify_dir(raw: str, expected: dict[str, bytes] | None = None) -> dict:
    """Reject added/missing/modified files, including a self-resealed manifest."""
    directory = safe_directory(raw)
    reference = expected if expected is not None else create_payload(original_packet())
    need(set(p.name for p in directory.iterdir()) == set(reference),
         "review bundle has unexpected, missing or renamed files")
    for name, reference_bytes in reference.items():
        path = directory / name
        need(not path.is_symlink() and path.is_file(),
             "non-regular or symlink packet file: " + name)
        mode = path.stat(follow_symlinks=False).st_mode
        need(stat.S_ISREG(mode), "not a regular file: " + name)
        need(path.stat().st_size == len(reference_bytes)
             and path.stat().st_size <= MAX_FILE_BYTES,
             "truncated or expanded evidence packet: " + name)
        with path.open("rb") as handle:
            observed = handle.read(MAX_FILE_BYTES + 1)
        need(hmac.compare_digest(sha(observed), sha(reference_bytes))
             and observed == reference_bytes,
             "byte-exact source/citation custody mismatch: " + name)
    return {"schema": SCHEMA, "release_state": HOLD,
            "verification": "BYTE_EXACT_EXPORT_MATCH_NOT_SOURCE_APPROVAL",
            "files": len(reference), "groups_unreviewed": 30,
            "may_publish": False, "may_merge": False}


def emit_dir(raw: str, expected: dict[str, bytes] | None = None) -> dict:
    """Create a sealed private bundle only in a pre-existing EMPTY scratch dir."""
    directory = safe_directory(raw)
    need(not any(directory.iterdir()),
         "scratch directory must be empty; never overwrite reviewer evidence")
    reference = expected if expected is not None else create_payload(original_packet())
    created: list[Path] = []
    try:
        for name, data in reference.items():
            target = directory / name
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            flags |= getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(target, flags, 0o600)
            created.append(target)
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        return verify_dir(str(directory), reference)
    except Exception:
        for path in created:
            try:
                path.unlink()
            except OSError:
                pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-check", action="store_true",
                       help="replay all source/citation export bytes without writing")
    group.add_argument("--emit-dir", metavar="EMPTY_SCRATCH_DIR")
    group.add_argument("--verify-dir", metavar="EXISTING_BUNDLE")
    args = parser.parse_args(argv)
    data = create_payload(original_packet())
    if args.emit_dir:
        result = emit_dir(args.emit_dir, data)
    elif args.verify_dir:
        result = verify_dir(args.verify_dir, data)
    else:
        result = {"schema": SCHEMA, "release_state": HOLD,
                  "verification": "IN_MEMORY_ONLY_NOT_SOURCE_APPROVAL",
                  "files": len(data), "groups_unreviewed": 30,
                  "may_publish": False, "may_merge": False}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Gate, r103.Gate, r102.Hold, OSError, ValueError, KeyError, TypeError) as exc:
        print("R104 PRIVATE HOLD: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
