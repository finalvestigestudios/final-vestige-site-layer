#!/usr/bin/env python3
"""Apollo R199: distinct NASA source links with bound limitations; staging only."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r198'
DIST = HERE / 'dist'
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
CLAIMS = (
    ('oxygen', 'oxygen atmosphere'),
    ('fire', 'ignition uncertainty'),
    ('hatch', 'hatch and escape'),
    ('chronology', 'cabin pressure chronology'),
)
CSS = '''\n/* R199: source/limitation pairs stay visibly connected during keyboard navigation. */
.fv-apollo-atlas .fv-apollo-trace-grid li:focus-within{outline:2px solid var(--accent);outline-offset:2px}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-trace-grid li:focus-within{outline-color:Highlight}}
@media print{.fv-apollo-atlas .fv-apollo-trace-grid li:focus-within{outline:0!important}}
'''
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def build() -> dict:
    sys.path.insert(0, str(PARENT))
    from build_r198 import build as build_parent
    parent = build_parent()
    prior = PARENT / 'dist'
    for path, digest in parent['files'].items():
        assert sha((prior / path).read_bytes()) == digest, 'parent artifact integrity: ' + path
    old_html = (prior / 'templates/atlas-fragment.html').read_bytes()
    html = old_html.decode('utf-8')
    assert html.count('Read NASA technical source</a>') == 4
    assert html.count('<details>') == 8 and html.count('class="cta"') == 1
    for slug, subject in CLAIMS:
        pattern = r'<li data-finding="fv-apollo-finding-' + slug + r'"[^>]*>.*?</li>'
        matches = list(re.finditer(pattern, html, re.S))
        assert len(matches) == 1, 'missing/duplicate claim ' + slug
        original = matches[0].group()
        assert original.count('href="' + BOARD + '"') == 1
        assert original.count('<p><b>Boundary:</b>') == 1
        boundary_id = 'fv-apollo-source-limit-' + slug
        revised = original.replace('<p><b>Boundary:</b>', '<p id="' + boundary_id + '"><b>Boundary:</b>', 1)
        revised = revised.replace('href="' + BOARD + '"',
            'href="' + BOARD + '" aria-describedby="' + boundary_id + '" data-authority="nasa-apollo-204-board"', 1)
        revised = revised.replace('Read NASA technical source</a>',
            'Read NASA Review Board report about ' + subject + '</a>', 1)
        assert revised != original
        html = html.replace(original, revised, 1)
    anchor = '<p>All four technical findings use the Apollo 204 Review Board, not an archival photograph, as their source of record. A source link is a way to check our wording, not a claim that NASA endorses this site.</p>'
    assert html.count(anchor) == 1
    html = html.replace(anchor, anchor + '\n<p class="fv-apollo-source-context">Each technical-source link opens the complete NASA Review Board report, not a claim-specific excerpt. The limitation beside each link explains what that report cannot establish.</p>', 1)
    assert html.count('Read NASA technical source</a>') == 0
    assert html.count('aria-describedby="fv-apollo-source-limit-') == 4
    old_css = (prior / 'assets/atlas-scoped.css').read_bytes()
    css = old_css + CSS.encode('utf-8')
    php = (prior / 'fv-ex2-apollo-r198.php').read_text('utf-8').replace('r198', 'r199').replace('R198', 'R199')
    for before, after in ((old_html, html.encode('utf-8')), (old_css, css)):
        digest = sha(before)
        assert php.count(digest) == 1, 'missing SHA-256 asset pin'
        php = php.replace(digest, sha(after), 1)
    js = (prior / 'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php
    files = {'templates/atlas-fragment.html': html.encode('utf-8'),
        'assets/atlas-scoped.css': css, 'assets/campaign-handoff.js': js,
        'fv-ex2-apollo-r199.php': php.encode('utf-8')}
    for path, blob in sorted(files.items()):
        dest = DIST / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
    shim = (prior / 'wp-render-shim-r198.php').read_text('utf-8').replace('r198', 'r199').replace('R198', 'R199')
    (DIST / 'wp-render-shim-r199.php').write_text(shim, encoding='utf-8')
    manifest = {'release':'r199', 'parent_head':'bff83305dd71913105c8008115d657869dffd11a',
        'scope':'Four distinct source accessible names, linked per-claim limitations, no-JS visual focus, full-report disclosure',
        'files':{key:sha(blob) for key,blob in sorted(files.items())},
        'parent_manifest_sha256':sha((prior / 'manifest.json').read_bytes()),
        'release_gate':'STAGING_HOLD; no installed WP, axe-core, production analytics, rights or checkout acceptance'}
    (DIST / 'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return manifest
if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
