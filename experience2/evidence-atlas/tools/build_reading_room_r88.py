#!/usr/bin/env python3
"""R88 isolated, no-publication Apollo comparative source reader. Verified data only."""
from __future__ import annotations
import hashlib
import html
import importlib.util
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R87 = HERE / 'build_chronology_r87.py'
CSS = HERE / 'reading_room_r88.css'
JS = HERE / 'reading_room_r88.js'
FILES = [
 'experience2/evidence-atlas/tools/build_reading_room_r88.py',
 'experience2/evidence-atlas/tools/reading_room_r88.css',
 'experience2/evidence-atlas/tools/reading_room_r88.js',
 'experience2/evidence-atlas/tests/test_reading_room_r88.py',
 'experience2/evidence-atlas/tests/browser_reading_room_r88.py',
 'experience2/evidence-atlas/R88_READING_ROOM_STAGING_HOLD.md',
 '.github/workflows/ex2-apollo-r88-reading-room.yml',
]
def sha(data):return hashlib.sha256(data).hexdigest()
def e(value):return html.escape(str(value),quote=True)
def imported(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    item=importlib.util.module_from_spec(spec)
    sys.modules[name]=item
    spec.loader.exec_module(item)
    return item

def verified_records():
    rail=imported(R87,'r87_verified_reader')
    concordance=imported(rail.R86,'r86_verified_reader')
    report=concordance.verify()  # Actual Research Desk + generated Atlas against source registers.
    groups, uncertain=rail.verified_groups(report,json.loads(rail.CROSSWALK.read_text('utf8')))
    assert len(report['records'])==6 and len(groups)==4 and len(uncertain)==1
    assert all(r['id']=='01' for r in uncertain)
    return rail,report,groups,uncertain

def page(records):
    cards=[]
    for r in records:
        identity=('PROVISIONAL — linked NASA page has no structured PIA' if r['id']=='01'
                  else 'PIA identified on the linked NASA page')
        certainty=('Month only — cannot place in a day-ordered chronology' if r['id']=='01'
                   else 'Day-specific photograph date; not an accident-event date')
        cards.append(f'''<article class="record" id="r88-{e(r['id'])}" data-record="{e(r['id'])}"
 data-title="{e(r['title'])}" data-catalog="{e(r['catalog'])}"
 data-date="{e(r['date'])}" data-limit="{e(r['limitation'])}" aria-labelledby="r88-title-{e(r['id'])}">
<p class="overline">EVIDENCE PLATE {e(r['id'])} / 06 · {e(r['precision'])}</p>
<h3 id="r88-title-{e(r['id'])}">{e(r['title'])}</h3>
<p><strong>Catalog:</strong> {e(r['catalog'])}</p>
<p><strong>Photograph date:</strong> {e(r['date'])}</p>
<p class="boundary"><strong>What it can establish:</strong> {e(r['scope'])}</p>
<p class="boundary"><strong>What it cannot establish:</strong> {e(r['limitation'])}</p>
<details><summary>SourceDrawer · custody, limitations and photographic rights</summary>
<dl><dt>NASA identity</dt><dd>{e(identity)}</dd><dt>Date certainty</dt><dd>{e(certainty)}</dd>
<dt>Credit on NASA page</dt><dd>{e(r['credit'])}</dd>
<dt>Cross-component match</dt><dd>Actual Research Desk + generated Evidence Atlas + source register: verified</dd>
<dt>Media rights</dt><dd><strong>INDIVIDUAL REVIEW REQUIRED</strong> — source metadata is not image-use permission.</dd>
<dt>Exact NASA link</dt><dd class="raw-url">{e(r['url'])}</dd></dl></details>
<div class="actions"><a class="source" href="{e(r['url'])}" target="_blank" rel="noopener noreferrer">NASA source {e(r['id'])} ↗</a>
<a class="rail-link" href="R87_PHOTOGRAPH_DATE_RAIL.html#r87-record-{e(r['id'])}">Find in photograph-date rail</a></div>
<p class="print-url"><strong>Official NASA source:</strong> {e(r['url'])} · <strong>Photo-specific rights:</strong> INDIVIDUAL REVIEW REQUIRED</p>
<label class="compare-choice" hidden><input type="checkbox" value="{e(r['id'])}"> Select for side-by-side source comparison</label>
</article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Apollo 1 · Research Reading Room · STAGING HOLD</title>
<link rel="stylesheet" href="reading_room_r88.css"><script src="reading_room_r88.js" defer></script></head><body>
<a href="#r88-main" class="skip">Skip to six source records</a>
<div class="shell"><header><p class="brand">FINAL VESTIGE STUDIOS / APOLLO EVIDENCE STUDIO / UNPUBLISHED STAGING</p>
<p class="overline">RESEARCH DESK × EVIDENCE ATLAS / INTERACTIVE READING ROOM</p>
<h1>Compare the sources.<br><em>Not the assumptions.</em></h1>
<p class="lead">Six source-linked NASA photograph records. The actual Research Desk and generated Evidence Atlas agree on their identity, dates and provenance. This desk lets readers examine what each record <strong>can and cannot establish.</strong></p>
<p class="hold" role="note"><strong>STAGING HOLD · 0/6 individual photo-use assessments completed.</strong> No photographs embedded. The proposed S67-19766 crew-portrait identity remains provisional; its day is unknown. Two 2017 tribute photographs share a date without a verified order. Photograph dates never reconstruct the January 27, 1967 fire.</p>
<nav class="routes" aria-label="Research routes"><a href="#r88-main">Six source records</a><a href="#r88-method">Source custody method</a><a href="R87_PHOTOGRAPH_DATE_RAIL.html">Photograph-date ChronologyRail ↗</a></nav>
</header><main id="r88-main"><section aria-labelledby="r88-index"><h2 id="r88-index">Evidence plates · source register order</h2>
<p>Cards use custody-record order, not accident chronology. Each SourceDrawer is a native disclosure; links and full evidence remain available without JavaScript.</p>
<div class="records">{''.join(cards)}</div></section>
<section class="compare-panel" id="r88-compare" hidden aria-labelledby="r88-compare-title">
<h2 id="r88-compare-title">Compare two records</h2><p>Select up to two checkboxes; the comparison is a reading aid, not a new claim of historical connection.</p>
<p class="compare-status" aria-live="polite" aria-atomic="true">No sources selected.</p>
<div class="comparison" role="group" aria-label="Selected source comparison"></div>
<button type="button" class="clear">Clear selections</button></section>
<section class="method" id="r88-method" aria-labelledby="r88-method-title"><h2 id="r88-method-title">How source custody was checked</h2>
<p>Before this page is generated, the build compares each evidence plate with the actual Research Desk markup, the generated Evidence Atlas and the R37/R79/R55 NASA source and rights registers. A source identity, photographic date, unresolved right, or catalog-status mismatch prevents output.</p>
<p>The month-only portrait remains outside the four day-specific photograph-date milestones. Neither the chronology nor a source comparison implies a causal relationship. NASA source links are not media licenses or evidence of NASA endorsement.</p>
<p>Official guidance: <a href="https://www.nasa.gov/nasa-brand-center/">NASA Brand Center ↗</a>. Individual rights checks, independent QA, hosted-platform acceptance and founder publication approval remain pending.</p></section>
</main><footer><p><strong>NOT DEPLOYABLE · DO NOT MERGE</strong> — No geographic pins, speculative edges, image binaries or third-party scripts. This component is a source-controlled research preview only.</p></footer></div></body></html>'''

def build(out):
    rail,report,groups,uncertain=verified_records()
    assert all(r['identity'] in ('PIA_ON_OFFICIAL_PAGE','PROVISIONAL_NO_PAGE_PIA') for r in report['records'])
    assert all(re.fullmatch(r'https://www\.nasa\.gov/image-detail/[a-z0-9_\-/]+/',r['url']) for r in report['records'])
    assert sorted(r['id'] for r in report['records'])==['01','02','03','04','05','06']
    generated=page(report['records']).encode('utf8')
    if re.search(rb'<(?:img|picture|iframe|video)\b|data-(?:lat|lon|geo-edge)\b',generated,re.I):
        raise ValueError('R88_UNREVIEWED_MEDIA_OR_GEO')
    out.mkdir(parents=True,exist_ok=True)
    # R87 builder checks parity again, and writes the exact referenced rail.
    rail.build(out)
    (out/'R88_READING_ROOM.html').write_bytes(generated)
    (out/'reading_room_r88.css').write_bytes(CSS.read_bytes())
    (out/'reading_room_r88.js').write_bytes(JS.read_bytes())
    receipt={'schema':'fv.apollo.r88.reading-room.v1','release':'STAGING_HOLD',
        'records':6,'photo_rights_cleared':0,'photographs_embedded':0,'inferred_geographic_edges':0,
        'publication_approved':False,'hosted_wordpress_verified':False,
        'chronology_milestones':[d for d,_ in groups],
        'unplaced_ids':[r['id'] for r in uncertain],
        'component_provenance':report['sha256'],
        'files':{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file() and p.name != 'R88_READING_ROOM_RECEIPT.json'}}
    (out/'R88_READING_ROOM_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt

def package(out,destination):
    content={'source/'+p:(ROOT/p).read_bytes() for p in FILES}
    for f in out.iterdir():
        if f.is_file():content['built/'+f.name]=f.read_bytes()
    content['SHA256_MANIFEST.json']=(json.dumps({'release':'STAGING_HOLD','not_deployable':True,
        'files':{p:sha(data) for p,data in sorted(content.items())}},sort_keys=True,indent=2)+'\n').encode()
    destination.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(destination,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in sorted(content.items()):
            meta=ZipInfo(name,date_time=(1980,1,1,0,0,0));meta.compress_type=ZIP_DEFLATED
            meta.external_attr=0o100644<<16;meta.create_system=3
            archive.writestr(meta,data)
    return sha(destination.read_bytes())

if __name__=='__main__':
    try:
        dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path('dist/apollo-r88')
        build(dest)
        if len(sys.argv)>2:print('R88 deterministic package',package(dest,Path(sys.argv[2])))
        print('R88 STAGING HOLD: six verified sources, compare reader, no rights cleared.')
    except Exception:
        print('R88_CUSTODY_HOLD: withheld output; source or build validation failed',file=sys.stderr)
        sys.exit(1)
