"""R177 isolated source-custody asset swap manifest; NEVER touches WordPress.

Reads authentic PR #158 JS and generated R176 Research Desk fragment (from the
source-pinned R176 transformer). Validates provenance and produces a staging-only
HTML *fixture*, not an installable WordPress page. The PHP adapter replacement
requires separate approval and real staging acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from html.parser import HTMLParser

ORIGINAL_JS_GIT_BLOB='32e757cc4dc8708397ff65ac21e89dd319781d78'
R174_SOURCE_GIT_BLOB='b23879150024b3b667679ff4dd7faae1e37cfc07'
SEARCH_JS_NAME='source-ledger-semantic-search.js'

def blob(s:bytes)->str:
    return hashlib.sha1(f'blob {len(s)}\0'.encode()+s).hexdigest()
def sha(s:bytes)->str: return hashlib.sha256(s).hexdigest()
class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.scripts=[];self.records=0;self.media=0;self.catalog=0
        self.inputs=0;self.status=0;self.empty=0;self.tools=0;self.forms=0;self.iframes=0
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='a': self.links.append(d.get('href',''))
        if t=='script': self.scripts.append(d.get('src','inline'))
        if t=='form':self.forms+=1
        if t=='iframe':self.iframes+=1
        if 'data-fvx-record' in d:self.records+=1
        if 'data-fvx-r174-media-custody' in d:self.media+=1
        if 'data-fvx-r175-catalog-review' in d:self.catalog+=1
        if t=='input' and 'data-fvx-search' in d:self.inputs+=1
        if 'data-fvx-status' in d:self.status+=1
        if 'data-fvx-empty' in d:self.empty+=1
        if 'data-fvx-tools' in d:self.tools+=1

def build(original_js:bytes,replacement_js:bytes,r176:bytes,*,expected_r176_sha256:str,origin:str='R176_STAGING_CANDIDATE') -> tuple[dict,bytes]:
    if blob(original_js)!=ORIGINAL_JS_GIT_BLOB: raise ValueError('HOLD: original PR #158 JS Git blob changed')
    if sha(r176)!=expected_r176_sha256: raise ValueError('HOLD: R176 HTML candidate differs from independently pinned audit SHA-256')
    if b'querySelectorAll' not in replacement_js or b'card.textContent' not in replacement_js:
        raise ValueError('HOLD: new source-custody search enhancement absent')
    if any(x in replacement_js.lower() for x in (b'fetch(',b'xmlhttprequest',b'localstorage',b'sessionstorage',b'document.cookie')):
        raise ValueError('HOLD: network or tracking functionality prohibited')
    parsed=Checker();parsed.feed(r176.decode('utf-8'))
    if (parsed.records,parsed.media,parsed.catalog,parsed.inputs,parsed.status,parsed.tools,parsed.empty)!=(6,6,1,1,1,1,1):
        raise ValueError('HOLD: unexpected record/source/control inventory')
    if len(parsed.links)!=14 or parsed.scripts or parsed.forms or parsed.iframes: raise ValueError('HOLD: source links or executable markup changed')
    doc=(b'<!doctype html><html lang="en"><head><meta charset="utf-8">'
         b'<meta name="viewport" content="width=device-width,initial-scale=1">'
         b'<title>UNPUBLISHED Research Desk semantic search acceptance fixture</title></head><body>'
         +r176+b'<script>\n'+replacement_js+b'\n</script></body></html>')
    manifest={
      'release_state':'UNPUBLISHED_STAGING_ONLY', 'source_origin':origin,
      'replacement':'ONLY source-ledger.js; original and replacement must not co-load',
      'original_pr158_script_git_blob':blob(original_js),
      'replacement_script_sha256':sha(replacement_js),
      'r176_candidate_sha256':sha(r176),
      'historical_records':parsed.records,'nasa_media_custody_records':parsed.media,
      'unverified_catalog_cautions':parsed.catalog,'preserved_links':parsed.links,
      'links_modified':False,'new_tracking_or_commerce':False,
      'production_wordpress_modified':False,'axe_tested':False,
      'actual_wordpress_staging_tested':False,
      'commercial_orders_verified':False,
      'required_gates':['source-controlled R176 transform','review one-asset replacement with Claude',
        'actual WP/Assembler Gutenberg/shortcode acceptance','axe-core and screen reader',
        'NASA media and rights review','production-like LCP/CLS and consent','CI and founder approval'],
    }
    return manifest,doc

def main():
    p=argparse.ArgumentParser();p.add_argument('--r176',type=Path,required=True)
    p.add_argument('--original-js',type=Path,required=True)
    p.add_argument('--replacement-js',type=Path,required=True)
    p.add_argument('--expected-r176-sha256',required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    manifest,doc=build(a.original_js.read_bytes(),a.replacement_js.read_bytes(),a.r176.read_bytes(),expected_r176_sha256=a.expected_r176_sha256)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'R177-UNPUBLISHED-SEARCH-FIXTURE.html').write_bytes(doc)
    (a.out/'R177-STAGING-ASSET-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'state':manifest['release_state'],'candidate_sha256':manifest['r176_candidate_sha256'],'links':len(manifest['preserved_links'])}))
if __name__=='__main__':main()
