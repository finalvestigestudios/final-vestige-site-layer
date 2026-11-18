# Apollo Experience 2.0 R458 — editorial reconciliation, not a new public gallery

**UNPUBLISHED STAGING CANDIDATE · NO RELEASE APPROVAL · no WordPress writes, no media downloads, no commerce**

Parent: [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); source Research Desk [draft PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158); business truth [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) / [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Predecessor [R457 draft PR #3012](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3012). **Do not edit homepage PR #49, replace the homepage lead, touch Grok/Praxxis TASK-008, or activate on public WordPress.**

## Why R458 is different from R457

R457 describes six NASA photo records and the public Atlas's editorial shown/withheld categories. R458 makes the **cross-page S67-19766 inconsistency an explicit review gate** and separates (A) historical event date, (B) archive record/link identity, (C) where the image was shown editorially, (D) source-based factual findings, and (E) commercial reproduction rights. Photographic context is **not** evidence proving the precise ignition wire. The NASA Images item \`KSC-20170124-PH_KLS01_0129\` remains \`unretrieved\`, not falsely certified. Other homepage surfaces are marked \`not_reviewed\`, not absent.

The six catalogue labels reflect a read-only observation documented Nov 18 in #150; R458 makes **no fresh live-site certification**. The 2017 records are retrospective exhibit documentation, not Jan 27 1967 events. Chronology rail and six-card source board are non-geographic. No invented pins, directed edges, still images, logos or mixed NASA-commercial promotional images.

## Component contract

- PHP entry \`apollo_editorial_reconciliation.php\`; shortcode \`[fv_apollo_editorial_reconciliation_r458]\` registers **only** with \`FV_R458_ENABLED === true\`, \`FV_R458_PAGE_ID\` positive integer, \`wp_get_environment_type() === 'staging'\`, and the exact queried page ID. These are not set in this PR; the reviewed staging integrator must supply them.
- JSON source custody \`data/records.json\`: six dated images; three independent 1967 Review Board claims with distinct boundaries. Explicit \`atlas_use\`, \`homepage_use\`, \`catalogue_status\`, \`review_state\`, \`precision\`; immutable local snapshot label. Validators require exactly six unique records, correct observed mismatch, one catalog hold, legitimate month/day ISO dates, nondecreasing month groups, strict HTTPS NASA host with no credentials/query/port.
- PHP pins \`sha256\` of JSON, CSS and JS; any mismatch **fails open to an accessible free investigation link**, not partially trusted markup.
- All information appears in semantic HTML (timeline \`<ol>\`, source \`<details>\`, explicit cited claims), even without JavaScript. Progressive filter is keyboard/touch-accessible; multiple instances are scoped, no fetch, storage, cookies, identity capture, hidden commerce, or tracking script. Four optional editorial-review checkboxes are *not* attestation or permission evidence.
- Responsive 320–1920 CSS with \`minmax(0,1fr)\`, long source-ID wraps, 44px touch targets, reduced-motion, forced-colors, focus-visible and print layout. Single free next action: [read the original investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). No product CTA until founder/Claude independently establish one actually purchasable rights-cleared SKU.

## Primary official sources and rights

- [NASA Report of the Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): probable electrical arc, no single conclusively identified ignition source.
- [NASA Review Board findings](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html): 100-percent oxygen ground-test atmosphere at 16.7 psia; internal pressure obstructed emergency hatch opening.
- [NASA media use](https://www.nasa.gov/nasa-brand-center/images-and-media/): factual editorial use generally permitted subject to exceptions, source attribution, third-party materials and identifiable-person publicity rights; do **not** imply NASA endorsement or general commercial product clearance.
- Public [Apollo Evidence Atlas](https://finalvestige.com/apollo-1-evidence-atlas/) / [homepage](https://finalvestige.com/) prior read-only observation detailed in [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150#issuecomment-6982362329). S67-19766 conflict is an editorial reconciliation, **not** automatic license breach.

## Executed local proof and hosted gate

\`\`\`bash
php -l experience2/apollo-r458/apollo_editorial_reconciliation.php
python experience2/apollo-r458/qa/test_contract.py
python experience2/apollo-r458/qa/browser_qa.py
\`\`\`

The local browser uses **actual PHP-rendered HTML** via Playwright \`page.set_content\`; this is not WordPress navigation. Local screenshots and deterministic archive are QA artifacts, not approval. \`qa/hosted_acceptance.py\` is a **fail-closed runner**: no access = \`HOLD_NOT_RUN\` (exit 2); it demands approved HTTPS staging host, locally supplied/independently reviewed axe-core with matching SHA256, and actual page navigation for genuine axe and lab LCP/CLS. No claim of *hosted* axe/LCP/CLS or field p75 results is made in this sprint.

Example for an authorized QA operator (do **not** run against production):

\`\`\`bash
FV_R458_APPROVED_STAGING_URL=https://approved-staging.example.invalid/apollo-review/ \
FV_R458_APPROVED_HOST=approved-staging.example.invalid \
FV_R458_AXE_CORE_PATH=/reviewed/local/axe.min.js \
FV_R458_AXE_SHA256=<actual-approved-bundle-sha256> \
python experience2/apollo-r458/qa/hosted_acceptance.py
\`\`\`

The hosted runner records complete lab evidence and screenshots only after real navigation. A lab pass cannot substitute for manually reviewed WCAG 2.2 AA, independent QD, confirmed CI, or p75 field data. Keep exact-head CI and production release on HARD HOLD.

## Business scope

One target buyer: secondary-school/homeschool history educator researching evidence literacy. Existing free path: a matching **verified already-published** Grok Apollo documentary (not yet proved) → this source trail → free Apollo investigation → a separately approved original educator lesson/evidence kit (not verified payable). Nonintrusive next action is *only* the free investigation. Relevant Mini Museum products are **not** inserted into the tragedy narrative; pending approved affiliate claims and settled commission reports do not constitute revenue.

Conversion hypothesis: better separation of archival photograph, primary finding, editorial status and commercial rights may increase qualified education-reader progression and trust. Measure through Claude's existing consent-reviewed instrument only: \`asset_id/utm_campaign → qualified human session → CTA click → verified lead if applicable → merchant-paid order → refunds/fees → realized net revenue / 1000 qualified human sessions\`, at 7/30 days with tiny-sample caveats. No unpublished Grok asset ID, commerce signal, visitor event, checkout or sale invented.
