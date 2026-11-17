#!/usr/bin/env python3
"""R446: independent exact-original adjudication packet integrity, always HARD HOLD.

Read-only, offline. Does not approve sources, advice, QD, publication, sales or offers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ORIGINAL_BLOB = "86d22a1d504c93db7689b914e2202a7845b648e2"
RELEASE = "DRAFT_HARD_HOLD"
COUNTS = {"articles":35,"source_ids":203,"occurrences":280,"exact_urls":181,
          "shared_url_groups":17,"scope_disputes":5,"forks":9,"branches":9}
PROTECTED = ("qualified_review_approved","publishable","safety_approved","merchant_offer_verified")


def unique_pairs(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate JSON key: " + name)
        result[name] = value
    return result


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()


def check(original: object, packet: object, raw: bytes | None,
          current_heads: object) -> dict:
    errors = []
    def fail(code): errors.append(code)
    if not isinstance(original,dict): original={}; fail("ORIGINAL_NOT_OBJECT")
    if not isinstance(packet,dict): packet={}; fail("PACKET_NOT_OBJECT")
    if raw is None or not isinstance(raw,bytes) or git_blob(raw)!=ORIGINAL_BLOB:
        fail("EXTERNAL_ORIGINAL_BLOB_PROOF_MISSING")
    if original.get("schema")!=1 or original.get("issue")!=136 or original.get("parent_conversion_issue")!=820:
        fail("ORIGINAL_IDENTITY_CHANGED")
    if original.get("release_state")!=RELEASE or any(original.get(k) is not False for k in
            ("publication_approved","qualified_safety_approved","automatic_variant_selection","merchant_offer_verified")):
        fail("ORIGINAL_RELEASE_AUTHORITY_CHANGED")
    if packet.get("schema")!="R446_ORIGINAL_ADJUDICATION_REVIEW_ONLY_v1" or packet.get("release_state")!=RELEASE:
        fail("PACKET_IDENTITY_CHANGED")
    if any(packet.get(k) is not False for k in PROTECTED):
        fail("FALSE_PACKET_APPROVAL")
    if packet.get("original_docket",{}).get("git_blob")!=ORIGINAL_BLOB:
        fail("PACKET_DOES_NOT_PIN_ORIGINAL")
    pins=original.get("branch_pins",[])
    pin_map={p.get("branch"):p.get("sha") for p in pins if isinstance(p,dict)} if isinstance(pins,list) else {}
    if len(pins)!=9 or len(pin_map)!=9 or not isinstance(current_heads,dict) or current_heads!=pin_map:
        fail("CURRENT_CONTRIBUTOR_SHA_NOT_PROVEN")
    if packet.get("branch_pins")!=pins:
        fail("PACKET_BRANCH_PINS_CHANGED")
    articles=original.get("original_articles",[])
    article_rows=[{"slug":a.get("slug"),"body_candidate_git_blobs":a.get("body_candidate_git_blobs")} for a in articles if isinstance(a,dict)] if isinstance(articles,list) else []
    if packet.get("article_identities")!=article_rows:
        fail("ARTICLE_CANDIDATE_CUSTODY_DRIFT")
    rows=original.get("all_original_source_id_crosswalk",[])
    rows=rows if isinstance(rows,list) else []
    source_map={}
    by_url=defaultdict(set)
    occurrences=0
    for i,row in enumerate(rows):
        if not isinstance(row,dict): fail("BAD_SOURCE_ROW"); continue
        sid=row.get("source_id")
        variants=row.get("variants",[])
        if not isinstance(sid,str) or not isinstance(variants,list):
            fail("BAD_SOURCE_ROW"); continue
        if sid in source_map: fail("DUPLICATE_ORIGINAL_SOURCE_ID")
        triples=set()
        for v in variants:
            occurrences+=1
            if not isinstance(v,dict): fail("BAD_SOURCE_VARIANT"); continue
            triple=(v.get("branch"),v.get("source_blob"),v.get("url"))
            try: triples.add(triple)
            except TypeError: fail("UNHASHABLE_SOURCE_VARIANT")
            if isinstance(v.get("url"),str): by_url[v["url"]].add(sid)
        source_map[sid]=triples
    original_groups={u:sorted(ids) for u,ids in by_url.items() if len(ids)>1}
    review_groups=packet.get("duplicate_exact_url_review",[])
    if not isinstance(review_groups,list): review_groups=[]
    actual_groups={}
    for g in review_groups:
        if not isinstance(g,dict): fail("BAD_PACKET_URL_GROUP"); continue
        u=g.get("url")
        if u in actual_groups: fail("DUPLICATE_PACKET_URL_GROUP")
        actual_groups[u]=g.get("source_ids")
        if g.get("review_required") is not True or g.get("decision")!="UNSELECTED" or g.get("merge_authorized") is not False or g.get("reviewer") is not None:
            fail("SHARED_URL_REVIEW_BYPASSED")
    if actual_groups!=original_groups:
        fail("EXACT_URL_TO_IDS_DRIFT")
    original_review=original.get("shared_exact_url_review_groups",[])
    if not isinstance(original_review,list) or len(original_review)!=17:
        fail("ORIGINAL_SHARED_URL_GROUPS_CHANGED")
    else:
        for g in original_review:
            if not isinstance(g,dict) or g.get("review_required") is not True or sorted(g.get("ids",[]))!=original_groups.get(g.get("url")):
                fail("ORIGINAL_SHARED_URL_CROSSWALK_DRIFT")
    original_disputes=original.get("source_evidence_disputes",[])
    packet_disputes=packet.get("source_scope_review",[])
    if not isinstance(original_disputes,list): original_disputes=[]
    if not isinstance(packet_disputes,list): packet_disputes=[]
    original_by_id={s.get("source_id"):s for s in original_disputes if isinstance(s,dict)}
    packet_by_id={s.get("source_id"):s for s in packet_disputes if isinstance(s,dict)}
    if len(original_by_id)!=5 or len(packet_by_id)!=5 or set(original_by_id)!=set(packet_by_id):
        fail("FIVE_ORIGINAL_DISPUTES_LOST")
    for sid, s in original_by_id.items():
        q=packet_by_id.get(sid,{})
        if s.get("decision")!="HUMAN_REVIEW_REQUIRED" or s.get("selected_record") is not None:
            fail("ORIGINAL_DISPUTE_PRESELECTED")
        if q.get("original_decision")!=s.get("decision") or q.get("source_variants")!=s.get("variants"):
            fail("CLAIM_OR_READING_SCOPE_VARIANT_DRIFT")
        if q.get("proposed_selection") is not None or q.get("reviewer") is not None or q.get("review_evidence") is not None or q.get("qualified_safety_approved") is not False:
            fail("PREMATURE_SOURCE_APPROVAL")
        for v in s.get("variants",[]):
            triple=(v.get("branch"),v.get("source_blob"),v.get("url"))
            if triple not in source_map.get(sid,set()) or not v.get("supports_exact") or not v.get("reading_scope_notes_exact"):
                fail("SOURCE_DISPUTE_EVIDENCE_OR_DEPTH_LOST")
    original_forks=original.get("original_fork_disputes",[])
    packet_forks=packet.get("manuscript_fork_review",[])
    if not isinstance(original_forks,list): original_forks=[]
    if not isinstance(packet_forks,list): packet_forks=[]
    fork_by_path={f.get("path"):f for f in original_forks if isinstance(f,dict)}
    review_by_path={f.get("path"):f for f in packet_forks if isinstance(f,dict)}
    if len(fork_by_path)!=9 or len(review_by_path)!=9 or set(fork_by_path)!=set(review_by_path):
        fail("NINE_ORIGINAL_MANUSCRIPT_FORKS_LOST")
    for path, f in fork_by_path.items():
        q=review_by_path.get(path,{})
        if f.get("decision")!="HUMAN_REVIEW_REQUIRED" or f.get("selected_sha") is not None or f.get("requires_reading_depth_review") is not True or f.get("requires_source_citation_review") is not True:
            fail("ORIGINAL_FORK_REVIEW_BYPASSED")
        if q.get("original_variants")!=f.get("variants") or q.get("original_decision")!=f.get("decision") or q.get("reading_depth_review_required") is not True or q.get("source_citation_review_required") is not True:
            fail("MANUSCRIPT_FORK_EVIDENCE_DRIFT")
        if q.get("proposed_selection") is not None or q.get("reviewer") is not None or q.get("review_evidence") is not None or q.get("qualified_safety_approved") is not False:
            fail("PREMATURE_MANUSCRIPT_APPROVAL")
    counts={"articles":len(articles) if isinstance(articles,list) else 0,"source_ids":len(source_map),
      "occurrences":occurrences,"exact_urls":len(by_url),"shared_url_groups":len(original_groups),
      "scope_disputes":len(original_disputes),"forks":len(original_forks),"branches":len(pin_map)}
    if counts!=COUNTS or packet.get("preservation_counts")!=COUNTS:
        fail("ORIGINAL_35_ARTICLE_COUNTS_CHANGED")
    return {"errors":sorted(set(errors)),"counts":counts,"structural_evidence_pass":not errors,
      "release_state":RELEASE,"qd_pass":False,"publishable":False,"verified_paid_offer":False}


def main(argv=None):
    parser=argparse.ArgumentParser(description="R446 original review queue; never release")
    parser.add_argument("--original",type=Path,required=True)
    parser.add_argument("--packet",type=Path,required=True)
    parser.add_argument("--observed-heads",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        raw=args.original.read_bytes()
        o=json.loads(raw,object_pairs_hook=unique_pairs)
        p=json.loads(args.packet.read_text(encoding="utf-8"),object_pairs_hook=unique_pairs)
        heads=json.loads(args.observed_heads.read_text(encoding="utf-8"),object_pairs_hook=unique_pairs)
        result=check(o,p,raw,heads)
    except (OSError,ValueError,TypeError,UnicodeError):
        result={"errors":["EVIDENCE_INPUT_INVALID_OR_MISSING"],"release_state":RELEASE,
                "qd_pass":False,"publishable":False,"structural_evidence_pass":False}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 2   # Explicit HOLD, including structurally consistent source graphs.


if __name__=="__main__":
    raise SystemExit(main())
