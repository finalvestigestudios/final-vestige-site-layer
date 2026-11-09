# EX2 / Focus destination: source-pinned repair candidate (2026-11-08)

**DRAFT ONLY · NO WORDPRESS WRITES · RELEASE HOLD · NOT A CONFIRMED LEAD TEST**

## Verified production source (read-only)
- Homepage Page 6 is **already published**: authenticated editor modified 2026-11-05 12:07:24 site-local; seven-chapter investigation, 72 Margins, contextual Focus routes and native Jetpack block remain present. Preserve this publication; do not replace Page 6 from the old Playground bundle.
- Focus Page 1579 is published, modified 2026-11-05 17:44:02 site-local, with one native \`wp:jetpack/subscriptions\` block and the existing complete 52-page Focus PDF destination.
- The live \`<script id="fvf-gift-v2">\` matched SHA-256 \`f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7\` on this run. It reveals \`#fvf-gift\` for arbitrary \`?subscribe=anything\`, without any form action or confirmed Jetpack state.
- Additional false positive: \`/\b is-subscriber \b/\` boundaries (without spaces as shown) also match \`is-subscriber-pending\`. See PR #1613's independent reproduction; this PR is its *code-level follow-up*, not an additional UX chapter.
- Reading the public front end does **not** verify confirmed Jetpack subscribers, PDF delivery, checkout, affiliate sales, or revenue.

## What is built
\`tools/experience-2/patch_focus_gift_review_only.py\` is a local, fail-closed **candidate generator**. It consumes a **read-only authenticated JSON export that the engineer already possesses**, checks site page id/status and exact original script hash, requires one native Jetpack block and unchanged PDF, and replaces **only** the JS inside the existing \`fvf-gift-v2\` element. All other editor bytes are preserved. It does not call the network, connect to a CMS, install a plugin, or publish.

The proposed replacement ignores all URL query values. It displays the download panel only on the *exact* \`is-subscriber\` class token on the Jetpack form container, including observed class mutations. This is **not** proof that an address was confirmed or even that Jetpack's real production markup follows that class contract. In particular, a pending/unconfirmed form state may not carry it. Actual Jetpack runtime states and fieldbook delivery MUST be independently established before any release.

Example **offline only**, with a private local JSON file you must NOT add to git:

\`\`\`bash
python tools/experience-2/patch_focus_gift_review_only.py \
    /secure/local-readonly-page1579.json \
    --candidate /secure/local-focus-candidate.blocks.html \
    --receipt /secure/local-review-receipt.json
python tests/experience-2/test_focus_gift_review_patch.py
node tests/experience-2/focus_gift_review_vm.cjs \
    /secure/review-script-only.js
\`\`\`

The Node test requires \`/secure/review-script-only.js\` to contain only \`REVIEW_SCRIPT\` from the generator, not the entire Gutenberg page. In-app/production Jetpack confirmation is not established by VM or local Chromium.

## Local verification (do not conflate with GitHub CI)
- 16/16 Python source-preservation / adversarial checks in the local synthetic test harness; 26/26 Node VM script-state checks. Source SHA pinned; false arbitrary-query success reproduced; exact-class fallback accepted; substring/pending class rejected; asynchronous class changes simulated. These are **local-sibling** test files that exercise the same candidate; re-run the committed exact-head tests independently.
- 32/32 local Chromium synthetic-fixture assertions across 320, 390, 768, 1440 and 1920px, JavaScript on/off, pending and exact-class mutation controls. The browser fixture uses \`about:blank\` and a simulated URLSearchParams return value because this environment blocks file/HTTP navigation. **Neither the screenshots nor these tests are real WordPress, actual URL navigation, Jetpack backend, 200% WordPress zoom, axe or CWV evidence.**
- **No WP production writes, synthetic subscribers, actual email addresses, new tracking, affiliate links, deployments, or purchase events.**

## Conversion priority and next decision
Offer: existing free **Seven Day Focus Fieldbook**.  
Funnel: homepage/investigation -> contextual Focus click -> actual Jetpack form -> **provider-confirmed lead** -> relevant approved offer -> **merchant-confirmed paid order** -> fees/refunds -> **realized net revenue**.  
Blocker: URL-only state can counterfeit a download-ready signal, contaminating UI trust and any naive conversion interpretation.  
Change: source-pinned, byte-preserving proposed repair with negative controls.  
Pass evidence: local synthetic preservation and browser VM cases, plus fresh authenticated live source pin.  
**Failed/pending gate:** no authorized Jetpack success/confirmation/delivery test. No verified sale or subscriber count.  
Owner: interim homepage QA creates reviewed source; Claude owns Jetpack production implementation and privacy-preserving attribution; Grok/Praxxis own campaign inventory; founder approves release.

Final release admission remains **HOLD** for genuine Jetpack states, no-JS/keyboard/200%-zoom/mobile WordPress staging, actual media transfer, WCAG 2.2 AA with axe/manual review, Lighthouse measurements and independent QD/CI exact SHA. Do not touch frozen PR #49, live Page 6 or Page 1579 before authorized release. No fee or plan upgrade.

## Rights and campaign scope
Historical media, artwork, 72 Margins records and the 52-page PDF are unchanged. Do not introduce unverified Inspire3 benefit or affiliate terms. Grok \`asset_id\`/\`utm_content\` remain campaign-owner data per Issues #820/#818 and TASK-008; this proposal deploys no attribution or new scripts beyond the existing gift-state callback.
