# Apollo Evidence Atlas R300 — repeated-instance accessible region names

**STAGING / HARD HOLD.** Parent issue #150, conversion governance #820 / charter #818. Stack on Apollo R299 draft #2132. Homepage PR #49 and Research Desk PR #158 are not edited.

## Defect and fix

R297/R298 distinguished five inner landmarks and native source disclosure summaries across repeated shortcode instances, but the outer named section remained an indistinguishable region labeled “What the record establishes” for every instance. Unique DOM IDs do not make accessible region names unique.

R300 appends a screen-reader-readable instance marker to the H2 that actually labels the region. The visible heading is unchanged, and without CSS the context is visible (fail open). No JavaScript, analytics, WordPress write, images, maps, NASA link changes, edited historical assertions, or new CTA. The one existing free investigation continuation remains after the 3 evidence plates.

## QA and reproduction

From experience2, run PHP syntax, inherited R295/R296 source custody, R296 stylesheet/cache, R296 and R298 browser regressions, R299 CTA placement, and the new apollo-r300/qa/region_landmark_contract.py. The R300 executable browser test requires PHP, Python 3, playwright, Chromium and pypdf. It renders the actual PHP using the existing local fixture and source-controlled CSS, tests 320/390/768/1440/1920 widths with JavaScript on/off, two component instances, Chromium CDP Accessibility.getFullAXTree, unique names and IDs, keyboard native disclosures, deep-link focus, no horizontal overflow, reduced motion, touch, one free investigation link and a negative control that deliberately reproduces duplicate landmark names by removing the instance suffix.

Local execution: 10/10 browser contexts, 20 distinguishable outer regions, 40 keyboard disclosure operations, 20 source-target focus checks, 10/10 negative controls and CSS-fail-open PASS. Five full-page PNG screenshots and a print PDF (13 pages, 70 link annotations) are generated. Two consecutive complete executions produced identical PNG/PDF digests after normalizing the printed PDF metadata. Offline PerformanceObserver measurements are diagnostic only, not production or field Core Web Vitals.

Build a deterministic evidence archive with apollo-r300/build_archive.py after running the new test. This produces an evidence manifest with SHA-256 for every payload and fixed ZIP timestamps. The binary QA artifacts remain in the run archive rather than being committed as images.

## Official evidence / rights

Original NASA Review Board narrative: https://www.nasa.gov/history/Apollo204/narr.html . This primary source distinguishes Jan. 27, 1967 oral authority from Jan. 28 convening. NASA's later summary uses differing establishment language; not independent eyewitness corroboration. NASA website linking and brand limitations: https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No new NASA photos, astronaut likenesses, insignia or commercial endorsements.

## Conversion and ownership

**OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:** Prospective Apollo educator evidence kit (not an approved sellable product) → verified Grok Apollo film to evidence atlas to free investigation and only later an approved relevant offer → no verified film asset ID, saleable SKU, merchant acceptance or paid-order reconciliation; indistinguishable accessible regions → R300 unique accessible region naming → local browser PASS, paid conversions/net revenue NOT COMPUTABLE → Apollo component owner; Grok creator and Praxxis external review; Claude production analytics and merchant; founder offer and release approval.

No affiliate clicks, leads, followers or social views are sales. Commercial success metric remains verified realized net revenue per 1,000 qualified-human landing sessions with 7/30-day cohorts once actual orders, fees, refunds and attribution exist.

## Release gate

HARD HOLD: genuine axe-core (unavailable), independent NVDA/VoiceOver, actual WordPress/Assembler and synced-block acceptance, real HTTP/CSP Chromium navigation (administrator blocked), exact-head hosted CI, field p75 LCP/CLS/INP, editorial/source/rights acceptance and founder authorization. No PR merge, production or CMS writes, Grok content posting, emails, paid vendor use or merchant activation. The Chromium PDF is untagged and not an accessibility certification.
