# EX2 — Live Page 6 reconciliation and production-state correction
**8 November 2026 · READ-ONLY · DO NOT DEPLOY / MERGE / EDIT WORDPRESS**

## P0 finding: the flagship is already in the published homepage editor
This changes the engineering priority, not the governance rules. Authenticated `wpcom_mcp_pages_get(id=6, context=edit)` returned **published** Page 6, modified **2026-11-05 12:07:24** (WordPress API local timestamp), with **150,710 raw editor-content characters**. It already has the full **seven-chapter `fv-hf__chapter-nav`**, all seven unique anchor targets, the **72 indexed Margins entries**, **one native Gutenberg `wp:jetpack/subscriptions` block**, four Focus links, one Dispatch link and **four editor image elements** (NASA Apollo, Franklin, NYPL 1903 map and Focus cover).

This is independently corroborated by the public `https://finalvestige.com/` crawler text on November 8: it contains the seven-chapter rail, Franklin 1847/1848 folio, evidence chamber, observer experiment, live imagery and investigation pathways. The active WordPress theme remains **Assembler**. WordPress activity log reports Page 6 updates on November 5 at **20:06:19 and 20:07:24 UTC**, via WordPress REST connected client; this metadata does NOT establish who authorized the changes. The connector lists just one site, production ID **256784396**.

### Why the correction matters
Prior stacked EX2 reports described the seven-chapter experience as *unpublished* and treated the private Playground bundle as the sole potential release target. That is **no longer a correct description of the production state**. Do not perform a second deployment, replace Page 6 with the shortcode-only private fixture, or assume the old PR #49 is what actually went live. PR #49 is still frozen at `10495883299d53596992c26a8987f629b2904670` pending exact-head QD/CI. We have **not** established an authorized release decision, production commit SHA, approval trail or successful runtime QA.

## New executable safeguard and evidence
- `tools/experience-2/verify_live_homepage_reconciliation.py` accepts a local read-only raw WordPress editor JSON export. It requires the exact seven chapter links/anchors, ordered 72 records, native subscriptions block, source links, all three archival image identities, Focus cover, Focus and Dispatch routes and absence of disposable Playground artifacts. It **never fetches or writes** an external system.
- `tests/test_ex2_live_homepage_reconciliation.py` uses synthetic Gutenberg editor documents with **17 positive/adversarial tests**; local execution: **17/17 PASS**. This is gate/fixture testing, NOT browser or native WordPress integration.
- `docs/experience-2.0/LIVE_PAGE6_AUTHENTICATED_READONLY_20261108.json` records **10/10 PASS** against the *actual authenticated editor source* in a connector-side, read-only cross-check: 7 chapter targets, 72 Margins, 1 native Jetpack block, 4 `<img>` tags, 4 Focus destinations and 1 Dispatch destination.
- Source content was never committed or distributed: the receipt contains counts, targets and status only (no subscriber, auth, or private data).

## Remaining actual release/quality risks — do not infer passing results
1. **Visible, already-published experience:** independent full-viewport Chromium checks on *real* live WordPress front end, 320/360/390/768/1440/1920, 200% zoom, no-JS, keyboard/touch, reduced motion, AXE WCAG 2.2 AA, and real page-to-Focus navigation. Public text crawl is not those tests.
2. **Actual media bytes:** verify status/body bytes for Apollo/Franklin/NYPL and image responsiveness, not just editor `src` or media metadata; complete item-specific derivative-rights review.
3. **Commercial integrity:** confirm genuine Jetpack subscription and email delivery without unapproved test signup; Focus Page 1579 query-string false-success issue tracked in PR #1613; never use UI text as a verified lead or sale. Audit mobile CTA clarity, source trust and contextual Fieldbook bridge. Attribution/backend remains Claude's lane, Grok owns creator distribution.
4. **Release history and governance:** compare WP revision to approved source baseline, independent QD and CI on relevant code. Preserve frozen #49 and all existing editor content; no automatic rollback, no overwrite, no deploy. Founder's exact permission is required for any further production modification.
5. **Performance:** report actual lab Lighthouse and field CWV separately. No measured real-world score is claimed.

## Decision
**ALREADY-PUBLISHED HOMEPAGE · URGENT POST-PUBLICATION QA HOLD.** Existing live work should be audited, not overwritten or described as awaiting a first staging release. The Personal plan lacks native staging clone; the free disposable Playground remains useful for *future code*, but is not a substitute for checking the *actual currently live* homepage.

**Conversion-first:** Offer = free 52-page Focus Fieldbook; step = contextual archival reader → Focus → confirmed Jetpack subscriber → verified sale; blocker = already-live front end lacks independent runtime/lead-confirmation acceptance and earlier reports misclassified live state; change = source-controlled read-only reconciliation; evidence = 10 real editor checks, 17 synthetic gate tests and public crawl; owner = interim homepage engineering for source/visual QA, Claude for Jetpack/analytics, founder for releases. **No verified incremental subscribers, paid orders, commissions or net revenue.**

No WordPress production writes, new subscriptions, affiliate activation, social distribution, PR #49 changes, merges or spending were performed in this audit.
