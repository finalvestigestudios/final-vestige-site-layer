# Apollo 1 Experience 2.0 — R418 source-specific chronology bridge

**STAGING CANDIDATE / PRODUCTION HARD HOLD.** All new files under `experience2/apollo-r418/`; based on R417 PR #2803. Do not modify or merge frozen homepage PR #49, lead homepage branches, Research Desk PR #158, WordPress, Grok/Praxxis TASK-008 or analytics. No paid products, social posting, external tracking or NASA media in this component.

## Specific R417→R418 correction

R415 ChronologyRail links both **Dec 1967–Feb 1968 deliberate fire-safety tests** and **March 14, 1968 atmosphere decision** to "Related evidence 06," while source card 06's NASA image is a **January 24, 2017 exhibit/tribute photograph**. That is an unproven visual-to-event relationship even though its adjacent NASA textual publication is relevant. R417 correctly classified the photograph. R418 makes the distinction explicit in a separate, **opt-in** chronology shortcode instead of silently modifying R415 or rewriting evidence records.

`[fv_ex2_apollo_chronology_r418]` uses three source-specific NASA text links with no inferred photograph/card edge. Each event shows its evidence limit **before any interaction**. Native details show the photo classification, and remain available without JavaScript. Exactly one nonintrusive CTA points to the existing free Apollo 1 investigation. The guide has no commercialization, forms, scripts, images, location pins, third-party dependencies or sales claims.

## NASA primary/reference sources and rights

1. [Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — concludes no single ignition source conclusively identified, electrical arc most probable; cabin was oxygen-rich.
2. [NASA, 50 Years Ago: Apollo Flammability Tests](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) — **102** deliberate Command Module ignitions **Dec 1967–Feb 1968**, later than the accident.
3. [NASA, Mixed-Gas Atmosphere Decision](https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/) — **Mar 14, 1968** later decision.
4. [NASA agency branding and imagery terms](https://www.nasa.gov/nasa-brand-center/images-and-media/) — original NASA assets require asset-by-asset rights and non-endorsement review; this patch embeds no NASA media or astronauts' likenesses.

Sources 01–06 and their NASA image URLs remain owned by original PR #158 and R411; R418 does not relabel photographs as direct proof or invent geospatial coordinates. Evidence language is original authored paraphrase, not copied NASA text. All archival source URLs point to NASA.

## Execution, tests, and limitations

- `python qa/test_contract.py` — native PHP source, exact upstream SHA, 11 semantic and anti-commerce tests, negative WordPress context and mutated CSS fail-open.
- `python qa/test_release_gate.py` — hostile/missing release-proof tests.
- `python qa/test_browser.py` — real Chromium **offline** HTML produced by actual PHP fixture. Responsive **320, 360, 390, 768, 1024, 1440, 1920**, touch, keyboard, JS-disabled native disclosure, 400% enlarged root font, reduced motion, forced colors, print, accessibility-tree inspection and screenshots. **Offline fixture, not genuine navigated WordPress staging.**
- `python qa/release_gate.py` — exits code 2 / HARD HOLD until actual installed WordPress, genuine axe-core, navigated LCP/CLS, screenreader/keyboard review, exact-head CI, QD and founder release checks are independently substantiated. Self-attested JSON will never independently authorize release.

Build artifact: `QA/Apollo_R418_Local_Evidence.zip` (deterministic, no timestamps/private data; generated locally; not committed). QA screenshots are illustrative of **offline** markup, not live FV.

## Conversion-first contract

**High-intent audience:** history/social studies educators and careful historical-investigation readers from a *verified* Grok Apollo long-form asset (publishing not verified). **One relevant next step:** free Apollo 1 investigation at the extant URL. A rights-cleared original educator classroom evidence/lesson kit could be considered **only after demand validation, approved purchasable SKU, license/fulfillment review and founder release**. Never add a paid CTA to this historical timeline before that proof exists.

**Priority:** OFFER (original educator dossier; UNSELLABLE/UNVERIFIED) → FUNNEL STEP (Grok tagged asset → free source experience → investigation → optional verified offer) → BLOCKER (no published asset/qualified sessions, verified merchant SKU, confirmed sales, fees/refunds) → CHANGE (separate source chronology from later photographs, keep one free relevant CTA) → QA (offline PHP/browser PASS, real staging/axe/LCP/CLS HOLD) → OWNERS (Apollo QA / Claude site & commercial engineering / Grok creator / Praxxis creator QA / founder release). 

Do not claim visits, signups, checkout starts, affiliate clicks or paid sales from offline fixtures. Revenue per 1,000 qualified human sessions, paid conversion, and 7/30-day cohorts are **not computable** from this artifact. #150 → #820 → #818; no queue changes to TASK-008.
