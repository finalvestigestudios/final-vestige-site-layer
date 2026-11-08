#!/usr/bin/env python3
"""Apollo R225: reconcile the R224 SOURCE LINK CUSTODY ledger with rendered HTML.

Staging-only, deterministic, stdlib-only builder; no external requests or WP writes.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil

EXPECTED_R224 = 'f739b70ced7c93254f69b9d58e1463a97d4288780202622b74d2be50431a57ea'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
REPORT_DATE = 'https://www.nasa.gov/apollo-1-resources/'
EXPECTED_DATES = ['1966-10-18', '1967-01-03', '1967-01-27', '1967-01-28', '1967-04']


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


class AtlasHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.bindings = []
        self.dates = []
        self.stack = []
        self.ids = []
        self.forbidden = []

    def handle_starttag(self, tag, raw):
        attrs = dict(raw)
        parent = self.stack[-1][1] if self.stack else False
        in_rail = parent or (tag == 'ol' and 'rail' in attrs.get('class', '').split())
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            href = attrs.get('href', '')
            if href.startswith(('https://', 'http://')):
                self.links.append(href)
            if 'data-source-id' in attrs:
                self.bindings.append({'source_id': attrs['data-source-id'], 'url': href})
        if tag == 'time' and in_rail:
            self.dates.append(attrs.get('datetime'))
        if tag in ('script', 'iframe', 'form', 'object', 'embed'):
            self.forbidden.append(tag)
        if any(k.startswith('on') or k in ('srcdoc', 'data-lat', 'data-lon') for k in attrs):
            self.forbidden.append('unsafe-attribute')
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, in_rail))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def reconcile(parent):
    man = json.loads((parent / 'manifest.json').read_text())
    if digest(parent / 'manifest.json') != EXPECTED_R224:
        raise ValueError('Unpinned R224 manifest: exact-head source is required')
    for path, expected in man['files'].items():
        if digest(parent / path) != expected:
            raise ValueError('R224 source artifact drift: ' + path)
    p = AtlasHTML()
    p.feed((parent / 'templates/atlas-fragment.html').read_text(encoding='utf-8'))
    prior = json.loads((parent / 'source-url-crosswalk.json').read_text())
    records = json.loads((parent / 'source-records.json').read_text())
    photo_urls = {r['source_id']: r['source_url'] for r in records if r['source_id'] != 'Apollo 204 Review Board'}
    approved = set(photo_urls.values()) | {BOARD, REPORT_DATE}
    if p.forbidden or len(set(p.ids)) != len(p.ids):
        raise ValueError('Active markup, speculative geography or duplicate IDs')
    if p.dates != EXPECTED_DATES:
        raise ValueError('Chronology dates or precision drift')
    if not p.links or set(p.links) != set(prior['external_urls']):
        raise ValueError('External destination set changed from reviewed R224 sources')
    if sum(url == FREE for url in p.links) != 1:
        raise ValueError('Original free investigation destination must appear exactly once')
    if len(p.bindings) != 6:
        raise ValueError('All six source-labelled anchors must be inventoried')
    for b in p.bindings:
        sid, url = b['source_id'], b['url']
        if sid == 'Apollo 204 Review Board':
            if url not in (BOARD, REPORT_DATE):
                raise ValueError('Review Board source URL substitution')
        elif photo_urls.get(sid) != url or url not in approved:
            raise ValueError('Photo source ID / NASA URL mismatch: ' + sid)
    if not any(b == {'source_id': 'Apollo 204 Review Board', 'url': REPORT_DATE} for b in p.bindings):
        raise ValueError('April 1967 report receipt missing')
    if prior['chronology_dates'] != EXPECTED_DATES[:-1]:
        raise ValueError('Unexpected prior date ledger: verify ancestry, do not silently repair')
    if prior['external_anchor_count'] != 50 or len(p.links) != 56:
        raise ValueError('Unexpected external-anchor delta; manual source review required')
    corrected = dict(prior)
    corrected['external_anchor_count'] = len(p.links)
    corrected['chronology_dates'] = p.dates
    corrected['source_bindings'] = p.bindings
    corrected['verification_method'] = 'exact-r224-rendered-anchor-and-chronology-census'
    corrected['report_month_precision'] = 'month-only: 1967-04'
    corrected['source_ancestry_status'] = 'R198_NOT_RECONCILED'
    return corrected, {'external_links': len(p.links), 'unique_external_urls': len(set(p.links)),
                       'source_bindings': len(p.bindings), 'chronology_dates': p.dates}


def build(parent, out):
    corrected, counts = reconcile(parent)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(parent, out)
    crosswalk_path = out / 'source-url-crosswalk.json'
    crosswalk_path.write_bytes(canonical(corrected))
    new_sha = digest(crosswalk_path)
    php_path = out / 'fv-ex2-apollo-r224.php'
    old_sha = digest(parent / 'source-url-crosswalk.json')
    src = php_path.read_text(encoding='utf-8')
    if src.count(old_sha) != 1:
        raise ValueError('PHP custody binding unavailable; fail closed')
    php_path.write_text(src.replace(old_sha, new_sha), encoding='utf-8')
    man = json.loads((out / 'manifest.json').read_text())
    man['release'] = 'R225'
    man['parent_manifest_sha256'] = EXPECTED_R224
    man['r225_crosswalk_reconciled'] = True
    for path in ('source-url-crosswalk.json', 'fv-ex2-apollo-r224.php'):
        man['files'][path] = digest(out / path)
    (out / 'manifest.json').write_bytes(canonical(man))
    report = {'result': 'BUILT_STAGING_NOT_LIVE', 'r224_parent_sha256': EXPECTED_R224,
              'r225_manifest_sha256': digest(out / 'manifest.json'),
              'crosswalk_sha256': new_sha, 'reconciled_counts': counts,
              'commercial_offers_enabled': False, 'creator_ids_verified': False,
              'installed_wordpress': 'NOT_TESTED', 'genuine_axe': 'NOT_EXECUTED'}
    (out / 'r225-reconciliation-receipt.json').write_bytes(canonical(report))
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(build(args.parent, args.out), sort_keys=True, indent=2))
