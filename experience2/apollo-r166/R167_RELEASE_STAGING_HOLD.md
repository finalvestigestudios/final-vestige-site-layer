# Apollo R167 — Gutenberg-block-safe R166 packaging (STAGING HOLD)

## Why this exists
R166's guarded offline builder removes the misleading association between archival photographs and the Apollo 1 fire-second slider, adds accessible independent selectors, and preserves evidence citations. However its generated `<style>` and `<script>` are appended **after** the final `<!-- /wp:html -->` delimiter. That is valid enough for an offline browser fixture but not a safe WordPress Custom HTML editor representation. R167 packages those assets **inside** the existing last WordPress Custom HTML block, before its closing Gutenberg comment, with no production changes.

## Current read-only WordPress source witness — 2026-11-06
- WordPress Page 2017, `https://finalvestige.com/apollo-1-evidence-atlas/`; `modified=2026-11-05T18:19:45` (site metadata).
- Editor content length: 96,288 JavaScript characters; **9 opening / 9 closing** Custom HTML block comments; **1 original script**.
- **1** archival gallery; **1** uncorrected `t < 6 ? 0 : (t < 11.3 ? 1 : 2)` photograph controller; **1** “Moving the slider changes the archival view for exploration only” instruction.
- NASA original records S66-58038, S67-15717, KSC-20170124-PH_KLS01_0129 remain cited; **no R167 marker is present**.
- This is source-level verification, **not installed-page browser acceptance or an authorization to write**. The current live page was not modified.

## Source and exact testing
- From predecessor R166, pinned source code: `build_offline.py` Git blob `51853a8acb35935b5baf8c30d810bc048c457d3a`; `stage_patch.py` `ede23550595c5d0c0d6b348681fb91543d65394c`.
- New `wp_block_pack.py` Git blob `7c9b168b6478e6f06bc1d9627a4f331621fed246`.
- New `test_wp_block_pack.py` Git blob `397aa1c56a7c9a32f3436bb9b62db35d4644812c`.
- Both new blobs and all imported R166 fixture/dependency blobs matched their local Chromium-tested source files.
- Reproduce within this directory with Python and Playwright + Chromium installed: `python -m unittest -v test_wp_block_pack`. To build an *offline preview*, obtain a current authorized **read-only** WP editor-source export and run `python wp_block_pack.py editor.txt preview-editor.txt`; inspect the resulting manifest and diff. Do not upload or publish.
- Chromium positive test: 2/2 Python unittest methods passed, twice. For each run, actual Chromium at 320/360/390/768/1440/1920, JavaScript enabled and disabled, emulated touch, reduced motion, no external media access, source citations, keyboard Home, fire-slider independence, error fallback, horizontal overflow. Six screenshots were saved; all six PNG SHA-256 hashes matched across two clean test runs.
- Negative controls: duplicate payload, missing Gutenberg boundaries, changed old controller, tampered NASA citation, text after final block all reject build; output manifest always says `OFFLINE_STAGING_HOLD` / `wordPress_writes=0`.
- Browser tests **use a source-derived Gutenberg-shaped fixture**, not an installed WordPress or exact production page. Test has placeholders and intentionally aborted external media; source counts against current WordPress are a read-only structural witness only.
- **Not executed:** actual installed WP staging test, native WordPress block serialization round-trip, true CSP, live NASA image/CDN delivery, real axe-core, manual screen reader, actual CWV/LCP/CLS, hosted exact-head CI. These remain required. No positive commercial conversion or attribution evidence was produced.

## Historical & commercial controls
- The three photographs represent separate archival moments (1966 training; January 1967 processing; 2017 hatch exhibition), **not** a second-by-second photo record of the 1967 fire. NASA source URLs remain intact and no geographic edges/pins are created.
- Single relevant action: **Read original investigation**. No unrelated affiliate link, hypothetical paid casefile CTA, tracking snippet, content publishing or merchant action. NASA media are not cleared for paid advertising or implied endorsement.
- Apollo casefile SKU/rights/checkout still unknown; Grok's published Apollo `asset_id` and qualified social referrals unknown. Realized net revenue per 1,000 qualified sessions remains not computable. Cross-reference #820 and business charter #818. Creator scripts, scheduling, distribution remain Grok's; Praxxis handles external creator review; Claude governs WP production engineering.
- **Release gate:** draft-only. Do not merge, deploy or update any WP content/settings, homepage PR #49, original Research Desk PR #158, analytics or paid services without independent QA and explicit founder approval.
