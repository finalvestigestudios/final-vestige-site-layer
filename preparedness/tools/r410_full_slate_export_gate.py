#!/usr/bin/env python3
"""R410 read-only 35-article draft HTML source/citation parity. Never a publication gate PASS."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
# -I isolation removes the script directory from sys.path; load only our fixed sibling file.
from importlib.util import module_from_spec, spec_from_file_location
_spec = spec_from_file_location("r409_source_equivalence_gate", Path(__file__).with_name("r409_source_equivalence_gate.py"))
_r409 = module_from_spec(_spec)
_spec.loader.exec_module(_r409)
graph_audit, read_original, unique_pairs = _r409.audit, _r409.read_original, _r409.unique_pairs

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
BLOCK_TAGS = {"script", "iframe", "frame", "frameset", "object", "embed", "form", "input", "button", "textarea", "select", "link", "style", "meta", "base", "svg", "math", "video", "audio", "source"}
BAD_ATTR = {"src", "srcset", "action", "formaction", "ping", "style", "srcdoc"}

class DraftHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors, self.cites, self.words, self.headings = [], [], [], []
        self.hidden = 0
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if len({k for k,v in attrs}) != len(attrs): self.errors.append("duplicate HTML attributes")
        attrs = dict(attrs)
        if tag in BLOCK_TAGS or tag == "img": self.errors.append("active, remote or non-text element: " + tag)
        for k,v in attrs.items():
            if k.lower().startswith("on") or k.lower() in BAD_ATTR:
                self.errors.append("active/remote attribute: " + k)
            if isinstance(v,str) and ("javascript:" in v.lower() or "data:" in v.lower() or "vbscript:" in v.lower()):
                self.errors.append("unsafe attribute URL")
        if tag in {"h1","h2","h3","h4","h5","h6"}: self.headings.append(tag)
        if tag == "a":
            sid = attrs.get("data-source-id")
            href = attrs.get("href")
            if not sid and href and ("http" in href or "#" in href): self.errors.append("unbound link")
            if sid or href:
                if not isinstance(sid,str) or not SLUG.fullmatch(sid): self.errors.append("missing/invalid source ID on link")
                if not isinstance(href,str): self.errors.append("missing citation target")
                self.cites.append((sid, href))
    def handle_startendtag(self, tag, attrs): self.handle_starttag(tag, attrs)
    def handle_data(self, data): self.words.extend(re.findall(r"\b[\w'-]+\b", data, flags=re.UNICODE))


def check(original, manifest, exports, *, raw_original=None, test_only=False):
    """Always return a held report, including on malformed nested evidence."""
    try:
        return _check(original, manifest, exports, raw_original=raw_original, test_only=test_only)
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        return {"release_state":"DRAFT_HARD_HOLD","eligible":False,"publication_approved":False,
                "integrity_ok":False,"errors":["malformed export/source evidence: "+str(exc)],"warnings":[]}

def _check(original, manifest, exports, *, raw_original=None, test_only=False):
    """exports maps slug -> (WordPress HTML bytes or str, private preview HTML bytes or str)."""
    errors, warnings, details = [], [], []
    def fail(msg): errors.append(msg)
    try:
        g = graph_audit(original, require_pin=not test_only, raw=raw_original)
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        fail("original graph parser failed: " + str(e)); g={"integrity_ok":False}
    if not g.get("integrity_ok"): fail("original source graph or exact Git receipt invalid")
    if not isinstance(manifest,dict):
        return {"release_state":"DRAFT_HARD_HOLD","eligible":False,"integrity_ok":False,"errors":["invalid manifest"],"warnings":[]}
    if manifest.get("schema") != 1 or manifest.get("release_state") != "DRAFT_HARD_HOLD" or manifest.get("approved") is not False:
        fail("manifest approval/schema changed")
    entries = manifest.get("articles")
    if not isinstance(entries,list): entries=[]; fail("manifest article list invalid")
    original_articles = original.get("original_articles",[]) if isinstance(original,dict) else []
    expected_slugs = [a.get("slug") for a in original_articles if isinstance(a,dict)]
    actual_slugs = [a.get("slug") for a in entries if isinstance(a,dict)]
    if len(expected_slugs)!=35 or len(entries)!=35 or len(actual_slugs)!=35 or set(actual_slugs)!=set(expected_slugs) or len(set(actual_slugs))!=35:
        fail("35-article identity/coverage mismatch")
    source_urls = {}
    for s in original.get("all_original_source_id_crosswalk",[]) if isinstance(original,dict) else []:
        if not isinstance(s,dict): continue
        variants = s.get("variants")
        if not isinstance(variants,list): continue
        urls = {v.get("url") for v in variants if isinstance(v,dict) and isinstance(v.get("url"),str)}
        if len(urls)==1: source_urls[s.get("source_id")]=next(iter(urls))
        else: fail("ambiguous original source URL: "+str(s.get("source_id")))
    routes=set()
    if not isinstance(exports,dict): exports={}; fail("missing exports")
    if set(exports)!=set(expected_slugs): fail("export file identity/coverage mismatch")
    for a in entries:
        if not isinstance(a,dict): fail("non-object article entry"); continue
        slug, route, sources = a.get("slug"), a.get("canonical_path"), a.get("sources")
        if not isinstance(slug,str) or not SLUG.fullmatch(slug): fail("unsafe slug"); continue
        if not isinstance(route,str) or not route.startswith("/preparedness/") or not route.endswith("/"+slug+"/") or "//" in route or "?" in route or "#" in route or ".." in route:
            fail("unsafe or unrelated canonical route: "+slug)
        if route in routes: fail("duplicate canonical route: "+slug)
        routes.add(route)
        if not isinstance(sources,list) or not sources or any(not isinstance(s,str) or s not in source_urls for s in sources) or len(set(sources))!=len(sources):
            fail("unknown/duplicate or empty citation manifest: "+slug); continue
        pair=exports.get(slug)
        if not isinstance(pair,(tuple,list)) or len(pair)!=2: fail("missing paired HTML: "+slug); continue
        parsed=[]
        for data in pair:
            if isinstance(data,bytes):
                try:data=data.decode("utf-8","strict")
                except UnicodeError: fail("invalid UTF-8: "+slug); continue
            if not isinstance(data,str) or not 10<=len(data.encode("utf-8"))<=1_000_000: fail("invalid/big HTML: "+slug); continue
            p=DraftHTML()
            try:p.feed(data); p.close()
            except (ValueError,TypeError) as e: fail("HTML parse failure: "+slug+": "+str(e)); continue
            if p.errors: fail("unsafe/unbound HTML: "+slug+": "+", ".join(sorted(set(p.errors))))
            actual=set(p.cites)
            for sid,href in actual:
                if sid not in sources or source_urls.get(sid)!=href: fail("citation/source URL mismatch: "+slug+": "+str(sid))
            if {x[0] for x in actual} != set(sources): fail("citations omitted or added: "+slug)
            if not p.headings or len(p.words)<50: fail("missing reading depth/headings: "+slug)
            parsed.append(p)
        if len(parsed)==2:
            if parsed[0].cites!=parsed[1].cites: fail("WordPress/preview source order parity lost: "+slug)
            if parsed[0].headings!=parsed[1].headings: fail("WordPress/preview heading structure lost: "+slug)
            if abs(len(parsed[0].words)-len(parsed[1].words))>max(3,len(parsed[0].words)//20):
                fail("WordPress/preview reading-depth drift: "+slug)
            details.append({"slug":slug,"wp_words":len(parsed[0].words),"preview_words":len(parsed[1].words),"source_ids":len(set(parsed[0].cites))})
    warnings.append("Original baseline reading depth/claim-to-citation factual support NOT established by paired-export parity")
    warnings.append("Five source scopes, nine manuscript forks and Article #7/#11/#15/Tool #104 safety/QD remain HARD HOLD")
    return {"release_state":"DRAFT_HARD_HOLD","eligible":False,"publication_approved":False,
            "integrity_ok":not errors,"errors":sorted(set(errors)),"warnings":warnings,"articles_inspected":len(details),"details":details}


def main():
    p=argparse.ArgumentParser(description="R410 read-only original-source-to-private-export gate; ALWAYS HOLD")
    p.add_argument("original",type=Path)
    p.add_argument("manifest",type=Path)
    p.add_argument("export_root",type=Path)
    args=p.parse_args()
    try:
        raw=read_original(args.original); original=json.loads(raw.decode("utf-8"),object_pairs_hook=unique_pairs)
        manifest=json.loads(read_original(args.manifest).decode("utf-8"),object_pairs_hook=unique_pairs)
        files={}
        for a in manifest.get("articles",[]):
            slug=a["slug"]
            if not isinstance(slug,str) or not SLUG.fullmatch(slug): raise ValueError("unsafe export slug")
            files[slug]=(read_original(args.export_root/"wordpress"/(slug+".html")),
                         read_original(args.export_root/"preview"/(slug+".html")))
        result=check(original,manifest,files,raw_original=raw)
    except (OSError,UnicodeError,ValueError,KeyError,TypeError,AttributeError,json.JSONDecodeError) as e:
        result={"release_state":"DRAFT_HARD_HOLD","eligible":False,"integrity_ok":False,"errors":[str(e)]}
    print(json.dumps(result,sort_keys=True,indent=2)); return 2

if __name__=="__main__": raise SystemExit(main())
