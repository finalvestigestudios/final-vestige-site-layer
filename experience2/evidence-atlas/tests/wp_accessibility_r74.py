"""R74 isolated real-WordPress accessibility probes (not AT certification)."""
from __future__ import annotations
import hashlib
from pathlib import Path


def verify_installed_controls(page, width: int, out: Path) -> dict:
    """Exercise installed Apollo markup, not a source-only HTML preview.

    Called at 390/1440 JS-on after source filters and reset. The high-contrast
    screenshot is laboratory evidence, not a screen-reader pass.
    """
    if width not in (390, 1440) or page.evaluate('innerWidth') != width:
        raise AssertionError('R74_UNEXPECTED_ACCESSIBILITY_VIEWPORT')
    buttons = page.locator('.fv-ex2-apollo-suite [data-fva-copy]')
    if buttons.count() != 6:
        raise AssertionError('R74_CITATION_CONTROL_COUNT')
    for button in buttons.all():
        visible = ' '.join(button.inner_text().split())
        accessible = button.get_attribute('aria-label') or ''
        if not visible or visible not in accessible:
            raise AssertionError('R74_WCAG_2_5_3_LABEL_MISMATCH')
    source_links = page.locator('.fv-ex2-apollo-suite .fva-card__external')
    if source_links.count() != 6:
        raise AssertionError('R74_NASA_SOURCE_LINK_COUNT')
    minimum = min(link.bounding_box()['height'] for link in source_links.all())
    if minimum < 44:
        raise AssertionError('R74_NASA_SOURCE_TARGET_UNDERSIZED')
    page.emulate_media(forced_colors='active', reduced_motion='reduce')
    try:
        summary = page.locator('.fv-ex2-apollo-suite [data-fva-drawer] summary').first
        summary.focus()
        if not summary.evaluate('el => document.activeElement === el'):
            raise AssertionError('R74_FORCED_COLORS_KEYBOARD_FOCUS_LOST')
        if page.locator('[data-fva-record]:visible').count() != 6:
            raise AssertionError('R74_FORCED_COLORS_SOURCE_CONTENT_LOST')
        if page.evaluate('document.documentElement.scrollWidth > innerWidth + 2'):
            raise AssertionError('R74_FORCED_COLORS_HORIZONTAL_OVERFLOW')
        pixels = page.screenshot(full_page=True, animations='disabled', caret='hide')
    finally:
        page.emulate_media(forced_colors='none', reduced_motion='reduce')
    out.mkdir(parents=True, exist_ok=True)
    name = f'R74_AUTHENTIC_WP_FORCED_COLORS_{width}.png'
    (out/name).write_bytes(pixels)
    return {'width': width, 'citation_label_parity': 6, 'nasa_links': 6,
            'minimum_nasa_link_height_px': round(minimum, 2),
            'forced_colors_source_records': 6, 'keyboard_focus_retained': True,
            'forced_colors_screenshot': name,
            'forced_colors_screenshot_sha256': hashlib.sha256(pixels).hexdigest(),
            'screen_reader_manual_testing_complete': False}
