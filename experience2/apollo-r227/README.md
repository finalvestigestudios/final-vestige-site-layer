# FV Apollo 1 R227 — PHP lifecycle / Evidence Atlas release gate

**Draft only · independent staging · NOT LIVE.** Base is R226 draft PR #1665 (`d75fd6f6ee36c286e26b1e2221d8ab65fae4fa38`). No changes to homepage frozen PR #49, Research Desk #158 or production WordPress. Governance: #150, conversion #820, charter #818.

## Why this exists

R226 verified ordered NASA source links in offline HTML. R227 checks an **additional real failure class**: whether the SHA-pinned Apollo PHP shortcode/asset loader behaves safely across direct posts, WordPress-style nested synced blocks, missing/repeated references, cycles, duplicate shortcodes, after-`wp_head` late rendering and mutated evidence files. This uses the actual pinned PHP adapter from generated R225. It does **not** claim an installed WordPress integration.

## Exact reproducibility

Use the unaltered `generated-r225/` folder from the R225 artifact (`Apollo_R225_Exact_Rendered_Crosswalk_Staging_QA.zip`), with `manifest.json` SHA-256:

`4efaf0a57d38af349d44302905fbfdc8b8936ac8bbc04a2d7a61fb805ba93628`

```bash
php -l experience2/apollo-r227/qa/wp_lifecycle_shim.php
python experience2/apollo-r227/qa/wp_lifecycle_browser_gate.py --dist generated-r225 --out qa-r227-A
python experience2/apollo-r227/qa/wp_lifecycle_browser_gate.py --dist generated-r225 --out qa-r227-B
sha256sum qa-r227-{A,B}/receipt.json
```

The Python runner validates **every R225 generated file** against its manifest before testing. It executes nine PHP lifecycle scenarios and five **disposable-copy** corruption/missing-file probes; all must fail open to the **one free original Apollo investigation**, never to an unapproved checkout or a corrupted Atlas. The Chromium acceptance uses the **actual PHP-rendered bytes** with CSS, ten independent contexts (320/390/768/1440/1920px × JS enabled/disabled), live native disclosure input, touch-target, anchor/ARIA, external-request and overflow assertions, screenshot hashes and one native accessibility snapshot. The two local runs passed; ten screenshot hashes and receipt SHA matched. Local reproducible receipt SHA-256: `9e02ec53fb8d698db6b21c9282ca13c317c15a2158845b72ff93e7d111553a8f`.

**Explicit limits:** The `parse_blocks()` function in this PHP shim parses **test fixtures**, not actual WordPress Gutenberg blocks. Browser testing uses `page.set_content`; direct HTTP navigation remained blocked (`ERR_BLOCKED_BY_ADMINISTRATOR`) and no installed WordPress, Assembler, axe-core, NVDA, VoiceOver, browser zoom, trusted production LCP/CLS, hosted CI or merchant checkout tests occurred. No new NASA image rights are established. The inherited R198 source-ancestry discrepancy is open. These tests narrow the release risk without satisfying release approval.

## Evidence → action and conversion gate

Selected historical flagship: Apollo 1, January 27, 1967. Official technical anchor: [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); the exact ignition source was not conclusively established. [NASA brand/usage rules](https://www.nasa.gov/nasa-brand-center/) are separate from public historical citation. Do not invent coordinates, film footage or media permissions.

**One honest visitor pathway** for a future *verified* Grok Apollo long-form asset: permitted social link with real `asset_id`/UTM → Apollo Evidence Atlas with NASA source limitations and chronology → **free original Apollo investigation**. A rights-cleared **educator evidence dossier** is a *hypothetical* paid next step; no live SKU, approved license, completed purchase or attributable Grok asset has been verified, so there is **no paid CTA**. Grok owns scripts/distribution, Praxxis owns creator QA/TASK-008, Claude owns core production analytics, Apollo owns this isolated browser gate. Issue #820 owns qualified-human session → source-linked lead → merchant-verified paid order → fees/refunds → realized net revenue, 7/30-day cohorts; clicks and unverified sessions are not sales.

**Release: HARD HOLD.** Remaining: independent exact-head GitHub CI, R198 ancestry reconciliation, genuine axe and manual assistive-technology testing, real WordPress/Assembler shortcode/asset acceptance, actual HTTP navigation/performance and founder approval. No live writes, emails, publishing, affiliate activation or spending.
