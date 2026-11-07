#!/usr/bin/env python3
"""R186: source-pinned Apollo Atlas landmark repair; unpublished plugin build.

Reuses R185's verified R183/R184 asset chain. No network, CMS writes, or deployment.
The --reuse-r185-dist switch is for testing a SHA-pinned archived R185 build.
"""
from pathlib import Path
import hashlib, importlib.util, json, shutil, sys

HERE = Path(__file__).resolve().parent
R185 = HERE.parent / 'apollo-r185'
OUT = HERE / 'dist'
EXPECTED_R185_HTML = '8d4a9dfd1181684381bac6021d2a37c540bfb053441c81098fee8c9a02b7f930'
EXPECTED_R185_CSS = 'dddb5a73a58d266f5d5dc67f88b7114c15fb8736134b2c345126717f91c1d7b6'
# Four actual R184 namespacing regressions. The article's title reference already works.
LANDMARKS = {
    'page-title': 'fv-apollo-page-title',
    'chronology-title': 'fv-apollo-chronology-title',
    'evidence-title': 'fv-apollo-evidence-title',
    'gallery-title': 'fv-apollo-gallery-title',
}

def sha(payload):
    return hashlib.sha256(payload).hexdigest()

def source_verify(html, css):
    if sha(html) != EXPECTED_R185_HTML or sha(css) != EXPECTED_R185_CSS:
        raise ValueError('R185 exact source pin mismatch; refusing release candidate')

def repair(html):
    original = html.decode('utf-8')
    fixed = original
    for old, new in LANDMARKS.items():
        attr = f'aria-labelledby="{old}"'
        if fixed.count(attr) != 1 or fixed.count(f'id="{new}"') != 1:
            raise ValueError(f'Unexpected source/label count for {old}; refusing to guess')
        fixed = fixed.replace(attr, f'aria-labelledby="{new}"', 1)
    assert fixed != original
    return fixed.encode('utf-8')

def build(reuse=False):
    source = R185 / 'dist'
    spec = importlib.util.spec_from_file_location('fv_apollo_r185', R185 / 'build_r185.py')
    if not spec or not spec.loader:
        raise RuntimeError('R185 builder unavailable')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if not reuse:
        mod.build()
    render_php = mod.render_php
    raw_html = (source/'templates/atlas-fragment.html').read_bytes()
    css = (source/'assets/atlas-scoped.css').read_bytes()
    source_verify(raw_html, css)
    html = repair(raw_html)
    if html.decode() != repair(raw_html).decode():
        raise RuntimeError('Non-deterministic repair')
    (OUT/'templates').mkdir(parents=True,exist_ok=True)
    (OUT/'assets').mkdir(parents=True,exist_ok=True)
    (OUT/'templates/atlas-fragment.html').write_bytes(html)
    (OUT/'assets/atlas-scoped.css').write_bytes(css)
    php = render_php(sha(html), sha(css)).replace('r185','r186').replace('R185','R186')
    php_file=OUT/'fv-ex2-apollo-r186.php'
    php_file.write_text(php,encoding='utf-8')
    manifest={'r185_fragment_sha256':sha(raw_html),'r185_css_sha256':sha(css),
              'r186_fragment_sha256':sha(html),'r186_php_sha256':sha(php.encode()),
              'landmarks_repaired':LANDMARKS,'deployment':'NOT_INSTALLED',
              'wordpress_staging_tested':False,'axe_executed':False,'orders_verified':False}
    (OUT/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    return manifest

if __name__=='__main__':
    print(json.dumps(build(reuse='--reuse-r185-dist' in sys.argv),sort_keys=True,indent=2))
