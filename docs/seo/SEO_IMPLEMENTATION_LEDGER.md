# SEO implementation ledger - 2026-11-02

Branch `feature/seo-competitor-implementation` (cut from `feature/experience-2-living-archive-sprint5` @ `9a74ecda`). Companion to `docs/experience-2.0/IMPLEMENTATION_LEDGER.md`.

## Summary

- Applied to finalvestige.com through the WordPress.com content tools after explicit user approval in the session: **54 meta edits** and **18 appended link blocks**.
- Verified on the public site by re-crawl (`evidence/crawl-after-2026-11-02.json`): meta 54/54, inserts 18/18. Failures: 0.
- Whole-site check after the change: 140 URLs crawled, non-200: 0, canonical mismatches: 0, pages not in the change set whose title or description changed: 0.
- **Homepage (page 6) was not edited.** Re-read after the change set via `page-sections.list`: modified `2026-11-02T17:48:13`, content_hash `1207973a80fb6618dcc91bd56131140a82854979`, block 1 SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277` (unchanged).
- No Preparedness Archive content was published; no safety claims were added (only navigation links and title/description wording drawn from existing text).
- No plugin, theme, menu or setting change. Schema comes from the existing Jetpack SEO `jetpack_seo_schema_type` field.

## Known gaps (stated, not hidden)

- **Ahrefs returned `Insufficient plan` for every data call**, so there is no keyword, traffic, ranking or Search Console number anywhere in this work. Competitors are SERP-observed and unverified by a tool (`01-COMPETITORS-AND-GAPS.md`). The keyword work can be redone from an Ahrefs/Semrush export or Search Console access.
- Effect on rankings is **unknown**. `05-GSC-MEASUREMENT-PLAN.md` defines how to measure it.
- The wp-admin browser session expired mid-task and I cannot sign in for you; the pre-edit snapshot was taken before that. Post-edit state is verified from the public site and the tools' own returned hashes, not from a second wp-admin snapshot.
- The 5 posts published by the content-packages session (IDs 1917-1926) appeared during this work; they are not in the change set and were not touched. The crawl takes its URL list from the public REST API, which did not list them yet (140 URLs both before and after), so they are also outside the before/after crawl comparison.

## Rollback (applies to every row below)

- **Meta edit:** `pages.update` / `posts.update` with `meta` set to the raw *before* values in `04-CHANGESET-DIFFS.md` (an empty before-value means set the field to an empty string). Success = the public `<title>`/description return to the baseline in `evidence/crawl-baseline-2026-11-02.json`.
- **Link block:** `post-sections.list` / `page-sections.list`, find the top-level `core/group` with class `fv-related-reading` (last block; index = the *index* column), then `post-sections.remove` / `page-sections.remove` with its `block_hash` and the fresh lock tokens. Success = `content_hash` equals the *content_hash before* column.
- **Full revert of a body:** the pre-edit raw content of every post and page is in `Projects/fv-release-backups/seo-2026-11-02/raw-content-2026-11-02.json` (outside the repo, keyed by ID), and WordPress keeps a revision for each save.
- **Schema test (page 1029):** set `jetpack_seo_schema_type` back to an empty string.

## A. Link-block inserts

| ID | URL path | Op @ index | content_hash before | content_hash after | In-content internal links before / after | Links added / found live | Verified |
|---|---|---|---|---|---|---|---|
| 291 | /2026/08/19/one-bulldozer-never-came-back-teton-dam/ | post-sections.insert @ 151 | `fdead53668fe` | `54c40d4d3a24` | 18 / 22 | 4 / 4 | yes |
| 166 | /2026/08/18/they-checked-the-dam-that-morning/ | post-sections.insert @ 71 | `28f3e97e6e98` | `de78a48874c4` | 15 / 19 | 4 / 4 | yes |
| 146 | /2026/08/17/the-dam-that-didnt-fail-vajont/ | post-sections.insert @ 124 | `b6ca5ffa5eb3` | `db8d44d37c48` | 17 / 21 | 4 / 4 | yes |
| 258 | /2026/08/18/inside-the-joint-silver-bridge/ | post-sections.insert @ 47 | `89f6444bcac9` | `6e1eb769633d` | 17 / 21 | 4 / 4 | yes |
| 276 | /2026/08/19/add-no-more-load-quebec-bridge/ | post-sections.insert @ 127 | `c89c04a114ed` | `0e89882fde37` | 17 / 21 | 4 / 4 | yes |
| 287 | /2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/ | post-sections.insert @ 150 | `a544fcd0a386` | `ffda2830ae5f` | 18 / 22 | 4 / 4 | yes |
| 285 | /2026/08/19/the-light-said-closed-three-mile-island/ | post-sections.insert @ 174 | `458dbcd1a6e5` | `3695c914530a` | 17 / 21 | 4 / 4 | yes |
| 221 | /2026/08/18/the-rod-was-supposed-to-move-four-inches/ | post-sections.insert @ 87 | `133047d2abc2` | `4e4e5c7c0f01` | 16 / 20 | 4 / 4 | yes |
| 434 | /2026/08/20/the-hatch-opened-inward-apollo-1/ | post-sections.insert @ 109 | `9d6d843d2aa9` | `150e8e23ef66` | 19 / 22 | 3 / 3 | yes |
| 269 | /2026/08/18/the-watch-lost-its-hands-halifax-explosion/ | post-sections.insert @ 88 | `9c2344aac7c2` | `5ef9456e91e1` | 16 / 19 | 3 / 3 | yes |
| 433 | /2026/08/20/all-well-was-written-first-franklin-expedition/ | post-sections.insert @ 116 | `01679145e2a8` | `ad8b8783c717` | 17 / 20 | 3 / 3 | yes |
| 1029 | /the-failure-chain/ | page-sections.insert @ 3 | `20e04c63d57d` | `7fa7dde522c8` | 3 / 12 | 9 / 9 | yes |
| 189 | /the-archive-trail/ | page-sections.insert @ 2 | `eaaa1ba9a9d8` | `9b9ecb82aa35` | 2 / 5 | 3 / 3 | yes |
| 1313 | /accountability/abuse-of-power/watergate-plumbers-abuse-of-power/ | page-sections.insert @ 1 | `d29b4a61c1f0` | `1e8a3fa35dd8` | 0 / 4 | 4 / 4 | yes |
| 1314 | /accountability/abuse-of-power/iraq-wmd-intelligence-public-claims/ | page-sections.insert @ 1 | `4991836cbdf1` | `e95d3f281035` | 0 / 4 | 4 / 4 | yes |
| 1316 | /accountability/public-money-private-power/andrew-do-orange-county-covid-relief-funds/ | page-sections.insert @ 1 | `a2bfcb96e36b` | `1d8291fa36d3` | 0 / 4 | 4 / 4 | yes |
| 1315 | /accountability/public-money-private-power/maximus-public-money-private-infrastructure/ | page-sections.insert @ 1 | `0597b9c12712` | `405c2007e906` | 0 / 4 | 4 / 4 | yes |
| 1312 | /accountability/failures-to-protect/gabriel-fernandez-warnings-in-the-system/ | page-sections.insert @ 1 | `ba8880bab634` | `edc7ad2fa75e` | 0 / 3 | 3 / 3 | yes |

Full 40-character hashes are in `evidence/verification-2026-11-02.json` and `evidence/changeset.json`.

## B. Meta edits

| ID | URL path | Fields | meta SHA-1 before | meta SHA-1 after | Verified on public page | Detail |
|---|---|---|---|---|---|---|
| 14 | /affiliate-disclosure/ | description, title | `87ceb91d5a34` | `cd1a3a7bdac1` | yes | title OK; desc OK |
| 15 | /privacy-policy/ | description, title | `5c4559dfba9e` | `d75a789f16a4` | yes | title OK; desc OK |
| 16 | /terms-disclaimer/ | description, title | `20022d3f6622` | `ddf92a43450d` | yes | title OK; desc OK |
| 156 | /2026/08/17/they-lifted-the-city-galveston/ | title | `c908cd9605a6` | `4bc8f1bf541e` | yes | title OK |
| 166 | /2026/08/18/they-checked-the-dam-that-morning/ | title | `83a35851c08d` | `4b54f057e0b8` | yes | title OK |
| 190 | /2026/08/18/the-hoses-that-wouldnt-fit/ | title | `88a8ff7be2b2` | `345c731da0b0` | yes | title OK |
| 211 | /2026/08/18/the-men-who-wouldnt-turn-left/ | title | `31d4299360bd` | `424c898e516f` | yes | title OK |
| 214 | /2026/08/18/the-lifeboats-never-left-the-deck/ | title | `d33398c05c90` | `b8eb43bbf4f8` | yes | title OK |
| 216 | /2026/08/18/the-fire-department-was-already-there/ | description, title | `4d612918a204` | `f70737119a4b` | yes | title OK; desc OK |
| 220 | /2026/08/18/too-deep-for-the-rescue-bell/ | title | `6dbe11698a60` | `a7d73e80ff5c` | yes | title OK |
| 221 | /2026/08/18/the-rod-was-supposed-to-move-four-inches/ | description, title | `f81696233889` | `95ee6be1e2de` | yes | title OK; desc OK |
| 252 | /2026/08/18/they-thought-the-books-were-charcoal/ | title | `e205d78a1551` | `e030115b3bc1` | yes | title OK |
| 253 | /2026/08/18/the-life-preservers-had-passed-inspection/ | title | `919626b61419` | `5150293cf762` | yes | title OK |
| 256 | /2026/08/18/the-torch-never-reopened/ | title | `4f7d5ae52eaa` | `65e2a817d5a9` | yes | title OK |
| 258 | /2026/08/18/inside-the-joint-silver-bridge/ | title | `d316d77143e5` | `6b6b0a37c6f2` | yes | title OK |
| 269 | /2026/08/18/the-watch-lost-its-hands-halifax-explosion/ | description, title | `4fa56004db19` | `8716c86d9eb2` | yes | title OK; desc OK |
| 274 | /2026/08/19/twenty-four-feet-from-air-uss-tang/ | title | `f4de658a5c05` | `c2bfa57831a9` | yes | title OK |
| 278 | /2026/08/19/they-walked-beyond-the-search-lady-be-good/ | title | `0d0cd4d35448` | `35a8318ec273` | yes | title OK |
| 279 | /2026/08/19/the-geologists-found-the-spy-satellite/ | title | `c011b7a12e66` | `eaa0ee7aec15` | yes | title OK |
| 280 | /2026/08/19/the-sledgehammers-broke-first-uss-pueblo/ | title | `9c24e73d72aa` | `b21957e6ad2c` | yes | title OK |
| 283 | /2026/08/19/the-crowd-became-the-lock-iroquois-theatre/ | title | `ed7d86c84334` | `5c4971f09358` | yes | title OK |
| 285 | /2026/08/19/the-light-said-closed-three-mile-island/ | description, title | `225da231c822` | `0087f261ea47` | yes | title OK; desc OK |
| 287 | /2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/ | title | `072f7a865c14` | `132b7ef8d1cb` | yes | title OK |
| 290 | /2026/08/19/the-city-kept-moving-camp-century/ | title | `6b01820f3c7b` | `aa16c28a4707` | yes | title OK |
| 299 | /2026/08/19/thirty-men-were-enough-vasa/ | title | `683cc5f9d29b` | `16a39fd87174` | yes | title OK |
| 370 | /2026/08/19/the-lines-were-in-the-fire-west-loch/ | description | `e297a98a027e` | `88d501178f80` | yes | desc OK |
| 747 | /community/ | title | `7351e6d94441` | `c85b23681273` | yes | title OK |
| 1027 | /the-turning-screw/ | description | `53c4b23b6b07` | `ed85dbf208fc` | yes | desc OK |
| 1029 | /the-failure-chain/ | description, schema | `71c79236fb39` | `aa1730fa99fa` | yes | desc OK; Article JSON-LD present |
| 1033 | /the-signal-chain/ | description | `da16321f14e3` | `645b55033849` | yes | desc OK |
| 1044 | /the-findspot/ | description | `f593e39753b4` | `6c33a9694496` | yes | desc OK |
| 1054 | /the-old-line/ | description | `88b8b4e17d03` | `0a3ba8c38561` | yes | desc OK |
| 1060 | /the-open-account/ | description | `6811f5aa6b29` | `8f583532f201` | yes | desc OK |
| 1120 | /the-working-order/ | description | `c9329d69ac8f` | `e0eba1ac1c90` | yes | desc OK |
| 1122 | /the-missing-caption/ | description | `acf77cc0a56e` | `43f21fff8f11` | yes | desc OK |
| 1123 | /the-paper-witness/ | description | `ac69b3b841c2` | `2829059eb4b7` | yes | desc OK |
| 1125 | /the-builders-trace/ | description | `05f697317ee4` | `b256bc9a70c5` | yes | desc OK |
| 1127 | /the-enumerators-block/ | description | `810755c04ed6` | `d88e59aad261` | yes | desc OK |
| 1148 | /archive-shelf/ | description | `cb0399b74231` | `7262c9fc51f7` | yes | desc OK |
| 1304 | /accountability/ | title | `7351e6d94441` | `8b2ffa96e211` | yes | title OK |
| 1305 | /accountability/failures-to-protect/ | title | `7351e6d94441` | `722543cb158d` | yes | title OK |
| 1306 | /accountability/public-money-private-power/ | title | `7351e6d94441` | `a44cb2600ee8` | yes | title OK |
| 1307 | /accountability/abuse-of-power/ | title | `7351e6d94441` | `a58420421033` | yes | title OK |
| 1308 | /accountability/votes-decisions/ | title | `7351e6d94441` | `58072040622e` | yes | title OK |
| 1309 | /accountability/watch/ | title | `7351e6d94441` | `8d85d36b62e0` | yes | title OK |
| 1310 | /accountability/ledger/ | title | `7351e6d94441` | `4ee883c2023f` | yes | title OK |
| 1311 | /accountability/evidence/ | title | `7351e6d94441` | `0d91092e93f1` | yes | title OK |
| 1312 | /accountability/failures-to-protect/gabriel-fernandez-warnings-in-the-system/ | title | `7351e6d94441` | `7c9ff5945fd9` | yes | title OK |
| 1313 | /accountability/abuse-of-power/watergate-plumbers-abuse-of-power/ | title | `7351e6d94441` | `6f7a6cb59355` | yes | title OK |
| 1314 | /accountability/abuse-of-power/iraq-wmd-intelligence-public-claims/ | title | `7351e6d94441` | `3d90380aa014` | yes | title OK |
| 1315 | /accountability/public-money-private-power/maximus-public-money-private-infrastructure/ | title | `7351e6d94441` | `6bc62254cf95` | yes | title OK |
| 1316 | /accountability/public-money-private-power/andrew-do-orange-county-covid-relief-funds/ | title | `7351e6d94441` | `c8f94ee69d28` | yes | title OK |
| 1480 | /podcast/ | title | `7351e6d94441` | `eae2c9eb5e69` | yes | title OK |
| 1484 | /podcast/the-textbook-found-open-in-the-ruins/ | description | `35ec721e8aca` | `4f7897185137` | yes | desc OK |

`meta SHA-1` is the SHA-1 of the JSON object of the edited fields (sorted keys, UTF-8). Body content is unchanged by meta edits, so each page's content SHA-1 (in `evidence/seo-prestate-2026-11-02.json`) is the same before and after.

## Findings not acted on

- Homepage structured data lists `Organization` twice (one from the theme/plugin, one from block 5 of page 6). Block 5 is inside the protected page-6 content, so it was not edited. Owner decision.
- 22 of the 24 method guides (`the-...`) still have one inbound content link; they need posts that genuinely use their method (see `03-INTERNAL-LINK-MAP.md`).
- Header/footer navigation was not changed.
