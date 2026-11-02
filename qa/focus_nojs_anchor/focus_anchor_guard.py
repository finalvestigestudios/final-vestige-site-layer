#!/usr/bin/env python3
"""Read-only saved-Gutenberg fragment-target census. Never asserts live DOM failure."""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote


class StaticHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.fragment_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        node_id = attrs_dict.get('id')
        if node_id:
            self.ids.add(node_id)
        href = attrs_dict.get('href')
        if tag == 'a' and href and href.startswith('#') and len(href) > 1:
            self.fragment_links.append(unquote(href[1:]))


def audit(saved_gutenberg: str) -> dict:
    if not isinstance(saved_gutenberg, str) or not saved_gutenberg.strip():
        raise ValueError('nonempty WordPress saved Gutenberg source required')
    parser = StaticHTML()
    parser.feed(saved_gutenberg)
    counts = Counter(parser.fragment_links)
    missing = {key: count for key, count in sorted(counts.items()) if key not in parser.ids}
    return {
        'evidence_level': 'SAVED_SOURCE_ONLY_NOT_RENDERED_HTML',
        'native_jetpack_block_count': saved_gutenberg.count('<!-- wp:jetpack/subscriptions'),
        'fragment_links': sum(counts.values()),
        'unique_fragment_targets': len(counts),
        'missing_static_targets': missing,
        'requires_anonymous_no_js_browser_verification': bool(missing),
        'production_defect_confirmed': False,
        'safe_recommendation': (
            'Verify the actual logged-out, JavaScript-disabled DOM. If targets are absent, '
            'coordinate with the WordPress editor to add one static anchor immediately '
            'before the native Jetpack block; keep its form and signup list unchanged.'
            if missing else 'Static source fragment targets were found; browser behavior remains unverified.'
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path, help='private local UTF-8 export of one page content.raw')
    args = ap.parse_args()
    # Deliberately no network calls, no site writes, and no raw page content printed.
    print(json.dumps(audit(args.source.read_text(encoding='utf-8')), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
