"""Read-only evidence of browser-delivered archival image payloads.

A naturalWidth > 0 can come from cache and is not an HTTP delivery receipt.
This gate records what Playwright actually observed for each selected currentSrc;
body_bytes are decoded response payload bytes, NOT exact on-wire transfer bytes.
No image bodies, credentials, cookies or editor state are saved to disk.
"""
from __future__ import annotations
import hashlib
from urllib.parse import urlsplit

EXPECTED_ARCHIVES = (
    '/wp-content/uploads/2026/08/s67-19766.webp',
    '/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg',
    '/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg',
)
MAX_IMAGE_BYTES = 8 * 1024 * 1024


def archive_identity(url: str) -> str | None:
    try:
        parts = urlsplit(url)
        if parts.scheme != 'https' or parts.username or parts.password or parts.port not in (None, 443):
            return None
        host = (parts.hostname or '').lower()
        prefix = '/wp-content/uploads/' if host == 'finalvestige.com' else (
            '/finalvestige.com/wp-content/uploads/' if host == 'i0.wp.com' else '')
        if not prefix or not parts.path.startswith(prefix):
            return None
        normalized = parts.path if host == 'finalvestige.com' else parts.path[len('/finalvestige.com'):]
        if normalized not in EXPECTED_ARCHIVES: return None
        if normalized.endswith('/s67-19766.webp'): return 'apollo'
        if normalized.endswith('/Franklinexpeditionnote.jpg'): return 'franklin'
        if normalized.endswith('/edit-017-v02-nypl-5003296-original.jpg'): return 'malbone'
        return None
    except (ValueError, TypeError):
        return None


def audit_image_payloads(images: list[dict], observed_responses: list) -> dict:
    """Fail closed for missing, non-200, non-image, empty or oversized responses.

    Collect response objects after lazy archival images finish loading. New browser
    contexts per viewport avoid persistent cross-test cache, but don't certify
    CDN wire transfer size or origin-server cache behavior.
    """
    results, failures = [], []
    selected = {image.get('url', '') for image in images}
    if len(images) != 3 or len(selected) != 3:
        failures.append('EXPECTED_THREE_DISTINCT_ARCHIVAL_IMAGES')
    identities = [archive_identity(image.get('url', '')) for image in images]
    if set(identities) != {'apollo', 'franklin', 'malbone'}:
        failures.append('IMAGE_URL_PROVENANCE_OUT_OF_SCOPE')
    for image in images:
        url = image.get('url', '')
        ident = archive_identity(url)
        matches = [r for r in observed_responses if getattr(r, 'url', '') == url
                   and getattr(getattr(r, 'request', None), 'resource_type', '') == 'image']
        entry = {'archive': ident, 'requested_url': url, 'response_seen': bool(matches),
                 'http_status': None, 'content_type': None, 'decoded_payload_bytes': 0,
                 'payload_sha256': None, 'measurement': 'PLAYWRIGHT_RESPONSE_BODY_NOT_WIRE_BYTES'}
        if not ident or not matches:
            failures.append((ident or 'unknown') + ':IMAGE_HTTP_RESPONSE_MISSING')
            results.append(entry); continue
        response = matches[-1]
        entry['http_status'] = response.status
        try:
            entry['content_type'] = (response.header_value('content-type') or '').split(';')[0].lower().strip()
            if response.status != 200: raise ValueError('HTTP_STATUS_NOT_200')
            if not entry['content_type'].startswith('image/'): raise ValueError('NOT_IMAGE_CONTENT_TYPE')
            body = response.body()
            entry['decoded_payload_bytes'] = len(body)
            if not 0 < len(body) <= MAX_IMAGE_BYTES: raise ValueError('IMAGE_BODY_SIZE_INVALID')
            entry['payload_sha256'] = hashlib.sha256(body).hexdigest()
        except Exception as exc:
            failures.append((ident or 'unknown') + ':' + (str(exc) if isinstance(exc, ValueError) else 'BODY_FETCH_FAILED'))
        results.append(entry)
    return {'status': 'PASS' if not failures else 'HOLD',
            'method': 'Chromium/Playwright actual response body bytes; not wire bytes, TAO or field CWV',
            'images': results, 'failure_codes': failures,
            'decoded_payload_total_bytes': sum(x['decoded_payload_bytes'] for x in results)}
