#!/usr/bin/env python3
"""Apollo R204: restore NASA source crosswalk to its independent landmark boundary.

R198 local handoff erroneously nested the crosswalk inside the methodology aside;
the canonical GitHub R198 builder places it AFTER the aside. This additive
correction fixes the visitor DOM while exact ancestor reconciliation remains open.
No website, WordPress, merchant, campaign, or analytics writes.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'apollo-r203'
DIST=HERE/'dist'
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def build()->dict:
    sys.path.insert(0,str(PARENT))
    from build_r203 import build as parent_build
    parent=parent_build()
    prior=PARENT/'dist'
    for name,digest in parent['files'].items():
        assert sha((prior/name).read_bytes())==digest,'parent corruption: '+name
    old=(prior/'templates/atlas-fragment.html').read_bytes()
    html=old.decode('utf-8')
    start='<section class="fv-apollo-trace"'
    end='</section>'
    assert html.count(start)==1
    a=html.index(start)
    b=html.index(end,a)+len(end)
    trace=html[a:b]
    original_position='</aside>\n<section aria-labelledby="fv-apollo-chronology-title"'
    assert html.count(original_position)==1
    html=html[:a]+html[b:]
    assert html.count(original_position)==1
    html=html.replace(original_position,'</aside>\n'+trace+'\n<section aria-labelledby="fv-apollo-chronology-title"',1)
    assert html.count(start)==1 and html.count('class="cta"')==1 and html.count('<details>')==8
    assert html.index('</aside>\n'+start)<html.index('id="fv-apollo-chronology"')
    new=html.encode('utf-8')
    css=(prior/'assets/atlas-scoped.css').read_bytes()
    js=(prior/'assets/campaign-handoff.js').read_bytes()
    php=(prior/'fv-ex2-apollo-r203.php').read_text('utf-8').replace('r203','r204').replace('R203','R204')
    assert php.count(sha(old))==1
    php=php.replace(sha(old),sha(new),1)
    assert sha(css) in php and sha(js) in php
    files={'templates/atlas-fragment.html':new,'assets/atlas-scoped.css':css,
           'assets/campaign-handoff.js':js,'fv-ex2-apollo-r204.php':php.encode('utf-8')}
    for path,data in sorted(files.items()):
        output=DIST/path;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data)
    shim=(prior/'wp-render-shim-r203.php').read_text('utf-8').replace('r203','r204').replace('R203','R204')
    (DIST/'wp-render-shim-r204.php').write_text(shim,encoding='utf-8')
    conversion=(prior/'conversion-validation.json').read_bytes()
    (DIST/'conversion-validation.json').write_bytes(conversion)
    manifest={'release':'r204','parent_sha':'c1966b75330c04e4a2e853be39519691c3d7ae38',
      'scope':'Repair Research Desk crosswalk independent landmark, preserving all source/CTA behavior',
      'files':{k:sha(v) for k,v in sorted(files.items())},
      'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
      'commercial_plan_sha256':sha(conversion),
      'known_canonical_r198_builder_git_blob':'57ef73d5719662a1b3647536a0eace5fb65bac4a',
      'known_local_r198_builder_git_blob':'2e09257cbd0b32a93f2e7e034a84685d93ed93f5',
      'source_chain_verified':False,
      'release_gate':'HOLD: canonical ancestor mismatch; axe-core, WP staging, assistive technology, hosted CI, founder approval, merchant validation'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return manifest
if __name__=='__main__':print(json.dumps(build(),indent=2))
