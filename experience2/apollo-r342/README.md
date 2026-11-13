# Apollo Experience R342 — direct NASA source custody and chronology precision

**Isolated draft only — not installed, published, merged or endorsed.** Stacked on R341 draft PR #2379; independently tracks Experience #150 and revenue #820/#818. Do not edit homepage PR #49 or Research Desk PR #158.

## Source correction / rendered behavior

1. R339's approximate **23:31:12** marker previously asserted that fire had spread beyond origin by that time. NASA's original Review Board instead says the fire was **not intense until about 23:31:12** according to surviving pressure and temperature measurements. The source text has been corrected; no inferred flame-front position or precise fire-start point is claimed.
2. The **23:31:22.4** telemetry boundary now distinguishes the end of the final voice transmission at **23:31:21.8** from the end of data at approximately **23:31:22.4**, and explicitly warns against a post-telemetry simulated sequence.
3. All six records render **Record custody** and **Evidence limit** in native HTML `details`; five use a NASA-hosted 1967 Board section and the postfire redesign uses a **separately labeled later NASA history**. Links go to the source section, rather than always the generic report index.
4. All original functionality remains: six-point text-first `ChronologyRail`, four link-only contextual NASA photograph cards, responsive scoped styles, keyboard/touch-friendly links, browser-native disclosures, no-JS meaning, unchanged one free investigation CTA. No photography copied, no geo pin or fabricated edge and no new commercial CTA.

See [SOURCE_CUSTODY.md](SOURCE_CUSTODY.md) for actual source URLs, rights boundaries and Grok→evidence→free investigation→separately approved relevant product hypothesis.

## Exact repeatable local QA

Requirements: PHP CLI; Python Playwright; Chromium. From repository root:

```bash
php -l experience2/apollo-r339/chronology-rail.php
php -l experience2/apollo-r340/apollo-accession-gallery.php
python experience2/apollo-r342/qa/source_custody_gate.py
```

The committed QA runner validates source tiers and boundaries, six event times, no invented coordinate/commercial fields, four contextual photo records, one existing editorial CTA, native disclosures and browser overflow in **six actual Chromium scenarios**, including 320px/400% text and JavaScript disabled. It writes two reproducible screenshots and a JSON receipt under `experience2/apollo-r342/QA/` (override with `FV_R342_OUT`). Chromium is local and should never be interpreted as production LCP/CLS or as installed-WordPress acceptance.

A separate **extended local 10-context** Playwright gate also exercises touch, reduced motion, forced colors, two simultaneous instances/unique IDs, fragment navigation, eight adversarial source/rights/commerce/geo mutations, and local browser LCP/CLS observers. The extended runner and generated receipts/screenshots are distributed in the review ZIP, not yet wired to hosted CI. Its LCP values are fixture observations with non-observations retained as null; **not production CWV**.

**Not executed:** real axe-core (no genuine installed library available in the execution environment), independent screen readers, Firefox/WebKit, installed WordPress/Assembler/CDN, actual HTTP CSP, hosted exact-HEAD CI, production Core Web Vitals, final rights/editorial review and merchant checkout acceptance. These are blocking, not passing, gates. Do not replace axe with a fake or count DOM checks as accessibility certification.

## Commercial acceptance / owner contract

One nonintrusive CTA continues to the free Apollo article; **the proposed paid educator kit is not a verified payable SKU**. No merchant conversion, subscribers, campaign attribution, qualified sessions, refund/fee data or realized net revenue were observed. The Grok Apollo asset ID and exact compliant social link remain unverified. Claude/Commerce owns native telemetry and seller-side reconciliation, without duplicate scripts. Founder approval remains required for any live deployment, posting, spending or commerce changes.

R342 is research/staging-only; keep all merge/release gates **HARD HOLD** pending independent review.
