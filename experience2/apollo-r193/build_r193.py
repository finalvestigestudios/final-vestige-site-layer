#!/usr/bin/env python3
"""R193: deterministic, staging-only Apollo Atlas source-disclosure labels.

Read the pinned R191 content from the R192 ancestry. Never change an ancestor,
production WordPress content, campaign code, or NASA source destinations.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r191' / 'dist'
DIST = HERE / 'dist'
EXPECTED = (
    ('Examine source custody', 'Read the NASA source for the oxygen atmosphere'),
    ('Examine source custody', 'Read the NASA source for ignition uncertainty'),
    ('Examine source custody', 'Read the NASA source for the inward-opening hatch'),
    ('Examine source custody', 'Read the NASA source for cabin pressure'),
    ('Open source details', 'Read catalog details for NASA S66-58038'),
    ('Open source details', 'Read catalog details for NASA S67-15717'),
    ('Open source details', 'Read catalog details for NASA S67-21294'),
    ('Open source details', 'Read catalog details for the 2017 hatch exhibit'),
)

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def build() -> dict:
    if not (PARENT/'manifest.json').exists():
        subprocess.run([sys.executable,str(HERE.parent/'apollo-r191'/'build_r191.py')],check=True)
    parent_manifest = json.loads((PARENT/'manifest.json').read_text())
    for name in ['templates/atlas-fragment.html', 'assets/atlas-scoped.css', 'assets/campaign-handoff.js']:
        assert (PARENT/name).exists(), f'missing pinned R191 input: {name}'
    html_path = PARENT/'templates/atlas-fragment.html'
    original = html_path.read_text()
    original_digest = sha(original.encode())
    # Parent manifest is a source-custody record, but R191 hard-coded PHP pins
    # are the actual executable integrity gate, so check them independently.
    original_php = (PARENT/'fv-ex2-apollo-r191.php').read_text()
    assert original_digest in original_php, 'source HTML no longer matches PHP custody pin'
    html = original
    # Each native disclosure remains functional and labels its evidence rather
    # than presenting eight ambiguous/duplicate buttons to screen-reader users.
    for generic, specific in EXPECTED:
        assert html.count('<summary>'+generic+'</summary>') >= 1, generic
        html = html.replace('<summary>'+generic+'</summary>', '<summary>'+specific+'</summary>', 1)
    assert html.count('<details>') == 8
    assert len({new for _, new in EXPECTED}) == 8
    assert '<summary>Examine source custody</summary>' not in html
    assert '<summary>Open source details</summary>' not in html
    # Correctly update R191 integrity pin and independent function and handle
    # namespaces. Do NOT modify its NASA links, copy, analytics or CTA.
    php = original_php.replace('r191', 'r193').replace('R191', 'R193')
    assert original_digest in php
    php = php.replace(original_digest, sha(html.encode()))
    assert original_digest not in php
    assets = {
        'templates/atlas-fragment.html': html.encode(),
        'assets/atlas-scoped.css': (PARENT/'assets/atlas-scoped.css').read_bytes(),
        'assets/campaign-handoff.js': (PARENT/'assets/campaign-handoff.js').read_bytes(),
        'fv-ex2-apollo-r193.php': php.encode(),
    }
    # Verify the parent file SHA pins survive for CSS and optional JS.
    for name in ('assets/atlas-scoped.css','assets/campaign-handoff.js'):
        assert sha(assets[name]) in php, name
    for name, data in assets.items():
        path = DIST/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    manifest = {
        'release':'r193', 'parent_html_sha256': original_digest,
        'ancestry':'R192 PR #1426 at 34592aa346a0798acf579213bd2a0b2b8da527b1',
        'scope':'accessible source disclosure labels; no NASA claims or destination changes',
        'files':{name:sha(data) for name,data in sorted(assets.items())},
        'labels':[new for _,new in EXPECTED],
        'printed_source_count':8,
        'source_manifest_from_r191': bool(parent_manifest),
    }
    (DIST/'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2)+'\n')
    return manifest

if __name__ == '__main__':
    print(json.dumps(build(),indent=2))
