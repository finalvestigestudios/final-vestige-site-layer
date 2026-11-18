# Library — FRUS Document 225 worked case | Source, rights, QA and publication ledger

**Verified:** Wednesday, 18 November 2026, America/Los_Angeles (08:37–08:45 local).  
**Scope:** ONLY the unpublished Library child WordPress page #2917, “The Declassified Source Desk”; GitHub branch `review/library-declassified-source-desk-20261118` / draft PR #3010. No Research Sources #1338 changes, public Library edits, Preparedness, Investigations, home engineering, email or social actions.

## Deliverable and reader need

**The meeting that appears in a memoir** is an original, about 1,380-word worked research case and reusable 10-field printable document-identity receipt. It teaches how to distinguish an individual's later claim, a government historical edition's editorial note, a cited but not independently examined historical chronology, and a linked operational-plan entry. Each evidence layer is labeled separately; absent minutes are not conflated with proof the meeting never happened.

- Exact reusable Gutenberg block: [HTML source](docs/editorial/library/declassified-source-desk-frus-225-worked-case-2026-11-18.html) — **16,675 characters**, one top-level `core/html` block; one original explanatory SVG, three comparison cards, six research steps, ten printable fields and a source/provenance register.
- WordPress: https://finalvestige.com/wp-admin/post.php?post=2917&action=edit
- Expected unpublished public child: https://finalvestige.com/free-resources/declassified-source-desk/ (HTTP 404 for signed-out visitors during this run)
- Git commit creating source: `e5ad7747ca26a913f9c48166e26bcc578fb3f284`
- Git blob verified by independent readback: `b1356ede13c5dbd43c6e1edc7f65605a6863f48a`

## Evidentiary sources checked directly (18 November 2026)

| # | Institution / source | What was inspected and what it establishes | Limitations | Rights / access |
|---|---|---|---|---|
| 1 | [US State Department, Office of the Historian — FRUS Iran (2018 second edition), Document 225](https://history.state.gov/historicaldocuments/frus1951-54IranEd2/d225) | Inspected HTML editorial note. Editors relate Roosevelt's account of a June 25, 1953 meeting; report no official record found; cite chronology that records State and UK Foreign Office authorization July 11, and report no written presidential authorization found | The original memoir page, chronology, handwritten addition and CIA original box not independently inspected; editorial note is NOT meeting minutes | Institutional HTML linked, not copied as scanned media; individual third-party cited materials may carry rights |
| 2 | [FRUS Document 221](https://history.state.gov/historicaldocuments/frus1951-54IranEd2/d221) | Official entry for undated Draft Operational Plan, 29 pages not declassified | Does not date June 25 meeting or itself prove approval | Link-only |
| 3 | [FRUS Document 232](https://history.state.gov/historicaldocuments/frus1951-54IranEd2/d232) | Official editorial note on July 1 communication to Roosevelt about British approval and plans | Not a proof of U.S. presidential written approval; original cited communication not inspected | Link-only |
| 4 | [FRUS Sources, Iran second edition](https://history.state.gov/historicaldocuments/frus1951-54IranEd2/sources) | Government editorial account of CIA source files, losses of original operational cables, later microfilm transcriptions and qualifications | Not a complete inventory of every potentially surviving record; transcriptions are not original cables | Link-only |
| 5 | [FRUS second edition volume landing page](https://history.state.gov/historicaldocuments/frus1951-54IranEd2) | 2018 volume identification, edition and US GPO publisher | An edited official documentary edition, not an unmediated entire archive | Link-only |
| 6 | [FRUS citation guidance](https://history.state.gov/historicaldocuments/citing-frus) | Official citation guidance for identifying volume/item | Does not grant permission to republish third-party materials | Link-only |

### Rights and visual provenance
- **Original FV artwork:** standalone SVG research-route diagram created 18 November 2026; graphic is schematic and its visible caption identifies it as an explanatory design, **not** a 1953 facsimile, map, archival photo or AI reconstruction. Alt-equivalent: inline SVG `title`, `desc`, `aria-labelledby` and accompanying text.
- **No third-party media reproduced:** no memoir pages, CIA facsimiles, government scans, copyrighted photographs, stock art, YouTube clips or model-generated photographic reconstructions copied or uploaded.
- **Institutional permissions:** availability of U.S. government-hosted HTML does not establish public-domain status of all cited or embedded material, nor does declassification establish copyright clearance; external originals stay at official URLs.

## Actual WordPress integrity QA
- Before update: section list #2917 showed **one** `core/html` block, SHA-1 block hash `f80728c674aef2ef307bdc8e2b094109f3fc1d68`, last modified 2026-11-18 07:38:19.
- Inserted a **second** `core/html` block at index 1 with optimistic modified + content-hash locks. WordPress write confirmed at 2026-11-18 08:37:33.
- Fresh section-list readback: **2** blocks; prior block's hash unchanged `f80728c674aef2ef307bdc8e2b094109f3fc1d68`; appended block SHA-1 `61e79bcae2129d556e1f9400894f6a00441da038`. Updated full-content hash `12b6963b4d06a571fb2d831f2472f53b4c47b070`.
- Fresh `context=edit` page readback: stored content **47,046 characters**, complete 16,675-character saved Gutenberg block **exactly matches** GitHub-source byte content; new module's unique ID present **once** and original desk wrapper present **once**. Draft under parent #77; `jetpack_seo_noindex=true`.
- Static QA: one top-level Gutenberg HTML block; 15 link occurrences / 10 unique HTTPS destinations; 5 unique HTML/SVG IDs (zero collisions in new module); no scripts or external CSS/JS dependencies; zero outside image media. CSS scoped under `.fv-dsd-case`; responsive wrapping breakpoints at 760px and 420px; print styles provided. This is source review, **not** a browser or assistive-tech pass.
- Visitor readback: existing [Library](https://finalvestige.com/free-resources/) **HTTP 200** with canonical metadata; [Research Sources](https://finalvestige.com/free-resources/research-sources/) **HTTP 200** with established canonical metadata; unpublished child URL **HTTP 404**, as intended. The standard 404 footer/widget's empty-action links are unrelated to the new draft.

## Open release gates (HARD HOLD)
1. Actual production-theme **draft preview** screenshots and overflow verification at **320, 390, 768, 1440** widths. Public-page mshots do **not** certify the unpublished child page.
2. Real keyboard navigation / visible focus, screen reader SVG semantics and receipt comprehension, print/PDF paper break behavior (including Safari/mobile), and browser console/JS interaction checks against production theme. Static checks above cannot substitute.
3. Verify the document's final title, cards, header hierarchy, contrast and source URLs in an actual preview. Check whether the extra standalone block inherits full-width container styling; adjust only within #2917 if necessary.
4. Confirm enforceable **per-publication** `_jetpack_dont_email_post_to_subs=true` and all social-publicize suppression via an authorized WordPress channel **before** first publish. Current page edit tool's registered-meta schema does not expose that key; do not assume a global default suffices.
5. Coordinate any promoted video concept with Grok **after** public release, without publishing to social accounts here.

**Decision:** KEEP DRAFT. Do not add to live Library index or expose unpublished sibling destinations. No third-party asset uploads or paid requests. Cross-links from the draft point to existing published FV Archive Trail, Apollo 1 Evidence Atlas, Research Sources and Editorial Standards only.

**Optional Grok promotion (not sent):** A 45–60-second documentary explainer: “The meeting in the memoir—and the note that could not find its minutes.” Must distinguish contemporaneous files, later memoir and editorial annotation on screen, with source-card lower thirds and no staged archival image.
