# Apollo 1 Evidence Atlas page: independent review packet

**Status: READY FOR INDEPENDENT REVIEW. Not published. No QD PASS exists and none is claimed by the author (`FVSL-QD-PASS: NO` until a reviewer other than the author records it).** Prepared 2026-11-02. Author's full record: `APOLLO1_PAGE_DRAFT_RECORD.md`.

## 1. Exact subject

| | |
|---|---|
| Repository / branch | `finalvestigestudios/final-vestige-site-layer`, `feature/atlas-apollo1-live` (not pushed at the time of writing) |
| Code head to review | **`43548df7a6be3b8074706cb45520ae176e25ac24`** (this packet and the record are docs-only commits on top; review the files below at that commit) |
| Committed blocks | `experience-2.0/page-blocks/apollo1-investigation/00..07*.block.html`, manifest `experience-2.0/page-blocks/manifest.json` |
| WordPress draft | page **2017**, private draft, title "Apollo 1: The Evidence Atlas", slug `apollo-1-evidence-atlas`. Edit: https://finalvestige.com/wp-admin/post.php?post=2017&action=edit . Preview (signed-in only): https://finalvestige.com/?page_id=2017&preview=true . Signed-out it is 404. |
| Mechanism | eight top-level `core/html` blocks, inline CSS and JS, **no plugin**, no template, header, navigation, homepage or global-style change |
| Draft last modified | 2026-11-02T23:15:36 |

### Block hashes (stored form = the block without the file's trailing newline; WordPress `block_hash` is the SHA-1 of that form and **was read back and equals this table for all eight blocks**)

| Block | Bytes | SHA-1 (= WordPress `block_hash`) | SHA-256 (stored form) |
|---|---:|---|---|
| 00-style | 23,748 | `bbf054a2f48f970fb560466102899d2c413a33fa` | `9c345e7d09b01c71953e80fc93d8cf5ecd0421d7985fb5b8b0df942a9ab95f8b` |
| 01-investigation | 32,669 | `7ce8f575b8ae075699785672020c571691c8ba1f` | `c8ffc9a84bd5530aadb4ec348eb918e1b0dd143be58206e3146a982588ec67a6` |
| 02-classification | 3,503 | `dc62ad1669b81ac1d84e0ba9be486cdad47c4cda` | `89db03241291c38fa2c6f699f515193af4b87315df698a12f3fed47a90454b36` |
| 03-research-desk | 22,550 | `4abe3e8ea0f17a2277f0135a1bca9ee8135fdc2f` | `1b1a358a6c01650181a1834eaa186f9502a94ba40ba9a807e508732b7f639bd4` |
| 04-rights | 8,318 | `dd84742473035a78ecea66ec7c03296f6ce84b20` | `bb0cab82b1ee0b495ee520c80cfb879582ad36fb8df1d68fb158250321732e13` |
| 05-related | 2,026 | `173982203da9eb3a8dff4e91d82725148d4afa86` | `851d7dcc51acb0be5f5bcea8b3f79026f1cbf162c73f5a8dae20c804cc04dd8a` |
| 06-footer | 564 | `b0c723e2b898eaf47bea17dcf3809001b98e7190` | `3434198cb9a09ba031219be4570c0257b63803258f58fcd8345a7aac455a0338` |
| 07-script | 9,655 | `2f4df25d143a4d559005aca8fb46d4d49f75b4ba` | `e6169fec1bb92471fecb4d32eeacb3de611d0b8bcc6ba865a664f534885e8c93` |

Committed files include one trailing newline each; their SHA-256 values are in the manifest. Whole page content (committed files joined by one newline, 103,048 bytes): SHA-1 `fc93015a77e55fae8a50d64b120ea748df6eea22`, SHA-256 `5ac375e00f31d0bee9e89b5248502296397a1ea2b290094167142192b68b1cbf`.

Live homepage page 6 block 1: SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277`, untouched (re-read after every write).

## 2. How it was tested, and what the method is not

`tools/verify_apollo_page.py` serves the **live Assembler shell** (GET of a published page: header, footer, theme CSS) from localhost with the eight committed blocks placed in `entry-content` exactly as WordPress prints `core/html`. Analytics hosts are blocked. Playwright + Edge + axe-core 4.10.2. **This is signed-out-equivalent. It is not the WordPress.com render of draft 2017**: that needs the founder's signed-in browser (gate below). Raw JSON: `docs/experience-2.0/evidence/apollo1-page/{structure,axe,behaviour,perf}.json`. Reproduce: `python experience-2.0/tools/verify_apollo_page.py all --runs 7` (needs network, Playwright, Edge or Chrome).

### Six widths (360, 390, 768, 1024, 1440, 1920), all PASS

One `h1`, valid heading order, no duplicate ids, no horizontal overflow (`scrollWidth - innerWidth = 0`), 6 of 6 images load, page root equals the viewport width, no page errors, both modules `data-fvx-ready=true`, every `target=_blank` link has `noopener noreferrer`.

### axe-core 4.10.2 (tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice)

0 violations and 0 incomplete at each of the six widths and at 1440 with motion enabled, for the block scope and for the whole page. (An earlier build had 12 "incomplete" contrast checks caused by a decorative gradient over the hero photograph; the photograph and gradient were removed.)

### Real throttled mobile method (390x844, 4x CPU, 150 ms RTT, 1.6 Mbps down, 750 kbps up, cache off; LCP read before any scripted scroll, CLS after)

| Runs on the final block | LCP | CLS |
|---|---|---|
| 12-run batch | median **1,810 ms**, max 1,860 ms | 0.0731 in every run |
| earlier 7-run batch on the same block | median 1,800 ms, **max 2,716 ms (one outlier)** | 0.0731 |

18 of 19 runs are at or under 1.89 s; one run reached 2.72 s, over the 2.5 s limit, and was not reproduced in the 12 runs that followed. **Please treat the p95 as unproven**; the limit is the founder's (LCP <= 2.5 s, CLS <= 0.10). LCP element: `p.fv-ex2-hero__dek` (text). Desktop 1440: LCP median about 0.4 s, CLS 0.0014. These are lab numbers on a local copy of the theme, not field data and not the WordPress.com origin.

### Behaviour and fail-open

Desk search and empty state, anchor from each plate to its desk record, chronology slider reports "Nothing is recorded between markers", one current chapter, **JavaScript disabled: complete document** (7 chapters, 6 records, 5 related), optional controls hidden, buttons and chapter links at least 24 px.

### Repository tests

`test_apollo_page` 14, `test_builders` 19, `test_atlas` 22, `test_browser` 31: pass. `build_all.py --check` OK. 9 plugin tests (PHP) error only because PHP is not installed on the author's machine; the plugin is not part of this change. One transient `test_builders` error was seen once and did not recur in 6 reruns.

## 3. What the page claims, and how each claim is labelled

Three labels, all derived from the committed data, not typed by hand: **Documented**, **Interpretive** (Atlas relationship `basis`, with its stored justification; Atlas `review_status` is `unreviewed` for every item and the page says "Not yet reviewed"), and **Open question** (every crosswalk row that is not `verified`, shown inside its chapter and again in the Research Desk). A test fails if an unverified row is not flagged in its chapter.

### Open questions on the page, and what the author could and could not check against NASA's text

The author fetched the Board report page on nasa.gov (verbatim text of Part IV and Part V sections 1 to 3; Part V section 4 and Part VI only as a model-extracted summary; the summary PDF has no text layer; the appendices were not read).

| Claim shown as open | Status on page | Finding |
|---|---|---|
| Plugs-out rehearsal with an unfueled Saturn IB (ch. 1) | article only | not checked against the report in this pass |
| The Block I hatch opened inward (ch. 4, and the page title) | article only | **No sentence stating the opening direction was found** in the readable text. Nearest: "opening the inner hatch is impossible because of the resulting force on the hatch" (Part IV section 4), and Finding 4 (summary): "Due to internal pressure, the Command Module inner hatch could not be opened prior to rupture of the Command Module." Direction would need NASA history or the appendices |
| An electrical arc was the most likely initiator (ch. 5) | partial | Found only in the **extracted summary, not verbatim-verified**: Part VI Finding 1 "The most probable initiator was an electrical arc in the sector between -Y and +Z spacecraft axes". Verbatim in Part V section 3: arcing named as one possible cause of the electromagnetic change, not as the conclusion. Needs the appendix or PDF text to close |
| NASA redesigned the hatch to open outward quickly (ch. 6) | partial | **Not found** in the Board text; the 5-second figure rests on the museum exhibit photograph only |
| 102 ignition tests of boilerplate 1224, Dec 1967 to Feb 1968 (ch. 6) | article only | not checked in this pass |
| Chapter title "Fourteen seconds" vs the Board's "approximately 15 seconds" (ch. 3) | editorial note | open editorial decision |

The data files were **not edited** by this pass (they are the Sprint 5 evidence record). The two findings above (arc wording located in the summary; direction and outward redesign still absent) should be applied to `atlas/data/curation.json` by a reviewer or the editor before publication if accepted.

**Decision the reviewer or founder should make:** the page ships the story as the published article tells it, with each unresolved claim visibly labelled. The founder's alternative rule is to remove an element whose claim is unresolved. If chosen, the elements to drop are the sentence "The Block I command module used an inward-opening pressure hatch" and "Ed White was responsible for opening the hatch..." (chapter 4; the second has no crosswalk row at all), the "outward-opening" and "102 ignition tests" sentences (chapter 6), and the chapter and page titles that assert the direction. That edit is small but it changes titles that match the live article, so it is not applied without a decision.

## 4. Image register (named-editor sign-off still required for every row)

NASA Media Usage Guidelines (retrieved 2026-10-30): editorial use with NASA acknowledged and no implied endorsement; not for promotional, product or merchandise use. Status in the data for all six: "editorial-use basis recorded; human rights review pending". **No named editor has signed any row.**

| # | NASA ID | Shown as | Credit | Identity evidence | Sign-off |
|---|---|---|---|---|---|
| 1 | S67-19766 | Interpretive, crew near LC-34, served from finalvestige.com | NASA | NASA record page `apollo-1-crew-honored` carries caption and "Image Credit: NASA"; the ID appears only in the file name `s67-19766.jpg`, not as printed catalogue text, and the NASA Image API did not return it | open |
| 2 | S67-15717 | Interpretive, Spacecraft 012 processing | NASA | NASA Image API match, JSC, 1967-01-03 (verified 2026-10-30) | open |
| 3 | S66-58038 | Interpretive, altitude-chamber training, 1966-10-18 | NASA | NASA Image API match | open |
| 4 | KSC-20170124-PH_KLS01_0129 | Interpretive, 2017 museum hatch display | NASA / Kim Shiflett | NASA Image API match | open |
| 5 | S67-21294 | **Documented**, interior of CM 012 after the fire, no people | NASA | NASA Image API match, 1967-01-28 | open |
| 6 | KSC-20170124-PH_KLS01_0090 | Interpretive, 2017 redesigned-hatch display | NASA / Kim Shiflett | NASA Image API match | open |

If a sign-off is withheld for a row, that plate can be removed without touching the others: it is one `<figure>` in block 01, one row in block 04 and one desk card; regenerate with `build_all.py` after removing the record's image, and re-hash.

## 5. Findings the reviewer should weigh

- The Desk and rights sections show data strings that read as internal notes to a visitor ("not re-checked in Sprint 5", "confirm before publication", "confirm wording", Atlas date status "candidate"). They are sourced and honest but unpolished.
- Mobile CLS 0.073 has little headroom (cause: web-font swap in the hero under the harshest throttle).
- The theme texturizes quotes on output; the local harness cannot reproduce that. Layout and axe are unaffected, but only the WordPress.com render shows it.
- The page replaces nothing: title, slug, indexability, and whether the Apollo 1 post links to it are open decisions. No nav entry was added (the founder owns navigation).

## 6. Gates still open

1. **Authenticated WordPress.com render of draft 2017**, same procedure as `PR604_WPCOM_DRAFT_RENDER_EVIDENCE.md`: needs the founder signed in; check `block_hash` of all eight blocks, one `h1`, console and network, screenshots at the six widths.
2. **Independent QD** of the exact hashes in section 1.
3. **Named-editor sign-off** per image (section 4) and the editor decision on section 3.
4. Founder approval to publish.

## 7. Rollback and publication

Nothing is live. Rollback now: `pages.delete` on 2017 (trash, restorable). After a publish: `pages.update` 2017 to `draft` (or trash), then confirm the slug returns 404 and page 6 block 1 is still `8c0dd5c3...`; no other object is changed, no plugin exists to deactivate. Publication, once all gates are clear: a single `pages.update` with `status: publish`, then verify signed-out (HTTP 200, one `h1`, eight block hashes via `page-sections.list`, sitemap entry) and record it.

## 8. Reviewer's questions

1. Do the stored hashes equal the committed files at `43548df7`? 2. Does the signed-in render match the harness? 3. Is any sentence on the page stronger than its crosswalk status allows? 4. Is the "documented" label used only where the source states it? 5. Are the open-question labels sufficient, or must the section 3 elements be removed? 6. Does anything outside the eight blocks change (diff the page list and page 6)?
