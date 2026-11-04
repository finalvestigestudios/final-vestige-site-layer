#!/usr/bin/env python3
"""R105 deterministic fail-closed Apollo source custody and route audit.

Offline sealed R103 package only. No NASA photo licensing inferred.
No network, media, WordPress, deployment, or production changes.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit

VIEWS = (
    'R85_NASA_SOURCE_REVIEW.html', 'R87_PHOTOGRAPH_DATE_RAIL.html',
    'R88_READING_ROOM.html', 'R89_REVIEW_HUB.html',
    'R93_SOURCE_PASSPORTS.html', 'R94_CURATED_ATLAS.html',
    'R97_SOURCE_GALLERY.html',
)
NASA = (
    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
    'https://www.nasa.gov/image-detail/amf-s67-21294/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)
RECEIPT = 'R103_MOBILE_GALLERY_RECEIPT.json'


def ensure(condition, code):
    if not condition:
        raise ValueError(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.hrefs = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            ensure(a['id'] not in self.ids, 'R105_DUPLICATE_HTML_ID:' + a['id'])
            self.ids.add(a['id'])
        if tag in ('img', 'picture', 'video', 'iframe', 'source', 'canvas'):
            self.errors.append('R105_UNCLEARED_MEDIA:' + tag)
        if any(k in a for k in ('data-lat', 'data-lon', 'data-geo-edge',
                                'data-longitude', 'data-latitude')):
            self.errors.append('R105_UNREVIEWED_GEOGRAPHY')
        if tag == 'script' and a.get('src', '').startswith(('http:', 'https:', '//')):
            self.errors.append('R105_EXTERNAL_SCRIPT')
        if tag == 'a' and 'href' in a:
            self.hrefs.append(a['href'])


def audit(stage):
    stage = Path(stage)
    ensure(stage.is_dir() and not stage.is_symlink(), 'R105_STAGE_DIRECTORY')
    raw_receipt = stage / RECEIPT
    ensure(raw_receipt.is_file() and not raw_receipt.is_symlink(), 'R105_MISSING_RECEIPT')
    receipt = json.loads(raw_receipt.read_text(encoding='utf-8'))
    for key, value in (
        ('schema', 'fv.apollo.r103.mobile-gallery.v1'),
        ('release', 'STAGING_HOLD'), ('publication_approved', False),
        ('records', 6), ('nasa_photo_rights_cleared', 0),
        ('images_embedded', 0), ('geo_pins', 0), ('inferred_edges', 0),
    ):
        ensure(type(receipt.get(key)) is type(value) and receipt.get(key) == value,
               'R105_RELEASE_BOUNDARY:' + key)
    files = receipt.get('files')
    ensure(isinstance(files, dict) and len(files) >= 20, 'R105_MANIFEST_INVALID')
    expected = set(files) | {RECEIPT, 'R99_PRIVATE_PREVIEW_RECEIPT.json'}
    actual = {p.relative_to(stage).as_posix() for p in stage.rglob('*')
              if p.is_file() or p.is_symlink()}
    ensure(actual == expected, 'R105_FILE_INVENTORY')
    for filename, checksum in files.items():
        ensure(isinstance(filename, str) and re.fullmatch(r'[A-Za-z0-9_./-]+', filename)
               and '..' not in Path(filename).parts and not filename.startswith('/'),
               'R105_UNSAFE_MANIFEST_PATH')
        p = stage / filename
        ensure(p.is_file() and not p.is_symlink(), 'R105_BAD_FILE:' + filename)
        ensure(re.fullmatch(r'[0-9a-f]{64}', checksum or '') and sha(p.read_bytes()) == checksum,
               'R105_HASH_MISMATCH:' + filename)
    ensure(all(not p.is_symlink() for p in stage.rglob('*')), 'R105_SYMLINK')
    old = stage / 'R99_PRIVATE_PREVIEW_RECEIPT.json'
    ensure(sha(old.read_bytes()) == receipt.get('historical_r99_input_receipt_sha256'),
           'R105_HISTORICAL_RECEIPT_MISMATCH')
    docs = {}
    for view in VIEWS:
        path = stage / 'review' / view
        ensure(path.is_file(), 'R105_MISSING_VIEW:' + view)
        doc = Document()
        html = path.read_text(encoding='utf-8')
        doc.feed(html)
        doc.close()
        ensure(not doc.errors, 'R105_VIEW_INTEGRITY:' + view + ':' + ','.join(doc.errors))
        nasa_urls = sorted(set(href for href in doc.hrefs
                               if href.startswith('https://www.nasa.gov/image-detail/')))
        ensure(set(nasa_urls) == set(NASA), 'R105_SOURCE_SET_DRIFT:' + view)
        ensure('STAGING HOLD' in html and 'INDIVIDUAL REVIEW REQUIRED' in html,
               'R105_RIGHTS_CONTEXT_MISSING:' + view)
        docs[view] = doc
    crosslinks = 0
    fragment_links = 0
    for source, doc in docs.items():
        for href in doc.hrefs:
            target = urlsplit(href)
            if target.scheme or target.netloc or target.path:
                continue
            query = parse_qs(target.query, keep_blank_values=True)
            if 'fv_apollo_r99' in query:
                ensure(len(query) == 1 and len(query['fv_apollo_r99']) == 1,
                       'R105_AMBIGUOUS_PRIVATE_ROUTE:' + source)
                dest = query['fv_apollo_r99'][0]
                if dest.endswith('.html'):
                    ensure(dest in docs, 'R105_UNKNOWN_VIEW:' + source + ':' + dest)
                    crosslinks += 1
                else:
                    continue
            elif target.query:
                continue
            else:
                dest = source
            if target.fragment:
                anchor = unquote(target.fragment)
                ensure(anchor in docs[dest].ids,
                       'R105_BROKEN_FRAGMENT:' + source + ':' + dest + '#' + anchor)
                fragment_links += 1
    gallery = (stage / 'review/R97_SOURCE_GALLERY.html').read_text(encoding='utf-8')
    ensure(gallery.count('INDIVIDUAL RIGHTS REVIEW PENDING') == 6
           and gallery.count('data-jump-compare') == 6
           and 'S67-19766 · provisional association' in gallery,
           'R105_GALLERY_RIGHTS_OR_PROVISIONAL_CLAIM_CHANGED')
    ensure(crosslinks >= 100 and fragment_links >= 50,
           'R105_SOURCE_ROUTES_UNEXPECTEDLY_MISSING')
    return {
        'schema': 'fv.apollo.r105.crossview-custody.v1',
        'release': 'STAGING_HOLD',
        'cms_or_production_tested': False,
        'nasa_links_checked_offline_only': True,
        'nasa_photographic_use_clearances': 0,
        'geographic_pins': 0,
        'source_count': 6,
        'view_count': len(VIEWS),
        'crossview_links_checked': crosslinks,
        'fragment_links_checked': fragment_links,
        'r103_receipt_sha256': sha(raw_receipt.read_bytes()),
        'source_manifest': {v: files['review/' + v] for v in VIEWS},
        'nasa_source_urls': list(NASA),
        'notes': ['No HTTP availability or NASA image reuse permission inferred.',
                  'Source navigation indicates alternate views, never causal edges.'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.stage)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in
                      ('schema', 'source_count', 'view_count',
                       'crossview_links_checked', 'fragment_links_checked', 'release')},
                     sort_keys=True))
