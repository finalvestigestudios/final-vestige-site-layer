"""Preparedness-only immutable cross-gate witness; evidence, NEVER release clearance.

Checks that the original 35-article review packet, integrated source reconciliation,
and single frozen WordPress/private-preview evidence window all refer to the same
manuscript candidates. No source, export, WordPress, or remote mutations.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def _bad_candidate(value):
    return not (isinstance(value, dict) and isinstance(value.get("branch"), str)
                and value["branch"].startswith("claude/prep-")
                and isinstance(value.get("body_sha"), str) and SHA.fullmatch(value["body_sha"]))


def _candidates(row, field):
    if not isinstance(row, dict) or not isinstance(row.get(field), list):
        return None
    values = row[field]
    if any(_bad_candidate(v) for v in values):
        return None
    keys = [(v["branch"], v["body_sha"]) for v in values]
    return set(keys) if len(keys) == len(set(keys)) else None


def _map(rows, errors, label):
    result = {}
    if not isinstance(rows, list):
        errors.append("MISSING_ROWS:" + label)
        return result
    for row in rows:
        slug = row.get("slug") if isinstance(row, dict) else None
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in result:
            errors.append("BAD_OR_DUPLICATE_SLUG:" + label)
        else:
            result[slug] = row
    return result


def _report_ok(report, status):
    return (isinstance(report, dict) and report.get("status") == status
            and report.get("errors") == []
            and report.get("publication_approved") is False
            and report.get("qualified_safety_approved") is False
            and report.get("live_release_allowed") is not True
            and report.get("merchant_offer_verified") is not True)


def check(packet, integrated, frozen):
    """Validate structural agreement only; input JSON is not proof of authenticity."""
    errors = []
    rows = []
    if not all(isinstance(r, dict) for r in (packet, integrated, frozen)):
        return _result(["MALFORMED_PARENT"], [])
    for name, report, status in (("original", packet, "REVIEW_PACKET_HARD_HOLD"),
                                 ("integrated", integrated, "INTEGRATED_REVIEW_HARD_HOLD"),
                                 ("frozen", frozen, "FROZEN_EXPORT_REVIEW_HARD_HOLD")):
        if not _report_ok(report, status):
            errors.append("FAILED_PARENT:" + name)
    if (packet.get("release") != "DRAFT_HARD_HOLD"
            or integrated.get("release_state") != "DRAFT_HARD_HOLD"
            or frozen.get("release_state") != "DRAFT_HARD_HOLD"):
        errors.append("RELEASE_STATE_DRIFT")
    if not isinstance(frozen.get("snapshot_sha256"), str) or not DIGEST.fullmatch(frozen["snapshot_sha256"]):
        errors.append("INVALID_FROZEN_SNAPSHOT")
    reports = frozen.get("reports")
    if not isinstance(reports, dict) or set(reports) != {"render", "anchor", "full"}:
        return _result(errors + ["THREE_REPORTS_REQUIRED"], [])
    render, anchor, full = (reports[k] for k in ("render", "anchor", "full"))
    for name, report, status in (("render", render, "RENDER_PARITY_REVIEW_HARD_HOLD"),
                                 ("anchor", anchor, "CLAIM_POSITION_REVIEW_HARD_HOLD"),
                                 ("full", full, "ALL_EXPORT_BYTES_REVIEW_HARD_HOLD")):
        if not _report_ok(report, status):
            errors.append("FAILED_AUDIT:" + name)
    if any(not isinstance(x, dict) for x in (render, anchor, full)):
        return _result(errors + ["INVALID_AUDIT_OBJECT"], [])
    originals = _map(packet.get("articles"), errors, "original")
    joined = _map(integrated.get("candidate_intersections"), errors, "integrated")
    renders = _map(render.get("articles"), errors, "render")
    anchors = _map(anchor.get("articles"), errors, "anchor")
    expected = set(originals)
    if len(expected) != 35 or any(set(m) != expected for m in (joined, renders, anchors)):
        errors.append("35_ARTICLE_COVERAGE_MISMATCH")
    forks = packet.get("unselected_conflicts")
    if (not isinstance(forks, list) or len(forks) != 9
            or any(not isinstance(f, dict) or f.get("selected_sha") is not None for f in forks)):
        errors.append("NINE_FORKS_NOT_PRESERVED")
    counts = integrated.get("counts")
    if not isinstance(counts, dict) or any(counts.get(k) != v for k, v in (
            ("original_articles", 35), ("unselected_manuscript_forks", 9),
            ("unselected_source_collisions", 5))):
        errors.append("SOURCE_OR_FORK_COUNT_DRIFT")
    exports = _map(full.get("exports"), errors, "export")
    if len(exports) < 50 or not expected.issubset(exports):
        errors.append("MISSING_FIFTY_PRIVATE_EXPORT_PAIRS")
    if frozen.get("matched_snapshot_pairs") != len(exports):
        errors.append("FROZEN_PAIR_COUNT_DRIFT")
    if isinstance(counts, dict) and (counts.get("wp_exports") != len(exports)
                                    or counts.get("private_previews") != len(exports)):
        errors.append("INTEGRATED_PAIR_COUNT_DRIFT")
    for slug, entry in exports.items():
        if any(not isinstance(entry.get(k), str) or not DIGEST.fullmatch(entry[k])
               for k in ("wp_sha256", "preview_sha256")):
            errors.append("INVALID_EXPORT_DIGEST:" + slug)
        if any(type(entry.get(k)) is not int or not (0 < entry[k] <= 3_000_000)
               for k in ("wp_bytes", "preview_bytes")):
            errors.append("INVALID_EXPORT_BYTES:" + slug)
        if entry.get("errors") != [] or entry.get("release_allowed") is not False or entry.get("qualified_review_required") is not True:
            errors.append("EXPORT_SAFETY_DRIFT:" + slug)
    for slug in sorted(expected):
        original = _candidates(originals[slug], "variants")
        r = _candidates(renders.get(slug), "matching_variant_candidates")
        a = _candidates(anchors.get(slug), "matching_original_candidates")
        i = _candidates(joined.get(slug), "matching_review_candidates")
        if (original is None or not original or r is None or a is None or i is None
                or not i or not r.issubset(original) or not a.issubset(original)
                or i != r.intersection(a, original)):
            errors.append("CANDIDATE_WITNESS_MISMATCH:" + slug)
        j = joined.get(slug, {})
        if j.get("auto_selected") is not False or j.get("qualified_review_required") is not True:
            errors.append("AUTO_SELECTION_OR_QD_BYPASS:" + slug)
        rows.append({"slug": slug, "candidate_count": len(i or ()), "auto_selected": False})
    if isinstance(counts, dict) and counts.get("candidate_intersection_articles") != sum(bool(r["candidate_count"]) for r in rows):
        errors.append("CANDIDATE_INTERSECTION_COUNT_DRIFT")
    return _result(errors, rows)


def _result(errors, rows):
    return {"schema": 1, "status": "INVALID_HARD_HOLD" if errors else "CROSS_GATE_WITNESS_REVIEW_HARD_HOLD",
            "release_state": "DRAFT_HARD_HOLD", "publication_approved": False,
            "qualified_safety_approved": False, "merchant_offer_verified": False,
            "live_release_allowed": False, "automatic_variant_selection": False,
            "errors": sorted(set(errors)), "article_count": len(rows),
            "witness_sha256": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "blocking_review": ["AUTHENTIC_GIT_AND_EXPORT_CUSTODY_NOT_ESTABLISHED_BY_THIS_CHECK",
                                "FIVE_SOURCE_CONFLICTS", "NINE_UNSELECTED_MANUSCRIPT_FORKS", "HUMAN_QD_REQUIRED"]}


def main(argv=None):
    parser = argparse.ArgumentParser()
    for name in ("original", "integrated", "frozen"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        paths = [getattr(args, n) for n in ("original", "integrated", "frozen")]
        if any(p.is_symlink() or not p.is_file() or not (0 < p.stat().st_size <= 5_000_000) for p in paths):
            raise ValueError("MISSING_OR_UNSAFE_EVIDENCE")
        result = check(*(json.loads(p.read_text(encoding="utf8")) for p in paths))
    except (OSError, ValueError, UnicodeError, TypeError, json.JSONDecodeError) as exc:
        result = _result(["UNAVAILABLE_EVIDENCE:" + type(exc).__name__], [])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2  # No implied QD/release approval; even structurally valid reports stay held.


if __name__ == "__main__":
    raise SystemExit(main())
