# 2026-11-05: published WordPress homepage vs. isolated flagship candidate

**Decision: HOLD — read-only source finding, NOT production browser certification.**

## Exact sources read

- **WordPress editor source, published Page 6,** site `256784396`, modified `2026-11-05T12:07:24` (as returned by WordPress edit-context API).
- **Review candidate** `experience2/home-flagship/index.html`, Git blob `8f4d64186c986a00ac48e23db7df2c05a610ceaa` on commit `0de4ec74faa7c4661c3dc457c2d8bea259dc9ad5` (parent draft PR #1187).
- **Published Focus Page 1579** source, modified `2026-11-05T17:44:02`.
- Machine-readable independently collected source receipt: `FV_EX2_PUBLISHED_SOURCE_PARITY_RECEIPT_20261105.json`. All findings reflect **editor and repository source**, not the public served page's effective DOM, viewport layout, network transfers, or visitor checkout.

## Findings that change the release plan

| Invariant | Published Page 6 editor source | Git review candidate |
| --- | --- | --- |
| Seven chapter destination IDs | 7 / 7 | 7 / 7 |
| Chapter destinations with `tabindex="-1"` | 0 / 7 | 7 / 7 |
| First-screen secondary CTA | Blog | Free 52-page Focus Fieldbook |
| Fieldbook masthead CTA | Absent | Present |
| Apollo + Franklin image elements | Present | Present |
| NYPL Brooklyn map image element | **Present (needs exact-capture rights QA)** | **Excluded** |
| Image elements in respective source | 4 (Apollo, Franklin, NYPL, Focus cover) | 2 (Apollo, Franklin) |
| Hidden in the Margins elements | 72 | Not included (staging candidate deliberately only the seven-chapter component) |
| Jetpack subscription block | Present | Not included (isolated review component) |

**Important correction:** This is not a situation where the seven chapters exist only in Git drafts. The *published WordPress Page 6 editor source already contains all seven chapter destinations and the Franklin folio*. We did **not** establish that the browser-served homepage matches this editor source, or which contributor made/approved its changes. Do not overwrite the live page with the isolated candidate; it omits site-specific Margins and native Jetpack content.

### Material release blocker 1 — rights / provenance

The published page embeds `edit-017-v02-nypl-5003296-original.jpg` from the `i0.wp.com` image proxy, whereas the isolated candidate does not embed the NYPL image. The NYPL catalogue link is **not** itself proof of clearance for this exact photographed or edited capture. NYPL documents that rights statements can be capture-specific: https://api.repo.nypl.org/api_documentation_v1 . Its general policy also distinguishes public-domain, copyrighted, and undetermined collections: https://digitalcollections.nypl.org/about .

**Gate:** Obtain the exact image/capture ID, rights statement, license or reuse basis, derivative provenance, proper attribution, and binary/transform comparison. Until established, label **REVIEW REQUIRED**, not `unlicensed`, `cleared`, or `public domain`. Do not republish/reuse in the revised candidate, and do not silently remove it from production without release approval.

### Material release blocker 2 — conversion-first visual intent

The published first-screen secondary CTA is “Read the investigations”, linking to `/blog/`; the review candidate already has a contextually labeled, free 52-page Focus Fieldbook CTA **and** a masthead Focus link. Avoid inventing more hero designs. This is a concrete candidate-vs-live difference to take into a controlled **founder-approved** release experiment, with evidence-first primary action retained.

**Hypothesis (untested):** For a high-intent Grok `Mind & Perception` visitor, an explicit above-fold free Focus Fieldbook action improves qualified lead completion *without* harming investigation engagement or paid conversion. This is **not** proof of more subscribers or purchases. Claude owns event attribution and payment data; Grok owns creator assets and campaign IDs, per #820 and TASK-008. No new pixel, script, links, or production page changes were made.

**Acceptance:** 320/360/390/768/1440/1920 px with effective WordPress/Assembler chrome; no obstructed CTAs at 200% zoom, touch and keyboard activation, no-JS anchor behavior, verified anonymous Jetpack subscription (consent and delivery), and separate verified paid-order reports. Evaluate 7/30-day net revenue per 1,000 qualified human campaign sessions with small-sample caveats.

### Material release blocker 3 — keyboard chapter navigation

Each of the seven candidate chapter destinations includes `tabindex="-1"`. The current published page's corresponding destination opening tags do not. **This is a source difference, not a proven keyboard failure in the live browser.** Run keyboard/tab/focus-order testing on the actual served document and apply a reviewed correction only if confirmed. Do not conflate element focusability with WCAG 2.2 AA certification.

### Relevant non-blocker — Focus Page already has the proposed anchor

Page 1579 already includes `id="subscribe-blog"` ahead of the existing `wp:jetpack/subscriptions` block, and five existing `#subscribe-blog` CTAs. Do **not** blindly apply #1180 again. Guest Jetpack form visibility and welcome email delivery remain unverified.

## Integration / safety boundaries

- Current WordPress account exposes one site (production only), not a separate private WordPress.com staging clone; Personal-plan clone support is unavailable. Use a **free disposable Playground/Assembler** environment for source QA, not a production import or settings change.
- Isolated Playground is not an exact simulation of WordPress.com Atomic, cache, Jetpack account sync, or field Core Web Vitals.
- Preserve live site data, all 72 Margins records, subscription records, existing visitors, Focus PDF, and three art directions.
- No merges, production CMS writes, plugin install/activation, publishing, affiliate links, tracking scripts, email sends, or paid tools.
- Preserve PR #49 exact SHA `10495883299d53596992c26a8987f629b2904670`, Apollo #158, Mind #171, and #252/#254 exact-source QA.
- No WordPress Playground execution, HTTP image byte receipts, axe, native zoom, Safari, Lighthouse or paid-order attribution was performed in this source-diff sprint. All remain **HOLD**.

## Release gate / owner decisions

1. **Homepage engineering / Site QA:** Reconcile what is *already in published page 6* with the proposed seven-chapter candidate; obtain a live served DOM snapshot/visual comparison, and independent review of the existing NYPL image use.
2. **Homepage engineering:** Use source-controlled WordPress Playground with pinned Assembler (PR #1187 stack), actual screenshots, 7 widths + 200% zoom, keyboard/touch/reduced-motion/no-JS/axe, selected network image bytes and Lighthouse.
3. **Claude:** Confirm native Jetpack guest capture and separate verified orders/net revenue, no analytics duplication; coordinate #820 and #818.
4. **Founder:** Review actual before/after and approve any proposed production deployment separately. No implied approval from this document.

**Verdict:** Source divergence is real and business-relevant. A deployed seven-chapter *editor source* exists, but none of the outstanding browser, image rights or commercial measurements is thereby certified.
