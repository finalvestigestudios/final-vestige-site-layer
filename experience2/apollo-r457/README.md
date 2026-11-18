# Apollo R457 — archival provenance gallery (STAGING ONLY)

Parent issues #150, #820 and #818. Stacked on R456 PR #3005. Separate path only: `experience2/apollo-r457/`; homepage PR #49, Research Desk PR #158, Grok/Praxxis TASK-008 and Claude production branches untouched.

## Why
The currently published Apollo Evidence Atlas names six NASA photographic records: S66-58038, S67-15717 and KSC-20170124-PH_KLS01_0129 are described as **shown**; S67-19766, S67-21294 and KSC-20170124-PH_KLS01_0090 are **withheld**. These are publicly displayed editorial statuses, NOT independent reuse certification. The NASA Images catalogue link for KSC-...0129 could not be independently retrieved on 2026-11-18: source-link acceptance remains HOLD. All cards distinguish date precision, event from later exhibit, source existence and media rights. Official NASA guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/.

## Built
Isolated staging shortcode `[fv_apollo_rights_gallery_r457]` with exact staging page gating, accessible six-card archival catalogue, native source drawers, optional JS status filter, fail-open fallback, no-JS records, keyboard/touch/forced-color/reduced-motion/print, 320–1920px CSS, no NASA photos/logos/likenesses, no fabricated geo pins. Exactly one relevant **free investigation** CTA. No commerce, analytics, signup or network requests.

## Local QA
`php -l apollo_rights_gallery.php`; `python qa/test_contract.py` (18 assertions PASS); `python qa/browser_qa.py` (20 Chromium cases PASS against PHP-generated markup via `page.set_content`, including 320–1920px and JS on/off; responsive screenshots in downloadable QA archive). This does NOT prove hosted navigation, axe-core, navigated LCP/CLS, real-device/assistive-tech or field CWV acceptance. Local navigation to 127.0.0.1 was blocked by browser policy. Exact-head CI/QD still needed.

## Conversion / release
Verified Grok Apollo long-form asset → source and image-rights gallery → one relevant free Apollo investigation CTA → **separately verified and founder-approved** rights-cleared original educator kit. No payable SKU, confirmed orders, fees/refunds, qualified-human sessions or net revenue currently verified. The global unrelated Focus Fieldbook signup popup on live Atlas should be inspected by Claude for conversion-intent mismatch; no WordPress change authorized. HARD HOLD: independent media rights, exact 2017 source link, authentic staging axe/LCP/CLS, QD, exact-head CI, founder permission. No social, WP, merchant, tracking or spending writes.
