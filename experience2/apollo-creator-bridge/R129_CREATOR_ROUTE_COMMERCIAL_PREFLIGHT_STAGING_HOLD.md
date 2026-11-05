# Apollo R129 — creator-to-classroom source and commercial route gate (STAGING HOLD)

## Scope and boundaries
Isolated draft stacked on R128 PR #1014 at `4a93409b98ade85a8009c171d496d6b06dea6bb3`. No changes to homepage PR #49, Research Desk PR #158, Claude production branches, Grok's queue, TASK-008, WordPress, merchants, analytics, ads, email or live pages. Canonical issue #150; commercial measurement charter #820 and #818.

**Flagship:** Apollo 1, “Fourteen seconds. More than one failure.” Grok may propose a video linking to this evidence page, but production/distribution is Grok's exclusive responsibility; no published video or referral is verified here. Provisional high-intent audience: secondary history/science educators.

## Real failure mode and implementation
Before R129, the R128 crosswalk checked six NASA photographs and printed worksheet URLs but did not fail when an otherwise intact landing added a fake merchant checkout, irrelevant affiliate URL, unreviewed form, broken internal classroom anchor, external analytics script, unapproved photograph binary or unsafe referrer link *outside* the six photo-table anchors.

New `r129_creator_route_gate.cjs` is a deterministic, read-only, zero-dependency **source preflight**, integrated as `creator_route` and `CREATOR_ROUTE_*` errors into `r127_source_role_crosswalk.cjs`. It validates:
- One primary anchor `#classroom-preview`, visible no-JS exercise and complete printable source index.
- Exact, reviewed external destination allowlist, valid in-page targets; blocks unapproved self-hosted commercial routes as well as external affiliate/checkouts.
- All 22 NASA links have `noreferrer noopener`; unreviewed embeds, media binaries, forms, storage, external JS/CSS, analytics or redirect additions fail.
- Staging robots `noindex,nofollow` retained. Existing main narrative and free worksheet unchanged.

The allowlist is a **change-review contract**, not a claim that all destinations are available forever or their image rights cleared. The report explicitly returns no verified paid product and no observable revenue. URL/content integrity is distinct from merchant, rights, historical, browser or production approvals.

## Reproduction and evidence
```sh
node experience2/apollo-creator-bridge/r129_creator_route_gate.cjs
node --test experience2/apollo-creator-bridge/test_r129_creator_route_gate.cjs
node --test experience2/apollo-creator-bridge/test_r127_source_role_crosswalk.cjs experience2/apollo-creator-bridge/test_r128_source_snapshot_and_worksheet.cjs
# Run existing qa_r113_print.py against exact HEAD in an unrestricted Chromium/axe environment.
```

Connector-fetched **actual R128 Apollo staging HTML** was evaluated using the same pure route-check functions in V8. Results: baseline **PASS**, 36 links, 22 protected NASA links, 23 external links, 1 classroom CTA. Fourteen adversarial mutations rejected (**14/14**): fake checkout, hidden worksheet, competing CTA, affiliate redirect, javascript URL, signup form, broken anchor, external script, inline handler, stripped NASA referrer privacy, missing worksheet index, false same-domain checkout, photograph embedding and visitor storage. The exact source-controlled R129 JS file was re-fetched and compiled in V8; its exported audit returned the same baseline.

**Not yet claimed:** native Node `node:test`/GitHub CI execution on exact head, full-page Chromium navigation, axe-core, actual-page LCP/CLS/screenshots, 320–1920 device validation, WP/Assembler integration. Earlier Chromium navigation under this execution environment returned `ERR_BLOCKED_BY_ADMINISTRATOR`; no injection fixture is accepted as genuine full-page acceptance. Source regex preflight is defense-in-depth, not an HTML parser/browser/security certification.

## Source custody and rights
Technical primary: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). Media/identity guidance: [NASA Brand Center](https://www.nasa.gov/nasa-brand-center/). Six photograph records remain **link-only visual context, 0/6 individually cleared for redistributing image binaries in an FV commercial pack**; NASA credit alone is not a file-specific rights decision. Crew photo `S67-19766` remains provisional. Research Desk PR #158 six editorial flags remain unresolved; no source role has been promoted to a technical measurement.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER
1. **Proposed teacher-ready Apollo casefile → merchant paid order:** no independently verified sellable SKU, rights, delivery, refund/fee records; inventory and fulfillment audit prior to any purchase link. **BLOCKED**. Owner: Claude/Growth and founder.
2. **Grok video → Apollo investigation → optional free student worksheet:** potential click misdirection, hidden worksheet or false merchant link could break trust. R129 source-level gate + source evidence. **BUILT; V8 source-tested; browser blocked.** Owner: Apollo.
3. **Worksheet → relevant paid classroom resource:** no approved matching offer, so no purchase CTA, signup interception or misleading availability claim. **NOT ACTIVATED.** Owner: founder/Claude.
4. **Qualified sessions by Grok asset_id/UTM → visit → resource click → confirmed lead where applicable → independently verified order → refunds/fees → realized net revenue per 1,000 qualified human sessions:** no reliable denominator, confirmed sales or merchant attribution in this lane. 7/30-day cohorts and tiny-sample flags required. **NOT COMPUTABLE.** Owner: Claude/Growth.

**Release gate:** STAGING HOLD until native Node/CI, actual-page Playwright/axe/LCP/CLS/print QA, Research Desk reconciliation, item-level media decisions, full WordPress acceptance, independent review and founder approval. No live operations performed.
