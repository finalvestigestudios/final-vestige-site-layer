# Apollo Experience 2.0 — R417 photograph/claim provenance integrity

**Status: BUILT, locally fixture-tested, PRODUCTION HARD HOLD. No WordPress staging installation, merge, deployment, paid product activation, analytics or social posting.**

This isolated staging-only shortcode `[fv_ex2_apollo_provenance_r417]` is **not a gallery of licensed photos**. It supplements R411/R414/R415 with NASA-original-caption provenance: what each externally linked photograph actually depicts; when it was taken; and why that image alone **does not prove** the associated historical claim.

## Editorial discovery (November 16, 2026)

The six image-detail URLs in the original #158/R411 ledger resolve to NASA, but **several images are illustrative context rather than direct evidence for the corresponding claim**. Attribution to NASA is not the same as relevance or contemporaneity.

| R411 index | NASA image subject, caption-date | Critical restriction |
|---|---|---|
| 01 | Apollo 1 crew training at LC-34, January 1967 | Training portrait; not a record of fire-hazard circumstances |
| 02 | Spacecraft 012 moved for preparation, **3 January 1967** | Transport image; not cabin oxygen pressure measurement |
| 03 | Crew entering **altitude chamber, 18 October 1966** | Earlier training photo; **not 27 January 1967 accident telemetry** |
| 04 | Apollo 1 tribute and displayed hatch, **24 January 2017** | Fifty-years-later museum photo; not contemporaneous hatch/egress evidence |
| 05 | Fire-damaged command module, **28 January 1967** | Aftermath; cannot positively establish ignition initiator |
| 06 | Redesigned hatch in Apollo 1 tribute, **24 January 2017** | Museum display; not photo of later 102 fire-safety tests |

NASA original caption pages:
- [01](https://www.nasa.gov/image-detail/apollo-1-crew-honored/) · [02](https://www.nasa.gov/image-detail/amf-s67-15717/) · [03](https://www.nasa.gov/image-detail/amf-s66-58038/)
- [04](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/) · [05](https://www.nasa.gov/image-detail/amf-s67-21294/) · [06](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/)

The primary **textual evidence** remains [NASA's Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). [NASA's later flammability testing](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) and [14 March 1968 atmosphere decision](https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/) are a distinct later chronological lane. [NASA's media policy](https://www.nasa.gov/nasa-brand-center/images-and-media/) prohibits misleading endorsement; no media is reproduced here. Source pages, caption dates and relationship labels were visually checked November 16, 2026.

## Implementation and safety

- New files only under `experience2/apollo-r417/`; based on R416 #2796. No PR #49/homepage/Research Desk #158 modifications. No changes to Grok TASK-008.
- Shortcode requires explicit `FV_R417_ENABLED === true`, a positive `FV_R417_STAGING_PAGE_ID`, the `staging` WordPress environment and matching singular page.
- Exact Git blob SHA-1 custody checks pin the original R411 PHP source (`efd0cc38...`), R415 integration PHP (`18d20114...`) and this component's reviewed CSS (`921f50a4...`). Changed/missing dependencies fall back to existing free Apollo investigation.
- Six caption classifications, six visible limitations, six optional native `<details>` disclosures, original NASA text/archive URLs, one existing free investigation CTA. No JavaScript, cookies, analytics, image downloads, commerce, forms or invented geolocations.
- CSS: scoped responsive 320–1920, keyboard focus, touch-friendly native disclosure, print, forced-colors and reduced-motion. Handles multiple shortcode instances with unique IDs.

## Reproduction

From a test checkout with sibling original R411/R415 files at the exact pinned blobs:

```sh
php -l experience2/apollo-r417/staging-provenance-guide.php
php experience2/apollo-r417/qa/render_fixture.php > /tmp/r417.html
python experience2/apollo-r417/qa/test_provenance.py
python experience2/apollo-r417/qa/test_browser.py
```

Local R417 corresponding implementation: 17/17 native Python/PHP contract tests and 15/15 offline Playwright Chromium cases PASS; 11 screenshots across 320–1920 including keyboard, touch, no-JS, enlarged text, forced colors and print. Those tests used a companion local implementation; **the committed PHP file's exact Git blob differs from the local build** and awaits byte-exact re-execution/independent CI. Do not treat the local numbers as exact-GitHub-HEAD CI.

**Unverified:** axe-core (not installed), browser navigation (`ERR_BLOCKED_BY_ADMINISTRATOR` on file URL), navigated LCP/CLS, hosted HTTPS/headers/WordPress environment, manual NVDA/VoiceOver, p75 CWV, actual paid checkout and human-session attribution. No invented numbers.

## Conversion-first bridge and approval owners

**One audience/offer:** history educators arriving from a genuinely published Grok Apollo long-form. Suggested source path: verified posted Grok asset `asset_id` and approved UTM -> this provenance guide -> [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) -> **only after independent product audit** optional original rights-cleared teacher dossier (proposed, NOT a current confirmed purchasable SKU).

**Hypothesis:** labeling contextual versus direct primary evidence decreases misleading trust cues and increases qualified educator progression. This is **not** a validated sales claim. No seller receipt, fulfillment, SKU, refund/fee report or verified matching social asset currently establishes revenue. `net revenue per 1,000 qualified human sessions = NOT COMPUTABLE`.

Owners: Apollo QA owns source/UI gate; QD owns independent editorial/rights/accessibility review; Grok owns video/distribution; Praxxis reviews Grok through existing Drive TASK-008; Claude owns checkout/analytics; founder must explicitly approve any commercial activation and release. Source-of-truth #150, business #818, attribution #820. No paid services or duplicate analytics.
