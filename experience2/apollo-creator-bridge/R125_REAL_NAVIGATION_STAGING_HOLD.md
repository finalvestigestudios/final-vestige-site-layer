# Apollo R125 — Real navigation acceptance gate and worksheet accessibility
**2026-11-04 · DRAFT / STAGING HOLD · Issue #150 · commercial charter #820 / #818**

## Scope and baseline
- Parent: R124 draft PR #988, commit `c144750cd5b76899091bd16398833b5109dbd5a4`. This PR is stacked **only** on the Apollo QA lineage.
- Do not touch or merge frozen homepage PR #49, Research Desk PR #158, production WordPress, analytics, merchant systems, Grok content queue or rights-uncleared imagery.
- Flagship: **Apollo 1: Fourteen Seconds, More Than One Failure**. Historical technical authority: NASA Apollo 204 Review Board (https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). Photograph-specific rights decisions remain **0/6**; tentative crew portrait ID `S67-19766` remains unconfirmed.

## Why this change
R113–R124 Playwright acceptance used `page.set_content(html)`. That exercises a document injected into a page, but does **not** establish a real browser navigation to the staged document. It is therefore insufficient for a navigation-level launch gate, genuine navigation timing, route semantics or a browser-replayed visitor-to-worksheet journey. A green source check is not a green browser check.

R125 switches the existing actual-source test harness to a bounded loopback HTTP server which serves the **exact on-disk canonical file bytes**, performs `page.goto(...)` at each viewport/mode, demands a 200 response, exact expected URL and a navigation timing record, and rejects injected-document fallback. The source file must still match `git show HEAD:experience2/apollo-creator-bridge/landing-preview.html`. The receipt additionally records `git rev-parse HEAD`.

The LCP/CLS observer is installed with Playwright `add_init_script` **before** each real navigation, with an explicit LCP observation wait and 300 ms stabilization delay. This corrects the old pattern of running observers on an about:blank/injected page and accepting apparent measurements that might not represent a loaded document. This is a lab-only performance test, **not** field CWV evidence.

The R124 preview also now handles Escape on `document`, not only while focus resides inside the worksheet. The actual-page runner asserts that Escape closes the preview and restores trigger focus after the visitor has moved focus to another page control. The preview remains optional; no-JS access and the original free worksheet/print path remain available.

## Verification — bounded by evidence
- **Built/source-controlled:** actual staging `landing-preview.html`, actual-page Playwright runner `qa_r113_print.py`, native Node regression `test_r125_actual_navigation_contract.cjs`, this document.
- **TESTED:** 17/17 exact GitHub source contracts passed under a V8 shim providing the Node test/assert/fs interfaces. **Native Node/CI not executed**; this is structural regression, not browser proof.
- **Browser environment probe:** Chromium 144.0.7559.96 launched; `page.goto` to local HTTP, local file and data URI each returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`. A newly created about:blank tab accepted `set_content`, but R125 intentionally **does not** downgrade to that approach for release acceptance. The probe ran on a separate one-line fixture, **not** the Apollo landing.
- **NOT EXECUTED:** actual Apollo full-document Playwright, axe-core on Apollo, Apollo LCP/CLS, Apollo screenshots/PDF, WordPress/Assembler compatibility, native Node CI. No pass or production readiness claim.
- **Not shipped:** no images, map pins/edges, external scripts, forms, checkout links, affiliate activations, social posts, emails, paid services or WP writes.

## Reproduction / release gate
At an authorized exact-head clone where Chromium permits loopback navigation, with an independently approved local axe-core bundle:

```sh
node --test experience2/apollo-creator-bridge/test_r125_actual_navigation_contract.cjs
python experience2/apollo-creator-bridge/qa_r113_print.py \
  --chromium /usr/bin/chromium \
  --axe /path/to/approved/axe.min.js \
  --out /tmp/apollo-r125-navigation
```

Complete acceptance requires 14 width/mode combinations (320, 360, 390, 768, 1024, 1440, 1920 px × JS on/off), genuine HTTP navigation, source identity, keyboard/touch, reduced-motion and print behavior, six lab LCP/CLS trials, four zero-violation axe-core scans, two page screenshots, two PDFs, reproducible artifact hashes, and review of actual screenshot content. **A missing axe bundle or blocked navigation must result in an incomplete FAIL receipt.** Pass of the local HTTP page still does not establish WordPress-rendered or production performance.

Additional release gates: reconcile Research Desk PR #158 source roles; resolve six photographic rights records and uncertain portrait ID; independent historical editorial signoff; actual WordPress/Assembler staging QA; founder authorizes release. No merge/deploy until all gates pass.

## Conversion-first single-path hypothesis (not a sale)
**Offer:** Apollo teacher-ready historical evidence casefile — *not yet merchant-verified; not currently authorized for sale*. **Audience:** secondary history/science educators reached by a Grok-owned Apollo video. **Path:** unique Grok asset ID/UTM → Apollo evidence chronology and NASA source register → one free classroom worksheet action → optional future, separately approved matching paid casefile **only after** a valid listing, rights, delivery, refund and attribution audit.

| Priority | Offer → step | Blocker | Change/experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| P0 | Teacher casefile → paid merchant order | No verified rights-cleared, fulfillable Apollo SKU | Claude/Growth to audit existing sellable catalog and eligibility before adding any paid CTA | BLOCKED; no confirmed merchant listing | Claude/Growth |
| P1 | Grok long-form/Short → Apollo → free worksheet | Real-document browser acceptance absent; Escape could fail after focus migration | R125 navigation gate and global Escape; isolated browser replay before any release | BUILT; 17/17 source contracts only; navigation probe BLOCKED | Apollo |
| P2 | Free worksheet → suitable paid casefile | No approved offer; source rights unresolved | Keep one free CTA; no unrelated product promotion | NOT ACTIVATED | Founder / Claude |
| P3 | Attributed paid order → net revenue per 1,000 qualified human sessions | No qualified-session/merchant-order reconciliation | Use existing #820 consent-safe attribution; cohort 7/30 days, refunds and fees | NOT COMPUTABLE; clicks/leads are not sales | Growth / Claude |

**Creative ownership:** Grok scripts/posts only with founder approval; Praxxis independently reviews Grok; Apollo owns on-site evidence-experience QA only. Do not change Grok's TASK-008 queue or infer any posts/sales are live.

**Release decision: STAGING HOLD.**
