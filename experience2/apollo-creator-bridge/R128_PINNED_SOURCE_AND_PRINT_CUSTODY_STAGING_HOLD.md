# Apollo R128 — pinned Research Desk source and classroom photo custody (STAGING HOLD)

## Ownership and release boundary

Isolated Apollo branch stacked on R127 at `4f241f7d173867fd6aee146da93c222d87585532`. Read-only comparison to independent Research Desk draft [PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158) at `250d7f05a4de037e73826dcf0cfaef0ec4c29383`. Frozen homepage PR #49 and all Claude production branches remain untouched. No WordPress/Assembler, merchant, email, affiliate, analytics, Grok/Praxxis queue, or social publishing modifications.

## Actual failure mode addressed

Prior R127 audit checked six official photo URLs but did not **pin the independently maintained Research Desk source bytes**. A different ledger containing the same six URLs could appear to pass URL-integrity checks while changing source-role assertions. Also, a `rel=noreferrer noopener` string elsewhere inside a photo table row could mask an unprotected NASA link, and the six links inside the separate printable classroom worksheet were not audited.

R128 does not assert that source-content matching establishes historical or reuse rights. It adds defense-in-depth checks for:

1. The exact Git blob of PR #158's `experience2/research-desk/templates/ledger.html`: `403d128c57b9bc82dac7c619651689070edef86c`; a changed ledger is `BLOCKED_UNREVIEWED_SOURCE` until independently re-reviewed, even when all URLs match.
2. Exactly one authorized NASA image anchor in each of six main table rows **and** six Research Desk cards; `noreferrer` and `noopener` must be on the actual Apollo photograph anchor.
3. Six separate printable-worksheet records with exact NASA URLs and privacy tokens; missing/duplicate/changed records fail.
4. Four dated photographic checkpoints in verified order (1966-10-18, 1967-01-03, 1967-01-28, 2017-01-24); the undated January 1967 crew portrait must retain its separate provisional notice.
5. Existing historical limits and unauthorised-media/embed exclusions remain in force. Photo-by-photo commercial rights remain 0/6 reviewed/approved. The tentative S67-19766 attribution is not promoted to confirmed.

## Reproduction

From the repository checkout with Apollo R128 and PR #158 available as a local ref:

```sh
node --test experience2/apollo-creator-bridge/test_r127_source_role_crosswalk.cjs \
  experience2/apollo-creator-bridge/test_r128_source_snapshot_and_worksheet.cjs
node experience2/apollo-creator-bridge/r127_source_role_crosswalk.cjs \
  --research-ref feature/experience-2-source-ledger-pilot-20261030 \
  --output /tmp/apollo-source-crosswalk-r128.json
```

The second command **must exit 2 / STAGING_HOLD** until both the six editorial flags and file-specific media rights are independently resolved. Its JSON may independently indicate `link_integrity:PASS` and `source_custody:VERIFIED_SNAPSHOT`; neither is authorization to publish. A newly changed Research Desk ledger requires a fresh fixed-blob review; do not auto-approve a mutable branch.

Actual-page Playwright/axe/performance acceptance remains blocked by Chromium's `ERR_BLOCKED_BY_ADMINISTRATOR` navigation policy observed in R125–R127. **Do not substitute `page.set_content()` fixtures for actual-page acceptance.** Run existing `qa_r113_print.py` in a permitted local/CI environment, recording HTTP navigation, no-JS, keyboard/touch, zoom/reduced-motion, screenshots at 320/390/768/1440/1920, LCP/CLS and axe receipts on exact HEAD.

## Source and commercial authority

Primary technical source: NASA Apollo 204 Review Board report, https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; six photography links provide visual context only. They are not sensor traces, historical permission certificates, or independent proof of the ignition source. No embedded photograph binaries or invented coordinates.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER**

- *Proposed* paid Apollo educator casefile → verified merchant order: no verified sellable SKU, pricing, rights, refunds or delivery → merchant inventory and rights audit before a CTA → **BLOCKED** → Growth/Claude and founder.
- Grok-owned long-form/Shorts → Apollo source trail → free worksheet: provenance and separate printed handout could silently diverge → R128 pinned crosswalk + handout checks → **BUILT; V8 contract partially TESTED; no full browser acceptance** → Apollo.
- Optional post-worksheet paid resource → verified purchase: no approved matching offer → **DO NOT ACTIVATE** a fictitious commerce link → founder/Claude.
- Verified asset_id/UTM sessions → CTA → confirmed lead if applicable → merchant-confirmed paid order → refunds/fees → realized net revenue: source-of-truth attribution absent → reuse #820 contract, 7/30-day cohorts, small-sample flag; **NOT COMPUTABLE** → Claude/Growth with Grok asset IDs.

This branch introduces no tracking scripts or additional primary marketing CTAs. No claimed affiliate commissions, sales, paid customers, attributed traffic or net revenue. This is not LIVE or independently historical/rights VERIFIED.

**Release gate: STAGING HOLD.** Requires six editorial reconciliations in Research Desk, six image-specific rights decisions, actual full-page Chromium/axe/LCP/CLS, WordPress/Assembler integration, independent historical review and founder publication approval.
