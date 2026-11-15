# Research Sources — guarded count-only repair (HOLD)

**Owner:** Final Vestige Library editorial. **Checked:** 2026-11-13 Pacific.
**Canonical public URL:** https://finalvestige.com/free-resources/research-sources/
**Published WordPress page:** #1338, parent Library #77, status publish.
**Release issue:** https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788
**Shared visual-QA blocker:** https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589

## The correction and why it is needed

Authenticated WordPress EDIT-context readback on November 13, 2026 confirmed published #1338 still has **90 source cards** but initial visible HTML presents **60**. The actual source counts by \`data-cat\` are:

| Research family | Actual cards | Current initial label |
| --- | ---: | ---: |
| Declassified & decisions | 12 | 9 |
| Accountability & public records | 24 | 18 |
| Engineering, disaster & safety | 21 | 16 |
| Archives, maps & research | 25 | 12 |
| Navigation & preservation | 8 | 5 |
| **Total** | **90** | **60** |

The page's appended JavaScript total map incorrectly says 23 accountability and 26 archives, even though the cards are 24 and 25. Google/search crawlers and no-JavaScript readers receive contradictory initial text. The Library parent #77 also advertises 60; correcting that parent is a **separate, narrowly scoped edit** after #1338 is cleared.

**Observed readback:** published #1338 modified \`2026-11-03T22:12:43\` (site-local); authenticated page-sections content hash \`19a43f2e15f1cba1adc12bd0243d1278d0f248df\`; nine serialized Gutenberg block openers in raw source; five top-level blocks; 90 cards with 90 unique names and destinations; two script tags. All 11 obsolete count strings in the fix each occurred exactly once at recheck. These observations are a snapshot, not permission to write if the page has subsequently changed.

## Do not replace the public page with staging draft #2354

Staging #2354 remains draft/noindex and is a substantive rewrite, not a count correction. On November 13 it had 90 cards and 90 distinct **primary** CTA destinations; twelve cards also contained supporting inline reference hyperlinks. A naïve first-\`href\` parser can falsely report 89 destinations and 14 link differences. Counting each card's intended primary source CTA shows **five** destination changes versus the public page; the cards also have substantial copy changes and altered script/HTML-block arrangement. Some may eventually merit publication, but none are authorized merely to fix the count. **The primary-link clarification supersedes the earlier 89-duplicate shorthand in the Nov 12 audit; do not propagate that claim without distinguishing supporting from primary anchors.**

The count-only candidate must start from a *fresh #1338 edit-context export*, not the staging draft. The Python guard makes exactly **11 text replacements** and rejects any unexpected card count, duplicate destination, category drift, incorrect baseline string, nested link or non-HTTPS source. It preserves every existing card's exact markup, source URLs, scripts/styles (except the one numeric totals constant), and Gutenberg block boundaries.

## Steps for a safe future release

1. Obtain a fresh authenticated EDIT-context export of the **published** page #1338 raw Gutenberg content. Confirm modified date, status, page ID, section content hash and comparison to the snapshot above. Stop if there is any concurrent edit.
2. Run \`python docs/editorial/library/tools/test_research_sources_90_count_guard.py\` (fully fictional fixture, no network).
3. Run \`python docs/editorial/library/tools/research_sources_90_count_guard.py published-1338.raw.html\` to see the source and candidate SHA-256 without writing.
4. Run the same command with \`--write --out 1338-count-candidate.html\`. Inspect the actual diff: eleven exact string changes only. The utility never contacts or publishes to WordPress.
5. An authorized browser/editor must pass production-theme QA at **320, 390, 768, 1440px**, JS on/off, with inspectable pixels; test filters (all five counts), search finding a card from the supplemental last thirty, keyboard navigation, focus, no horizontal page overflow, actual source CTA behavior and visible rights note. An mshots link with no accessible image does **not** satisfy this gate.
6. Confirm newsletter/social publication behavior *for the actual installation* before a live write. This is an **update to an existing WordPress page**, not a first-time post, but no site-specific hook may be presumed absent. Avoid sharing changes automatically; no subscriber blast, paid tools, or new spending.
7. Apply **only** the two affected Gutenberg HTML sections (with section-hash guards if possible), never the whole staging page. Immediately read back #1338 in EDIT context and compare all 90 source cards byte-for-byte to the pre-edit baseline.
8. From an ordinary visitor's browser verify the canonical URL, correct static and dynamic counts, navigation from Library parent, right-click/new-tab anchors, mobile/desktop appearance and metadata. Only after this, update the separate Library landing-card claim of 60 to 90 with its own hash/readback/visual QA. Log the result and close #1788.

## Rights and source trail

- **Final Vestige Library:** https://finalvestige.com/free-resources/ — public landing, checked Nov 13 2026.
- **Research Sources:** https://finalvestige.com/free-resources/research-sources/ — published directory, checked Nov 13 2026.
- **Editorial Standards:** https://finalvestige.com/editorial-standards/ — sources, rights and evidence policy, checked Nov 13 2026.
- **Original institutional collections:** linked *out* from the existing 90 source cards. Their open availability is **not** a license to reprint individual scans, images, or contributed material; no image/file was copied for this patch.
- **Verification limits:** public HTML opened successfully; authenticated WordPress readback succeeded; the WordPress screenshot provider supplied public URLs but not inspectable image pixels; container browser navigation failed due to DNS restrictions. Thus *production visual/interactive QA remains blocked.* The present source URL inventory is not a fresh per-link browser health or item-level reuse-rights audit.

**Publication decision on Nov 13:** HOLD. No WordPress edits, public changes, emails, social distribution, or new expenditure are authorized by this engineering artifact. Related Preparedness, Investigations and shared site templates are out of scope.
