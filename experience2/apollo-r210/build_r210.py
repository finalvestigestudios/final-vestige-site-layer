#!/usr/bin/env python3
"""R210: consolidate Apollo evidence exercise & generate read-only provenance receipts.

STAGING-ONLY. No WordPress, remote services, checkout, analytics or publishing.
"""
from __future__ import annotations
import hashlib, json, os, re, shutil
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=Path(os.environ.get('FV_APOLLO_R209_DIST',str(ROOT.parent/'apollo-r209'/'dist')))
DIST=ROOT/'dist'
PARENT_MANIFEST_SHA='8365d42571fc54d36950e8ce2d8cae4ef36503fd300ef7cc8f5e9f4a2181cb91'
TECH='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
PHOTO='https://www.nasa.gov/image-detail/amf-s67-21294/'
REQUIRED=('templates/atlas-fragment.html','assets/atlas-scoped.css','assets/campaign-handoff.js','fv-ex2-apollo-r209.php')

def digest(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def require(cond,msg):
    if not cond:raise ValueError(msg)

class Links(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.hrefs=[];self.labels=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if d.get('id'):self.ids.append(d['id'])
        if tag=='a' and d.get('href'):self.hrefs.append(d['href'])
        for key in ('aria-labelledby','aria-describedby'):
            if d.get(key):self.labels.extend(d[key].split())

def build():
    manifest_file=BASE/'manifest.json'
    require(manifest_file.is_file(),'R209 manifest absent')
    require(digest(manifest_file.read_bytes())==PARENT_MANIFEST_SHA,'R209 manifest mismatch')
    parent=json.loads(manifest_file.read_text(encoding='utf8'))
    require(parent['release']=='r209','Not R209')
    require(parent['upstream_R198_reconciled'] is False,'Historical trust gate unexpectedly changed')
    require(not parent['approved_purchase_offer'] and not parent['media_commercial_rights_cleared'],'Commercial gate unexpectedly changed')
    for path in REQUIRED:
        require((BASE/path).is_file(),f'Missing parent asset: {path}')
        require(digest((BASE/path).read_bytes())==parent['files'][path],f'Changed parent asset: {path}')
    html=(BASE/'templates/atlas-fragment.html').read_text(encoding='utf8')
    css=(BASE/'assets/atlas-scoped.css').read_text(encoding='utf8')
    require(html.count('<section class="fv-apollo-reading-lab"')==1,'Legacy exercise count changed')
    require(html.count('<section class="fv-apollo-lesson section"')==1,'R209 exercise count changed')
    require(html.count('class="cta"')==1,'CTA count changed')
    # Safely remove a duplicated three-question exercise from R202. Its complete
    # two-source activity has been superseded by R209's sourced comparison and
    # accessible, optional answer guide. The historical narrative is unchanged.
    html,removed=re.subn(r'<section class="fv-apollo-reading-lab"[^>]*>.*?</section>', '', html, count=1, flags=re.S)
    require(removed==1 and html.count('fv-apollo-reading-lab')==0,'Legacy duplicate not fully removed')
    old='<a href="#fv-apollo-gallery">Archive gallery</a></nav>'
    new='<a href="#fv-apollo-gallery">Archive gallery</a><a href="#fv-apollo-source-test">Source test</a></nav>'
    require(html.count(old)==1,'Primary navigation insertion point changed')
    html=html.replace(old,new,1)
    # Remove unused legacy rules; retain all scoped component behaviors.
    css='\n'.join(line for line in css.split('\n') if '.fv-apollo-reading-lab' not in line)
    # Native closed details hide their contents during print in Chromium.
    # Make the R209 teaching answer guide printable even when left closed.
    css+='\n@media print{.fv-apollo-atlas .fv-apollo-lesson-key::details-content{content-visibility:visible!important;display:block!important}}\n'
    parsed=Links();parsed.feed(html)
    require(len(parsed.ids)==len(set(parsed.ids)),'Duplicate IDs')
    require(all(i in parsed.ids for i in parsed.labels),'ARIA reference broken')
    require(all(h[1:] in parsed.ids for h in parsed.hrefs if h.startswith('#')),'Dead fragment href')
    require(html.count('class="cta"')==1 and html.count('<details')==12,'Evidence controls lost')
    require(html.count(TECH)>=5 and html.count(PHOTO)>=3,'NASA source custody reduced')
    require(html.count('id="fv-apollo-source-test"')==1,'Lesson landmark missing')
    require('datetime="1967-04"' in html and 'datetime="1967-01-27"' in html,'Report/event conflated')
    require('NASA does not endorse Final Vestige' in html,'Rights boundary missing')
    require('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' in html,'Free destination missing')
    require(not re.search(r'\b(buy now|subscribe now|checkout|limited time offer)\b',html,re.I),'Unexpected commercial CTA')
    for forbidden in ('data-lat','data-lng','data-geo-edge','<iframe','<img','<script'):
        require(forbidden not in html, f'Unreviewed media/geo/script: {forbidden}')
    js=(BASE/'assets/campaign-handoff.js').read_bytes()
    assets={'templates/atlas-fragment.html':html.encode('utf8'),'assets/atlas-scoped.css':css.encode('utf8'),'assets/campaign-handoff.js':js}
    php=(BASE/'fv-ex2-apollo-r209.php').read_text(encoding='utf8').replace('r209','r210').replace('R209','R210')
    for path in ('templates/atlas-fragment.html','assets/atlas-scoped.css'):
        require(php.count(parent['files'][path])==1,f'Expected exactly one PHP pin for {path}')
        php=php.replace(parent['files'][path],digest(assets[path]),1)
    require(php.count("'2150b99027d8'")==1,'Expected PHP CSS version pin')
    php=php.replace("'2150b99027d8'","'"+digest(assets['assets/atlas-scoped.css'])[:12]+"'",1)
    assets['fv-ex2-apollo-r210.php']=php.encode('utf8')
    # The custody receipt is derived from the rendered HTML, not a parallel
    # manual source list; it provides proof of intended links, not live HTTP QA.
    nasa_links=sorted(set(h for h in parsed.hrefs if h.startswith('https://www.nasa.gov/')))
    receipt={
        'source':'rendered_R210_html','verification':'static_link_and_evidence_contract_ONLY',
        'reproduces_nasa_source_text_without_embedding_media':True,
        'nasa_source_urls':nasa_links,
        'claim_source':TECH,'aftermath_source':PHOTO,
        'report_date':'1967-04','event_date':'1967-01-27','aftermath_photo_date':'1967-01-28',
        'media_rights_for_commercial_promotion':'NOT_CLEARED',
        'commercial_offer':'NOT_APPROVED','published_creator_asset_id':'NOT_VERIFIED',
        'geographic_pins':[], 'speculative_relationship_edges':[],
        'visitor_action':{'label':'Read original investigation','url':'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/','type':'free_editorial'},
        'source_integrity':{'duplicate_exercise_removed':True,'primary_cta_count':1,'details_count':12,'navigation_to_lesson':True},
        'origin_manifest_sha256':PARENT_MANIFEST_SHA,'canonical_ancestry_from_R198':'NOT_RECONCILED'
    }
    generated={**assets,'source-audit.json':(json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode('utf8')}
    shim=(BASE/'wp-render-shim-r209.php').read_text(encoding='utf8').replace('r209','r210').replace('R209','R210')
    generated['wp-render-shim-r210.php']=shim.encode('utf8')
    for name in ('commercial-offer-gate.json','conversion-validation.json','source-records.json','custody-ledger.json'):
        generated[name]=(BASE/name).read_bytes()
    manifest={'release':'r210','parent_manifest_sha256':PARENT_MANIFEST_SHA,
      'files':{n:digest(generated[n]) for n in sorted(assets)},
      'source_audit_sha256':digest(generated['source-audit.json']),
      'unreviewed_media_introduced':False,'geo_pins':[],
      'upstream_R198_reconciled':False,'installed_WordPress_accepted':False,
      'genuine_axe_core_tested':False,'media_commercial_rights_cleared':False,
      'approved_purchase_offer':False,'release_gate':'STAGING HOLD: full ancestry / WP / axe / screen readers / CI / founder approval'}
    generated['manifest.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode('utf8')
    if DIST.exists():shutil.rmtree(DIST)
    for path,data in sorted(generated.items()):
        out=DIST/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
    return manifest

if __name__=='__main__':print(json.dumps(build(),indent=2,sort_keys=True))
