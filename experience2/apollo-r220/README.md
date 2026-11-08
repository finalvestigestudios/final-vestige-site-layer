# Apollo R220 — exact-source accessibility and source custody (staging only)

**Release: STAGING HOLD. Nothing in this branch is live or install-approved.** Relates #150, #820 and #818. This is a child of draft R219 PR #1616, not homepage PR #49 or Research Desk PR #158.

## New executable source
`qa/semantic_gate.py` (Git blob `e948d6a273b3d565b2126a4bc4dc4d39c4c580d8`) verifies the exact upstream R219 gate Git blob `99e4ee33e69ddeee011b33b25ab6c54fef8c8e89`. It **runs the parent gate**, which re-builds pinned R217 PHP/HTML/CSS and performs 16 true mobile-viewport browser contexts at widths 320–1920px, including eight actual JavaScript-disabled cases.

R220 adds ten independent Chromium browser contexts across widths 320, 390, 768, 1440 and 1920, each with JavaScript enabled and disabled, forced colors and reduced motion. Checks use Chromium's **native CDP accessibility tree**, actual Tab+Enter interactions through skip navigation and the single free-investigation route, a 200% CSS zoom **layout stress** (not browser zoom), 44px CTA touch size, no horizontal overflow, valid internal anchors, pinned NASA identifier-to-URL custody and explicit allowed external hosts.

## Local execution and artifacts
Prepare a workspace containing `apollo-r216/build_r216.py`, verified R216 `dist/` files and manifest (SHA-256 `a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128`), `apollo-r217/build_r217.py` (Git blob `769b574c14a37220d522e37ceaea01044630e3e7`), R217 generated `dist/`, and the exact R219 `r219/qa/mobile_gate.py`. The R217 generated manifest is pinned to SHA-256 `90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72`.

Run:
```sh
python experience2/apollo-r220/qa/semantic_gate.py --workspace /path/to/pinned-workspace --output /tmp/apollo-r220-QA
```
Requires Python Playwright, local Chromium (`/usr/bin/chromium`), PHP. Network services and site writes are not required. The fixture contains complete HTML viewport metadata, real PHP-rendered markup and pinned CSS.

**Observed local runs on November 8, 2026:** 2 independent invocations PASS; R219 16/16 responsive contexts and R220 10/10 native AX/focus/source/forced-colors contexts per invocation; 16/16 parent and 10/10 new screenshot hashes match between runs. No JavaScript injected by the components. R219 locally measured fixture LCP/CLS; these are **not** production Web Vitals or field performance.

## Evidence and unresolved release gates
- NASA Apollo 204 Review Board remains the technical source. A probable electrical arc is **not** a conclusive specific ignition-source identification. Photographic catalogs must not be treated as ignition footage.
- Commercial photo/astronaut-likeness use and endorsement are **not certified**; this code introduces no imagery and no paid CTA.
- Grok has not supplied a verifiable published Apollo `asset_id`; no attribution passthrough or new tracking is authorized.
- No approved sellable Apollo educator-dossier SKU, authenticated merchant order, refund/fee ledger or qualified-human cohort exists. Revenue per 1,000 qualified sessions is **not computable**.
- **NOT TESTED:** genuine axe-core, NVDA/VoiceOver, actual browser zoom, installed WordPress/Assembler theme, production HTTP navigation/CDN/CSP, hosted CI on exact new HEAD, independent QD review or R198 canonical source ancestry.
- Site Layer homepage PR #49, Research Desk PR #158, live WordPress, Grok's content queue, email and commerce remain unchanged.

**Conversion hypothesis:** Grok long-form audience → verified NASA Evidence Atlas → one adjacent **free** original investigation CTA → rights-cleared educator evidence product only if commerce validates an actual SKU and checkout. CTA-path integrity was tested; actual sales impact was **not** established.

**Owners:** Apollo independent code/QA; Grok content/distribution; Praxxis external creator evidence review; Claude production/analytics/checkout engineering; founder commercial and release approval.
