#!/usr/bin/env python3
"""R56: original-evidence-bound, PRIVATE review crosswalk for consequential actions.

This organizes the R53/R54 unresolved action/source evidence without silently
deduplicating shared URLs, dropping uncited blocks, or changing safety states.
All rows remain unverified; a human or qualified reviewer must examine the
underlying source and original article before any editorial/safety decision.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r56-private-unverified-action-source-crosswalk-v1"
REVIEW_STATE = "UNREVIEWED_HUMAN_SOURCE_AND_QUALIFIED_SAFETY_ASSESSMENT_REQUIRED"
FLAGS = ("may_publish", "qualified_safety_clearance", "independent_QD_approval",
         "human_source_links_verified", "claim_accuracy_verified")


class CrosswalkHold(ValueError):
    """An original work order, source relationship or safety hold was lost."""


def require(ok, message):
    if not ok:
        raise CrosswalkHold(message)


def load_r54():
    path = Path(__file__).with_name("r54_action_review_export.py")
    require(path.is_file() and not path.is_symlink(),
            "original R54 reviewer-export gate missing")
    spec = importlib.util.spec_from_file_location("r56_original_r54", path)
    require(spec is not None and spec.loader is not None,
            "original R54 reviewer-export gate cannot load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def crosswalk(report, *, expected=None):
    """Re-derive a complete machine-only crosswalk from original R53 evidence.

    Original R53 is ALWAYS recomputed from the on-disk corpus in the production
    CLI. Self-hashed caller fixtures do not constitute external source custody.
    No row is changed, collapsed, promoted or reclassified.
    """
    r54 = load_r54()
    if expected is None:
        expected = r54.EXPECTED
    rows = r54.audit_report(report, expected=expected)
    actions = rows["action_review.csv"]
    sources = rows["scoped_source_review.csv"]
    incidents = rows["open_safety_exceptions.csv"]
    inaccessible = rows["historical_source_access_hold.csv"]
    require(len(actions) == expected[1] and
            len(incidents) == expected[4] and
            len(inaccessible) == expected[5],
            "original unreviewed evidence census changed")

    action_ids = {}
    article_ordinals = set()
    for ordinal, row in enumerate(actions, 1):
        aid = row["work_order_id_sha256"]
        key = (row["article"], row["block_ordinal"])
        require(aid not in action_ids and key not in article_ordinals,
                "duplicate action ID or article/block ordinal")
        action_ids[aid] = row
        article_ordinals.add(key)
        require(row["review_state"] == "NOT_REVIEWED",
                "action review status must remain NOT_REVIEWED")
        require(row["same_block_citation_count"] ==
                len(row["citation_source_id_occurrences_json"]),
                "repeated citation occurrences changed")
        require(row["source_readings_count"] ==
                len(set(row["citation_source_id_occurrences_json"])),
                "per-action contributor-specific source readings changed")

    by_url = defaultdict(list)
    by_source_id = defaultdict(list)
    source_count_by_action = defaultdict(int)
    for row in sources:
        aid = row["work_order_id_sha256"]
        action = action_ids.get(aid)
        require(action is not None and
                row["article"] == action["article"] and
                row["block_ordinal"] == action["block_ordinal"],
                "source row has no exact originating article/action")
        require(row["review_state"] == "NOT_REVIEWED",
                "source review status must remain NOT_REVIEWED")
        require(row["citation_occurrences_in_block"] ==
                action["citation_source_id_occurrences_json"].count(row["source_id"]),
                "source-specific repeated citation count drift")
        source_count_by_action[aid] += 1
        by_url[row["original_url"]].append(row)
        by_source_id[row["source_id"]].append(row)

    for aid, action in action_ids.items():
        require(source_count_by_action[aid] == action["source_readings_count"],
                "lost a source reading in an individual work order")

    uncited = [row for row in actions if row["uncited_in_same_visible_block"]]
    cited = [row for row in actions if not row["uncited_in_same_visible_block"]]
    require(len(uncited) == expected[2] and len(cited) == expected[3],
            "cited-versus-uncited consequential action census changed")
    require(all(row["same_block_citation_count"] == 0 and
                row["source_readings_count"] == 0 for row in uncited),
            "uncited work order was given a fabricated source reading")

    grouped = []
    for url in sorted(by_url):
        occurrence_rows = by_url[url]
        variants = sorted({
            (r["source_id"], r["source_contributor_origin"],
             r["original_source_record_sha256"])
            for r in occurrence_rows
        })
        if len(variants) > 1 or any(
                r["shared_url_group_requires_human_review"]
                for r in occurrence_rows):
            grouped.append({
                "original_url_exact_not_canonicalized": url,
                "distinct_source_variants_not_merged": [
                    {"source_id": source_id, "source_contributor_origin": contributor,
                     "source_record_sha256": sha}
                    for source_id, contributor, sha in variants
                ],
                "ALL_original_action_scoped_reading_occurrences": occurrence_rows,
                "requires_independent_source_scope_review": True,
            })

    fallback = [
        row for row in sources
        if row["base_fallback_requires_human_review"]
    ]
    blocked_ids = set()
    historical = []
    for row in inaccessible:
        sid = row["original_source_id"]
        require(sid not in blocked_ids and
                row["historical_machine_failure_only"] is True,
                "historical access hold lost or reclassified")
        blocked_ids.add(sid)
        historical.append({
            "original_source_id": sid,
            "historical_failure_only_not_current_access_verdict": True,
            "action_scoped_readings_if_any": by_source_id.get(sid, []),
            "human_link_recheck_status": "NOT_REVIEWED",
        })
    for row in incidents:
        require(row["review_state"] == "NOT_REVIEWED",
                "safety exception falsely cleared")

    result = {
        "schema": SCHEMA,
        "issue": 136,
        "release_state": "HOLD",
        "review_state": REVIEW_STATE,
        "machine_only": True,
        "source_report_R53_sha256": report["fingerprint_sha256"],
        "counts": {
            "all_original_action_work_orders": len(actions),
            "uncited_consequential_action_blocks": len(uncited),
            "cited_consequential_action_blocks": len(cited),
            "all_action_scoped_source_reading_rows": len(sources),
            "shared_url_action_subset_review_groups_not_full_corpus_total": len(grouped),
            "action_scoped_fallback_readings_not_full_corpus_total": len(fallback),
            "historical_machine_access_holds_not_current_link_failures": len(historical),
            "open_safety_exceptions_without_authenticated_clearance": len(incidents),
        },
        "original_unreviewed_action_rows": actions,
        "original_unreviewed_action_source_rows": sources,
        "uncited_action_review_queue": uncited,
        "shared_url_variant_review_queue": grouped,
        "fallback_source_scope_review_queue": fallback,
        "historical_access_hold_queue": historical,
        "open_safety_exceptions_without_verified_article_mapping": incidents,
        "safety_incident_mapping_status": "HUMAN_EXACT_ARTICLE_AND_CLAIM_LOCATOR_REQUIRED",
        "corpus_wide_30_shared_URL_groups_and_43_fallbacks": (
            "NOT_CLEARED_BY_THIS_ACTION_SUBSET_CROSSWALK"),
        "limitations": (
            "This is a non-destructive, machine-only transport. Same-block "
            "uncited is not necessarily unsupported; a nearby or broader "
            "citation still needs independent contextual review. Same URLs "
            "do not mean interchangeable contributor readings. Historical "
            "link failures are not current failures. Safety incidents have "
            "not been linked to exact claim locators by a qualified reviewer. "
            "No human source link check, claim approval, qualified medical "
            "or hazard review, QD approval or publication is performed."),
        **{flag: False for flag in FLAGS},
    }
    result["fingerprint_sha256"] = r54.digest(result)
    return result


def verify_crosswalk(report, result, *, expected=None):
    require(type(result) is dict and result == crosswalk(report, expected=expected),
            "crosswalk evidence, approval state, order or fingerprint changed")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true",
                        help="verify exact source census; never write files")
    parser.add_argument("--write-private", action="store_true",
                        help="exclusively create ignored preparedness/build output")
    args = parser.parse_args(argv)
    try:
        r54 = load_r54()
        report = r54.original_report(ROOT.parent)
        result = crosswalk(report)
        verify_crosswalk(report, result)
        output = {
            "schema": SCHEMA, "release_state": "HOLD", "may_publish": False,
            "fingerprint_sha256": result["fingerprint_sha256"],
            "counts": result["counts"], "wrote_private_files": False,
        }
        if args.write_private:
            build = ROOT / "build"
            require(build.is_dir() and not build.is_symlink() and
                    build.resolve() == build.absolute(),
                    "private ignored build directory missing or redirected")
            folder = build / ("r56-unreviewed-crosswalk-HOLD-" +
                              result["fingerprint_sha256"][:20])
            require(not folder.exists(), "private output already exists")
            folder.mkdir(mode=0o700, exist_ok=False)
            path = folder / "UNVERIFIED_ACTION_SOURCE_CROSSWALK.json"
            with path.open("x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, sort_keys=True,
                          indent=2, allow_nan=False)
                handle.write("\n")
            output["wrote_private_files"] = True
            output["private_location"] = str(folder.relative_to(ROOT.parent))
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (CrosswalkHold, OSError, ValueError, TypeError, KeyError,
            ImportError, OverflowError) as exc:
        print("R56 PRIVATE CROSSWALK HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
