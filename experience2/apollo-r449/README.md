# Apollo R449 — first single-CTA research-to-classroom integration (DRAFT STAGING ONLY)

**Foundation:** #150 and draft #158. **Commerce contract:** #818 and #820. **Stacked base:** Apollo R448 (unmerged). Home PR #49 and Claude's owned production/analytics branches are NEVER edited. Grok and Praxxis retain TASK-008 creator ownership.

## What this fixes

R439–R448 produced many valuable individually tested modules, but individual shortcode prototypes do **not** prove an integrated user path. Combining arbitrary cards would duplicate free links, contaminate commercial conversion experiments and complicate source review. This **first assembled, isolated demonstration** reuses only **two** specific checked modules: R448's four-record chronological claim crosswalk and R440's original educator activity. The gallery R447 is explicitly excluded until the previously unverified image catalogue link and potential media-rights clearance are reconciled; it remains its own separate draft. R446 creator-tag registry is also deliberately not loaded until an actual approved Grok post is verified.

The composition provides one and only one link to the existing **free** Apollo investigation. Source documents have four official NASA provenance links and separate disclosures. The educator preview can export a user-initiated `.txt` original activity, with no login, analytics, upload or paid checkout. Both components remain complete without JavaScript. No new JavaScript is shipped by R449; only hashes of inherited scripts are checked. No images, geographic pins, map edges or NASA marks are included.

## Safe installation (only if separately reviewed)

**Not installed anywhere.** Site engineering would copy this as a WordPress-accessible nested staging module **alongside the exact source-controlled R440 and R448 folders**. Install/review the PHP file with release governance, then explicitly opt into staging by defining `FV_R449_ENABLE_STAGING=true` and integer `FV_R449_STAGING_PAGE_ID=<approved preview page id>` in a nonproduction environment. Embed `[fv_apollo_evidence_journey_r449]` only on that staging page. There is no general production shortcode registration. The adapter checks `wp_get_environment_type()`, the exact queried page ID, eight immutable SHA-256 dependency pins, and a ninth CSS pin; any discrepancy yields one free fallback link. For actual staging, separately confirm the adapter `plugins_url()` asset paths work with the chosen WordPress plugin installation layout. A source-only git PR does not install or publish anything.

R440's internal paid-product evidence manifest is itself marked `HOLD_NOT_SELLABLE`: no verified seller, payable SKU, rights clearance, merchant checkout, fulfillment or founder approval. This wrapper does not change that status. NASA source identity is not independent QD editorial approval or NASA endorsement.

## Executed local acceptance / blocked network acceptance

```bash
python experience2/apollo-r449/qa/test_contract.py
python experience2/apollo-r449/qa/browser_qa.py
python experience2/apollo-r449/qa/staging_gate.py
```

`test_contract` deliberately edits a temporary copy of each dependency to prove fail-open behavior and leaves upstream files untouched. Chromium tests run actual PHP-generated HTML through `page.set_content`, with 320/360/390/768/1024/1440/1920 JS-on and JS-off, plus keyboard, touch, forced colors, 2× pixel density and print, screenshots and actual `.txt` download. **These are local tests, not navigated staging, genuine axe or field Core Web Vitals.** This environment rejects `localhost`, `file:` and HTTPS Chrome navigations (`ERR_BLOCKED_BY_ADMINISTRATOR`) and does not contain genuine axe-core. Staging gate therefore intentionally returns `HOLD_NOT_RUN` without founder-approved staging origin and reviewed axe file / matching SHA. Staging must independently test 320–1920px real page navigation, WCAG2.2 AA axe, keyboard, screen-reader, LCP<=2.5s, CLS<=0.1 and actual WordPress asset resolving; 75th-percentile field CWV and INP remain additional production evidence gates.

## One conversion-first pathway

**Verified Grok Apollo documentary** (publication URL and immutable asset ID still unverified) → NASA source crosswalk → free original classroom activity → **one** free Apollo investigation link → optional rights-cleared original paid educator kit **only after** a founder-approved, authenticated SKU is confirmed. The kit is NOT currently for sale. Do not imply the user has agreed to receive emails by downloading a local file.

Hypothesis: A teacher can verify accident findings, inspect chronological boundaries, and try an original exercise before deciding whether later to purchase a distinct educator product. This is a usability/intent hypothesis, not a measured conversion outcome.

**OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER:**

| Offer | Funnel step | Blocker | Change/experiment | Evidence | Owner |
|---|---|---|---|---|---|
| Original teacher kit (proposal only) | verified paid order | seller, SKU, rights, checkout, delivery unverified | withhold paid CTA; validate original product and fulfillment with founder | Commercial HARD HOLD | Founder / Claude |
| Grok video | qualified landing | published asset_id and human-session evidence missing | keep R446 registry empty; demand actual post URL, approved link and permissions | UNKNOWN, zero verified attribution | Grok / Praxxis |
| Original source activity | free research continuation | many prototype links could mislead measurement | combine two pinned modules, assert one next action, export local worksheet | local browser PASS / staging NOT RUN | Apollo / Site QA |
| Confirmed paid purchase | realized net revenue | merchant settlement, refunds, fees and 7/30-day qualified-human denominator absent | Claude to evaluate existing approved analytics/merchant data, no duplicate scripts | net revenue/1,000 sessions NOT COMPUTABLE | Claude / Commerce |

**Release conditions:** prior R417 reconciliation; public Atlas review status; R447 rights/ID issues; exact-head green CI; independent editor QD; authentic staging axe, screen-reader, 320–1920px navigation and performance; commercial inventory and only founder-authorized release. No WordPress write, site/merchant tracking change, creator handoff edit, social posting, email, spending, merge or production deployment.

**NASA primary sources:** [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); [Apollo 1 gallery](https://www.nasa.gov/gallery/apollo-1/); [NASA 2017 tribute announcement](https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/); [2018 flammability retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/); [NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/). Event date is not necessarily publication date; post-fire controlled tests do not identify the first spark. Historical interpretation remains PENDING independent QD.
