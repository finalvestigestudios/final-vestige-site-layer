# SEO ledger addendum - inbound links to the five 2026-11-02 posts (applied 2026-11-03)

Companion to `SEO_IMPLEMENTATION_LEDGER.md` (which covers the first 72 changes and is not repeated here).

## Authorization and sequencing

- Founder decision relayed by the orchestrating session (19-link target; drop the Lycurgus Cup -> The Working Order link; refresh locks before each write; visual check of pages 499, 501, 498; spot-check a sample of the earlier 72; homepage and Preparedness excluded).
- **The user approved the 9 inbound blocks in this session** (answer "Approve all 9 blocks"), after the diffs in `06-NEW-POSTS-LINKING-PROPOSAL.md` section B were shown.
- The five new posts' bodies were **not** touched. The 5 outbound blocks (9 links) are **held** until the content session reports corrected post IDs and block counts.

## A. Applied: 9 inbound blocks (10 links)

Every lock below was re-read with `page-sections.list` / `post-sections.list` immediately before the write and matched the recorded token. Each write used `expected_modified` + `expected_content_hash`; none was refused; `_content_warnings` empty on all.

| Target | Op @ index | Links to | content_hash before | content_hash after | modified after (site time) |
|---|---|---|---|---|---|
| 193 `/the-lost-landscape/` | page insert @ 2 | Piri Reis map | `bcc5bbea15f18003d74919b89c0225e62d09a6e6` | `9a9840bbe05e15d2cf9e46f2f5ed2f1721997747` | 2026-11-03T14:46:46 |
| 254 post `the-lump-had-gears` | post insert @ 40 | Lycurgus Cup | `e7be9cf3b7159f9e4f6bfed0bedd5ea31a37ce74` | `bdb26bda0690aa7a85df8ea5406927b3d07c53d9` | 14:46:49 |
| 1122 `/the-missing-caption/` | page insert @ 3 | Change Blindness | `325dbd1f21c0c9bbdae3b708ad7e47b379cefac2` | `6a1e1b220dbf779646ca7e66f6f12f36d87bf098` | 14:46:51 |
| 1338 `/free-resources/research-sources/` | page insert @ 3 | Change Blindness | `4c4f8f303c55ac56d3472b9f5db81038be33c064` | `29101b6aca4b399e2ebcf8883d3b6d57bee96bb5` | 14:46:54 |
| 1377 `/free-resources/puysegurs-animal-magnetism-files/` | page insert @ 1 | Mesmerism | `108c81d667f53b52a9d3c0cdbdbb9414195f1e34` | `c9b708a7a3d0b6bc5f45a1d53783615fe0eb9dbf` | 14:46:58 |
| 1044 `/the-findspot/` | page insert @ 6 | Crystal Skulls | `fd368ad49a80029260dbc344369a23c2eaddf13a` | `d2737b85c4c054504acfd0c21983eee11f652200` | 14:47:00 |
| 499 `/watch/maps-places/` | page insert @ 10 | Piri Reis map | `a12b1816450fb6f9138d44d3d0a2b9494a2b31a1` | `c569118fdee828800cca0fef4ca0226a1adad0e5` | 14:47:03 |
| 501 `/watch/objects-archaeology/` | page insert @ 10 | Lycurgus Cup, Crystal Skulls | `bfe9a11f9c5cd27c704e15b7bcce6d72c825dbb4` | `acc1745beac0678125334a8a0e880771e6bba5e1` | 14:47:06 |
| 498 `/watch/primary-sources/` | page insert @ 12 | Mesmerism | `20e9fd2b28d39779763e0d1d2d259f5b97a64df1` | `b37f5b2949c71d35bb6c7af6038ffa162d22e122` | 14:47:09 |

Hashes in this table were copied by hand from the tool responses; a fresh `*-sections.list` on the target is the authoritative current `content_hash`.

Duplicate check at apply time: none of the 10 links was already present in its target body.

**Rollback** (any row): list sections, find the last top-level `core/group` with class `fv-related-reading`, `page-sections.remove` / `post-sections.remove` it with its `block_hash` and fresh locks. Success = `content_hash` equals the *before* column. Pre-edit bodies for the 2026-11-02 snapshot are in `Projects/fv-release-backups/seo-2026-11-02/`; pages 1122 and 1044 were last edited by this program's meta edits (tokens as recorded), the rest are untouched since 2026-10-29 or earlier.

## B. Verification

- **Public page, all 9** (`evidence/verification-newposts-inbound-2026-11-03.json`): HTTP 200; exactly one `fv-related-reading` block; every added link present; JSON-LD parses; one `<h1>`; schema types unchanged (BreadcrumbList on the pages; Person/Article/BreadcrumbList on post 254 and page 1377, which already had Article).
- **Visual, custom-styled pages 499, 501, 498 (desktop 1024 px and mobile 375 px):** the block renders after the page's existing content, readable on the dark theme, no horizontal overflow (`scrollWidth` equals viewport width), heading text and links inside the viewport (heading 28-321 px of 375). Observation: the block is indented about 64 px more than the page's own text column on desktop and the h2 is larger than the page's section titles. It is legible and not broken, so it was kept; if the owner prefers a tighter look the block can be removed (rollback above) or restyled.
- **The five posts:** each still serves exactly one Article, one FAQPage and one BreadcrumbList; none has a related-reading block yet (the outbound blocks are on hold).

## C. Independent spot check of the earlier 72 changes (2026-11-02, second crawl)

`tools/spot_check.py` on a fresh crawl (`evidence/crawl-spotcheck-2026-11-02b.json`, 145 URLs): all 54 meta edits show the exact applied title/description, 200, self-canonical, no noindex, parseable JSON-LD, no duplicate Article/FAQPage/BreadcrumbList, one H1; Article JSON-LD present on page 1029; all 18 related-reading blocks present exactly once with 23 unique links, every one HTTP 200 with no redirect. **Problems: 0. No regression found, so no corrective edit was made.** Site-wide: no non-200, no JSON-LD parse error, no noindex, one H1 everywhere.

## D. Outstanding

1. 5 outbound blocks (9 links) from the new posts, waiting for the content session's corrected IDs and block counts; locks and insertion indexes must be recomputed then.
2. Visual polish of the three hub blocks is optional (see B).
3. Ahrefs/Search Console data is still unavailable; measurement per `05-GSC-MEASUREMENT-PLAN.md`.
