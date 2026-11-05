# 2026-11-04 — Already-published homepage: real anonymous Focus conversion gate (draft / HOLD)

**Source of truth:** Experience #150; Revenue/Attribution #820 and charter #818.  
**Base:** PR #1005 exact `4253522373f3b4032d38acf74242cf24c7173cdc`, a source-only audit.  
**This branch:** separate automated **actual public-browser** qualification of the existing **published** WordPress homepage; *not* a plugin, production payload, extra chapter or analytics deployment.

## Why this is the highest-value next verification

WordPress site's read-only connected API (site `256784396`) returned:
- Page **6**, published `/home/` as `https://finalvestige.com/`, modified **2026-11-04T14:39:24** per WP. Seven identifiable chapters: `fv-hf-chronicle`, `-evidence`, `-apollo`, `-franklin`, `-malbone`, `-inquiry`, `-observer`. **72** numbered Margins, **four** in-page Focus links, Franklin evidence folio and Jetpack markup.
- Published `/focus/`, page **1579**, modified **2026-11-03T14:36:15**. Fieldbook landing markup and Jetpack subscription block present. This establishes source presence only, *not* successful confirmation, download delivery, sales or browser visibility.
- The live `assembler//header` has **FREE EBOOK** native nav link + separate Focus strip. Its actual CSS declares `.fv-nav-free-ebook{display:none}`; at **min-width 1280px**, it becomes `display:flex`. The strip defaults to `display:none`, becoming `display:block` at **max-width 1279px**; Focus page 1579 suppresses both to avoid duplication. At <700px, the strip becomes a column. These are source-verified CSS rules, NOT proof of computed display/hit-test.
- Because Page 6 already has seven chapters and native header links, creating additional links or chapters before **real** anonymous viewport evidence risks conversion friction and duplicate CTAs.

## New executable browser gate

`live_public_focus_browser_gate.mjs` issues **GET only** to the live homepage and (after a user-visible CTA click) `/focus/`. There are **no writes** or subscriber test submissions; no cookie reuse, no commerce checkout, no analytics injection, no API credentials. It fails closed if Playwright or axe-core is unavailable, and records only pathnames (not query-string PII).

| Mode | Widths | Hard checks | Receipt |
|---|---|---|---|
| JS enabled, reduced-motion | 320, 390, 768, **1279, 1280**, 1440, 1920 | exact seven chapter landmarks, single accessible main, no root overflow/visible dialog, existing header Focus CTA actually visible, on-screen, >=44x44, unoccluded center, correct breakpoint mode, actual archival image `naturalWidth`, real HTTP response bytes, no page exceptions, full-document axe WCAG2/2.1/2.2 AA | each full-page screenshot, JSON receipt |
| Actual Focus navigation | 390 + 1440 | hit-test a genuine Focus CTA, click, require destination `/focus/`, verify subscription markup exists; **do not subscribe** | Focus screenshots |
| JS disabled, reduced-motion | 390 | seven meaningful chapter anchors still present, one main, no horizontal overflow, existing Focus CTA discoverable + hittable | no-JS screenshot |
| Lab metrics only | all JS-enabled widths | browser navigation timing, LCP/CLS observations, actual first-party/third-party image responses and transferred response byte lengths | explicitly **not** Lighthouse score, field CWV, Safari or full WCAG certification |

```bash
# Trusted isolated checkout; no paid subscription required.
# Install from the project's approved dependencies if available; otherwise record setup HOLD.
node --test experience2/home-flagship/qa/release-candidate/test_live_public_focus_browser_gate.mjs
node experience2/home-flagship/qa/release-candidate/live_public_focus_browser_gate.mjs
# Offline screenshot/receipt path: artifacts/ex2-live-focus-20261104/
```

## Tested versus untested: do not confuse

- **BUILT / source-controlled:** browser test and ten Node regression controls (positive/negative).
- **OFFLINE TESTED:** 10/10 extracted pure-helper V8 checks against committed browser source in a minimal simulated URL environment. This is *not* Node, Chromium or a native URL-parser run.
- **NOT TESTED:** exact-checkout Node test, live Chromium requests/screenshots, whole-document axe, real image transfer, physical 200% zoom, Safari, Lighthouse CLI or production field CWV. Those remain explicit release HOLD gates. Container runtime was unavailable for executable browser/Node checks in this sprint.
- **Additional release gates:** private WordPress Playground Assembler Gutenberg exact-source admission; host-specific QA that Playground cannot replicate; independent QD at exact SHA, CI, founder visual & explicit release approval. Existing published Page 6 is not equivalent to unmerged source candidate. Do not replace production from this branch.
- Existing frozen PR #49 SHA `10495883299d53596992c26a8987f629b2904670` is unaffected. Apollo #158, Franklin #254, Mind #171, Grok/Praxxis TASK-008 remain their respective lanes.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

**Offer:** free **52-page** Seven Day Focus Fieldbook (lead capture, **not itself paid revenue**). Paid-product and approved affiliate purchase validation remains a separate merchant/Claude-owned gate.

**Step:** Grok asset-linked qualified visitor → published homepage / evidence → *visible* native Focus CTA → `/focus/` → independently confirmed signup → later verified merchant order/commission → net revenue after refunds/fees.

**Blocker/hypothesis:** source-visible WordPress header CTA could be absent, occluded, too small or below fold in anonymous/mobile view. Breakpoint boundary **1279/1280px** has not been browser-proven; the native overlay may affect navigation. If exposed, a mobile/desktop conversion regression could exist despite four in-page links.

**Experiment:** execute exact committed anonymous-browser test at seven widths and no-JS; only if genuine failing screenshot/hit test appears propose a small separate, reviewed CSS/UX fix—not another CTA and not another chapter.

**Pass:** CTA intersects first viewport with >=44px target and unoccluded center; click reaches real Focus page; Jetpack markup; seven evidence stages and 72 Margins preserved; no full-doc axe violations and image failures; no uncontrolled overlays. Independent human accessibility/200% zoom, performance and commercial attribution gates remain.

**Owner:** Homepage engineering tests/visual QA. Claude owns live analytics, paid offer eligibility and conversion events; Grok owns creative/distribution, Praxxis independent creator-traffic QA; founder approves any production or spending changes.

**Revenue/attribution:** no customer order, Jetpack confirmation or partner payout was accessed here. KPI (eventually) = independently verified **realized net revenue / qualified human sessions * 1000**, with 7/30-day cohorts and small-sample caution. UTMs from Grok TASK-008 only; do not introduce competing instrumentation.

## Art and archival safeguards
No images, CSS, words, historical facts, affiliates or affiliate claims are added to production or candidate. The authenticated Franklin evidence is editorial typesetting rather than a facsimile. NASA Apollo rights/nonendorsement, Franklin source derivative and NYPL provenance require separate existing rights signoff; a successful image GET alone is **not** image licensing clearance. Preserve obsidian/antique-gold editorial identity and no-JS meaning.

**Decision: HOLD.** No production CMS/theme/nav/settings write, merge, deploy, plugin, email, affiliate activation or new subscription authorized.
