# Apollo R430 — Evidence-to-classroom reasoning lab (DRAFT; staging only)

**Issue:** [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) · **Business charter:** [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818) · **Revenue/attribution:** [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). **Proposed flagship:** Apollo 1 (1967), the full free investigation at <https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/>.

## Why this exists

A documentary viewer who wants to teach or independently verify the case should have something *useful*, not just an animation or another attention loop. R430 wraps the **actual unchanged R429 evidence rail**, then adds three original, printable primary-source reasoning exercises (ground-test oxygen risk; likely electrical arc vs unproven exact spark; 102 later deliberate flammability ignitions vs initial accident). Each question links to the governing NASA document, includes a free-text answer box and a native instructor explanation drawer. Entries stay entirely on the viewer's device and are **not stored or sent**. The inherited article link is the **one relevant next action**, not an invented paid offer or a new signup form. There are no geo pins or speculative connections.

## Source custody and NASA usage boundaries

- **1967 primary evidence:** NASA, *Report of the Apollo 204 Review Board* — <https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/>. The January 27 fire occurred during a ground test. The board found a 100% oxygen atmosphere at 16.7 psia, considerable combustibles, a probable electrical arc, and **no conclusively identified single ignition source**. The report's date and event date are not image-capture dates.
- **2018 retrospective:** NASA Johnson Space Center, John Uri, Feb 14, 2018, *50 Years Ago: Apollo Flammability Tests* — <https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/>. The 102 deliberate CM Boilerplate 1224 ignitions were carried out **December 1967–February 1968** after the original fire. They cannot identify its ignition spark.
- No copied archival photo or NASA mark. Source links are contextual citations, **not** evidence of licensed commercial reuse or NASA endorsement. Consult <https://www.nasa.gov/nasa-brand-center/> before any future gallery use or educator-product resale.

### Actual upstream code, not a synthetic reinterpretation

R430 only renders if these **two exact reviewed R429 Git blob identities** match the files alongside it:

- `experience2/apollo-r429/staging-attribution-bridge.php`: `c604bccf9873688ec1d9b64187d1a9a7fdcf89ac`
- `experience2/apollo-r429/assets/bridge.css`: `15942f8ef27d82695c8d2af8bdc8a807396da33e`

Missing, altered or symlinked files trigger a plain, functional **free-investigation fallback**. An already-global unknown R429 renderer also fails safely; this prevents accidentally trusting a differently loaded version. Source integrity is checked for each render; only successful first loading is reused for later instances. The original R429 logic, CSS, UTM allowlist, chronology and one CTA per instance are preserved unchanged. **Do not silently lift these SHA pins on upstream changes:** audit and revise them in a dedicated reviewed PR.

## Staging integration (not performed)

1. After QA/founder review, place R430 adjacent to R429 inside an authorized *staging-only* WordPress plugin directory. Install no files on public WordPress within this task.
2. Define `FV_R430_ENABLED=true` and exact positive integer `FV_R430_STAGING_PAGE_ID` **only in approved staging config**; install shortcode `[fv_apollo_educator_lab_r430]` only on that page. Other environments/pages get the free article fallback.
3. The `wp_enqueue_scripts` hook loads immutable R429 CSS followed by R430 CSS if all source checks pass. No JavaScript, cookies, storage, user-submitted email, merchant controls or measurement vendors are introduced.
4. Do **not** activate R429 itself simultaneously on the same request; R430 deliberately treats already-global R429 functions as a source-provenance conflict and falls back.

## Reproducible tests and release barriers

```sh
php -l staging-educator-case-lab.php
python qa/test_contract.py
python qa/browser_qa.py
python qa/package_evidence.py
```

Contract tests execute the real PHP using independently copied source files and test environment misconfiguration, tampered blobs, symlink paths, duplicate instances and one-CTA custody. Browser tests use actual PHP-generated DOM in real Chromium at 320/360/390/768/1024/1440/1920, keyboard, touch, no-JavaScript, forced-colors, reduced-motion, 200% root text and print. **They use `page.set_content`, not real HTTP navigation, field data or genuine axe-core.** Reproducible screenshots are produced only for the tested offline fixture.

A separate **read-only** `qa/staging_acceptance.py` requires an *exact founder-approved HTTPS staging host*, a locally reviewed SHA-256-pinned axe-core bundle, real browser `page.goto`, actual component checks, lab LCP/CLS, axe WCAG 2.2 AA rule tags and no-JS checks. Without all inputs it returns **HOLD**. Even a passing lab is not p75 field CWV or a screen-reader audit.

**HARD HOLD**: R417 archive/source mismatch, independent QD exact-head review, installed Assembler/WordPress staging acceptance, genuine axe and navigated LCP/CLS, media rights for any future gallery, official commercial SKU/checkout/fulfillment validation, founder approval. No merge/deployment/WordPress write/post/email/spend.

## OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Change and proof | Owner |
| --- | --- | --- | --- | --- |
| *Proposed* original Apollo educator evidence dossier | verified paid order | No authenticated payable rights-cleared SKU / checkout / settlement | Withhold paid CTA; audit existing FV inventory and merchant proof first | Founder / Claude / Commerce |
| Grok-approved Apollo long-form video | qualified landing | No independently verified published asset ID, matching URL, or unique human sessions | Maintain TASK-008 UTM metadata and do not assert published video or attributable sessions | Grok / Praxxis / Claude |
| Evidence trail → free Apollo article | documented relevant CTA | Staging uninstalled | Preserve R429's single, source-appropriate CTA; offline tests only | Apollo QA / QD |
| Original educational value → eventual paid casefile | qualified high-intent buyer | No educator demand validation or approved offer | Test free exercise; interview educators only after founder authorizes outreach; do not sell or collect private answers | Founder / Content / Commerce |
| Merchant-confirmed purchase → realized revenue | 7/30d cohorts | No independently confirmed paid orders, fees, refunds, or qualified-human denominator | Net revenue / 1,000 qualified sessions **NOT COMPUTABLE**; clicks/leads are not sales | Claude / Commerce |

One proposed pathway: **Grok-approved, actually published Apollo long-form → source-backed, free worksheet → existing full free Apollo investigation → separately approved, rights-cleared paid original educator casefile.** No educator product, affiliate link, signup form, or payment control is invented or activated. Grok remains creator/distribution owner, Praxxis external review, Claude core site/analytics, founder release/spend authority.
