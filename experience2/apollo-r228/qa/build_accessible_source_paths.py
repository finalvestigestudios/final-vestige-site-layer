#!/usr/bin/env python3
"""R228: exact-input, append-only tap-target treatment for source-to-finding paths.

Builds a disposable staging adapter from SHA-pinned R225 dist; no WP mutations.
Does not imply NASA rights, installed WP acceptance or a paid Apollo offer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

PARENT_MANIFEST = '4efaf0a57d38af349d44302905fbfdc8b8936ac8bbc04a2d7a61fb805ba93628'
CSS_APPEND = '''
/* R228: distinguish dense inline editorial citations from standalone source-navigation
   actions. Source-trace jumps and custody record actions are navigation, not prose.
   WCAG 2.2 2.5.8 minimum target at least 24 CSS px; provide 44px for touch.
   No JavaScript, page-level layout styling, badges or commerce added. */
.fv-apollo-atlas .fv-apollo-trace-grid li p>a[href^="#"],
.fv-apollo-atlas .fv-apollo-custody-list li>p>a{
  display:inline-flex;align-items:center;min-height:44px;
  padding-block:.55rem;max-width:100%;white-space:normal;
  overflow-wrap:anywhere;text-underline-offset:.2em;
}
.fv-apollo-atlas .fv-apollo-trace-grid li p>a[href^="#"]:focus-visible,
.fv-apollo-atlas .fv-apollo-custody-list li>p>a:focus-visible{
  outline:3px solid #f6cf86;outline-offset:2px;
}
@media(forced-colors:active){
  .fv-apollo-atlas .fv-apollo-trace-grid li p>a[href^="#"]:focus-visible,
  .fv-apollo-atlas .fv-apollo-custody-list li>p>a:focus-visible{
    outline-color:Highlight;
  }
}
@media(prefers-reduced-motion:reduce){
  .fv-apollo-atlas .fv-apollo-trace-grid li p>a[href^="#"],
  .fv-apollo-atlas .fv-apollo-custody-list li>p>a{
    scroll-behavior:auto!important;transition:none!important;
  }
}
'''

def sha(data): return hashlib.sha256(data).hexdigest()
def encode(obj):return (json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8')

def verify_parent(src):
    assert sha((src/'manifest.json').read_bytes()) == PARENT_MANIFEST, 'Parent manifest differs'
    manifest=json.loads((src/'manifest.json').read_text())
    for path, expected in manifest['files'].items():
        assert (src/path).is_file() and sha((src/path).read_bytes())==expected, 'Parent asset drift: '+path
    return manifest

def build(src,out):
    manifest=verify_parent(src)
    assert src.resolve()!=out.resolve() and not out.exists(), 'Refusing overwrite of source or existing destination'
    shutil.copytree(src,out)
    cssfile=out/'assets/atlas-scoped.css'
    original=cssfile.read_bytes()
    assert b'/* R228:' not in original
    patched=original.rstrip(b'\n')+b'\n'+CSS_APPEND.encode('utf-8')
    cssfile.write_bytes(patched)
    adapter=out/'fv-ex2-apollo-r224.php'
    php=adapter.read_text()
    oldhash=sha(original);newhash=sha(patched)
    assert php.count(oldhash)==1, 'Expected exactly one pinned CSS sha in PHP'
    php=php.replace(oldhash,newhash)
    # Keep unchanged slug/shortcode/function names so existing R227 PHP tests test the same adapter.
    adapter.write_text(php)
    manifest['files']['assets/atlas-scoped.css']=newhash
    manifest['files']['fv-ex2-apollo-r224.php']=sha(adapter.read_bytes())
    manifest['r228_parent_manifest_sha256']=PARENT_MANIFEST
    manifest['r228_change']='44px source-trace/custody navigation targets; adapter CSS hash re-pinned'
    manifest['axe_core']='NOT_EXECUTED'
    (out/'manifest.json').write_bytes(encode(manifest))
    receipt={'status':'BUILT_NOT_LIVE','parent_manifest_sha256':PARENT_MANIFEST,
       'parent_css_sha256':oldhash,'new_css_sha256':newhash,
       'new_adapter_sha256':sha(adapter.read_bytes()),
       'new_manifest_sha256':sha((out/'manifest.json').read_bytes()),
       'files_changed':['assets/atlas-scoped.css','fv-ex2-apollo-r224.php','manifest.json'],
       'source_links_edited':False,'geo_added':False,'tracked_js_added':False,
       'offer':'free original Apollo investigation only; paid dossier NOT VERIFIED'}
    (out/'r228-build-receipt.json').write_bytes(encode(receipt))
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.parent.resolve(),a.out.resolve()),indent=2))
