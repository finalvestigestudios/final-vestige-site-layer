#!/usr/bin/env python3
"""Bridge a Playwright Page's actual image responses into archival admission.

The older audit_archive_gallery API accepted page.request.get(), which fetches
an independent, possibly different HTTP body. Here .request.get() is a strictly
local *lookup* in Page.on('response') events captured before page.goto(). It
never makes another HTTP request. This applies only to isolated stage QA.
"""
from urllib.parse import urlsplit

IMAGE_MIME = {'apollo.webp': 'image/webp',
              'franklin.jpg': 'image/jpeg', 'nypl.jpg': 'image/jpeg'}

class BrowserMediaAdmissionClosed(RuntimeError):
    pass


def require(ok, reason):
    if not ok:
        raise BrowserMediaAdmissionClosed('BROWSER MEDIA ADMISSION CLOSED: ' + reason)


class CapturedBrowserRequest:
    """Restricted request facade; .get() returns the browser's response."""
    def __init__(self, events, stage_origin):
        require(isinstance(events, list), 'response event ledger required')
        self.events = events
        self.stage_origin = stage_origin

    def get(self, src, timeout=30000):
        u = urlsplit(src)
        name = u.path.rsplit('/', 1)[-1]
        require((u.scheme, u.netloc) == self.stage_origin and
                u.path.endswith('/media/' + name) and name in IMAGE_MIME and
                not u.query and not u.fragment,
                'unexpected image source in browser response lookup')
        matched = [r for r in self.events if r.url == src]
        require(len(matched) == 1,
                name + ': expected one browser network response, found ' + str(len(matched)))
        response = matched[0]
        request = response.request
        require(request.url == src and request.resource_type == 'image',
                name + ': event is not the image request made by the browser')
        require(request.redirected_from is None,
                name + ': redirect chain present in browser image request')
        require(response.status == 200,
                name + ': browser image HTTP status differs from 200')
        require(not response.from_service_worker,
                name + ': service-worker body is not a direct stage-image transfer')
        content_type = response.headers.get('content-type', '').split(';', 1)[0].strip().lower()
        require(content_type == IMAGE_MIME[name],
                name + ': incorrect browser image response MIME')
        # Response.body() below waits for the browser transfer; do not issue a
        # separate finished() task that can outlive the Playwright context.
        return response


class BrowserEvidencePage:
    """Read-only Page facade with verified browser-response lookup, not HTTP GET."""
    def __init__(self, page, response_events, stage_origin):
        self._page = page
        self.request = CapturedBrowserRequest(response_events, stage_origin)

    def __getattr__(self, name):
        return getattr(self._page, name)
