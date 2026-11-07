# Apollo Experience 2.0 — R198 claim/source custody crosswalk (DRAFT; NOT LIVE)

**Parent:** R197 draft PR #1466 / exact commit `7bb1742262ca842be8df359fbc317f38cf609f34`. **No edits to PR #49, PR #158 or production WordPress.** Source location: `experience2/apollo-r198/` only.

## Change
The R197 research guide navigated to four claims but required visitors to open separate details to find the NASA source. R198 adds a visibly readable, no-JavaScript **claim-to-record crosswalk** beside the guide: four individually labeled finding links, four direct NASA Review Board source links, independent evidence limitations, and a separate NASA S67-21294 aftermath/advertising-rights distinction. 2-column/1-column responsive layout (650px breakpoint); accessible links, print styling and forced-colors handling. The built output is integrity-pinned HTML/CSS/PHP and inherits the optional-JS fail-open mechanism, eight native source disclosures, four chronology events, archival gallery, and one free investigation CTA.

This is *not* evidence of rights-cleared commercial use. NASA Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; photo: https://www.nasa.gov/image-detail/amf-s67-21294/ ; advertising: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Photos are **not** treated as ignition proof. Zero map pins or fabricated relationships.

## Reproduce in an actual checkout
```sh
python -I experience2/apollo-r198/build_r198.py
php -l experience2/apollo-r198/dist/fv-ex2-apollo-r198.php
python -I experience2/apollo-r198/qa/gate_r198.py /tmp/apollo-r198-browser
```
Requires Python 3, bs4, Playwright and local Chromium at `/usr/bin/chromium`. The generated `dist/` is intentionally not committed. Builder determinism is constrained by the SHA-256 manifests of the complete inherited pipeline. Do not run this build to install a WordPress plugin.

## Independently executed local prototype evidence (NOT exact GitHub builder acceptance)
A functionally equivalent local R198 builder and PHP shim were executed; a verbatim copy of the **committed QA script** was executed on its generated output. Local checks: PHP syntax, normal/printed/late rendering, four native claim anchors, eight disclosures and four chronology events passed; real Playwright/Chromium passed **12 contexts / 48 focus journeys**, 320–1920px, no-JS, touch, reduced motion, forced colors and simulated CSS zoom, with no horizontal overflow. Separately **8/8** adversarial source-rights/link/ID mutations were rejected in the expanded local custodian. **12/12** screenshots SHA-256 matched across two independent runs; fixture LCP approximately **108–252ms**, CLS 0. `page.set_content` was necessary: environment blocks localhost and file browser navigation. Those are **offline fixture results**, not field CWV or installed WordPress acceptance.

**Limit:** the committed GitHub `build_r198.py` uses an equivalent source-record data generator, not the byte-identical locally executed builder. The exact committed QA script was tested against equivalent generated output. Exact-HEAD rebuild, exact committed PHP/CSS/HTML hash confirmation, native installed WordPress, genuine axe-core, NVDA/VoiceOver, navigation, CSP/CDN, hosted CI and independent site QA are **BLOCKED / NOT VERIFIED**. Do not merge or deploy on this evidence alone.

## Conversion-first handoff
**Flagship:** Apollo 1, for source-conscious history and education long-form viewers. **Immediate action:** Read original investigation (free). **Product hypothesis:** original classroom evidence dossier; *no existing verified sellable Apollo SKU*, checkout, approved rights or fulfillment, so **no paid CTA**. Grok maintains production/distribution and immutable campaign asset IDs; Praxxis reviews creator facts and rights; Claude owns WP/analytics engineering. No verified published Grok Apollo asset ID, qualified-human-session denominator, Payhip merchant order, affiliate payout, fees/refunds or net revenue. 7/30-day realized revenue per 1,000 qualified human sessions is NOT COMPUTABLE. #150 / #820 / #818 and existing TASK-008 Drive handoff remain governing.

**Hard release hold:** founder approval + independent QA + staging acceptance + source-media and commercial rights. No CMS, tracking, email, social posting, payout, spend, merge or production change.
