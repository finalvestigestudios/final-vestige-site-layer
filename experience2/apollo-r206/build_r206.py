#!/usr/bin/env python3
"""Apollo R206: native evidence-confidence ladder, isolated staging builder.

No source images downloaded; no speculation, tracking, product sale or WP writes.
An R205 dist snapshot is required because historic R198 GitHub/local ancestry diverges.
This builder verifies R205 output SHA-256 against its manifest before mutation,
then creates only R206 output. Missing parent assets cause a hard, honest failure.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'apollo-r205'/'dist'
DIST=HERE/'dist'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
AFTERMATH='https://www.nasa.gov/image-detail/amf-s67-21294/'

def digest(b:bytes)->str: return hashlib.sha256(b).hexdigest()

CONFIDENCE='''<section class="fv-apollo-confidence section" id="fv-apollo-confidence" aria-labelledby="fv-apollo-confidence-title" tabindex="-1">
<span class="eyebrow">Research Desk / evidence confidence</span>
<h2 id="fv-apollo-confidence-title">What is documented, probable, and unresolved?</h2>
<p class="intro">A documented condition is not the same as a proven cause. Compare the Review Board's findings before drawing a conclusion; each record has a different evidentiary limit.</p>
<ol class="fv-apollo-confidence-list">
<li><details><summary><span class="fv-apollo-confidence-status">Documented</span><span class="fv-apollo-confidence-question">What were the test conditions?</span></summary><div class="fv-apollo-confidence-answer"><p>The Board documented a 100-percent oxygen atmosphere at 16.7 psia and combustible materials in the cabin. These hazardous conditions help explain rapid fire spread; they do not identify the specific ignition source.</p><p><a href="#fv-apollo-finding-oxygen">Check the atmosphere finding</a> · <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Read NASA Review Board Finding 2</a></p></div></details></li>
<li><details><summary><span class="fv-apollo-confidence-status">Most probable</span><span class="fv-apollo-confidence-question">How might the fire have started?</span></summary><div class="fv-apollo-confidence-answer"><p>The Board considered an electrical arc the most probable initiator. That determination is an evidence-based assessment, not a positively identified individual wire, spark, or precise ignition point.</p><p><a href="#fv-apollo-finding-fire">Check the ignition finding</a> · <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Read NASA Review Board Finding 1</a></p></div></details></li>
<li><details><summary><span class="fv-apollo-confidence-status">Not determined</span><span class="fv-apollo-confidence-question">Can a photograph settle the cause?</span></summary><div class="fv-apollo-confidence-answer"><p>No single ignition source was conclusively identified. NASA's S67-21294 photograph shows damage documented on January 28, 1967; it does not show the ignition event or prove a particular point of origin.</p><p><a href="#fv-apollo-photo-aftermath">Examine the aftermath record</a> · <a href="https://www.nasa.gov/image-detail/amf-s67-21294/">Open NASA S67-21294 catalog</a></p></div></details></li>
</ol>
<p class="fv-apollo-confidence-boundary"><strong>Research note:</strong> NASA sources document the investigation; linking to them does not imply agency endorsement or permission to use astronaut identities or archival photography in commercial promotions.</p>
</section>'''
CSS='''
/* R206: no-JS confidence ladder. Scoped, responsive, printable. */
.fv-apollo-atlas .fv-apollo-confidence{margin:clamp(1.3rem,3vw,2.3rem) 0;min-width:0}
.fv-apollo-atlas .fv-apollo-confidence-list{list-style:none;padding:0;margin:1rem 0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(.7rem,1.6vw,1.2rem)}
.fv-apollo-atlas .fv-apollo-confidence-list li{min-width:0}
.fv-apollo-atlas .fv-apollo-confidence-list details{border:1px solid var(--line);background:var(--bg);height:100%;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-confidence-list summary{cursor:pointer;padding:clamp(.8rem,2vw,1.2rem);min-height:5rem;line-height:1.5}
.fv-apollo-atlas .fv-apollo-confidence-status{display:block;color:var(--accent);font-size:.81rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase}
.fv-apollo-atlas .fv-apollo-confidence-question{display:block;font-weight:700;margin-top:.45rem;color:var(--paper)}
.fv-apollo-atlas .fv-apollo-confidence-list summary:focus-visible,.fv-apollo-atlas .fv-apollo-confidence-list a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.fv-apollo-atlas .fv-apollo-confidence-answer{padding:0 clamp(.8rem,2vw,1.2rem) 1.2rem;line-height:1.65}
.fv-apollo-atlas .fv-apollo-confidence-answer a{overflow-wrap:anywhere;text-underline-offset:.16em}
.fv-apollo-atlas .fv-apollo-confidence-boundary{font-size:.89rem;max-width:80ch}
@media(max-width:850px){.fv-apollo-atlas .fv-apollo-confidence-list{grid-template-columns:minmax(0,1fr)}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-confidence-list details{border-color:CanvasText}.fv-apollo-atlas .fv-apollo-confidence-status{color:CanvasText}}
@media(prefers-reduced-motion:reduce){.fv-apollo-atlas .fv-apollo-confidence-list *{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
@media print{.fv-apollo-atlas .fv-apollo-confidence-list{display:block}.fv-apollo-atlas .fv-apollo-confidence-list li{break-inside:avoid;margin-bottom:1rem}.fv-apollo-atlas .fv-apollo-confidence-list details{color:#111!important;background:#fff!important}.fv-apollo-atlas .fv-apollo-confidence-list .fv-apollo-confidence-answer{display:block!important}.fv-apollo-atlas .fv-apollo-confidence-list a{color:#111!important;text-decoration:underline!important}.fv-apollo-atlas .fv-apollo-confidence-list a::after{content:' [' attr(href) ']';overflow-wrap:anywhere;font-size:.7em}}
'''

def build()->dict:
    assert PARENT.is_dir(), 'R205 generated dist missing: canonical ancestry rebuild is NOT certified; release hold'
    parent=json.loads((PARENT/'manifest.json').read_text('utf8'))
    assert parent['release']=='r205' and parent['source_chain_verified'] is False
    for name,hash_expected in parent['files'].items():
        assert digest((PARENT/name).read_bytes())==hash_expected, 'R205 parent digest mismatch: '+name
    raw=(PARENT/'templates/atlas-fragment.html').read_bytes()
    html=raw.decode('utf8')
    marker='<section aria-labelledby="fv-apollo-evidence-title"'
    assert html.count(marker)==1, 'unexpected source/structure change'
    assert 'id="fv-apollo-confidence"' not in html
    html=html.replace(marker,CONFIDENCE+'\n'+marker,1)
    assert len(re.findall(r'<details(?: |>)',html))==11
    assert html.count('class="cta"')==1 and 'affiliate' not in CONFIDENCE.lower()
    base_css=(PARENT/'assets/atlas-scoped.css').read_bytes()
    css=base_css+CSS.encode('utf8')
    js=(PARENT/'assets/campaign-handoff.js').read_bytes()
    php=(PARENT/'fv-ex2-apollo-r205.php').read_text('utf8')
    assert 'r205' in php
    php=php.replace('r205','r206').replace('R205','R206')
    for before,after in ((raw,html.encode('utf8')),(base_css,css)):
        assert php.count(digest(before))==1, 'unverified PHP asset hash pin'
        php=php.replace(digest(before),digest(after),1)
    assert digest(js) in php
    artifacts={
        'templates/atlas-fragment.html':html.encode('utf8'),
        'assets/atlas-scoped.css':css,
        'assets/campaign-handoff.js':js,
        'fv-ex2-apollo-r206.php':php.encode('utf8'),
    }
    for name,blob in sorted(artifacts.items()):
        target=DIST/name; target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(blob)
    shim=(PARENT/'wp-render-shim-r205.php').read_text('utf8').replace('r205','r206').replace('R205','R206')
    (DIST/'wp-render-shim-r206.php').write_text(shim,encoding='utf8')
    for additional in ('commercial-offer-gate.json','conversion-validation.json','source-records.json'):
        (DIST/additional).write_bytes((PARENT/additional).read_bytes())
    manifest={
        'release':'r206','parent_head':'0f64a13fb258f8c4007c2d04d7553085d7500019',
        'source':'Apollo 204 Review Board, NASA catalog S67-21294',
        'files':{n:digest(b) for n,b in sorted(artifacts.items())},
        'parent_manifest_sha256':digest((PARENT/'manifest.json').read_bytes()),
        'source_chain_verified':False,
        'inherited_r198_local_git_blob':'2e09257cbd0b32a93f2e7e034a84685d93ed93f5',
        'canonical_r198_builder_git_blob':'57ef73d5719662a1b3647536a0eace5fb65bac4a',
        'no_commercial_activation':True,'no_photographs_copied':True,'record_links_only':True,
        'release_gate':'STAGING HOLD: canonical R198 discrepancy, installed WordPress, axe-core, screen readers, exact-head CI, independent QA, founder approval',
    }
    (DIST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return manifest

if __name__=='__main__':print(json.dumps(build(),indent=2,sort_keys=True))
