#!/usr/bin/env python3
"""Fail-closed browser request boundary for unpublished EX2 WordPress QA.

Allowed: current isolated preview origin, non-network data/blob, and exactly the
Apollo 1 / Franklin media URLs (including reviewed WP CDN derivatives). This
prevents preview scripts/iframes/beacons from calling production or merchants.
It does NOT prove archival rights, image delivery, WP host parity or conversion.
"""
from urllib.parse import urlsplit
from verify_archival_provenance import MEDIA, ORIGIN, BASE, classify_source


def admit_request(request_url, preview_url, *, navigation=False):
    """Return a labeled allow decision; raise ValueError on unexpected requests.

    Policy operates on the fully resolved browser request URL, not an HTML
    attribute. Playwright applies this check again on redirected requests.
    """
    target = urlsplit(request_url)
    preview = urlsplit(preview_url)
    if target.scheme in ('data', 'blob') and not navigation:
        return 'INLINE_NO_NETWORK'
    if (target.username or target.password or target.fragment or
            target.scheme not in ('http', 'https')):
        raise ValueError('INVALID_REQUEST_URL')
    if (preview.scheme, preview.hostname, preview.port) == (
            target.scheme, target.hostname, target.port):
        return 'ISOLATED_PREVIEW_ORIGIN'
    if navigation:
        raise ValueError('CROSS_ORIGIN_NAVIGATION_REFUSED')
    if target.scheme != 'https' or target.port is not None:
        raise ValueError('EXTERNAL_NON_HTTPS_OR_PORT_REFUSED')
    for index, media in enumerate(MEDIA):
        approved = 'https://' + ORIGIN + BASE + media['file']
        try:
            kind = classify_source(approved, request_url, index)
            return 'APPROVED_ARCHIVE_CDN' if not kind['first_party'] else 'APPROVED_ARCHIVE_ORIGIN'
        except ValueError:
            pass
    raise ValueError('UNAPPROVED_EXTERNAL_BROWSER_REQUEST')
