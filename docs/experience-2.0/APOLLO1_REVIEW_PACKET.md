# Apollo 1 Evidence Atlas page: independent review packet (revision 2, responds to the HOLD on `65f98aad`)

> **Current status addendum — November 4, 2026:** This packet preserves the November 3 **private, image-free revision-2 review** as historical evidence. The page is now **published** at https://finalvestige.com/apollo-1-evidence-atlas/ and has since received scoped centering fixes and three explicitly approved contextual NASA photographs tied to the timeline. See draft PR #991 and `APOLLO1_IMAGE_DECISION_SHEET.md` for the current source/rights state. The original `FVSL-QD-PASS` line immediately below applies only to the earlier revision, not to the current site. The enhanced current head has no hosted CI PASS while the GitHub job-start gate fails; do not mistake the earlier approved package for an exact-head acceptance.

**`FVSL-QD-PASS: NO`.** No independent reviewer has cleared this revision; the author issues no pass. Page 2017 is a **private, unpublished draft**. Prepared 2026-11-03. Earlier verdict being answered: HOLD, PR #798 comment 6607291873, head `65f98aad79369c9c8a3ef9dad4bea1f136bf43c5`. Author's full record: `APOLLO1_PAGE_DRAFT_RECORD.md`. Image decisions: `APOLLO1_IMAGE_DECISION_SHEET.md`.

## 1. Exact subject

| | |
|---|---|
| Branch / PR | `feature/atlas-apollo1-live`, draft PR #798, base `feature/experience-2-living-archive-sprint5` |
| Head to review | the full SHA is stated in the PR comment that links this packet (a docs file cannot name its own commit); the code and block files it refers to are the ones hashed below |
| WordPress draft | page **2017**, private draft, `apollo-1-evidence-atlas`. Preview (signed-in only): https://finalvestige.com/?page_id=2017&preview=true . Signed-out: 404 |
| Mechanism | **nine** top-level `core/html` blocks, no plugin; no header, navigation, homepage, global-style or template change |
| Draft readback | `page-sections.list` after the final write: all nine `block_hash` values equal the SHA-1 column below; `pages.get` in `context=edit` and `context=view` re-read and compared (section 9). Draft last modified 2026-11-03T14:18:31 |
| Homepage page 6 block 1 | SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277`, never touched by this work |

### Block hashes (stored form = file without its trailing newline; WordPress `block_hash` = its SHA-1)

| Block | Bytes | SHA-1 (= WordPress `block_hash`) | SHA-256 (stored form) | SHA-256 (committed file, +`\n`) |
|---|---:|---|---|---|
| 00-style | 23,748 | `bbf054a2f48f970fb560466102899d2c413a33fa` | `9c345e7d09b01c71953e80fc93d8cf5ecd0421d7985fb5b8b0df942a9ab95f8b` | `bd76f0a27c4430bdea43d8edbe217b320eae279eb9af469add2893e46d37aeef` |
| 00b-style-text | 260 | `81cce82b98d1a20ceac5ce81c1b92db5c1d6430a` | `ddc89f367d4b3c75841a3e2063fd0e35c89d8ac9f62a3d1228856193558af2c3` | `2122ef64ba74dce3c7a7efb4d13ecbf7ea447420a3e0b25f220c79f26b6e12fd` |
| 01-investigation | 18,676 | `1514f90217616678da8070201b0aeaa78504037c` | `a695928e1f9a73e4fd24209d6af86a326f459781783b01c5eca22272fe833ce7` | `eb8ee9d5a0638d57d70f2821744d1f4e2369c5f90e23726f4354ce7cf6554bb3` |
| 02-classification | 1,216 | `29e44fc0d5309c433850ef107cb75e6e907283c9` | `d1a13f733de52c0bae1feecbeb411b6143191d666807c90e9c8b828ee0002ed2` | `9317d7a17e24a76a50b259168d9eaee0782790eaa7802abaf9416f462d7dbfc5` |
| 03-research-desk | 27,958 | `2b20e5dc8127f96dec7308af7f74203f42a635ae` | `02a1ebe59bf5c7c66e4958efc4d2ea7f9a64a9ed675d3b50cef82165b4f02e85` | `9d2ff551b85a2ca395a4ae0756571cbc3a6bbd35ceab09c148df193dbfa0d9ca` |
| 04-rights | 4,193 | `ab57e96b46fab88bbbba9061bb0696268be1e9a7` | `166779789a8839183649338a580a04bddfd8b1634c6b87bf180bfee6b66262db` | `e6babbf1ac89b95d270834979f9fb0bbec2012fb72b5f016fde1ead7ce2bf9b3` |
| 05-related | 1,890 | `3ccc0c6ce3d9f3fef520b26501c93e5927867d4a` | `6b5b9e53d336d4a32aeb248a54151ebd7c648f670c271eb24cb6009463fe6a05` | `05054781ba29931e8619179f443d2689bbaa01cbaa1be37dfbaef61f96c67cc8` |
| 06-footer | 496 | `10351c226f0be67a780c89aba99b8942e5ee2fec` | `d557a650ad2367254ce6b990ea33671b734b15a0961d83e2d66e3283675bce23` | `cf2f3b4d3610a5ff3cfe760c09e88c82cfdfdb64a12159dd015521e690d76b91` |
| 07-script | 9,750 | `d8f1ddea4f13ae283072093b2bb8d597e558a38e` | `f0e37c2d90ace6d2b6cd014951bcd1e67c87741789bcd463091e389b7b685296` | `34a5093c520dd6e783c135b8f62c8d51cef7842e74c64a83d1da08806020d4fc` |

Whole page content (committed files joined by one newline, 88,204 bytes): SHA-1 `4df60e9f07c59ae11d4c15c91c968f0c58a482f7`, SHA-256 `d06613cba4c276645440813192512c49ac3331459a14fd91efbd304c1e45ddfb`. Block 00 is byte-identical to the first revision; `00b` holds the two CSS rules for text-only chapters; block 07 changed in revision 3 (below).

Sources of the build (SHA-256): `data/apollo1.json` `dbcb8cc25544b35e49cdfdebf62b498cac653283bb34af186a4d65f8f2672721`; `atlas/data/atlas.json` `ec1f6513fa790d7416dd1fa4f4aea7fa60be9b36507e0baa08ab453b3eb4d40f`; `page-blocks/image-signoffs.json` `578d9dbe3239332218d130f1b97707f495f3ca3fa550fa6e22e5a38e640f1cf9` (no approvals); `page-blocks/manifest.json` `1ceb6ffba47ad1d9cf240a48f0c219be29e56b9dc2e7d295619c1cbe13043d6f`.

## 2. How each point of the HOLD was handled

| HOLD point | Result | NASA source used (verbatim quotes are in the Research Desk crosswalk on the page) |
|---|---|---|
| Inward-opening Block I hatch | Stated on the page and marked verified: "the innermost one opening inward and taking 90 seconds to open under ideal conditions" | NASA History, "55 Years Ago: The Apollo 1 Fire and its Aftermath" (J. Uri, 3 Feb 2022) |
| Unfueled test | Verified; also the Board's own Part IV statement that the Plugs-Out Test was not classified hazardous because only tests involving fueled vehicles were. The "Saturn IB" and "countdown rehearsal" wording, which no source I could read confirms, was removed | same NASA History article; Board report Part IV |
| Ed White and the hatch | Verified in two steps: the Board says emergency procedures called for the Senior Pilot to unlatch and remove the hatch and that his harness buckle was found unopened, indicating he began the procedure; the NASA crew biography names White as Senior Pilot. **The biography does not say White opened the hatch during the fire**, so the page does not claim it | Board report Part V (invest.html); NASA, Detailed Biographies of the Apollo 1 Crew |
| Probable arc and no single source | Both stated: Finding 1 Determination, "The most probable initiator was an electrical arc in the sector between -Y and +Z spacecraft axes", and "No single ignition source of the fire was conclusively identified" | Board, Findings, Determinations and Recommendations (find.html), read in full |
| Outward-opening quick hatch | Stated as NASA's article words it: a unified hatch openable from inside or outside "in three seconds", with "the new outward-opening unified hatch". The article does not say "quick-release"; the page does not either. **Discrepancy recorded:** the 2017 museum exhibit text gives 5 seconds for the Block II hatch; the page uses NASA's article and the exhibit photograph is not shown | same NASA History article |
| 102 flammability tests | Stated as NASA words it: "three series of tests comprising 102 deliberate ignitions between December 1967 and February 1968", Boilerplate 1224. The page says "ignitions", not "tests" | NASA History, "50 Years Ago: Apollo Flammability Tests" (14 Feb 2018) |
| "Fourteen seconds" heading | Now **"About fifteen seconds changed the system."** The chapter states both measures: the Board's "approximately 15 seconds after the verbal report" for the first stage, and 14.7 seconds counting 23:31:04.7 to 23:31:19.4 | Board report Part V, Chronology of the Fire |
| Internal notes in visitor text | Removed from every block: no "Sprint 5", "not re-checked", "confirm", "candidate", "human rights review pending", "integration candidate", "prototype". Related-investigation lines no longer print Atlas date status. A test fails if any returns | n/a |
| Three labels | Documented / Interpretive stay; **no claim is left "open"** because every claim now cites a named NASA source. The Open-question label still exists in the renderer and a test proves it would appear if an unverified claim ever returned | n/a |

Two corrections to my own earlier text, found while checking sources: I had removed an unsourced sentence about orbital pressure ("not the same regime the spacecraft would use in orbit") and an unsourced statement that fire "destroyed crucial physical evidence"; neither is on the page now. Also, NASA pages disagree on cabin pressure (16.7 psia in the Board's Finding 2, 16.2 psi on the flammability article); the page uses the Board's figure.

**What I could not close:** the NASA History article's three-second and "inward" wording was read in full text by a second pass but both of my passes went through an automated fetch tool, not a browser; the reviewer's own check of the same sentences is the independent confirmation. The Board's Part VI and appendices were not read beyond Findings 1, 2, 4 and 9.

## 3. Image rights: the first release shows no photographs

Per the founder's rule, an image without a named-editor sign-off is omitted. **No row is signed, so all six NASA photographs are omitted** and the page stands as text and documents. The six-row decision sheet (use, credit, record URL, identity evidence, risk points, recommendation, blank decision fields) is `APOLLO1_IMAGE_DECISION_SHEET.md`; the homepage sign-off is explicitly not carried over. Signing a row is a one-line entry in `page-blocks/image-signoffs.json` (tested: entries missing editor, date or use are ignored), after which the plate appears with its caption, credit and provenance. The rights block lists the six photographs as "not shown" with their NASA record links and the editorial-use restriction.

## 4. Local evidence (not hosted CI)

`tools/verify_apollo_page.py` serves the live Assembler shell (GET) with the nine committed blocks as `entry-content`; analytics hosts are blocked. **This is not the WordPress.com render.** Raw JSON in `docs/experience-2.0/evidence/apollo1-page/`.

- Six widths 360, 390, 768, 1024, 1440, 1920: one `h1`, valid heading order, no duplicate ids, no horizontal overflow, no page errors, both modules ready, all external links `noopener noreferrer`, no images (none are shown).
- axe-core 4.10.2 (wcag2a/aa, 21a/aa, 22aa, best-practice): **0 violations, 0 incomplete** at all six widths and with motion on, block scope and whole page.
- Real throttled mobile method (390x844, 4x CPU, 150 ms RTT, 1.6 Mbps, cache off; LCP read before any scripted scroll): **12 runs, LCP median 1,770 ms, max 1,896 ms; CLS 0.0731 in every run.** Earlier batches on near-identical blocks produced one 2,716 ms outlier in 19 runs, so the 95th percentile against 2.5 s is still not demonstrated. Desktop median LCP about 0.4 s.
- Behaviour: desk search and empty state, anchors to each desk record, chronology slider ("Nothing is recorded between markers"), one current chapter, JavaScript off gives a complete document, controls at least 24 px.
- Repository: `test_apollo_page` 18, `test_atlas` 22, `test_browser` 31 pass; `test_builders` 19 pass (it fails intermittently with `OSError: Invalid argument` while writing `dist/apollo-1/index.html`, which looks like a file lock on the OneDrive-synced folder, not an assertion; it passed on the reruns). `build_all.py --check` OK; `build_dataset.py --check` OK; `validate_atlas.py` OK. The 9 PHP plugin tests cannot run on the author's machine (no PHP).
- **Hosted CI did not run on the previous head and has not run on this one: GitHub reports the jobs never start because recent account payments failed or the spending limit needs raising. That is a billing restriction, not a code failure. Local results above are not hosted CI and must not be described as such.**

## 5. Shared files changed (the plugin is staging-only and is not installed)

`fvx_lib.py` (validates optional `claim_sources`, row `url` and `source_ids`), `render_flagship._crosswalk` (a "NASA source" link when a row has a `url`), `render_desk(show_images=)`, `atlas/tools/build_dataset.py` (adds the five NASA claim sources and row-level source ids), `data/apollo1.json` (claims, wording, `claim_sources`), regenerated `atlas.json`, and the regenerated staging-plugin template and manifest (the crosswalk now carries source links). No existing assertion was edited.

## 6. Gates still open (none waived)

1. **Authenticated WordPress.com browser review of the revised draft: NOT DONE.** The in-app browser is not signed in (preview returns "Page not found" with no admin bar) and an assistant cannot enter credentials. To perform: founder signs in; then check the nine `block_hash` values, one `h1`, interaction, six widths, links, console and network, and that header, footer and navigation are unchanged.
2. Independent QD of this revision's exact head and hashes.
3. Named-editor sign-offs (or the documented omission) for the six images.
4. CI: billing fixed and hosted `experience-2` green on the exact head.
5. Founder approval to publish; title, slug, indexability.

## 7. Apply and rollback

- **Apply** (only after the gates): one `pages.update` on page 2017 with `status: publish`; then verify signed-out (HTTP 200, one `h1`, `page-sections.list` shows nine matching hashes, page 6 block 1 still `8c0dd5c3...`, sitemap entry), then the links from the Research Desk, Discovery Library and the related investigations as separate steps. The header and homepage go through their owner.
- **Add an image later:** sign its row, rebuild, `page-sections.replace` the changed blocks against their recorded `block_hash`, re-read.
- **Rollback now:** `pages.delete` on 2017 (trash, restorable). After publish: `pages.update` to `draft`, confirm the slug is 404 and page 6 is unchanged. No other object changes; nothing to deactivate.

## 8. Questions for the reviewer

1. Do the nine stored hashes equal the committed files at the reviewed head? 2. Is each claim on the page matched by a quote in its crosswalk row that you can find at the cited NASA URL? 3. Is the "About fifteen seconds" chapter clear about which interval is meant? 4. Is any visitor text still an internal note? 5. Is a page with no photographs acceptable as the first release, and is the decision sheet's default (omit all) right? 6. Does anything outside these nine blocks change?

## 9. Revision 3: the `&&` rendering defect (found by the independent reviewer on `40c891e9`)

**Defect.** WordPress's output filters rewrite a bare ampersand to `&#038;`. In the served inline script two of the 14 `&&` operators (the source-drawer Next handler and the timeline "upcoming marker" test) became `&#038;&#038;`, a JavaScript syntax error that would stop the script. The stored block was correct; the damage happened on render. The page's own content stays readable because it is complete HTML first, but the interactions (chronology slider, desk search, chapter bar) would not have started.

**Fix, narrowest form.** Every `&&` in the shared source `design-system/src/js/fv-ex2.js` is now an explicit `if` or conditional expression with the same meaning (13 lines; the script now contains **no ampersand at all**). No design, NASA citation, historical text or interaction changed. Block 07 is the only block whose bytes changed; the other eight stored hashes are unchanged. The staging-plugin copy of the script and its manifest regenerate from the same source.

**Evidence.**
- Reproduction before the fix (local, not the server): the committed script compiles with node as stored, and fails to compile after a conversion pass that rewrites bare ampersands; the reviewer's observation on the served draft is the primary evidence.
- Draft 2017 after the fix: block 07 rewritten, `block_hash` `d8f1ddea4f13ae283072093b2bb8d597e558a38e` = source. `pages.get` `context=view` (87,895 characters, saved to a file and processed locally): **0 occurrences of `&#038;`**, the served inline script is **identical to the source script** and passes `node --check`. `pages.get` `context=edit`: all nine stored blocks are byte-identical to the committed files; the served and stored scripts and style blocks are identical.
- Two new tests in `test_apollo_page`: no bare ampersand in any block outside a valid entity, and the script compiles with node both as committed and after a conversion pass that changes nothing. They require `node` and fail without it (no skip).
- Local browser acceptance and repository tests are in section 4's list, re-run on this head. **The page has no source drawer** (no dialog and no source buttons), so the drawer's Next handler is not reachable here; it is exercised by the repository's drawer tests on the flagship page, which pass with the fixed script.
