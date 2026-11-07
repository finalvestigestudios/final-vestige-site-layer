#!/usr/bin/env python3
"""Apollo R196: evidence-classification guide, source custody, and disclosure limits.

Staging-only, deterministic build derived from source-pinned R195; no WP writes.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r195'
DIST = HERE / 'dist'
NASA_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
NASA_PHOTO = 'https://www.nasa.gov/image-detail/amf-s67-21294/'
GUIDE = '''<aside class="fv-apollo-method" aria-labelledby="fv-apollo-method-title">
  <span class="eyebrow">Research Desk / how to read this case</span>
  <h2 id="fv-apollo-method-title">Three kinds of evidence. Three different limits.</h2>
  <p class="fv-apollo-method-intro">The record is strongest when its sources are kept distinct. An interpretation is not a photograph, and a photograph is not a measurement.</p>
  <dl class="fv-apollo-method-grid">
    <div><dt>01 / Review Board determination</dt><dd>The Board identified hazardous conditions and considered an electrical arc most probable. <strong>It did not conclusively identify the specific ignition source.</strong> <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Read the Board's findings</a>.</dd></div>
    <div><dt>02 / Recorded sequence</dt><dd>Pressure and communication records support the sequence and cabin rupture. <strong>A timestamp is not a camera frame or proof of a particular spark.</strong> <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Examine the recorded chronology</a>.</dd></div>
    <div><dt>03 / Archival photograph</dt><dd>NASA's S67-21294 catalog documents the damaged cabin on January 28, 1967. <strong>It records the aftermath, not the initiating event.</strong> <a href="https://www.nasa.gov/image-detail/amf-s67-21294/">Verify the photo record</a>.</dd></div>
  </dl>
  <p class="fv-apollo-method-rights">Source links are for historical verification. No NASA promotional endorsement, photograph licensing, or astronaut-likeness clearance is implied.</p>
</aside>
'''
CSS_PATCH = '''\n/* R196: visible, semantic Research Desk evidence classification, not commerce. */
.fv-apollo-atlas .fv-apollo-method{margin:0 0 3rem;border:1px solid var(--line);border-top:3px solid var(--accent);padding:clamp(1.1rem,3vw,2.1rem);background:#15191b}
.fv-apollo-atlas .fv-apollo-method h2{margin:.5rem 0 1rem;font-size:clamp(1.6rem,3vw,2.35rem)}
.fv-apollo-atlas .fv-apollo-method-intro{max-width:70ch;color:var(--muted)}
.fv-apollo-atlas .fv-apollo-method-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin:1.5rem 0}
.fv-apollo-atlas .fv-apollo-method-grid>div{border-left:2px solid var(--accent);padding:.3rem 1rem;min-width:0;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-method dt{font-size:.82rem;letter-spacing:.025em;font-weight:800;color:var(--accent)}
.fv-apollo-atlas .fv-apollo-method dd{margin:.65rem 0 0;color:var(--paper)}
.fv-apollo-atlas .fv-apollo-method dd a{display:inline;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-method-rights{border-top:1px solid var(--line);padding-top:1rem;margin-bottom:0;color:var(--muted);font-size:.87rem}
@media(max-width:840px){.fv-apollo-atlas .fv-apollo-method-grid{grid-template-columns:minmax(0,1fr)}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-method,.fv-apollo-atlas .fv-apollo-method-grid>div{border-color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-method{background:#fff!important;color:#000!important;border-color:#444!important;break-inside:avoid}.fv-apollo-atlas .fv-apollo-method dt,.fv-apollo-atlas .fv-apollo-method dd,.fv-apollo-atlas .fv-apollo-method-intro,.fv-apollo-atlas .fv-apollo-method-rights{color:#000!important}.fv-apollo-atlas .fv-apollo-method-grid>div{border-color:#444!important}}
'''

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def build():
    sys.path.insert(0, str(PARENT))
    from build_r195 import build as build_parent
    parent = build_parent()
    old = PARENT / 'dist'
    for name, digest in parent['files'].items():
        assert sha((old / name).read_bytes()) == digest, 'Parent corruption: ' + name
    html_old = (old / 'templates/atlas-fragment.html').read_bytes()
    css_old = (old / 'assets/atlas-scoped.css').read_bytes()
    php = (old / 'fv-ex2-apollo-r195.php').read_text()
    html = html_old.decode()
    anchor = '<section aria-labelledby="fv-apollo-chronology-title"'
    assert html.count(anchor) == 1, 'Chronology anchor is ambiguous'
    html = html.replace(anchor, GUIDE + anchor)
    assert html.count('id="fv-apollo-method-title"') == 1
    assert html.count('class="fv-apollo-method"') == 1
    assert html.count(NASA_BOARD) >= 2 and html.count(NASA_PHOTO) >= 2
    # The research note must remain distinct from the single, free editorial action.
    assert html.count('class="cta"') == 1
    assert '<img ' not in GUIDE and '<script' not in GUIDE and '<form' not in GUIDE
    css = css_old + CSS_PATCH.encode()
    php = php.replace('r195', 'r196').replace('R195', 'R196')
    for name, old_data, new_data in [('HTML',html_old,html.encode()), ('CSS',css_old,css)]:
        assert php.count(sha(old_data)) == 1, name + ' parent digest missing'
        php = php.replace(sha(old_data),sha(new_data))
    js = (old / 'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php, 'Optional JS integrity pin lost'
    files = {'templates/atlas-fragment.html':html.encode(),
             'assets/atlas-scoped.css':css,
             'assets/campaign-handoff.js':js,
             'fv-ex2-apollo-r196.php':php.encode()}
    for name, data in sorted(files.items()):
        f = DIST / name
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(data)
    shim = (old/'wp-render-shim-r195.php').read_text()
    (DIST/'wp-render-shim-r196.php').write_text(shim.replace('r195','r196').replace('R195','R196'))
    manifest = {'release':'r196','parent_head':'5d329e59c25da99644adf246b7750d8803b8a1ae',
      'change':'Source-hierarchy guide distinguishes Board findings, instrument chronology and archival photograph; no sales activation.',
      'files':{name:sha(data) for name,data in sorted(files.items())},
      'parent_manifest_sha256':sha((old/'manifest.json').read_bytes()),
      'policy':'NASA-source links are research citations; no promotional rights, implied endorsements or likeness clearance.',
      'commercial':'One free original-investigation CTA; no verified paid Apollo dossier, orders or qualified-session denominator.'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    return manifest

if __name__=='__main__': print(json.dumps(build(),indent=2))
