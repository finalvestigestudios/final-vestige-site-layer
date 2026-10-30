#!/usr/bin/env python3
"""Audit WordPress navigation links against the current published/draft inventory.

Local JSON only: no network, credentials, database writes, or WordPress API calls.
Proposed patches are printed to a local file; they are never applied to the CMS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

NAV_LINK = re.compile(r'<!--\s*wp:navigation-link\s+(\{[^\n]*?\})\s*/-->')


def canonical(url: str) -> str | None:
    if not url or url.lstrip().startswith(('#', 'mailto:', 'tel:', 'javascript:')):
        return None
    parts = urlsplit(url)
    if parts.scheme and parts.scheme not in ('https', 'http'):
        return None
    if parts.netloc and parts.netloc.lower() not in ('finalvestige.com', 'www.finalvestige.com'):
        return None
    if not parts.netloc and not url.startswith('/'):
        return None
    path = parts.path or '/'
    return path.rstrip('/') or '/'


def find_links(markup: str) -> list[dict]:
    result = []
    for match in NAV_LINK.finditer(markup):
        try:
            attributes = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        result.append({'label': attributes.get('label', ''),
                       'url': attributes.get('url', ''),
                       'path': canonical(attributes.get('url', '')),
                       'block': match.group(0)})
    return result


def analyze(navigation_markup: str, inventory: list[dict]) -> dict:
    route_status = {}
    for item in inventory:
        path = canonical(item.get('link', ''))
        if path:
            route_status[path] = {'status': item.get('status', 'unknown'),
                                  'title': item.get('title', ''),
                                  'id': item.get('id')}
    results = []
    for link in find_links(navigation_markup):
        data = route_status.get(link['path'])
        if data and data['status'] not in ('publish', 'future'):
            results.append({'severity': 'P1', 'reason': 'link-to-unpublished-content',
                            'label': link['label'], 'url': link['url'],
                            'destination_status': data['status'], 'destination_id': data['id']})
    return {'findings': results,
            'navigation_sha256': hashlib.sha256(navigation_markup.encode()).hexdigest(),
            'navigation_link_count': len(find_links(navigation_markup))}


def proposed_remove(navigation_markup: str, target_url: str) -> str:
    target = canonical(target_url)
    matching = [x for x in find_links(navigation_markup) if x['path'] == target]
    if len(matching) != 1:
        raise ValueError(f'Expected exactly one navigation link to {target_url}; found {len(matching)}')
    changed = navigation_markup.replace(matching[0]['block'], '', 1)
    if changed == navigation_markup or any(x['path'] == target for x in find_links(changed)):
        raise ValueError('Refusing incomplete or ambiguous edit')
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='Sanitized local JSON with navigation_markup and inventory')
    parser.add_argument('--propose-remove', help='Internal URL to remove from a locally generated proposal')
    parser.add_argument('--output', type=Path, help='Destination for proposed navigation markup; never writes WordPress')
    args = parser.parse_args(argv)
    if args.propose_remove and not args.output:
        parser.error('--output is required with --propose-remove')
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
    markup = snapshot['navigation_markup']
    inventory = snapshot['inventory']
    report = analyze(markup, inventory)
    if args.propose_remove:
        matches = [x for x in report['findings'] if canonical(x['url']) == canonical(args.propose_remove)]
        if len(matches) != 1:
            parser.error('Target must be exactly one link to an unpublished destination')
        out = proposed_remove(markup, args.propose_remove)
        if args.output.exists():
            parser.error('Refusing to overwrite existing proposal')
        args.output.write_text(out, encoding='utf-8')
        report['proposal_path'] = str(args.output)
    print(json.dumps(report, indent=2))
    return int(bool(report['findings']))


if __name__ == '__main__':
    raise SystemExit(main())
