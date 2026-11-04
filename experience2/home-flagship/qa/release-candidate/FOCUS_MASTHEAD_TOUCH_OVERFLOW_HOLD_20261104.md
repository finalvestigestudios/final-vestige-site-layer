# EX2 flagship Focus masthead: conversion-first release HOLD (2026-11-04 PT)

Parent exact head: PR #918 / `3ec8f41d0b20478be726281452d699c034fc7aa7`. Frozen #49 unchanged. No WordPress production writes.

**Source-grounded bug:** Existing mast CTA uses 9px vertical padding and 10px (mobile) / 11px (desktop) font with no 44px minimum. The no-wrap mobile masthead can exceed 320/360px widths. Both conflict with anonymous-visitor admission requirements.

**Actual change:** Scoped CSS gives the existing canonical `https://finalvestige.com/focus/` CTA a 44px minimum and flex centering; allows wrapping <=600px; makes CTA full-width <=420px. No new chapter, popup, JS, affiliate link, UTM, merchant claim or tracker. Seven chapters, all 72 Margins, Fieldbook and Jetpack contract preserved.

**Actually measured, not WordPress staging:** Isolated faithful masthead markup/CSS Chromium fixture, JS disabled + reduced motion, 9 viewport widths 320/360/390/420/600/720/768/1440/1920. Previous CTA height: 36.5px mobile / 38.14px desktop; new: 44px at all widths. At 320px, scrollWidth previously 388px, now 320px; at 360px, 388px→360px. Previous layout failed 9/9 touch checks; new passes 9/9. Before/after screenshot/JSON evidence provided separately. This is representative component evidence, **not** full exact-source WordPress evidence.

**Exact-source browser test BUILT, NOT YET EXECUTED:** `tests/verify_focus_masthead_browser.py` loads actual `index.html` plus all six source stylesheets, disables JS and external requests, checks all nine widths for first-screen placement, 44px hit area, center obstruction, keyboard focus, canonical destination and overflow. Run `python -I experience2/home-flagship/tests/verify_focus_masthead_browser.py` on an exact checkout with Playwright/Chromium. It generates 320/390/1440 screenshots and JSON; no CMS writes.

**Still HOLD:** anonymous real WordPress/Assembler full-document axe with serious vendor navigation finding; actual archived-image bytes/rights; genuine 200% browser zoom, Safari, measured Lighthouse/CWV, independent QD, founder visual approval, verified product/paid conversion and net revenue. WordPress.com Personal does not provide native staging; free isolated Playground is not Atomic/Jetpack parity.

OFFER free Focus Fieldbook → FUNNEL first-screen anonymous reader CTA → BLOCKER <44px mobile CTA + narrow overflow → CHANGE scoped responsive CSS → EVIDENCE standalone fixture PASS, exact-source/WP pending → OWNER interim homepage engineering; Claude analytics/commerce, Grok/Praxxis campaign assets, founder release. No claim that a signup or purchase occurred.
