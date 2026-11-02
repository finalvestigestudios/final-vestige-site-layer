"""R123: private, read-only six-app Windows 11 witness progress; NEVER release.

Only summary counts and fixed check identifiers are emitted. Physical reviews,
source custody, antivirus, licensing, QD approval and founder approval are
separate gates. No evidence files or candidate executables are modified.
"""
from __future__ import annotations

import argparse
from private_review_cli_r146 import PrivateReviewParser
import json
import sys
from pathlib import Path

import windows11_manual_acceptance_r109 as qa
import windows11_witness_writer_r122 as writer
import windows11_witness_inventory_r124 as inventory

SCHEMA = "fv-labs-win11-progress-r123-v1"
HOLD = qa.ERROR


def inspect(*, dist: Path, r9_report: Path, expected_pin: str,
            review: Path, witnesses: Path) -> dict:
    """Fail closed on untrusted custody or an inconsistent witness inventory.

    This is read-only reviewer guidance, not an attestation. An independently
    authenticated R9 digest and genuine Win11 workstation are required.
    """
    pin = qa.external_r9_pin(expected_pin)
    build = qa.native_win11_build()
    report, actual, raw = qa.load_custody(dist, r9_report, pin)
    template = qa.make_template(report, actual, raw)
    writer._safe_dir(review.parent)
    witness_dir = writer._safe_dir(witnesses)
    writer._excluded_from_candidates(review, dist)
    writer._excluded_from_candidates(witness_dir, dist)

    # Do not race a cooperating R122 writer or silently accept stale locks.
    lock = review.with_name(review.name + ".r122.lock")
    if lock.exists() or lock.is_symlink():
        raise qa.ReviewHold("Concurrent or abandoned review lock")

    original = qa._bytes(review, qa.MAX_REPORT_BYTES)
    matrix = qa._strict_json(original)
    if matrix.get("windows11_build") != build:
        raise qa.ReviewHold("Native reviewer build mismatch")
    valid = qa.validate_review(matrix, template, witness_dir)

    # R109 checks every referenced witness but intentionally ignores stray
    # files. An orphan may indicate an interrupted R122 write; require manual
    # custody investigation instead of reporting an apparently clean queue.
    per_app = []
    for app in qa.ALL:
        counts = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0}
        next_check = None
        for check in qa._checks(app):
            state = matrix["apps"][app]["checks"][check]["state"]
            counts[state] += 1
            if state == "NOT_RUN" and next_check is None:
                next_check = check
        per_app.append({"app": app, "counts": counts, "next_check": next_check})

    # R124: same strict inventory contract as the one-check writer.
    inventory.verify_clean(matrix, witness_dir)

    # Bind the output to a second full witness check and the original matrix
    # bytes; this is still cooperative local custody, not a hostile-FS proof.
    if qa._bytes(review, qa.MAX_REPORT_BYTES) != original:
        raise qa.ReviewHold("Review changed during inspection")
    verified_again = qa.validate_review(matrix, template, witness_dir)
    inventory.verify_clean(matrix, witness_dir)
    if verified_again != valid or sum(valid["counts"].values()) != 46:
        raise qa.ReviewHold("Inconsistent manual acceptance counts")
    combined = {key: sum(p["counts"][key] for p in per_app)
                for key in ("PASS", "FAIL", "NOT_RUN")}
    if combined != valid["counts"]:
        raise qa.ReviewHold("Summary does not agree with verified witness counts")

    return {"schema": SCHEMA, "status": "RELEASE_HOLD",
            "matrix_status": valid["status"], "counts": combined,
            "total_checks": 46, "per_app": per_app,
            "release_authorized": False, "premium_editor_licensed": False}


def main(argv: list[str] | None = None) -> int:
    parser = PrivateReviewParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--r9-report", type=Path, required=True)
    # Intentionally redact missing/invalid pin through the common HOLD handler.
    parser.add_argument("--expected-r9-sha256")
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--witnesses", type=Path, required=True)
    try:
        # Parse inside the same constant-message privacy boundary as inspect.
        args = parser.parse_args(argv)
        result = inspect(
            dist=args.dist, r9_report=args.r9_report,
            expected_pin=args.expected_r9_sha256,
            review=args.review, witnesses=args.witnesses)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except (qa.ReviewHold, OSError, UnicodeError, ValueError, TypeError, KeyError):
        print(HOLD, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
