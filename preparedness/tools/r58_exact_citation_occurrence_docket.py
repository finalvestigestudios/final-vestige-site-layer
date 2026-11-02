#!/usr/bin/env python3
"""R58 PRIVATE HOLD: exact per-citation occurrence reviewer docket.

A citation occurrence is a review work item, NOT evidence that the cited source
supports the claim. Never infer that a nearby action is supported by this token.
No filesystem writes by default, no network, no CMS or publication permissions.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r58-private-exact-citation-occurrence-docket-v1"
FLAGS = (
    "may_publish", "independent_QD_approval", "qualified_safety_clearance",
    "human_source_links_verified", "claim_accuracy_verified",
    "human_source_reviews_completed", "source_claim_accuracy_verified",
)
SHA = re.compile(r"[0-9a-f]{64}\Z")


class DocketHold(ValueError):
    """Input custody, per-token evidence or machine-only status has changed."""


def require(ok, reason):
    if not ok:
        raise DocketHold(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_hold(doc, label):
    require(type(doc) is dict and doc.get("schema") == (
        "r57-global-citation-to-action-review-bridge-v1") and
        doc.get("release_state") == "HOLD" and
        doc.get("machine_only") is True and
        all(doc.get(flag) is False for flag in FLAGS) and
        type(doc.get("fingerprint_sha256")) is str and
        bool(SHA.fullmatch(doc["fingerprint_sha256"])) and
        doc["fingerprint_sha256"] == digest({
            k: v for k, v in doc.items() if k != "fingerprint_sha256"
        }), label + " is untrusted, modified or falsely approved")


def create_docket(bridge, *, expected=(35, 1, 1959, 367, 43, 30, 779, 15, 25)):
    """Make a deterministic reviewer docket without discarding original evidence.

    Full R57 verification, including all contributor source and original HTML
    custody, MUST be executed by the production entry point before this call.
    Synthetic tests may use an explicit smaller census.
    """
    validate_hold(bridge, "original R57 full-corpus bridge")
    require(type(expected) is tuple and len(expected) == 9 and
            all(type(v) is int and v >= 0 for v in expected),
            "invalid independently pinned review census")
    counts = bridge.get("counts")
    require(type(counts) is dict and tuple(counts.get(k) for k in (
        "articles", "water_tools", "all_citation_occurrences",
        "all_original_article_source_relationships",
        "all_base_fallback_source_relationships",
        "all_global_shared_url_groups_even_uncited",
        "all_high_consequence_action_orders")) == expected[:7],
        "complete source, article or action census drift")
    relationships = bridge.get("all_original_cited_relationships_unreviewed")
    actions = bridge.get("all_original_consequential_action_orders_unreviewed")
    scopes = bridge.get("all_original_action_source_rows_unreviewed")
    shared = bridge.get("all_global_shared_url_groups_unreviewed")
    fallbacks = bridge.get("all_base_fallback_relationships_unreviewed")
    safety = bridge.get("open_safety_exceptions_unreviewed")
    access = bridge.get("historical_machine_access_holds_not_current_failures")
    require(all(type(v) is list for v in (
        relationships, actions, scopes, shared, fallbacks, safety, access)),
        "untrusted evidence collection type")
    require((len(relationships), len(actions), len(shared), len(fallbacks),
             len(safety), len(access)) == (expected[3], expected[6],
                                           expected[5], expected[4],
                                           expected[7], expected[8]),
            "source, action, safety or access records missing")

    action_ids = {}
    for action in actions:
        require(type(action) is dict and
                action.get("review_state") == "NOT_REVIEWED" and
                type(action.get("work_order_id_sha256")) is str and
                action["work_order_id_sha256"] not in action_ids,
                "action work order missing, duplicated or falsely reviewed")
        action_ids[action["work_order_id_sha256"]] = action
    by_relationship = defaultdict(list)
    for scope in scopes:
        require(type(scope) is dict and
                scope.get("review_state") == "NOT_REVIEWED" and
                type(scope.get("article")) is str and
                type(scope.get("source_id")) is str and
                scope.get("work_order_id_sha256") in action_ids and
                scope["article"] == action_ids[scope["work_order_id_sha256"]].get("article"),
                "action-source relationship lost or falsely reviewed")
        by_relationship[(scope["article"], scope["source_id"])].append(
            scope["work_order_id_sha256"])

    queue = []
    article_tally = defaultdict(int)
    relationship_ids = set()
    task_ids = set()
    source_scoped_total = 0
    for row in relationships:
        require(type(row) is dict and type(row.get("slug")) is str and
                type(row.get("source_id")) is str and
                row.get("human_link_checked_by_this_gate") is False and
                row.get("human_claim_reviewed_by_this_gate") is False,
                "source relationship identity changed or falsely reviewed")
        key = (row["slug"], row["source_id"])
        require(key not in relationship_ids, "repeated article/source relationship")
        relationship_ids.add(key)
        contexts = row.get("all_citation_contexts_for_human_claim_review")
        offsets = row.get("citation_token_codepoint_offsets")
        count = row.get("citation_occurrences")
        record = row.get("original_source_record_as_selected")
        require(type(count) is int and count > 0 and
                type(contexts) is list and len(contexts) == count and
                type(offsets) is list and len(offsets) == count and
                all(type(v) is str and v for v in contexts) and
                all(type(v) is int and v >= 0 for v in offsets) and
                offsets == sorted(set(offsets)),
                "individual citation excerpt or Unicode codepoint offset lost")
        require(type(record) is dict and
                row.get("original_source_record_sha256") == digest(record) and
                type(row.get("frozen_article_html_sha256")) is str and
                bool(SHA.fullmatch(row["frozen_article_html_sha256"])) and
                type(row.get("frozen_source_use_sha256")) is str and
                bool(SHA.fullmatch(row["frozen_source_use_sha256"])) and
                record.get("id") == row["source_id"] and
                record.get("_origin") == row.get("source_origin") and
                record.get("url") == row.get("source_url"),
                "citation unbound from frozen original reading/HTML/source")
        related = sorted(set(by_relationship.get(key, [])))
        source_scoped_total += len(related)
        for ordinal, (context, offset) in enumerate(zip(contexts, offsets), 1):
            identity = {
                "slug": row["slug"], "source_id": row["source_id"],
                "source_origin": row["source_origin"],
                "citation_ordinal_within_article_source": ordinal,
                "token_offset_codepoints_in_original_html": offset,
                "frozen_article_html_sha256": row["frozen_article_html_sha256"],
                "original_source_record_sha256": row["original_source_record_sha256"],
                "original_visible_citation_context_sha256": hashlib.sha256(
                    context.encode("utf-8")).hexdigest(),
            }
            task_id = digest(identity)
            require(task_id not in task_ids, "citation occurrence identity collision")
            task_ids.add(task_id)
            queue.append({
                "citation_occurrence_work_order_id_sha256": task_id,
                "exact_original_token_identity": identity,
                "original_unabridged_visible_context": context,
                "original_unabridged_contributor_source_record": record,
                "original_unabridged_article_source_relationship": row,
                "related_action_work_order_ids_same_article_source_ONLY_NOT_CLAIM_SUPPORT":
                    related,
                "same_url_variants_human_review_required":
                    row.get("shared_url_group_requires_human_review") is True,
                "base_fallback_human_scope_review_required":
                    row.get("base_fallback_requires_human_scope_review") is True,
                "human_source_retrieval_state": "NOT_REVIEWED",
                "human_claim_support_state": "NOT_REVIEWED",
                "qualified_hazard_safety_state": "NOT_REVIEWED",
            })
            article_tally[row["slug"]] += 1
    require(len(queue) == expected[2] and
            len(task_ids) == expected[2] and
            len(relationship_ids) == expected[3],
            "citation occurrence work orders missing or duplicated")
    result = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "machine_only": True,
        "parent_R57_bridge_sha256": bridge["fingerprint_sha256"],
        "counts": {
            "original_articles": expected[0], "water_tools": expected[1],
            "exact_citation_occurrence_work_orders": len(queue),
            "original_article_source_relationships": len(relationship_ids),
            "unreviewed_action_work_orders": len(actions),
            "unreviewed_global_shared_url_groups": len(shared),
            "unreviewed_base_fallback_relationships": len(fallbacks),
            "open_safety_exceptions": len(safety),
            "historical_machine_access_holds": len(access),
            "source_relationships_with_related_action_work_orders": sum(
                bool(by_relationship.get(key)) for key in relationship_ids),
            "per_article_citation_occurrences": dict(sorted(article_tally.items())),
        },
        "individual_original_citation_occurrence_review_queue": queue,
        "original_action_work_orders_NOT_REVIEWED": actions,
        "original_action_source_relationships_NOT_REVIEWED": scopes,
        "original_shared_url_evidence_NOT_REVIEWED": shared,
        "original_fallback_evidence_NOT_REVIEWED": fallbacks,
        "original_safety_exceptions_OPEN": safety,
        "original_historical_machine_access_holds": access,
        "limitations": (
            "Same-article/source action associations are NOT token-to-claim "
            "evidence or proof of support. Source URLs, machine accessibility "
            "and visible citation text do not establish correctness. This docket "
            "does not complete source checks, authenticate a reviewer, clear "
            "emergency/medical safety advice, authorize QD or publish."),
        **{flag: False for flag in FLAGS},
    }
    result["fingerprint_sha256"] = digest(result)
    return result


def verify_docket(bridge, result, *, expected=(35, 1, 1959, 367, 43, 30, 779, 15, 25)):
    require(type(result) is dict and result == create_docket(
        bridge, expected=expected),
        "private exact occurrence docket modified or reviewer approval forged")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--write-private", action="store_true")
    args = parser.parse_args(argv)
    try:
        # R57 production bridge explicitly re-runs R25 and R56 gates.
        import importlib.util
        path = Path(__file__).with_name("r57_global_citation_action_bridge.py")
        require(path.is_file() and not path.is_symlink(), "original R57 gate missing")
        spec = importlib.util.spec_from_file_location("r58_r57_custody", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        r54 = module.module("r54_action_review_export.py")
        r56 = module.module("r56_unreviewed_action_source_crosswalk.py")
        build = module.module("build.py")
        r25 = module.module("citation_fallback_review_gate.py")
        lib = build.Library(ROOT)
        original = r54.original_report(ROOT.parent)
        action = r56.crosswalk(original)
        r56.verify_crosswalk(original, action)
        cited = r25.audit(lib)
        bridge = module.bridge(lib, cited, action)
        module.verify_bridge(lib, cited, action, bridge)
        docket = create_docket(bridge)
        verify_docket(bridge, docket)
        summary = {"schema": SCHEMA, "release_state": "HOLD",
                   "may_publish": False, "counts": docket["counts"],
                   "fingerprint_sha256": docket["fingerprint_sha256"],
                   "wrote_private_files": False}
        if args.write_private:
            folder = ROOT / "build"
            require(folder.is_dir() and not folder.is_symlink() and
                    folder.resolve() == folder.absolute(),
                    "private ignored build folder missing or symlink")
            target = folder / ("r58-occurrences-HOLD-" +
                               docket["fingerprint_sha256"][:16])
            target.mkdir(mode=0o700, exist_ok=False)
            require(target.resolve().parent == folder.resolve(),
                    "private export escaped build root")
            with (target / "docket.json").open("x", encoding="utf-8",
                                               newline="\n") as stream:
                stream.write(json.dumps(docket, ensure_ascii=False,
                                        sort_keys=True, indent=2, allow_nan=False))
                stream.write("\n")
            summary["wrote_private_files"] = True
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (DocketHold, ValueError, OSError, KeyError, TypeError) as error:
        print("R58 PRIVATE HOLD: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
