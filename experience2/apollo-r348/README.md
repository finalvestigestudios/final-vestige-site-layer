# Apollo R348 — NASA source-page custody drawer (research only)

Independent Apollo 1 Experience 2.0 work: Issue #150, commercial #818/#820. This branch stacks on R347 PR #2410 at 2da97b0054ca962eaa7aa38b5772a989acf07e80. Do not edit frozen homepage PR #49 or Research Desk owner PR #158.

## Implementation

- New shortcodes: fv_apollo_source_drawer_r348 (standalone crosswalk) and fv_apollo_experience_r348 (existing combined experience plus source custody).
- Derives 13 evidence references directly from the earlier reviewed R347 canonical PHP ledger; groups them into eight exact NASA page identities based **only on shared source URLs**. No inferred geographic/cause relationships or photo-based ignition claims.
- Fixed allowlist of eight source-page addresses. A spoofed NASA host, new unreviewed NASA page or executable URL is not linked; the underlying evidence description and boundary remain visible with a clear quarantine notice.
- Accessible native details/summary with source URL visible even when details are closed. 320–1920px layouts, keyboard/touch/no-JS, forced colors, reduced motion, enlarged text, unique instance IDs and print-only custody twins for PDFs.
- Read-only WordPress pre-head asset resolver for direct and bounded nested reusable blocks. Exactly one existing free-investigation continuation action in the combined experience; no new commerce links, analytics, media embeds, pins or paid services.

Original NASA sources: https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html , https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html , https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html . Later history: https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/ . NASA photo accession pages are contextual references only, not independent media-rights clearance or proof of an exact ignition source.

## Executed local tests

Run with PHP 7.4+, Python, system Chromium, Playwright, PyMuPDF:
- php -l experience2/apollo-r348/source-custody.php
- php experience2/apollo-r348/qa/preflight.php
- python experience2/apollo-r348/qa/acceptance.py

PHP syntax PASS; WordPress **stub** and negative mutation controls 15/15 PASS. Real Playwright Chromium 10/10 contexts across 320/390/768/1440/1920 logical CSS px with JS on/off, native keyboard/touch disclosures, 400% text, forced colors, reduced motion and duplicate instances PASS. A 320px/400%-text overflow was discovered, CSS fixed and retested. Browser-generated PDF at 390px preserves full custody and evidence boundaries when source drawers are closed and R347 filtered to Photos only. Local PerformanceObserver readings are fixture-only, not production CWV.

**Unverified release blockers:** genuine axe-core, screen-reader acceptance, Firefox/WebKit, installed WordPress/Assembler/CDN, native HTTP/CSP, exact-HEAD hosted CI, NASA/editorial rights clearance, published Grok asset and landing URL, authenticated payable Apollo product, independently confirmed paid orders/fees/refunds, qualified-human attribution, founder/QD authorization.

## Business decision

Offer: a future rights-cleared Apollo educator dossier, ONLY after commercial verification. Audience: evidence-curious educators/researchers arriving from Grok Apollo long-form. Journey: Grok film → documented NASA experience → existing free Apollo investigation → separately approved relevant paid educational offer. The hypothesis that inspectable provenance improves purchase trust is unmeasured. Claude owns measurement/commerce under #820; Grok owns social/video and Praxxis owns creator review through TASK-008. This component does not add an unrelated purchase CTA or duplicate analytics.

**HARD HOLD: no deployment, merge, WordPress writes, merchant activation, posting, email, affiliate or spending changes.**
