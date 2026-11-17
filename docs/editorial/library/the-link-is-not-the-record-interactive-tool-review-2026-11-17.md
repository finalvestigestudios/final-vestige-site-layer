# The Link Is Not the Record — interactive reader receipt (offline release candidate)

**Owner:** Final Vestige Studios / LIBRARY only  
**Researched and tested:** 2026-11-17, Pacific  
**Status:** usable standalone HTML in Library Studio run; **HOLD public WordPress release**  
**Related:** [source worksheet](./source-directory-evidence-receipt-2026-11-16.md), [90-source directory release gate](./research-sources-90-release-gate-2026-11-16.md), [issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788), [draft PR #2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816)

## Actual new reader deliverable

A self-contained, original `the-link-is-not-the-record.html` tool has been authored as the **interactive companion** to the existing static Markdown worksheet, not as a duplicate public page. It is supplied as an HTML download and a QA ZIP in the Library Studio run. **The HTML source is not committed to this branch**; do not mistake this design/QA receipt for a deployed file or invent a live URL.

The offline tool has 17 labeled fields: record custodian, collection/series, item title, identifier, item/version date, landing URL, specific-item URL, access check date/time zone, retrieval state, direct observation, narrowly supported claim, what is not established, item-level rights status/source, credit line and next verification action. It supplies accessible and distinct retrieval states (item opened, landing only, application shell, description only, restricted request, timeout, etc.), displays `Not recorded` for blank fields, updates an editable Markdown receipt, and permits user-initiated copying, download and print. No trackers, fonts, cookies, form submissions, storage, payments or network requests. Readers should not enter private/sensitive identifiers.

**Original visual:** four-stage SVG (discover / inspect / qualify / rights), marked explicitly as a conceptual diagram, with title, text alternative and caption. All text and visual are original FV materials, free for personal research; redistribution/commercial reuse is not granted by the tool. No third-party archival photograph or scan reproduced.

## Primary-source ledger; last inspected 2026-11-17

- [National Archives electronic-record access FAQs](https://www.archives.gov/research/electronic-records/access-in-catalog-faqs): archival description, downloadable data and associated technical documentation must be distinguished; its quantitative estimate is scoped to particular electronic record series, not the whole archive.
- [NARA textual-archives request guidance](https://www.archives.gov/research/order/textual-records-dc.html): record group, series, box, folder and document identifiers help locate off-line material; not a guaranteed fulfillment route.
- [Library of Congress PH Filing Series rights/access](https://www.loc.gov/collections/ph-filing-series-photographs/about-this-collection/rights-and-access/): the library generally does not grant rights it does not hold; researchers investigate specific third-party restrictions.
- [Smithsonian Open Access FAQ](https://www.si.edu/openaccess/faq): CC0 is attached to designated items only, and noncopyright restrictions may remain.
- [FV Editorial Standards](https://finalvestige.com/editorial-standards/): separate evidence from interpretation, preserve disagreement, verify captions and rights.
- [FV Research Sources](https://finalvestige.com/free-resources/research-sources/): original directory, pending 90-card labeling correction (not yet live).

## Actual local QA

Ran Chromium against the **delivered HTML** via `page.set_content` because local `file://` navigation was blocked in this environment, with 320, 390, 768 and 1440-pixel viewports. Result: four responsive configurations passed: no top-level overflow or JS exceptions; live Markdown preview; 17 explicit form labels; focusable output; original SVG title; record-ID and access-status accuracy; browser-generated Markdown download with expected content. A malicious-looking image tag submitted as text did not become a DOM element. The screenshots were independently inspected and are local-tool renders, **not** public WordPress or screen-reader acceptance tests.

HTML SHA-256: `eea21c5ce2b1fcfc860dc5184667b5b8e18e2f78465146ea6923b44e01256953` (2026-11-17 delivery).

## Release blockers, no shortcuts

1. The existing public #1338 correction still needs genuine production-theme screenshots, search/filter/keyboard and assistive-technology QA at 320/390/768/1440. Offline HTML and WordPress screenshot URLs without inspectable pixels do not pass.
2. For the *new* standalone tool, verify a serving strategy that does not strip its JavaScript from WordPress; do not assume Gutenberg HTML embeds scripts safely. Review real rendered/keyboard/mobile behavior again on the served URL.
3. Pages connector does not expose the `_jetpack_dont_email_post_to_subs` switch; do not confuse the site's default newsletter option with enforceable first-publish email/social suppression. Confirm notification behavior for the actual publish path before posting.
4. If released, add one **Library-only** card/internal link; preserve all original directory cards, page paths, SEO, and unrelated editorial lanes. No paid magnet, spending, Grok account action or notifications.

**WordPress status this run:** #1338 and Library #77 remain published at their prior revisions; staging #2354 remains draft/noindex. The standalone tool is delivered privately as a downloadable artifact, *not published on finalvestige.com*.