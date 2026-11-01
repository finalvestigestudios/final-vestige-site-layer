#!/usr/bin/env python3
"""Pure gates for a real, isolated WordPress/Assembler seven-chapter preview.

Do not use as a replacement for WordPress runtime, field CWV, independent
image-rights clearance, Jetpack fulfillment, WCAG or independent QD review.
"""
import hashlib
import hmac
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

MEDIA = {
    'apollo.webp': {'bytes': 78346, 'dimensions': [1041, 810],
        'source_url': 'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'},
    'franklin.jpg': {'bytes': 466043, 'dimensions': [960, 1526],
        'source_url': 'https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg'},
    'nypl.jpg': {'bytes': 5553669, 'dimensions': [5667, 3831],
        'source_url': 'https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg'},
}

class AdmissionClosed(RuntimeError):
    pass

def require(condition, reason):
    if not condition:
        raise AdmissionClosed('FV INTEGRATED WORDPRESS STAGE CLOSED: ' + reason)

def validate_stage_url(url, approved_extra_host=None):
    """Allow loopback, the official Playground UI, or a named HTTPS stage.

    A named external host is an explicit operator choice, NOT proof of
    ownership or actual WordPress installation. Never accept prod aliases.
    """
    u = urlsplit(url)
    host = (u.hostname or '').lower().rstrip('.')
    require(u.scheme in ('http', 'https') and host and not u.username and not u.password,
            'explicit HTTP(S) preview URL without credentials required')
    require(not u.fragment and not u.query, 'unexpected query or fragment in stage URL')
    require(host != 'finalvestige.com' and not host.endswith('.finalvestige.com'),
            'production domain or subdomain prohibited')
    try:
        loopback = ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = host == 'localhost' or host.endswith('.localhost')
    approved = approved_extra_host is not None and host == approved_extra_host.lower().rstrip('.')
    require(loopback or host == 'playground.wordpress.net' or approved,
            'host not on isolated-stage allowlist')
    if approved and not loopback and host != 'playground.wordpress.net':
        require(u.scheme == 'https', 'non-local approved stage requires HTTPS')
    return host

def read_trusted_media_manifest(path):
    """Never mistake an image's self-reported test-run hash for trusted custody."""
    source = Path(path)
    require(source.is_file(), 'independently reviewed original-image manifest missing')
    data = json.loads(source.read_text(encoding='utf-8'))
    require(isinstance(data, dict) and data.get('purpose') == 'isolated-staging-media-review'
            and isinstance(data.get('images'), dict), 'media manifest schema/purpose invalid')
    images = data['images']
    require(set(images) == set(MEDIA), 'must attest exactly three archival originals')
    identities = {}
    for name, expected in MEDIA.items():
        record = images[name]
        require(isinstance(record, dict) and record.get('source_url') == expected['source_url']
                and type(record.get('bytes')) is int and record['bytes'] == expected['bytes']
                and isinstance(record.get('sha256'), str)
                and re.fullmatch('[0-9a-f]{64}', record['sha256']),
                'untrusted original image metadata/identity for ' + name)
        identities[name] = record['sha256']
    return identities

def verify_integrated_dom(data):
    """Require retained live content and the genuine WordPress theme body class."""
    require(isinstance(data, dict), 'missing rendered DOM metrics')
    require(data.get('main') == 1 and data.get('h1') == 1,
            'WordPress page landmarks invalid')
    require(data.get('links') == 7 and data.get('panels') == 3,
            'seven chapters and three investigation cases missing')
    require(data.get('flagship_roots') == 1, 'unique cinematic flagship root missing')
    require(data.get('legacy_hero') == 0 and data.get('dev_controls') == 0,
            'obsolete or developer-only hero leaked')
    require(data.get('margins') == 72,
            '72 original Hidden in the Margins records not rendered')
    require(data.get('focus_links', 0) >= 2,
            'original Fieldbook links not rendered')
    require('wp-theme-assembler' in data.get('body_classes', []),
            'Assembler WordPress body-class evidence missing')
    require(data.get('sw', 0) <= data.get('cw', -1) + 1, 'horizontal root overflow')
    return True

def verify_media_payload(name, body, natural_dimensions, expected_sha):
    """Compare genuine HTTP image bytes to a manifest established beforehand."""
    require(name in MEDIA, 'unexpected stage image')
    expected = MEDIA[name]
    require(isinstance(body, bytes) and len(body) == expected['bytes'],
            name + ': exact HTTP byte length mismatch')
    require(list(natural_dimensions) == expected['dimensions'],
            name + ': browser-decoded natural dimensions mismatch')
    require(isinstance(expected_sha, str)
            and re.fullmatch('[0-9a-f]{64}', expected_sha),
            name + ': independent trusted digest missing')
    actual = hashlib.sha256(body).hexdigest()
    require(hmac.compare_digest(actual, expected_sha),
            name + ': HTTP content differs from independently reviewed original')
    return {'bytes': len(body), 'dimensions': expected['dimensions'], 'sha256': actual}
