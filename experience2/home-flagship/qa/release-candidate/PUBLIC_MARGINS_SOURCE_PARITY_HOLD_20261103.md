# EX2 seven-chapter full-page parity: 72 published Margins instead of invented fixture copy — HOLD

**Scope:** isolated WordPress Playground/Assembler Gutenberg development fixture only. No production WordPress writes, no live theme/plugin changes, no public preview, no merge or release authorization.

## Actual source and scope

Read-only WordPress.com API `wpcom_mcp_pages_get`, site `256784396`, **published page ID 6**, `context=edit`, `modified=2026-11-02T17:48:13`, canonical `https://finalvestige.com/`.

The source contains exactly **72 `fv-margin-strip__item` spans**, indices **0..71**, **72 distinct published fragment strings**. Extracted *only the 72 publicly available text nodes* into `public_page6_margins_20261102.json` (no page export, subscribers, visitor data, WordPress credentials, settings, Jetpack configuration or production database). Index 0 begins with Nanni's clay complaint; index 71 discusses unredacted information in the 2025 JFK release. These texts were already public; **this import is NOT a new historical fact-check or license grant**.

Important source distinction: `context=view` encodes typographic apostrophes (e.g. `&#8217;`), while `context=edit` exposes exact stored text. We compared to the raw edit-source output, not to a re-encoded presentation string.

## Before → candidate change

**Before**: the isolated, Gutenberg-saved seven-chapter experience used all 72 **invented** `Historic fragment 0…71` records. The 390px and 1440px [real Playground screenshots](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41736939617) showed these visibly above the monument-scale archival flagship. That was useful for structural/axe testing but was not first-screen editorial parity with the live public homepage.

**After in source (NOT YET rendered in a WordPress browser):** the same 72 indexed spans are replaced with **exact published page-6 historical fragment texts**, HTML-escaped and visibly marked `72 PUBLISHED MARGINS · TEST FIXTURE`. The scroll region remains keyboard-focusable and labeled. The seven chapters, six original CSS sources, four original JS sources, NYPL capture withholding, pinned Assembler staging stylesheet and existing native navigation remediation are unchanged. The Jetpack subscriptions block and Focus wrapper in the disposable test remain **synthetic**, and the public site's rotating Margins behavior is **not** replicated. Do not treat the result as complete WordPress.com/Jetpack parity or advertise it as final art-direction approval.

## Deterministic source custody & test contracts

- Separate JSON file pins `source_site_id`, `source_page_id`, canonical `source_url`, `source_modified`, `status`, count and ordered 0..71 text records.
- Candidate builder refuses missing/extra/duplicate indices, duplicate fragment text, HTML tag/control-character payloads, changed source scope and unrecognized provenance; `html.escape(quote=False)` prevents accidental injection when published text is inserted into Gutenberg HTML.
- Manifest retains `page6_live_content_included = false` to mean **the actual complete page is not copied**. New `public_page6_margins_texts_included = true`, source modified date and SHA-256 of the fixture explicitly distinguish the *public text only* from the still-fake Jetpack/Focus wrapper.
- Two additional test methods cover source identity / first, middle and last fragments, 72 real text nodes, and nine adversarial mutations (count, index, duplicate, HTML, empty, wrong page/site/status).
- **17/17 independent connected-source/static preflight assertions passed**, including exact text comparison to current live raw page-6 content and checking the source branch's escaped insertion and test contracts. This is **NOT** an executed Python test run or a passed browser/axe result.

## Honest release gates

At the last check GitHub Actions remains broken **before any job step**, across the older parent exact head; [runner run 41758582559](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41758582559) also failed after a fresh retry, with no steps/log blob. Therefore **this branch has no successful exact-head Python or WordPress/browser CI result**. The whole-document Assembler desktop `list` axe issue is still **unresolved**; no evidence says the native header correction passed.

Next execute exact-head `python3 experience2/home-flagship/qa/release-candidate/test_source_flagship_playground_candidate.py`; then genuine isolated Gutenberg Save + 320/390/768/1440/1920 + no-JS + 200% zoom + full-document axe + keyboard/touch + real image transfer/decoding + measured Lighthouse; compare resulting screenshots to prior baseline and the **actual** published header/Margins appearance. Do not suppress axe or inject browser-only CSS. Even green Playground tests cannot qualify WordPress.com Atomic/Jetpack behavior or field CWV.

**Release: HOLD.** Await independent QD, source rights review, manual WCAG 2.2 AA and explicit founder approval. PR #49 remains frozen; no new art direction, affiliate promotion, chapter, theme override, production publication or subscription cost was added.
