#!/usr/bin/env python3
"""R354 read-only exact source-to-render citation custody. No approval or publishing."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import re

SCHEMA="fv-preparedness-r354-exact-render-hold-v1"
BUILDER_BLOB="349173d1e1d735eade218d95c7a0a2649c8cccd9"
TAXONOMY_BLOB="15c547bb3018ac182b12a51036389cfa39a59168"
R353_BLOB="e30195338e0de50c475d0ed178cefd2cac0c3db6"
HOLD={"may_merge":False,"may_publish":False,"qualified_qd_pass":False,
      "human_link_check_complete":False,"emergency_safety_verified":False,
      "native_build_pass":False,"verified_paid_orders":False}
CITE=re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
ANCHOR=re.compile(r'<sup class="pa-cite"><a href="#src-(\d+)" aria-label="Source (\d+): [^"]*">\[(\d+)\]</a></sup>')
OPEN='<div class="pa-body" id="pa-main">'
END='</div></div><section class="pa-sources"'

def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def _inner(raw, kind):
    if not isinstance(raw,str):return None
    if kind=="wp":
        m=re.fullmatch(r"<!-- wp:html -->\n<style>.*?</style>\n(.*?)\n<!-- /wp:html -->\n",raw,re.S)
    else:
        if not raw.lower().startswith("<!doctype html>") or len(re.findall(r'<meta\s+name="robots"\s+content="noindex,nofollow"\s*>',raw))!=1:return None
        m=re.search(r"<main>(.*?)</main></body></html>$",raw,re.S)
    return m.group(1) if m else None

def audit(rows,artifacts,report):
    """Pure audit of canonical builder expectations, not a safety verdict."""
    errors=[]
    if not isinstance(rows,list) or not isinstance(artifacts,dict) or not isinstance(report,dict):
        return {"schema":SCHEMA,"status":"INVALID_HARD_HOLD","errors":["INVALID_INPUT"],**HOLD}
    originals={}
    for row in rows:
        if not isinstance(row,dict):errors.append("INVALID_SOURCE_ROW");continue
        slug=row.get("slug")
        if not isinstance(slug,str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug):
            errors.append("INVALID_SLUG");continue
        if slug in originals:errors.append("DUPLICATE_SOURCE_SLUG:"+slug)
        originals[slug]=row
        if row.get("kind") not in ("articles","tools") or row.get("publish")!="draft" or row.get("safety") not in ("pending","not-required"):
            errors.append("PRIVATE_SOURCE_STATE_DRIFT:"+slug)
        if not all(isinstance(row.get(k),str) for k in ("original","resolved","sources_html")) or not isinstance(row.get("source_ids"),list):
            errors.append("INVALID_SOURCE_EXPECTATION:"+slug);continue
        if list(dict.fromkeys(CITE.findall(row["original"])))!=row["source_ids"] or any(not isinstance(x,str) for x in row["source_ids"]):
            errors.append("SOURCE_ID_ORDER_UNBOUND:"+slug)
    if len(originals)!=41 or sum(r.get("kind")=="articles" for r in originals.values())!=35 or sum(r.get("kind")=="tools" for r in originals.values())!=6:
        errors.append("CORPUS_35_ARTICLES_6_TOOLS_REQUIRED")
    buildrows=report.get("articles")
    if not isinstance(buildrows,list):buildrows=[];errors.append("BUILD_REPORT_MISSING")
    reports={}
    for rec in buildrows:
        if not isinstance(rec,dict) or not isinstance(rec.get("slug"),str):errors.append("INVALID_REPORT_ROW");continue
        if rec["slug"] in reports:errors.append("DUPLICATE_REPORT_SLUG")
        reports[rec["slug"]]=rec
    if set(reports)!=set(originals):errors.append("BUILD_REPORT_IDENTITY_DRIFT")
    release=report.get("release_evidence")
    if not isinstance(release,dict) or release.get("state")!="HOLD" or release.get("independent_qa_verified") is not False or release.get("wordpress_publication_performed") is not False or release.get("article_published")!=0 or any(bool(release.get(k)) for k in ("qualified_qd_pass","verified_paid_orders","paid_offer_verified","human_safety_review_verified")):
        errors.append("RELEASE_HOLD_MISSING_OR_FALSE")
    compared=0
    for slug,row in sorted(originals.items()):
        if not all(isinstance(row.get(k),str) for k in ("original","resolved","sources_html")) or not isinstance(row.get("source_ids"),list):continue
        if reports.get(slug,{}).get("sources")!=row["source_ids"]:errors.append("REPORT_CITATION_SOURCE_DRIFT:"+slug)
        try:expected=[str(row["source_ids"].index(s)+1) for s in CITE.findall(row["original"])]
        except (ValueError,TypeError):expected=[];errors.append("SOURCE_ID_ORDER_UNBOUND:"+slug)
        for kind in ("wp","preview"):
            key=kind+"/"+slug+".html"
            inner=_inner(artifacts.get(key),kind)
            if inner is None:errors.append("INVALID_OR_MISSING_PRIVATE_EXPORT:"+key);continue
            if inner.count(OPEN)!=1 or inner.count(END)!=1:
                errors.append("BODY_BOUNDARY_DRIFT:"+key);continue
            body=inner.split(OPEN,1)[1].split(END,1)[0]
            if body!=row["resolved"]:errors.append("EXACT_CLAIM_RENDER_DRIFT:"+key)
            if not row["sources_html"].startswith('<section class="pa-sources"') or inner.count(row["sources_html"])!=1:
                errors.append("EXACT_SOURCE_DISCLOSURE_DRIFT:"+key)
            actual=ANCHOR.findall(body)
            if len(actual)!=len(expected) or any(a!=b or b!=c or a!=n for (a,b,c),n in zip(actual,expected)):
                errors.append("CLAIM_CITATION_POSITION_DRIFT:"+key)
            if "{{cite:" in inner:errors.append("UNRESOLVED_CITATION:"+key)
        wp=_inner(artifacts.get("wp/"+slug+".html"),"wp")
        pv=_inner(artifacts.get("preview/"+slug+".html"),"preview")
        if wp is not None and pv is not None:
            compared+=1
            if wp!=pv:errors.append("WP_PREVIEW_CONTENT_DRIFT:"+slug)
    return {"schema":SCHEMA,"status":"INVALID_HARD_HOLD" if errors else "RESEARCH_ONLY_EXACT_RENDER_HARD_HOLD",
            "errors":sorted(set(errors)),"original_documents":len(originals),"paired_private_documents":compared,
            "original_sha256":{s:hashlib.sha256(r["original"].encode()).hexdigest() for s,r in sorted(originals.items()) if isinstance(r.get("original"),str)},**HOLD}

def native_audit(repo):
    """Read only complete exact-pinned checkout plus preexisting drafts; never build."""
    try:
        repo=Path(repo).resolve(strict=True);root=repo/"preparedness"
        if not (repo/".git").exists():raise ValueError("MISSING_NATIVE_CHECKOUT")
        pins={"build":(root/"tools"/"build.py",BUILDER_BLOB),
              "tax":(root/"taxonomy.json",TAXONOMY_BLOB),
              "r353":(root/"tools"/"r353_private_wp_preview_parity_hold.py",R353_BLOB)}
        for file,expected in pins.values():
            if file.is_symlink() or not file.is_file() or git_blob(file.read_bytes())!=expected:
                raise ValueError("PINNED_INPUT_MISSING_OR_DRIFTED")
        spec=importlib.util.spec_from_file_location("r354_pinned_builder",pins["build"][0])
        if spec is None or spec.loader is None:raise ValueError("BUILDER_IMPORT_FAILED")
        build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
        library=build.Library(root);rows=[]
        for slug,meta in sorted(library.articles.items()):
            body,order=build.resolve_tokens(library,meta)
            rows.append({"slug":slug,"kind":"tools" if meta.get("kind")=="tool" else "articles",
                         "publish":meta["status"]["publish"],"safety":meta.get("safety_review",{}).get("state","pending"),
                         "original":meta["_body"],"resolved":body,
                         "sources_html":build.sources_block(library,order,meta),"source_ids":order})
        artifacts={}
        for kind in ("wp","preview"):
            for row in rows:
                name=row["slug"]+".html";p=root/"build"/kind/name
                if p.is_symlink() or not p.is_file():raise ValueError("MISSING_OR_UNSAFE_PRIVATE_EXPORT")
                artifacts[kind+"/"+name]=p.read_text(encoding="utf-8")
        report=root/"build"/"build-report.json"
        if report.is_symlink():raise ValueError("UNSAFE_REPORT")
        return audit(rows,artifacts,json.loads(report.read_text(encoding="utf-8")))
    except (OSError,ValueError,KeyError,TypeError,UnicodeError,ImportError,AttributeError,json.JSONDecodeError) as exc:
        return {"schema":SCHEMA,"status":"INVALID_HARD_HOLD",
                "errors":["NATIVE_EVIDENCE_UNAVAILABLE:"+type(exc).__name__],**HOLD}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[2])
    print(json.dumps(native_audit(p.parse_args().repo_root),indent=2,sort_keys=True))
    raise SystemExit(2)
