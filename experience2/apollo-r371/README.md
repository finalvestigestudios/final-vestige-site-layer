# R371 Apollo 1 Source-Custody Documentary Gallery

**STAGING-ONLY / DRAFT / HARD HOLD.** Apollo charter #150 and conversion #820. Stack is on R370 PR #2535, not frozen homepage PR #49 or independent Research Desk PR #158. No creator-task changes.

## Scope

- Four curated text-only documentary source cards: the original 1967 Apollo 204 Review Board report; later 102 deliberate Command Module test ignitions, described by NASA in 2018; the March 1968 mixed-gas launch-pad decision, described by NASA in 2018; and the 2022 NASA historical retrospective.
- Each has a dated source type, provenance, a limitation and a native HTML disclosure. A four-item source gallery is *not* a geospatial map. There are no coordinates, inferred edges, external images, logos, scripts, tracking, forms or commerce widgets.
- Exact source records are immutable at runtime. Altering a field, deleting, reordering or duplicating a record prevents the entire gallery from rendering. R367 must independently attest the upstream four-record chronology. The accessible fallback retains only the original free Apollo investigation link.
- Print-only citation anchors address a bug observed in local Chromium: closed native source drawers initially left the print PDF without NASA links. Corrected print PDF contains four distinct NASA destinations plus the single free editorial link.

## Staging integration, not executed

The source-gallery.php file registers the optional shortcode [fv_apollo_source_gallery_r371]. Authorized nonproduction WordPress staging would need R365, R367, source-gallery.php and staging-assets.php loaded before wp_enqueue_scripts. The optional bounded staging-assets.php handles the current queried singular post, nested reusable blocks, same-theme template parts, and only actually resolved matching block templates. It loads the CSS before normal head output when it finds the gallery. It does not guess template hierarchy, write WordPress data, or change the live Site Layer plugin. Nothing was installed or deployed.

## Reproduce from the repository root

1. php -l experience2/apollo-r371/source-gallery.php
2. php -l experience2/apollo-r371/staging-assets.php
3. php experience2/apollo-r371/qa/contract.php
4. php experience2/apollo-r371/qa/wp_contract.php
5. python experience2/apollo-r371/qa/browser.py

**2026-11-14 local execution:** source/claim contract 178/178 PHP assertions PASS; isolated WordPress API-stub contract 21/21 PASS; real Playwright Chromium 10/10 PHP-fixture contexts and 121/121 checks PASS (320 through 1920 CSS pixels, keyboard, touch, no-JS, forced colors, reduced motion and 4x root-font stress). Print PDF 2 pages, 4 unique NASA source links and 1 editorial link. Screenshots, PDF, test results and checksums are in the separate downloadable evidence bundle. PDF and screenshot binary bytes can change with Chromium version; the source archive can be rebuilt deterministically.

**Unexecuted release gates:** installed WordPress/Assembler, hosted exact-head CI, actual HTTP/CSP browser enforcement (navigation blocked by the environment), native browser 400% zoom, genuine axe-core, Firefox/WebKit, NVDA/VoiceOver, and actual p75 LCP/CLS/INP. The local PHP fixture is not a production Core Web Vitals test or WCAG certification.

## NASA source and rights review (2026-11-14)

- https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — original Board; most probable electrical arc, no conclusively established single ignition source.
- https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ — retrospective on 102 later deliberate Boilerplate 1224 ignitions.
- https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/ — March 1968 launch-pad atmosphere, not the orbital atmosphere.
- https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/ — 2022 historical context, not a primary Board record.
- https://www.nasa.gov/nasa-brand-center/ — NASA link policy and no implied endorsement. No NASA imagery, insignia, third-party media or identifiable-person likeness is represented as cleared for merchandise/commercial use.

## Conversion-first decision

One *proposed*, not launched journey: Grok's approved Apollo long-form asset (real published asset ID remains unverified) → this source gallery / chronology → existing free Apollo investigation → future founder-authorized educator product **only after** SKU, rights, price, checkout, delivery and merchant acceptance verification. Exactly one free editorial CTA exists. Research hypothesis: trustworthy source distinctions may increase qualified educator purchase intent, but no uplift is demonstrated. Claude owns compliant attribution and checkout engineering; Grok owns production/posting; Praxxis owns independent creator QA.

Net realized revenue per 1,000 qualified human sessions, 7/30-day paid conversion, lead-to-customer and fees/refunds are NOT COMPUTABLE from current evidence. Do not equate views, clicks, checkouts, or opt-ins to settled sales.

**Production HARD HOLD:** founder/QD release authorization, verified rights and payable offer, true staging WordPress acceptance, independent accessibility, CSP/HTTPS and hosted CI are required. No merge, deploy, WordPress content/settings write, affiliate activation, posting, email, analytics installation or spending is authorized.
