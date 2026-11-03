# PR #604 go-live gate packet (2026-11-02)

**Subject (current):** PR #604 head `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`; replacement block 108,155 bytes, SHA-256 `506aa8d9d9d9c3fe7821d8e479dc8857957667f06f5f6ea5432e3f3ad0fbc7c9`, SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277`. Keep #604 frozen while these run. Any new commit voids every item below that is marked against this head.

Publishing is one hash-locked write (`RELEASE_AND_ROLLBACK.md`). It happens the moment gates 1 to 3 are genuinely closed. Gate 4 is already done.

| # | Gate | Owner | State |
|---|---|---|---|
| 1 | Fresh independent QD review of this exact head and hash | ChatGPT (founder relays) | **Open.** Prompt below. |
| 2 | Authenticated WordPress.com render and test of the exact block | Founder signs in; Claude runs it | **Done 2026-11-02 for the flagship block on private draft 1902** (exact block stored unstripped, hash `8c0dd5c3...`; render, interactions, images, skip link, widths and console checked). Limits and a lesson about double-wrapping the block are in `PR604_WPCOM_DRAFT_RENDER_EVIDENCE.md`. |
| 3 | Named-editor NASA item sign-off | A named person | **Recorded 2026-11-02: APPROVED by Bryan Rhodes, Founder** (see the sign-off below). Note: the founder is acting as the named editor; the independent reviewer may state whether that satisfies the gate. |
| 4 | Mobile LCP exception (4.58 s) | Founder | **Approved 2026-11-02** as a temporary first-release exception, not a standard. |
| 5 | Post-release PR targeting mobile LCP of 2.5 s or better, same approved visuals | Claude | Opened after go-live (it must not touch the frozen head). |

Founder design approval is granted and is not any of the above.

## Gate 1: prompt to give ChatGPT

> Re-review PR #604 in `finalvestigestudios/final-vestige-site-layer` at the exact head `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` (your previous HOLD, comment 6588886797, was for `368399842d...` and does not carry over). Package: `experience2/home-flagship/release/production-change/replacement-block-index1.html`, 108,155 bytes, SHA-256 `506aa8d9d9d9c3fe7821d8e479dc8857957667f06f5f6ea5432e3f3ad0fbc7c9`, SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277`. Diff `368399842d..bdf01b4a3e` and confirm it changes only: `chronicle.css` (`.fv-hf__skip` z-index 200 to 100001), the regenerated block and descriptor, two documentation figures, and the new `INDEPENDENT_REPRODUCTION.md` plus `evidence/reproduction/`. Read `INDEPENDENT_REPRODUCTION.md` and the update comment 6589597053, then repeat the checks in `docs/experience-2.0/QD_HANDOFF_PR604.md` on the Experience 2.0 branch (`feature/experience-2-living-archive-sprint5`). If you can run a browser, verify the skip-link fix yourself (focus "Skip to the evidence room"; it must be fully visible above the site header). Record the verdict, with `FVSL-QD-PASS: YES` only if you genuinely approve, and the exact head and SHA-256 in a PR comment. Do not infer results you cannot run.

The founder has approved the mobile LCP exception as a temporary first-release exception; the reviewer should still state whether they accept it.

## Gate 2: authenticated WordPress.com render

Needs the founder to sign in to WordPress.com in the in-app browser (the assistant does not enter credentials). Then Claude will:

1. Put the exact 108,155-byte block into private draft page 1902 and confirm `page-sections.list` shows its `block_hash` equals `8c0dd5c3adce073fd58f5001e0f90d523ffad277` (unstripped).
2. Open the draft preview in the signed-in browser and check: the Assembler header and footer, seven chapters, Franklin switch, case chooser, inquiry accordion, Observer Lab, three archival images loading, the preserved Margins strip, the Jetpack Dispatch form visible, `#dispatch` anchor, no console errors, no horizontal overflow at 320, 390, 768, 1440 and 1920, keyboard (skip link visible), reduced motion.
3. Record screenshots and measurements in the PR's `dry-run/` evidence.
4. Trash draft 1902 only after the evidence is saved.

Mechanism: the block file is served from a local `127.0.0.1` web server and inserted through the editor; if that fails, the founder can paste the file contents into a Custom HTML block in draft 1902 by hand. Either way the draft's stored `block_hash` is checked against the SHA-1 above. Limits: this render is checked with the in-app browser's own tools, not the repository's Playwright suite, because a private draft needs the signed-in session.

## Gate 3: NASA and image rights sign-off worksheet

For the named editor. Facts below were checked on 2026-11-02; this is evidence, not a legal opinion, and the editor decides.

**A. NASA photograph S67-19766 (Apollo 1 crew at Launch Complex 34, January 1967), the item that needs the named sign-off**

- NASA record `https://www.nasa.gov/image-detail/apollo-1-crew-honored/` shows "Image Credit: NASA" and describes the three astronauts near Launch Complex 34 during Apollo 1 training in January 1967. The identifier S67-19766 appears in the page's file name; it is **not** returned by NASA's Image API search by id (the file on the site is a copy from the Final Vestige media library).
- NASA Media Usage Guidelines (read 2026-10-30, `https://www.nasa.gov/nasa-brand-center/images-and-media/`): NASA content is generally not subject to copyright in the United States and may be used for educational or informational purposes with NASA acknowledged as the source and no implied endorsement. Clearances may be needed for images that include NASA logos or NASA employees when used as cover art or in promotional content. Names and likenesses of deceased astronauts may be controlled by their estates for commercial use.
- The photograph shows three deceased astronauts. In the flagship it is used editorially, credited "Credit: NASA. Shown for editorial and educational context; NASA does not endorse Final Vestige or any product or service.", and labelled as not evidence of the hatch or ignition. The flagship carries no earning link; the homepage's free Focus Fieldbook block is separate.
- **Editor confirms:** (a) editorial, non-promotional use is the right reading for a homepage investigation section; (b) the on-page credit and non-endorsement line are sufficient; (c) no affiliate, product or Inspire3 link will be placed beside this photograph; (d) the S67-19766 identifier question is acceptable (NASA's record page and credit are confirmed) or the editor wants the identifier removed from visible copy.

**B. Wikimedia Commons File:Franklinexpeditionnote.jpg** (re-read today): license "Public domain" (`pd`), not copyrighted, attribution not required; SHA-1 `584cf387d7dcf3e259058ec14db2f4c7d04bac00` matches the register; a scan of an 1869 printed reproduction. The page makes no claim of a museum image licence.

**C. NYPL Digital Collections image 5003296** (re-read today in a browser): "The New York Public Library believes that this item is in the public domain under the laws of the United States, but did not make a determination as to its copyright status under the copyright laws of other countries." Credit is not required; NYPL suggests "From The New York Public Library" with a link back, which the page carries.

**D. Media-library records** (read 2026-11-02): record 1258 (NYPL map) already has a caption and description with the credit. Records **473** (NASA photo) and **474** (Franklin note) have **empty captions and credit fields**. Proposed text, to be applied with the release if the editor approves (these are production media edits and are not made without that approval):
- 473 caption: "Apollo 1 astronauts Gus Grissom, Ed White and Roger Chaffee near Launch Complex 34, January 1967. Credit: NASA (image S67-19766). Editorial use; not an endorsement by NASA."
- 474 caption: "The Victory Point note from the Franklin expedition (1847, with the 1848 addition), shown from the Wikimedia Commons file marked public domain, a scan of an 1869 printed reproduction. The museum object is held by the Royal Museums Greenwich (HSR/C/9/1)."

**Sign-off recorded 2026-11-02** (as stated in chat by the founder; recorded verbatim, not inferred):

- **Name and role:** Bryan Rhodes, Founder
- **Decision:** APPROVED
- **(a)** Editorial, non-promotional use is the right reading for the homepage investigation section: **yes**
- **(b)** The on-page credit and non-endorsement line are sufficient: **yes**
- **(c)** No affiliate, product or Inspire3 link will sit beside the photograph: **yes** ("no product will sit by the photo")
- **(d)** The S67-19766 identifier question is acceptable (NASA record page and credit confirmed; NASA's image search does not return the id): **yes**; the identifier stays and the block is unchanged
- **Item 4, media-library captions:** the proposed captions for records 473 and 474 **may be applied with the release**: **yes**. They are not applied yet; they are applied as part of the release step so that one coordinated change has one rollback.

Scope: this is the named-editor sign-off for gate 3 only. It is not independent QD (gate 1), does not alter the open reviewer question about a founder acting as editor, and applies to the images and credits as they appear in head `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`. Any later change to the images, credits or surrounding copy needs it confirmed again.

## After the gates: publish and verify

Re-read `page-sections.list` immediately before the write and refuse if `modified` is not `2026-10-30T09:14:14` or `content_hash` is not `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`. Apply operation 1 (and optional operation 2) from `PROPOSED_PRODUCTION_CHANGE.json`. Then verify on the live site: six top-level blocks, untouched hashes for blocks 0, 3, 4, 5; 72 Margins items; the Jetpack form; Focus links; one `main`; the skip link visible when focused; seven-width screenshots from the live URL; no critical console errors; links and the Focus Fieldbook path. Do not submit the subscription form with a real address. Roll back exactly as `RELEASE_AND_ROLLBACK.md` says on any regression. A merged PR or a successful API response is not completion; the visible live page is.

## Post-release performance PR (gate 5)

Target: mobile LCP of 2.5 s or better in the strict lab mode (today 4.58 s) without changing the approved visual design, plus field data once available. First step: identify the actual LCP element and its load chain; the earlier session found that fonts, preloads, CSS and `will-change` did not move the model-based number, while `content-visibility` on preserved sections cut blocking time. Opened as its own PR on top of the released head after go-live.
