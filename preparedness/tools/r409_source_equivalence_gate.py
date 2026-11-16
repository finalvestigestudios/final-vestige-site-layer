#!/usr/bin/env python3
"""R409: read-only original source-ID/URL/fork graph guard. NEVER release/QD PASS.

Native mode requires the unchanged R397 JSON's exact Git blob. Test-only
injected count parameters cannot be supplied on the CLI.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit, urlunsplit

PIN = "86d22a1d504c93db7689b914e2202a7845b648e2"
COUNTS = {"original_article_count": 35, "original_object_paths": 77,
          "original_source_fragments": 7, "source_record_occurrences": 280,
          "original_distinct_source_ids": 203, "base_source_records": 34,
          "source_evidence_disputes": 5, "unselected_original_forks": 9}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def unique_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate JSON key: " + k)
        out[k] = v
    return out


def read_original(path: Path, max_bytes: int = 2_000_000):
    p = Path(path)
    before = p.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 0 < before.st_size <= max_bytes:
        raise ValueError("not bounded single-link regular docket")
    fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as f:
        after = os.fstat(f.fileno())
        if not stat.S_ISREG(after.st_mode) or after.st_nlink != 1:
            raise ValueError("docket changed file type")
        data = f.read(max_bytes + 1)
    if len(data) > max_bytes or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError("docket changed during guarded read")
    return data


def checked_url(raw):
    if not isinstance(raw, str) or len(raw) > 2048 or any(ord(ch) < 33 or ord(ch) == 127 for ch in raw):
        raise ValueError("bad source URL encoding")
    u = urlsplit(raw)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.port not in (None, 443):
        raise ValueError("source URL must be HTTPS with no credentials/custom port")
    if not re.fullmatch(r"[a-z0-9.-]+", u.hostname.lower()) or u.hostname.startswith("."):
        raise ValueError("invalid hostname")
    return urlunsplit(("https", u.hostname.lower(), u.path.rstrip("/") or "/", u.query, ""))


def audit(d, counts=COUNTS, require_pin=True, raw=None):
    errors, risks = [], []
    def fail(message): errors.append(message)
    if not isinstance(d, dict):
        return {"release_state":"DRAFT_HARD_HOLD", "eligible":False, "errors":["docket not an object"], "risks":[]}
    if require_pin and (raw is None or blob(raw) != PIN): fail("original R397 Git blob mismatch/missing")
    if d.get("schema") != 1 or d.get("provenance") != "ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY" or d.get("issue") != 136: fail("docket identity mismatch")
    for key in ("publication_approved", "qualified_safety_approved", "merchant_offer_verified", "automatic_variant_selection"):
        if d.get(key) is not False: fail("false approval flag required: " + key)
    if d.get("release_state") != "DRAFT_HARD_HOLD": fail("release state changed")
    for name, expected in counts.items():
        if d.get("expected", {}).get(name) != expected or d.get("observed", {}).get(name) != expected:
            fail("expected/observed count changed: " + name)
    articles = d.get("original_articles", [])
    ids = d.get("all_original_source_id_crosswalk", [])
    shared = d.get("shared_exact_url_review_groups", [])
    source_disputes = d.get("source_evidence_disputes", [])
    forks = d.get("original_fork_disputes", [])
    pins = d.get("branch_pins", [])
    if not all(isinstance(x, list) for x in (articles, ids, shared, source_disputes, forks, pins)):
        fail("missing graph arrays"); return {"release_state":"DRAFT_HARD_HOLD","eligible":False,"errors":errors,"risks":[]}
    if len(articles) != counts["original_article_count"]: fail("article identities dropped/added")
    if len(ids) != counts["original_distinct_source_ids"]: fail("source identities dropped/added")
    if len(source_disputes) != counts["source_evidence_disputes"]: fail("original source dispute missing")
    if len(forks) != counts["unselected_original_forks"]: fail("original manuscript fork missing")
    if len(pins) != 9 or len({p.get("branch") for p in pins if isinstance(p,dict)}) != 9 or not all(isinstance(p,dict) and isinstance(p.get("sha"),str) and HEX40.fullmatch(p["sha"]) for p in pins): fail("original branch pin failure")
    slugs = [v.get("slug") for v in articles if isinstance(v,dict)]
    if len(slugs) != len(articles) or len(set(slugs)) != len(slugs) or not all(isinstance(s,str) and SLUG.fullmatch(s) for s in slugs): fail("article slug identity collision")
    for x in source_disputes:
        if not isinstance(x,dict) or x.get("decision") != "HUMAN_REVIEW_REQUIRED" or x.get("selected_record") is not None or len(x.get("variants",[])) < 2:
            fail("unreviewed source choice promoted")
    for x in forks:
        if not isinstance(x,dict) or x.get("decision") != "HUMAN_REVIEW_REQUIRED" or x.get("selected_sha") is not None or len(x.get("variants",[])) < 2 or x.get("requires_reading_depth_review") is not True or x.get("requires_source_citation_review") is not True:
            fail("unreviewed manuscript choice promoted")
    by_url, by_id, normalized, occurrences = defaultdict(set), {}, defaultdict(set), 0
    for s in ids:
        if not isinstance(s,dict): fail("malformed source ID"); continue
        sid = s.get("source_id")
        if not isinstance(sid,str) or not SLUG.fullmatch(sid) or sid in by_id:
            fail("invalid/duplicate source identity"); continue
        var = s.get("variants", [])
        if not isinstance(var,list) or not var: fail("source has no variants"); continue
        by_id[sid] = var
        u_set = set()
        for v in var:
            occurrences += 1
            if not isinstance(v,dict) or not isinstance(v.get("source_blob"),str) or not HEX40.fullmatch(v["source_blob"]) or v.get("branch") not in {p.get("branch") for p in pins if isinstance(p,dict)}:
                fail("source-variant provenance mismatch: " + sid); continue
            try: normalized[checked_url(v.get("url"))].add(v["url"])
            except (ValueError,TypeError): fail("invalid source URL: " + sid); continue
            by_url[v["url"]].add(sid)
            u_set.add(v["url"])
        if len(u_set)>1:
            fail("source-ID URL drift requires adjudication: " + sid)
            risks.append({"kind":"SOURCE_ID_URL_DRIFT","id":sid,"urls":sorted(u_set)})
    if occurrences != counts["source_record_occurrences"]: fail("original source occurrences changed")
    derived = {u: sorted(sids) for u,sids in by_url.items() if len(sids)>1}
    declared = {}
    for g in shared:
        if not isinstance(g,dict) or not isinstance(g.get("url"),str) or g["url"] in declared or g.get("review_required") is not True or not isinstance(g.get("ids"),list):
            fail("invalid shared-URL review group"); continue
        declared[g["url"]] = g["ids"]
    if len(declared) != 17: fail("shared-URL group count changed")
    if declared != derived: fail("shared-URL crosswalk inconsistent with per-source identities")
    for url, sids in sorted(derived.items()):
        risks.append({"kind":"EXACT_URL_DISTINCT_SOURCE_IDS","url":url,"ids":sids,"requires_human_review":True})
    for norm, originals in sorted(normalized.items()):
        if len(originals)>1: risks.append({"kind":"POTENTIAL_NORMALIZED_URL_ALIAS_DO_NOT_COLLAPSE","normalized":norm,"originals":sorted(originals)})
    return {"release_state":"DRAFT_HARD_HOLD","eligible":False,"publication_approved":False,
            "integrity_ok":not errors,"errors":sorted(set(errors)),"risks":risks,
            "counts":{"articles":len(articles),"source_ids":len(ids),"occurrences":occurrences,
                      "exact_url_review_groups":len(derived),"source_disputes":len(source_disputes),"forks":len(forks),"branches":len(pins)}}


def main():
    parser=argparse.ArgumentParser(description="R409 read-only original graph HOLD gate")
    parser.add_argument("docket",type=Path,nargs="?",default=Path(__file__).resolve().parents[1]/"reviews"/"r397_original_source_fork_docket.json")
    a=parser.parse_args()
    try:
        data=read_original(a.docket)
        report=audit(json.loads(data.decode("utf-8"),object_pairs_hook=unique_pairs),raw=data)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        report={"release_state":"DRAFT_HARD_HOLD","eligible":False,"integrity_ok":False,"errors":[str(exc)],"risks":[]}
    print(json.dumps(report,sort_keys=True,indent=2))
    return 2

if __name__ == "__main__": raise SystemExit(main())
