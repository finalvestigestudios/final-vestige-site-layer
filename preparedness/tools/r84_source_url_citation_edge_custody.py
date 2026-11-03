#!/usr/bin/env python3
"""R84 PRIVATE HOLD: four-stage exact source-URL and citation-edge custody.

This diagnostic joins R83 visible citation placements to R82's complete original
source readings. All URLs and source identities remain literal and unverified.
It is NEVER a link checker, claim-support verdict, safety approval or publisher.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import io
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

SCHEMA = "r84-four-stage-literal-source-url-citation-edge-hold-v1"
STAGES = ("frozen", "integrated", "current", "rc")
REVIEW = "NOT_REVIEWED"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
BAD_PERCENT = re.compile(r"%(?![0-9A-Fa-f]{2})")


class Hold(ValueError):
    """Source and citation custody has failed closed."""


def need(ok, reason):
    if not ok:
        raise Hold(reason)


def parent_modules():
    path = Path(__file__).with_name("r83_citation_placement_context_custody.py")
    need(path.is_file() and not path.is_symlink(), "R83 exact parent absent")
    spec = importlib.util.spec_from_file_location("r84_r83", path)
    need(spec is not None and spec.loader is not None, "R83 unavailable")
    r83 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r83)
    return r83, r83.parent_module()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def url_observation(literal):
    """Diagnostic clues only. NEVER canonicalize, merge or validate a URL."""
    need(type(literal) is str, "source URL not a literal string")
    flags = []
    if not literal or any(ord(c) <= 32 or ord(c) == 127 for c in literal):
        flags.append("EMPTY_SPACE_OR_CONTROL_REVIEW")
    if "\\" in literal:
        flags.append("BACKSLASH_REVIEW")
    if BAD_PERCENT.search(literal):
        flags.append("MALFORMED_PERCENT_ESCAPE_REVIEW")
    if any(ord(c) > 127 for c in literal):
        flags.append("NONASCII_LITERAL_REVIEW")
    try:
        parsed = urlsplit(literal)
        scheme = parsed.scheme
        authority = parsed.netloc
        hostname = parsed.hostname
        try:
            port = parsed.port
        except ValueError:
            port = None
            flags.append("INVALID_PORT_REVIEW")
        if scheme != "https":
            flags.append("NOT_LITERAL_HTTPS_REVIEW")
        if not authority or not hostname:
            flags.append("NO_PARSEABLE_AUTHORITY_REVIEW")
        if "@" in authority:
            flags.append("AUTHORITY_USERINFO_REVIEW")
        if "%" in authority:
            flags.append("ENCODED_AUTHORITY_REVIEW")
        if authority.count("@") > 1:
            flags.append("MULTIPLE_USERINFO_DELIMITERS_REVIEW")
        if hostname and hostname.endswith("."):
            flags.append("HOST_TRAILING_DOT_REVIEW")
        if port is not None:
            flags.append("EXPLICIT_PORT_REVIEW")
        if hostname:
            try:
                ip = ipaddress.ip_address(hostname)
                flags.append("IP_ADDRESS_HOST_REVIEW")
                if not ip.is_global:
                    flags.append("NON_GLOBAL_IP_HOST_REVIEW")
            except ValueError:
                if hostname in ("localhost",) or hostname.endswith((".local", ".internal")):
                    flags.append("LOCAL_HOSTNAME_REVIEW")
        if parsed.fragment:
            flags.append("URL_FRAGMENT_REVIEW")
        if parsed.query:
            flags.append("URL_QUERY_REVIEW")
        if "/../" in parsed.path or parsed.path.startswith("../") or "/./" in parsed.path:
            flags.append("DOT_SEGMENT_PATH_REVIEW")
        # Full original URL is the only identity; parsed fields are observations.
        fields = {"scheme": scheme, "authority": authority, "hostname": hostname,
                  "explicit_port": port, "path": parsed.path,
                  "query": parsed.query, "fragment": parsed.fragment}
    except ValueError:
        flags.append("UNPARSEABLE_URL_REVIEW")
        fields = {"scheme": None, "authority": None, "hostname": None,
                  "explicit_port": None, "path": None,
                  "query": None, "fragment": None}
    return {"literal_URL_UNVERIFIED_UNCHANGED": literal,
            "parsed_observation_NOT_LINK_CHECK": fields,
            "review_cues_NOT_VERDICTS": sorted(set(flags)),
            "human_link_review": REVIEW, "may_publish": False}


def catalog(fragments):
    """All source records and literal URL collisions remain separate."""
    need(type(fragments) is list, "complete R82 fragments required")
    rows, index = [], {}
    for frag in fragments:
        need(type(frag) is dict and frag.get("stage") in STAGES
             and type(frag.get("origin")) is str,
             "malformed fragment custody")
        stage, origin = frag["stage"], frag["origin"]
        for source in frag["source_readings_UNABRIDGED"]:
            sid = source["raw_source_id"]
            fingerprint = source["reading_sha256"]
            original = source["complete_reading_UNABRIDGED_NOT_APPROVED"]
            need(type(sid) is str and sid and type(fingerprint) is str
                 and HEX64.fullmatch(fingerprint) is not None,
                 "incomplete literal source identity")
            need(type(original) is dict and original.get("id") == sid
                 and sha(canonical(original)) == fingerprint,
                 "source reading altered or reidentified")
            key = (stage, origin, sid, fingerprint)
            need(key not in index, "duplicate exact source-record identity")
            observation = url_observation(original.get("url"))
            row = {"stage": stage, "origin": origin, "literal_source_ID": sid,
                   "reading_sha256": fingerprint,
                   "reading_ordinal": source["ordinal"],
                   "complete_original_reading_UNABRIDGED_NOT_APPROVED": original,
                   "url_observation": observation,
                   "human_source_review": REVIEW, "qualified_safety_review": REVIEW,
                   "may_publish": False}
            index[key] = row
            rows.append(row)
    rows.sort(key=lambda r: (STAGES.index(r["stage"]), r["origin"],
                             r["reading_ordinal"], r["literal_source_ID"]))
    # Collision groups use exact byte-for-byte URL strings only; different
    # origin/ID/readings are never collapsed or silently reconciled.
    groups = defaultdict(list)
    for row in rows:
        groups[(row["stage"], row["url_observation"][
            "literal_URL_UNVERIFIED_UNCHANGED"])].append({
                "origin": row["origin"], "literal_source_ID": row["literal_source_ID"],
                "reading_sha256": row["reading_sha256"],
                "reading_ordinal": row["reading_ordinal"]})
    collisions = [{
        "stage": stage, "exact_literal_URL_UNVERIFIED": url,
        "distinct_origin_scoped_readings_NOT_MERGED": sorted(members,
            key=lambda x: (x["origin"], x["literal_source_ID"],
                           x["reading_sha256"], x["reading_ordinal"])),
        "human_identity_reconciliation": REVIEW, "may_publish": False
    } for (stage, url), members in sorted(groups.items())
      if len(members) > 1]
    return rows, index, collisions


def citation_edge(anchor, index, stage, article_origin, article_path):
    """Preserve the R83 anchor and every exact R82 scoped source variant."""
    need(stage in STAGES and type(article_origin) is str
         and type(article_path) is str and type(anchor) is dict,
         "incomplete citation context")
    sid = anchor["raw_source_id"]
    variants = anchor["source_candidates_NOT_ALIASED"]
    need(type(sid) is str and sid and type(variants) is list,
         "missing raw citation/source variant set")
    seen, matches = set(), []
    cues = []
    for variant in variants:
        need(type(variant) is dict and variant["literal_source_id"] == sid
             and type(variant["origin"]) is str
             and type(variant["reading_sha256"]) is str,
             "candidate identity does not match literal citation")
        key = (stage, variant["origin"], sid, variant["reading_sha256"])
        need(key not in seen, "repeated source edge masquerading as variant")
        seen.add(key)
        need(key in index, "candidate source reading not in sealed fragments")
        record = index[key]
        matches.append({
            "origin": record["origin"], "literal_source_ID": sid,
            "reading_sha256": record["reading_sha256"],
            "literal_URL_UNVERIFIED_UNCHANGED": record["url_observation"][
                "literal_URL_UNVERIFIED_UNCHANGED"],
            "URL_review_cues_NOT_VERDICTS": record["url_observation"][
                "review_cues_NOT_VERDICTS"],
            "human_claim_support": REVIEW, "qualified_safety_review": REVIEW})
        cues.extend(record["url_observation"]["review_cues_NOT_VERDICTS"])
    if not matches:
        need(anchor["source_scope_state"] == "OUTSIDE_SEVEN_FRAGMENT_SCOPE",
             "citation candidates silently removed")
        cues.append("OUTSIDE_SEVEN_FRAGMENT_SCOPE_REVIEW")
    elif len(matches) > 1:
        need(anchor["source_scope_state"] == "MULTIPLE_ORIGIN_VARIANTS_UNRESOLVED",
             "multi-origin variant incorrectly resolved")
        cues.append("MULTIPLE_SOURCE_VARIANTS_REVIEW")
    else:
        need(anchor["source_scope_state"] ==
             "ONE_SCOPED_CANDIDATE_NOT_CLAIM_PROOF",
             "single source not tracked without approval")
    if anchor["scope_state"] != "VISIBLE_CONTAINER_NOT_SUPPORT_PROOF":
        cues.append("NONVISIBLE_OR_UNMAPPED_CITATION_REVIEW")
    # Complete unabridged anchor remains sealed in R83 and the full original
    # reading in the catalog above. These immutable digests link both, avoiding
    # duplicated/shortened context or silently substituting another source.
    return {"stage": stage, "article_origin": article_origin,
            "article_path": article_path, "citation_ordinal": anchor["ordinal"],
            "literal_raw_source_ID": sid,
            "R83_complete_anchor_sha256": sha(canonical(anchor)),
            "R83_complete_container_text_sha256": sha((
                anchor["complete_container_text_UNABRIDGED"] or "").encode("utf-8"))
                if anchor["complete_container_text_UNABRIDGED"] is not None else None,
            "exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED": matches,
            "source_scope_state": anchor["source_scope_state"],
            "review_cues_NOT_VERDICTS": sorted(set(cues)),
            "human_claim_support": REVIEW, "qualified_safety_review": REVIEW,
            "may_publish": False}


def construct(r82_report, r83_report):
    """R82 and R83 verification is mandatory; no digest-only acceptance."""
    r83, r82 = parent_modules()
    r82.verify(r82_report)
    r83.verify(r83_report, r82_report)
    need(r82_report.get("release_state") == "HOLD"
         and r83_report.get("release_state") == "HOLD"
         and r82_report.get("may_publish") is False
         and r83_report.get("may_publish") is False, "parent release not HOLD")
    rows, index, collisions = catalog(
        r82_report["all_four_snapshot_source_fragments_UNABRIDGED"])
    need(len(rows) == sum(x["source_count"] for x in r82_report[
        "all_four_snapshot_source_fragments_UNABRIDGED"]), "source reading lost")
    edges = []
    for packet in r83_report["all_29_four_stage_citation_context_packets_UNABRIDGED"]:
        for stage in STAGES:
            for anchor in packet["four_snapshot_citation_anchors_NOT_APPROVED"][stage]:
                edges.append(citation_edge(anchor, index, stage, packet["origin"],
                                           packet["path"]))
    need(len(edges) == r83_report["counts"]["four_stage_citation_anchors"],
         "citation/source crosswalk lost an occurrence")
    seen = set()
    for edge in edges:
        identity = (edge["stage"], edge["article_origin"],
                    edge["article_path"], edge["citation_ordinal"])
        need(identity not in seen, "same citation twice in custody crosswalk")
        seen.add(identity)
    flagged = sum(bool(e["review_cues_NOT_VERDICTS"]) for e in edges)
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "may_publish": False, "medical_safety_approved": False,
        "human_source_approvals": 0, "human_claim_approvals": 0,
        "qualified_safety_approvals": 0, "independent_QD_approvals": 0,
        "R82_unabridged_provenance_sha256": r82_report["sha256_seal"],
        "R83_unabridged_citation_context_sha256": r83_report["sha256_seal"],
        "separate_RC_sha": r82_report["separate_RC_sha"],
        "counts": {
            "source_reading_snapshots": len(rows),
            "complete_citation_source_crosswalk_rows": len(edges),
            "citation_edges_to_known_scoped_variants": sum(len(
                e["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"]) for e in edges),
            "literal_URL_duplicate_groups_NOT_MERGED": len(collisions),
            "citation_rows_with_review_cues_NOT_ERRORS": flagged,
            "citation_rows_outside_seven_fragment_scope": sum(
                e["source_scope_state"] == "OUTSIDE_SEVEN_FRAGMENT_SCOPE"
                for e in edges),
            "source_rows_with_URL_observation_cues": sum(bool(
                r["url_observation"]["review_cues_NOT_VERDICTS"]) for r in rows),
        },
        "all_complete_four_stage_source_readings_UNABRIDGED": rows,
        "exact_literal_URL_collision_groups_NOT_MERGED": collisions,
        "all_four_stage_literal_citation_to_source_edges_NOT_APPROVED": edges,
    }
    report["sha256_seal"] = sha(canonical(report))
    return report


def verify(report, r82_report, r83_report):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == "HOLD"
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(report.get(key) == 0 for key in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "R84 approval/publication state forged")
    need(report.get("sha256_seal") == sha(canonical({
        k: v for k, v in report.items() if k != "sha256_seal"})),
        "R84 ledger seal broken")
    need(report == construct(r82_report, r83_report),
         "R84 cannot reproduce exact original source/citation custody")


def reviewer_csv(report, r82_report, r83_report):
    verify(report, r82_report, r83_report)
    r82 = parent_modules()[1]
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["stage", "article_origin", "article", "citation_ordinal",
                     "raw_source_ID", "review_cues_NOT_VERDICTS",
                     "human_source_and_claim_review", "release"])
    for row in report["all_four_stage_literal_citation_to_source_edges_NOT_APPROVED"]:
        if row["review_cues_NOT_VERDICTS"]:
            writer.writerow([row["stage"], r82.safe_csv(row["article_origin"]),
                             r82.safe_csv(row["article_path"]), row["citation_ordinal"],
                             r82.safe_csv(row["literal_raw_source_ID"]),
                             ";".join(row["review_cues_NOT_VERDICTS"]), REVIEW, "HOLD"])
    return out.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-stdout", action="store_true",
                        help="private one-way review queue; NEVER public upload")
    args = parser.parse_args(argv)
    r83, r82 = parent_modules()
    parent = r82.live_report()
    citations = r83.construct(parent)
    report = construct(parent, citations)
    if args.csv_stdout:
        print(reviewer_csv(report, parent, citations), end="")
    else:
        print(json.dumps({"schema": SCHEMA, "release": "HOLD",
                          "counts": report["counts"], "R84_sha256_seal":
                          report["sha256_seal"], "human_approvals": 0,
                          "medical_safety_approved": False, "may_publish": False,
                          "CMS_and_WordPress_writes": 0}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Hold, ValueError, TypeError, KeyError, OSError) as exc:
        raise SystemExit("R84 FAILED CLOSED — " + str(exc))
