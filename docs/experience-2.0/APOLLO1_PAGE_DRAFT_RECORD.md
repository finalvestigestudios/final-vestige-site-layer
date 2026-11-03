# Apollo 1 investigation page: plugin-free draft (2026-11-02)

**Revision 2 (2026-11-03), after the independent HOLD on `65f98aad`:** every claim now cites a named NASA source with a verbatim quote and link (Board Findings and Investigation pages, NASA History 2022 and 2018 articles, crew biographies); "Fourteen seconds" is now "About fifteen seconds"; internal notes are gone from visitor text; the six photographs are omitted pending named-editor sign-off (`APOLLO1_IMAGE_DECISION_SHEET.md`, `page-blocks/image-signoffs.json`); the draft now has nine blocks, all read back equal to the source. The hash tables further down describe the previous revision and are superseded by `APOLLO1_REVIEW_PACKET.md`. Authenticated WordPress.com review is still outstanding (browser not signed in).

**Update (later 2026-11-02):** block 01 was changed to add the third label ("Open question") inside every chapter that has an unverified claim; the stored hash was read back (`7ce8f575...`). The tables below carry the current hashes. Review packet: `APOLLO1_REVIEW_PACKET.md`. Mobile perf on the final block: 12 runs median 1,810 ms, max 1,860 ms; an earlier 7-run batch on the same block had one 2,716 ms outlier.

**Status: PRIVATE DRAFT, not published. No independent QD review exists and none is claimed (no `FVSL-QD-PASS`).** Branch `feature/atlas-apollo1-live` (cut from `feature/experience-2-living-archive-sprint5`), commit `79c0a017` plus this record. Worktree `Projects/fv-atlas-live`.

## 1. Decision: no production plugin

`ARCHITECTURE-DECISION.md` recommends a separate staging plugin. The founder rejected installing a new production plugin for a minor gain, so **that plugin is not installed and not needed**. The same renderers (`render_flagship.py`, `render_desk.py`, the Atlas dataset) now emit **top-level `core/html` blocks** with inline CSS and JS, on the mechanism already proven for the homepage block (PR #604): CSS `.fv-ex2*`, custom properties `--fvx-*`, hooks `data-fvx-*`; content is complete HTML first; the script only reveals optional controls and fails open (JavaScript-off test below). Nothing is stored, fetched or sent by the script (a test scans for `fetch(`, `XMLHttpRequest`, storage, `innerHTML`, `eval`, external `<script src>`, `<link>`, `@import`, `url(`).

Every statement comes from `data/apollo1.json` and `atlas/data/atlas.json`; only interface wording (headings, labels, legend) is new. `tools/render_apollo_page.py` builds it; `python tools/build_all.py --check` fails CI if `page-blocks/` is stale.

## 2. The draft

| | |
|---|---|
| WordPress page ID | **2017** (draft, no password) |
| Title / slug | "Apollo 1: The Evidence Atlas" / `apollo-1-evidence-atlas` |
| Edit | https://finalvestige.com/wp-admin/post.php?post=2017&action=edit |
| Preview (signed-in only) | https://finalvestige.com/?page_id=2017&preview=true |
| Signed-out check | `/?page_id=2017` and `/apollo-1-evidence-atlas/` return **404**; not in the REST pages list; not in `sitemap-1.xml` |
| Template | default (Assembler `page`; the theme prints no page title, so the block owns the one `h1`) |

Page content: eight top-level `core/html` blocks (`page-blocks/apollo1-investigation/00..07`). Contents, in order: inline CSS; the investigation (text hero, how-to-read legend, chapter bar, six evidence plates with the four-marker chronology, conclusion); the Atlas classification list (documented vs interpretive, from the 8 relationships); the Research Desk (6 records, search, claim crosswalk); image sources and rights (6 images, NASA basis, restriction, identity checks); related investigations (the 5 other Atlas investigations sharing a theme tag, linked to their live posts); footer; inline JS.

Each block was written with the WordPress.com content tools (`pages.create` for block 0, `page-sections.insert` for 1 to 7; `_content_warnings` empty every time) and **read back with `page-sections.list`: every block's `block_hash` equals the local SHA-1** (WordPress hashes the block without the file's trailing newline).

| Block | Bytes (as stored) | SHA-1 (= WordPress `block_hash`) | SHA-256 (as stored) | SHA-256 (committed file, +trailing `\n`) |
|---|---:|---|---|---|
| 00-style | 23,748 | `bbf054a2f48f970fb560466102899d2c413a33fa` | `9c345e7d09b01c71953e80fc93d8cf5ecd0421d7985fb5b8b0df942a9ab95f8b` | `bd76f0a27c4430bdea43d8edbe217b320eae279eb9af469add2893e46d37aeef` |
| 01-investigation | 32,669 | `7ce8f575b8ae075699785672020c571691c8ba1f` | `c8ffc9a84bd5530aadb4ec348eb918e1b0dd143be58206e3146a982588ec67a6` | `006e6474bf52a842759d118639808e9f3309c51116446263da2d81a9693dfc40` |
| 02-classification | 3,503 | `dc62ad1669b81ac1d84e0ba9be486cdad47c4cda` | `89db03241291c38fa2c6f699f515193af4b87315df698a12f3fed47a90454b36` | `9aad27071d522d9695fe10e705e55a75f6de32ce7f8b11b4fcdf748c8514bca0` |
| 03-research-desk | 22,550 | `4abe3e8ea0f17a2277f0135a1bca9ee8135fdc2f` | `1b1a358a6c01650181a1834eaa186f9502a94ba40ba9a807e508732b7f639bd4` | `bc1ae2cb0a2209ae5fb9a8f9acb2ea912c3a51329ea01f8da2fc17af2d2d977e` |
| 04-rights | 8,318 | `dd84742473035a78ecea66ec7c03296f6ce84b20` | `bb0cab82b1ee0b495ee520c80cfb879582ad36fb8df1d68fb158250321732e13` | `3315f3df3bf2d0f296c4e5d67ef0b48a03e1b465df9fdbb6a34117bbb80a5729` |
| 05-related | 2,026 | `173982203da9eb3a8dff4e91d82725148d4afa86` | `851d7dcc51acb0be5f5bcea8b3f79026f1cbf162c73f5a8dae20c804cc04dd8a` | `f1decab5a2c8c980bd1e5cb7f200e313626695e86e505a9ce91c7efa2bd713e7` |
| 06-footer | 564 | `b0c723e2b898eaf47bea17dcf3809001b98e7190` | `3434198cb9a09ba031219be4570c0257b63803258f58fcd8345a7aac455a0338` | `0dfb6749b34b88f099e8d25825d8439a9ef17f1b938f9fa474aedf0bdf3ba967` |
| 07-script | 9,655 | `2f4df25d143a4d559005aca8fb46d4d49f75b4ba` | `e6169fec1bb92471fecb4d32eeacb3de611d0b8bcc6ba865a664f534885e8c93` | `c95c1f386f2b65a37656808533b36f50f8df686697d2be3cd09ce478200dc8b0` |

Whole page content (committed blocks joined by one newline, 103,048 bytes): SHA-1 `fc93015a77e55fae8a50d64b120ea748df6eea22`, SHA-256 `5ac375e00f31d0bee9e89b5248502296397a1ea2b290094167142192b68b1cbf`. WordPress's own page `content_hash` differs because it joins blocks its own way; the per-block hashes are the proof.

Live page 6 (homepage) was not touched: re-read after the writes, block 1 SHA-1 is still `8c0dd5c3adce073fd58f5001e0f90d523ffad277`, `modified 2026-11-02T17:48:13`, earlier than every write here. Draft 1902 (earlier probe) was not touched.

## 3. Test results

**Method.** A WordPress.com draft is private, so it cannot be loaded signed-out. `tools/verify_apollo_page.py` takes the **live Assembler shell** of a published page (header, footer, theme CSS from finalvestige.com, GET only), puts the committed blocks in its `entry-content` exactly as WordPress prints `core/html` (comment delimiters removed, bytes untouched), serves that from localhost and tests it with Playwright + Edge + axe-core 4.10.2. Analytics hosts are aborted so no production analytics hit is sent. This is signed-out-equivalent for markup, CSS and script, but **it is not the WordPress.com render of draft 2017** (see section 5). Raw results: `evidence/apollo1-page/*.json`.

| Check | Result |
|---|---|
| Widths 360, 390, 768, 1024, 1440, 1920 | one `h1`, heading order valid, no duplicate ids, **no horizontal overflow**, all 6 images load, root exactly viewport width (full bleed via the theme's `alignfull`), no page errors, both script modules `ready=true`, external links all `noopener noreferrer` |
| axe-core, WCAG 2.0/2.1/2.2 A and AA + best-practice, 7 runs (6 widths + motion on) | **0 violations, 0 incomplete**, for the block scope and the whole page |
| Behaviour | desk search filters to 1 of 6 and empty state; plate link lands on its desk record; chronology slider reports "Nothing is recorded between markers" at +8 s; one current chapter; **JavaScript off**: complete document (7 chapters, 6 records, 5 related), optional controls hidden; buttons, summaries, chapter links at least 24 px |
| Mobile performance, real throttled method (390x844, 4x CPU, 150 ms RTT, 1.6 Mbps, cache off), 7 runs | **LCP median 1,800 ms, max 1,892 ms** (limit 2,500); **CLS 0.073** in every run (limit 0.10). LCP element: `p.fv-ex2-hero__dek` |
| Desktop 1440, 7 runs | LCP median 432 ms, max 624 ms; CLS 0.0014 |
| Repository suites | `test_apollo_page` 13, `test_builders` 19, `test_atlas` 22 pass; `test_browser` 31 pass (run on the shared code before the final block split; shared code unchanged since); `build_all.py --check` OK. PHP-based plugin tests not run (no PHP on this machine; the plugin is not part of this change) |

**Two findings from the measurement, both fixed in this change.** (1) The flagship's background photograph was the mobile LCP element at about 2.8 s, over the limit, so this page has a **text-only hero** (and no entrance animation, since an element that starts at opacity 0 is not counted until it paints). (2) The Assembler theme sets `.wp-site-blocks main * { min-width: 0 }`, which collapsed the 44 px chapter links to 15 px; the page CSS restores them. Also a defect inherited from the Sprint 5 flagship CSS: Chromium confines a sticky grid item to the grid container, so the sticky plate slid over the chronology below it; fixed in the page CSS only (the shared CSS and the staging plugin still have it; `test_sticky_plate_only_with_room` asserts the old behaviour, so I did not change the shared file).

## 4. Rollback

Nothing is live. The change is one private draft (ID 2017) and files in the repository.

- **Discard the draft:** `pages.delete` on 2017 (moves it to trash; restorable). No other page, post, menu, template, plugin or setting was changed. There is no plugin to deactivate.
- **After a future publish:** set 2017 back to `draft` (`pages.update`, `status: draft`) or trash it; the URL then 404s again. Nothing else links to it yet (no existing post was edited), so there are no dangling links.
- **Code:** revert commit `79c0a017` (and this record) on the branch; no production system consumes it.

## 5. What is NOT done, and what blocks publication

1. **Authenticated WordPress.com render of draft 2017 is not done.** The in-app browser is not signed in and credentials are not entered by an assistant. The founder must sign in once; then the preview, a console and network pass and the screenshots can be taken, as was done for draft 1902. Until then the exact stored bytes are proven (hashes) but not seen in the WordPress.com renderer. WordPress also texturizes text nodes (straight quotes become curly quotes); the local harness does not, which cannot affect layout or axe but should be glanced at.
2. **Independent QD review: none, not claimed.** Needs a fresh review of the exact block hashes above.
3. **Sourced-data issues that become visible to visitors on this page** (all are in the committed data and were left as is, not edited by me; an editor should decide before publication):
   - Image S67-19766: its identity note says "confirm before publication" and the NASA Image API did not find the ID (the file is hosted on finalvestige.com).
   - "The Block I hatch opened inward" is `article-only`; the "most likely initiator was an electrical arc" sentence is `partial` (exact Board wording not located); the redesigned hatch "opens outward" is `partial`; the 102-ignition-tests figure is `article-only`. The crosswalk shows these labels to the reader, which is honest, but the body text states them without qualification.
   - Crosswalk and identity notes contain internal wording ("not re-checked in Sprint 5", "before publication", "confirm wording") that reads oddly to a visitor.
   - Related-investigation lines show Atlas date status "candidate" (for example "1917 (year, candidate)").
   - Title "Fourteen seconds" versus the Board's "approximately 15 seconds" is an open editorial note (shown in the crosswalk).
   - Rights: "editorial-use basis recorded; human rights review pending" is displayed; the NASA item-specific named-editor sign-off is still open and Atlas `review_status` is `unreviewed` for every item (shown as "Not yet reviewed").
4. **Decisions for the founder:** page title and slug; whether the page is indexable or `noindex` at first (its text overlaps the full article, and the page is a companion, not a replacement); whether to add the hero photograph back (it cost about 1 s of mobile LCP); adding links to this page from the Apollo 1 post (a post edit, not done here); the 0.073 CLS has little headroom (font swap in the hero; measured under the harshest throttle).
5. **Not covered:** screen reader, Safari and real-device tests; field Core Web Vitals; the theme's own console noise when signed in.

## 6. To publish (needs the founder's approval; not done)

After items 1 to 3 above: one `pages.update` on 2017 with `status: publish`, then verify signed out: HTTP 200 at the slug, one `h1`, the eight block hashes via `page-sections.list`, page 6 block 1 still `8c0dd5c3...`, and the sitemap entry. No plugin step exists.
