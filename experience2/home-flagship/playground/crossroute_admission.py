#!/usr/bin/env python3
"""EX2 read-only cross-route release contract: homepage Focus CTA + truthful gift.

Only local SHA-pinned artifacts. No network, WordPress writes, sales or lead claims.
The public Page 1579 still contains the unguarded original; thus release HOLD.
"""
import argparse, hashlib, json, re
from pathlib import Path
from zipfile import ZipFile

ZIP_SHA='8db20aac81deba544d057abfe28fe3baaf71639f74f421a210676fbb0b36e56b'
GUARD_BLOB='1847178a1dd7e3c97d2a8278af6933910982e96e'
LIVE_SCRIPT_SHA='f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7'
HERO='<a class="fv-hf__text-link fv-hf__text-link--focus" href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook <span aria-hidden="true">↗</span></a>'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def admit(bundle,guard,fixture):
    if sha(bundle)!=ZIP_SHA:raise ValueError('HOLD: EX2 protected package changed')
    with ZipFile(__import__('io').BytesIO(bundle)) as z:
        php=z.read('mu-plugins/fv-ex2-playground-review.php')
        custody=json.loads(z.read('SOURCE_CUSTODY.json'))['files_sha256']
        if sha(php)!=custody['mu-plugins/fv-ex2-playground-review.php']:
            raise ValueError('HOLD: source custody mismatch')
    code=php.decode()
    m=re.search(r"<<<'FVPG_HTML_END'\n(.*?)\nFVPG_HTML_END",code,re.S)
    if not m or m.group(1).count(HERO)!=1:
        raise ValueError('HOLD: homepage Focus hero missing or duplicated')
    html=m.group(1)
    if html.count('class="fv-margin-strip__item"')!=72:
        raise ValueError('HOLD: 72 Margins not preserved')
    if len(re.findall(r'href="#fv-hf-(?:title|chronicle|evidence|inquiry|method-title|observer|mind-title)"',html))<7:
        raise ValueError('HOLD: seven chapters not preserved')
    if blob(guard)!=GUARD_BLOB:raise ValueError('HOLD: review-only PR1451 guard drift')
    active=re.sub(rb'/\*.*?\*/|//[^\n]*',b'',guard,flags=re.S)
    if b'URLSearchParams' in active or b'location.search' in active:
        raise ValueError('HOLD: untrusted query drives subscriber UI')
    f=json.loads(fixture)
    if f.get('page_id')!=1579 or sha(f['script'].encode())!=LIVE_SCRIPT_SHA:
        raise ValueError('HOLD: WordPress Focus original script drift')
    if 'new URLSearchParams(window.location.search)' not in f['script']:
        raise ValueError('HOLD: original gift bug not reproduced from actual source')
    return {'offline_contract':'PASS','published_page6':'UNCHANGED','focus_live_page1579':'UNPATCHED',
            'cross_route_release':'HOLD','guard_candidate_source':'PR1451_NOT_LIVE',
            'real_subscribers':'UNKNOWN','real_paid_orders':'UNKNOWN',
            'next_gate':'Authorize and independently verify actual Jetpack browser behavior, then approve a coordinated, rollback-ready release.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--guard-js',type=Path,required=True);ap.add_argument('--focus-fixture',type=Path,required=True)
    a=ap.parse_args();print(json.dumps(admit(a.candidate.read_bytes(),a.guard_js.read_bytes(),a.focus_fixture.read_bytes()),indent=2))
