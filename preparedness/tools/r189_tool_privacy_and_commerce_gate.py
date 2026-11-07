#!/usr/bin/env python3
"""R189 independent, read-only hold for ALL six Preparedness interactive tools.

Scans authored HTML, transitively inlined JavaScript, and the generated
WordPress DRAFT artifacts. Complements (does not replace) R185 source custody.
Passing structural checks NEVER imply browser, privacy, safety, QD, merchant,
or publication clearance. Do not call this against untrusted runnable code.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit, parse_qsl

SCHEMA = 'fv-preparedness-r189-six-tool-privacy-commerce-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
# Authenticated original producer JS Git blob SHA1 at R188 exact commit
# 595edb5099a92aa276cee39d7802af369effff3d (Nov 7, 2026).
JS_PINS = {
 'shelter_common.js': 'efe1c7910d99437e3687621dabab8ce55dc24fd4',
 'fire_worksheet.js': '7bfd283205c68ec1cbd9666cb63051c332ba23ac',
 'kit_planner.js': '3bf8ea8e64a7b8e70815f1c6d8ee8df15bf7822f',
 'kit_planner_ui.js': 'd2ff08d8ba5585fe69b557a73db55de42aac9d92',
 'plan_builder.js': '311aa78ec1abca6f7c1113f2620a459dad92748d',
 'plan_builder_ui.js': '2cc9a1196a6b433d861d91dafa6c5a85161990fb',
 'reunion_card.js': 'b1a09b1eda1ae26f081de65b400a37bc19538035',
 'outage_items.js': '3bd519402202c40a49e9e1bde9fc9ba0f54d3fff',
 'water_planner.js': '9cd2944e7b5c5061ae041669c327069d488c2062',
}
TOOLS = {
 'family-reunification-card': ('shelter_common.js', 'reunion_card.js'),
 'home-fire-escape-worksheet': ('shelter_common.js', 'fire_worksheet.js'),
 'kit-builder': ('kit_planner.js', 'kit_planner_ui.js'),
 'power-outage-planner': ('shelter_common.js', 'outage_items.js'),
 'reunification-plan': ('plan_builder.js', 'plan_builder_ui.js'),
 'water-planner': ('water_planner.js',),
}
TOKEN = re.compile(r'\{\{inline-js:([a-z_]+\.js)\}\}')
# Static denylist, including common computed-property bypasses. Does NOT
# prove absence of runtime exfiltration or unsafe control flow.
PRIVACY_SINKS = {
 'network_api': re.compile(r'\b(?:fetch\s*\(|XMLHttpRequest\b|sendBeacon\s*\(|WebSocket\s*\(|EventSource\s*\(|importScripts\s*\(|RTCPeerConnection\s*\(|\bpostMessage\s*\()|(?:\[\s*[\'\"](?:fetch|sendBeacon|postMessage)[\'\"]\s*\]\s*\()', re.I),
 'persistent_storage': re.compile(r'\b(?:localStorage|sessionStorage|indexedDB|cookieStore|document\s*(?:\.\s*cookie|\[\s*[\'\"]cookie[\'\"]\s*\]))\b', re.I),
 'navigation_or_remote_loader': re.compile(r'(?:\b(?:window\.)?(?:location\s*\.\s*(?:href|assign|replace)|open)\s*\(|\b(?:window\.)?location\s*\.\s*href\s*=|\bnew\s+Image\s*\(|\b(?:document\.write|import\s*\(|eval\s*\(|new\s+Function\s*\(|serviceWorker\s*\.\s*register\s*\())', re.I),
 'dynamic_remote_reference': re.compile(r'(?:\.\s*(?:src|action)\s*=\s*[\'\"]https?://|\.\s*setAttribute\s*\(\s*[\'\"](?:src|action)[\'\"]\s*,\s*[\'\"]https?://)', re.I),
}
# A store listing is not a rights/fulfillment/merchant-approval receipt.
BLOCKED_HOSTS = ('payhip.com', 'awin1.com', 'gumroad.com',
                 'checkout.stripe.com', 'clickbank.net', 'digistore24.com',
                 'shopify.com', 'paypal.com')
BANNED_QS = frozenset(('aff_id', 'affiliate', 'affiliate_id', 'subid',
                       'hop', 'checkout', 'add-to-cart'))


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def safe_read(path: Path) -> str:
    mode = path.lstat().st_mode
    if not stat.S_ISREG(mode) or path.stat().st_size > 8_000_000:
        raise ValueError('missing, nonregular or oversize artifact: ' + path.name)
    return path.read_text(encoding='utf-8')


def bad_url(url: str) -> bool:
    u = url.strip().replace('&amp;', '&')
    if u.startswith(('//', '\\', 'javascript:', 'data:')):
        return True
    p = urlsplit(u)
    if p.scheme and p.scheme not in ('https', 'http'):
        return True
    host = (p.hostname or '').lower().rstrip('.')
    if any(host == h or host.endswith('.' + h) for h in BLOCKED_HOSTS):
        return True
    return any(k.lower() in BANNED_QS for k, _ in parse_qsl(p.query, keep_blank_values=True))


class Surface(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.forms = 0
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('iframe', 'object', 'embed', 'base', 'link'):
            self.errors.append('external/embed-capable element: ' + tag)
        if tag == 'script':
            self.scripts += 1
            if 'src' in a:
                self.errors.append('external script loading')
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            self.errors.append('redirecting meta refresh')
        if tag == 'form':
            self.forms += 1
            if any(k in a for k in ('action', 'formaction', 'method', 'enctype', 'target')):
                self.errors.append('data-submitting form')
            if a.get('onsubmit', '').strip().replace(' ', '').lower() != 'returnfalse':
                self.errors.append('form without explicit local-only submit prevention')
        for k, v in attrs:
            if k in ('href', 'src', 'action', 'formaction', 'data-href') and v and bad_url(v):
                self.errors.append('merchant/unsafe outbound destination')
            if k.startswith('on') and k != 'onsubmit':
                # The native article/tool builder injects an explicit local-only
                # print button into every generated WordPress draft. R189's
                # original broad denylist rejected all authentic exports here.
                # Only the exact user-initiated window.print() button is safe
                # to admit; all other handlers, variants and combined actions
                # remain blocked (including extra semicolon/call text).
                local_print = (tag == 'button' and k == 'onclick'
                               and v == 'window.print()'
                               and a.get('type') == 'button'
                               and set((a.get('class') or '').split()) ==
                                   {'pa-btn', 'pa-btn--ghost'})
                if not local_print:
                    self.errors.append('unreviewed inline event handler')
            if k in ('src', 'srcset') and v and ('://' in v or v.startswith('//')):
                self.errors.append('externally loading media')
        if tag == 'a' and a.get('rel') and 'sponsored' in a['rel'].lower().split():
            self.errors.append('unapproved sponsored-link placement')


def inspect_js(text: str) -> list[str]:
    return [label for label, matcher in PRIVACY_SINKS.items() if matcher.search(text)]


def check(prep: Path, pins: dict[str,str] | None = None, *, require_exports: bool = True) -> dict:
    packet = {'schema': SCHEMA, 'state': INVALID, 'tools_checked': 0,
              'js_producers_verified': 0, 'wp_exports_checked': 0, 'errors': [],
              'publication_authorized': False, 'independent_qd_pass': False,
              'qualified_safety_review_complete': False,
              'privacy_browser_qa_complete': False, 'merchant_offer_verified': False,
              'verified_paid_orders': None, 'realized_net_revenue': None}
    errors = packet['errors']
    try:
        if not prep.is_dir() or prep.is_symlink():
            raise ValueError('missing or symlinked Preparedness root')
        approved = JS_PINS if pins is None else pins
        if set(approved) != set(JS_PINS) or not all(re.fullmatch(r'[0-9a-f]{40}', x or '') for x in approved.values()):
            raise ValueError('JavaScript pin roster malformed')
        tools_dir = prep / 'tools'
        if tools_dir.is_symlink():
            raise ValueError('symlinked producer tools directory')
        modules = {}
        for filename, expected in sorted(approved.items()):
            file = tools_dir / filename
            content = safe_read(file)
            if blob_sha(content.encode('utf-8')) != expected:
                raise ValueError('JavaScript source Git identity drift: ' + filename)
            if inspect_js(content):
                raise ValueError('interactive module privacy sink: ' + filename)
            modules[filename] = content
            packet['js_producers_verified'] += 1
        body_names = {p.name.removesuffix('.body.html') for p in (prep/'content/tools').glob('*.body.html')}
        meta_names = {p.name.removesuffix('.meta.json') for p in (prep/'content/tools').glob('*.meta.json')}
        if body_names != set(TOOLS) or meta_names != set(TOOLS):
            raise ValueError('six tool body/metadata roster changed')
        for name, expected_modules in sorted(TOOLS.items()):
            body = safe_read(prep/'content/tools'/f'{name}.body.html')
            meta = json.loads(safe_read(prep/'content/tools'/f'{name}.meta.json'))
            if meta.get('slug') != name or meta.get('status', {}).get('publish') != 'draft':
                raise ValueError('non-draft or mismatched tool identity: ' + name)
            uses = TOKEN.findall(body)
            if tuple(uses) != expected_modules or body.count('{{inline-js:') != len(uses):
                raise ValueError('unknown/reordered/unresolved inlined JS module: ' + name)
            if inspect_js(body.replace('{{inline-js:', '<!-- inline module ')):
                raise ValueError('tool body privacy sink: ' + name)
            surface = Surface()
            surface.feed(body)
            if surface.errors:
                raise ValueError('tool source HTML failed boundary: ' + name + ': ' + ', '.join(surface.errors))
            packet['tools_checked'] += 1
            if require_exports:
                target = prep/'build/wp'/f'{name}.html'
                markup = safe_read(target)
                if not markup.startswith('<!-- wp:html -->') or not markup.rstrip().endswith('<!-- /wp:html -->'):
                    raise ValueError('not a WordPress draft: ' + name)
                if '{{inline-js:' in markup or 'data-verify="reviewed"' in markup or 'safety-approved-draft' in markup:
                    raise ValueError('unresolved token or false approval in export: ' + name)
                for filename in expected_modules:
                    if markup.count(modules[filename]) != 1:
                        raise ValueError('JS module not faithfully inlined exactly once: ' + name + '/' + filename)
                if inspect_js(markup):
                    raise ValueError('WordPress export privacy sink: ' + name)
                rendered = Surface()
                rendered.feed(markup)
                if rendered.errors:
                    raise ValueError('WordPress export HTML failed boundary: ' + name + ': ' + ', '.join(rendered.errors))
                packet['wp_exports_checked'] += 1
        packet['state'] = HOLD if require_exports else INVALID
        if not require_exports:
            errors.append('source-only structural screening; missing native WordPress export acceptance')
    except (ValueError, OSError, UnicodeError, TypeError, KeyError, AttributeError, json.JSONDecodeError) as exc:
        errors.append(str(exc)[:250])
    return packet


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path('.'))
    ap.add_argument('--source-only', action='store_true',
                    help='source diagnostics only; always INVALID_HARD_HOLD')
    args = ap.parse_args(argv)
    print(json.dumps(check(args.repo/'preparedness', require_exports=not args.source_only), sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
