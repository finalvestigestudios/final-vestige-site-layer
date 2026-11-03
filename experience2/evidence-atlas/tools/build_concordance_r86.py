#!/usr/bin/env python3
"""R86 verified source concordance across the actual Desk and Atlas. STAGING HOLD."""
from __future__ import annotations
import hashlib, html, importlib.util, json, re, sys
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
DESK=ROOT/'experience2/research-desk/templates/ledger.html'
ATLAS=ROOT/'experience2/evidence-atlas/build_atlas.py'
CSS=HERE/'concordance_r86.css'
IDS=tuple(f'{i:02d}' for i in range(1,7))

def hold(code):
    raise ValueError('R86_CUSTODY_HOLD:'+code)

def hash256(data):
    return hashlib.sha256(data).hexdigest()

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj

class SourceArticles(HTMLParser):
    """Bind each NASA link to its *specific rendered article*, not the whole page."""
    def __init__(self,component):
        super().__init__(convert_charrefs=True)
        self.component=component
        self.open_article=None
        self.cards={}
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if tag=='article':
            if self.open_article is not None:
                hold('NESTED_ARTICLE')
            if self.component=='desk' and 'data-fvx-record' in a:
                m=re.fullmatch(r'fv-ex2-ledger-apollo1-record-(\d\d)',a.get('id',''))
                if not m: hold('DESK_ARTICLE_ID')
                self.start(m.group(1))
            elif self.component=='atlas' and 'data-fva-record' in a:
                self.start(a.get('data-fva-id',''))
        if self.open_article is not None:
            if tag in ('img','iframe','picture','video','source') or any(
                k in a for k in ('data-lat','data-lon','data-geo-edge')):
                hold('UNREVIEWED_MEDIA_OR_GEO')
            if tag=='a' and '/image-detail/' in a.get('href',''):
                self.open_article['links'].append(a['href'])
            if tag=='details' and 'data-fvx-photo-record' in a:
                self.open_article['drawers'].append(a['data-fvx-photo-record'])
    def start(self,id):
        if id not in IDS or id in self.cards: hold('DUPLICATE_OR_UNKNOWN_ID')
        self.open_article={'id':id,'text':[],'links':[],'drawers':[]}
    def handle_data(self,data):
        if self.open_article is not None: self.open_article['text'].append(data)
    def handle_endtag(self,tag):
        if tag=='article' and self.open_article is not None:
            self.cards[self.open_article['id']]=self.open_article
            self.open_article=None

def validate_component(document,records,name):
    p=SourceArticles(name)
    p.feed(document)
    p.close()
    if p.open_article is not None or tuple(sorted(p.cards))!=IDS:
        hold(name.upper()+'_RECORD_SET')
    for r in records:
        card=p.cards[r['id']]
        text=' '.join(' '.join(card['text']).split())
        if card['links']!=[r['url']]:hold(name.upper()+'_SOURCE_LINK_'+r['id'])
        if r['catalog'] not in text:hold(name.upper()+'_CATALOG_'+r['id'])
        if r['component_date_label'] not in text:
            hold(name.upper()+'_PHOTO_DATE_'+r['id'])
        rights_notice=('not been individually reviewed or cleared' if name=='desk'
                       else 'Individual review required')
        if rights_notice.lower() not in text.lower():
            hold(name.upper()+'_MEDIA_RIGHTS_'+r['id'])
        if r['id']=='01' and not any(term in text.lower() for term in (
            'provisional','not been confirmed','unconfirmed')):
            hold(name.upper()+'_CREW_IDENTITY')
        if name=='desk' and card['drawers']!=[r['id']]:
            hold('DESK_RIGHTS_DRAWER_'+r['id'])
    return p.cards

def verify():
    board=load(HERE/'build_rights_board_r85.py','r85_board_r86')
    sources=board.load_sources()
    records=[{**r,'component_date_label':sources['crosswalk']['records'][i]['date_label']}
             for i,r in enumerate(board.verify(sources))]
    desk_bytes=DESK.read_bytes()
    desk_html=desk_bytes.decode('utf-8')
    desk=validate_component(desk_html,records,'desk')
    atlas=load(ATLAS,'atlas_builder_r86')
    custody=atlas.validate_custody()
    if custody['records']!=sources['crosswalk']['records'] or any(
        atlas.EXPECTED_URLS[r['id']]!=r['url'] for r in records):
        hold('ATLAS_CUSTODY_SOURCE_DRIFT')
    atlas_html=atlas.make_html(custody,
        (ATLAS.parent/'atlas.css').read_text('utf-8'),
        (ATLAS.parent/'atlas.js').read_text('utf-8'))
    gallery=validate_component(atlas_html,records,'atlas')
    if re.search(r'<(?:img|iframe|picture|video)\b|data-lat\b|data-lon\b|data-geo-edge\b',
                 atlas_html,re.I):hold('ATLAS_MEDIA_OR_GEO')
    if 'chrono-unplaced' not in desk_html or '2017-01-24' not in atlas_html:
        hold('PHOTO_DATE_UNCERTAINTY')
    return {'records':records,'desk':desk,'atlas':gallery,
        'blobs':{k:v[1] for k,v in board.SOURCES.items()},
        'sha256':{'desk_template':hash256(desk_bytes),
                  'atlas_generated':hash256(atlas_html.encode()),
                  'atlas_builder':hash256(ATLAS.read_bytes())}}

def render(report):
    q=lambda value:html.escape(str(value),quote=True)
    rows=[]
    cards=[]
    for r in report['records']:
        identity=('PROVISIONAL · no PIA on NASA page' if r['id']=='01'
                  else 'PIA appears on NASA page')
        rows.append(f'<tr><th scope="row"><a href="#r86-{q(r["id"])}">{q(r["id"])}</a></th><td>{q(r["catalog"])}</td><td>{q(r["date"])} / {q(r["precision"])}</td><td>{q(identity)}</td><td>Desk + Atlas verified</td><td>HOLD</td></tr>')
        cards.append(f"""<article class="evidence" id="r86-{q(r['id'])}" aria-labelledby="title-{q(r['id'])}">
<p class="eyebrow">EVIDENCE PLATE {q(r['id'])} / 06 · THREE-REGISTRY PARITY</p>
<h3 id="title-{q(r['id'])}">{q(r['title'])}</h3>
<p><strong>Catalog:</strong> {q(r['catalog'])} · <strong>Photograph date:</strong> {q(r['date'])} ({q(r['precision'])})</p>
<p><strong>NASA identity status:</strong> {q(identity)}. Source identity is not image-use permission.</p>
<p class="boundary"><strong>Evidence boundary:</strong> {q(r['limitation'])}</p>
<details><summary>Inspect the component crosswalk and pending decisions</summary>
<dl><dt>R37 custody</dt><dd>Catalog, date and destination match</dd>
<dt>R79 NASA metadata</dt><dd>{q(r['scope'])}</dd>
<dt>R55 rights assessment</dt><dd>Individual media reuse not reviewed or cleared</dd>
<dt>Research Desk</dt><dd>Actual rendered evidence plate and source URL match</dd>
<dt>Evidence Atlas</dt><dd>Actual generated source card and URL match</dd>
<dt>Remaining approval</dt><dd>Rights, editorial, accessibility, hosted and founder reviews pending</dd></dl></details>
<a class="primary" target="_blank" rel="noopener noreferrer" href="{q(r['url'])}">Inspect NASA source {q(r['id'])} ↗</a></article>""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Apollo Evidence Concordance — STAGING HOLD</title><link rel="stylesheet" href="concordance_r86.css"></head>
<body><div class="wrap"><div class="mast">FINAL VESTIGE STUDIOS / APOLLO EVIDENCE STUDIO / PRIVATE REVIEW</div>
<header><p class="eyebrow">SOURCE CUSTODY · RESEARCH DESK × ATLAS × NASA</p>
<h1>Three ledgers.<br><em>One accountable record.</em></h1>
<p class="lead">A source-controlled comparison of six NASA reference records against the actual Research Desk and generated Evidence Atlas. Matching source metadata is <strong>not image-rights clearance, NASA endorsement, or permission to publish.</strong></p>
<p class="hold" role="note"><strong>STAGING HOLD — 0 of 6 photographs cleared.</strong> The crew portrait's proposed S67-19766 catalog association is provisional, and its January 1967 day is unknown. Both 2017 photos share a date without a verified time sequence. No photograph dates reconstruct the January 27 fire.</p>
<div class="stats"><span>NASA 6/6</span><span>DESK 6/6</span><span>ATLAS 6/6</span><span>RIGHTS 0/6</span><span>GEO EDGES 0</span></div></header>
<main><section aria-labelledby="matrix-title"><h2 id="matrix-title">The verification matrix</h2>
<p>Source custody order, not fire chronology. Each NASA link is bound to its own rendered component article.</p>
<div class="table-wrap" role="region" tabindex="0" aria-label="Scrollable six-record evidence matrix">
<table><caption>Actual Research Desk and Evidence Atlas source concordance</caption>
<thead><tr><th scope="col">Source</th><th scope="col">Catalog</th><th scope="col">Photograph date</th>
<th scope="col">NASA identity</th><th scope="col">Component parity</th><th scope="col">Media reuse</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div></section>
<section aria-labelledby="detail-title"><h2 id="detail-title">Evidence and unresolved decisions</h2>
<div class="grid">{''.join(cards)}</div></section></main>
<footer><p><strong>Source parity PASS does not imply publication PASS.</strong> Pending: six individual rights decisions, independent QA, hosted WordPress.com, NVDA/VoiceOver, physical devices, and founder approval.</p>
<p>Official reference: <a href="https://www.nasa.gov/nasa-brand-center/">NASA Brand Center / media guidelines ↗</a>.
No photos, external scripts, invented map pins, or speculative historical edges are embedded.</p></footer></div></body></html>"""

def build(destination):
    report=verify() # all gates run before any output
    page=render(report).encode('utf-8')
    destination.mkdir(parents=True,exist_ok=True)
    (destination/'R86_EVIDENCE_CONCORDANCE.html').write_bytes(page)
    (destination/'concordance_r86.css').write_bytes(CSS.read_bytes())
    receipt={'schema':'fv.apollo.r86.component-concordance.v1','release':'STAGING_HOLD',
             'records':6,'research_desk_matches':6,'atlas_matches':6,
             'photo_rights_cleared':0,'images_embedded':0,'geographic_pins':0,
             'invented_edges':0,'hosted_wordpress_tested':False,
             'production_cwv_measured':False,'approved_for_publication':False,
             'source_git_blobs':report['blobs'],'components_sha256':report['sha256'],
             'html_sha256':hash256(page),'css_sha256':hash256(CSS.read_bytes())}
    (destination/'R86_CONCORDANCE_RECEIPT.json').write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt

if __name__=='__main__':
    try:
        dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path('dist/apollo-r86')
        build(dest)
        print('R86: six NASA records cross-checked against Desk and Atlas / STAGING_HOLD')
    except Exception:
        print('R86_CUSTODY_HOLD: validation failure; publication forbidden',file=sys.stderr)
        sys.exit(1)
