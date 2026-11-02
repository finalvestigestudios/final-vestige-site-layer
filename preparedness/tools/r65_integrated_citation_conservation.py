#!/usr/bin/env python3
"""R65 PRIVATE HOLD: all 35 integrated citation slugs vs 29 frozen/proposed contributors.

Preserves original R58 source readings (including the six outside original
seven clusters) and both R61 contributor versions. Exact token pairing is
structural only, never proof of claim support or safety clearance.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r65-private-35-article-citation-conservation-v1"
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
EXPECTED = (35, 29, 1959, 1709, 1728, 6)
SHA = re.compile(r"[0-9a-f]{64}\Z")


class ConservationHold(ValueError):
    """Missing or falsified historical research and publication HOLD."""


def need(value, message):
    if not value:
        raise ConservationHold(message)


def digest(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def valid_sha(value):
    return type(value) is str and SHA.fullmatch(value) is not None


def held(doc, name):
    need(type(doc) is dict and doc.get("release_state") == "HOLD" and
         doc.get("machine_only") is True and
         all(doc.get(field) is False for field in HOLD) and
         valid_sha(doc.get("fingerprint_sha256")) and
         digest({k: v for k, v in doc.items() if k != "fingerprint_sha256"}) ==
         doc["fingerprint_sha256"],
         name + " original evidence or release state was changed")


def construct(original, lineage, dependency, *, expected=EXPECTED):
    """Synthetic-friendly deterministic core. Only report() verifies BOTH original roots."""
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(i) is int and i >= 0 for i in expected) and
         expected[0] == expected[1] + expected[5], "invalid census contract")
    for title, obj in (("R58 integrated", original),
                       ("R61 contributor", lineage),
                       ("R64 dependency", dependency)):
        held(obj, title)
    need(original.get("schema") == "r58-private-exact-citation-occurrence-docket-v1"
         and lineage.get("schema") == "r61-private-contributor-two-version-lineage-v1"
         and dependency.get("schema") ==
         "r64-private-article-source-dependency-coverage-v1"
         and dependency.get("parent_R61_sha256") == lineage["fingerprint_sha256"],
         "upstream schema or contributor provenance fingerprint changed")
    citations = original.get("individual_original_citation_occurrence_review_queue")
    articles = lineage.get("per_article_citation_and_context_lineage_NOT_REVIEWED")
    links = dependency.get("article_source_dependency_work_orders_ALL_NOT_APPROVED")
    need(all(type(x) is list for x in (citations, articles, links)) and
         len(citations) == expected[2] and len(articles) == expected[1],
         "integrated citation or contributor article census missing")
    need(tuple(original.get("counts", {}).get(k) for k in
               ("original_articles", "exact_citation_occurrence_work_orders")) ==
         (expected[0], expected[2]) and
         original["counts"].get("water_tools") == 1 and
         tuple(lineage.get("counts", {}).get(k) for k in
               ("original_contributor_articles", "old_citation_occurrences",
                "observed_citation_occurrences_UNVERIFIED")) ==
         expected[1:4:1][:0] + expected[1:2] + expected[3:5],
         "frozen 35/29 article or 1959/1709/1728 citation census changed")

    by_slug, seen_offsets, seen_ids, ordinals = defaultdict(list), set(), set(), defaultdict(list)
    for row in citations:
        need(type(row) is dict and
             all(row.get(k) == "NOT_REVIEWED" for k in
                 ("human_source_retrieval_state", "human_claim_support_state",
                  "qualified_hazard_safety_state")),
             "original citation lacks open human/safety review")
        token = row.get("exact_original_token_identity")
        record = row.get("original_unabridged_contributor_source_record")
        relation = row.get("original_unabridged_article_source_relationship")
        need(type(token) is dict and type(record) is dict and type(relation) is dict,
             "complete original citation/source reading is missing")
        slug, sid, origin = token.get("slug"), token.get("source_id"), token.get("source_origin")
        offset = token.get("token_offset_codepoints_in_original_html")
        ordinal = token.get("citation_ordinal_within_article_source")
        work_id = row.get("citation_occurrence_work_order_id_sha256")
        need(type(slug) is str and bool(slug) and type(sid) is str and bool(sid)
             and type(origin) is str and bool(origin) and
             type(offset) is int and offset >= 0 and
             type(ordinal) is int and ordinal > 0 and valid_sha(work_id) and
             valid_sha(token.get("frozen_article_html_sha256")) and
             valid_sha(token.get("original_source_record_sha256")) and
             token["original_source_record_sha256"] == digest(record) and
             record.get("id") == sid and record.get("_origin") == origin and
             relation.get("slug") == slug and relation.get("source_id") == sid and
             relation.get("source_origin") == origin and
             type(row.get("original_unabridged_visible_context")) is str,
             "original citation/source identity inconsistent")
        need((slug, offset) not in seen_offsets and work_id not in seen_ids,
             "duplicate original citation token offset/work order")
        seen_offsets.add((slug, offset))
        seen_ids.add(work_id)
        ordinals[(slug, sid)].append(ordinal)
        by_slug[slug].append(row)
    need(len(by_slug) == expected[0], "integrated original citation-bearing slug census mismatch: observed " + str(len(by_slug)) + ", expected " + str(expected[0]) + "; slugs=" + repr(sorted(by_slug)))
    for key, value in ordinals.items():
        need(sorted(value) == list(range(1, len(value) + 1)),
             "lost per-source citation ordinal " + repr(key))

    contributors, frozen_count, proposed_count = {}, 0, 0
    for row in articles:
        need(type(row) is dict and row.get("review_state") == "NOT_REVIEWED",
             "contributor article falsely approved")
        slug, cluster = row.get("slug"), row.get("cluster")
        need(type(slug) is str and slug in by_slug and slug not in contributors
             and type(cluster) is str and bool(cluster),
             "duplicate or orphan contributor article")
        for version in ("frozen", "observed"):
            item = row["versions"][version]
            ts = item["citation_occurrences_in_original_order"]
            need(valid_sha(item.get("body_sha256")) and type(ts) is list and
                 type(item.get("full_source_use_mapping_UNABRIDGED")) is dict,
                 "contributor article text/citation/source-use lost")
            offsets = []
            for token in ts:
                need(type(token.get("source_id")) is str and bool(token["source_id"])
                     and type(token.get("offset_codepoints")) is int and
                     token["offset_codepoints"] >= 0 and
                     type(token.get("unabridged_local_context")) is str and
                     token.get("human_claim_support_state") == "NOT_REVIEWED",
                     "incomplete unreviewed frozen/proposed contributor token")
                offsets.append(token["offset_codepoints"])
            need(offsets == sorted(set(offsets)), "contributor citation offset collision")
        frozen_count += len(row["versions"]["frozen"]["citation_occurrences_in_original_order"])
        proposed_count += len(row["versions"]["observed"]["citation_occurrences_in_original_order"])
        contributors[slug] = row
    need((frozen_count, proposed_count) == expected[3:5],
         "original/proposed contributor citations were lost or multiplied")

    deps = defaultdict(dict)
    for dep in links:
        need(type(dep) is dict and dep.get("human_claim_support") == "NOT_REVIEWED"
             and dep.get("qualified_safety_review") == "NOT_REVIEWED"
             and valid_sha(dep.get("work_order_sha256")),
             "article/source relationship falsely verified")
        slug, sid = dep["article_slug"], dep["source_id"]
        need(slug in contributors and dep["article_cluster"] == contributors[slug]["cluster"]
             and sid not in deps[slug], "dependency belongs to wrong source or contributor")
        deps[slug][sid] = dep
    need(len(deps) == expected[1], "missing R64 article/source dependency groups")
    for slug, article in contributors.items():
        required = set()
        for version in ("frozen", "observed"):
            item = article["versions"][version]
            required.update(item["full_source_use_mapping_UNABRIDGED"])
            required.update(c["source_id"] for c in
                            item["citation_occurrences_in_original_order"])
        need(set(deps[slug]) == required, "source-use or citation dependency disappeared")
        for sid, dep in deps[slug].items():
            for version in ("frozen", "observed"):
                item = article["versions"][version]
                detail = dep["versions"][version]
                hits = [x["offset_codepoints"] for x in
                        item["citation_occurrences_in_original_order"]
                        if x["source_id"] == sid]
                observed_hits = [x["offset_codepoints"] for x in
                                 detail["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]]
                need(hits == observed_hits and
                     detail["source_use_present"] ==
                     (sid in item["full_source_use_mapping_UNABRIDGED"]) and
                     detail["source_use_note_UNABRIDGED_NOT_SUPPORT_PROOF"] ==
                     item["full_source_use_mapping_UNABRIDGED"].get(sid),
                     "R64 dependency lost original unabridged source-use or token position")

    result_rows, flag_counts = [], Counter()
    paired, unpaired = 0, 0
    for slug in sorted(by_slug):
        cited = sorted(by_slug[slug], key=lambda row: row[
            "exact_original_token_identity"]["token_offset_codepoints_in_original_html"])
        html_shas = {x["exact_original_token_identity"]["frozen_article_html_sha256"]
                     for x in cited}
        need(len(html_shas) == 1, "original article citation records disagree on HTML bytes")
        original_tokens = [{
            "source_id": x["exact_original_token_identity"]["source_id"],
            "original_codepoint_offset": x["exact_original_token_identity"][
                "token_offset_codepoints_in_original_html"],
            "source_origin": x["exact_original_token_identity"]["source_origin"],
            "R58_work_order_sha256": x["citation_occurrence_work_order_id_sha256"],
            "unabridged_original_visible_context_NOT_SUPPORT_PROOF":
                x["original_unabridged_visible_context"],
            "unabridged_original_source_reading_NOT_HUMAN_CHECKED":
                x["original_unabridged_contributor_source_record"],
            "unabridged_original_relationship_NOT_HUMAN_CHECKED":
                x["original_unabridged_article_source_relationship"],
        } for x in cited]
        flags, contributor = set(), None
        if slug in contributors:
            row = contributors[slug]
            versions = row["versions"]
            frozen = versions["frozen"]
            observed = versions["observed"]
            old_tokens = frozen["citation_occurrences_in_original_order"]
            new_tokens = observed["citation_occurrences_in_original_order"]
            integrated_seq = [(x["source_id"], x["original_codepoint_offset"])
                              for x in original_tokens]
            frozen_seq = [(x["source_id"], x["offset_codepoints"]) for x in old_tokens]
            observed_seq = [(x["source_id"], x["offset_codepoints"]) for x in new_tokens]
            if set(html_shas) != {frozen["body_sha256"]}:
                flags.add("INTEGRATED_VS_CONTRIBUTOR_FROZEN_HTML_BYTES_DIFFER")
            if [x[0] for x in integrated_seq] != [x[0] for x in frozen_seq]:
                flags.add("INTEGRATED_VS_FROZEN_CITATION_ID_SEQUENCE_DIFFER")
            if integrated_seq != frozen_seq:
                flags.add("INTEGRATED_VS_FROZEN_CITATION_OFFSETS_DIFFER")
            if frozen["body_sha256"] != observed["body_sha256"]:
                flags.add("CONTRIBUTOR_BODY_CHANGED_UNREVIEWED")
            if frozen_seq != observed_seq:
                flags.add("CONTRIBUTOR_CITATIONS_CHANGED_UNREVIEWED")
            if frozen.get("metadata_sha256") != observed.get("metadata_sha256"):
                flags.add("CONTRIBUTOR_METADATA_CHANGED_UNREVIEWED")
            if any(x["source_origin"] not in ("base", row["cluster"])
                   for x in original_tokens):
                flags.add("INTEGRATED_SELECTED_SOURCE_FROM_DIFFERENT_CLUSTER")
            # Pair ONLY if the entire frozen HTML bytes agree, source ID matches,
            # and codepoint offset is exact; never match on URL, fuzzy text or alias.
            original_index = ({(x["source_id"], x["original_codepoint_offset"]):
                               x["R58_work_order_sha256"] for x in original_tokens}
                              if html_shas == {frozen["body_sha256"]} else {})
            matches = []
            for number, token in enumerate(old_tokens, 1):
                original_id = original_index.get((token["source_id"],
                                                  token["offset_codepoints"]))
                if original_id is not None:
                    matches.append({"frozen_contributor_token_ordinal": number,
                                    "original_R58_work_order_sha256": original_id,
                                    "relation": "EXACT_HTML_ID_OFFSET_NOT_CLAIM_SUPPORT"})
            paired += len(matches)
            unpaired += len(old_tokens) - len(matches)
            if len(matches) != len(old_tokens) or len(matches) != len(original_tokens):
                flags.add("UNPAIRED_CITATION_REQUIRES_HUMAN_RECONCILIATION")
            contributor = {
                "original_cluster": row["cluster"],
                "old_and_proposed_article_versions_UNABRIDGED": versions,
                "all_article_source_dependencies_UNABRIDGED": [
                    deps[slug][sid] for sid in sorted(deps[slug])],
                "exact_token_candidate_pairs_NOT_CLAIM_SUPPORT": matches,
                "frozen_citations": len(old_tokens),
                "proposed_citations_UNREVIEWED": len(new_tokens),
            }
        else:
            flags.add("INTEGRATED_ONLY_SIX_ARTICLES_OUTSIDE_SEVEN_R14_CLUSTERS")
        if not flags:
            flags.add("UNCHANGED_STRUCTURAL_REFERENCES_NOT_VERIFIED")
        flag_counts.update(flags)
        result_rows.append({
            "article_slug": slug,
            "integrated_article_html_sha256": next(iter(html_shas)),
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED": original_tokens,
            "frozen_and_proposed_contributor_custody_OR_NULL": contributor,
            "review_flags_NOT_SAFETY_VERDICTS": sorted(flags),
            "human_source_review": "NOT_REVIEWED",
            "qualified_safety_review": "NOT_REVIEWED",
        })
    need(len(result_rows) == expected[0] and
         sum(len(x["all_original_integrated_citation_and_reading_evidence_UNABRIDGED"])
             for x in result_rows) == expected[2] and
         sum(x["frozen_and_proposed_contributor_custody_OR_NULL"] is None
             for x in result_rows) == expected[5],
         "original integrated citation/contributor evidence disappeared")
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD", "machine_only": True,
        "original_R58_fingerprint_sha256": original["fingerprint_sha256"],
        "frozen_proposed_R61_fingerprint_sha256": lineage["fingerprint_sha256"],
        "original_dependency_R64_fingerprint_sha256": dependency["fingerprint_sha256"],
        "all_35_original_article_review_work_orders_NOT_APPROVED": result_rows,
        "counts": {
            "integrated_articles": expected[0], "original_water_planning_tools": 1,
            "integrated_citation_occurrences": expected[2],
            "frozen_contributor_articles": expected[1],
            "frozen_contributor_citations": frozen_count,
            "proposed_contributor_citations_UNREVIEWED": proposed_count,
            "six_other_integrated_articles": expected[5],
            "exact_R58_to_frozen_R61_candidate_tokens_NOT_CLAIM_SUPPORT": paired,
            "unpaired_frozen_contributor_tokens_NEED_HUMAN_REVIEW": unpaired,
            "review_flags_NOT_SAFETY_VERDICTS": dict(sorted(flag_counts.items())),
        },
        "limitations": ("The original 35-article evidence is preserved alongside both "
                        "29-article versions. URL/source-ID equality is NOT proof of "
                        "citation support, verified source access, safe advice, reviewer "
                        "approval, or inclusion of proposed contributor changes."),
        **{field: False for field in HOLD},
    }
    report["fingerprint_sha256"] = digest(report)
    return report


def _module(filename):
    path = Path(__file__).with_name(filename)
    need(path.is_file() and not path.is_symlink(), "required original gate missing: " + filename)
    spec = importlib.util.spec_from_file_location("r65_" + filename.replace(".", "_"), path)
    need(spec is not None and spec.loader is not None, "cannot load original gate")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def report(bridge, original, lineage, docket_r62, source_r63, dependency_r64):
    """Production safety boundary: regenerate and reverify independent R58 and R64."""
    r58 = _module("r58_exact_citation_occurrence_docket.py")
    r64 = _module("r64_article_source_dependency_review.py")
    try:
        r58.verify_docket(bridge, original)
        r64.verify_report(dependency_r64, lineage, docket_r62, source_r63)
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise ConservationHold("R58 or R64 original source custody failed") from error
    return construct(original, lineage, dependency_r64)


def real_evidence(repo_root, remote):
    need(re.fullmatch(r"[a-zA-Z0-9_-]+", remote) is not None,
         "unsafe Git remote name")
    r57 = _module("r57_global_citation_action_bridge.py")
    r58 = _module("r58_exact_citation_occurrence_docket.py")
    r64 = _module("r64_article_source_dependency_review.py")
    r54 = r57.module("r54_action_review_export.py")
    r56 = r57.module("r56_unreviewed_action_source_crosswalk.py")
    build = r57.module("build.py")
    r25 = r57.module("citation_fallback_review_gate.py")
    lib = build.Library(ROOT)
    old = r54.original_report(ROOT.parent)
    action = r56.crosswalk(old)
    r56.verify_crosswalk(old, action)
    cited = r25.audit(lib)
    bridge = r57.bridge(lib, cited, action)
    r57.verify_bridge(lib, cited, action, bridge)
    original = r58.create_docket(bridge)
    r58.verify_docket(bridge, original)
    parent = Path(__file__).with_name("r61_contributor_version_source_lineage.py")
    need(parent.is_file() and not parent.is_symlink(),
         "original Git-object contributor gate absent")
    try:
        process = subprocess.run(
            [sys.executable, "-I", str(parent), "--repo-root", str(repo_root),
             "--remote", remote],
            check=False, capture_output=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ConservationHold("fresh contributor Git object check unavailable") from error
    need(process.returncode == 0 and 0 < len(process.stdout) < 48_000_000,
         "fresh R61 Git-object custody failed closed")
    try:
        lineage = r64.r62.strict_load(process.stdout.decode("utf-8", "strict"))
        docket = r64.r62.make_report(lineage)
        sources = r64.r63.make_report(lineage, docket)
        dependency = r64.make_report(lineage, docket, sources)
    except (UnicodeError, ValueError, TypeError, KeyError) as error:
        raise ConservationHold("R61/R62/R63/R64 regeneration rejected") from error
    return bridge, original, lineage, docket, sources, dependency


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT.parent)
    parser.add_argument("--remote", default="origin")
    opts = parser.parse_args(argv)
    try:
        evidence = real_evidence(opts.repo_root, opts.remote)
        packet = report(*evidence)
        need(packet == report(*evidence), "non-deterministic integrated evidence")
        print(json.dumps({"schema": SCHEMA, "release_state": "HOLD",
                          "may_publish": False, "wrote_private_files": False,
                          "counts": packet["counts"],
                          "fingerprint_sha256": packet["fingerprint_sha256"]},
                         sort_keys=True, ensure_ascii=False))
        return 0
    except (ConservationHold, ValueError, OSError, KeyError, TypeError,
            UnicodeError, AttributeError, ImportError) as error:
        print("R65 ORIGINAL FULL-CORPUS SOURCE CONSERVATION HOLD: " + str(error),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
