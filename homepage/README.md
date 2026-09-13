# Homepage redesign — "The Vestige Assembly" (page ID 6, slug `home`)

This directory holds the **WordPress page content** half of the homepage redesign. The other
half — the progressive-enhancement JavaScript/CSS that plays the choreography, rotates the
margins wire, and drives the investigation walkthrough — ships through the governed Site Layer
plugin as three new payloads: `hero-assembly-wp-block-v1.txt`, `margins-wire-wp-block-v1.txt`,
and `investigation-walkthrough-wp-block-v1.txt` (see `../payloads/`, wired into
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
   exactly as published. Only a new Site Layer payload (Margins Wire) enhances it in place.
1. `fv-studios-hero` — **redesigned**. Same real headline ("Find what others miss.") and eyebrow.
   The dek was rewritten to drop the brief's flagged buzzword line ("signal buried in records,
   systems, and markets") for the plain-language version. The six identical pathway cards are
   gone from the hero; the four evidence-fragment cards ("Document" / "Record set" / "Map" /
   "Photograph") are new and are what the Hero Assembly payload animates.
2. **New:** `fv-worlds` — the six real pathways (Investigations, The Public Record, Labs,
   Editions, Films & Media, The Exchange — same real copy and URLs as the old hero cards), now
   laid out as six differentiated treatments instead of one repeated card shape.
3. **New:** `fv-mission` — a short, quiet editorial statement (no dynamic content).
4. **New:** `fv-invest` — the Live Investigation walkthrough. Uses one real, already-published
   Final Vestige investigation, ["The Hatch Opened Inward"](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/)
   (Apollo 1). All six stage headlines and body copy are drawn from that real article; all six
   evidence images, captions, and quotations are the real NASA photographs and footnoted
   quotations already used in that post (see the payload's `EVIDENCE` array for exact source
   URLs). Nothing here is invented.
5. `fv-home-shell` — **unchanged block logic.** The existing dynamic `wp:query` / `wp:terms-query`
   blocks (Latest investigation, Recently filed, category strip, Exchange preview, More
   investigations, Research Trails, Sources and research tools) are untouched — same queries,
   same attributes, same real data at render time. Two additions inside it:
   - The existing "How we work with sources" section gained a small `SOURCE → PROVENANCE →
     CORROBORATION → RECONSTRUCTION → CONCLUSION` visual strip (new `<!-- wp:html -->`, purely
     additive; the real paragraph and the three real buttons — Editorial Standards, About the
     Editor, Send a Correction — are untouched).
   - **New:** `fv-last` ("The Last Vestige") was inserted immediately before the Dispatch group.
     Its one line is reused verbatim from margin-strip item 41 (the CIA robotic-catfish note) —
     real, already-vetted content, not a new claim.
   - The Dispatch block itself (`wp:jetpack/subscriptions`) is **completely untouched** — same
     block, same attributes, same real subscription mechanism.
6. `fv-enter-record` — **unchanged.** Same four real cards (Editorial Standards, The Failure
   Chain, Research Sources, Journal), same copy, same URLs.
7. JSON-LD organization schema — **untouched.**

## Applying this

`page-6-home.blocks.html` is the complete, ready-to-paste block markup for page ID 6 (slug
`home`). To apply:

1. Open the page in the WordPress block editor, switch to the Code Editor view (or use
   `pages.update` and paste this file's content into `content`), and replace the existing content
   with this file's content exactly.
2. Confirm the four dynamic query sections inside `fv-home-shell` still render real posts/terms —
   their block attributes are byte-identical to what's live today, so they should behave
   identically.
3. Deploy the three new Site Layer payloads (this repo's normal governed release process; see
   `../DEPLOYMENT.md`) so the enhancement layer is present. The page reads correctly without them
   — they only add motion and interactivity.
4. The Fraunces display typeface is loaded by the Site Layer plugin itself (a new `wp_head` hook,
   gated by the same release-integrity check as the footer payloads) — no theme change needed.
   Every rule that uses it lists `ui-serif, Georgia, serif` as a fallback, so a blocked or slow
   font request never breaks layout, only softens the typographic contrast.

## What this does **not** attempt (and why)

- **Real archival images/maps/documents for the hero fragments or a Library evidence-object
  viewer** — this session has no access to Final Vestige's media library beyond what's already
  attached to published posts. The hero fragments are abstract CSS art (document lines, a file
  stack, a map grid, a photo vignette), not real archival images, so nothing fabricated is
  presented as evidence. A Library/evidence-object section was not attempted.
- **"Current Signal" as a distinct new section** — the real `fv-home-shell` already contains a
  live, dynamically-updating feed (Latest investigation, Recently filed, More investigations,
  Research Trails). Rather than duplicate that mechanism, this redesign left it in place and
  restyled around it.
- **Header/footer/global navigation** — these belong to the live theme, not to page content or
  this plugin, and were not touched or reconstructed.

## Content sources (real, verified)

- Site: `finalvestige.com` (WordPress.com Atomic, blog ID `256784396`), theme `Assembler`.
- Page content, "Hidden in the Margins" items, hero copy, and all `fv-home-shell`/`fv-enter-record`
  content: read via WordPress.com Content Authoring (`pages.get`, id 6) on 2026-09-13.
- Investigation content and images: read via `posts.get` (id 434, "The Hatch Opened Inward") on
  2026-09-13; images are the real, already-published NASA photographs hosted at
  `i0.wp.com/finalvestige.com/...` and `images-assets.nasa.gov/...`.
- Design tokens (colors, borders) are the exact values already used in the live page's inline
  CSS, not new choices.
