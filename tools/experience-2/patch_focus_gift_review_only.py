#!/usr/bin/env python3
"""Fail-closed, review-only replacement of Focus Page 1579's misleading gift-state JS.

This writes a LOCAL candidate, never connects to WordPress or publishes anything.
It is not evidence of a Jetpack-confirmed subscription and needs backend review.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

EXACT_LIVE_SHA256 = 'f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7'
SCRIPT_RE = re.compile(r'(<script id="fvf-gift-v2">)([\s\S]*?)(</script>)')
# The native Jetpack form remains the only subscription authority. A class token
# may reflect a client-side success/pending state, NOT a confirmed email or sale.
REVIEW_SCRIPT = '''(function(){
  var gift=document.getElementById('fvf-gift');
  if(!gift){return;}
  var container=document.querySelector('.wp-block-jetpack-subscriptions__container');
  if(!container){return;}
  function update(){
    var tokens=String(container.className||'').split(/\\s+/);
    if(tokens.indexOf('is-subscriber')!==-1){gift.hidden=false;}
  }
  update();
  if(window.MutationObserver){
    new MutationObserver(update).observe(container,{attributes:true,attributeFilter:['class']});
  }
})();'''

class SourceDrift(ValueError):
    pass


def editor_source(response):
    if not isinstance(response, dict): raise SourceDrift('NO_PAGE_OBJECT')
    d=response.get('structuredContent', response)
    d=d.get('data', d)
    if d.get('id')!=1579 or d.get('status')!='publish':
        raise SourceDrift('NOT_PUBLISHED_FOCUS_PAGE_1579')
    source=d.get('content')
    if isinstance(source,dict): source=source.get('raw')
    if not isinstance(source,str): raise SourceDrift('MISSING_RAW_EDITOR_CONTENT')
    return source


def build(source):
    hits=list(SCRIPT_RE.finditer(source))
    if len(hits)!=1: raise SourceDrift('GIFT_SCRIPT_MISSING_OR_DUPLICATED')
    m=hits[0]
    original=m.group(2)
    oldhash=hashlib.sha256(original.encode()).hexdigest()
    if oldhash!=EXACT_LIVE_SHA256: raise SourceDrift('EXACT_SOURCE_SHA_DRIFT')
    if source.count('<!-- wp:jetpack/subscriptions ')!=1:
        raise SourceDrift('JETPACK_NATIVE_BLOCK_CHANGED')
    if source.count('id="fvf-gift"')!=1 or '52-page' not in source:
        raise SourceDrift('FOCUS_GIFT_OR_EDITION_DRIFT')
    if 'Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf' not in source:
        raise SourceDrift('EXISTING_FIELD_BOOK_DOWNLOAD_CHANGED')
    out=source[:m.start(2)]+REVIEW_SCRIPT+source[m.end(2):]
    assert out[:m.start(2)]==source[:m.start(2)]
    assert out[m.start(2)+len(REVIEW_SCRIPT):]==source[m.end(2):]
    assert out.count('<!-- wp:jetpack/subscriptions ')==1
    assert out.count('id="fvf-gift"')==1
    assert 'URLSearchParams' not in REVIEW_SCRIPT and "get('subscribe')" not in REVIEW_SCRIPT
    return out, {
      'decision':'REVIEW_ONLY_RELEASE_HOLD', 'live_source_script_sha256':oldhash,
      'review_script_sha256':hashlib.sha256(REVIEW_SCRIPT.encode()).hexdigest(),
      'substituted_script_count':1,'other_editor_bytes_identical':True,
      'native_jetpack_block_preserved':True,'fieldbook_download_preserved':True,
      'url_success_signals_accepted':0,'wp_writes':0,
      'must_test_actual_jetpack_states':True,'confirmed_lead_claimed':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('readonly_page1579_json',type=Path)
    p.add_argument('--candidate',required=True,type=Path)
    p.add_argument('--receipt',required=True,type=Path)
    a=p.parse_args()
    raw=editor_source(json.loads(a.readonly_page1579_json.read_text(encoding='utf-8')))
    patched,receipt=build(raw)
    a.candidate.write_text(patched,encoding='utf-8')
    a.receipt.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
