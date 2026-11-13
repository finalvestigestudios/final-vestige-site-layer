#!/usr/bin/env python3
"""R331 deterministic E325/R328/R329 read-only reviewer handoff; NEVER publish approval."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

SCHEMA = "fv-preparedness-r331-e325-crosswalk-draft-hard-hold-v1"

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def strict_json(raw):
    def unique(pairs):
        d = {}
        for k,v in pairs:
            if k in d: raise ValueError("DUPLICATE_JSON_KEY")
            d[k]=v
        return d
    return json.loads(raw.decode("utf-8","strict"), object_pairs_hook=unique)

def inspect(docs, manifest, *, simulated=False):
    errors=[]; rows=[]
    if not isinstance(manifest,dict) or manifest.get("schema")!=SCHEMA:
        return {"state":"INVALID_HARD_HOLD","errors":["INVALID_MANIFEST_SCHEMA"],"release":False}
    src=manifest.get("source_objects")
    issues=manifest.get("original_review_witnesses")
    directions=manifest.get("editorial_directions")
    gates=manifest.get("gates")
    if not isinstance(src,dict) or set(src)!={"a_body","a_meta","t_body","t_meta"}: errors.append("INVALID_SOURCE_SCOPE");src={}
    if not isinstance(docs,dict) or set(docs)!=set(src): errors.append("MISSING_SOURCE_ROLES");docs={}
    if not isinstance(directions,dict) or set(directions)!={f"E325-{i:02d}" for i in range(1,8)}:
        errors.append("SEVEN_EDITORIAL_DIRECTIONS_REQUIRED");directions={}
    if not isinstance(gates,dict) or not gates or any(v is not False for v in gates.values()):
        errors.append("FORGED_RELEASE_OR_SAFETY_CLEARANCE")
    if not isinstance(issues,list) or len(issues)!=17 or len({r.get("id") for r in issues if isinstance(r,dict)})!=17:
        errors.append("SEVENTEEN_UNIQUE_UNRESOLVED_REVIEWS_REQUIRED");issues=[]
    text={};meta={}
    for role,rec in src.items():
        if not isinstance(rec,dict) or not str(rec.get("path","")).startswith("preparedness/content/"):
            errors.append("INVALID_PINNED_PATH_"+role);continue
        raw=docs.get(role)
        if type(raw) is not bytes: errors.append("MISSING_SOURCE_BYTES_"+role);continue
        if not simulated and blob(raw)!=rec.get("git_blob_sha1"):
            errors.append("AUTHENTIC_GIT_OBJECT_MISMATCH_"+role)
        try:
            text[role]=raw.decode("utf-8","strict")
            if role.endswith("meta"):meta[role]=strict_json(raw)
        except (UnicodeError,ValueError,TypeError):
            errors.append("BAD_UTF8_OR_DUPLICATE_JSON_"+role)
    for role,body,n,slug in [("a_meta","a_body",15,"family-communication-plan"),("t_meta","t_body",104,"family-reunification-card")]:
        m=meta.get(role)
        if (not isinstance(m,dict) or type(m.get("n")) is not int or m.get("n")!=n or
            m.get("slug")!=slug or m.get("status")!={"editorial":"drafted","publish":"draft"} or
            not isinstance(m.get("safety_review"),dict) or m["safety_review"].get("state")!="pending" or
            m["safety_review"].get("reviewer") is not None or m["safety_review"].get("date") is not None or
            not isinstance(m.get("source_use"),dict)):
            errors.append("UNREVIEWED_SOURCE_SAFETY_STATE_DRIFT_"+role);continue
        cites=set(re.findall(r"\{\{cite:([a-z0-9-]+)\}\}", text.get(body,"")))
        if cites!=set(m["source_use"]): errors.append("CITATION_DECLARATION_DRIFT_"+role)
    for w in issues:
        if not isinstance(w,dict):errors.append("INVALID_REVIEW_ROW");continue
        rid,role,anchor,edit=w.get("id"),w.get("source_role"),w.get("exact_anchor"),w.get("editorial_candidate")
        if (not isinstance(rid,str) or role not in src or not isinstance(anchor,str) or
            (edit is not None and edit not in directions) or w.get("disposition")!="UNRESOLVED_HUMAN_REVIEW" or
            w.get("clearance") is not False):
            errors.append("INVALID_REVIEW_ROW_"+str(rid));continue
        offsets=[m.start() for m in re.finditer(re.escape(anchor),text.get(role,""))]
        if len(offsets)!=1:errors.append("MISSING_OR_DUPLICATE_ANCHOR_"+rid);continue
        rows.append({"id":rid,"role":role,"byte_offset":len(text[role][:offsets[0]].encode("utf-8")),
                     "editorial_candidate":edit,"status":"HUMAN_REVIEW_PENDING","cleared":False})
    if len(rows)!=17:errors.append("INCOMPLETE_WITNESS_COVERAGE")
    if sum(r["role"].startswith("t_") for r in rows)!=8:errors.append("TOOL104_EIGHT_HOLDS_REQUIRED")
    if sum(r["editorial_candidate"] is not None for r in rows)!=9:errors.append("ARTICLE15_NINE_OPEN_HOLDS_REQUIRED")
    used={r["editorial_candidate"] for r in rows if r["editorial_candidate"]}
    if set(directions)-used!={"E325-03","E325-07"}:errors.append("E325_EXTRA_DIRECTIONS_DRIFT")
    return {"state":"INVALID_HARD_HOLD" if errors else "DRAFT_HARD_HOLD","errors":sorted(set(errors)),
        "provenance":"SIMULATED_FIXTURE" if simulated else "AUTHENTIC_GIT_BLOB_CHECK",
        "review_count":len(rows),"unaddressed_tool104":8,"source_witnesses":rows,
        "release_authorized":False,"independent_qd_pass":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);args=ap.parse_args()
    root=args.root.resolve()
    p=root/"preparedness/audits/r331_e325_claim_handoff_crosswalk.json"
    try:
        m=strict_json(p.read_bytes())
        docs={}
        for role,rec in m["source_objects"].items():
            f=root/rec["path"]
            if f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(root):raise OSError("INVALID_NATIVE_SOURCE")
            docs[role]=f.read_bytes()
        r=inspect(docs,m)
    except (OSError,ValueError,TypeError,KeyError,UnicodeError):
        r={"state":"INVALID_HARD_HOLD","errors":["AUTHENTIC_NATIVE_CHECKOUT_AND_MANIFEST_REQUIRED"],"release_authorized":False,"independent_qd_pass":False}
    print(json.dumps(r,indent=2,sort_keys=True))
    return 2 if r["state"]=="DRAFT_HARD_HOLD" else 1

if __name__=="__main__":raise SystemExit(main())
