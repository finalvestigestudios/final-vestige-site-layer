# Apollo R203 — source navigation and reader-language staging

**Draft only. No WordPress installation, homepage edits, deployment, or paid offer.** This additive layer is based on R202 / PR #1506 at `ad10ccf0c0df350fc5ba0bfa4986957c11370e5d`.

## Change
Remove seven remaining component/development labels from public-facing text (including `ChronologyRail`, `EvidencePlate`, `SourceDrawer` and internal Research Desk prompts). Introduce one concise, non-promotional two-source comparison near the print source ledger: NASA's Apollo 204 Review Board for the technical investigation and S67-21294 for the January 28 aftermath photograph. No photographs copied, no speculative geodata, no affiliate/checkout, and no new JS, forms, or tracking. Preserve original investigation as the **single CTA** and keep eight native source disclosures and four chronological records.

## Reproduce from a local ancestor checkout
Requires Python 3, BeautifulSoup, PHP, Chromium, Python Playwright; all prior additive Apollo builder scripts from R191–R202 must be available.

```bash
python experience2/apollo-r203/build_r203.py
python experience2/apollo-r203/qa/gate_r203.py ./r203-a
python experience2/apollo-r203/qa/gate_r203.py ./r203-b
```

## Test evidence — local, not installed WordPress
Builder Git blob `9d3d5764508fbf48362ae82f9e577602e68c8101`; QA blob `a04b801491a1d1b539f3fe7e2d1991671a267433`. Executed byte-identical local scripts. PHP normal/print/late-render fallbacks passed. Chromium 144.0.7559.96: two independent runs, 12 contexts/run, 320–1920 px, no-JS, touch, keyboard, reduced-motion, forced-colors, simulated 200% CSS zoom, 48 chronology journeys/run, 24 native disclosure toggles/run, 11/11 adversarial mutations rejected, four UTM policy cases, no horizontal overflow, and 12/12 screenshots hash-matched. Local fixture PerformanceObserver LCP 68–168 ms and CLS zero; these are **not** production Core Web Vitals.

## Explicit HOLD
Canonical GitHub R198 builder blob `57ef73d5719662a1b3647536a0eace5fb65bac4a` **differs** from the R198 file in the inherited local R202 package (`2e09257cbd0b32a93f2e7e034a84685d93ed93f5`). A full exact-GitHub-ancestor clean rebuild is **not** verified. Also required: installed WP/Assembler staging, genuine axe-core (not run), NVDA/VoiceOver, actual zoom, real destination/network and CSP/CDN checks, exact-head hosted CI, independent review, founder release approval. No paid Apollo SKU or merchant-confirmed net revenue is verified; the public action remains the free investigation.

Refs #150, #820 and charter #818. Grok owns creator production; Praxxis owns external creator QA; Claude owns production engineering. Homepage PR #49 and Research Desk PR #158 untouched.
