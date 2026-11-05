# Apollo R145 — Semantic gallery custody + deterministic local review build

**Governance:** Experience 2.0 [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); commercial attribution [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); charter #818. **Status: STAGING HOLD.** Branch stacked exclusively on R144 PR #1115 at `95ce2fa8d95213bfb19e506722619a41bb8fed08`; no touch to homepage #49, Research Desk #158, Claude production lanes, Grok/Praxxis task queue, WordPress, Payhip, email or analytics.

## Newly discovered validation weakness and response

R144's image/source audit recognizes `figure`, `img`, source anchors and `figcaption` through regular-expression checks. During R145 adversarial validation, the R144 audit **returned no blockers** when a photograph record was present only in an HTML comment or `<template>`, a NASA source link was inside a comment, an original-source link was hidden, two matching links appeared in a single caption, or the gallery itself had a hidden ancestor. Those variants would not establish usable archival source evidence for a visitor.

R145 adds a dependency-free, **fail-closed structural parser** that ignores comments and non-navigable raw content, scopes the three chronological figures to exactly one chronology/gallery, verifies each visible `img` source, alt and dimensions, requires one visible canonical NASA original-source anchor inside each contextual caption, and rejects hidden/inert ancestor containers, malformed/duplicate attributes and ambiguous structures. It composes with—not replaces—the R144 media/rights audit and R143 one-character repair guard.

### Actual current WordPress source check — read-only, 2026-11-05

WordPress **published page 2017** `https://finalvestige.com/apollo-1-evidence-atlas/`, last modified `2026-11-04T17:09:24`, returned **96,274 raw characters**. The committed R145 source was executed in the V8 tool context on the actual connected WordPress content; it identified **1 chronology, 1 gallery, 3 visible ordered media records, exactly 1 caption source link per record, 0 parser warnings**. The only source-audit blocker was `PUBLISHED_GALLERY_ENHANCEMENT_DEFECT`: the live inline selector still uses `$(box, '[data-fvx-chrono-photo]')` instead of `$$(...)`.

The committed R145 review-builder and R143 patch function were also evaluated **in memory** on the exact WP export with a deterministic fake-hash implementation for V8 compatibility: the postpatch semantic audit reported 0 blockers, the updated string had **96,275 characters**, and exactly one `$` was added. **This is not a native SHA-256 test, a live WP patch or browser acceptance.** The actual Node `node:crypto` implementation is used by the committed CLI when run in a native Node environment.

### Reproducible local commands (requires Node 22+, no dependency installation)

```bash
node --test experience2/apollo-creator-bridge/test_r145_semantic_gallery_custody.cjs
node --test experience2/apollo-creator-bridge/test_r145_review_preview_cli.cjs
node experience2/apollo-creator-bridge/r145_review_preview_cli.cjs \
  --input /path/to/read-only-wp-page-2017-export.html --out /tmp/fv-apollo-r145-review
```

The CLI refuses any unknown source drift and requires the **one documented live defect** before generating `apollo-r145-local-review.html` and `apollo-r145-manifest.json`. It will not overwrite its input. Manifest SHA-256 values are determined solely from the supplied bytes; no timestamps, random IDs, customer data or tracking are emitted. These are **local review files**, NOT deployment artifacts. Opening the HTML in a browser might load existing embedded third-party resources; use an approved offline/sandboxed browser environment, not a publicly reachable server.

**Source-controlled Git blob IDs:**
- `r145_semantic_gallery_custody.cjs`: `26b1f89e837fbf591363cf5fe5e4e807bf1b1d29`
- `test_r145_semantic_gallery_custody.cjs`: `493586b40f75d529db12d3756635d424e58be656`
- `r145_review_preview_cli.cjs`: `a3311dc08bec58151f0a9a9d5f982d7809664d58`
- `test_r145_review_preview_cli.cjs`: `547cb820aa1605bf0f91402df853574a42f7d31f`

**Execution evidence in this environment:** 20/20 synchronous adversarial regression assertions **passed under the connector V8 evaluator with mapped `node:test`/`node:assert/strict` semantics**, not native Node; the actual WP content was independently source-audited as stated above. Native Node, Playwright real-page navigation, axe-core, actual LCP/CLS, screenshot artifacts and exact-head hosted CI are **NOT VERIFIED**. Historical R143 synthetic Chromium fixture checks are a separate predecessor result, not new R145 browser acceptance.

## NASA source/rights, chronology, geography and accessible behavior

The three published context records remain S66-58038 (October 1966 crew training), S67-15717 (January 1967 spacecraft preparation) and KSC-20170124-PH_KLS01_0129 (2017 preserved-hatch display). None depicts the ignition/fire sequence in progress. Their source pages are linked on the Atlas; the Apollo 204 Review Board report remains the technical anchor. No speculative map pins/edges or unreviewed new imagery were added.

NASA's [Brand Center](https://www.nasa.gov/nasa-brand-center/) and [Advertising Guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) distinguish archival educational/editorial display from promotional reuse, prohibit implied endorsement and may require likeness/publicity-rights clearance. **All three photo-specific commercial/promotional clearances remain unverified.** An original NASA source link is not approval to sell imagery or include it in product ads.

A source-gate pass does not prove a page's computed styles, keyboard/touch focus, screen-reader semantics, actual network source delivery or LCP/CLS. The R134/R135 full real-page Playwright/axe acceptance runner and the six-width R143 fixture suite are available in the stacked branch, but actual WordPress navigation previously failed with `ERR_BLOCKED_BY_ADMINISTRATOR`. Recheck in a permitted environment; take 320/360/390/768/1440/1920 screenshots and metrics and perform manual screen-reader QA before release.

## One conversion-first reader pathway, not opportunistic commerce

**Audience:** grades 6–9 teachers and homeschool educators arriving from an independently verified future Grok Apollo 1 long-form video. **Single currently valid action:** published Atlas → **Read the full investigation** → the existing linked investigation. A source-analysis worksheet or paid classroom dossier is not presumed published or sellable.

**Offer → Funnel step → Blocker → Change / experiment → Evidence → Owner**

1. **Proposed original educator evidence dossier → verified paid purchase:** No verified live SKU, merchant acceptance, fulfillment, refund and license record → Claude/Growth audits the genuinely sellable rights-cleared Payhip inventory and buyer fit before any CTA proposal → **NOT VERIFIED** → Claude/Growth, founder authorization.
2. **Grok long-form → actual Atlas:** Published unique Grok asset ID, landing campaign and qualified human sessions unverified → Praxxis/Grok reconcile TASK-008/dated Drive handoff, then Claude uses #820 privacy-safe source tagging without duplicate scripts → **NOT VERIFIED** → Grok/Praxxis/Claude.
3. **Atlas → full investigation:** Source-validator was fooled by ghost records/hidden links and live selector still wrong → R145 semantic gate + R143 isolated selector patch → **BUILT, source-evaluated; browser NOT TESTED** → Apollo, Claude for governed WP integration.
4. **Investigation → approved educator offer:** No verified relevant paid product and media reuse approvals → retain non-intrusive reading CTA, withhold checkout → **BLOCKED** → Founder/Claude.
5. **Paid order → realized net revenue:** No verified merchant order/refund/fee and qualified-session matching → #820 7-/30-day cohorts; net revenue per 1,000 *qualified human* sessions when denominators are substantiated → **NOT COMPUTABLE** → Claude/Analytics.

Never turn a click, view, outbound merchant visit or form interaction into a revenue claim. No Grok post is assumed live. Grok owns publishing; Praxxis owns independent content QA; this lane owns only in-site evidence integrity and review.

## Governance / next release gates

Keep this draft stacked on PR #1115. **No merge, deployment, WP edits, new email/newsletter, tracking or commercial activation.** Next: native Node test and CLI replay with real SHA-256 on an authorized copy of WP content; actual webpage Playwright + axe + device/performance review; photo-specific rights decisions; independent editorial/QD and screenshot review; matching offer and checkout verification; green exact-head CI; founder sign-off and Claude-controlled release. This exact record should be linked in #150 with conversion cross-reference #820.
