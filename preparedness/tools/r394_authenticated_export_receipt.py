"""R394: original Git-object + private export custody receipt; NEVER a safety pass.

This closes R393's structural-only witness gap. The exact R384 original Git
manifest and 77 pinned original objects must be available, and the R391
frozen-export receipt must match files reread with no-follow inode checks.
A valid result is still a draft/HARD HOLD requiring qualified human review.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

try:
    from . import r384_variant_review_packet as originals
    from . import r391_frozen_export_attestation as frozen_audit
    from . import r393_cross_gate_witness as cross_gate
except ImportError:  # Direct CLI invocation from preparedness/tools
    import r384_variant_review_packet as originals
    import r391_frozen_export_attestation as frozen_audit
    import r393_cross_gate_witness as cross_gate

MANIFEST_SHA = "5e7d9a8972872c82b4bc46ac13aab18883d8149a"
BRANCH_PINS = {
    "claude/prep-start-bbfeb8": "2122d856fce9f64887c16df3d52e64be9f59a55b",
    "claude/prep-food-ccdc55": "f911ff7a655de8d81535ea86ec3d65a49ee76648",
    "claude/prep-health-837444": "d5ef5bafd68361434dd1cc9209915b8e8a4eaf17",
    "claude/prep-hist-field-9db767": "4e5caf812727953aa45e3bda2d382f2c67b6a09c",
    "claude/prep-hist-food-b81f19": "67e116e536c7410bed30f8f3b1bb8c166f3c223d",
    "claude/prep-hist-home-0e0e38": "7504a5f099594d635e3dd7332a33a2e1346c43a2",
    "claude/prep-shelter-5e1e0e": "5daeaf2dd5ab71806a6b73c91edfb1d8df5da976",
    "claude/prep-shelter-continuation": "ac8625faf30dd5538fadc31e06cb5a2cea1defae",
    "claude/prep-shelter-followup-evidence": "6a5998ead97eca997e573ce8d3ceacf1c6aabad4",
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value):
    return sha256(value).hexdigest()


def _receipt(errors, digest=None, counts=None):
    return {
        "schema": 1,
        "status": "INVALID_HARD_HOLD" if errors else "AUTHENTIC_OBJECT_AND_EXPORT_REVIEW_HARD_HOLD",
        "release_state": "DRAFT_HARD_HOLD",
        "publication_approved": False,
        "qualified_safety_approved": False,
        "live_release_allowed": False,
        "merchant_offer_verified": False,
        "automatic_variant_selection": False,
        "errors": sorted(set(errors)),
        "custody_sha256": digest,
        "counts": counts or {},
        "required_reviews": ["SOURCE_SCOPE_FIVE_GROUPS", "SHELTER_NINE_FORKS",
                             "ARTICLE_7_WATER", "ARTICLE_11_FOOD", "TOOL_104_CHILD_PRIVACY",
                             "QUALIFIED_HUMAN_QD", "NATIVE_BUILD_AND_PRIVATE_RENDER"],
    }


def attest(manifest_bytes, blob_reader, original_packet, integrated, frozen, witness,
           wp_dir, preview_dir, *, expected_manifest_sha=MANIFEST_SHA,
           expected_branch_pins=BRANCH_PINS):
    """Return review-only original-object/export attestation, never a release PASS.

    expected_* may be overridden by isolated synthetic tests, not CLI. Authentic
    CLI pins the original 77-object inventory and nine original branch identities.
    """
    errors = []
    counts = {}
    try:
        if not isinstance(manifest_bytes, bytes) or originals.blob_sha(manifest_bytes) != expected_manifest_sha:
            return _receipt(["ORIGINAL_MANIFEST_GIT_BLOB_PIN_MISMATCH"])
        manifest = json.loads(manifest_bytes)
        pins = manifest.get("branch_pins")
        if not isinstance(pins, list) or len(pins) != 9 or any(not isinstance(p, dict) for p in pins):
            return _receipt(["NINE_BRANCH_PINS_REQUIRED"])
        current = {p.get("branch"): p.get("sha") for p in pins}
        if len(current) != len(pins) or current != expected_branch_pins:
            return _receipt(["ORIGINAL_CONTRIBUTOR_BRANCH_PIN_DRIFT"])
        rebuilt = originals.build_packet(manifest, blob_reader)
        if rebuilt.get("status") != "REVIEW_PACKET_HARD_HOLD" or rebuilt.get("errors"):
            return _receipt(["ORIGINAL_GIT_OBJECT_CUSTODY_FAILED"] + rebuilt.get("errors", []))
        if canonical(rebuilt) != canonical(original_packet):
            errors.append("ORIGINAL_PACKET_NOT_REPRODUCED_FROM_GIT_BLOBS")
        counts["original_articles"] = len(rebuilt["articles"])
        counts["original_conflicts"] = len(rebuilt["unselected_conflicts"])
        counts["original_manifest_objects"] = len(manifest.get("objects", []))
        cross = cross_gate.check(original_packet, integrated, frozen)
        if cross["status"] != "CROSS_GATE_WITNESS_REVIEW_HARD_HOLD" or cross.get("errors"):
            errors.append("R393_CROSS_GATE_REJECTED")
        if canonical(cross) != canonical(witness):
            errors.append("R393_WITNESS_OR_DIGEST_NOT_REPRODUCED")
        # This is a second direct observation of the private exports. R391 must
        # still run the independent audits within its own frozen window.
        before_wp = frozen_audit._snapshot(Path(wp_dir))
        before_preview = frozen_audit._snapshot(Path(preview_dir))
        wp, pv = before_wp["files"], before_preview["files"]
        counts["wp_private_pairs"] = len(wp)
        if set(wp) != set(pv) or len(wp) < 50:
            errors.append("INCOMPLETE_OR_MISMATCHED_PRIVATE_EXPORTS")
        if not {row["slug"] for row in rebuilt["articles"]}.issubset(wp):
            errors.append("ORIGINAL_35_NOT_IN_PRIVATE_EXPORTS")
        full = frozen.get("reports", {}).get("full", {})
        rows = full.get("exports", []) if isinstance(full, dict) else []
        if not isinstance(rows, list):
            rows = []
        indexed = {}
        for row in rows:
            slug = row.get("slug") if isinstance(row, dict) else None
            if not isinstance(slug, str) or slug in indexed:
                errors.append("DUPLICATE_OR_INVALID_EXPORT_REPORT_SLUG")
            else:
                indexed[slug] = row
        if set(indexed) != set(wp) or set(wp) != set(pv):
            errors.append("FROZEN_REPORT_EXPORT_SET_MISMATCH")
        for slug in sorted(set(wp) & set(pv) & set(indexed)):
            row = indexed[slug]
            if (row.get("wp_sha256") != wp[slug]["sha256"] or
                    row.get("preview_sha256") != pv[slug]["sha256"] or
                    row.get("wp_bytes") != wp[slug]["size"] or
                    row.get("preview_bytes") != pv[slug]["size"] or
                    row.get("release_allowed") is not False or
                    row.get("qualified_review_required") is not True or row.get("errors") != []):
                errors.append("PRIVATE_EXPORT_HASH_OR_HOLD_MISMATCH:" + slug)
        inventory = {"preview": {k: v["sha256"] for k, v in sorted(pv.items())},
                     "wp": {k: v["sha256"] for k, v in sorted(wp.items())}}
        if frozen.get("snapshot_sha256") != _sha256(canonical(inventory)):
            errors.append("FROZEN_SNAPSHOT_DIGEST_NOT_REPRODUCED")
        after_wp = frozen_audit._snapshot(Path(wp_dir))
        after_preview = frozen_audit._snapshot(Path(preview_dir))
        if before_wp != after_wp or before_preview != after_preview:
            errors.append("PRIVATE_EXPORT_CHANGED_DURING_RECEIPT")
        if not errors:
            payload = {"original_manifest_sha": expected_manifest_sha,
                       "original_git_packet": rebuilt,
                       "cross_gate": cross,
                       "integrated_report": integrated, "frozen_report": frozen,
                       "private_export_inventory": inventory}
            return _receipt([], _sha256(canonical(payload)), counts)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError,
            json.JSONDecodeError, subprocess.SubprocessError) as exc:
        errors.append("CUSTODY_UNAVAILABLE:" + type(exc).__name__)
    return _receipt(errors, None, counts)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    for name in ("original", "integrated", "frozen", "witness", "wp", "preview"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    def read(sha):
        return subprocess.run(["git", "-C", str(args.repo), "cat-file", "blob", sha],
                              capture_output=True, check=True, timeout=30).stdout
    try:
        packet = json.loads(args.original.read_text(encoding="utf-8"))
        integrated = json.loads(args.integrated.read_text(encoding="utf-8"))
        frozen = json.loads(args.frozen.read_text(encoding="utf-8"))
        witness = json.loads(args.witness.read_text(encoding="utf-8"))
        result = attest(read(MANIFEST_SHA), read, packet, integrated, frozen,
                        witness, args.wp, args.preview)
    except (OSError, ValueError, UnicodeError, TypeError, json.JSONDecodeError,
            subprocess.SubprocessError) as exc:
        result = _receipt(["AUTHENTIC_NATIVE_INPUT_UNAVAILABLE:" + type(exc).__name__])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2  # Even authentic custody cannot grant QD/safety or release approval.


if __name__ == "__main__":
    raise SystemExit(main())
