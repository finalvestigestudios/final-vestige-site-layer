# Research Sources — Source Census Desk and Primary-Link Integrity (2026-11-10)

**Owner:** Final Vestige LIBRARY Resource Studio. **Status:** research utility built locally; NO live release. Scope only Research Sources #1338 and internal staging #2354; no Preparedness, Investigations, homepage, navigation, subscribers, or social changes.

## Why this exists

A source-card body may include one or more **supporting** links embedded in descriptive prose, as well as a distinct **primary destination** link. A naive card parser that treats the first href as the primary destination incorrectly reduces staging from 90 to 89 distinct destinations. In the *President’s Daily Brief — Kennedy and Johnson* card, the supporting CIA FOIA Reading Room link appears in the description, while the primary direct-child anchor points to the CIA's specific 2015 publication/booklet page. A separate CIA Reading Room card legitimately uses the FOIA portal as its primary destination. This is **not** a duplicate primary destination.

**Correct invariant:** exactly one direct-child primary anchor per `article.fv-rs-card`. Inline anchors in `<p>` are supporting evidence routes, **not** primary card identities. Preserve both and their source context.

## Authenticated WordPress structural evidence (read-only, checked November 10, 2026 Pacific)

| Metric | Public #1338 | Draft #2354 |
|---|---:|---:|
| Status | publish (modified Nov 3, 22:12:43) | draft/noindex (modified Nov 10, 12:36:48) |
| Cards | 90 | 90 |
| Unique titles | 90 | 90 |
| Unique **primary** URLs | 90 | 90 |
| Category counts | 12 / 24 / 21 / 25 / 8 | 12 / 24 / 21 / 25 / 8 |
| Cards with supporting description anchors | 0 | 12 |
| Supporting description anchors | 0 | 15 |

Staging differs in **47 source-card HTML bodies** and **five primary destinations** (NRC ADAMS, govinfo Congressional Hearings, NRC Three Mile Island digest, NTSB CAROL and National Archives Donated Collection Explorer). No cards/titles added or removed. Public #1338 retains stale static sixty-source labels and 60+30 architecture. These are *HTML/readback* facts, not evidence that all outbound source URLs are available to ordinary visitors.

### New free local utility

**Source Census Desk** is a standalone, client-only HTML inspector; it accepts file input or pasted Gutenberg HTML and displays source counts, unique **primary** destinations, nested supporting link counts, category expected-vs-actual values, structural problems and a comparison/retargeting ledger. JSON audit export, print view and labeled scrollable tables included. Local files are processed by `DOMParser` and serialized as text, never inserted as executable content or uploaded. It does **not** crawl source websites, download scans, call paid services or auto-publish.

Original assets in this conversation's release package (not uploaded to WP, not served as live links): `Source_Census_Desk.html`, `Source_Census_Field_Card.pdf` (two pages, blank paper audit ledger), `Source_Provenance_Rights.csv`, `WordPress_Readback_2026-11-10.json`, Chromium screenshots/QA, test scripts and release ZIP. Illustrations/worksheet/copy are original FV 2026 material; no archival scans, copyrighted reports, third-party pictures, trademarks or government seals reproduced.

## Independent QA of STANDALONE utility

- Chromium in-memory rendered at **320, 390, 768, 1440**: no page-wide horizontal overflow or JS exceptions.
- Functional tests PASS: supporting-link not miscounted as primary, real duplicate primary URL flagged, invalid scheme rejected, HTML-shaped input inert, native JSON audit download, reset.
- Full **fictional 90-card** test fixture: 90 cards, 90 unique primary links, category distribution 12/24/21/25/8 and 12 supporting anchors — PASS. Fictional URLs (`example.org`) are test data, NOT research records.
- PDF exactly two pages; both rendered and visually inspected, 7 clickable references.
- This is NOT a WordPress-theme preview PASS, not a production visitor-browser PASS, and not a source-rights / external link accessibility certification.

## Source and rights ledger (last checked November 10, 2026)

1. Public Research Sources page: https://finalvestige.com/free-resources/research-sources/ (web.open returned 429 this run; authenticated WP edit-context readback available, no broken-link conclusion).
2. CIA 2015 PDB publication: https://www.cia.gov/resources/publications/presidents-daily-brief-delivering-intelligence-to-kennedy-and-johnson/ (official institution source; article/booklet not equivalent to the underlying briefs).
3. CIA FOIA Reading Room: https://www.cia.gov/readingroom/ (official source portal, linked only).
4. FV Editorial Standards: https://finalvestige.com/editorial-standards/ (retrieved).
5. Coordination issue #1788: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788
6. Shared actual-theme QA gate #1589: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589

No institutional image/text was copied; linked records have item-specific access and reuse conditions.

## Release HOLD

Do not publish staging #2354 or overwrite existing #1338 based on standalone tests. Require inspectable **actual production WordPress-theme** screenshots at 320/390/768/1440; ordinary guest-browser link/category/search/keyboard checks; comparison of fresh content hash before scoped edits; safe explicit first-publication `_jetpack_dont_email_post_to_subs=true` and Jetpack Social suppression for any new page; postpublish independent public readback and metadata/link health. This tool addresses a verification blind spot, not the shared release blocker.

**Grok concept (not launched):** “Ninety sources. Eighty-nine links? The archive wasn't wrong—the counting method was.” Use the original illustrative diagram; no claim of source access, no account changes until a live public destination is verified.
