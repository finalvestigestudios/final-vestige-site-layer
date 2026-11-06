"""R169 Apollo archive proof and visitor-journey integrity gate (offline staging only).

This is an additive verifier around R168's pinned WordPress source transform.
It does NOT download pages, inject analytics, publish content or authorize commerce.
Use with the real, separately witnessed WP editor source; no auto-rebase.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import NamedTuple

from wp_source_custody_gate import stage, WITNESS

SOURCE_IDS = (
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129',
)
OLD_NOTE = 'Moving the slider changes the archival view for exploration only.'
NEW_NOTE = 'These three archival photographs are independent of the chronology slider; each retains its original NASA source record.'


class Anchor(NamedTuple):
    href: str
    label: str
    target: str
    rel: str


class SourceParser(HTMLParser):
    """Parse anchor labels, images and visible text; script/style is not narrative."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self.images = []
        self.visible = []
        self._anchor = None
        self._ignored = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in ('script', 'style'):
            self._ignored += 1
        if tag == 'a':
            if self._anchor is not None:
                raise ValueError('HOLD: nested anchor markup')
            self._anchor = {'href': html.unescape(d.get('href') or ''),
                            'target': d.get('target') or '',
                            'rel': ' '.join(sorted((d.get('rel') or '').split())),
                            'text': []}
        if tag == 'img':
            self.images.append(tuple(d.get(k) or '' for k in ('src', 'srcset', 'alt', 'width', 'height', 'loading', 'decoding')))

    def handle_endtag(self, tag):
        if tag == 'a' and self._anchor is not None:
            a = self._anchor
            self.anchors.append(Anchor(a['href'], ' '.join(''.join(a['text']).split()), a['target'], a['rel']))
            self._anchor = None
        if tag in ('script', 'style') and self._ignored:
            self._ignored -= 1

    def handle_data(self, data):
        if self._anchor is not None:
            self._anchor['text'].append(data)
        if not self._ignored and data.strip():
            self.visible.append(data)


def parse(markup):
    p = SourceParser()
    p.feed(markup)
    p.close()
    if p._anchor is not None:
        raise ValueError('HOLD: unclosed anchor markup')
    return p


def _normalized_visible(parsed):
    return ' '.join(' '.join(parsed.visible).split())


def verify(before: str, after: str) -> dict:
    """Fail closed on any retargeted outgoing link, altered archival image, or narrative.

    Exactly ONE expected archival-gallery explanatory sentence may change.
    New commercial CTAs or unverified affiliate links cannot slip through this gate.
    Existing editorial links, image alt text, and captions stay byte-identical.
    """
    original, staged = parse(before), parse(after)
    if original.anchors != staged.anchors:
        raise ValueError('HOLD: anchor custody drift (href, text, target, rel or ordering)')
    if original.images != staged.images:
        raise ValueError('HOLD: archival image custody drift (src/srcset/alt/size/lazy metadata)')
    for url in SOURCE_IDS:
        count = sum(a.href == url for a in original.anchors)
        if count < 1 or sum(a.href == url for a in staged.anchors) != count:
            raise ValueError('HOLD: original NASA source link unavailable or changed: '+url)
    old, new = _normalized_visible(original), _normalized_visible(staged)
    if old.count(OLD_NOTE) != 1 or new.count(NEW_NOTE) != 1:
        raise ValueError('HOLD: historical-gallery explanatory note drift')
    if old.replace(OLD_NOTE, NEW_NOTE, 1) != new:
        raise ValueError('HOLD: visitor-facing narrative was unexpectedly rewritten')
    if 'const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);' in after:
        raise ValueError('HOLD: fire-second photographic controller remains')
    if after.count('<!-- wp:html -->') != before.count('<!-- wp:html -->') or after.count('<!-- /wp:html -->') != before.count('<!-- /wp:html -->'):
        raise ValueError('HOLD: Gutenberg editor block structure drift')
    if before.count('<script>') != 1 or after.count('<script>') != 2:
        raise ValueError('HOLD: unexpected script count; check CSP/WordPress integration')
    return {
        'gate':'PASS_OFFLINE_ONLY', 'approved_for_publish':False,
        'source_sha256':hashlib.sha256(before.encode('utf-8')).hexdigest(),
        'preview_sha256':hashlib.sha256(after.encode('utf-8')).hexdigest(),
        'unchanged_outgoing_links':len(original.anchors),
        'unchanged_media_elements':len(original.images),
        'nasa_source_records_verified':len(SOURCE_IDS),
        'allowed_explanatory_changes':1,
        'new_affiliate_or_checkout_links':0,
        'wordpress_writes':0,
        'commercial_activation':'HOLD_NO_VERIFIED_APOLLO_OFFER',
        'measurement':'UNVERIFIED_NO_PAID_ORDER_OR_QUALIFIED_SESSION_EVIDENCE',
    }


def offline_preflight(editor_content: str, witness: dict = WITNESS):
    """Run pinned R168 stage first, then independent R169 semantic custody gate."""
    staged, build_receipt = stage(editor_content, witness)
    return staged, {'r168':build_receipt, 'r169':verify(editor_content, staged)}


def main():
    import argparse
    cli = argparse.ArgumentParser(description='Apollo R169 verified offline preview; not a WordPress publisher')
    cli.add_argument('wordpress_editor_export',type=Path)
    cli.add_argument('output_html',type=Path)
    args=cli.parse_args()
    input_text=args.wordpress_editor_export.read_text(encoding='utf-8')
    preview, receipt=offline_preflight(input_text)  # pinned original WP 2017 witness only
    args.output_html.parent.mkdir(parents=True,exist_ok=True)
    args.output_html.write_text(preview,encoding='utf-8')
    args.output_html.with_suffix('.audit.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt['r169'],sort_keys=True))

if __name__=='__main__':
    main()
