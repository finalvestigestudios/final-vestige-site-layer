#!/usr/bin/env python3
"""Apollo R202: remove internal conversion/prototype copy from the public Atlas.

Only the existing editorial CTA survives. No affiliate, tracking, image, or WP writes.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r201'
DIST = HERE / 'dist'
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

CHANGES = (
    ('Case study / January 27, 1967 / research prototype', 'Case study / January 27, 1967 / primary-source investigation'),
    ('Unpublished research prototype. Staging QA and founder release approval outstanding. NASA material is cited for research; NASA does not endorse Final Vestige.', 'Independent historical research. NASA sources are credited for verification; NASA does not endorse Final Vestige.'),
)
NOTE = '''<section class="fv-apollo-reading-lab" aria-labelledby="fv-apollo-reading-lab-title"><span class="eyebrow">Research Desk / Try the source test</span><h2 id="fv-apollo-reading-lab-title">Two records. One question they cannot answer.</h2><p>Compare <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">the Apollo 204 Review Board's findings</a> with <a href="https://www.nasa.gov/image-detail/amf-s67-21294/">NASA's January 28 damage photograph</a>. A written investigation and an aftermath image answer different questions.</p><ol><li><strong>Identify the source:</strong> Who created each record, and when?</li><li><strong>Separate observation from inference:</strong> Which hazards did the Board identify? What damage does the photograph show?</li><li><strong>State the limit:</strong> Can either record prove the precise initiating spark? Explain why not.</li></ol><p class="small">This optional exercise is free; the investigation and all source references remain open.</p></section>'''
CSS = '''
.fv-apollo-atlas .fv-apollo-reading-lab{min-width:0;max-width:100%;margin:1.5rem 0;padding:clamp(.9rem,2.3vw,1.6rem);border:1px solid var(--line);background:var(--surface);overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-reading-lab h2{font-size:clamp(1.5rem,3.2vw,2.35rem);max-width:24ch}
.fv-apollo-atlas .fv-apollo-reading-lab ol{margin:1rem 0;padding-left:1.5rem;max-width:70ch}
.fv-apollo-atlas .fv-apollo-reading-lab li{margin:.5rem 0;overflow-wrap:anywhere}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-reading-lab{border-color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-reading-lab{background:white!important;color:black!important;break-inside:avoid}}
'''

def build() -> dict:
    sys.path.insert(0, str(PARENT))
    from build_r201 import build as parent_build
    parent=parent_build()
    prior=PARENT/'dist'
    for path,digest in parent['files'].items():
        assert sha((prior/path).read_bytes()) == digest, 'inherited file integrity: '+path
    original=(prior/'templates/atlas-fragment.html').read_bytes()
    html=original.decode('utf-8')
    for old,new in CHANGES:
        assert html.count(old)==1, 'not precisely one source string: '+old[:55]
        html=html.replace(old,new,1)
    needle='<!-- R191 print-only source custody; visible without JS in printed output. -->'
    assert html.count(needle)==1
    html=html.replace(needle, NOTE+needle,1)
    assert html.count('class="cta"')==1 and html.count('<details>')==8
    assert all(term not in html for term in ('unpublished prototype', 'proposed product', 'affiliate conversion is claimed'))
    old_css=(prior/'assets/atlas-scoped.css').read_bytes()
    css=old_css+CSS.encode('utf-8')
    php=(prior/'fv-ex2-apollo-r201.php').read_text('utf-8').replace('r201','r202').replace('R201','R202')
    for old,new in ((original,html.encode('utf-8')),(old_css,css)):
        assert php.count(sha(old))==1, 'expected parent integrity pin'
        php=php.replace(sha(old),sha(new),1)
    js=(prior/'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php
    files={'templates/atlas-fragment.html':html.encode('utf-8'),
           'assets/atlas-scoped.css':css,
           'assets/campaign-handoff.js':js,
           'fv-ex2-apollo-r202.php':php.encode('utf-8')}
    for path,blob in sorted(files.items()):
        dest=DIST/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
    shim=(prior/'wp-render-shim-r201.php').read_text('utf-8').replace('r201','r202').replace('R201','R202')
    (DIST/'wp-render-shim-r202.php').write_text(shim,encoding='utf-8')
    plan={
      'product_hypothesis':'Original educator Apollo 1 source-analysis dossier, not a currently purchasable item',
      'audience':'Educators and research-oriented viewers of a future verified Grok Apollo long-form asset',
      'current_destination':'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
      'current_single_action':'Read original investigation',
      'commercial_offer_status':'not_verified_for_sale',
      'published_grok_apollo_asset_id':None,
      'attribution_status':'unverified',
      '7_day_qualified_human_sessions':None,
      '30_day_qualified_human_sessions':None,
      'merchant_confirmed_orders':None,
      'realized_net_revenue':None,
      'net_revenue_per_1000_qualified_sessions':None,
      'release_gate':'staging_hold',
      'requirements':['verify product and rights','verify checkout/fulfillment','inspect completed orders, fees and refunds','real WP staging and accessibility/axe','founder approval'],
    }
    (DIST/'conversion-validation.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    manifest={'release':'r202','parent_head':'4d48cf59085efd726b9c2fe251b4c05ed3f8b8d5',
      'scope':'Remove residual prototype language and add free accessible NASA source comparison',
      'files':{k:sha(v) for k,v in sorted(files.items())},
      'conversion_validation_sha256':sha((DIST/'conversion-validation.json').read_bytes()),
      'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
      'gate':'draft_only_not_live; installed WP, axe-core, assistive technology, exact-head CI, seller rights and purchase proof open'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return manifest
if __name__=='__main__': print(json.dumps(build(),indent=2))
