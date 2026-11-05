# Apollo Experience 2.0 R135 — deterministic evidence acceptance and conversion-first review
**Status:** BUILT / STAGING HOLD. No production approval, merge, merchant verification, or publication.

**Scope:** separate Apollo/Research Desk branch stacked on the R134 draft branch; **do not** modify frozen homepage PR #49, Research Desk PR #158, Claude's production engineering, Grok's queue, live WordPress, analytics or Payhip.

## Exact implemented changes
- Strengthened the R134 **real-navigation** Playwright acceptance runner, without substituting `page.setContent`: build the actual R133 Research Desk from committed source *twice* in separate directories. Compare both HTML byte-for-byte, compare full manifests, verify the manifest's SHA-256 matches the served HTML, and REFUSE nondeterministic builds.
- At viewport widths **320, 360, 390, 768, 1440, 1920**, verify six unique NASA image-detail targets, source-link `noopener noreferrer`, document language, one H1, visible search clear control, zero embedded uncleared media, and no cookie/local/session storage mutations. Existing no-horizontal-overflow, page-error, network, LCP/CLS and screenshot checks remain.
- At **390 touch** and **390/1440 keyboard**, assert actual clear-button touch reset and Tab navigation to the reset control before click; existing Escape, focus restoration, search and zero-result checks remain.
- In an actual **no-JS 390** page, capture a full-page screenshot, emulate print media, verify six record cards and source links remain printable, and generate a printable PDF checksum artifact. A print PDF still needs human visual QA before release.
- Native Node test file verifies deterministic dual-build, exact source links, no-JS records, existing Apollo free worksheet CTA, explicit commercial hold, local HTTP headers/path isolation, and that the browser runner includes actual interaction/performance/axe checks.

## Provenance and rights boundaries
The Review Board is the technical source of record:
https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/

The six photographs are **visual records**, not fire telemetry. Their public NASA source-page metadata can be documented, but it is **not** specific commercial-use clearance; source-linked-only presentation remains mandatory. No archive image is embedded here. No speculative geospatial pins or relationship edges. Crew image identification `S67-19766` remains provisional. The 2017 hatch exhibits remain explicitly retrospective. NASA's advertising/media guidance bars implied agency endorsement and requires special care with personnel likenesses and protected identifiers:
https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

## Single controlled reader-to-product hypothesis
**Audience:** grades 6–9 teachers and homeschool educators who arrived after a future Grok Apollo 1 long-form video. **Current unintrusive next action:** the existing free, no-signup Apollo source-analysis exercise on the investigation page. The user sees evidence limitations and source proof before using the worksheet. **Proposed paid successor:** an original teacher-ready investigation casefile (lesson, differentiated student sheets, answer key, rubric, rights manifest). **NOT VERIFIED, NOT LISTED, NOT FOR SALE** through this PR; no paid CTA is added.

**Offer → funnel → blocker → experiment → evidence → owner**
1. **Proposed classroom casefile → merchant purchase →** no verifiable live Apollo casefile, fulfillment/refund record or approved price → audit actual Payhip SKU and rights first → **BLOCKED** → Claude/Growth + founder.
2. **Grok YouTube asset → Apollo evidence → free worksheet →** risk of inaccessible or altered source route → deterministic dual-build / browser acceptance checks → **BUILT, source syntax checked; real browser not executed** → Apollo owner.
3. **Worksheet → relevant product (after approval) →** absent verified matching offer and photo-specific rights approval → do not insert checkout or affiliate link; test separate educator demand and merchant fulfillment → **BLOCKED / NO CHANGE** → Founder/Claude.
4. **Confirmed paid order → realized net revenue →** no campaign-linked merchant order/refund/fee evidence → Issue #820 source-of-truth measurement contract → **NOT COMPUTABLE** → Claude/Analytics.

**Grok coordination only:** use `utm_source=youtube`, `utm_medium=organic_social`, `utm_campaign=history_pilot_2026_11`, `utm_content=<Grok_assigned_asset_id>` after Grok/Claude verify real destination and permitted link placement. No social asset publication, traffic, lead, checkout or sale is claimed. The site should use an existing measurement mechanism only after the separate owner approves it. Do not inject a second analytics script.

**KPI after actual sales:** `net realized revenue / qualified-human sessions × 1000`. Calculate using reconciled merchant-confirmed paid orders minus refunds, applicable fees, and a documented campaign-to-order attribution method. Report 7- and 30-day cohorts and small samples; do not treat clicks or registrations as sales.

## Verification and exit gate
**Completed here:** source-controlled implementation and draft tests; V8 JavaScript syntax compilation and exact-string contract checks; read-only Chromium navigation probe in this environment fails with `ERR_BLOCKED_BY_ADMINISTRATOR`, so nothing is marked browser-accepted.

**Must still run from a full checkout (Native Node + unrestricted browser):**
```sh
node --test experience2/apollo-creator-bridge/test_r135_artifact_and_acceptance.cjs
node --test experience2/apollo-creator-bridge/test_r134_actual_page_browser_acceptance.cjs
node experience2/apollo-creator-bridge/r134_actual_page_browser_acceptance.cjs --out /tmp/apollo-r135-browser-qa
```
Use local Playwright + Chromium + axe-core already installed in the approved tester environment; no automatic installation or paid services. Compare receipt checksum/PNG/no-JS PDF and inspect print legibility, keyboard, touch, zoom, 320–1920 overflow, LCP/CLS. Lab metrics are not field CWV or human traffic.

**Separate release blockers:** actual browser navigation/axe/metrics/screenshots; complete-source successful Node build; editorial approval; six photo-by-photo commercial reuse assessments; WordPress/Assembler integration; verified current merchant product, pricing and refund terms; independent QA; CI on exact HEAD; founder approval. Nothing here grants a live release or a new commercial offer.

**Coordination:** Apollo source-of-truth #150; revenue #820 and #818; Research Desk PR #158 is unchanged; Grok/Praxxis TASK-008 shared Drive handoff unchanged. R135 is separate from homepage PR #49.
