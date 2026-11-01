# Final Vestige Experience 2.0 — The Living Archive

**Status:** FOUNDATION / RESEARCH ONLY — no approved visual direction, no deployment, no production modifications.
**Date:** 2026-10-29
**Benchmark:** https://bluecorridors.org/ (caliber of craftsmanship only; do NOT copy copyrighted content, code, styling or layouts).

This is a separate planning branch, forked from `production`. It does NOT contain or modify the unmerged Vestige Assembly PR #49. The larger source, art-direction concept board, test snapshots, CSS token proposal and implementation files are also collected in the conversation artifact **Final_Vestige_Experience_2_Foundation.zip**. Request or attach that ZIP when resuming with Claude; it is not stored in this Git branch.

## North star

**Make the evidence itself the experience.** Every significant movement, map, comparison, annotation and transition must reveal a verifiable relationship. The desired result is a cinematic, premium historical research experience with a transparent source trail—not an over-animated content magazine.

## Verified groundwork

- Blue Corridors won the 2026 Webby Award in Best Data Visualization. The benchmark is its purposeful layering of evidence, source attribution, storytelling and usable explorer UI.
- Ode's own project study explains its use of a shared visual grammar, visual layers, cited research, authored narrative and datasets that can grow over time.
- Connected WordPress snapshot: finalvestige.com is WordPress.com Atomic using the Assembler theme, with 61 posts, 79 pages, 125 media assets, and 18 active plugins at inspection. Treat counts as a point-in-time snapshot, not guaranteed live.
- Actual homepage candidate in PR #49 includes an authentic four-fragment hero, 72-item Margins Wire, real NASA Apollo 1 investigation walkthrough, NYPL evidence inspector/slider, six Worlds, Focus Fieldbook and Dispatch. Preserve this investment and its existing safety controls.
- Homepage candidate styles use dark surfaces (#090a0a/#0c0d0d), antique gold (#b8955e/#c7a66c), parchment (#f4efe6), display Fraunces, and Inter; the Assembler theme presets themselves remain generic. Favor a namespaced token system.

## Creative directions (no founder selection yet)

**A. Black Dossier:** cinematic text, authentic archival photo, dark editorial framing, focused story chapters. *Recommended for first visual exploration.*

**B. Museum After Hours:** serious exhibition feel, warm paper evidence plates, large catalogued objects, museum labels and quiet navigation.

**C. Observatory:** cartographic/technical lines, source-network and geography-first exploration, precise legends, data layering without decorative noise.

Recommended eventual blend: A for the homepage's emotional architecture, B for evidence plates, C for a future Atlas—**not all three implemented simultaneously**. Founder chooses primary direction after viewing desktop/mobile compositions.

## Signature experiences

1. **Evidence Unfolds** (ship first): one outstanding, source-grounded investigation chronology, provisionally the published *The Hatch Opened Inward* / Apollo 1 article already used in PR #49. 5–7 real, cited editorial stages; source drawer; readable no-JS narrative; meaningful deep links. Source and image rights must be reverified before use.
2. **Research Desk:** reusable source inspection for maps, photos and documents, with zoom, provenance, original URL, rights, alt/transcripts, and explicit separation of 'What the document says' from 'What Final Vestige concludes'.
3. **Evidence Atlas** (build after data verification): a curated, accessible map/list of published geolocatable investigations. First create a source-verified location catalog, 6–12 reviewed entries, then decide whether SVG/map tiles/WebGL are justified. Do not generate speculative geocodes or draw relationship lines based only on proximity.

## Engineering + editorial invariants

- WordPress remains canonical for stories, URLs, taxonomies, subscription blocks and evidence links.
- Site Layer offers optional, progressively-enhanced UI; essential information remains in semantic HTML when JS is absent.
- No paid SaaS by default; no extra heavy framework without cost/license/accessibility/performance case.
- Every artifact: title, original institution/link/ID, date or range, rights, caption, alt/transcript, supporting claim. Every map feature: coordinates/geographic precision, authoritative source and approval. Every inferred relationship requires an explicit editorial basis.
- Honor reduced motion, keyboard, touch, zoom and screen readers. No scroll traps. A noninteractive stage must never advertise interactive ARIA or block normal mobile scrolling.
- Preserve Focus Fieldbook and actual Jetpack Dispatch subscription behavior. Social content drives engaged visitors toward stories first, then useful resources and relevant products.
- No additional edits to PR #49, no new WordPress deployment, no claims that unpublished code already shipped.

## Build order

**0 — Measure & choose:** Capture real live-site + PR candidate screenshots at 360/390/768/1024/1440/1920, record baseline Core Web Vitals where possible; establish actual media rights, show three distinctive compositions, obtain founder selection.

**1 — Tokens & components:** Build namespaced CSS and 3–4 reusable content-first primitives. Test static/JS/partial-error states.

**2 — One flagship:** Convert one already-published investigation into a source-grounded interactive chronology; full source and human editorial QA.

**3 — Homepage integration:** Art-direction pass, not wholesale replacement, preserving existing routes, dynamic queries, conversion and accessibility.

**4 — Atlas catalog:** Verify places/sources first; accessible list before interactive map.

## Release gates

- WCAG 2.2 AA and independent keyboard/touch/screen-reader validation.
- Google 'good' CWV targets **LCP <=2.5s, INP <=200ms, CLS <=0.1** at 75th percentile; these are targets, not measured current values.
- Visual screenshot comparisons at 360,390,768,1024,1440,1920; no horizontal overflow and no broken media/contrast.
- Repeatable source manifest, verified citations, legal media usage, no factually misleading relationship design.
- Independent QD at exact candidate head/package SHA; hosted CI green; founder-approved governed deployment, rollback and post-deployment verification.

## Starter sources

- https://bluecorridors.org/
- https://ode.partners/en/projects/blue-corridors
- https://ode.partners/en/insights/beneath-the-surface-a-deeper-dive-into-our-work-on-blue
- https://winners.webbyawards.com/2026/websites-and-mobile-sites/features-design/best-data-visualization/364937/wwf--blue-corridors
- https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49
- https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/
- https://web.dev/articles/defining-core-web-vitals-thresholds
- https://www.w3.org/TR/wcag/

## Handoff note

When Claude usage returns, start by reading this foundation and the conversation ZIP. Verify current PR #49 release status independently without touching its head. Then focus on screenshot-grounded design options, actual source asset rights, founder art-direction selection, a single high-quality flagship, and separate scoped PRs. This document is not a release authorization.