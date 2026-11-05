# Apollo R141 — Reader CTA visibility/DOM custody (isolated staging)

**Decision: STAGING_HOLD.** Governing [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); commercial [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter #818. Stacked on R140 draft PR #1092. Do **not** merge into homepage PR #49, touch Research Desk PR #158, modify WordPress, or activate commercial/social channels.

## Actual defect reproduced in R140

R140 uses a regular expression that identifies a matching `<a>` tag and treats its own attributes as proof of visibility. On native Node, its source gate incorrectly returned `SOURCE_LINK_CONTINUITY_ONLY` for all of these forged CTA sources:

- `<section hidden><a ...>Read the full investigation</a></section>`
- `<section aria-hidden="true"><a ...>Read the full investigation</a></section>`
- `<div style="display:none"><a ...>Read the full investigation</a></div>`
- `<!-- <a ...>Read the full investigation</a> -->`

These are **false passes at the source-review gate**, not proof that the live Apollo CTA is broken. The existing source gate should not be equated with true keyboard/touch accessibility or live commercial conversion.

## Implementation

`r141_dom_custody_gate.cjs` wraps the earlier audited R140 route/source check and adds a conservative source-tree pass. It excludes markup inside comments/scripts/styles/templates/noscript/embedded content, propagates ancestor hidden/inert/aria-hidden/display-none/visibility-hidden, verifies a single visible literal reader label, checks exact approved article URL, bans deceptive accessible labels, tab-order manipulations, downloads, new-tab primary actions and ambiguous nested anchors. It records only hashes and structural counts, never emails, source HTML, supposed media rights or transactions. This is **not a browser DOM or full HTML5 parsing engine**; ambiguous markup must remain `REVIEW_REQUIRED`.

`test_r141_dom_custody_gate.cjs`: 22 adversarial native Node assertions, including 18 dangerous or ambiguous CTA variants.

`r141_browser_fixtures.py`: optional Playwright/Chromium *synthetic representative* suite for six widths (320, 360, 390, 768, 1440, 1920), no-JS keyboard Tab, focus-visible outline, overflow and reduced-motion setup, plus three negative DOM visibility cases. Screenshots and SHA-256 manifest are deterministic in provenance but PNG bytes may vary by Chromium/font platform. Requires locally installed Playwright and Chromium. It **uses `page.set_content` on about:blank**, **not** successful navigation to WordPress, so it is a controlled component regression only.

## Source checks performed 2026-11-05

Read-only WordPress page 2017 `publish` at `https://finalvestige.com/apollo-1-evidence-atlas/`, last-modified field `2026-11-04T17:09:24`, contains **one** exact `Read the full investigation` anchor with destination `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/` in the hero action group. It also contains a NASA Apollo 204 Review Board source link. Post 434 source and status were independently read earlier. This does **not** establish HTTP browser navigation or click success. The unapproved worksheet fragment and Apollo paid SKU remain unavailable; neither is added.

## QA and remaining release gates

Local native Node ran 22/22 R141 tests successfully against SHA-matched R141 gate content. Local installed Chromium executed 9/9 **synthetic** cases and wrote six screenshots. A direct attempt to navigate Chromium to `finalvestige.com` returned `ERR_BLOCKED_BY_ADMINISTRATOR`; actual-page Playwright, axe, full WordPress/Assembler browser tests, real-page LCP/CLS and performance evidence are **NOT DONE**. No production or merchant changes.

The principal NASA Apollo 204 Review Board report remains a documentary technical source. Six photographic records remain **not individually cleared for FV commercial reuse**; a source URL alone is not clearance. No speculative geographic pins or implied NASA endorsements.

## Conversion-first owner handoff

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Apollo educator dossier → paid order | No verified currently sellable Apollo SKU, ownership/rights/delivery/refund proof | Independently verify existing Payhip listing before offering checkout | **BLOCKED / NO SALE CLAIM** | Claude Growth + founder |
| Grok long-form or Shorts → published Atlas | No verified Apollo Grok asset ID, actual post URL or human-session attribution | Praxxis validates Grok-published asset and permitted linked destination under TASK-008 | **NOT VERIFIED** | Grok / Praxxis |
| Atlas → published full investigation | Source validator falsely accepted hidden/forged CTAs | R141 static source custody + 320–1920 representative keyboard checks | **BUILT / NATIVE SOURCE & FIXTURE TESTED; ACTUAL BROWSER BLOCKED** | Apollo |
| Investigation → paid educator product | No relevant approved offer; avoid historically unrelated purchase CTA | Keep single existing relevant `Read the full investigation` action until product verified | **NO PURCHASE CTA ADDED** | Founder / Claude |
| Qualified audience → paid confirmed orders → refunds/fees → net revenue | Missing human-session attribution, merchant reconciliation | Reuse #820 event contract for 7-/30-day cohorts; net revenue/1,000 sessions only when evidence exists | **NOT COMPUTABLE** | Claude Analytics |

**Hypothesis only:** teachers attracted by a source-led Apollo investigation may later consider a rights-cleared classroom evidence kit. An outbound click, lead or product idea is not a purchase. No new analytics, checkout scripts, paid services, Grok posts, email sends, WordPress writes or production release authorized.

**Next release gate:** execute actual page-bound browser/axe/LCP/CLS and integration in an authorized environment; independently verify rights and a real merchant product; obtain QD/Claude review and founder release approval.
