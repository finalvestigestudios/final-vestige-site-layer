#!/usr/bin/env python3
"""R195: focus-target repair for eight in-page Apollo evidence journeys.

Deterministically builds a separate WordPress staging candidate from R194.
No WordPress, homepage, creator, analytics, or merchant writes.
"""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r194'
DIST = HERE / 'dist'
CSS_PATCH = """
/* R195: shrink the one-column hero grid instead of honoring long-word min-content;
   preserve readable, non-scrolling reflow at 200% browser zoom. */
@media(max-width:840px){.fv-apollo-atlas .hero{grid-template-columns:minmax(0,1fr)}.fv-apollo-atlas .hero>*{min-width:0}}
.fv-apollo-atlas h1{overflow-wrap:anywhere}
"""
TARGETS = ('fv-apollo-main', 'fv-apollo-chronology', 'fv-apollo-evidence',
           'fv-apollo-gallery', 'fv-apollo-photo-1966', 'fv-apollo-photo-prep',
           'fv-apollo-finding-fire', 'fv-apollo-photo-aftermath')

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def build():
    sys.path.insert(0, str(PARENT))
    from build_r194 import build as build_parent
    parent = build_parent()
    old = (PARENT / 'dist')
    for name, digest in parent['files'].items():
        assert sha((old / name).read_bytes()) == digest, 'R194 parent digest mismatch: ' + name
    html = (old / 'templates/atlas-fragment.html').read_text()
    php = (old / 'fv-ex2-apollo-r194.php').read_text()
    # Anchor destinations must be unique. tabindex=-1 enables focus without
    # introducing additional sequential tab stops or requiring JavaScript.
    for anchor in TARGETS:
        pattern = r'(<(?:div|section|article)\b[^>]*\bid="' + re.escape(anchor) + r'"[^>]*)(>)'
        assert len(re.findall(pattern, html)) == 1, 'Missing/ambiguous destination: ' + anchor
        html = re.sub(pattern, lambda m: m.group(1) + ' tabindex="-1"' + m.group(2), html, count=1)
        assert html.count('href="#' + anchor + '"') >= 1, 'Orphan focus destination: ' + anchor
    for href in re.findall(r'href="#([^"]+)"', html):
        assert href in TARGETS, 'Unreviewed internal destination: ' + href
    assert html.count('tabindex="-1"') == len(TARGETS)
    old_html = (old / 'templates/atlas-fragment.html').read_bytes()
    php = php.replace('r194', 'r195').replace('R194', 'R195')
    assert php.count(sha(old_html)) == 1, 'Expected one parent HTML integrity pin'
    php = php.replace(sha(old_html), sha(html.encode()))
    js = (old / 'assets/campaign-handoff.js').read_bytes()
    old_css = (old / 'assets/atlas-scoped.css').read_bytes()
    css = old_css + CSS_PATCH.encode()
    assert php.count(sha(old_css)) == 1, 'Expected one parent CSS integrity pin'
    php = php.replace(sha(old_css), sha(css))
    assert sha(js) in php, 'Unchanged optional script integrity pin missing'
    files = {'templates/atlas-fragment.html':html.encode(),
             'assets/atlas-scoped.css':css,
             'assets/campaign-handoff.js':js,
             'fv-ex2-apollo-r195.php':php.encode()}
    for name, data in files.items():
        dest = DIST / name; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    shim = (old / 'wp-render-shim-r194.php').read_text()
    (DIST / 'wp-render-shim-r195.php').write_text(shim.replace('r194','r195').replace('R194','R195'))
    manifest = {'release':'r195','parent_head':'051fbc829f3e26994c8b80d7726af88aff2a7abd',
      'change':'In-page keyboard destinations take focus; 200% zoom reflows hero text without horizontal overflow',
      'targets':list(TARGETS),'files':{name:sha(data) for name,data in sorted(files.items())},
      'parent_manifest_sha256':sha((old / 'manifest.json').read_bytes()),
      'rights':'Source links only. No NASA commercial image, likeness or endorsement permissions certified.',
      'commercial':'Free investigation remains sole CTA; proposed educator dossier is not purchasable.'}
    (DIST / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2)+'\n')
    return manifest

if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
