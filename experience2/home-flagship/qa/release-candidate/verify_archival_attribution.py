#!/usr/bin/env python3
"""Source-link and image identity gate for FV Experience 2.0's three archive cards.

No network, CMS writes, rights grants, or image-byte validation. A PASS means that
reviewed source references and first-party media identifiers are still in the
candidate HTML; it is NOT an image license, transfer test, or publication gate.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path('experience2/home-flagship')
EXPECTED = {
    'apollo': {
        'filename': 's67-19766.webp',
        'sources': ('https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
                    'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'),
    },
    'franklin': {
        'filename': 'Franklinexpeditionnote.jpg',
        'sources': ('https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg',
                    'https://www.rmg.co.uk/collections/objects/rmgc-object-504898'),
    },
    'malbone': {
        'filename': 'edit-017-v02-nypl-5003296-original.jpg',
        'sources': ('https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0',),
    },
}


class ArchiveParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cases: dict[str, list[dict]] = {}
        self.active: dict | None = None
        self.article_depth = 0
        self.orphan_images = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and self.active is not None:
            self.article_depth += 1
        elif tag == 'article' and 'data-fv-case' in attrs:
            name = attrs['data-fv-case']
            self.active = {'images': [], 'links': [], 'text': []}
            self.cases.setdefault(name, []).append(self.active)
            self.article_depth = 1
        if tag == 'img' and 'data-fv-archive-img' in attrs:
            if self.active is None:
                self.orphan_images += 1
            else:
                self.active['images'].append(attrs)
        if tag == 'a' and self.active is not None:
            self.active['links'].append(attrs.get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'article' and self.active is not None:
            self.article_depth -= 1
            if self.article_depth == 0:
                self.active = None

    def handle_data(self, data):
        if self.active is not None:
            self.active['text'].append(data)


def allowed_image_url(url: str, filename: str) -> bool:
    p = urlsplit(url)
    if p.scheme != 'https' or p.username or p.password or p.fragment:
        return False
    original_path = f'/wp-content/uploads/2026/08/{filename}'
    if p.hostname == 'finalvestige.com':
        return p.path == original_path and not p.query
    if p.hostname == 'i0.wp.com':
        return p.path == '/finalvestige.com' + original_path and ('ssl=1' in p.query)
    return False


def audit(html: str) -> dict:
    parser = ArchiveParser()
    parser.feed(html)
    failures = []
    if parser.orphan_images:
        failures.append(f'{parser.orphan_images} archive img(s) outside recognized case')
    if set(parser.cases) != set(EXPECTED):
        failures.append(f'case set differs: {sorted(parser.cases)}')
    results = {}
    for name, spec in EXPECTED.items():
        entries = parser.cases.get(name, [])
        if len(entries) != 1:
            failures.append(f'{name}: required exactly one source case, got {len(entries)}')
            continue
        case = entries[0]
        if len(case['images']) != 1:
            failures.append(f'{name}: required one archival image, got {len(case["images"])}')
            continue
        img = case['images'][0]
        alt = img.get('alt', '').strip()
        if len(alt) < 50 or alt.lower() in ('image', 'photo', 'map'):
            failures.append(f'{name}: meaningful descriptive alt is missing')
        if img.get('loading') != 'lazy' or img.get('decoding') != 'async':
            failures.append(f'{name}: lazy/decode media contract changed')
        try:
            if int(img.get('width', 0)) <= 0 or int(img.get('height', 0)) <= 0:
                raise ValueError()
        except ValueError:
            failures.append(f'{name}: intrinsic media dimensions missing')
        if not allowed_image_url(img.get('src', ''), spec['filename']):
            failures.append(f'{name}: original media identity/host/path changed')
        candidates = [x.strip() for x in img.get('srcset', '').split(',') if x.strip()]
        if not candidates:
            failures.append(f'{name}: responsive srcset is absent')
        widths = []
        for candidate in candidates:
            m = re.fullmatch(r'(\S+)\s+(\d+)w', candidate)
            if not m or not allowed_image_url(m.group(1), spec['filename']):
                failures.append(f'{name}: disallowed responsive variant: {candidate[:85]}')
                continue
            widths.append(int(m.group(2)))
        if widths != sorted(set(widths)) or any(n < 100 or n > 2400 for n in widths):
            failures.append(f'{name}: invalid or duplicate responsive widths')
        if not img.get('sizes'):
            failures.append(f'{name}: responsive sizes is absent')
        for link in spec['sources']:
            if link not in case['links'] and not (name == 'franklin' and 'rmg.co.uk' in link and link in html):
                failures.append(f'{name}: expected source link missing: {link}')
        body = ' '.join(case['text'])
        if not re.search(r'\b(?:limit|evidence boundary)\b', body, re.I):
            failures.append(f'{name}: evidence limit not disclosed')
        results[name] = {
            'media': spec['filename'],
            'source_reference_count': len(spec['sources']),
            'responsive_variants': len(candidates),
            'rights_admission': 'NOT_CERTIFIED',
            'image_network_delivery': 'NOT_TESTED',
        }
    return {'status':'PASS_SOURCE_LINKS_ONLY' if not failures else 'FAIL',
            'case_count':len(parser.cases), 'cases':results, 'failures':failures,
            'release':'HOLD', 'binary_provenance_verified':False,
            'rights_cleared':False, 'word_press_stage_verified':False}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--index',type=Path,default=ROOT/'index.html')
    ap.add_argument('--receipt',type=Path)
    args=ap.parse_args()
    raw=args.index.read_bytes()
    result=audit(raw.decode('utf-8'))
    result['index_sha256']=hashlib.sha256(raw).hexdigest()
    if args.receipt:
        args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result['status']=='PASS_SOURCE_LINKS_ONLY' else 2

if __name__ == '__main__':
    raise SystemExit(main())
