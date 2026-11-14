#!/usr/bin/env python3
"""R353: read-only, fail-closed private WordPress/preview export parity.

Checks artifact completeness and evidence preservation, not editorial safety.
Does not build, publish, modify files, call WordPress or grant independent QD.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import html
import json
import re

SCHEMA = "fv-preparedness-r353-private-pair-custody-v1"
SITE = "https://finalvestige.com"
BASE = "/preparedness/"
HOLD = {"may_merge": False, "may_publish": False, "qualified_qd_pass": False,
        "independent_claim_support_verified": False, "native_build_pass": False,
        "paid_offer_verified": False, "verified_paid_orders": False}
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")

def _wp(text):
    m = re.fullmatch(r"<!-- wp:html -->\n<style>.*?</style>\n(.*?)\n<!-- /wp:html -->\n",text,re.S)
    return m.group(1) if m else None

def _preview(text):
    if not text.lower().startswith("<!doctype html>"):
        return None
    if not re.search(r'<meta\s+name="robots"\s+content="noindex,nofollow"\s*>',text):
        return None
    m = re.search(r"<main>(.*?)</main></body></html>$",text,re.S)
    return m.group(1) if m else None

def _words(raw):
    raw = re.sub(r"<(?:style|script)\b[^>]*>.*?</(?:style|script)>"," ",raw,flags=re.I|re.S)
    raw = html.unescape(re.sub(r"<[^>]+>"," ",raw))
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*",raw))

def audit(taxonomy, documents, artifacts, report):
    """Receives the 41 original documents, 100 private HTML files, report."""
    errors=[]
    if not isinstance(taxonomy,dict) or not isinstance(documents,list) or not isinstance(artifacts,dict) or not isinstance(report,dict):
        return {"schema":SCHEMA,"status":"INVALID_HARD_HOLD","errors":["BAD_INPUT"],**HOLD}
    sections = taxonomy.get("sections",[])
    section_ids=[s.get("slug") for s in sections if isinstance(s,dict)] if isinstance(sections,list) else []
    if taxonomy.get("base_path")!=BASE or len(section_ids)!=8 or len(set(section_ids))!=8:
        errors.append("BAD_TAXONOMY_OR_SECTION_COUNT")
    originals={}; routes=set()
    for row in documents:
        if not isinstance(row,dict) or not isinstance(row.get("meta"),dict) or not isinstance(row.get("body"),str):
            errors.append("INVALID_ORIGINAL_DOCUMENT");continue
        meta=row["meta"];slug=meta.get("slug");section=meta.get("section")
        if not isinstance(slug,str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug) or section not in section_ids:
            errors.append("INVALID_DOCUMENT_ROUTE");continue
        if slug in originals:errors.append("DUPLICATE_ORIGINAL_SLUG")
        originals[slug]=row
        route=SITE+BASE+section+"/"+slug+"/"
        if route in routes:errors.append("DUPLICATE_CANONICAL_ROUTE")
        routes.add(route)
        if (meta.get("status") or {}).get("publish")!="draft" or (meta.get("safety_review") or {}).get("state") not in ("pending","not-required"):
            errors.append("NONPRIVATE_OR_UNSAFE_STATE:"+slug)
    if len(originals)!=41 or sum(x.get("kind")=="articles" for x in originals.values())!=35 or sum(x.get("kind")=="tools" for x in originals.values())!=6:
        errors.append("CORPUS_NOT_35_ARTICLES_6_TOOLS")
    expected=set(originals)|{"landing"}|{"hub-"+s for s in section_ids}
    expected_paths={folder+"/"+slug+".html" for folder in ("wp","preview") for slug in expected}
    if len(expected)!=50 or len(artifacts)!=100 or set(artifacts)!=expected_paths:
        errors.append("PRIVATE_EXPORT_SET_NOT_EXACT_100")
    entries=report.get("articles")
    if not isinstance(entries,list):entries=[]
    report_rows={}
    for entry in entries:
        if not isinstance(entry,dict) or not isinstance(entry.get("slug"),str):
            errors.append("BAD_REPORT_ROW");continue
        if entry["slug"] in report_rows:errors.append("DUPLICATE_REPORT_ID")
        report_rows[entry["slug"]]=entry
    if set(report_rows)!=set(originals):errors.append("REPORT_CORPUS_MISMATCH")
    hubs=report.get("hubs")
    if not isinstance(hubs,list) or sorted(x.get("section") for x in hubs if isinstance(x,dict))!=sorted(section_ids):
        errors.append("REPORT_HUBS_MISMATCH")
    land=report.get("landing")
    if not isinstance(land,dict) or land.get("article_cards")!=41 or set(land.get("populated_sections",[]))!=set(section_ids):
        errors.append("REPORT_LANDING_MISMATCH")
    release=report.get("release_evidence")
    if (not isinstance(release,dict) or release.get("state")!="HOLD"
        or release.get("independent_qa_verified") is not False
        or release.get("wordpress_publication_performed") is not False
        or release.get("article_drafts")!=41 or release.get("article_published")!=0
        or release.get("qualified_qd_pass") is True or bool(release.get("verified_paid_orders"))):
        errors.append("FALSE_OR_MISSING_RELEASE_HOLD")
    valid_routes=routes|{SITE+BASE}|{SITE+BASE+s+"/" for s in section_ids}
    checked=0
    for slug in sorted(expected):
        wp=artifacts.get("wp/"+slug+".html")
        pv=artifacts.get("preview/"+slug+".html")
        if not isinstance(wp,str) or not isinstance(pv,str):continue
        inner=_wp(wp);preview_inner=_preview(pv)
        if inner is None or preview_inner is None:
            errors.append("UNSAFE_OR_MALFORMED_EXPORT:"+slug);continue
        checked+=1
        if inner!=preview_inner:errors.append("WORDPRESS_PREVIEW_PARITY_FAIL:"+slug)
        scripts=re.findall(r'<script type="application/ld\+json">(.*?)</script>',inner,re.S)
        try:
            graph=json.loads(scripts[0]) if len(scripts)==1 else {}
            graph=graph.get("@graph",[graph])
        except (json.JSONDecodeError,TypeError,AttributeError):
            graph=[]
        if slug in originals:
            record=originals[slug]
            source=record["body"]; row=report_rows.get(slug,{})
            canonical=SITE+BASE+record["meta"]["section"]+"/"+slug+"/"
            citations=list(dict.fromkeys(CITE.findall(source)))
            if row.get("canonical")!=canonical or row.get("sources")!=citations:
                errors.append("SOURCE_CITATION_OR_CANONICAL_DRIFT:"+slug)
            body=re.search(r'<div class="pa-body" id="pa-main">(.*?)</div></div><section class="pa-sources"',inner,re.S)
            if not body or _words(body.group(1)) < _words(source)*0.85:
                errors.append("READING_DEPTH_REDUCTION:"+slug)
            if not isinstance(row.get("words"),int) or row["words"] < _words(source)*0.85:
                errors.append("READING_REPORT_REDUCTION:"+slug)
            if len(re.findall(r'<sup class="pa-cite">',inner))!=len(CITE.findall(source)):
                errors.append("INLINE_CITATION_LOSS:"+slug)
            if sorted(map(int,re.findall(r'<li id="src-(\d+)">',inner)))!=list(range(1,len(citations)+1)):
                errors.append("SOURCE_FOOTNOTE_DRIFT:"+slug)
            articles=[x for x in graph if isinstance(x,dict) and x.get("@type")=="Article"]
            if len(articles)!=1 or articles[0].get("mainEntityOfPage")!=canonical or "datePublished" in articles[0]:
                errors.append("ARTICLE_STRUCTURED_DATA_DRIFT:"+slug)
            if "Draft: not public" not in inner or "Independent safety/source and QD verification pending" not in inner:
                errors.append("DRAFT_HOLD_MARKER_MISSING:"+slug)
        else:
            canonical=SITE+BASE if slug=="landing" else SITE+BASE+slug[4:]+"/"
            if sum(x.get("@type")=="CollectionPage" and x.get("url")==canonical for x in graph if isinstance(x,dict))!=1:
                errors.append("HUB_OR_LANDING_CANONICAL_DRIFT:"+slug)
        for link in re.findall(r'\bhref="([^"]+)"',inner):
            link=html.unescape(link)
            if link.startswith(BASE) and SITE+link.split("?",1)[0].split("#",1)[0] not in valid_routes:
                errors.append("UNBUILT_INTERNAL_LINK:"+slug)
            if link.lower().startswith(("http:","javascript:","vbscript:","data:")):
                errors.append("UNSAFE_EXPORT_LINK:"+slug)
    return {"schema":SCHEMA,"status":"INVALID_HARD_HOLD" if errors else "PRIVATE_PARITY_ONLY_HARD_HOLD",
            "errors":sorted(set(errors)),"pairs_compared":checked,
            "source_body_sha256":{k:hashlib.sha256(v["body"].encode()).hexdigest() for k,v in sorted(originals.items())},
            **HOLD}

def native_audit(repo):
    """Native read-only collector; no source mutation, build or remote calls."""
    try:
        repo=Path(repo).resolve(strict=True)
        root=repo/"preparedness"
        if not (repo/".git").exists():raise ValueError("FULL_CHECKOUT_UNAVAILABLE")
        documents=[]
        for kind in ("articles","tools"):
            for meta in (root/"content"/kind).glob("*.meta.json"):
                body=meta.with_name(meta.name.replace(".meta.json",".body.html"))
                if meta.is_symlink() or body.is_symlink() or not body.is_file():
                    raise ValueError("NONREGULAR_SOURCE")
                documents.append({"kind":kind,"meta":json.loads(meta.read_text()),"body":body.read_text()})
        artifacts={}
        for folder in ("wp","preview"):
            for file in (root/"build"/folder).iterdir():
                if file.is_symlink() or not file.is_file() or file.suffix!=".html":
                    raise ValueError("NONREGULAR_OUTPUT")
                artifacts[folder+"/"+file.name]=file.read_text()
        report_file=root/"build"/"build-report.json"
        if report_file.is_symlink():raise ValueError("NONREGULAR_REPORT")
        return audit(json.loads((root/"taxonomy.json").read_text()),documents,artifacts,json.loads(report_file.read_text()))
    except (OSError,ValueError,TypeError,UnicodeError,json.JSONDecodeError) as error:
        return {"schema":SCHEMA,"status":"INVALID_HARD_HOLD",
                "errors":["NATIVE_UNAVAILABLE:"+type(error).__name__],**HOLD}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[2])
    print(json.dumps(native_audit(p.parse_args().repo_root),indent=2,sort_keys=True))
    raise SystemExit(2)  # non-release gate: never emits a publish pass
