# Apollo R229 — rendered accessibility and conversion-path acceptance

**Status: BUILT + exact GitHub source / local browser QA PASS / DRAFT / STAGING HOLD / NOT LIVE.** This change adds a standalone QA lane only; it does not edit R228's generated Apollo HTML, CSS, PHP adapter, WordPress, homepage PR #49, or Research Desk #158.

## Why this exists

R228 improved 14 source-navigation hit targets. R229 verifies the *whole rendered reading surface*: link names and destinations, duplicate IDs, fragment paths, ARIA references, heading progression, skip-link presence, source disclosures, empty-image alt attributes, unexpected geographic attributes, unexpected scripts, a **single visible 44px+ free-investigation CTA**, and no horizontal overflow.

A genuine Chromium computed-style audit walks painted text nodes and alpha-composites translucent panel backgrounds from outermost ancestor to element. This avoids misleading nearest-background contrast tests (gold translucent panels otherwise appear to have ~1.1:1 contrast). It checks 4.5:1 for ordinary text, 3:1 for large text. This is a computed-color audit of this fixture, **not full WCAG 2.2 AA certification**, and does not replace visual/axe/assistive-tech review.

## Exact input and reproducible run

- Parent draft R228 #1678 at `4c7d903f0ac8e4a310fb97b3aed89edb60c3b426`.
- Input: verified R228 `generated-r228/` bundle from the prior staging evidence package. Manifest SHA-256 **`28f1427da6d096c801927ac8e1e8dd8a53f14ff3f6fcb014089ada2bdd662413`**; all member file hashes are independently checked before browser startup.
- Runtime: Python 3 + Playwright + local Chromium (executable `/usr/bin/chromium`), no network or paid dependencies.
- Command: `python experience2/apollo-r229/qa/r229_gate.py --dist /path/to/generated-r228 --out /tmp/apollo-r229-qa`.
- Two independent local executions: **10 contexts each**, five widths (320/390/768/1440/1920px) × JavaScript on/off, mobile touch, keyboard disclosure, 320 reduced-motion, 768 forced-colors, Chromium Accessibility.getFullAXTree roles, no outbound requests, no horizontal overflow. **389 painted text nodes sampled per context; observed minimum computed ratio 7.69:1 in ordinary colors and 13.99:1 in forced colors.**
- Nine adversarial in-memory modifications **all detected**: duplicate ID, broken fragment, hidden CTA, blank CTA, unreadable text, missing H1, script injection, invented geo coordinate, and image without alt.
- Screenshot reproducibility: **10/10 hashes identical** across the two runs. Stable QA receipt SHA-256 **`e6a59b38238d9abd58bd1e590de8c0fef7fd167c9b72aea152c10b479546496f`**.
- The acceptance script executed locally must match the GitHub blob SHA of `r229_gate.py` before independent release review.

## Truthful limitations

Playwright `page.set_content` tests the exact generated component, **not installed WordPress/Assembler**, not HTTP navigation (local navigation is administrator-blocked), not host theme cascading, not third-party scripts. **Genuine axe-core was unavailable and NOT executed.** Native Chromium accessibility tree is not an axe substitute. NVDA/VoiceOver, actual desktop zoom, independent editorial/rights/QD, hosted exact-head CI, field LCP/CLS and founder authorization are outstanding. R198 source ancestry is still unresolved. Never present local test data as production Core Web Vitals.

## Founder conversion gate — one truthful next step

**One relevant action:** “Read original investigation” links to the existing free Apollo history article. No unrelated Mini Museum or paid affiliate insertion into Apollo's historical evidence. Apollo educator dossier remains a **product hypothesis**, not a rights-cleared SKU, verified checkout, or confirmed paid order. Before any landing-to-purchase activation, founder and Claude must verify product ownership/rights, delivered files, price/refunds, merchant acceptance and qualified visitor-to-order attribution. Grok owns creator production/posting; Praxxis owns creator crosswalk; the Apollo lane owns only evidence-to-reading integration.

Measurement chain: verified Grok platform URL/asset_id/UTM → qualified-human Atlas sessions → original investigation click → separately confirmed lead, if applicable → independently confirmed paid purchase/affiliate settlement → fees/refunds → realized net revenue per 1,000 qualified sessions (7/30-day cohorts). None of the paid-outcome measurements are available in this run; clicks are not sales. NASA factual source linking is not commercial-use clearance, and NASA's advertising guidelines bar implied endorsements.

**Release gate: HARD HOLD.** No merge, production, WordPress, paid spend, audience posting, script installation or activation authorized.

References: [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [Priority #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [Business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818), [NASA Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).
