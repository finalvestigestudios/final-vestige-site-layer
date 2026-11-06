#!/usr/bin/env python3
"""Real browser evidence gate for the two flagship archival plates.

Requires decoded pixels AND a successful response-body receipt for the exact
selected responsive URL. Does not establish archive rights or image identity.
Does not certify production, WCAG, Lighthouse, Jetpack, or affiliate revenue.
"""
from urllib.parse import urlparse

ARCHIVES = {
    'apollo': 's67-19766.webp',
    'franklin': 'Franklinexpeditionnote.jpg',
}


def public_url(url):
    """Avoid persisting tokens, private-preview query strings or fragments."""
    p = urlparse(url)
    return p._replace(query='', fragment='', params='').geturl()


def audit_archival_transfers(page, transfers, widths=(390, 1440)):
    """Inspect selected srcset URLs at each width using actual browser requests.

    ``transfers`` is keyed by the *full* response.url (including query) in
    memory, while returned receipts never expose query/preview parameters.
    Only two known sources are mandatory; NYPL remains rights-gated separately.
    """
    evidence = {}
    for width in widths:
        page.set_viewport_size({'width': width, 'height': 844})
        evidence[str(width)] = {}
        for name, needle in ARCHIVES.items():
            loc = page.locator(f'img[src*="{needle}"]').first
            entry = {'present': bool(loc.count()), 'pixels_decoded': False,
                     'response_verified': False, 'alt_present': False, 'passed': False}
            if not entry['present']:
                evidence[str(width)][name] = entry
                continue
            try:
                loc.scroll_into_view_if_needed(timeout=5000)
                page.wait_for_function("""selector => {
                    const image = document.querySelector(selector);
                    return !!(image && image.complete);
                }""", arg=f'img[src*="{needle}"]', timeout=8000)
                dom = loc.evaluate("""image => ({
                    current_src: image.currentSrc || image.src,
                    natural_width: image.naturalWidth,
                    natural_height: image.naturalHeight,
                    alt: image.getAttribute('alt') || ''
                })""")
                entry['selected_url'] = public_url(dom['current_src'])
                entry['pixels_decoded'] = dom['natural_width'] > 0 and dom['natural_height'] > 0
                entry['alt_present'] = bool(dom['alt'].strip())
                response = transfers.get(dom['current_src'])
                if response:
                    entry['http_status'] = response.get('status')
                    entry['body_bytes'] = response.get('actual_body_bytes', 0)
                    entry['sha256'] = response.get('sha256')
                    entry['response_verified'] = (
                        isinstance(response.get('status'), int)
                        and 200 <= response['status'] < 300
                        and response.get('actual_body_bytes', 0) > 0
                        and isinstance(response.get('sha256'), str)
                        and len(response['sha256']) == 64
                    )
                entry['passed'] = (entry['pixels_decoded'] and entry['alt_present']
                                   and entry['response_verified'])
            except Exception as exc:
                entry['error'] = type(exc).__name__
            evidence[str(width)][name] = entry
        page.evaluate('window.scrollTo(0,0)')
    return {'widths': evidence, 'passed': all(
        item['passed'] for width in evidence.values() for item in width.values()),
        'rights_clearance': 'NOT_ASSESSED', 'identity_verification': 'NOT_ASSESSED'}
