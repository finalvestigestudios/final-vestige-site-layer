#!/usr/bin/env python3
"""Read-only Final Vestige WordPress release preflight against a local JSON snapshot.

This program performs no network requests and never changes the website.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

START = re.compile(r"<!--\s*(/?)wp:([\w/-]+)\b")
HOLDING = re.compile(r"\b(?:will appear here as (?:they are )?released|coming soon|under construction)\b", re.I)


def blocks(markup: str):
    """Yield (closing, name, attributes, self_closing) for Gutenberg comments."""
    for m in START.finditer(markup):
        end = markup.find('-->', m.end())
        if end < 0:
            continue
        payload = markup[m.end():end].strip()
        attrs = {}
        if payload.startswith('{'):
            try:
                attrs, _ = json.JSONDecoder().raw_decode(payload)
            except (json.JSONDecodeError, ValueError):
                pass
        yield bool(m.group(1)), m.group(2), attrs, payload.rstrip().endswith('/')


def normalize_url(value: str):
    parsed = urlsplit(value.strip())
    if parsed.scheme and parsed.netloc and parsed.netloc.lower() not in {'finalvestige.com', 'www.finalvestige.com'}:
        return None
    p = (parsed.path or '/').rstrip('/') or '/'
    return p.lower()


def unpack(v):
    if isinstance(v, dict) and 'data' in v and isinstance(v['data'], dict):
        return v['data']
    return v if isinstance(v, dict) else {}


def inspect(snapshot: dict):
    findings = []
    def report(code, priority, message, evidence):
        findings.append({'code':code, 'priority':priority, 'message':message, 'evidence':evidence})

    nav = unpack(snapshot.get('navigation', {}))
    nav_items = nav.get('content', {})
    markup = (nav_items.get('raw', '') if isinstance(nav_items, dict) else nav_items) or snapshot.get('navigation_markup', '')
    if not isinstance(markup, str) or not markup:
        report('NAV_UNAVAILABLE', 'UNKNOWN', 'Navigation markup missing; cannot test duplication or mobile menu density.', 'Provide navigation.content.raw from WordPress.')
    else:
        subscription_count = 0
        submenu_depth = 0
        root_links = []
        for closing, name, attrs, self_closing in blocks(markup):
            if name == 'navigation-submenu':
                if closing:
                    submenu_depth = max(0, submenu_depth - 1)
                else:
                    if submenu_depth == 0:
                        root_links.append((attrs.get('label', 'submenu'), attrs.get('url', '')))
                    if not self_closing:
                        submenu_depth += 1
            elif not closing and name == 'navigation-link' and submenu_depth == 0:
                root_links.append((attrs.get('label', 'link'), attrs.get('url', '')))
            elif not closing and name == 'jetpack/subscriptions':
                subscription_count += 1
        if subscription_count > 1:
            report('DUPLICATE_SUBSCRIBE', 'P1', 'Navigation contains multiple subscription blocks.', f'{subscription_count} wp:jetpack/subscriptions blocks')
        if len(root_links) > 8:
            report('DENSE_NAVIGATION', 'P2', 'Primary navigation may overwhelm desktop and mobile visitors; verify with screenshots.', f'{len(root_links)} top-level navigation items')
        destinations = {}
        for label, url in root_links:
            target = normalize_url(url)
            if target:
                destinations.setdefault(target, []).append(label)
        for target, labels in destinations.items():
            if len(labels) > 1:
                report('DUPLICATE_ROOT_LINK', 'P2', 'Multiple top-level links lead to the same destination.', f'{target}: {", ".join(labels)}')

    settings = unpack(snapshot.get('settings', {}))
    identity = settings.get('identity', {})
    if identity and not identity.get('site_icon'):
        report('MISSING_SITE_ICON', 'P2', 'WordPress identity has no site icon assigned; verify favicon in rendered site.', 'identity.site_icon = 0')
    if identity and not identity.get('site_logo'):
        report('MISSING_SITE_LOGO_SETTING', 'INFO', 'WordPress identity has no logo assigned; theme may nevertheless display a custom brand mark.', 'identity.site_logo = 0')

    monitor = unpack(snapshot.get('monitor', {}))
    if monitor and monitor.get('monitor_active') is False:
        report('MONITOR_DISABLED', 'P2', 'WordPress uptime monitoring is disabled.', 'monitor.monitor_active = false')

    backup = unpack(snapshot.get('backup', {}))
    if backup.get('backups', {}).get('last_attempt_failed') is True:
        report('BACKUP_FAILED', 'P0', 'Most recent backup attempt failed; verify recovery before release.', str(backup.get('backups', {}).get('last_attempt_status', 'failed')))

    scan = unpack(snapshot.get('scan', {}))
    threats = scan.get('threats', [])
    if isinstance(threats, list) and threats:
        report('ACTIVE_THREATS', 'P0', 'WordPress security scan reports active threats.', f'{len(threats)} active threat(s)')

    homepage = snapshot.get('homepage_html', '')
    landing_pages = snapshot.get('landing_pages', {})
    if homepage and isinstance(landing_pages, dict):
        for url, body in landing_pages.items():
            dest = normalize_url(url)
            if dest and re.search(r'href\s*=\s*[\"\']'+re.escape(dest)+r'/?[\"\']',homepage,re.I) and HOLDING.search(body or ''):
                report('FEATURED_HOLDING_PAGE', 'P1', 'Homepage prominently links to a destination advertising future rather than available content.', f'{dest} contains a release-placeholder phrase')

    rank = {'P0':0,'P1':1,'P2':2,'INFO':3,'UNKNOWN':4}
    return sorted(findings, key=lambda x:(rank.get(x['priority'],5),x['code']))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='Local, sanitized JSON snapshot (no credentials or visitor data)')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero on P0 or P1')
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
        if not isinstance(snapshot, dict): raise ValueError('Top-level JSON must be an object')
    except (ValueError,OSError) as exc:
        parser.error(str(exc))
    findings = inspect(snapshot)
    print(json.dumps({'findings':findings,'counts':{severity:sum(f['priority']==severity for f in findings) for severity in ['P0','P1','P2','INFO','UNKNOWN']}}, indent=2))
    return int(args.strict and any(f['priority'] in {'P0','P1'} for f in findings))


if __name__=='__main__':
    sys.exit(main())
