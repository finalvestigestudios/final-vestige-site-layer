#!/usr/bin/env python3
"""Fail-closed read-only delta gate; NEVER a WordPress or production release pass."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile

EXPECTED_ZIP = '8db20aac81deba544d057abfe28fe3baaf71639f74f421a210676fbb0b36e56b'
PHP_PATH = 'mu-plugins/fv-ex2-playground-review.php'
CHAPTERS = ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
            'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def media_name(url):
    p = urlparse(html.unescape(url))
    if p.scheme != 'https' or p.hostname not in ('i0.wp.com','finalvestige.com'):
        raise ValueError('Untrusted archival image host')
    if '/wp-content/uploads/' not in p.path:
        raise ValueError('Not a WordPress media source')
    return p.path.rsplit('/',1)[-1]

def candidate(zip_path):
    if sha(Path(zip_path).read_bytes()) != EXPECTED_ZIP:
        raise ValueError('Candidate ZIP SHA mismatch; refuse changed source')
    with ZipFile(zip_path) as z:
        raw = z.read(PHP_PATH)
        custody = json.loads(z.read('SOURCE_CUSTODY.json'))
        if custody.get('files_sha256',{}).get(PHP_PATH) != sha(raw):
            raise ValueError('Candidate PHP does not match custody')
        if custody.get('native_wordpress_tested') is not False:
            raise ValueError('Unexpected WordPress qualification claim')
    match = re.search(r"<<<'FVPG_HTML_END'\n(.*?)\nFVPG_HTML_END", raw.decode(), re.S)
    if not match:
        raise ValueError('Cannot extract exact private PHP-rendered homepage')
    content = match.group(1)
    images = []
    for tag in re.findall(r'<img\b[^>]*>',content):
        x = re.search(r'\bsrc="([^"]+)"',tag)
        if x: images.append(media_name(x.group(1)))
    return dict(sha256=sha(content.encode()),images=images,
                chapters=[c for c in CHAPTERS if 'id="'+c+'"' in content],
                margins=len(re.findall(r'class="fv-margin-strip__item"',content)),
                focus=len(re.findall(r'href="https://finalvestige.com/focus/"',content)),
                folio='fv-hf__folio-note' in content)

def audit(live, preview):
    required = ('kind','source','wp_page_id','wp_status','wp_modified','wp_slug',
                'wp_content_utf8_sha256','chapter_ids','margins_count',
                'focus_link_count','archive_images','hero_folio_present','flagship_present')
    if any(k not in live for k in required): raise ValueError('Incomplete live source inventory')
    if (live['kind'],live['source'],live['wp_page_id'],live['wp_status'],live['wp_slug']) != (
       'FV_READ_ONLY_WORDPRESS_PAGE_6_INVENTORY_V1','WORDPRESS_PAGES_GET_READ_ONLY',6,'publish','home'):
        raise ValueError('Source is not published WordPress page 6')
    if not re.fullmatch(r'[a-f0-9]{64}',live['wp_content_utf8_sha256']):
        raise ValueError('Invalid live content fingerprint')
    if live['chapter_ids'] != CHAPTERS: raise ValueError('Unexpected live chapter inventory')
    published_images = [media_name(x) for x in live['archive_images']]
    risks = []
    if live['margins_count'] != 72 or preview['margins'] != 72: risks.append('MARGINS_DRIFT')
    if preview['chapters'] != CHAPTERS: risks.append('CHAPTER_DRIFT')
    if live['focus_link_count'] != preview['focus']: risks.append('FOCUS_CTA_COUNT_DIFFERENCE')
    if not (live['hero_folio_present'] and preview['folio']): risks.append('HERO_FOLIO_DRIFT')
    missing = sorted(set(published_images)-set(preview['images']))
    if missing: risks.append('LIVE_ARCHIVAL_MEDIA_NOT_IN_PREVIEW')
    if any('nypl-5003296' in x for x in published_images): risks.append('PUBLIC_NYPL_RIGHTS_REVIEW')
    return {'decision':'HOLD','never_publish_automatically':True,
        'published_wordpress_page6_already_seven_chapter':bool(live['flagship_present']),
        'published_modified':live['wp_modified'],
        'published_source_sha256':live['wp_content_utf8_sha256'],
        'candidate_zip_sha256':EXPECTED_ZIP,'candidate_html_sha256':preview['sha256'],
        'published':{'chapters':len(live['chapter_ids']),'margins':live['margins_count'],
                     'focus_links':live['focus_link_count'],'archive_images':published_images},
        'candidate':{'chapters':len(preview['chapters']),'margins':preview['margins'],
                     'focus_links':preview['focus'],'archive_images':preview['images']},
        'missing_from_preview':missing,'source_delta_risks':risks,
        'remaining_release_gates':['true isolated WordPress/Assembler render',
          'real archive image transfers and rights','independent WCAG 2.2 AA',
          'measured Lighthouse/CWV','real Jetpack and merchant confirmation',
          'founder approval','exact-head independent QD and CI'],
        'limits':'Read-only metadata comparison, not rendering/rights/sales or staging approval.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--live',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    x=p.parse_args()
    try:
        r=audit(json.loads(x.live.read_text()), candidate(x.candidate))
    except (OSError,ValueError,KeyError,TypeError) as e:
        r={'decision':'HOLD','admission':'FAIL_CLOSED','error':str(e)}
    x.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(r['decision'],r.get('admission','SOURCE_DELTA_RECORDED'))
    return int(r.get('admission')=='FAIL_CLOSED')

if __name__=='__main__': raise SystemExit(main())
