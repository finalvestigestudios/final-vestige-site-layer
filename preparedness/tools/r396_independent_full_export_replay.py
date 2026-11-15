"""R396: independently replay R390 for every private export before R395 custody.

R395 replays original citation/anchor audits but previously accepted the frozen
R390 full-export report as a supplied JSON object. This additive review-only
checker regenerates R390 from private HTML, binds its rows to a no-follow R391
snapshot, and then invokes R395 native Git/citation replay inside the same
observation window. A clean result still means DRAFT_HARD_HOLD, NEVER QD PASS.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from . import r390_all_export_custody as full_gate
    from . import r391_frozen_export_attestation as frozen_gate
    from . import r395_authentic_render_replay as replay_gate
except ImportError:
    import r390_all_export_custody as full_gate
    import r391_frozen_export_attestation as frozen_gate
    import r395_authentic_render_replay as replay_gate

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
DIGEST = re.compile(r"[a-f0-9]{64}\Z")


def _canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _result(errors, counts=None, digest=None):
    return {"schema": 1,
            "status": "INVALID_HARD_HOLD" if errors else "INDEPENDENT_FULL_EXPORT_REPLAY_HARD_HOLD",
            "release_state": "DRAFT_HARD_HOLD", "publication_approved": False,
            "qualified_safety_approved": False, "live_release_allowed": False,
            "merchant_offer_verified": False, "automatic_variant_selection": False,
            "errors": sorted(set(errors)), "counts": counts or {},
            "independent_replay_sha256": digest,
            "required_reviews": ["FIVE_SOURCE_COLLISIONS", "NINE_SHELTER_FORKS",
                                 "ARTICLE_7_WATER", "ARTICLE_11_FOOD",
                                 "TOOL_104_CHILD_PRIVACY", "QUALIFIED_QD_SAFETY_REVIEW",
                                 "NATIVE_BUILD_PRIVATE_HTML_AND_COMMERCIAL_ACCEPTANCE"]}


def _valid_held(obj, expected):
    return (isinstance(obj, dict) and obj.get("status") == expected and
            obj.get("errors") == [] and obj.get("publication_approved") is False and
            obj.get("qualified_safety_approved") is False and
            obj.get("live_release_allowed") is not True and
            obj.get("merchant_offer_verified") is not True and
            obj.get("automatic_variant_selection") is not True)


def audit(repo: Path, original: dict, integrated: dict, frozen: dict,
          witness: dict, claimed_r395: dict, wp_dir: Path, preview_dir: Path,
          *, full_auditor=None, snapshotter=None, native_replayer=None):
    """Isolated tests may supply fakes; native CLI ALWAYS uses real validators."""
    errors, counts = [], {}
    full_auditor = full_gate.audit if full_auditor is None else full_auditor
    snapshotter = frozen_gate._snapshot if snapshotter is None else snapshotter
    native_replayer = replay_gate.replay_native if native_replayer is None else native_replayer
    try:
        if not _valid_held(original, "REVIEW_PACKET_HARD_HOLD"):
            errors.append("ORIGINAL_DRAFT_MANUSCRIPT_EVIDENCE_MISSING")
        if not _valid_held(integrated, "INTEGRATED_REVIEW_HARD_HOLD"):
            errors.append("INTEGRATED_SOURCE_CITATION_EVIDENCE_MISSING")
        if not _valid_held(frozen, "FROZEN_EXPORT_REVIEW_HARD_HOLD"):
            errors.append("FROZEN_PRIVATE_EXPORT_EVIDENCE_MISSING")
        if not _valid_held(witness, "CROSS_GATE_WITNESS_REVIEW_HARD_HOLD"):
            errors.append("ORIGINAL_CROSS_GATE_WITNESS_MISSING")
        if not _valid_held(claimed_r395, "AUTHENTIC_RENDER_REPLAY_REVIEW_HARD_HOLD"):
            errors.append("R395_NATIVE_GIT_AND_CITATION_REPLAY_MISSING")
        if not isinstance(claimed_r395, dict) or not isinstance(claimed_r395.get("replay_sha256"), str) or not DIGEST.fullmatch(claimed_r395["replay_sha256"]):
            errors.append("R395_REPLAY_DIGEST_MISSING")
        articles = original.get("articles") if isinstance(original, dict) else None
        conflicts = original.get("unselected_conflicts") if isinstance(original, dict) else None
        slugs = [r.get("slug") for r in articles] if isinstance(articles, list) and all(isinstance(r, dict) for r in articles) else []
        if (len(slugs) != 35 or len(set(slugs)) != 35 or
                any(not isinstance(s, str) or not SLUG.fullmatch(s) for s in slugs)):
            errors.append("ORIGINAL_35_SLUG_CUSTODY_INVALID")
        if not isinstance(conflicts, list) or len(conflicts) != 9:
            errors.append("NINE_ORIGINAL_FORKS_NOT_PRESERVED")
        if errors:
            return _result(errors)
        before = {"wp": snapshotter(Path(wp_dir)), "preview": snapshotter(Path(preview_dir))}
        first_wp, first_pv = before["wp"]["files"], before["preview"]["files"]
        counts["private_pairs"] = len(first_wp)
        counts["original_articles"] = len(slugs)
        counts["unselected_shelter_forks"] = len(conflicts)
        if set(first_wp) != set(first_pv) or len(first_wp) < 50 or not set(slugs).issubset(first_wp):
            return _result(["PRIVATE_EXPORT_SET_INCOMPLETE"], counts)
        fresh_full = full_auditor(Path(wp_dir), Path(preview_dir), slugs)
        if not _valid_held(fresh_full, "ALL_EXPORT_BYTES_REVIEW_HARD_HOLD"):
            errors.append("INDEPENDENT_R390_FULL_EXPORT_AUDIT_FAILED")
        claimed_full = frozen.get("reports", {}).get("full")
        if _canonical(fresh_full) != _canonical(claimed_full):
            errors.append("R390_FULL_REPORT_NOT_REPRODUCED_FROM_HTML")
        rows = fresh_full.get("exports") if isinstance(fresh_full, dict) else None
        if not isinstance(rows, list) or len(rows) != len(first_wp):
            errors.append("R390_FULL_REPORT_ROW_SET_INVALID")
        else:
            seen = set()
            for row in rows:
                slug = row.get("slug") if isinstance(row, dict) else None
                if slug in seen or slug not in first_wp or slug not in first_pv:
                    errors.append("R390_DUPLICATE_OR_UNKNOWN_EXPORT_SLUG")
                    continue
                seen.add(slug)
                a, b = first_wp[slug], first_pv[slug]
                if (row.get("wp_sha256") != a["sha256"] or
                        row.get("preview_sha256") != b["sha256"] or
                        row.get("wp_bytes") != a["size"] or
                        row.get("preview_bytes") != b["size"] or
                        row.get("qualified_review_required") is not True or
                        row.get("release_allowed") is not False or
                        row.get("errors") != [] or
                        row.get("kind") != ("original_article" if slug in slugs else "unreviewed_supplemental")):
                    errors.append("R390_HASH_OR_SAFETY_STATE_DRIFT:" + str(slug))
            if seen != set(first_wp):
                errors.append("R390_EXPORT_COVERAGE_GAP")
        if frozen.get("matched_snapshot_pairs") != len(first_wp):
            errors.append("FROZEN_EXPORT_COUNT_DRIFT")
        inventory = {k: {s: v["sha256"] for s, v in sorted(a["files"].items())}
                     for k, a in sorted(before.items())}
        if frozen.get("snapshot_sha256") != sha256(_canonical(inventory)).hexdigest():
            errors.append("FROZEN_SNAPSHOT_NOT_REPRODUCED")
        # Re-run R395 with its real native Git provenance and independent render /
        # anchor checks; never trust an arbitrary submitted R395 JSON by itself.
        fresh_replay = None
        if not errors:
            fresh_replay = native_replayer(repo, original, integrated, frozen, witness,
                                           Path(wp_dir), Path(preview_dir))
            if not _valid_held(fresh_replay, "AUTHENTIC_RENDER_REPLAY_REVIEW_HARD_HOLD"):
                errors.append("R395_AUTHENTIC_NATIVE_REPLAY_FAILED")
            elif _canonical(fresh_replay) != _canonical(claimed_r395):
                errors.append("R395_REPLAY_REPORT_NOT_REPRODUCED")
        after = {"wp": snapshotter(Path(wp_dir)), "preview": snapshotter(Path(preview_dir))}
        if before != after:
            errors.append("PRIVATE_HTML_CHANGED_DURING_INDEPENDENT_REPLAY")
        if not errors:
            digest = sha256(_canonical({"original": original, "full": fresh_full,
                                       "r395": fresh_replay, "snapshot": inventory})).hexdigest()
            return _result([], counts, digest)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError,
            UnicodeError, json.JSONDecodeError) as exc:
        errors.append("INDEPENDENT_AUDIT_INPUT_FAILURE:" + type(exc).__name__)
    except Exception as exc:  # Never let a test/CLI crash turn into a release PASS.
        errors.append("NATIVE_AUDIT_UNAVAILABLE:" + type(exc).__name__)
    return _result(errors, counts)


def main(argv=None):
    parser = argparse.ArgumentParser(description="R396 read-only full-export R390/R395 replay")
    parser.add_argument("--repo", type=Path, default=Path("."))
    for name in ("original", "integrated", "frozen", "witness", "r395", "wp", "preview"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        reports = [json.loads(getattr(args, name).read_text(encoding="utf-8"))
                   for name in ("original", "integrated", "frozen", "witness", "r395")]
        result = audit(args.repo, *reports, args.wp, args.preview)
    except (OSError, ValueError, UnicodeError, TypeError, json.JSONDecodeError) as exc:
        result = _result(["NATIVE_EVIDENCE_NOT_AVAILABLE:" + type(exc).__name__])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2  # Even successful technical custody NEVER grants publishing/safety approval.


if __name__ == "__main__":
    raise SystemExit(main())
