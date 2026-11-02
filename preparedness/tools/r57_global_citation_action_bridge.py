#!/usr/bin/env python3
"""R57: full-corpus source groups + fallback relationships linked to R56 actions.

A PRIVATE, deterministic evidence bridge, not a fact check or safety decision.
The complete 30-group / 43-fallback archive remains independently reviewable
even where no high-consequence action cites the source. No URL deduplication.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r57-global-citation-to-action-review-bridge-v1"
CENSUS = (35, 1, 1959, 367, 43, 30)
INVENTORY = (224, 186, 30, 15)
ACTIONS = (779, 237, 542, 15, 25)
FLAGS = ("may_publish", "independent_QD_approval", "qualified_safety_clearance",
         "human_source_links_verified", "claim_accuracy_verified",
         "human_source_reviews_completed", "source_claim_accuracy_verified")


class BridgeHold(ValueError):
    """Source/citation/action evidence changed or appeared falsely approved."""


def need(ok, why):
    if not ok:
        raise BridgeHold(why)


def module(filename):
    path = Path(__file__).with_name(filename)
    need(path.is_file() and not path.is_symlink(), "required original gate missing: " + filename)
    spec = importlib.util.spec_from_file_location("r57_" + filename[:-3], path)
    need(spec is not None and spec.loader is not None,
         "required original gate cannot load: " + filename)
    item = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(item)
    return item


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    import hashlib
    return hashlib.sha256(canonical(value)).hexdigest()


def untouched(doc, title):
    need(type(doc) is dict and doc.get("release_state") == "HOLD"
         and all(doc.get(k) is False for k in FLAGS if k in doc),
         title + " escaped machine-only HOLD")
    fp = doc.get("fingerprint_sha256")
    need(type(fp) is str and len(fp) == 64 and fp == digest({
        k: v for k, v in doc.items() if k != "fingerprint_sha256"
    }), title + " original evidence fingerprint changed")


def bridge(lib, cited, action, *, census=CENSUS, inventory=INVENTORY,
           action_census=ACTIONS):
    """Reconcile R25's whole cited corpus against R56's consequential subset.

    Inputs are pre-audited by their original gates in the production CLI.
    Recheck the entire raw URL/variant inventory here, including uncited groups.
    Synthetic callers may explicitly supply smaller censuses for isolated tests.
    """
    need(type(census) is tuple and len(census) == 6
         and all(type(v) is int and v >= 0 for v in census),
         "invalid frozen article/citation census")
    need(type(inventory) is tuple and len(inventory) == 4
         and all(type(v) is int and v >= 0 for v in inventory),
         "invalid frozen source inventory")
    need(type(action_census) is tuple and len(action_census) == 5
         and all(type(v) is int and v >= 0 for v in action_census),
         "invalid action/safety census")
    untouched(cited, "original full-corpus citation packet")
    untouched(action, "R56 action-source crosswalk")
    need(cited.get("machine_authority") ==
         "STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY"
         and action.get("schema") ==
         "r56-private-unverified-action-source-crosswalk-v1"
         and action.get("machine_only") is True,
         "untrusted original reviewer authority")
    cc = cited.get("counts", {})
    need(type(cc) is dict and
         tuple(cc.get(k) for k in (
             "articles", "tools", "citations", "relationships",
             "base_fallback_relationships", "shared_url_groups_unreviewed")) == census,
         "full original cited corpus census drift")
    ac = action.get("counts", {})
    need(type(ac) is dict and
         tuple(ac.get(k) for k in (
             "all_original_action_work_orders",
             "uncited_consequential_action_blocks",
             "cited_consequential_action_blocks",
             "open_safety_exceptions_without_authenticated_clearance",
             "historical_machine_access_holds_not_current_link_failures")) == action_census,
         "original action/safety census drift")
    variant_source = getattr(lib, "source_variants", None)
    groups = getattr(lib, "crosswalk_groups", None)
    origins = getattr(lib, "article_origins", None)
    need(type(variant_source) is dict and type(groups) is dict and
         type(origins) is dict, "original contributor source identity maps missing")
    by_url, raw_keys, repeated_ids = defaultdict(list), {}, set()
    for sid, records in variant_source.items():
        need(type(sid) is str and sid and type(records) is list and records,
             "malformed contributor-specific source records")
        for record in records:
            need(type(record) is dict and record.get("id") == sid
                 and type(record.get("_origin")) is str and record["_origin"]
                 and type(record.get("url")) is str
                 and record["url"].startswith("https://"),
                 "invalid original record identity or URL")
            key = (record["_origin"], sid)
            need(key not in raw_keys, "duplicate contributor/source record identity")
            raw_keys[key] = record
            by_url[record["url"]].append(record)
        if len(records) > 1:
            repeated_ids.add(sid)
    shared = {url: rows for url, rows in by_url.items() if len(rows) > 1}
    need((len(raw_keys), len(by_url), len(shared), len(repeated_ids)) == inventory,
         "224 original records/186 URLs/30 shared groups/15 repeated IDs drift")
    need(set(shared) == set(groups), "global duplicate URL inventory lost or extended")
    for url, g in groups.items():
        need(type(g) is dict and g.get("url") == url
             and g.get("review_status") ==
                 "pending-human-source-and-reading-scope-review"
             and g.get("reviewer") is None and g.get("reviewed_on") is None,
             "shared URL group lost its unresolved safety state")
        rows = g.get("variants")
        need(type(rows) is list and len(rows) == len(shared[url]),
             "shared URL group lost original variants")
        group_keys = set()
        for row in rows:
            need(type(row) is dict and type(row.get("source")) is dict
                 and type(row.get("origin")) is str,
                 "malformed frozen shared-source row")
            source = row["source"]
            key = (row["origin"], source.get("id"))
            need(key in raw_keys and key not in group_keys and
                 canonical(source) == canonical({
                     k: v for k, v in raw_keys[key].items() if k != "_origin"
                 }), "source reading notes or contributor variant changed")
            group_keys.add(key)
        need(group_keys == {(r["_origin"], r["id"]) for r in shared[url]},
             "shared group silently omitted an uncited variant")
    cited_rows = cited.get("review_queue")
    need(type(cited_rows) is list and len(cited_rows) == census[3],
         "lost full article/source relationship queue")
    relationships, cited_by_url, fallbacks = {}, defaultdict(list), []
    claimed_occurrences = 0
    for row in cited_rows:
        need(type(row) is dict and type(row.get("slug")) is str
             and type(row.get("source_id")) is str
             and row["slug"] in origins,
             "cited relationship is orphaned")
        key = (row["slug"], row["source_id"])
        need(key not in relationships, "same relationship duplicated or collapsed")
        selected_key = (row.get("source_origin"), row["source_id"])
        selected = raw_keys.get(selected_key)
        need(selected is not None and
             row.get("article_origin") == origins[row["slug"]] and
             row.get("source_url") == selected["url"] and
             row.get("original_source_record_sha256") == digest(selected) and
             canonical(row.get("original_source_record_as_selected")) ==
                canonical(selected),
             "cited original full source/reading identity substituted")
        fallback = row["source_origin"] == "base" and origins[row["slug"]] != "base"
        need(row.get("base_fallback_requires_human_scope_review") is fallback and
             row.get("shared_url_group_requires_human_review") is
                 (selected["url"] in shared) and
             row.get("human_link_checked_by_this_gate") is False and
             row.get("human_claim_reviewed_by_this_gate") is False,
             "fallback/shared state or human clearance forged")
        occurrence = row.get("citation_occurrences")
        need(type(occurrence) is int and occurrence > 0 and
             type(row.get("all_citation_contexts_for_human_claim_review")) is list
             and len(row["all_citation_contexts_for_human_claim_review"]) == occurrence,
             "cited occurrence reading depth or repeated tokens lost")
        claimed_occurrences += occurrence
        relationships[key] = row
        cited_by_url[selected["url"]].append(row)
        if fallback:
            fallbacks.append(row)
    need(len(relationships) == census[3] and claimed_occurrences == census[2]
         and len(fallbacks) == census[4], "1,959 citations or 43 fallbacks lost")
    action_rows = action.get("original_unreviewed_action_rows")
    source_rows = action.get("original_unreviewed_action_source_rows")
    need(type(action_rows) is list and type(source_rows) is list and
         len(action_rows) == action_census[0],
         "action work orders truncated")
    action_ids = {}
    for row in action_rows:
        need(type(row) is dict and type(row.get("work_order_id_sha256")) is str
             and row["work_order_id_sha256"] not in action_ids
             and row.get("review_state") == "NOT_REVIEWED",
             "action work order missing/duplicated/approved")
        action_ids[row["work_order_id_sha256"]] = row
    action_links, action_by_url, action_by_relationship = [], defaultdict(list), defaultdict(list)
    for scope in source_rows:
        need(type(scope) is dict and
             scope.get("review_state") == "NOT_REVIEWED",
             "action source scope falsely reviewed")
        parent = action_ids.get(scope.get("work_order_id_sha256"))
        key = (scope.get("article"), scope.get("source_id"))
        cited_source = relationships.get(key)
        need(parent is not None and cited_source is not None
             and scope["article"] == parent["article"]
             and scope["block_ordinal"] == parent["block_ordinal"]
             and scope.get("source_contributor_origin") == cited_source["source_origin"]
             and scope.get("article_contributor_origin") == cited_source["article_origin"]
             and scope.get("original_url") == cited_source["source_url"]
             and scope.get("original_source_record_sha256") ==
                 cited_source["original_source_record_sha256"]
             and scope.get("original_source_use") ==
                 cited_source["article_source_use_as_recorded"]
             and scope.get("original_source_reading_scope") ==
                 cited_source["original_source_record_as_selected"].get("notes", "")
             and scope.get("original_source_supports_note") ==
                 cited_source["original_source_record_as_selected"].get("supports", "")
             and scope.get("base_fallback_requires_human_review") ==
                 cited_source["base_fallback_requires_human_scope_review"]
             and scope.get("shared_url_group_requires_human_review") ==
                 cited_source["shared_url_group_requires_human_review"],
             "consequential action re-bound to wrong article/source reading")
        action_links.append(scope)
        action_by_url[scope["original_url"]].append(scope)
        action_by_relationship[key].append(scope)
    require_sources = sum(int(row.get("source_readings_count", -1)) for row in action_rows)
    need(len(action_links) == require_sources,
         "one or more per-action source readings lost")
    full_groups = []
    for url in sorted(shared):
        variants = sorted(shared[url], key=lambda x:(x["_origin"], x["id"]))
        full_groups.append({
            "source_url_exact_no_canonicalization": url,
            "unreviewed_original_crosswalk_group": groups[url],
            "all_original_contributor_records": variants,
            "all_cited_relationships_not_only_high_risk": cited_by_url[url],
            "consequential_action_source_rows_if_any": action_by_url[url],
            "human_source_scope_review": "NOT_STARTED",
            "qualified_safety_review": "NOT_STARTED",
        })
    fallback_queue = []
    for row in sorted(fallbacks, key=lambda x: (x["slug"], x["source_id"])):
        fallback_queue.append({
            "full_original_fallback_relationship": row,
            "consequential_action_source_rows_if_any":
                action_by_relationship[(row["slug"], row["source_id"])],
            "human_source_scope_review": "NOT_STARTED",
            "qualified_safety_review": "NOT_STARTED",
        })
    result = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "machine_only": True,
        "parent_R25_cited_source_sha256": cited["fingerprint_sha256"],
        "parent_R56_action_source_sha256": action["fingerprint_sha256"],
        "counts": {
            "articles": census[0], "water_tools": census[1],
            "all_citation_occurrences": claimed_occurrences,
            "all_original_article_source_relationships": len(relationships),
            "all_global_shared_url_groups_even_uncited": len(full_groups),
            "all_base_fallback_source_relationships": len(fallback_queue),
            "all_high_consequence_action_orders": len(action_rows),
            "action_scoped_source_reading_rows": len(action_links),
            "shared_groups_with_no_high_consequence_action":
                sum(not group["consequential_action_source_rows_if_any"]
                    for group in full_groups),
            "fallbacks_with_no_high_consequence_action":
                sum(not case["consequential_action_source_rows_if_any"]
                    for case in fallback_queue),
        },
        "all_global_shared_url_groups_unreviewed": full_groups,
        "all_base_fallback_relationships_unreviewed": fallback_queue,
        "all_original_cited_relationships_unreviewed": cited_rows,
        "all_original_consequential_action_orders_unreviewed": action_rows,
        "all_original_action_source_rows_unreviewed": source_rows,
        "open_safety_exceptions_unreviewed":
            action["open_safety_exceptions_without_verified_article_mapping"],
        "historical_machine_access_holds_not_current_failures":
            action["historical_access_hold_queue"],
        "limitations": (
            "Original URL equality is not source support. A claim may be uncited "
            "in its action block yet supported elsewhere; flagged means machine "
            "triage only. Uncited global variants and fallbacks must not vanish. "
            "No live link visit, authenticated human identity, current source "
            "availability, medical/hazard safety, editorial QD or publication "
            "is established by this bridge."),
        **{flag: False for flag in FLAGS},
    }
    need(len(result["open_safety_exceptions_unreviewed"]) == action_census[3]
         and len(result["historical_machine_access_holds_not_current_failures"]) ==
             action_census[4], "original safety/access holds lost")
    result["fingerprint_sha256"] = digest(result)
    return result


def verify_bridge(lib, cited, action, result, *, census=CENSUS,
                  inventory=INVENTORY, action_census=ACTIONS):
    need(type(result) is dict and result == bridge(
        lib, cited, action, census=census, inventory=inventory,
        action_census=action_census),
        "source/citation/action bridge evidence changed or approval forged")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true",
                        help="reconcile original source inventory without writing")
    parser.add_argument("--write-private", action="store_true",
                        help="create exclusive ignored private review output only")
    args = parser.parse_args(argv)
    try:
        r54 = module("r54_action_review_export.py")
        r56 = module("r56_unreviewed_action_source_crosswalk.py")
        build = module("build.py")
        r25 = module("citation_fallback_review_gate.py")
        lib = build.Library(ROOT)
        original = r54.original_report(ROOT.parent)
        action = r56.crosswalk(original)
        r56.verify_crosswalk(original, action)
        cited = r25.audit(lib)
        result = bridge(lib, cited, action)
        verify_bridge(lib, cited, action, result)
        summary = {"schema": SCHEMA, "release_state": "HOLD",
                   "may_publish": False, "counts": result["counts"],
                   "fingerprint_sha256": result["fingerprint_sha256"],
                   "wrote_private_files": False}
        if args.write_private:
            folder_root = ROOT / "build"
            need(folder_root.is_dir() and not folder_root.is_symlink() and
                 folder_root.resolve() == folder_root.absolute(),
                 "ignored private build folder missing or redirected")
            folder = folder_root / ("r57-global-bridge-HOLD-" +
                                    result["fingerprint_sha256"][:20])
            folder.mkdir(mode=0o700, exist_ok=False)
            with (folder / "UNVERIFIED_GLOBAL_SOURCE_ACTION_BRIDGE.json").open(
                    "x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False,
                          sort_keys=True, indent=2, allow_nan=False)
                handle.write("\n")
            summary["wrote_private_files"] = True
            summary["private_location"] = str(folder.relative_to(ROOT.parent))
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (BridgeHold, ValueError, OSError, KeyError, TypeError, AttributeError,
            ImportError, OverflowError) as exc:
        print("R57 PRIVATE GLOBAL SOURCE BRIDGE HOLD: " + str(exc),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
