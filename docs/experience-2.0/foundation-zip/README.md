# FINAL VESTIGE EXPERIENCE 2.0 — THE LIVING ARCHIVE

**Status:** Design research / foundation sprint, 2026-10-29. **Not approved for implementation or production.**
**Owner:** Final Vestige Studios. **Reference benchmark:** https://bluecorridors.org/.
**Release constraint:** Do **not** alter, merge, or deploy the independent pending PR #49 as part of Experience 2.0.

## North star

> Make the evidence itself the experience. Every movement, map, image, contrast, and transition should reveal a verified relationship a conventional content page cannot communicate as clearly.

We are not cloning Blue Corridors or borrowing its branded assets, UI, colors, artwork, behavior code, or scientific data. We are adopting the **caliber** of its narrative design, progressive disclosure, visual hierarchy, attribution, and meaningful layered visualization, while preserving Final Vestige's black/charcoal, muted gold, parchment, investigative editorial identity.

## Decision already supported by research

Build the first flagship as one **source-grounded interactive investigation** (provisional candidate: the existing published *The Hatch Opened Inward* / Apollo 1 article). The content, evidence stage sequence, and NASA assets already have a path into our current Site Layer work. Advance the **Evidence Atlas** as a second flagship once a verified geospatial content catalog exists. Do not build an empty globe or infer coordinates from stories.

## Three creative directions to choose from

1. **The Black Dossier** — monolithic type, archival photography, ink-dark surfaces, restrained gold, dramatic editorial pacing. Recommended starting direction.
2. **The Museum After Hours** — precise exhibition labels, warm neutral paper displays nested in darkness, larger artifacts, calm curatorial authority.
3. **The Observatory** — measured cartographic geometry, coordinate grids, geographic context, relationship networks, minimalist data overlays.

They share a common design system and information architecture. Founder visual selection is required before production coding. See `02_Creative_Directions.md` and the local `concept-board.html` (visual **study**, not site clone or final mockup).

## Current, independently checked facts

- Production host: `https://finalvestige.com`; WordPress.com Atomic; Assembler theme; existing WP Site Layer plugin, governed deployment bridge.
- WordPress site snapshot retrieved 2026-10-29: **61 posts, 79 pages, 125 media**, 18 active plugins, 966 monthly views reported by the site metadata endpoint at read time (not a validated analytics KPI).
- Assembler preset typography is Inter; preset colors generic black/white/gray. Existing site-layer homepage is heavily custom styled using #090a0a / #0c0d0d, gold #b8955e/#c7a66c, parchment #f4efe6, and Fraunces display type, meaning design tokens currently straddle theme presets and custom per-section CSS.
- PR #49 (unmerged) builds the Vestige Assembly homepage: 72-item Margins Wire, four-evidence-fragment hero, free Focus Fieldbook CTA, six Worlds, Apollo 1 investigation walkthrough, NYPL map loupe, historical comparison slider, current content, and intact Dispatch subscription mechanism. This is an **asset to preserve**, not something to discard.
- WordPress content includes Investigations, the Public Record, Labs, History Lab, the Exchange, Focus, many research pages, and currently published historical reports. Do not replace existing URLs, taxonomy or subscriptions on a design whim.
- Final Vestige's existing acquisition goal emphasizes a content/social → investigations → useful free resource → subscription / relevant product path. Avoid intrusive monetization inside research evidence.

## Working files

- `01_Benchmark_and_Gap_Analysis.md` — evidenced benchmark study and grounded Site Layer assessment
- `02_Creative_Directions.md` — three distinct design directions with choice criteria
- `03_Design_System.md` — typography, rhythm, layout, motion, accessibility, photo treatment, components
- `design-tokens.css` — proposed **namespaced** CSS variables, not a production stylesheet
- `04_Signature_Experiences.md` — user journeys and interaction design for the flagship chronology, Evidence Atlas, Library
- `05_Architecture_and_Data.md` — WordPress-first delivery pattern and verified record graph
- `record-schema.example.json` — illustrative schema (do not treat sample entries as verified historical data)
- `06_Roadmap_and_QA.md` — work packages, gates, tests, performance, go/no-go
- `07_Handoff_State.md` — exact next steps for Claude, dependencies, open decisions, what was and was not done
- `concept-board.html` — self-contained concept board comparing the three art directions, with no network dependencies and no production connection

## Hard boundaries

- Do not change production WordPress, deployed Site Layer, or PR #49 in this R&D lane.
- No unverifiable artifacts, invented historical dates, invented coordinates, AI-created images misrepresented as historical photographs, or unlabeled reconstructions.
- No new paid SaaS dependency without explicit approval. Default to static assets, WP-native blocks/data, SVG, CSS, and lazy-loaded vanilla JS.
- No UX that depends on dragging, hover, animation, sound, large downloads, or JavaScript to access essential research.
- No QD PASS from a developer's own report. Visual/keyboard/mobile/semantic tests and governed code review are separate gates.

## Sources

- Blue Corridors: https://bluecorridors.org/
- Agency project case study: https://ode.partners/en/projects/blue-corridors
- Agency technical/editorial article: https://ode.partners/en/insights/beneath-the-surface-a-deeper-dive-into-our-work-on-blue
- Award: https://winners.webbyawards.com/2026/websites-and-mobile-sites/features-design/best-data-visualization/364937/wwf--blue-corridors
- Performance baseline thresholds: https://web.dev/articles/defining-core-web-vitals-thresholds
- WCAG 2.2: https://www.w3.org/TR/wcag/
- Current FV homepage work (not merged): https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49


## Sprint 02 extensions (working prototypes)

- [Implementation report](09_Sprint_Implementation.md) — concrete output and remaining gates.
- [Claude handoff delta](10_Handoff_Delta.md) — new work that should not be repeated.
- [Apollo 1 working exhibit](flagship-apollo1/index.html) — six sourced chapters, responsive documentary viewer and source inspector; see its README for caveats.
- [Evidence Atlas interactive catalog](atlas-preview.html) — verified published records with safe non-geocoded fallback.
- [Atlas research queue](atlas_seed_catalog.json) / [audit](ATLAS_SOURCE_AUDIT.md).

Neither prototype has been published to finalvestige.com.

## Sprint 03 — now includes a reusable Research Desk and WordPress integration candidate

The isolated R&D package has advanced since Sprint 02. Open `experience-lab.html` for a local index of three working prototypes: flagship Apollo 1 investigation, six-record Research Desk / Source Ledger, and non-geocoded Evidence Atlas. Relative screenshot paths in the gallery require extracting the ZIP intact; the sandbox's browser restrictions prevent its automated screenshots from loading local images, though local filesystem references were checked.

New files:

- `source-ledger/index.html` — original, source-backed evidence UI, search/filter, native `<details>` and verified no-JS content.
- `source-ledger/build_ledger.py` — deterministic source-driven HTML generation with approved HTTPS record links and escaping.
- `source-ledger/verify_ledger.py` and screenshots — real Chromium QA for six widths, controls, native details, multiple components on one page, no-JS and link/path checks.
- `source-ledger/wordpress-block.html` — Gutenberg Custom HTML markup candidate; no CSS/JS by itself.
- `source-ledger/wp-staging-plugin/` — **uninstalled, unapproved standalone** shortcode proof of integration, plus CSS, JS and static template.
- `11_Experience_2_Integration_and_Release.md` and `12_Sprint_03_Summary.md` — concrete architecture, tested behavior, open editorial/performance/QD gates and WordPress-specific constraints.
- `verify_all_v3.py` and `QA_V3_MANIFEST.json` — orchestrated local checks and per-file SHA-256 records.

All prototypes remain local research work; **PR #49, the live WordPress site, subscription flows, production deployment bridge, and public code were not changed by these prototypes.** See GitHub [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and isolated `research/experience-2-foundation-2026-10-29` branch for the durable planning references. The executable prototype code is inside this ZIP, not yet committed as an implementation PR.

## Sprint 04 — connected evidence journey and an important fallback fix

The Apollo 1 flagship source dialog now links directly to its corresponding entry in the new Research Desk prototype; the standalone exhibit also has a Research Desk footer link. Actual Chromium tests confirm the source-dialog URL and that a missing `IntersectionObserver` no longer produces a misleading stale evidence viewer. See `14_Sprint_04_Flagship_Hardening.md`.
