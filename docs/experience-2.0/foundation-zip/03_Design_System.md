# Proposed Experience 2.0 Design System

**Prototype proposal only.** `design-tokens.css` is namespaced under `.fv-ex2` and must not override the live site/theme until designed, tested, and approved. Existing WP Assembler preset tokens are generic; retain and reconcile rather than destructively replace them.

## Color

| Intent | Proposal | Existing precedent |
|---|---|---|
| Midnight surface | `#090A0A` | Existing hero section |
| Core ink | `#0C0D0D` | Existing site-layer body |
| Elevated panel | `#171715` | Derived charcoal for panels |
| Quiet line | `#34322E` | Existing border |
| Antique gold | `#B8955E` | Existing accent |
| Highlight gold | `#C7A66C` | Existing accent bright |
| Parchment text | `#F4EFE6` | Existing primary text |
| Subdued secondary | `#B8B1A6` | Existing secondary text |
| Source surface | `#E9E0D1` | Proposed warm evidence-paper panel |

Use opaque surfaces behind text; ensure measured WCAG contrast with all combinations. Never use gold-only text as the *only* indicator for reliability, provenance or state.

## Type system

- Editorial display: existing **Fraunces** where available; fallback Georgia/serif. Use for story-led titles and one major visual statement per view.
- Interface and narrative body: **Inter** (already included in Assembler), fallback system-ui/sans-serif. Body 16–19px depending on container.
- Artifact catalog data: native ui-monospace or documented existing mono; avoid fetching new typefaces until verified asset strategy is agreed.
- Hero fluid desktop `clamp(3.7rem, 8.5vw, 9rem)`, 0.93–1.02 line-height; small-screen cap and careful line breaks.
- Body line length 60–72ch; page essays can use 70ch + optional side notes. Exhibit caption 12–14px (not hard-to-read 9px microtext).

## Responsive grid and rhythm

- Content frame max 1440px; narrative frame 760–860px; control panel frame 1100–1240px; responsive safe gutters clamp(20px,4vw,64px).
- Section rhythm 88–168px at wide widths; 52–96px at narrow; each section justified by a narrative transition.
- Breakpoints to QA: 360, 390, 768, 1024, 1440, 1920px. Explicit tablet behavior; don't treat tablet as mobile desktop hybrid by accident.
- No horizontal overflow, no 100vw nested under scrollbars, no locked browser zoom. At 200%/400% zoom content stays usable.

## Image art direction and provenance

- Privilege **authentic source material**: NASA, NYPL, official archives, existing FV licensed assets. Never invent primary artifacts for aesthetic completeness.
- Source image stays legible when inspected; do not permanently obscure it with heavy decorative filters. Use discreet grading in editorial previews only.
- Labels are fixed to actual assets: title, date/range, repository, rights/credit, document ID and source URL if known. Missing metadata displays as 'Unverified — not published', never guessed.
- Generate alternative crops in a content pipeline, not heavy blur/high-res transfer client-side. Declare width/height or aspect-ratio to prevent layout shifts.

## Motion grammar

- **Reveal** (180–280ms): opacity and slight translate (8–18px) at most; only where content becomes meaningful.
- **Evidence focus** (200–360ms): highlighting a real annotation, inspector zoom, side-panel detail.
- **Narrative transition** (350–550ms): optional crossfade between chapter evidence panels; avoid scroll-jacking.
- **System feedback** (90–160ms): clear response to pointer/keyboard actions.
- NO indefinite unsolicited motion as a prerequisite for reading. All nonessential motion stops on `prefers-reduced-motion: reduce`; pause controls for anything autonomous.
- Explicit touch/drag alternative; `touch-action:none` only on a verified operable surface, never on static fallback.

## Component vocabulary

1. **ExhibitHero** — optional editorial media + lead title + two meaningful paths.
2. **EvidencePlate** — image/scan, caption, provenance and transcript, source link.
3. **SourceDrawer** — actual archive links, support level, interpretation boundary, downloads if licensed.
4. **StoryChapter** — text + illustrated/captioned record, step progress, direct deep-link.
5. **ChronologyRail** — ordered dated events, grounded uncertainty bands, keyboard nav, static list fallback.
6. **MapLayerTray** — only validated map features, with text-based results and legends.
7. **RelatedInquiry** — editorial relationship to another published investigation, explicit rationale.
8. **DispatchBridge** — a helpful invitation after useful content, without changing actual Jetpack subscription block.

## Navigation and microcopy

Global navigation remains understandable without effects. The homepage answers **What is this? What can I find? Where do I start?** within the first viewport. Avoid abstract labels where they hide function; a term like 'Living Archive' gets a plain-language subheading. Interface actions use concrete verbs: 'Inspect the note', 'Open the source', 'Compare records', 'Read the investigation'.

## Inclusive interaction

- WCAG 2.2 AA as the target; axe automated checks **plus** real keyboard, screen-reader, touch and zoom QA.
- Focus visibility, escape/close behavior, accessible control names, semantically correct slider bounds/step controls, no hidden links tab-reachable.
- A screen-reader-readable chronological list and source index must exist independently of canvas/map visualizations.
- Every reveal has an equivalent button or link. No motion gated knowledge. Never use generic `div role=slider` unless its accessible value, range and commands reflect actual operation.
