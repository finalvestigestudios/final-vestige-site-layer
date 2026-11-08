#!/usr/bin/env python3
"""Apollo R202: remove leftover development copy and compare two NASA sources.

Staging-only generator. No WordPress writes, telemetry, products or promotion.
"""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
from bs4 import BeautifulSoup
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'apollo-r201'
DIST=HERE/'dist'
REPORT='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
PHOTO='https://www.nasa.gov/image-detail/amf-s67-21294/'
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def sha(blob):return hashlib.sha256(blob).hexdigest()
COMPARE='''<section class="fv-apollo-compare" aria-labelledby="fv-apollo-compare-title">
<span class="eyebrow">Research Desk / a two-source exercise</span>
<h3 id="fv-apollo-compare-title">What can each record prove?</h3>
<p>Read two different records, then consider this question before revealing the explanation: can either one identify the precise event that started the fire?</p>
<div class="fv-apollo-compare-grid">
<div><strong>Technical finding</strong><p>The <a href="'''+REPORT+'''">Apollo 204 Review Board report</a> describes hazardous conditions and concludes that the exact ignition source was not conclusively identified.</p></div>
<div><strong>Photographic record</strong><p>NASA's <a href="'''+PHOTO+'''">S67-21294 catalog entry</a> documents the damaged command module on January 28, 1967, the day after the accident.</p></div></div>
<details class="fv-apollo-compare-answer"><summary>Compare the evidence and its limits</summary>
<p><strong>What the report supports:</strong> technical findings about conditions and likely ignition, with uncertainty about the specific initiating source.</p>
<p><strong>What the photograph supports:</strong> visible damage after the event, not a view of the fire starting.</p>
<p><strong>What neither proves:</strong> which precise spark began the accident. A source link is not a commercial-image license or NASA endorsement.</p></details></section>'''
CSS='''
.fv-apollo-atlas .fv-apollo-compare{border:1px solid var(--line);padding:clamp(.85rem,2.5vw,1.4rem);margin:1.3rem 0;min-width:0;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-compare h3{margin:.4rem 0 1rem;font-size:clamp(1.15rem,2.5vw,1.5rem)}
.fv-apollo-atlas .fv-apollo-compare-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}
.fv-apollo-atlas .fv-apollo-compare-grid>div{min-width:0;padding:.8rem;border:1px solid var(--line);background:rgba(190,152,88,.04)}
.fv-apollo-atlas .fv-apollo-compare-grid strong{color:var(--paper)}
.fv-apollo-atlas .fv-apollo-compare-answer{margin-top:1rem;padding:.75rem;border:1px solid var(--line)}
.fv-apollo-atlas .fv-apollo-compare-answer>summary{cursor:pointer}
.fv-apollo-atlas .fv-apollo-compare a:focus-visible,.fv-apollo-atlas .fv-apollo-compare summary:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
@media(max-width:650px){.fv-apollo-atlas .fv-apollo-compare-grid{grid-template-columns:minmax(0,1fr)}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-compare,.fv-apollo-atlas .fv-apollo-compare-grid>div,.fv-apollo-atlas .fv-apollo-compare-answer{border-color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-compare{color:#111!important;background:#fff!important}.fv-apollo-atlas .fv-apollo-compare-grid>div{background:#fff!important;break-inside:avoid}.fv-apollo-atlas .fv-apollo-compare-grid strong{color:#111!important}.fv-apollo-atlas .fv-apollo-compare-answer:not([open])>p{display:block!important}.fv-apollo-atlas .fv-apollo-compare a{color:#111!important;text-decoration:underline!important}}
'''
def custody(html):
    root=BeautifulSoup(html,'html.parser').select_one('article.fv-apollo-atlas')
    assert root is not None
    text=root.get_text(' ',strip=True)
    for pat in ('research prototype','unpublished','staging','founder release','proposed product','affiliate conversion'):
        assert pat not in text.lower(),'public internal copy: '+pat
    assert len(root.select('a.cta'))==1 and root.select_one('a.cta')['href']==DEST
    assert len(root.select('.rail > li'))==4 and len(root.select('details'))==9
    assert len(root.select('.fv-apollo-compare-grid > div'))==2
    assert root.select_one('.fv-apollo-compare-answer summary').get_text(strip=True)=='Compare the evidence and its limits'
    assert len(root.select('a[href="'+REPORT+'"]'))>=4 and len(root.select('a[href="'+PHOTO+'"]'))>=1
    assert 'NASA does not endorse Final Vestige' in text
    assert not root.select('form,iframe,[data-lat],[data-geo],[data-affiliate],[data-purchase]')
    ids=[n['id'] for n in root.select('[id]')]
    assert len(ids)==len(set(ids))
    assert all(a['href'][1:] in ids for a in root.select('a[href^="#"]'))
    return True
def build():
    sys.path.insert(0,str(PARENT))
    from build_r201 import build as parent_build
    parent=parent_build();prior=PARENT/'dist'
    for name,digest in parent['files'].items():
        assert sha((prior/name).read_bytes())==digest,name
    original=(prior/'templates/atlas-fragment.html').read_bytes()
    html=original.decode('utf-8')
    fixes=(
      ('Case study / January 27, 1967 / research prototype','Case study / January 27, 1967 / Apollo 204'),
      ('Unpublished research prototype. Staging QA and founder release approval outstanding. NASA material is cited for research; NASA does not endorse Final Vestige.',
       'Read the original records and distinguish observation from interpretation. NASA does not endorse Final Vestige.'),
    )
    for before,after in fixes:
        assert html.count(before)==1
        html=html.replace(before,after,1)
    assert html.count('<footer class="end">')==1
    html=html.replace('<footer class="end">',COMPARE+'\n<footer class="end">',1)
    custody(html)
    old_css=(prior/'assets/atlas-scoped.css').read_bytes()
    css=old_css+CSS.encode()
    php=(prior/'fv-ex2-apollo-r201.php').read_text().replace('r201','r202').replace('R201','R202')
    for before,after in ((original,html.encode()),(old_css,css)):
        assert php.count(sha(before))==1
        php=php.replace(sha(before),sha(after),1)
    js=(prior/'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php
    files={'templates/atlas-fragment.html':html.encode(),'assets/atlas-scoped.css':css,'assets/campaign-handoff.js':js,'fv-ex2-apollo-r202.php':php.encode()}
    for name,data in sorted(files.items()):
        p=DIST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    shim=(prior/'wp-render-shim-r201.php').read_text().replace('r201','r202').replace('R201','R202')
    shim=shim.replace("substr_count($rendered,'<details>')","substr_count($rendered,'<details')")
    (DIST/'wp-render-shim-r202.php').write_text(shim)
    (DIST/'conversion-validation.json').write_bytes((prior/'conversion-validation.json').read_bytes())
    receipt={'release':'r202','parent_head':'4d48cf59085efd726b9c2fe251b4c05ed3f8b8d5','files':{k:sha(v) for k,v in sorted(files.items())},
      'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
      'commercial_offer':'No verified Apollo SKU; single free investigation CTA',
      'inherited_source_blocker':'R198 local builder differs from R198 GitHub blob; exact-head cold build not certified',
      'release':'r202-staging-hold'}
    (DIST/'manifest.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt
if __name__=='__main__':print(json.dumps(build(),indent=2))
