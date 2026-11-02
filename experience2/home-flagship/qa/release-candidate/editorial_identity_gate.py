"""Exact rendered-identity gate for the founder-approved locked flagship direction.

Used by the *private* WordPress/Assembler acceptance harness. Pure Playwright
locators only: never loads a live CMS, adds content, or changes production.
"""
from __future__ import annotations


def check_locked_editorial_identity(frame) -> dict[str, bool]:
    """Fail closed on missing/altered Franklin folio or obsolete studio picker.

    The folio is explicitly editorial typesetting of dated evidence, not a
    facsimile. These checks must run on rendered browser DOM, not static HTML.
    """
    hero = frame.locator('[data-fv-home-flagship]')
    note = frame.locator('.fv-hf__opening-art .fv-hf__folio-note')
    original = note.locator('time[datetime="1847-05-28"]')
    addition = note.locator('.fv-hf__folio-margin')
    caption = note.locator('.fv-hf__folio-note-foot')
    source = frame.locator(
        '.fv-hf__opening-art a[href="https://www.rmg.co.uk/collections/objects/rmgc-object-504898"]'
    )
    checks = {
        'locked_direction_no_legacy_picker': frame.locator(
            '[data-fv-direction-choice], .fv-hf__studio-controls'
        ).count() == 0 and hero.count() == 1 and hero.get_attribute('data-fv-direction') is None,
        'archival_folio_one_visible': note.count() == 1 and note.is_visible(),
        'folio_1847_original_dated': original.count() == 1
            and '1847' in (original.inner_text() if original.count() else ''),
        'folio_1848_addition_explicit': addition.count() == 1
            and '1848' in (addition.inner_text() if addition.count() else ''),
        'folio_disclaims_facsimile': caption.count() == 1
            and 'NOT A FACSIMILE' in (caption.inner_text() if caption.count() else ''),
        'folio_original_source_link': source.count() == 1 and source.is_visible(),
    }
    if note.count() == 1:
        paint = note.evaluate('''el => {
            const box = el.getBoundingClientRect(), css = getComputedStyle(el);
            return {width: box.width, height: box.height, bg: css.backgroundColor};
        }''')
        checks['folio_real_geometry_and_paint'] = (
            paint['width'] >= 150 and paint['height'] >= 230 and
            paint['bg'] not in ('transparent', 'rgba(0, 0, 0, 0)'))
    else:
        checks['folio_real_geometry_and_paint'] = False
    return checks
