# Apollo R310 — source/media catalogue semantics (staging; NOT LIVE)

Source-of-truth: [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [business #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stacked **only** on R309 draft #2196; independent Research Desk PR #158 and frozen homepage PR #49 untouched.

## Correctness defect and repair

R309's new, link-only four-record NASA photo disclosure was appended **inside** a three-entry documentary-source `<ul>`. A `<details>` is not a valid direct child of that list; the fourth non-`<li>` child could distort screen-reader list navigation and cause source-card semantics to vary by parser.

R310 closes the three-source `<ul>` **before** rendering the independent `<details>`, then renders the unchanged rights-boundary paragraph as a sibling. The source list now has precisely three direct `<li>` children; the optional contextual media list is separately labeled and has four `<li>` children. No media are embedded, no image reuse is licensed, no contextual photograph is promoted as fire-cause proof; the remaining two unverified Research Desk candidates stay withheld. No change to historical text, NASA endpoints, campaign validation, single editorial continuation, pricing or analytics.

## Run source-controlled gate

```sh
python experience2/apollo-r310/qa/source_controlled_gate.py
```

Uses actual PHP shortcode output and 12 offline Playwright Chromium contexts (320,360,390,768,1440,1920px × JS on/off), native keyboard/touch disclosures, source focus, forced-colors/reduced-motion, cross-instance segregation, three negative controls and zero false purchase claims. Expanded reviewer QA in deterministic founder evidence package adds Chromium accessibility tree, five negative controls, no-CSS fallback, screenshot capture, print PDF and **offline-only** LCP/CLS observations. **Neither suite performs actual axe-core, screen-reader, installed WordPress, HTTP/CSP or field CWV acceptance.**

## Conversion pathway and release

One audience: history teachers / evidence-led documentary viewers. Proposed offer: original rights-cleared Apollo evidence teaching kit **not an authenticated payable FV SKU**. Correct journey: Grok-approved Apollo film with verifiable asset ID → cited NASA Evidence Atlas → **one free Apollo investigation** → only later, a founder-approved relevant verified product with functional checkout. Media/source clicks remain noncommercial. Grok/Praxxis own creator evidence; Claude owns analytics and merchant settlement; Founder owns purchase offer, release and posting approvals. No qualified-human denominator, merchant orders, refunds, fees or net revenue was verified; net revenue/1,000 qualified humans is NOT COMPUTABLE.

**Additional major release gate:** R308 server-rendered campaign propagation varies by URL query. A full-page cache configured to ignore UTMs *could* replay one viewer's campaign labels to another; this is an unverified risk, not a finding about the actual WordPress CDN. Validate cache key/no-store behavior or default-off continuity before any deployment. One canonical first-party metrics owner; no duplicate scripts.

**HARD HOLD:** genuine axe-core, independent NVDA/VoiceOver, installed WP/Assembler and reusable-block acceptance, real browser HTTP/CSP, production CWV, NASA/likeness/editorial media rights, actual Grok asset_id, cache behavior, checkout/paid order evidence, hosted exact-SHA CI and founder approval outstanding. No production deployment, PR #49 or PR #158 modification, WordPress write, social post, merchant activation, email or spending.
