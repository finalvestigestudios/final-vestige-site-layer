# EX2 — Focus Fieldbook claim-integrity release blocker (2026-11-08)

**DRAFT / HOLD / NO WORDPRESS OR TRACKING WRITES.** Stacked on PR #1607 exact parent `9699672ee19837a62ffde3074f273e0890fb1e80`; frozen PR #49 remains unchanged.

## Why the homepage funnel is affected

The archival homepage's contextual Focus CTA leads to the real WordPress Page **1579**. Its authenticated editor source includes a native `wp:jetpack/subscriptions` block (unchanged) and the inline script `fvf-gift-v2`, exact SHA-256 `f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7`. That script reveals the `fvf-gift` panel for **any nonempty** `subscribe` query parameter other than five hard-coded failure strings. In a read-only Chromium simulation, an arbitrary `?subscribe=anything` displays **“Your fieldbook is ready to download”** despite zero form interaction or subscriber creation.

This is a **misleading client-side success state**, **not** evidence that Jetpack created a subscription, sent an email, or recorded revenue. The Fieldbook file is an existing free asset; there is no claim of unauthorized disclosure. A second gap: the current word-boundary regular expression also treats a `is-subscriber-pending` class as success.

## Reversible candidate — review only

The accompanying native Node regression file reproduces the live behavior and exercises a possible narrowed UI condition: show the panel only when the Jetpack container carries an **exact** `is-subscriber` class token (including asynchronously added tokens). The proposed condition ignores all query-string values and rejects substring lookalikes. **It is a candidate, not an approved fix**: Jetpack may use a different signal for completed-but-unconfirmed signups. Claude must validate the real Jetpack state transitions and messaging before recommending any change to page 1579. Even a genuine client-side success state is NOT a verified confirmed lead.

## Evidence and boundaries

- Actual Page 6 source: seven chapters, 72 Margins entries, four existing images, Jetpack block; **no edits**.
- Actual Focus Page 1579 source: existing 52-page Fieldbook CTA, one Jetpack subscription block, inline `fvf-gift-v2` as above; **no edits**.
- `node experience2/review/focus_query_claim_gate.cjs`: native offline expectation suite for existing and proposed script, query controls, async class transitions and substring class tokens. The equivalent local 21-case Node suite PASS.
- Separate offline Chromium 144 fixture: **48/48 simulated browser cases PASS** at 320/390/768px for both scripts, with JS disabled and enabled. No WordPress Core, Assembler, real Jetpack/SMTP, lead capture, real media or staging backend in this fixture.
- Scope: client-side gift readiness messaging only. No additional chapter, art, merchant, affiliate URL, UTM, tracking script, popup or analytics vendor.

## Offer → funnel → blocker → change → evidence → owner

**Offer:** Existing free Seven Day Focus Fieldbook.  
**Funnel:** historical investigation → contextual Focus CTA → Jetpack subscribe request → verified confirmed email subscription → purchase/affiliate merchant report → realized net revenue.  
**Blocker:** URL query values alone can falsely imply a completed signup.  
**Change:** Reproducible fail-closed test plus a review-only exact-class-token candidate, not a production modification.  
**Evidence:** actual edit-context script fingerprint; 21 passing Node checks and 48 passing Chromium fixture checks, plus negative-query and substring controls.  
**Owner:** interim homepage QA; Claude owns Jetpack production code, lead attribution, receipt integrity; Grok/Praxxis own distribution.  
**KPI:** Qualified-human sessions → confirmed leads → verified paid conversions → net realized revenue per 1,000 qualified sessions. **No revenue or signup was observed in this sprint.**

## Release admission (all remain HOLD)

1. Execute the protected seven-chapter bundle in real, **isolated** WordPress Core with pinned Assembler theme; Personal plan has no native WP.com clone. Do not install on the production host.
2. With explicit authorization, test Jetpack success, pending-confirmation, already-subscribed, invalid-address and delivery states in an appropriate safe environment; do not create real subscribers in this review.
3. Independently verify 320/390/768/1440/1920, keyboard/no-JS/reduced-motion, 200% zoom, axe + manual WCAG 2.2 AA; transfer and decode genuine archival image bytes; measure Lighthouse/CWV honestly.
4. Verify rights of every image (including NYPL edited derivative), live Focus CTA behavior, and no-loss preservation of native Jetpack/72 Margins. Founder/QD/CI exact-SHA release approval required.

This PR contains **only offline test/review source**. Do not merge, deploy, publish, activate any affiliate, create subscribers, or change existing measurement.