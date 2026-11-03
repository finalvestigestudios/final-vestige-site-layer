#!/usr/bin/env python3
"""Apollo R94: text-first, no-map curated Atlas derived only from verified R93 source passports."""
import argparse,hashlib,html,json,re
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

# R95: explicit R92/R93 staging input contract. These are inherited artifact names,
# not permission for a caller to attach arbitrary browser-executable assets.
R92_INPUTS=frozenset((
    "R85_NASA_SOURCE_REVIEW.html","R85_RIGHTS_RECEIPT.json",
    "R87_PHOTOGRAPH_DATE_RAIL.html","R87_RAIL_RECEIPT.json",
    "R88_READING_ROOM.html","R88_READING_ROOM_RECEIPT.json",
    "R89_INTEGRITY_RECEIPT.json","R89_REVIEW_HUB.html",
    "R91_ASSET_BOUNDARY_RECEIPT.json","R92_RECIPROCAL_ROUTES_RECEIPT.json",
    "chronology_r87.css","reading_room_r88.css","reading_room_r88.js",
    "review_hub_r89.css","rights_board_r85.css",
))
R93_INPUTS=frozenset((
    "R93_SOURCE_PASSPORTS.html","R93_SOURCE_PASSPORTS.json",
    "R93_NASA_REFERENCES.txt","R93_PASSPORT_RECEIPT.json",
    "source_passports_r93.css","source_passports_r93.js",
))
R91_PINNED_ASSETS=frozenset((
    "R85_NASA_SOURCE_REVIEW.html","R87_PHOTOGRAPH_DATE_RAIL.html",
    "R88_READING_ROOM.html","R89_REVIEW_HUB.html",
    "chronology_r87.css","reading_room_r88.css","reading_room_r88.js",
    "review_hub_r89.css","rights_board_r85.css",
))
def verify_input_inventory(src):
    """Admit the complete sealed input set; reject extra scripts, files, dirs and links."""
    if src.is_symlink() or not src.is_dir():
        raise ValueError("R94_UNREVIEWED_ASSET:SOURCE_NOT_DIRECTORY")
    actual={p.name:p for p in src.iterdir()}
    expected=R92_INPUTS|R93_INPUTS
    extra=sorted(actual.keys()-expected)
    missing=sorted(expected-actual.keys())
    if extra:raise ValueError("R94_UNREVIEWED_ASSET:"+extra[0])
    if missing:raise ValueError("R94_CUSTODY_FILE_MISSING:"+missing[0])
    for name,p in actual.items():
        if p.is_symlink() or not p.is_file():
            raise ValueError("R94_UNREVIEWED_ASSET:NONREGULAR:"+name)
    custody=read(src/"R91_ASSET_BOUNDARY_RECEIPT.json")
    if (custody.get("schema")!="fv.apollo.r91.asset-boundary.v1"
        or custody.get("release")!="STAGING_HOLD"
        or custody.get("photographic_rights_cleared")!=0
        or custody.get("network_asset_dependencies")!=0
        or custody.get("deployment_allowed") is not False
        or custody.get("source_bindings_inherited")!=24
        or set(custody.get("files",{}))!=R91_PINNED_ASSETS):
        raise ValueError("R94_INHERITED_ASSET_CUSTODY_GATE")
    for name,meta in custody["files"].items():
        if not isinstance(meta,dict) or sha(src/name)!=meta.get("sha256"):
            raise ValueError("R94_INHERITED_ASSET_HASH_MISMATCH:"+name)
    return [actual[name] for name in sorted(actual)]

def load(src):
    verified_files=verify_input_inventory(src)
    p=read(src/"R93_PASSPORT_RECEIPT.json");r=read(src/"R92_RECIPROCAL_ROUTES_RECEIPT.json")
    rights=read(src/"R85_RIGHTS_RECEIPT.json");book=read(src/"R93_SOURCE_PASSPORTS.json")
    if (p.get("schema")!="fv.apollo.r93.build.v1" or p.get("release")!="STAGING_HOLD"
        or p.get("publication_approved") is not False or p.get("photographic_rights_cleared")!=0
        or p.get("verified_source_passports")!=6 or p.get("new_geo_pins")!=0
        or p.get("new_historical_edges")!=0 or p.get("source_r92_receipt_sha256")!=sha(src/"R92_RECIPROCAL_ROUTES_RECEIPT.json")
        or r.get("source_bindings")!=24 or r.get("reviewed_geographic_pins")!=0
        or r.get("photographic_rights_cleared")!=0 or r.get("release")!="STAGING_HOLD"
        or rights.get("rights_cleared")!=0 or rights.get("images_embedded")!=0
        or rights.get("geographic_pins")!=0 or rights.get("release")!="STAGING_HOLD"):
        raise ValueError("R94_CUSTODY_OR_RELEASE_GATE")
    for receipt in (p,r):
        for name,expected in receipt["files"].items():
            if not re.fullmatch("[A-Za-z0-9_.-]+",name) or not (src/name).is_file() or sha(src/name)!=expected:
                raise ValueError("R94_CUSTODY_FILE_MISMATCH:"+name)
    if len(p["files"])!=5 or book.get("photo_reuse_approved") is not False or book.get("schema")!="fv.apollo.r93.passports.v1":
        raise ValueError("R94_PASSPORT_GATE")
    rows=book["records"];refs=rights["records"]
    if [x["id"] for x in rows]!=[f"{n:02}" for n in range(1,7)] or [x["id"] for x in refs]!=[f"{n:02}" for n in range(1,7)]:
        raise ValueError("R94_REGISTER_SIZE")
    for a,b in zip(rows,refs):
        n=a["id"]
        if (a["url"]!=b["url"] or a["catalog"]!=b["catalog"]
            or a["rights"]!="INDIVIDUAL REVIEW REQUIRED" or b["media_review"]!="INDIVIDUAL_REVIEW_REQUIRED"
            or a["provisional"] is not (n=="01") or not all(a.get(k) for k in ("title","can","cannot"))
            or not re.fullmatch(r"https://www\.nasa\.gov/image-detail/[a-z0-9_-]+/",a["url"])):
            raise ValueError("R94_SOURCE_OR_RIGHTS_MISMATCH:"+n)
        if n=="01" and (a["date"]!="January 1967 — day unconfirmed" or b["date_precision"]!="MONTH_ONLY" or b["identity"]!="PROVISIONAL_NO_PAGE_PIA"):
            raise ValueError("R94_MONTH_ONLY_DAY_INVENTED")
        if n!="01" and b["date_precision"]!="DAY":raise ValueError("R94_DATE_PRECISION_MISMATCH")
        if n in ("04","06") and a["date"]!="January 24, 2017":raise ValueError("R94_TRIBUTE_SEQUENCE_INVENTED")
    return rows
def e(v):return html.escape(str(v),quote=True)
CSS="""*{box-sizing:border-box}body{margin:0;background:#181b1d;color:#f0e9d9;font:16px/1.6 system-ui,sans-serif}a{color:#f4d089;overflow-wrap:anywhere;text-underline-offset:.2em}a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #f8d68f;outline-offset:4px}.shell{width:min(1180px,calc(100% - 2rem));margin:auto}.skip{position:absolute;top:-10rem;left:1rem;padding:1rem;background:#fff;color:#111}.skip:focus{top:1rem}header{padding:clamp(2.5rem,7vw,6rem) 0 2rem;border-bottom:1px solid #746a56}.kicker,.index{font-size:.78rem;letter-spacing:.09em;color:#edc782;font-weight:700}h1{font:normal clamp(2.5rem,6vw,5rem)/1.1 Georgia,serif}h1 em{color:#edc782}h2{font:normal clamp(1.8rem,3.2vw,2.6rem)/1.2 Georgia,serif}h3{font:normal 1.6rem/1.3 Georgia,serif}.lead{max-width:800px;font-size:1.14rem;color:#e5d8c6}.hold{max-width:950px;padding:1.1rem 1.3rem;background:#39332a;border-left:5px solid #edc782}.jump,.routes,.buttons{display:flex;flex-wrap:wrap;gap:.6rem}.jump a,.routes a,.source{min-height:44px;display:inline-flex;align-items:center;border:1px solid #ac9470;padding:.55rem .85rem}.jump{margin:1.7rem 0}.head{display:flex;justify-content:space-between;align-items:end;gap:2rem;margin:2rem 0}.head>div{max-width:700px}.status{border:1px solid #988364;padding:.7rem 1rem}.filters{border:1px solid #958364;background:#252b2c;padding:1.2rem;margin:1.5rem 0}.filters[hidden],.card[hidden],.empty[hidden]{display:none!important}button{min-height:44px;font:inherit;color:#f0e9d9;border:1px solid #a79374;background:#192023;padding:.6rem .9rem;cursor:pointer}button[aria-pressed=true]{background:#edc782;color:#1d2223;font-weight:bold}label{display:block;font-weight:bold;margin:1rem 0 .3rem}input{width:min(100%,420px);min-height:44px;padding:.65rem;font:inherit;background:#fff;color:#111}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.card{min-width:0;background:#22282a;border:1px solid #7c6c54;padding:clamp(1rem,2.5vw,2rem);scroll-margin-top:1rem}.card:target{outline:2px solid #edc782;outline-offset:3px}.card dt,.card strong{color:#f4d089}.card dl{display:grid;grid-template-columns:minmax(8rem,.5fr) minmax(0,1fr);gap:.3rem .8rem}.card dd{margin:0;overflow-wrap:anywhere}.card details{padding:.5rem;border:1px solid #958364}.card summary{min-height:44px;padding:.65rem;cursor:pointer}.routes{margin:.8rem 0}.method{max-width:810px;border-top:1px solid #958364;margin:4rem 0 2rem}footer{border-top:1px solid #958364;padding:2rem 0;color:#e5d8c6}.print{display:none}@media(max-width:730px){.grid{grid-template-columns:1fr}.head{display:block}.card dl{grid-template-columns:1fr}.jump a{flex:1 1 110px}}@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}html{scroll-behavior:auto}}@media(forced-colors:active){.card,.filters,.hold{border-color:CanvasText}a{color:LinkText}button[aria-pressed=true]{background:Highlight;color:HighlightText}}@media print{html,body,.card,.hold{background:#fff!important;color:#000!important}.shell{width:100%}h1{font-size:26pt}h3{font-size:16pt}.card,.card[hidden]{display:block!important;break-inside:avoid;margin:.5rem 0;padding:.7rem;border:1px solid #555}.grid{display:block}.jump,.filters,.method,.status,.source,.card details,footer{display:none!important}.card dt,.card strong,.index{color:#000!important}.print{display:block!important;color:#000!important;overflow-wrap:anywhere}}"""
JS='''"use strict";(()=>{const panel=document.querySelector("#filters"),cards=[...document.querySelectorAll(".card")],buttons=[...document.querySelectorAll("[data-filter]")],search=document.querySelector("#query"),status=document.querySelector("#count"),empty=document.querySelector("#empty");if(!panel||cards.length!==6||buttons.length!==3||!search||!status||!empty)return;let mode="all";function update(){let n=0;const q=search.value.trim().toLocaleLowerCase();cards.forEach(c=>{const show=(mode==="all"||c.dataset.precision===mode)&&c.dataset.search.includes(q);c.hidden=!show;if(show)n++});buttons.forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.filter===mode)));status.textContent="Showing "+n+" of 6 records.";empty.hidden=n!==0}buttons.forEach(b=>b.addEventListener("click",()=>{if(!["all","day","month"].includes(b.dataset.filter))return;mode=b.dataset.filter;update()}));search.addEventListener("input",update);panel.hidden=false;update()})();'''
def render(rows):
    parts=[]
    for a in rows:
        n=a["id"];kind="month" if a["provisional"] else "day"
        routes="".join('<a href="'+path+"#"+prefix+n+'">'+label+"</a>" for path,prefix,label in [
           ("R93_SOURCE_PASSPORTS.html","passport-","Source passport"),("R88_READING_ROOM.html","r88-","EvidencePlate"),
           ("R87_PHOTOGRAPH_DATE_RAIL.html","r87-record-","ChronologyRail"),("R85_NASA_SOURCE_REVIEW.html","r85-source-","Rights board")])
        parts.append('<article class="card" id="atlas-'+n+'" data-precision="'+kind+'" data-search="'+e((a["title"]+" "+a["catalog"]).casefold())+'">'+
          '<p class="index">SOURCE '+n+' / 06 · REUSE PENDING</p><h3>'+e(a["title"])+'</h3>'+
          '<dl><dt>NASA catalog claim</dt><dd>'+e(a["catalog"])+(" · provisional" if a["provisional"] else "")+'</dd>'+
          '<dt>Photo date</dt><dd>'+e(a["date"])+'</dd><dt>Date certainty</dt><dd>'+("Month only; exact day unknown" if a["provisional"] else "Specific photographic day")+'</dd></dl>'+
          '<p><strong>What it can establish:</strong> '+e(a["can"])+'</p>'+
          '<p><strong>What it cannot establish:</strong> '+e(a["cannot"])+'</p>'+
          '<p><a class="source" href="'+e(a["url"])+'" rel="noopener noreferrer" target="_blank">NASA source '+n+' ↗</a></p>'+
          '<details><summary>SourceDrawer · other views of source '+n+'</summary><p>Different presentations of the same source; no inferred event connections.</p>'+
          '<nav class="routes" aria-label="Other views of source '+n+'">'+routes+'</nav><p>Image reuse remains unreviewed.</p></details>'+
          '<p class="print">NASA: '+e(a["url"])+'<br>Photographic reuse: INDIVIDUAL REVIEW REQUIRED</p></article>')
    links="".join('<a href="#atlas-'+f"{i:02}"+'">Source '+f"{i:02}"+"</a>" for i in range(1,7))
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Apollo · Curated Evidence Atlas · STAGING HOLD</title><link rel="stylesheet" href="curated_atlas_r94.css"><script src="curated_atlas_r94.js" defer></script></head><body><a class="skip" href="#atlas">Skip to six sources</a><div class="shell"><header><p class="kicker">FINAL VESTIGE STUDIOS / APOLLO EVIDENCE STUDIO</p><p class="kicker">CURATED EVIDENCE ATLAS / TEXT-FIRST SOURCE INDEX</p><h1>Locate the evidence.<br><em>Not imagined places.</em></h1><p class="lead">Six NASA source records, each with evidence boundaries and precise source custody. This is not a map: photographic source pages do not establish reviewed coordinates or historical connections.</p><p class="hold" role="note"><strong>STAGING HOLD · NOT FOR PUBLICATION.</strong> Zero of six photo-use reviews completed. S67-19766 and its exact photographic day remain provisional. Two 2017 tribute photographs share January 24 without a claimed order. These photo dates do not reconstruct the January 27, 1967 Apollo 1 fire. No NASA photographs are embedded.</p><nav class="jump" aria-label="Jump to sources">'''+links+'''</nav></header><main id="atlas"><div class="head"><div><p class="kicker">REGISTER ORDER, NOT ACCIDENT CHRONOLOGY</p><h2>Six sourced records</h2><p>All records and source links are readable without JavaScript. Optional view filters do not change historical claims or reuse status.</p></div><p id="count" role="status" aria-live="polite" class="status">Showing all 6 of 6 records.</p></div><section class="filters" id="filters" aria-label="Optional source filters" hidden><p>Date certainty</p><div class="buttons" role="group" aria-label="Photographic date precision"><button type="button" data-filter="all" aria-pressed="true">All six</button><button type="button" data-filter="day" aria-pressed="false">Specific-day records (5)</button><button type="button" data-filter="month" aria-pressed="false">Month only (1)</button></div><label for="query">Search title or catalog</label><input id="query" type="search" autocomplete="off" placeholder="e.g. S67-15717"></section><div class="grid">'''+''.join(parts)+'''</div><p id="empty" class="empty" hidden>No records match these view filters. Clear the search or select All six.</p><section class="method"><h2>Why there are no geo pins</h2><p>No coordinates or map edges are independently audited for these sources. A future geospatial Atlas needs individual archival location evidence and editorial sign-off, not inferred relationships.</p><p>NASA linking is not photo-use clearance. <a href="R85_NASA_SOURCE_REVIEW.html">Rights board</a> · <a href="R93_SOURCE_PASSPORTS.html">Source passports</a>.</p></section></main><footer>Isolated staging. No WordPress, photographs, speculative map connections or deployment.</footer></div></body></html>'''
def build(src,out,archive=None):
    if out.exists() and any(out.iterdir()):raise ValueError("R94_NONEMPTY_OUTPUT")
    if archive and archive.exists():raise ValueError("R94_ARCHIVE_EXISTS")
    data=load(src);out.mkdir(parents=True,exist_ok=True)
    for p in verify_input_inventory(src):
        (out/p.name).write_bytes(p.read_bytes())
    new={"R94_CURATED_ATLAS.html":render(data),"curated_atlas_r94.css":CSS,"curated_atlas_r94.js":JS}
    for n,s in new.items():(out/n).write_text(s)
    receipt={"schema":"fv.apollo.r94.curated-atlas.v1","release":"STAGING_HOLD","publication_approved":False,
      "photo_rights_cleared":0,"geo_pins":0,"inferred_edges":0,"source_count":6,
      "precision":{"day":5,"month":1},"r93_receipt_sha256":sha(src/"R93_PASSPORT_RECEIPT.json"),
      "files":{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    (out/"R94_ATLAS_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    if archive:
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,"w",compression=ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(out.iterdir()):
                item=ZipInfo(p.name,date_time=(1980,1,1,0,0,0))
                item.compress_type=ZIP_DEFLATED;item.create_system=3;item.external_attr=0o100644<<16
                z.writestr(item,p.read_bytes())
    return receipt
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--src",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True);a.add_argument("--archive",type=Path)
    v=a.parse_args();print(json.dumps(build(v.src,v.out,v.archive),sort_keys=True))
