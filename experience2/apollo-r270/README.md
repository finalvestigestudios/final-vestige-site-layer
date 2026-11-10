# Apollo R270 — Research Desk multi-instance accessibility custody (STAGING HOLD)

Issue #150 / conversion issue #820 / charter #818. This is an optional, isolated WordPress filter plugin, **not part of the frozen homepage PR #49** or Research Desk PR #158. Base branch is Apollo R269. It is neither installed nor approved for publication.

## Actual source defect

The existing PR #158 Research Desk `ledger.html` has nine literal IDs (one heading, input, grid and six records) and references them with `for`, `aria-labelledby`, `aria-controls`. This is fine once, but two `[fv_ex2_research_desk]` shortcodes on a single page duplicate the IDs. Such duplicates are particularly likely in a reusable/nested block or two placements of the same source ledger. The original Search JS scopes its lookups to each root, but duplicated label/control IDREFs can send assistive technology to the wrong copy. PR #158's original source remains untouched.

## Implementation

The separate `rd-instance-scope.php` registers the WordPress `do_shortcode_tag` filter, verifies the known six-record markup shape, and rewrites all nine IDs and their associated HTML IDREFs only for the second and subsequent Research Desk render in the PHP request. The first shortcode preserves its existing stable IDs. It does **not** alter NASA anchors, dates, interpretations, artwork, commerce, CSS/JS, homepage content or tracking. If a template no longer matches the structural contract, the filter passes through the original markup rather than hiding it. With JavaScript disabled, the native summaries, source links and labels still work. **Important:** original PR #158 assets may still be missed when a shortcode appears only in a nested/dynamic block: this separate adapter does not fix that existing load condition.

## Exact source and tests

PR #158 originals independently read: `final-vestige-ex2-research-desk.php` Git blob `d1879a90101b5475990132369178f42743f4b57c`; `templates/ledger.html` Git blob `403d128c57b9bc82dac7c619651689070edef86c` (9 IDs, 6 evidence cards, 14 source links); `assets/source-ledger.js` Git blob `32e757cc4dc8708397ff65ac21e89dd319781d78`. No source text or rights transfer is implied. This branch includes **no copy of the six historical records**.

Execute:

```sh
php -l experience2/apollo-r270/rd-instance-scope.php
php experience2/apollo-r270/qa/php-scope-gate.php > /tmp/three-desks.html
python experience2/apollo-r270/qa/research_desk_browser.py /tmp/apollo-r270-qa
```

Requirements: PHP 7.4+, Python Playwright and `/usr/bin/chromium` (for this tested runner). The CLI WordPress filter simulation outputs a **synthetic, semantically compatible six-card fixture**, not the original full PR #158 HTML. The browser test loads that generated output with a copy of PR #158's source-ledger.js, 320, 390, 768, 1440 and 1920px with JS enabled/disabled, reduced motion, keyboard/native disclosure, 3 independently scoped searches, no extra network, valid IDREFs and no horizontal overflow. Actual original-template integration and genuine axe-core are **not claimed**. Test with real template and real WordPress/Assembler before acceptance.

## Release and business gates

HARD HOLD: genuine axe-core; screen readers; actual 320–1920 device/zoom; installed WordPress with two repeated/nested shortcodes; HTTP/CSP and asset-enqueue lifecycle; field LCP/CLS; exact-HEAD hosted CI; independent QA; source/rights verification; relevant merchant status; founder release permission. No production writes, no new analytics/vendor script, no posts or payments.

Conversion mapping, one editorial-to-purchase hypothesis only: Grok's **verified existing** Apollo asset (not yet provided) → Apollo Evidence Atlas → free original investigation (`https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`) → optional **separate, disclosed** Mini Museum guide (`https://finalvestige.com/mini-museum-history-collectibles/`) → merchant-confirmed paid affiliate sale **only if independently reported**. Apollo specimen provenance is not to be inferred from unrelated merchant collectibles. This sprint changes only a Research Desk accessibility blocker, not the CTA or merchant route.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Mini Museum guide | Qualified purchase | Awin acceptance and settlement unavailable | Verify seller approval/paid orders, fees and refunds | HOLD, not revenue | Founder / Claude |
| Grok Apollo documentary | Acquisition to Atlas | Original published asset ID, rights and clickable path unverified | Existing TASK-008 source audit only | UNKNOWN | Grok / Praxxis |
| Free Research Desk | Evidence-to-investigation trust bridge | Repeated shortcodes duplicate IDREFs | R270 server-side namespace | PHP + Chromium fixture PASS, WordPress NOT TESTED | Apollo |
| Confirmed customers | Revenue/1k qualified sessions | No qualified-human denominator or authenticated paid settlement | 7/30-day cohort reconciliation | NOT COMPUTABLE | Claude / Commerce |

Do not publish or activate the Mini Museum CTA from this branch. Conversion success is realized net revenue per 1,000 qualified human sessions, not pageviews, outbound clicks or unconfirmed checkout starts.
