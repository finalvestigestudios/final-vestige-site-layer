# Apollo Experience 2.0 R226 — ordered-link custody and reader journey

**DRAFT / ISOLATED STAGING / NOT LIVE.** Parent: R225 draft PR #1657 at \`a5d173cb3b7d27668a8842ff7b58f056d15dfd35\`. Engineering charter #150; revenue and attribution coordination #820; business charter #818. Homepage PR #49 and Research Desk PR #158 are untouched.

## Problem and change

R225 reconciles **56 external anchors, 11 distinct destinations, six source-ID bindings, and five chronology events**. However, a simple *set-of-approved-URLs* check can still pass if two non-source anchor destinations are swapped while the approved URL set and anchor count remain unchanged. For research readers, that creates a misleading source-to-claim relationship even though every resulting URL remains an approved NASA destination.

R226 adds an independently executable, strictly **read-only occurrence-level custody gate**. It records the ordered href, visible accessible name, source ID, target, and relationship attributes for **every anchor**. It rejects duplicate IDs, broken internal anchor destinations, orphan ARIA labels/descriptions, unnamed or hidden links, unapproved outbound URLs, scripting/form/geocoordinate injection, missing new-tab security attributes, and extra or missing commercial/editorial CTAs. Two adversarial tests confirm detection of (1) a two-way URL swap that evades R225's set/count census and (2) an intentionally false source-link label.

This is an **acceptance gate**, not production runtime protection. R225's separate PHP adapter still SHA-pins the rendered source files. No new JavaScript, tracking, source images, maps, offers, redirects, affiliate links, email, or WP code is introduced by R226. A further semantic editorial assessment remains essential.

## Reproduce

Requires a byte-identical locally extracted **generated-r225** directory from the R225 staging archive, Python 3, Playwright Chromium, and /usr/bin/chromium. Verify \`generated-r225/manifest.json\` SHA-256 equals:

\`4efaf0a57d38af349d44302905fbfdc8b8936ac8bbc04a2d7a61fb805ba93628\`

\`\`\`bash
python experience2/apollo-r226/qa/ordered_custody_gate.py --dist generated-r225 --out qa-r226-A
python experience2/apollo-r226/qa/ordered_custody_gate.py --dist generated-r225 --out qa-r226-B
\`\`\`

Local executable Git blob (checked against GitHub): \`c9a2df16ac92fc6fad7f6954c19a070a7a3ee742\`. The ordered-link occurrence baseline SHA-256 is \`ea8d4809f5dacb836a7f74f91a7fe622de69aacb1d28fc52343b669c4ce73519\`.

Two independent local executions passed: 10 Chromium contexts per run (320, 390, 768, 1440, 1920px, JavaScript enabled/disabled, native keyboard/touch disclosure), zero observed overflow, **10/10 matching screenshot hashes** and byte-identical structured QA receipts. Local R226 supplementary expanded fixture testing also passed 14 contexts at 320–1920px and verified five additional semantic mutants; that supplementary code is **not committed** and cannot be represented as exact-HEAD validation. No live HTTP navigation was possible (\`ERR_BLOCKED_BY_ADMINISTRATOR\`).

## Rights, source integrity and commercial objective

Official NASA Apollo 204 Review Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . It calls an electrical arc the most probable initiator, but **does not conclusively identify one ignition source**. NASA official brand/media restrictions: https://www.nasa.gov/nasa-brand-center/ . Citation and public historical access do not license a NASA endorsement, and no paid media use is authorized here.

One relevant action remains the **free original Apollo investigation**; a paid educator dossier is hypothetical and **not an approved, sellable SKU**. No Grok Apollo published asset ID, verified payment, affiliate conversion, or net revenue is established. Prioritize matching a real approved product and verifying checkout/fees/refunds before adding commerce. No fabricated campaign/conversion data.

## Blocked gates

Inherited R198 source ancestry, genuine axe-core, manual NVDA/VoiceOver, actual browser zoom, installed WordPress/Assembler and real HTTP flow, hosted CI exact-head, independent QA, reviewed rights for paid use, verified product/creator ID, and founder approval are outstanding. **No merge or release permitted.**