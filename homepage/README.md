# Homepage redesign — "The Vestige Assembly" (page ID 6, slug `home`)

This directory holds the **WordPress page content** half of the homepage redesign. The other
half — the progressive-enhancement JavaScript/CSS that plays the choreography, rotates the
margins wire, drives the investigation walkthrough, and powers the Library magnifier — ships
through the governed Site Layer plugin as four new payloads: `hero-assembly-wp-block-v1.txt`,
`margins-wire-wp-block-v1.txt`, `investigation-walkthrough-wp-block-v1.txt`, and
`library-inspector-wp-block-v1.txt` (see `../payloads/`, wired into
`../final-vestige-site-layer.php` and `../release-manifest.json`).

**Why two halves.** This plugin can only inject content at `wp_footer`; it cannot restructure
the real homepage template. So the split follows the brief's own architectural principle:
WordPress page content carries all real meaning (headline, copy, navigation, evidence) as plain
semantic HTML that works with JavaScript disabled; the Site Layer payloads only add choreography,
interactivity, and motion on top of markup that already means something without them.

## What changed on the page

Top-level block order (was: margin strip → hero-with-six-cards → home shell → enter-record →
JSON-LD):

0. `fv-margin-strip` — **unchanged**, byte-for-byte. All 72 real "Hidden in the Margins" items,
   exactly as published. Only a new Site Layer payload (Margins Wire) enhances it in place —
   turning the old passive-only CSS animation into a pausable, keyboard-navigable rotator with
   visible position and prev/next/pause controls, without touching a single real item's text.
1. `fv-studios-hero` — **redesigned**. Same real headline ("Find what others miss.") and eyebrow.
   The dek was rewritten to drop the brief's flagged buzzword line ("signal buried in records,
   systems, and markets") for the plain-language version. The six identical pathway cards are
   gone from the hero; in their place are four evidence-fragment cards ("Document" / "Record set"
   / "Map" / "Photograph") built from **real, already-published Final Vestige media**, not
   decorative CSS art:
   - Document: the real Franklin Expedition Victory Point Note (1847–48).
   - Record set: Final Vestige's own real evidence-boundary diagram from a published investigation.
   - Map: the real 1903 NYPL map of the Brooklyn Rapid Transit system (also used in the Library
     section below).
   - Photograph: the real U.S. Navy photo of the USS Forrestal fire (1967), with its real USN
     photo ID as the credit line.
   The Hero Assembly payload animates these four cards scattering (rotated, offset) and then
   assembling into place, with an amber rule drawing across the full row as they connect.
2. **New:** `fv-worlds` — the six real pathways (Investigations, The Public Record, Labs,
   Editions, Films & Media, The Exchange — same real copy and URLs as the old hero cards), laid
   out as six differentiated treatments instead of one repeated card shape.
3. **New:** `fv-mission` — a short, quiet, centered editorial statement (no dynamic content) —
   the page's one deliberate monumental pause between the hero and the investigation.
4. **New:** `fv-invest` — the Live Investigation walkthrough. Uses one real, already-published
   Final Vestige investigation, ["The Hatch Opened Inward"](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/)
   (Apollo 1). All six stage headlines and body copy are drawn from that real article; all six
   evidence images, captions, and quotations are the real NASA photographs and footnoted
   quotations already used in that post (see the payload's `EVIDENCE` array for exact source
   URLs). Nothing here is invented.
5. **New:** `fv-library` — "Inspect the evidence." Built around the real 1903 NYPL map of the
   Brooklyn Rapid Transit system, which is itself real evidence already used in a real, published
   investigation, ["Six Miles an Hour"](https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/)
   (the 1918 Malbone Street subway wreck) — the metadata panel (title, date, collection, source,
   rights, "why it matters") is drawn from that post's real figcaption and NYPL catalog record,
   not invented. The Library Inspector payload adds a cursor/touch-driven magnifying loupe over a
   higher-resolution version of the same real image.
6. `fv-home-shell` — **unchanged block logic.** The existing dynamic `wp:query` / `wp:terms-query`
   blocks (Latest investigation, Recently filed, category strip, Exchange preview, More
   investigations, Research Trails, Sources and research tools) are untouched — same queries,
   same attributes, same real data at render time. Additions inside it:
   - A small "Current Signal" eyebrow now labels the dynamic Latest-investigation feed explicitly,
     rather than leaving its role implicit.
   - The existing "How we work with sources" section gained a small `SOURCE → PROVENANCE →
     CORROBORATION → RECONSTRUCTION → CONCLUSION` visual strip, plus one real worked example (a
     real diagram and link from "Six Miles an Hour" showing operating-history evidence kept
     deliberately separate from the later legal outcome). The real paragraph and the three real
     buttons — Editorial Standards, About the Editor, Send a Correction — are untouched.
   - **New:** `fv-last` ("The Last Vestige") was inserted immediately before the Dispatch group.
     Its one line is reused verbatim from margin-strip item 41 (the CIA robotic-catfish note) —
     real, already-vetted content, not a new claim.
   - The Dispatch block itself (`wp:jetpack/subscriptions`) is **completely untouched** — same
     block, same attributes, same real subscription mechanism.
7. `fv-enter-record` — **unchanged.** Same four real cards (Editorial Standards, The Failure
   Chain, Research Sources, Journal), same copy, same URLs.
8. JSON-LD organization schema — **untouched.**

## Applying this

`page-6-home.blocks.html` is the complete, ready-to-paste block markup for page ID 6 (slug
`home`). See **Deployment safety** below before applying it to production.

1. Open the page in the WordPress block editor, switch to the Code Editor view (or use
   `pages.update` and paste this file's content into `content`), and replace the existing content
   with this file's content exactly.
2. Confirm the dynamic query sections inside `fv-home-shell` still render real posts/terms —
   their block attributes are byte-identical to what's live today, so they should behave
   identically.
3. Deploy the four new Site Layer payloads (this repo's normal governed release process; see
   `../DEPLOYMENT.md`) so the enhancement layer is present. The page reads correctly without them
   — they only add motion and interactivity.
4. The Fraunces display typeface is loaded by the Site Layer plugin itself (a new `wp_head` hook,
   gated by the same release-integrity check as the footer payloads) — no theme change needed.
   Every rule that uses it lists `ui-serif, Georgia, serif` as a fallback, so a blocked or slow
   font request never breaks layout, only softens the typographic contrast.

## Deployment safety — treat both halves as one release

The page content and the Site Layer payloads are versioned and reviewed separately (a content
edit vs. a plugin-code PR), but they are designed to be **deployed together** as one release. The
compatibility contract:

- **Page-6 content version.** This file corresponds to Site Layer release
  `FVSL-VESTIGE-ASSEMBLY-HOME-001` / plugin version `0.3.0` (see `../final-vestige-site-layer.php`
  and `../CHANGELOG.md`). If a future Site Layer release changes the selectors, data attributes,
  or class names these four payloads depend on (`[data-fv-assembly]`, `.fv-margin-strip__item`,
  `[data-fv-invest-stages]`/`[data-fv-invest-image]`/etc., `[data-fv-library-frame]`/etc.), that
  release's own changelog entry must say so explicitly, and this file must be updated in the same
  release.
- **Fail-safe if only one half is live.** Every payload here is written to degrade to a static,
  fully-meaningful page if its half is missing or stale:
  - Old page content + new Site Layer payloads: each payload's `querySelector` calls simply find
    nothing (old markup lacks the new `data-fv-*` attributes) and no-op via the same fail-closed
    `try/catch` used elsewhere in this plugin. No error, no partial/broken UI — the visitor sees
    the old page, unanimated.
  - New page content + old Site Layer payloads (or the payloads disabled/corrupted and
    fail-closed by `fvsl_release_is_intact()`): the new markup is plain, real, readable HTML on
    its own — headline, fragments, worlds, investigation stages, library metadata, all present as
    static text and images. Nothing on the new page depends on JavaScript to convey its meaning.
  - **Net effect:** any mismatched combination of the two halves renders a correct, readable,
    accessible page — never a blank section, a broken layout, or a console error. Each payload's
    gate function (`fvHaShouldRun`, `fvMwShouldRun`, `fvIwShouldRun`, `fvLiShouldRun`) is unit
    tested to return `false` — and the payload to no-op rather than throw — when its expected
    elements are absent (`tests/verify_hero_assembly.py`, `verify_margins_wire.py`,
    `verify_investigation_walkthrough.py`, `verify_library_inspector.py`). This has not been
    additionally verified by hand against a live mismatched deploy; do that as part of the
    post-deploy checklist below if the two halves ever ship on different schedules.
- **Rollback.** Page content: WordPress's own revision history on page ID 6 is the rollback path
  — restore the prior revision. Site Layer: `git revert` the merge commit through the normal
  governed release process (`../DEPLOYMENT.md`); the plugin's own byte/hash integrity check means
  a partially-rolled-back payload set fails closed (emits nothing) rather than serving a broken
  mix.
- **Post-deploy verification checklist** (in addition to `../DEPLOYMENT.md` §9's live-destination
  verification):
  - [ ] Page 6 loads with no console errors and the real headline/CTAs are present with
        JavaScript disabled (View Source or a no-JS browser profile).
  - [ ] Hero fragments scatter and assemble on load; instant final state under
        `prefers-reduced-motion: reduce`.
  - [ ] Margins wire shows prev/pause/next controls and all 72 items are still reachable.
  - [ ] Investigation stages respond to click, keyboard (Enter/Space), and scroll, and the
        evidence panel's image/caption/citation/quote match the clicked stage.
  - [ ] Library map loads, the loupe follows the cursor (desktop) and touch drag (mobile), and
        keyboard Enter/Space toggles a centered magnified view.
  - [ ] Dispatch subscription form still submits successfully (unchanged block, but verify after
        any theme/plugin update in case an unrelated change affects Jetpack blocks).
  - [ ] `wp-json/fv-deploy/v1/deploy` bridge logs show the expected package SHA-256 was applied.

## What this does **not** attempt (and why)

- **A distinct visual treatment for Films & Media and The Exchange beyond the differentiated
  Worlds card** — both get their own layout/background treatment in `fv-worlds` (see the section
  markup), but a dedicated full section for either (mirroring the Library section's depth) was
  not built, given the scope already covered and the real content available to build it from.
- **Header/footer/global navigation** — these belong to the live theme, not to page content or
  this plugin, and were not touched or reconstructed.
- **A from-scratch information-architecture reorder of `fv-home-shell`'s internal sections** — its
  dynamic query blocks were kept as one contiguous, unmodified unit rather than interleaved with
  new sections, to avoid the risk of breaking real, working WP Query block attributes through
  manual surgery on deeply nested block-comment JSON. The current top-to-bottom order already
  reasonably follows discovery → explore → reconstruct → trust/signal, even though it isn't a
  byte-for-byte match to the design brief's suggested section numbering.

## Content sources (real, verified)

- Site: `finalvestige.com` (WordPress.com Atomic, blog ID `256784396`), theme `Assembler`.
- Page content, "Hidden in the Margins" items, hero copy, and all `fv-home-shell`/`fv-enter-record`
  content: read via WordPress.com Content Authoring (`pages.get`, id 6) on 2026-09-13.
- Media library: audited via `media.list` (71 real items) on 2026-09-13. Hero fragments, the
  Library map, and the Show the Work diagram all come from this audit.
- Apollo 1 investigation content and images: read via `posts.get` (id 434, "The Hatch Opened
  Inward") on 2026-09-13; images are the real, already-published NASA photographs.
- Malbone Street / "Six Miles an Hour" investigation content: read via `posts.get` (id 621) on
  2026-09-13, confirming the real NYPL map and evidence-boundary diagram's actual editorial use
  and captions.
- Design tokens (colors, borders) are the exact values already used in the live page's inline
  CSS, not new choices. The one new token (the Fraunces display typeface) is documented above.
