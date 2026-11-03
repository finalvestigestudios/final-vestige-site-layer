#!/usr/bin/env python3
"""R83 exact-source Apollo custody contract for authentic synced-pattern WordPress.

Read-only, total, and independent of JavaScript enhancements. Do not include
raw browser URLs or DOM text in any uploaded receipt or assertion error.
"""
from __future__ import annotations

NASA_SOURCE_URLS = (
    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
    'https://www.nasa.gov/image-detail/amf-s67-21294/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)
CITE_IDS = ('01', '02', '03', '04', '05', '06')


def verify_source_parity_r83(*, nasa_links, citation_ids, drawer_count,
                            images, geographic_claims, suite_heading,
                            rights_notice):
    """Reject omissions/substitutions without exposing mutable page content.

    The approved URLs track the pinned R37 crosswalk. Their presence does NOT
    certify that NASA links were fetched or that any photo can be reused.
    """
    if tuple(nasa_links) != NASA_SOURCE_URLS:
        raise AssertionError('R77_R83_LINK_CUSTODY_CHANGED')
    if tuple(citation_ids) != CITE_IDS:
        raise AssertionError('R77_R83_CITATIONS_MISSING')
    if drawer_count != 6:
        raise AssertionError('R77_R83_SOURCE_DRAWERS_MISSING')
    if images != 0:
        raise AssertionError('R77_R83_MEDIA_UNCLEARED')
    if geographic_claims != 0:
        raise AssertionError('R77_R83_GEO_UNVERIFIED')
    if not isinstance(suite_heading, str) or 'no image-use rights are asserted' not in suite_heading.lower():
        raise AssertionError('R77_R83_RIGHTS_NOTICE_MISSING')
    if 'unconfirmed s67-19766' not in suite_heading.lower():
        raise AssertionError('R77_R83_PROVISIONAL_NOTICE_MISSING')
    if not isinstance(rights_notice, str) or (
        '0 of 6' not in rights_notice or
        'not a human link check' not in rights_notice.lower() or
        'rights clearance' not in rights_notice.lower()
    ):
        raise AssertionError('R77_R83_RIGHTS_CLEARANCE_UNVERIFIED')
    return {
        'approved_nasa_destinations': 6,
        'reviewed_citation_ids': 6,
        'native_source_drawers': 6,
        'photographs_embedded': 0,
        'geographic_claims': 0,
        'individual_photo_rights_cleared': 0,
        'catalog_source_01_provisional': True,
        'official_link_fetch_or_rights_verified': False,
    }
