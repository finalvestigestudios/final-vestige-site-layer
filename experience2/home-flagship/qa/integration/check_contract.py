#!/usr/bin/env python3
"""Fail-closed checks for the *actual* unpublished Experience 2.0 page checkout.

Local-only, read-only and offline. Does not inspect production WordPress, replace a
homepage, grant release approval or pretend to provide a WCAG certification.
"""
from __future__ import annotations
import argparse
import hashlib
import html.parser
import json
from pathlib import Path
from urllib.parse import urlparse

STYLES = ["flagship.css", "chronicle.css", "chronicle-lens.css", "inquiry.css", "observer-lab.css", "reading-trail.css"]
SCRIPTS = ["flagship.js", "observer-lab.js", "chronicle-lens.js", "reading-trail.js"]
ASSETS = ["index.html", *STYLES, *SCRIPTS]
CASES = {"apollo", "franklin", "malbone"}
CHAPTERS = ["fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry", "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title"]
NECESSARY_DESTINATIONS = ["/focus/", "/editorial-standards/", "/free-resources/puysegurs-animal-magnetism-files/"]
PUBLICATION_FORBIDDEN = ["inspire3.com/checkout", "clickbank.net/", "hop.clickbank", "buy now", "guaranteed brain reprogramming"]

class Capture(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.anchors=[]; self.assets=[]; self.scripts=[]; self.styles=[]
        self.images=[]; self.buttons=[]; self.details=[]; self.headings=[]; self.labels=[]
        self.cases=[]; self.case_buttons=[]; self.section_ids=[]
        self.observers=[]; self.chronicle_views=[]; self.forms=[]
    _ns = 0
    def handle_endtag(self, tag):
        if tag.lower() == 'noscript': self._ns -= 1
    def handle_starttag(self,tag, attrs):
        if tag.lower() == 'noscript': self._ns += 1
        a=dict(attrs)
        if a.get("id"):self.ids.append(a["id"])
        if tag=="section" and a.get("id"):self.section_ids.append(a["id"])
        if tag=="a" and "href" in a:self.anchors.append(a["href"])
        if tag=="link" and a.get("rel")=="stylesheet":self.styles.append(a.get("href"))
        if tag=="script" and a.get("src"):self.scripts.append(a["src"])
        if tag=="img" and not self._ns:self.images.append(a)
        if tag=="button":self.buttons.append(a)
        if tag=="form":self.forms.append(a)
        if tag=="details":self.details.append(a)
        if tag in ("h1","h2","h3"):self.headings.append((tag,a))
        if a.get("data-fv-case"):self.cases.append(a["data-fv-case"])
        if a.get("data-fv-case-button"):self.case_buttons.append(a["data-fv-case-button"])
        if a.get("data-fv-observer-frame"):self.observers.append(a["data-fv-observer-frame"])
        if a.get("data-fv-chronicle-view"):self.chronicle_views.append(a["data-fv-chronicle-view"])


def scan(root:Path):
    checks={}; observations={}; errors=[]
    def ck(name,ok,detail=""):
        checks[name]=bool(ok)
        if not ok: errors.append(f"{name}: {detail}")
    ck("exact_asset_set_present",all((root/p).is_file() for p in ASSETS),"Missing: "+str([p for p in ASSETS if not (root/p).is_file()]))
    if not (root/"index.html").is_file():return checks,observations,errors
    content=(root/"index.html").read_text(encoding="utf-8")
    p=Capture();p.feed(content)
    observations["asset_sha256"]={x:hashlib.sha256((root/x).read_bytes()).hexdigest() for x in ASSETS if (root/x).is_file()}
    observations["index_bytes"]=len((root/"index.html").read_bytes())
    observations["id_count"]=len(p.ids)
    observations["image_count"]=len(p.images)
    observations["local_style_count"]=len(p.styles)
    observations["local_script_count"]=len(p.scripts)
    observations["chapter_count"]=len(CHAPTERS)
    ck("only_expected_local_styles",p.styles==["./"+x for x in STYLES],p.styles)
    ck("only_expected_local_scripts",p.scripts==["./"+x for x in SCRIPTS],p.scripts)
    ck("unique_dom_ids",len(p.ids)==len(set(p.ids)),"duplicates "+str([x for x in p.ids if p.ids.count(x)>1]))
    ck("seven_chapters_resolve",all(x in p.ids for x in CHAPTERS),"unresolved "+str([x for x in CHAPTERS if x not in p.ids]))
    ck("internal_anchor_targets_resolve",all(x[1:] in p.ids for x in p.anchors if x.startswith("#") and x!="#"),"broken "+str([x for x in p.anchors if x.startswith("#") and x!="#" and x[1:] not in p.ids]))
    ck("exact_three_evidence_panels",set(p.cases)==CASES and len(p.cases)==3,p.cases)
    ck("exact_three_case_controls",set(p.case_buttons)==CASES and len(p.case_buttons)==3,p.case_buttons)
    ck("single_locked_art_direction",'data-fv-direction-choice' not in content,"studio direction-picker markup must be fully retired, not merely hidden")
    ck("both_observer_frames",p.observers==["a","b"],p.observers)
    ck("three_lens_modes",set(p.chronicle_views)=={"original","addition","both"} and len(p.chronicle_views)==3,p.chronicle_views)
    ck("one_document_h1",len([x for x,_ in p.headings if x=="h1"])==1,[x for x,_ in p.headings if x=="h1"])
    ck("minimum_six_native_details",len(p.details)>=6,str(len(p.details)))
    ck("preserved_editorial_routes",all(s in content for s in NECESSARY_DESTINATIONS),NECESSARY_DESTINATIONS)
    ck("unpublished_banner",'DESIGN CANDIDATE · NOT LIVE' in content and 'DO NOT DEPLOY AS THE WORDPRESS HOME PAGE' in content)
    ck("no_external_executable_assets",all(x.startswith("./") for x in p.styles+p.scripts))
    ck("no_web_form_or_affiliate_checkout",not p.forms and not any(x in content.lower() for x in PUBLICATION_FORBIDDEN))
    ck("source_custody_links",all(s in content for s in ("rmg.co.uk/collections/objects/","historymuseum.ca/blog/a-very-special-piece-of-paper","nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/","digitalcollections.nypl.org/items/")))
    ck("image_dimensions_declared",all(x.get("width") and x.get("height") and x.get("alt") for x in p.images),str([x.get("src") for x in p.images if not (x.get("width") and x.get("height") and x.get("alt"))]))
    ck("no_script_only_chapters",all(x in content for x in ('id="fv-hf-chronicle"','id="fv-hf-evidence"','id="fv-hf-inquiry"','id="fv-hf-observer"')))
    # Relative assets are fully enumerated, preventing accidental unbundled files.
    ck("asset_manifest_self_contained",all((root/x.lstrip("./")).is_file() for x in p.styles+p.scripts))
    return checks,observations,errors


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);parser.add_argument("--report",type=Path)
    args=parser.parse_args();checks,observations,errors=scan(args.root)
    report={"scope":"unpublished source checkout only—not live WordPress, CI, WCAG or performance certification", "root":str(args.root.resolve()),"checks":checks,"observations":observations,"errors":errors,"passed":not errors}
    if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"passed":not errors,"passed_checks":sum(checks.values()),"total_checks":len(checks),"errors":errors},indent=2))
    raise SystemExit(0 if not errors else 1)
if __name__=="__main__":main()
