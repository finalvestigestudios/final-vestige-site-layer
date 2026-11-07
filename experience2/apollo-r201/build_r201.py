#!/usr/bin/env python3
"""Apollo R201: remove internal conversion/prototype copy from the public Atlas.

Only the existing editorial CTA survives. No affiliate, tracking, image, or WP writes.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r200'
DIST = HERE / 'dist'
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

CHANGES = (
    ('A text-first gallery links to NASA\'s own image records. No NASA image files are reproduced in this unpublished prototype. Image descriptions do not grant permission for paid-product promotion, astronaut endorsements or branded advertising.',
     'These links open NASA\'s original image records, not reproductions. Dates and descriptions distinguish preparation photographs from images taken after the fire. None shows the moment of ignition.'),
    ('Free historical analysis. An Apollo educator dossier is a proposed product, not a verified item for sale. No purchase, signup or affiliate conversion is claimed here.',
     'Explore the complete investigation free of charge, with no account or signup required. Follow the sources and decide what the surviving records actually establish.'),
    ('The next link opens Final Vestige\'s free investigation, not a checkout.',
     'NASA does not endorse Final Vestige. The linked investigation is free to read.'),
)
NOTE = ('<p class="small fv-apollo-educator-note"><strong>For educators and researchers:</strong> '
        'compare the Review Board\'s written findings with a dated archival photograph. '
        'Ask what each record establishes—and what it leaves unanswered.</p>')
CSS = '''\n/* R201: restrained educator utility, rather than a speculative product pitch. */
.fv-apollo-atlas .fv-apollo-educator-note{margin-block:1rem;max-width:66ch;border-left:3px solid var(--accent);padding:.35rem 0 .35rem .9rem;overflow-wrap:anywhere}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-educator-note{border-color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-educator-note{border-color:#444!important}}
'''

def build() -> dict:
    sys.path.insert(0, str(PARENT))
    from build_r200 import build as parent_build
    parent=parent_build()
    prior=PARENT/'dist'
    for path,digest in parent['files'].items():
        assert sha((prior/path).read_bytes()) == digest, 'inherited file integrity: '+path
    original=(prior/'templates/atlas-fragment.html').read_bytes()
    html=original.decode('utf-8')
    for old,new in CHANGES:
        assert html.count(old)==1, 'not precisely one source string: '+old[:55]
        html=html.replace(old,new,1)
    needle='<p class="small fv-apollo-source-boundary">'
    assert html.count(needle)==1
    html=html.replace(needle, NOTE+needle,1)
    assert html.count('class="cta"')==1 and html.count('<details>')==8
    assert all(term not in html for term in ('unpublished prototype', 'proposed product', 'affiliate conversion is claimed'))
    old_css=(prior/'assets/atlas-scoped.css').read_bytes()
    css=old_css+CSS.encode('utf-8')
    php=(prior/'fv-ex2-apollo-r200.php').read_text('utf-8').replace('r200','r201').replace('R200','R201')
    for old,new in ((original,html.encode('utf-8')),(old_css,css)):
        assert php.count(sha(old))==1, 'expected parent integrity pin'
        php=php.replace(sha(old),sha(new),1)
    js=(prior/'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php
    files={'templates/atlas-fragment.html':html.encode('utf-8'),
           'assets/atlas-scoped.css':css,
           'assets/campaign-handoff.js':js,
           'fv-ex2-apollo-r201.php':php.encode('utf-8')}
    for path,blob in sorted(files.items()):
        dest=DIST/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
    shim=(prior/'wp-render-shim-r200.php').read_text('utf-8').replace('r200','r201').replace('R200','R201')
    (DIST/'wp-render-shim-r201.php').write_text(shim,encoding='utf-8')
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
    manifest={'release':'r201','parent_head':'0769224d8c1ba6499a4546d79c455ce90ef477ff',
      'scope':'Replace internal project/sales language with reader-facing provenance, free next action and educator use case',
      'files':{k:sha(v) for k,v in sorted(files.items())},
      'conversion_validation_sha256':sha((DIST/'conversion-validation.json').read_bytes()),
      'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
      'gate':'draft_only_not_live; installed WP, axe-core, assistive technology, exact-head CI, seller rights and purchase proof open'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return manifest
if __name__=='__main__': print(json.dumps(build(),indent=2))
