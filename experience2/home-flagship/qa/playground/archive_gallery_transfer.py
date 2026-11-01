#!/usr/bin/env python3
"""Exact three-case image-transfer admission for isolated FV WordPress staging.

The source galleries use loading=lazy and the JavaScript case chooser hides
inactive panels.  A gallery check must select, reveal and scroll each panel
before evaluating image.decode/naturalWidth.  It must not force eager loading.
"""
from urllib.parse import urlsplit

CASE_MEDIA = (
    ('apollo', 'apollo.webp'),
    ('franklin', 'franklin.jpg'),
    ('malbone', 'nypl.jpg'),
)


def audit_archive_gallery(page, stage_origin, trusted_media, media_spec,
                          require, verify_payload):
    """Return attested case-keyed HTTP identities or fail closed.

    page is an actual Playwright Page in production, or a strict fake in tests.
    This is not a rights certificate, a production audit or a CWV result.
    """
    require(set(trusted_media) == {name for _, name in CASE_MEDIA},
            'three independent original-media identities required')
    all_images = page.locator('.fv-hf img').all()
    require(len(all_images) == len(CASE_MEDIA),
            f'exactly three case images required; found {len(all_images)}')
    attested = {}
    for case, name in CASE_MEDIA:
        button = page.locator(f'[data-fv-case-button="{case}"]')
        require(button.count() == 1 and button.is_visible(),
                case + ': usable case chooser button missing')
        button.click()
        panel = page.locator(f'[data-fv-case="{case}"]')
        require(panel.count() == 1 and panel.is_visible(),
                case + ': case panel never became visible')
        photo = panel.locator('img[data-fv-archive-img]')
        require(photo.count() == 1, case + ': unique archival image absent')
        require(bool((photo.get_attribute('alt') or '').strip()),
                case + ': source-bearing image has no meaningful alternative text')
        require(not photo.get_attribute('srcset'),
                case + ': external/responsive srcset survived first-party staging rewrite')
        # Crucial: hidden lazy-load images are not expected to have decoded at
        # initial page load. Selecting case + scrolling naturally initiates load.
        photo.scroll_into_view_if_needed(timeout=10000)
        page.wait_for_function("""caseId => {
            const panel=document.querySelector('[data-fv-case="'+caseId+'"]');
            const img=panel && panel.querySelector('img[data-fv-archive-img]');
            return !!(panel && !panel.hidden && img && img.complete &&
                img.naturalWidth>0 && img.naturalHeight>0);
        }""", arg=case, timeout=30000)
        src = photo.evaluate('(img) => img.currentSrc')
        u = urlsplit(src)
        require((u.scheme, u.netloc) == stage_origin and
                u.path.endswith('/media/' + name) and not u.query and not u.fragment,
                case + ': image not loaded from exact local stage-media path: ' + src)
        obj = page.request.get(src, timeout=30000)
        final = urlsplit(obj.url)
        require((final.scheme, final.netloc) == stage_origin and
                final.path.endswith('/media/' + name) and not final.query,
                case + ': media HTTP request redirected or changed media path')
        raw = obj.body()
        length, width, height = media_spec[name]
        require(obj.status == 200 and len(raw) == length,
                case + ': actual HTTP payload length/status mismatch')
        dims = photo.evaluate('(img) => [img.naturalWidth, img.naturalHeight]')
        require(dims == [width, height],
                case + ': actual decoded image dimensions mismatch')
        verified = verify_payload(name, raw, dims, trusted_media[name])
        attested[name] = {**verified, 'case': case, 'origin': final.netloc,
                          'transfer': 'VISIBLE_CASE_LAZY_LOADED_AND_SHA256_MATCHED',
                          'trusted_identity': 'INDEPENDENT_MANIFEST_MATCH'}
    # End the audit in the intended editorial default; a later interaction test
    # must still be able to select Franklin from this stable Apollo baseline.
    page.locator('[data-fv-case-button="apollo"]').click()
    require(page.locator('[data-fv-case="apollo"]').is_visible(),
            'default Apollo case not restored after media verification')
    return attested
