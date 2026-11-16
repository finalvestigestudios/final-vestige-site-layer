# Apollo Experience 2.0 — R408: Curated Evidence Atlas, no fabricated geography

**DRAFT / STAGING ONLY / PRODUCTION HARD HOLD.** This new directory is independent of frozen homepage PR #49 and original Research Desk PR #158. The companion to R407 PR #2736 adds a no-geospatial, six-question source navigator with native `SourceDrawer` disclosures and optional keyboard/touch classification filters. This does not represent a deployed WordPress integration or an approved redesign.

## Implementation and dependencies

- `staging-atlas.php` defines `[fv_ex2_evidence_atlas_r408]` and requires **both** `FV_R408_ENABLED === true` and matching `FV_R408_STAGING_PAGE_ID` on WordPress `staging`. It also requires source-controlled R407 shortcode `[fv_ex2_research_desk_r407]` to be authorized and its reviewed source dependencies to have passed R407 checks. Inactive/missing/incorrect assets lead to a plain public free-investigation link—not a broken atlas or a purchase solicitation. R408 pins the exact Git blob identities of both proposed CSS/JS assets and refuses missing or altered bytes. It does not write options, post content, files, user data or analytics.
- `fv_r408_extract_parent_instance()` verifies R407's unique six-record anchor contract and its **single free article CTA** before assembling the Atlas + Chronicle + Desk. Repeated shortcodes produce noncolliding IDs. Source links are to NASA's report and later testing retrospective; no images/logos/embedded assets or commercial offer links are introduced.
- **Evidence Atlas** is intentionally a curated **question index**, not a geolocated map: no map pins, numerical positional data, simulations, unsupported connections, or claims about pinpointing the original ignition. Six questions follow record titles in PR #158 exactly. No editorial claim is inferred from a map edge.
- **SourceDrawer** uses `<details><summary>`: complete limitation and source link with JavaScript unavailable. The optional JS allows All / Conditions / Sequence / Investigation / Aftermath filters, sets `aria-pressed`, updates a live count, and fails open if markup or classification is invalid. It does not log clicks, set cookies, or phone home. ChronologyRail and the underlying R407 source desk remain native HTML and unchanged.
- The only downstream content CTA is the original [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) **inside** R407. No new sales CTA until founder proves an appropriate rights-cleared, working educator product checkout/fulfillment or verified partner offer. Grok retains video/distribution; Praxxis reviews creator work; Claude owns checkout/measurement engineering.

## Primary source and rights boundaries

- Original [1967 Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): an ignition source was not conclusively identified. Do **not** turn possible sites/wiring into an asserted proven cause.
- [NASA history retrospective on later flammability tests](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/): 102 deliberate Command Module ignitions took place **December 1967–February 1968**, not during the January 27 accident. The later testing is not a retrospective ignition-site identifier.
- [NASA media-use](https://www.nasa.gov/nasa-brand-center/images-and-media/) and [NASA brand rules](https://www.nasa.gov/nasa-brand-center/): links to source material do not mean NASA endorses or has reviewed Final Vestige, an AI-authored explanation or a product. No NASA image/insignia/person likeness is included, and no implied NASA partnership or "NASA approved" product language is allowed.
- Source cards and original PR #158 ledger are independently authored presentation. An eventual commercial educator kit requires rights/asset audit and founder signoff; free NASA documents themselves are not marketed as proprietary merchandise.

## Reproducible local QA

```sh
php -l staging-atlas.php
php qa/test_php.php
python qa/test_browser.py
python qa/package.py
sha256sum QA/Apollo_R408_Local_Evidence.zip
```

- **30/30 PHP structural and adversarial checks PASS**: staging/page gate, immutable six-record targets, duplicated-instance isolation, native disclosures, original free CTA and source/geo boundaries, fail-open fallback; missing or modified R408 CSS/JS are rejected. PHP test uses a mocked parent shortcode and does **not** exercise original NASA HTML or installed WordPress.
- **7/7 Playwright Chromium browser test methods PASS**: genuine system Chromium executes the proposed CSS+JS against a **PHP-rendered synthetic** six-record source stub. Functional category filters and `aria-pressed`, keyboard Enter, touch, native disclosures, no-JS completeness, malformed-data fail-open and absent commerce/geo assets are exercised. **9 screenshot contexts** spanning 320, 390, 768, 1440 and 1920px, no-JS, touch, forced colors, reduced motion, and root font 4x; **0 horizontal overflow in local fixtures**.
- No axe-core installed. Browser administration policy blocks all `page.goto`, even localhost or intercepted HTTPS; `page.set_content` is **not** a navigated page and does not yield production-valid LCP/CLS or real HTTP/CSP. Metrics are explicitly `null` in results. Native browser zoom, VoiceOver/NVDA, exact NASA original template, deployed Assembler/WordPress, independent QD and exact-head hosted CI were **not run**.
- `qa/package.py` creates a fixed timestamp, sorted ZIP and SHA-256 manifest with reproducible rebuilds.

## Founder conversion mandate / release gate

One proposal: Grok-owned (unverified posted) Apollo documentary → **source-attributed curated Atlas** → chronology + Research Desk → one free Apollo article CTA → future separately authorized educator dossier. Conversion hypothesis: question-oriented navigation makes source inspection and the one appropriate free article CTA easier without interrupting evidence with commerce. This is **not proof of lead lift or paid conversion**. The critical next business gate is an actual rights-cleared, merchant-verified buyable offer; no product CTA should appear until then.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Educator kit | Confirmed paid order | No verified rights-cleared payable SKU, checkout, fulfillment or refund process | Withhold product CTA | **HOLD**, no paid evidence | Founder / Claude |
| Grok Apollo long-form | Qualified attributable landing | Posted asset ID, link, UTMs, consented first-party attribution unverified | Draft matching site path only | **UNKNOWN**, no observed sessions | Grok / Praxxis |
| Curated Atlas | Free research CTA | Need a reliable source-aware entry with no fabricated map | R408 six-question native gallery | **PASS local stub; HOLD actual staging** | Apollo QA / QD |
| Merchant-confirmed orders | Realized net revenue / 1000 qualified sessions | 7/30-day denominators, paid orders, fees, refunds missing | No custom tracking installation | **NOT COMPUTABLE** | Claude / Commerce |

**Release remains HARD HOLD** for real original R407/R158 package assembly, installed WordPress/Assembler, genuine axe-core, actual HTTP/CSP/asset delivery, browser-navigation LCP/CLS/INP, screen-reader/native zoom, independent QD and founder approval. No merge, production settings/content write, tracking installation, paid service, email, merchant activation or social publication is authorized.

Coordination: [Apollo Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and [business issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter #818. Grok/Praxxis Drive TASK-008 remains unchanged.
