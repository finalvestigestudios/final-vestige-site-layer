# Apollo R339 — NASA-verified native ChronologyRail (isolated staging)

Scope: issue #150, commerce #820/#818. **Draft-only** child of R338 (#2361), ultimately depending on Research Desk source-custody #2358 and owner PR #158. Never edit/merge homepage #49, modify Grok TASK-008, install a WordPress plugin or deploy this module without independent QD/founder approval.

## Actual implementation

- `chronology-rail.php`: isolated WordPress-compatible shortcode `[fv_apollo_chronology_r339]`, six source-custodied events, progressively enhanced **without JavaScript**, native chronological fragment links and native `details` source drawers. Each render gets unique heading and event IDs, including when multiple shortcode instances appear.
- `assets/chronology-rail.css`: scoped editorial rail, 320–1920px reflow, enlarged-type handling, 44px+ native links, focus, forced colors, touch, reduced motion, printable evidence. No image bytes, no map pins, no invented graph edges, no analytics, scripts, affiliate or paid-product links. CSS is **not automatically enqueued** by this research module: installation/asset lifecycle is separately gated.
- Exactly **one existing free investigation link per module**. It is an editorial continuation, not a purchase or an inferred sale. No authenticated Apollo-specific paid SKU was available to this sprint.

## Source custody: observable vs inferred

NASA 1967 **Apollo 204 Review Board**: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/

1. **23:31:04.7 GMT**, recorded first emergency voice transmission. Onset does not establish the ignition time and the first word/speaker remain uncertain.
2. **About 23:31:12**, Board's approximate analysis that the fire spread beyond its origin. Not an individual sensor reading.
3. **23:31:16.8**, recorded beginning of the last crew voice transmission. NASA cautions no definitive transcription of the garbled recording.
4. **About 23:31:19**, estimated command module rupture at **at least 29 psia**. Approximate time and pressure.
5. **23:31:22.4**, recorded last telemetry/voice data. Do not interpolate precise later event times after this boundary.
6. **Following the 1967 fire**, separate later NASA account of outward-opening unified hatch and broader redesign: https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/

The Board found **electrical arcing the most probable initiator**, **not a conclusively identified single ignition source**. NASA imagery/public records are not an automatic endorsement or blanket commercial-use clearance. The prototype uses **links and original editorial summaries, no embedded NASA photos**. Source categories and limitations remain visible with JS disabled.

## Reproduce local browser gate

```bash
php -l experience2/apollo-r339/chronology-rail.php
# Requires Python 3 + playwright + beautifulsoup4 and installed Chromium; no network needed.
FV_R339_OUT=/tmp/fv-apollo-r339 python experience2/apollo-r339/qa/chronology_gate.py
```

Test emits its own PHP-rendered **two-instance fixture** via CLI and tests native Chromium document semantics at widths 320,360,390,768,1024,1440,1920, no-JS, 200/400% root type, forced colors/reduced motion, real keyboard Enter, native fragment navigation and target hitboxes, with six negative custody/commerce mutation cases, structured JSON receipts and screenshots. Fixture LCP/CLS are diagnostics only, **not installed WordPress performance, certified axe, or field CWV**.

## Revenue path and permissions

**Hypothesis only:** Grok published Apollo video [UNVERIFIED] → NASA-backed R339 chronology + existing evidence Atlas/Research Desk [STAGING] → free Apollo investigation → separately **verified, genuinely payable and rights-cleared** educator case-file [BLOCKED]. Tracking must be implemented/reconciled separately by Claude/Grok via existing #820 contract: qualified-human asset_id/utm campaign session → CTA → independently confirmed paid order → fees/refunds → net realized revenue per 1,000 qualified human sessions. No paid conversion or commercial value is inferred from an editorial click.

## HOLD — required before release

Real WordPress/Assembler/CDN integration and shortcode asset delivery; independent Research Desk owner review; non-Chromium and screen-reader review; actual axe-core WCAG 2.2 AA testing; native HTTP/CSP, real hosted exact-HEAD CI, production p75 LCP/CLS, editorial/rights approval, authenticated Grok asset, validated checkout SKU and founder/QD approval. No live CMS, merchant, email, social, analytics, affiliate or spending changes are authorized.
