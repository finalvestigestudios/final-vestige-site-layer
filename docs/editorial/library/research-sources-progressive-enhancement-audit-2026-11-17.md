# The ninety-source page under a dead script: structural QA and release test

**Final Vestige Studios · Library integrity · 2026-11-17 (America/Los_Angeles)**  
**State:** STATIC REVIEW COMPLETE / PUBLICATION HOLD  
**Reviewed:** [published Research Sources #1338](https://finalvestige.com/free-resources/research-sources/), [WordPress staging #2354](https://finalvestige.com/wp-admin/post.php?post=2354&action=edit), [Library #77](https://finalvestige.com/free-resources/), [Editorial Standards](https://finalvestige.com/editorial-standards/), [GitHub coordination #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) and [draft PR #2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816).

## What was actually tested

Read authenticated **raw Gutenberg content** separately from the unchanged public page (modified 2026-11-03T22:12:43 site-local) and the staged count-only correction (modified 2026-11-16T22:35:24). Parsed all source article headings, categories, outbound URLs, filter labels, script bodies and the independent fallback block. Code: [read-only audit utility](../../../scripts/editorial/check-research-sources-runtime-surface.mjs). The same pure function was executed on both real WordPress responses, not merely on a hand-written fixture.

| Structural check | Public #1338 | Draft #2354 |
|---|---:|---:|
| Cards in first content block | 60 | 60 |
| Additional cards in separate HTML fallback | 30 | 30 |
| Distinct card titles / destination URLs | 90 / 90 | 90 / 90 |
| Five actual categories | 12 / 24 / 21 / 25 / 8 | 12 / 24 / 21 / 25 / 8 |
| Static search label / first count statistic | 60 / 60 | 90 / 90 |
| Read-only structural verdict | **PASS_STATIC_STRUCTURE_ONLY** | **PASS_STATIC_STRUCTURE_ONLY** |

Both structural verdicts mean *only* that the expected inventory for each page version is intact. They are not functional search checks, layout screenshots, keyboard tests, or link-level item permission checks.

## Additional reader-facing issues found

**1. The no-JavaScript fallback is present but its controls have no explanation.** The 30 later cards are actually present as a second HTML group and remain readable when scripts do not run. The second script moves the cards into their intended five categories and removes the duplicate wrapper; it does not load records over the network. Thus it would be incorrect to assert that 30 records are missing for scriptless visitors. But search and filter buttons remain on the page even if JavaScript is disabled, and there is no `<noscript>` instruction telling readers that manual browsing of the categories is required. Mark as **accessibility/progressive-enhancement concern**, not proven inaccessible content.

**2. The search runs twice when JavaScript is enabled.** The first script registers search and click handlers against the original 60 cards; the second script registers new handlers on the same controls after it moves the 30 extras into the main index. Both react to each input/click. In source order, the second pass should ultimately process all 90; this is a code-level observation, **not proof that a specific browser result is wrong**. Search twice on each keystroke and differing totals create a future maintenance hazard. Do not remove either handler without targeted browser regression testing.

**3. The filter numerals are deliberately CSS-hidden.** The published block `<style>.fv-rs-filters button span{display:none}</style>` suppresses the category-number spans, including the corrections made in staging. The numbers remain in HTML but are not visible and are omitted from the accessibility tree while hidden. The count corrections are still needed for source integrity, but a screenshot might not show them. Keep a separate visible/announced-result-count test.

**4. The filter region's label lacks group semantics.** The controls sit in `<div class="fv-rs-filters" aria-label="Filter research sources">`, not an explicit `role="group"` or `<fieldset><legend>`. Whether the label is announced properly is unverified. A semantic wrapper improvement should be separately tested against the live theme and screen reader.

## Release test card — must be executed against the actual production theme

Use public `/free-resources/research-sources/` at **320, 390, 768 and 1440 px**, with scripts ON and OFF. Keep inspectable screenshots and console/accessibility evidence. At each width, verify no horizontal scroll or clipped buttons, readable labels, visible keyboard focus, screen-reader group announcement, and ordinary link activation. With JS ON, search exact supplemental title **“CIA Freedom of Information Act Electronic Reading Room”** and expect **one of ninety**; clear it and click all five category filters to verify **12 / 24 / 21 / 25 / 8** outcomes and a single `aria-pressed="true"` state. With JS OFF, verify all **90** links remain browsable, including the 30 in their separate fallback section; do **not** claim the search field functions, and consider an explicit scriptless explanation before public release.

After live QA, independently verify current WordPress section hashes, restore no unexpected changes, and confirm that an existing-page edit will not send emails or social syndication. `email_new_posts_by_default=false` is not an all-channel suppression guarantee. Apply the existing fifteen-anchor correction only with a revision/hash guard. Then read back WordPress, the public title/description, all cards and URLs, and sample records. If any gate is unverified, HOLD.

## Provenance, rights, and visual integrity

- Source / owner: Final Vestige Studios WordPress #1338, unpublished comparison draft #2354; direct authenticated edit-context reads on **2026-11-17**. Public viewer additionally checked on 2026-11-17. Linked primary institutional destinations remain recorded in the [90-row source ledger](research-sources-90-inventory-2026-11-16.json) with individual last-checked outcomes and use caveats.
- Internal coordination: [Library issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788); [draft PR #2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816). Review source-of-truth right before editing because WordPress/GitHub can change.
- This report and script are original editorial QA. No external photographs, scans, artwork, agency seals, videos or archival documents were embedded, duplicated or asserted to be public domain. Linking to a source does not authorize copying it; use item-specific rights and licensing for any future media.
- No paid service, subscriber email, automated social post or edits outside the Library. No WordPress content was changed by this audit. **All actual browser, screen reader and notification-suppression gates remain HOLD.**

**Grok promotional concept (handoff only):** one short explaining why an old archive can contain ninety records while a script and static labels report only sixty—and why inspecting the raw source matters. Do not publish or alter Grok's accounts from this lane.
