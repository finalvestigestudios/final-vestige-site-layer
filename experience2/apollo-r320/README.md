# Apollo R320 — late dynamic-shortcode asset parity (staging only)

## What changed
Issue #150 / conversion coordination #820 / founder charter #818. Base R319 draft PR #2253. This staging-only change fixes a concrete render-lifecycle gap: a shortcode added by dynamic/synced WordPress blocks may not be visible during the normal `wp_enqueue_scripts` preflight. Previously the CSS body fallback rendered but the optional first-party campaign-continuation JS was never scheduled. R320 adds a bounded footer enqueue from the verified render path, preserving WordPress handle de-duplication. It refuses admin, feed and already-completed footer contexts and never emits inline scripts.

**No live WordPress install, rollout, source-media embedding, merchant call, cookie, analytics tag, email, posting, or spending.** PHP remains query-invariant for shared-cache safety; the sole free investigation link works when JS is missing. The R317 validator only accepts restricted campaign labels; those labels are NOT verified sessions or purchases.

## Reproduce locally (requires PHP, Node, Python Playwright, Chromium)
```sh
php -l experience2/apollo-r281/apollo-source-experience.php
php -l experience2/apollo-r320/qa/wp_late_shortcodes.php
node --check experience2/apollo-r281/assets/apollo-cache-continuation.js
python experience2/apollo-r320/qa/late_shortcode_gate.py
```
The gate uses six separate actual PHP lifecycle cases: static preflight hit; dynamic shortcode first seen after head; already queued handle; footer already fired; admin; feed. A true R319 PHP source negative control demonstrates the original late-shortcode miss. Offline Chromium then checks 320, 360, 390, 768, 1024, 1440, 1920px × JS / no-JS / forced-colors, keyboard menu campaign continuity, first/second instance isolation, source navigation and focus, reduced motion and layout overflow. The gate writes four deterministic-named screenshots and a JSON receipt in `QA/` (runtime QA images are not committed). It does not need a database, network, vendor, or production.

QA source identities (Git blobs):
- Pre-R320 Apollo PHP: `9ff32d45b7e957e1d25724ab5fc55c467aaa55e2`.
- R320 Apollo PHP: `854dc28b1596813c682e053f40941bbaafa9e444`.
- Preserved campaign JS: `a3c858b51005495ebebb326086badc155c1b7e5a`.

## Source, licensing and editorial boundaries
Original NASA Apollo 204 Review Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . It identifies the **most probable** initiator but not a conclusively established specific ignition source. NASA's advertising guidelines: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ explicitly forbid implied agency endorsement; the four contextual NASA photo records remain **links and metadata only, not rights clearance**. Neither this change nor the QA adds photo assets, speculative map pins, geo edges, claims, or paid links.

## Conversion-first proposed pathway and hard gates
**Grok actual published Apollo film (asset ID and landing destination unverified)** → this Atlas and original NASA source custody → one free Apollo investigation CTA → separately reviewed, genuinely payable and rights-cleared offer, **only after merchant/founder approval**. Hypothesis: reliable mobile evidence-to-investigation continuity reduces qualified-session loss; there is **no measured uplift**. Grok owns content/posting; Praxxis independently reviews; Claude owns deployed analytics and the paid funnel.

**Release HARD HOLD:** installed Assembler/WordPress native shortcode, synced block, footer hook and cache acceptance; browser HTTP/CSP; genuine axe-core and independent screen readers; production LCP/CLS/INP; NASA rights/editorial review; Grok published asset and channel mapping; consent; payable merchant/affiliate acceptance and confirmed net-revenue reconciliation; hosted CI/QD and founder approval. This PHP simulation and offline Playwright are NOT installed WordPress or production performance evidence. Never label CTA opens, signup clicks or UTM labels as orders.

Do not edit homepage PR #49, Research Desk PR #158, or Grok/Praxxis TASK-008. No deployment authorized.
