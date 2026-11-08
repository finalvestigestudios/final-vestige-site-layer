#!/usr/bin/env python3
"""R205: each chronology milestone receives a source-specific NASA record link.

Additive read-only Apollo Evidence Atlas staging builder. No NASA images copied,
no paid CTA, no analytics, no WordPress writes. The R198 ancestral mismatch is
explicitly retained as a release hold, not papered over.
"""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'apollo-r204'
DIST=HERE/'dist'
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
# Sources verified against NASA original catalog and Board on 2026-11-07.
RECORDS=(
    ('archival-photo','1966-10-18','S66-58038','https://www.nasa.gov/image-detail/amf-s66-58038/',
     'Open NASA 18 October 1966 crew training photograph','Photograph: training, not accident evidence'),
    ('photo-and-history','1967-01-03','S67-15717','https://www.nasa.gov/image-detail/amf-s67-15717/',
     'Open NASA 3 January 1967 spacecraft processing photograph','Photograph: processing, not the ignition event'),
    ('technical-report','1967-01-27','Apollo 204 Review Board',BOARD,
     'Open NASA Apollo 204 Review Board account of 27 January 1967','Investigation: no conclusively identified ignition source'),
    ('aftermath-photo','1967-01-28','S67-21294','https://www.nasa.gov/image-detail/amf-s67-21294/',
     'Open NASA 28 January 1967 aftermath photograph record','Photograph: damage the following day, not ignition'),
)
CSS='''
/* R205: make every ChronologyRail record directly checkable; no JavaScript. */
.fv-apollo-atlas .fv-apollo-rail-source{display:inline-block;margin-top:.4rem;padding:.22rem 0;text-underline-offset:.2em;overflow-wrap:anywhere;font-size:.88rem;line-height:1.5}
.fv-apollo-atlas .fv-apollo-rail-source:focus-visible{outline:3px solid var(--accent);outline-offset:4px}
.fv-apollo-atlas .fv-apollo-rail-source::after{content:' ↗'}
@media(max-width:650px){.fv-apollo-atlas .fv-apollo-rail-source{display:block;max-width:100%}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-rail-source:focus-visible{outline-color:Highlight}}
@media print{.fv-apollo-atlas .fv-apollo-rail-source{color:#111!important;text-decoration:underline!important}.fv-apollo-atlas .fv-apollo-rail-source::after{content:' [' attr(href) ']';font-size:.72em;overflow-wrap:anywhere}}
'''

def build()->dict:
    sys.path.insert(0,str(PARENT))
    from build_r204 import build as parent_build
    parent=parent_build();prior=PARENT/'dist'
    for name,digest in parent['files'].items():
        assert sha((prior/name).read_bytes())==digest, 'R204 parent file digest differs: '+name
    assert parent.get('source_chain_verified') is False, 'Do not imply certified ancestry'
    orig=(prior/'templates/atlas-fragment.html').read_bytes();html=orig.decode('utf8')
    entries=list(re.finditer(r'<li data-evidence-kind="([^"]+)">(.*?)</li>',html,re.S))
    assert len(entries)==4,'Unexpected chronology shape (fail closed)'
    assert [m.group(1) for m in entries]==[row[0] for row in RECORDS]
    ledger=[]
    for match,row in reversed(list(zip(entries,RECORDS))):
        kind,date,ref,url,label,boundary=row
        assert match.group(2).count(f'<time datetime="{date}">')==1, date
        assert match.group(2).count('<small>')==1 and match.group(2).count('</small>')==1
        note='fv-apollo-rail-note-'+kind
        new=match.group(0).replace('<small>','<small id="'+note+'">',1)
        new=new.replace('</small></li>',
            '</small><a class="fv-apollo-rail-source" href="'+url+'" '
            'aria-describedby="'+note+'" rel="noopener noreferrer" '
            'data-source-id="'+ref+'">'+label+'</a></li>',1)
        assert new!=match.group(0)
        html=html[:match.start()]+new+html[match.end():]
        ledger.append({'date':date,'evidence_kind':kind,'source_id':ref,'source_url':url,
                       'accessible_label':label,'limitation':boundary,
                       'source_agency':'NASA','media_copied':False,
                       'commercial_advertising_clearance':'NOT CERTIFIED'})
    ledger.reverse();assert html.count('class="fv-apollo-rail-source"')==4
    assert html.count('class="cta"')==1 and html.count('<details>')==8
    css=(prior/'assets/atlas-scoped.css').read_bytes()+CSS.encode('utf-8')
    js=(prior/'assets/campaign-handoff.js').read_bytes()
    php=(prior/'fv-ex2-apollo-r204.php').read_text('utf8').replace('r204','r205').replace('R204','R205')
    for old,new in ((orig,html.encode()),((prior/'assets/atlas-scoped.css').read_bytes(),css)):
        assert php.count(sha(old))==1
        php=php.replace(sha(old),sha(new),1)
    assert sha(js) in php
    files={'templates/atlas-fragment.html':html.encode(), 'assets/atlas-scoped.css':css,
           'assets/campaign-handoff.js':js,'fv-ex2-apollo-r205.php':php.encode()}
    for p,data in sorted(files.items()):
        output=DIST/p;output.parent.mkdir(exist_ok=True,parents=True);output.write_bytes(data)
    shim=(prior/'wp-render-shim-r204.php').read_text('utf8').replace('r204','r205').replace('R204','R205')
    (DIST/'wp-render-shim-r205.php').write_text(shim,encoding='utf8')
    (DIST/'conversion-validation.json').write_bytes((prior/'conversion-validation.json').read_bytes())
    (DIST/'source-records.json').write_text(json.dumps(ledger,sort_keys=True,indent=2)+'\n',encoding='utf8')
    offer={'activation':'disabled','hypothesis':'Original educator evidence dossier for historically curious teachers and enthusiasts',
           'seller_verified':False,'rights_clearance_verified':False,'checkout_fulfillment_verified':False,
           'founder_production_approval':False,'price_verified':False,
           'visitor_cta':'Read original investigation','paid_cta_rendered':False,
           'campaign_asset_id':'UNVERIFIED','qualified_human_sessions':None,
           'confirmed_orders':None,'confirmed_leads':None,'realized_net_revenue':None,
           'kpi_net_revenue_per_1000_qualified_sessions':None,
           'prohibited_equivalence':'clicks, affiliate outbound and checkout starts are not merchant-confirmed sales'}
    (DIST/'commercial-offer-gate.json').write_text(json.dumps(offer,sort_keys=True,indent=2)+'\n',encoding='utf8')
    manifest={'release':'r205','parent_head':'5a5d91becd08735e97889d52de8800188959772e',
      'purpose':'Four individual NASA-backed chronology source links, stable accessibility IDs and source role ledger',
      'files':{k:sha(v) for k,v in sorted(files.items())},
      'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
      'source_record_sha256':sha((DIST/'source-records.json').read_bytes()),
      'commercial_gate_sha256':sha((DIST/'commercial-offer-gate.json').read_bytes()),
      'source_chain_verified':False,
      'inherited_r198_local_git_blob':'2e09257cbd0b32a93f2e7e034a84685d93ed93f5',
      'canonical_r198_builder_git_blob':'57ef73d5719662a1b3647536a0eace5fb65bac4a',
      'release_gate':'STAGING HOLD: inherited source mismatch; exact GitHub-head build/CI, WP installed acceptance, axe-core, screen readers and founder approval missing'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return manifest
if __name__=='__main__':print(json.dumps(build(),sort_keys=True,indent=2))
