# Focus popup: isolated browser smoke test (DRAFT/HOLD)

This optional test exercises the exact source-controlled assets in `experience2/conversion/focus-popup.*` from draft PR #349. At widths 320, 390, 768 and 1440px it tests four states: no Jetpack form vs a representative mocked native form, each with JavaScript on and off. It tests **fallback-link preservation**, explicit-click modal activation, keyboard Enter/Escape, email focus, focus return, JavaScript errors, and horizontal overflow. It sends **no email or network request**, does not subscribe visitors, and does not touch WordPress.

```bash
python -m unittest qa.focus_popup_browser.test_focus_popup_chromium -v
# Requires Python Playwright and a local Chromium/Playwright browser.
# Optional FV_CHROMIUM=/path/to/chromium
```

**Important acceptance limits:** The mock form is not a real WordPress/Jetpack block. This test does not prove `do_blocks`/shortcode Gutenberg renderability, real confirmation, actual received welcome email, download delivery, mobile Safari, screen-reader behavior, full-page WCAG 2.2 AA, Lighthouse, media rights, or production page readiness. Keep the popup unpublished pending isolated WordPress integration and QD approval. The current Focus Fieldbook remains the only live lead magnet; never duplicate it or revive retired water marketing.
