#!/usr/bin/env python3
"""R200 staging-only ChronologyRail evidence-mode labels and machine-readable custody manifest.

No new image assets, external scripts, source claims, commercial CTA or tracking.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r199'
DIST = HERE / 'dist'
CHRONOLOGY = (
    ('1966-10-18', 'fv-apollo-photo-1966', 'Catalog photograph · before the accident', 'archival-photo', 'https://www.nasa.gov/image-detail/amf-s66-58038/'),
    ('1967-01-03', 'fv-apollo-photo-prep', 'Preparation record · before the accident', 'photo-and-history', 'https://www.nasa.gov/humans-in-space/55-years-ago-final-preparations-for-the-planned-launch-of-apollo-1/'),
    ('1967-01-27', 'fv-apollo-finding-fire', 'Review Board account · accident date', 'technical-report', 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'),
    ('1967-01-28', 'fv-apollo-photo-aftermath', 'Catalog photograph · the following day', 'aftermath-photo', 'https://www.nasa.gov/image-detail/amf-s67-21294/'),
)
CSS = '''\n/* R200 chronology evidence roles: readable, not color-only, no additional scripting. */
.fv-apollo-atlas .rail li{min-width:0;overflow-wrap:anywhere}
.fv-apollo-atlas .rail .fv-apollo-rail-kind{display:block;width:fit-content;max-width:100%;margin:.48rem 0;font-size:.72rem;line-height:1.55;letter-spacing:.025em;font-weight:700;color:var(--paper);border:1px solid var(--line);border-radius:2px;padding:.15rem .45rem;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-rail-reading-key{margin:.8rem 0 1.2rem;max-width:72ch;font-size:.92rem;line-height:1.65;overflow-wrap:anywhere}
.fv-apollo-atlas .rail a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
@media(forced-colors:active){.fv-apollo-atlas .rail .fv-apollo-rail-kind{border-color:CanvasText;color:CanvasText}.fv-apollo-atlas .rail a:focus-visible{outline-color:Highlight}}
@media print{.fv-apollo-atlas .rail .fv-apollo-rail-kind{color:#111!important;border-color:#444!important}.fv-apollo-atlas .fv-apollo-rail-reading-key{color:#111!important}}
'''

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def build() -> dict:
    sys.path.insert(0, str(PARENT))
    from build_r199 import build as parent_build
    parent = parent_build()
    prior = PARENT/'dist'
    for path, digest in parent['files'].items():
        assert sha((prior/path).read_bytes()) == digest, 'parent integrity failed: '+path
    old_html = (prior/'templates/atlas-fragment.html').read_bytes()
    html = old_html.decode('utf-8')
    assert html.count('<ol class="rail">') == 1
    assert html.count('</ol></section>\n<section aria-labelledby="fv-apollo-evidence-title"') == 1
    for date, target, badge, kind, official_url in CHRONOLOGY:
        needle = '<li><time datetime="'+date+'">'
        assert html.count(needle) == 1, 'chronology date uniqueness: '+date
        assert html.count('id="'+target+'"') == 1, 'resolved evidence destination: '+target
        # Type is a source class, not a causal inference. The existing text remains intact.
        html = html.replace(needle,'<li data-evidence-kind="'+kind+'"><time datetime="'+date+'">',1)
        end = '<a href="#'+target+'">'
        start = html.index('<li data-evidence-kind="'+kind+'">')
        assert html[start:].count(end) >= 1
        anchor = html.index(end,start)
        html = html[:anchor]+'<span class="fv-apollo-rail-kind">'+badge+'</span>'+html[anchor:]
    tail='</ol></section>\n<section aria-labelledby="fv-apollo-evidence-title"'
    note= ('</ol><p class="fv-apollo-rail-reading-key" id="fv-apollo-rail-reading-key">'
           '<strong>Reading the record:</strong> this rail puts dated photographs, a NASA historical preparation account, '
           'and the Apollo 204 Review Board account in sequence. A photograph is not a sensor trace; '
           'a source date is not proof of a particular ignition mechanism. '
           '<a href="https://www.nasa.gov/gallery/apollo-1/">Compare the NASA Apollo 1 photo catalog</a> '
           'with the <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">NASA Review Board findings</a>.</p></section>\n'
           '<section aria-labelledby="fv-apollo-evidence-title"')
    assert html.count(tail)==1
    html=html.replace(tail,note,1)
    assert html.count('data-evidence-kind=')==4
    assert html.count('class="cta"')==1 and html.count('<details>')==8
    prior_css=(prior/'assets/atlas-scoped.css').read_bytes()
    css=prior_css+CSS.encode('utf-8')
    php=(prior/'fv-ex2-apollo-r199.php').read_text('utf-8').replace('r199','r200').replace('R199','R200')
    for before, after in ((old_html,html.encode('utf-8')),(prior_css,css)):
        assert php.count(sha(before))==1,'missing parent SHA-256 pin'
        php=php.replace(sha(before),sha(after),1)
    js=(prior/'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php
    files={'templates/atlas-fragment.html':html.encode('utf-8'),
           'assets/atlas-scoped.css':css,'assets/campaign-handoff.js':js,
           'fv-ex2-apollo-r200.php':php.encode('utf-8')}
    for path,blob in sorted(files.items()):
        dest=DIST/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
    shim=(prior/'wp-render-shim-r199.php').read_text('utf-8').replace('r199','r200').replace('R199','R200')
    (DIST/'wp-render-shim-r200.php').write_text(shim,encoding='utf-8')
    source_ledger=[dict(date=date,target=target,evidence_kind=kind,visible_label=badge,official_source=source,commercial_media_rights='not_certified')
                   for date,target,badge,kind,source in CHRONOLOGY]
    (DIST/'chronology-source-ledger.json').write_text(json.dumps(source_ledger,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    manifest={'release':'r200','parent_head':'d89b57bc8ea159077f6216c1d7aea50fc3fab815',
      'scope':'Visible distinct chronology source roles plus machine-readable dated source ledger; same single free investigation CTA',
      'files':{k:sha(v) for k,v in sorted(files.items())},
      'chronology_source_ledger_sha256':sha((DIST/'chronology-source-ledger.json').read_bytes()),
      'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
      'release_gate':'DRAFT; installed WordPress, axe-core, assistive technology, host CI, founder approval and commercial checkout acceptance outstanding'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return manifest
if __name__=='__main__': print(json.dumps(build(),indent=2))
