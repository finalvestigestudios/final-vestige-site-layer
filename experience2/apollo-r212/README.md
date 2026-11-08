# Apollo Experience 2.0 R212 — one evidence-to-investigation bridge (DRAFT / STAGING HOLD)

Scope: isolated Apollo-only stacked change on R211, not homepage PR #49, core Research Desk PR #158, live WordPress, analytics, affiliates or Grok/Praxxis queue. References #150, #820 and charter #818.

## Visitor-facing change

R211 buried its one free `Read original investigation` CTA after every evidence section and the printed source index. R212 moves **the same single CTA** after the four-source technical crosswalk, before chronology. The crosswalk links to the official NASA Apollo 204 Review Board report and clearly states its limitations. A short accessible bridge makes the free investigation's purpose and no-signup requirement clear. The footer now provides a return-to-bridge anchor, not a second external CTA. No tracking scripts, media, paid buttons, fabricated geolocation or urgency.

This tests a specific **not-yet-activated conversion hypothesis**: in a future verified Grok Apollo documentary campaign, a free original-investigation link after source proof will improve qualified visitors' progression to the article. It cannot establish purchases or realized revenue until a relevant rights-cleared product exists and independently verified orders/refunds/fees can be attributed to consent-safe human sessions. The educator evidence dossier remains an unapproved hypothesis, not an SKU.

## Source and rights limits

- Technical evidence: NASA Apollo 204 Review Board https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; no one ignition source conclusively identified.
- Photo dates/custody retained from R211: https://www.nasa.gov/image-detail/amf-s67-15717/ , https://www.nasa.gov/image-detail/amf-s67-21294/ . Photographs are not proof of the initiating spark; a matching date does not prove the image depicts chamber removal.
- NASA advertising and endorsement restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No embedded images, rights certification, commercial approval, astronaut endorsement or paid offer.

## Deterministic build and browser QA

Requires **the EXACT R211 `dist/`** produced from its pinned input, with `manifest.json` SHA-256 `ee5a10237cca0a57718b435425dfc0969562da957cc1cd6c50e32558423268b4` and manifest-listed file hashes. Example:

```bash
FV_APOLLO_R211_DIST=/path/to/R211/dist python experience2/apollo-r212/build_r212.py
python experience2/apollo-r212/qa/gate_r212.py /tmp/apollo-r212-qa
```

Local PHP CLI shim + actual Playwright Chromium 144 ran twice with 11 contexts each: 320,360,390,768,1440,1920, no-JS, touch, reduced-motion, forced-colors and simulated 200% CSS zoom. Assertions cover focus/keyboard Enter, disclosure, print-expanded answer guide, safe source/CTA links, real local click interception, at-least-44px CTA target, layout overflow, malformed ARIA IDs, duplicate actions, invented geo and false marketing. Nine deliberate unsafe mutations rejected per run. **11/11 screenshot SHA-256 hashes matched across runs**. Browser fixture CTA begins at ~22–29% of page scroll height, not tested against a live-user control cohort. Offline PerformanceObserver LCP 100–344ms where available, CLS zero; **not production CWV**.

No localhost/external browser navigation was successful in this runtime, so native click was intercepted locally solely to verify intent; destination health is **unverified**. No genuine axe-core was installed/executed, no manual NVDA/VoiceOver, no installed WordPress/Assembler, no actual browser zoom or CDN/CSP testing. Hosted exact-head CI and independent QD/founder gates remain outstanding.

## Release gate and owner map

**HOLD.** R198 canonical GitHub-vs-inherited builder blob discrepancy remains unresolved, so full build ancestry is not certified. Do not merge or deploy. Grok owns video script/publishing; Praxxis QA of actual creator IDs; Claude production WP/analytics; founder approval of publishing/paid activation; Apollo lane source-integrity and browser QA. No product, merchant purchase, qualified session attribution, email lead, affiliate sale or net revenue independently verified. Preserve original page and fixed single external CTA until all acceptance gates are passed.
