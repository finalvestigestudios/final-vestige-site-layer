"""Read-only source audit for Final Vestige's 4-editorial/2-commercial Dispatch pilot.

Usage: python email_copy_preflight.py REPOSITORY_ROOT [--json]
This script never edits files, sends email, makes requests or creates subscribers.
It does not certify a Jetpack render, merchant approval, consent or CAN-SPAM compliance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

SOURCE_PAIRS = [
    ("dispatch/campaign-2026-mind/issues/01-the-mind-is-not-a-camera.md", "dispatch/r444/ISSUE01_UNADOPTED.md"),
    ("dispatch/campaign-2026-mind/issues/02-before-hypnosis-had-a-name.md", "dispatch/r443/ISSUE02_UNADOPTED.md"),
    ("dispatch/campaign-2026-mind/issues/03-the-twelve-minute-question.md", "dispatch/r441/ISSUE03_UNADOPTED.txt"),
    ("dispatch/campaign-2026-mind/issues/04-the-hatch-and-the-spark.md", "dispatch/r442/ISSUE04_APOLLO_UNADOPTED.txt"),
    ("dispatch/campaign-2026-mind/issues/05-before-you-press-play.md", "dispatch/r440/ISSUE_05_HYPNOSIS_LIVE_UNADOPTED.md"),
    ("dispatch/campaign-2026-mind/issues/06-the-evidence-log.md", "dispatch/r445/ISSUE06_EIGHT_CUPS_UNADOPTED.md"),
]


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def analyze_text(number: int, variant: str, raw: str, expected_sha: str | None = None) -> dict:
    data = raw.encode("utf-8")
    sha = git_blob_sha(data)
    lines = raw.splitlines()
    subject = next((s for s in lines if re.match(r"\*{0,2}Subject(?: candidate)?:", s)), "")
    preheader = next((s for s in lines if re.match(r"\*{0,2}Preheader(?: candidate)?:", s)), "")
    urls = re.findall(r"https?://[^\s\]>\)]+", raw)
    external = [u for u in urls if "finalvestige.com" not in u]
    lower = raw.lower()
    blocks = []
    if not subject or not preheader:
        blocks.append("MISSING_SUBJECT_OR_PREHEADER")
    if "[[" not in raw or "postal" not in lower or "unsubscribe" not in lower:
        blocks.append("LEGAL_WITNESS_NOT_EXPLICIT")
    else:
        blocks.append("POSTAL_AND_UNSUBSCRIBE_NOT_RENDER_VERIFIED")
    if number in (3, 5):
        if "commercial disclosure" not in lower:
            blocks.append("MISSING_COMMERCIAL_DISCLOSURE")
        blocks.extend(("NAMED_AFFILIATE_EMAIL_PERMISSION_MISSING", "LIVE_APPROVED_GUIDE_AND_EARNING_URL_MISSING"))
    if variant == "alternate" and number == 5 and "SUBSCRIBER-FACING CANDIDATE COPY ENDS" in raw:
        blocks.append("REVIEWER_NOTES_OUTSIDE_EMAIL_BODY_MUST_BE_EXCLUDED")
    if expected_sha and sha != expected_sha:
        blocks.append("SOURCE_CHANGED_REVIEW_REQUIRED")
    return {
        "edition": number, "variant": variant, "sha": sha,
        "subject_present": bool(subject), "preheader_present": bool(preheader),
        "url_count": len(urls), "external_url_count": len(external),
        "review_required": sorted(set(blocks)), "release": "HOLD_UNSENT",
    }


def scan(root: pathlib.Path, pins: dict[str, str] | None = None) -> dict:
    pins = pins or {}
    rows = []
    missing = []
    for i, (original, alternate) in enumerate(SOURCE_PAIRS, 1):
        for variant, path in (("original", original), ("alternate", alternate)):
            file = root / path
            if not file.is_file():
                missing.append(path)
                continue
            rows.append({"path": path, **analyze_text(i, variant, file.read_text(encoding="utf-8"), pins.get(path))})
    return {
        "campaign": "fv-dispatch-six-week-draft", "master_issue": 174,
        "expected_editorial": [1, 2, 4, 6], "expected_commercial": [3, 5],
        "source_files_found": len(rows), "source_files_missing": missing,
        "source_pin_mismatches": [r["path"] for r in rows if "SOURCE_CHANGED_REVIEW_REQUIRED" in r["review_required"]],
        "editions": rows, "send_authorized": False, "release": "HOLD_UNSENT",
        "caveat": "Static source QA only; NOT a WordPress email render, legal attestation, merchant authorization, or send gate."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_root", type=pathlib.Path)
    parser.add_argument("--pins", type=pathlib.Path)
    args = parser.parse_args()
    pins_doc = json.loads(args.pins.read_text(encoding="utf-8")) if args.pins else {}
    pins = pins_doc.get("source_pins", pins_doc)
    result = scan(args.repository_root, pins)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["source_files_missing"] or result["source_pin_mismatches"] else 0


if __name__ == "__main__":
    sys.exit(main())
