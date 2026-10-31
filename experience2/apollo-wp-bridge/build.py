#!/usr/bin/env python3
"""Deterministic, static-first Apollo casefile -> isolated WordPress shortcode assets.

No website writes and no network. Requires tinycss2 1.5.x at *build time only*;
PHP/WordPress runtime needs no Python, JS libraries or paid services.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import tinycss2
import os

BRIDGE = Path(__file__).resolve().parent
ROOT = BRIDGE.parent / 'apollo-casefile'
OUT = BRIDGE / 'generated'
SOURCE_FILES = (
    'render.py','trail.py','response_lab.py',
    'assets/app.css','assets/response.css','assets/trail.css',
    'assets/app.js','assets/response.js','assets/trail.js',
    'records.json','custody.json','response-crosswalk.json',
)
EXPORTS=('evidence-export.csv','evidence-export.json','response-export.csv','response-export.json')
CSS_FILES=('app.css','response.css','trail.css')
JS_FILES=('app.js','response.js','trail.js')
PLACEHOLDER='{{FV_EX2_ASSET_BASE}}'


def digest(raw:bytes)->str: return hashlib.sha256(raw).hexdigest()

def scope_prelude(prelude):
    """Prefix top-level comma-separated selectors without splitting function args."""
    groups=[];curr=[]
    for token in prelude:
        if token.type=='literal' and token.value==',':
            groups.append(curr);curr=[]
        else:curr.append(token)
    groups.append(curr)
    normalized=[]
    for group in groups:
        sel=tinycss2.serialize(group).strip()
        if not sel:raise ValueError('Empty CSS selector')
        if sel in (':root','html','body'):
            normalized.append('.fv-ex2-apollo')
        elif sel.startswith(':root ') or sel.startswith('html ') or sel.startswith('body '):
            normalized.append(re.sub(r'^(?:html|body|:root)(?=\s)', '.fv-ex2-apollo',sel,count=1))
        elif sel.startswith('html:') or sel.startswith('body:'):
            # Pseudo-class on root document is unsupported in an embedded region.
            raise ValueError('Unsupported global pseudo selector: '+sel)
        else:
            normalized.append('.fv-ex2-apollo '+sel)
    return ','.join(normalized)


def scope_css(content:str)->str:
    rules=tinycss2.parse_stylesheet(content,skip_whitespace=False,skip_comments=False)
    parts=[]
    for r in rules:
        if r.type in ('whitespace','comment'):
            parts.append(r.serialize());continue
        if r.type=='error':raise ValueError('Invalid CSS: '+r.message)
        if r.type=='qualified-rule':
            parts.append(scope_prelude(r.prelude)+'{'+tinycss2.serialize(r.content)+'}')
        elif r.type=='at-rule':
            keyword=r.lower_at_keyword
            if keyword in ('import','namespace','font-face'):
                raise ValueError('Unapproved CSS at-rule: '+keyword)
            if keyword in ('media','supports','container'):
                inner=tinycss2.serialize(r.content) if r.content else ''
                parts.append('@'+keyword+tinycss2.serialize(r.prelude)+'{'+scope_css(inner)+'}')
            elif keyword in ('keyframes','-webkit-keyframes'):
                # Keyframe selectors are percentages, not scoped element selectors.
                parts.append(r.serialize())
            else:raise ValueError('Unreviewed CSS at-rule: '+keyword)
        else:raise ValueError('Unexpected CSS rule '+r.type)
    css=''.join(parts)
    # A shortcode must NEVER emit an unscoped page-level font/body override.
    if re.search(r'(?<![\w-])(?:body|html|:root)\s*\{',css):
        raise ValueError('Unscoped document CSS')
    return css


def build()->dict:
    if not ROOT.is_dir():raise ValueError('Missing sibling experience2/apollo-casefile source')
    for item in SOURCE_FILES:
        if not (ROOT/item).is_file():raise ValueError('Missing upstream file: '+item)
    pin=json.loads((BRIDGE/'upstream-pr215-blobs.json').read_text(encoding='utf-8'))
    hashes={item:hashlib.sha1(b'blob '+str((ROOT/item).stat().st_size).encode()+b'\0'+(ROOT/item).read_bytes()).hexdigest() for item in SOURCE_FILES}
    mismatches={name:{'expected':wanted,'actual':hashes.get(name)} for name,wanted in pin['expected_blob_sha1'].items() if hashes.get(name)!=wanted}
    if mismatches and os.environ.get('FV_EX2_ALLOW_UNPINNED_FIXTURE')!='1':
        raise RuntimeError('SOURCE_PIN_MISMATCH: refusing build from unreviewed inputs: '+json.dumps(mismatches,sort_keys=True))
    # Create the canonical static rendering and deterministic exports, never fetch data.
    run=subprocess.run([sys.executable,str(ROOT/'render.py')],cwd=str(ROOT),capture_output=True,text=True,timeout=60)
    if run.returncode:raise RuntimeError('Upstream Apollo render failed: '+run.stdout+run.stderr)
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    m=re.search(r'<main id="main">([\s\S]+?)</main><script>',html)
    if not m or html.count('<main id="main">')!=1:
        raise ValueError('Upstream HTML shape changed: expected one canonical main')
    fragment=m.group(1)
    if fragment.count('<h1 id="case-title">')!=1:
        raise ValueError('Expected one Apollo hero heading')
    fragment=fragment.replace('<h1 id="case-title">','<h2 id="case-title">').replace('</h1>','</h2>')
    fragment=fragment.replace('href="#main"','href="#fv-ex2-apollo-top"')
    fragment='<div class="fv-ex2-apollo__content" id="fv-ex2-apollo-top">'+fragment+'</div>'
    # All four export links become a WordPress plugin-owned, explicit URL at runtime.
    for export in EXPORTS:
        if f'href="{export}"' not in fragment:raise ValueError('Missing expected export: '+export)
        fragment=fragment.replace(f'href="{export}"',f'href="{PLACEHOLDER}/{export}"')
    if '<script' in fragment.lower() or '<style' in fragment.lower() or re.search(r'<\s*img\b',fragment,re.I):
        raise ValueError('Fragment contains script/style or historical image not approved for reproduction')
    if PLACEHOLDER.count('{')!=2 or fragment.count(PLACEHOLDER)!=len(EXPORTS):
        raise ValueError('Asset URL substitution error')
    for tag in ('main','body','html','head'):
        if re.search(r'<\s*/?\s*'+tag+r'(?:\s|>)',fragment,re.I):
            raise ValueError('Standalone document landmark leaked into shortcode: '+tag)
    for name in ('chronology','research-desk','claim-ledger','comparison-lab','response-audit','documentary-trails','source-gallery','atlas'):
        if f'id="{name}"' not in fragment:raise ValueError('Missing expected document chapter: '+name)
    css='\n'.join((ROOT/'assets'/name).read_text(encoding='utf-8') for name in CSS_FILES)
    scoped=scope_css(css).replace('.fv-ex2-apollo .ex2-hero h1','.fv-ex2-apollo .ex2-hero h2')
    scoped+='\n.fv-ex2-apollo{display:block;margin-inline:auto;max-width:100%;overflow-wrap:anywhere}.fv-ex2-apollo__content{min-width:0}.fv-ex2-apollo [hidden]{display:none!important}\n'
    js='\n'.join((ROOT/'assets'/name).read_text(encoding='utf-8') for name in JS_FILES)
    if any(x in js.lower() for x in ('fetch(', 'xmlhttprequest','sendbeacon','localstorage','sessionstorage')):
        raise ValueError('Unreviewed remote API or local storage in enhancement JS')
    OUT.mkdir(parents=True,exist_ok=True)
    contents={'fragment.html':fragment.encode('utf-8'),'apollo.css':scoped.encode('utf-8'),'apollo.js':js.encode('utf-8')}
    for export in EXPORTS:contents[export]=(ROOT/export).read_bytes()
    for name,raw in sorted(contents.items()):
        (OUT/name).write_bytes(raw)
    manifest={
      'schema_version':1,
      'status':'STAGING_ONLY_UNREVIEWED_FOR_PUBLICATION',
      'upstream':'Experience 2.0 Apollo 1 casefile; PR #215 historical baseline',
      'pinned_head':pin['pinned_head'],
      'source_matches_pr215':not bool(mismatches),
      'source_pin_mismatches':sorted(mismatches),
      'upstream_source_git_blob_sha1':hashes,
      'outputs_sha256':{name:digest(raw) for name,raw in sorted(contents.items())},
      'outputs_bytes':{name:len(raw) for name,raw in sorted(contents.items())},
      'release_gates':['Install only in isolated WordPress staging after separate approval',
          'Validate no namespace/theme CSS collisions, shortcode nested/template rendering, JS/CSP on actual WP',
          'Verify export route and MIME headers on staging',
          'Independently review media rights and quoted historical evidence',
          'Real axe-core, Safari/VoiceOver/NVDA, LCP/CLS/INP, hosted CI and independent QD',
          'Founder approval before merge or live WordPress content/settings changes'],
    }
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    summary=build()
    print('BRIDGE_BUILD_PASS',len(summary['outputs_sha256']),'outputs',summary['status'])
