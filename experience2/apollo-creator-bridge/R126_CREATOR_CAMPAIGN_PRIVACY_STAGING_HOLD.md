# Apollo R126 — Creator-campaign continuity and source-exit privacy

**2026-11-04 / independent Apollo staging / Issue #150 / commercial priority #820 / charter #818**

## Why this release exists

Apollo 1: *Fourteen Seconds, More Than One Failure* is a proposed Grok-owned YouTube long-form / Shorts discovery destination, not an already published Grok campaign. Its most relevant visitor is a secondary history or science educator who wants a trustworthy, source-grounded teaching exercise. The only currently authorized on-site action is **Review the free classroom evidence exercise**. A teacher-ready paid casefile remains an unverified product hypothesis; no merchant CTA, price, newsletter duplicate, affiliate, tracking pixel or order event is activated.

R125 made true browser navigation a requirement rather than accepting injected HTML. R126 makes that stronger by testing a **synthetic** Grok-style campaign journey: real document navigation with standard UTMs → one free worksheet CTA → same original URL query and hash destination, while detecting automatic outbound requests, browser persistence and source-link referrer leakage.

## Actual implementation (isolated, stacked on R125 only)

1. `landing-preview.html`: all 22 outgoing official NASA source anchors now have `rel="noreferrer noopener"`. This prevents external NASA source clicks from receiving the synthetic campaign referrer. Source URLs, text, chronology, no-JS links and photographer credits are unchanged; the independent FV original-article link is left alone. This does **not** create first-party analytics or claim the visitor consented to anything.
2. `qa_r113_print.py`: an additional **real-navigation-only** `audit_campaign_boundary` checks at 390px and 1440px, using `utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_youtube_lf_qa001`. It requires a 200 navigation with exact URL/timing via R125, preserves the query during the free CTA hash navigation, finds all 22 external NASA link protections, detects unexpected network requests and confirms no cookies/session/local storage. The main acceptance receipt cannot be complete without both results.
3. `test_r126_campaign_privacy_contract.cjs`: 11 source + mutation contracts assert that the actual HTML and browser runner preserve privacy, no signup/checkout, original source links and release identity gates. Mutation tests confirm removal of one `noreferrer` or an unauthorized link host fails the audit.
4. This release-hold record supplies the independent QA and creator-to-product handoff. No homepage, Research Desk PR #158, production WP, analytics, Grok queue or merchant service was changed.

## Evidence classification (do not conflate)

- **BUILT / COMMITTED:** isolated GitHub branch with actual Apollo HTML and true-navigation Playwright QA extension; no production deployment.
- **TESTED source-level:** 11/11 regression/mutation contracts executed via V8 using Node-compatible `test`, `assert`, `fs` and `URL` shims against the actual GitHub branch blobs. This is **not** native Node or hosted CI.
- **TESTED browser environment, not Apollo:** Chromium 144.0.7559.96 launched; loopback HTTP, file and data URI `page.goto` each returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` on the current authorized runner. The reproducer and receipt are retained separately. `page.set_content` is technically available but **must not** be used to claim acceptance.
- **NOT TESTED:** R126 actual-page campaign replay, full-page Playwright/axe, performance LCP/CLS, reproducible Apollo screenshots, page PDF, WordPress/Assembler integration, screen-reader and device acceptance.
- **NOT VERIFIED:** six photograph-by-photograph republication permissions (0/6), provisional portrait identifier `S67-19766`, Research Desk source-role editorial reconciliation, merchant product eligibility, Grok asset traffic, subscriber/order/commission attribution or net revenue.
- **LIVE:** none of R126.

## Reproduction when a trusted runner allows actual navigation

```bash
node --test experience2/apollo-creator-bridge/test_r125_actual_navigation_contract.cjs
node --test experience2/apollo-creator-bridge/test_r126_campaign_privacy_contract.cjs
python experience2/apollo-creator-bridge/qa_r113_print.py \
  --chromium /usr/bin/chromium \
  --axe /path/to/approved/axe.min.js \
  --out /tmp/apollo-r126-real-browser
```

The actual-page release receipt must show two successful synthetic campaign runs **in addition** to 14 width/JS modes (320–1920px), six real-document LCP/CLS lab trials, four axe scans, correct keyboard/touch/reduced-motion behavior, screenshots/PDF and source/head identity. Keep exact SHA and artifacts. A network-blocked trial, absent axe bundle or missing real navigation is a FAIL/INCOMPLETE result; do not substitute fixture screenshots. WordPress-hosted page remains a separate gate.

## Flagship and conversion hypothesis, not a product launch

- **Creator / audience:** Grok owns any Apollo long-form and Shorts content; Praxxis independently reviews rights, hooks, assets and source alignment under existing TASK-008. This Apollo lane does not write to that Drive queue.
- **Landing / proof:** NASA Apollo 204 Review Board technical report; five bounded clock points with ignition uncertainty; separate six-source photographic custody register and clear 2017 retrospective labels; no fabricated Atlas geographic pins.
- **Relevant action:** one nonintrusive no-signup classroom evidence exercise, accessible beneath the source trail. No unrelated preparedness/Mind sales pitch in this tragedy.
- **Future conditional paid bridge:** *only if* Claude/Growth verifies a live, rights-cleared, fulfillment-tested Apollo teacher casefile with real pricing/refunds and founder approval, add a clearly separated optional casefile CTA **after** the free worksheet (not beside findings or chronology). Never label a free worksheet interaction as a purchase.
- **Testable hypothesis:** verified educator sessions that visit the source register and obtain the worksheet will have greater *future* teacher-casefile purchase rate than eligible sessions that don't, conditional on a real product, privacy-safe consent and comparable traffic. This is not a validated effect; avoid causal claims from self-selected tiny cohorts.
- **Measurement:** Grok immutable `asset_id` / `utm_content` + `utm_campaign` → qualified human landing session → relevant CTA → independently confirmed lead (if applicable) → source-confirmed paid merchant order → refunds and fees → realized net revenue. Report 7/30-day cohorts, net revenue per 1,000 qualified human sessions, true paid conversion and small-sample warnings; labels `UNOBSERVABLE` until data exist.

## Priority grid — OFFER → STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Order | Offer / step | Blocker | Change or experiment | Evidence | Owner |
|---|---|---|---|---|---|
| P0 | Apollo educator casefile → verified paid order | No matching verified sellable SKU, rights, pricing, delivery/refund receipt | Inventory current Payhip inventory; independently verify eligibility and fulfillment before adding paid CTA | **BLOCKED / no merchant confirmation** | Claude / Growth; founder commercial release |
| P1 | Grok video → Apollo evidence landing → free worksheet | Source exit can leak referral; campaign continuity untested under navigation policy | R126 `noreferrer` hardening + true-browser dual-viewport campaign QA | **BUILT, 11 V8 contracts pass; browser BLOCKED** | Apollo QA |
| P2 | Free worksheet → optional matching paid kit | No verified offer, no approved commercial module | Hold optional paid module until merchant audit + independent rights review | **NOT ACTIVATED** | Founder / Claude |
| P3 | Paid orders → net revenue per 1,000 qualified human sessions | No independently reconciled orders, sessions, or refunds | Reuse #820 event/UTM framework; avoid duplicate instrumentation | **NOT COMPUTABLE** | Growth / Claude |

**RELEASE GATE: STAGING HOLD.** No merge, WordPress write, deployment, social post, email, affiliate activation or paid spend. Research Desk PR #158 and homepage PR #49 remain frozen/unmodified by this lane. Cross-reference #150 and #820.
