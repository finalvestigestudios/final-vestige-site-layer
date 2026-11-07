#!/usr/bin/env python3
"""R194 isolated, deterministic Apollo evidence-to-investigation trust boundary.

Never writes WordPress, merchant, homepage, video/creator, analytics or existing
ancestor files. R193 dist can be generated from its pinned GitHub ancestry.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'apollo-r193'/'dist'
DIST=HERE/'dist'
INTRO='<p class="small">Free historical analysis. An Apollo educator dossier is a proposed product, not a verified item for sale. No purchase, signup or affiliate conversion is claimed here.</p>'
ADDITION=('<p class="small fv-apollo-source-boundary"><strong>Verify before continuing:</strong> '
          'the <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">'
          'Apollo 204 Review Board report</a> is the technical source. NASA photograph catalog entries are '
          'separate archival evidence; they cannot prove the ignition source or grant commercial advertising rights. '
          'The next link opens Final Vestige\'s free investigation, not a checkout.</p>')
CSS='''\n/* R194: a quiet source boundary adjacent to the single editorial CTA. */
.fv-apollo-atlas .fv-apollo-source-boundary{border-left:2px solid var(--accent);padding:.55rem 1rem;max-width:70ch}
@media print{.fv-apollo-atlas .fv-apollo-source-boundary{border-left-color:#444!important;color:#000!important}}
'''

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def build():
    if not (PARENT/'manifest.json').exists():
        subprocess.run([sys.executable,str(HERE.parent/'apollo-r193'/'build_r193.py')],check=True)
    m=json.loads((PARENT/'manifest.json').read_text())
    names=['templates/atlas-fragment.html','assets/atlas-scoped.css','assets/campaign-handoff.js','fv-ex2-apollo-r193.php']
    for n in names:
        b=(PARENT/n).read_bytes()
        assert sha(b)==m['files'][n], 'R193 parent mismatch: '+n
    old=(PARENT/'templates/atlas-fragment.html').read_text()
    old_css=(PARENT/'assets/atlas-scoped.css').read_text()
    old_php=(PARENT/'fv-ex2-apollo-r193.php').read_text()
    assert old.count(INTRO)==1,'single existing non-commercial CTA notice required'
    assert old.count('class="cta"')==1
    assert 'fv-apollo-source-boundary' not in old
    html=old.replace(INTRO, INTRO+ADDITION)
    css=old_css+CSS
    php=old_php.replace('r193','r194').replace('R193','R194')
    for before,after in ((sha(old.encode()),sha(html.encode())),(sha(old_css.encode()),sha(css.encode()))):
        assert php.count(before)==1, 'one exact parent pin expected'
        php=php.replace(before,after)
    # Preserve JS digest; the optional handoff is not changed by this sprint.
    assert sha((PARENT/'assets/campaign-handoff.js').read_bytes()) in php
    assets={'templates/atlas-fragment.html':html.encode(),
            'assets/atlas-scoped.css':css.encode(),
            'assets/campaign-handoff.js':(PARENT/'assets/campaign-handoff.js').read_bytes(),
            'fv-ex2-apollo-r194.php':php.encode()}
    for name,data in assets.items():
        path=DIST/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    parent_shim=(PARENT/'wp-render-shim-r193.php').read_text().replace('r193','r194').replace('R193','R194')
    (DIST/'wp-render-shim-r194.php').write_text(parent_shim)
    ledger={
      'release':'r194','parent':'R193 draft PR #1433 / cb9dbcc8ffa1fbaf9f57f8a1a37a770361570d12',
      'change':'One proximal technical-source verification note at the free investigation CTA; no purchase offer',
      'source_rights':'NASA advertising rights and astronaut likeness permissions NOT cleared; text-only citation, no images',
      'claim_basis':{'ignition':'NASA Apollo 204 Review Board; ignition source not conclusively proven',
                     'gallery':'NASA archival image catalog; images neither ignition frames nor licensed commercial creatives'},
      'commercial_gate':'Founder/Claude to verify matching rights-cleared product, actual checkout and merchant orders',
      'files':{name:sha(data) for name,data in sorted(assets.items())},
      'parent_manifest_sha256':sha((PARENT/'manifest.json').read_bytes())}
    (DIST/'manifest.json').write_text(json.dumps(ledger,sort_keys=True,indent=2)+'\n')
    return ledger
if __name__=='__main__':print(json.dumps(build(),indent=2))
