#!/usr/bin/env python3
"""R197: native, accessible evidence-to-claim navigation; staging only."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r196'
DIST = HERE / 'dist'
NAV = '''<nav class="fv-apollo-claim-nav" aria-label="Check the four findings">
  <h3>Verify a specific finding</h3>
  <p>Jump to the claim, its limitation and the original NASA source. Each finding can be examined independently.</p>
  <ol>
    <li><a href="#fv-apollo-finding-oxygen">Oxygen atmosphere</a></li>
    <li><a href="#fv-apollo-finding-fire">Ignition uncertainty</a></li>
    <li><a href="#fv-apollo-finding-hatch">Hatch and escape</a></li>
    <li><a href="#fv-apollo-finding-chronology">Cabin pressure</a></li>
  </ol>
</nav>'''
CSS = '''\n/* R197: keyboard, touch and no-JS claim navigation, source-first. */
.fv-apollo-atlas .fv-apollo-claim-nav{margin:1.2rem 0;padding:1rem;border:1px solid var(--line)}
.fv-apollo-atlas .fv-apollo-claim-nav h3{margin:0 0 .4rem;font-size:1.1rem}
.fv-apollo-atlas .fv-apollo-claim-nav p{margin:.2rem 0 1rem;color:var(--muted)}
.fv-apollo-atlas .fv-apollo-claim-nav ol{display:flex;flex-wrap:wrap;gap:.65rem;list-style:none;padding:0;margin:0}
.fv-apollo-atlas .fv-apollo-claim-nav li{margin:0;max-width:100%}
.fv-apollo-atlas .fv-apollo-claim-nav a{display:inline-block;padding:.55rem .8rem;border:1px solid var(--accent);color:var(--accent);text-underline-offset:.18em;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-claim-nav a:focus-visible{outline:3px solid var(--paper);outline-offset:3px}
.fv-apollo-atlas .plate{scroll-margin-top:2rem}
.fv-apollo-atlas .plate:target{outline:3px solid var(--accent);outline-offset:3px}
@media(max-width:480px){.fv-apollo-atlas .fv-apollo-claim-nav ol{display:grid;grid-template-columns:minmax(0,1fr)}.fv-apollo-atlas .fv-apollo-claim-nav a{display:block}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-claim-nav a,.fv-apollo-atlas .plate:target{border-color:LinkText;outline-color:Highlight}}
@media print{.fv-apollo-atlas .fv-apollo-claim-nav{display:none!important}.fv-apollo-atlas .plate:target{outline:0}}
'''
def sha(data): return hashlib.sha256(data).hexdigest()
def build():
    sys.path.insert(0,str(PARENT))
    from build_r196 import build as build_parent
    parent = build_parent()
    old=PARENT/'dist'
    for name,digest in parent['files'].items():
        assert sha((old/name).read_bytes())==digest, 'parent digest failed: '+name
    original_html=(old/'templates/atlas-fragment.html').read_bytes()
    html=original_html.decode()
    anchor='<dl class="fv-apollo-method-grid">'
    assert html.count(anchor)==1
    html=html.replace(anchor,NAV+'\n  '+anchor,1)
    for id in ('oxygen','hatch','chronology'):
        needle='id="fv-apollo-finding-'+id+'"'
        assert html.count(needle)==1
        html=html.replace(needle,needle+' tabindex="-1"',1)
    assert html.count('class="cta"')==1
    assert html.count('<details>')==8
    original_css=(old/'assets/atlas-scoped.css').read_bytes()
    css=original_css+CSS.encode()
    php=(old/'fv-ex2-apollo-r196.php').read_text()
    php=php.replace('r196','r197').replace('R196','R197')
    for before,after in ((original_html,html.encode()),(original_css,css)):
        digest=sha(before)
        assert php.count(digest)==1, 'missing integrity pin '+digest
        php=php.replace(digest,sha(after),1)
    js=(old/'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php
    files={'templates/atlas-fragment.html':html.encode(),
           'assets/atlas-scoped.css':css,
           'assets/campaign-handoff.js':js,
           'fv-ex2-apollo-r197.php':php.encode()}
    for name,data in sorted(files.items()):
        f=DIST/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
    shim=(old/'wp-render-shim-r196.php').read_text().replace('r196','r197').replace('R196','R197')
    (DIST/'wp-render-shim-r197.php').write_text(shim)
    manifest={'release':'r197','parent_head':'68c48f9cb9be83101c8e665eb055801ffcebd050',
      'purpose':'Accessible four-claim native evidence navigation; preserves a single free original-investigation CTA',
      'files':{k:sha(v) for k,v in sorted(files.items())},
      'parent_manifest_sha256':sha((old/'manifest.json').read_bytes()),
      'release_gate':'draft, no WordPress installation or rights-clearance approval'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    return manifest
if __name__=='__main__':print(json.dumps(build(),indent=2))
