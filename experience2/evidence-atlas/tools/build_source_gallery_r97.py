#!/usr/bin/env python3
"""R97 staging-only rights-safe source gallery; no NASA photos or invented geography."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def esc(x):
    return html.escape(str(x),quote=True)

def load(src):
    if not src.is_dir() or src.is_symlink():
        raise ValueError("R97_INPUT_DIRECTORY")
    receipt=json.loads((src/"R94_ATLAS_RECEIPT.json").read_text())
    if (receipt.get("schema")!="fv.apollo.r94.curated-atlas.v1"
        or receipt.get("release")!="STAGING_HOLD"
        or receipt.get("publication_approved") is not False
        or receipt.get("photo_rights_cleared")!=0
        or receipt.get("geo_pins")!=0 or receipt.get("inferred_edges")!=0
        or receipt.get("source_count")!=6):
        raise ValueError("R97_RELEASE_GATE")
    expected=set(receipt["files"])|{"R94_ATLAS_RECEIPT.json"}
    if {p.name for p in src.iterdir()}!=expected:
        raise ValueError("R97_UNREVIEWED_INPUT")
    for name in sorted(expected):
        p=src/name
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+",name) or not p.is_file() or p.is_symlink():
            raise ValueError("R97_UNREVIEWED_ASSET:"+name)
        if name in receipt["files"] and sha(p)!=receipt["files"][name]:
            raise ValueError("R97_SHA_MISMATCH:"+name)
    book=json.loads((src/"R93_SOURCE_PASSPORTS.json").read_text())
    rights=json.loads((src/"R85_RIGHTS_RECEIPT.json").read_text())
    if book.get("photo_reuse_approved") is not False or rights.get("rights_cleared")!=0 or rights.get("images_embedded")!=0:
        raise ValueError("R97_PHOTO_RIGHTS_GATE")
    rows=book["records"]
    if [r["id"] for r in rows]!=[f"{i:02}" for i in range(1,7)] or len(rights["records"])!=6:
        raise ValueError("R97_RECORD_COUNT")
    for a,b in zip(rows,rights["records"]):
        if (a["id"]!=b["id"] or a["catalog"]!=b["catalog"] or a["url"]!=b["url"]
            or a["rights"]!="INDIVIDUAL REVIEW REQUIRED"
            or b["media_review"]!="INDIVIDUAL_REVIEW_REQUIRED"
            or a["provisional"] is not (a["id"]=="01")
            or not re.fullmatch(r"https://www\.nasa\.gov/image-detail/[a-z0-9_-]+/",a["url"])
            or not all(a.get(k) for k in ("title","date","can","cannot"))):
            raise ValueError("R97_SOURCE_BINDING:"+a["id"])
        if a["id"]=="01" and a["date"]!="January 1967 — day unconfirmed":
            raise ValueError("R97_INVENTED_CREW_DAY")
        if a["id"] in ("04","06") and a["date"]!="January 24, 2017":
            raise ValueError("R97_INVENTED_SEQUENCE")
    return rows,expected

CSS="""*{box-sizing:border-box}body{margin:0;background:#101515;color:#f0e7da;font:16px/1.6 system-ui,sans-serif}a{color:#f7d18b;overflow-wrap:anywhere}a:focus-visible,summary:focus-visible,input:focus-visible,button:focus-visible{outline:3px solid #ffe5a9;outline-offset:3px}.skip{position:absolute;top:-9rem;padding:.8rem;background:white;color:black}.skip:focus{top:1rem}.shell{width:min(1320px,calc(100% - 2rem));margin:auto}.mast{padding:1.5rem 0;border-bottom:1px solid #75694e;color:#eed29a;font:700 .75rem ui-monospace,monospace;letter-spacing:.1em}.hero{padding:clamp(2rem,7vw,6rem) 0;display:grid;grid-template-columns:1.2fr .8fr;gap:3rem}.hero h1{font:normal clamp(3rem,7vw,6.5rem)/1 Georgia,serif;letter-spacing:-.03em}.hero em{color:#edc888}.hold{border-left:3px solid #edc888;padding:1rem 1.4rem;background:#292b27}.gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.2rem}.card{min-width:0;display:flex;flex-direction:column;border:1px solid #7b6d52;background:#1e2624}.media{min-height:190px;padding:1rem;display:grid;place-items:center;text-align:center;background:repeating-linear-gradient(135deg,#27312e 0 14px,#212b29 14px 28px);color:#eecb8b;font:700 .8rem/1.65 ui-monospace,monospace}.media span{background:#19201f;border:1px solid #aa956b;padding:1rem}.inside{padding:1.25rem;display:flex;flex:1;flex-direction:column;gap:.7rem}.kicker{font:700 .75rem ui-monospace,monospace;letter-spacing:.05em;color:#f7d18b}.inside h2{font:normal clamp(1.5rem,2.2vw,2rem)/1.2 Georgia,serif;margin:0}.inside .meta{color:#e0d2bb}.inside details{margin-top:auto;border-top:1px solid #776950;padding-top:.5rem}.inside summary{cursor:pointer;padding:.65rem 0;min-height:44px;color:#f7d18b;font-weight:700}.inside strong{color:#f7d18b}.links{display:flex;gap:.5rem;flex-wrap:wrap}.links a{display:inline-flex;align-items:center;min-height:44px;border:1px solid #9c8967;padding:.4rem .65rem;font-size:.9rem}.select{border-top:1px solid #776950;padding-top:.7rem;min-height:44px;display:flex;gap:.6rem;align-items:center}.select input{width:22px;height:22px;accent-color:#edc888}.compare{border:1px solid #a88d64;background:#29312d;margin:2rem 0;padding:1.5rem}.compare h2{font:normal 2rem Georgia,serif}.compare table{width:100%;border-collapse:collapse;table-layout:fixed}.compare td,.compare th{border:1px solid #a28d70;padding:.6rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}.compare button{font:700 1rem system-ui;min-height:44px;background:#efd092;color:#151a18;border:1px solid #efd092;padding:.6rem 1rem;cursor:pointer}.method,footer{max-width:830px;padding:1.5rem 0}footer{border-top:1px solid #786a53}.print{display:none}[hidden]{display:none!important}@media(max-width:1000px){.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}.hero{grid-template-columns:1fr;gap:1rem}}@media(max-width:650px){.gallery{grid-template-columns:1fr}.media{min-height:140px}.compare{padding:.6rem}.compare td,.compare th{padding:.4rem;font-size:.85rem}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}@media(forced-colors:active){.card,.media,.compare,.hold{background:Canvas;border-color:CanvasText}.media span,.kicker{color:CanvasText}.compare button{background:ButtonFace;color:ButtonText}}@media print{body,.card,.hold{background:white!important;color:black!important}.shell{width:100%}.hero{display:block;padding:0}.hero h1{font-size:24pt}.gallery{display:block}.card{break-inside:avoid;margin:.5rem 0}.media,.select,.compare,.links,.method,footer{display:none!important}.inside{padding:.5rem;gap:0}.inside h2{font-size:17pt}.inside details{display:none}.inside .print{display:block!important;color:black!important;overflow-wrap:anywhere}.inside .meta,.inside .kicker,.inside strong{color:black!important}}"""
JS="""(()=>{'use strict';const root=document.querySelector('[data-gallery]');if(!root)return;const boxes=[...root.querySelectorAll('[data-select]')];const cards=[...root.querySelectorAll('[data-card]')];const groups=[...root.querySelectorAll('[data-compare-controls]')];const panel=root.querySelector('#comparison');const state=root.querySelector('#compare-status');const reset=root.querySelector('#compare-reset');const headings=[...root.querySelectorAll('[data-heading]')];const cells=[...root.querySelectorAll('[data-value]')];if(boxes.length!==6||cards.length!==6||groups.length!==7||!panel||!state||!reset||headings.length!==2||cells.length!==10)return;const ids=new Map(cards.map(c=>[c.dataset.card,c]));if(ids.size!==6)return;function update(){const selected=boxes.filter(b=>b.checked);panel.hidden=selected.length!==2;if(selected.length===2){const pair=selected.map(b=>ids.get(b.value));const fields=['title','catalog','date','can','cannot'];pair.forEach((c,j)=>headings[j].textContent='Source '+c.dataset.card);fields.forEach((field,i)=>pair.forEach((c,j)=>cells[2*i+j].textContent=c.dataset[field]));state.textContent='Comparing two documented records. No historical relationship inferred.'}else{state.textContent=selected.length?'One source selected. Choose one more.':'Select exactly two records for a custody comparison.'}}boxes.forEach(b=>b.addEventListener('change',()=>{if(b.checked&&boxes.filter(x=>x.checked).length>2){b.checked=false;state.textContent='Only two records can be compared. Clear another first.';return}update()}));reset.addEventListener('click',()=>{boxes.forEach(b=>b.checked=false);update();boxes[0].focus()});groups.forEach(x=>x.hidden=false);update()})();"""

def render(rows):
    parts=[]
    for a in rows:
        n=a["id"];kind="RETROSPECTIVE EXHIBIT / 2017" if n in ("04","06") else "DOCUMENTED HISTORICAL PHOTOGRAPH"
        parts.append(f'<article class="card" id="gallery-{n}" data-card="{n}" data-title="{esc(a["title"])}" data-catalog="{esc(a["catalog"])}" data-date="{esc(a["date"])}" data-can="{esc(a["can"])}" data-cannot="{esc(a["cannot"])}"><div class="media" role="note"><span>ARCHIVAL IMAGE WITHHELD<br>INDIVIDUAL RIGHTS REVIEW PENDING<br>RECORD {n}</span></div><div class="inside"><p class="kicker">SOURCE {n} / 06 · {kind}</p><h2>{esc(a["title"])}</h2><p class="meta">{esc(a["catalog"])}{" · provisional association" if a["provisional"] else ""}<br>{esc(a["date"])}</p><details><summary>SourceDrawer · context and limitations</summary><p><strong>Establishes:</strong> {esc(a["can"])}</p><p><strong>Does not establish:</strong> {esc(a["cannot"])}</p><p><strong>Media rights:</strong> INDIVIDUAL REVIEW REQUIRED</p></details><div class="links"><a href="{esc(a["url"])}" target="_blank" rel="noopener noreferrer">NASA source {n} ↗</a><a href="R93_SOURCE_PASSPORTS.html#passport-{n}">Passport</a><a href="R87_PHOTOGRAPH_DATE_RAIL.html#r87-record-{n}">Chronology</a><a href="R94_CURATED_ATLAS.html#atlas-{n}">Atlas</a></div><p class="print">NASA: {esc(a["url"])}<br>Photographic reuse: INDIVIDUAL REVIEW REQUIRED<br>Establishes: {esc(a["can"])}<br>Does not establish: {esc(a["cannot"])}</p><div data-compare-controls hidden class="select"><input id="compare-{n}" type="checkbox" value="{n}" data-select><label for="compare-{n}">Compare source {n}</label></div></div></article>')
    rows_html=''.join('<tr><th scope="row">'+field+'</th><td data-value></td><td data-value></td></tr>' for field in ("Title","NASA catalog","Photograph date","Establishes","Does not establish"))
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Apollo source gallery · STAGING HOLD</title><link rel="stylesheet" href="source_gallery_r97.css"><script defer src="source_gallery_r97.js"></script></head><body><a href="#gallery" class="skip">Skip to evidence</a><div class="shell" data-gallery><div class="mast">FINAL VESTIGE STUDIOS / APOLLO RESEARCH DESK / PHOTO-FREE SOURCE GALLERY</div><header class="hero"><div><p class="kicker">SIX NASA SOURCES · ZERO CLEARED IMAGES</p><h1>The image<br><em>and the absence.</em></h1><p>Study historical photographic records without reproducing unreviewed images or pretending the surviving evidence can say more than it does.</p></div><div class="hold" role="note"><strong>STAGING HOLD · NOT FOR PUBLICATION.</strong><p>The crew portrait S67-19766 association and exact day remain provisional. Two 2017 tribute displays are retrospective, not images of the 1967 fire.</p><p>No NASA photographs, invented archival images, inferred map pins or speculative connections appear here.</p></div></header><main id="gallery"><p>Source-register order, not accident chronology. All six references are available without JavaScript.</p><section class="gallery" aria-label="Six NASA source records">'+''.join(parts)+'</section><section class="compare" data-compare-controls hidden aria-labelledby="compare-title"><h2 id="compare-title">Compare source custody</h2><p>Comparing two records does not imply shared location, sequence or causation.</p><p role="status" aria-live="polite" id="compare-status">Select two records.</p><div id="comparison" hidden><table><caption>Side-by-side independently recorded sources</caption><thead><tr><th scope="col">Field</th><th scope="col" data-heading>Source one</th><th scope="col" data-heading>Source two</th></tr></thead><tbody>'+rows_html+'</tbody></table><p>No photographic reuse has been cleared.</p></div><button type="button" id="compare-reset">Clear comparison</button></section><section class="method"><h2>Evidence is not permission</h2><p>NASA source links are not photographic-use clearance. See <a href="R85_NASA_SOURCE_REVIEW.html">photographic rights board</a> and <a href="R88_READING_ROOM.html">Research Reading Room</a>.</p></section></main><footer>STAGING HOLD · No WordPress changes, geo pins, images, external scripts, or deployment.</footer></div></body></html>'

def build(src,out,archive=None):
    rows,expected=load(src)
    if out.exists() and any(out.iterdir()):raise ValueError("R97_NONEMPTY_OUTPUT")
    if archive and archive.exists():raise ValueError("R97_EXISTING_ARCHIVE")
    out.mkdir(parents=True,exist_ok=True)
    for name in sorted(expected):
        (out/name).write_bytes((src/name).read_bytes())
    for name,s in {"R97_SOURCE_GALLERY.html":render(rows),"source_gallery_r97.css":CSS,"source_gallery_r97.js":JS}.items():
        (out/name).write_text(s,encoding="utf-8")
    receipt={"schema":"fv.apollo.r97.gallery.v1","release":"STAGING_HOLD","publication_approved":False,"photo_rights_cleared":0,"images_embedded":0,"geo_pins":0,"inferred_edges":0,"records":6,"inherited_receipt_sha256":sha(src/"R94_ATLAS_RECEIPT.json"),"files":{p.name:sha(p) for p in sorted(out.iterdir())}}
    (out/"R97_GALLERY_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    if archive:
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,"w",compression=ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(out.iterdir()):
                info=ZipInfo(p.name,date_time=(1980,1,1,0,0,0))
                info.compress_type=ZIP_DEFLATED;info.create_system=3;info.external_attr=0o100644<<16
                z.writestr(info,p.read_bytes())
    return receipt

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--src",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--archive",type=Path)
    args=a.parse_args()
    print(json.dumps(build(args.src,args.out,args.archive),sort_keys=True))
