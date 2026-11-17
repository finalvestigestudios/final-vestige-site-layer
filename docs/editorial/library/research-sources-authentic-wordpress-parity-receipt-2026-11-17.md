# The ninety-source parity receipt
**Final Vestige Studios · Library Resource Studio · 2026-11-17, 03:35–04:00 Pacific**

**Release state:** AUTHENTIC WORDPRESS SOURCE QA PASS — **PUBLICATION HOLD**. Scope is only Research Sources #1338, unpublished staging #2354, and the existing Library landing #77. No production write, merge, email or public deployment.

## The reader problem
The published source directory contains ninety actual citations, but its visible static labels still call it a sixty-source directory. Readers should not have to guess whether a record exists merely because the search interface and underlying HTML disagree. A pending staging repair fixes those claims, accessibility semantics and controller duplication. Before copying that staging into a live page, we need proof that the original catalogue itself will survive unchanged.

## Authentic WordPress evidence (independent authenticated read, not a fixture)
- **Published #1338**: `publish`, slug `research-sources`, modified `2026-11-03T22:12:43`; edit-context Gutenberg raw length **56,078** characters.
- **Staging #2354**: `draft`, `jetpack_seo_noindex=true`, modified `2026-11-17T02:43:03`; edit-context Gutenberg raw length **55,715** characters.
- **Library parent #77**: published; last known modified `2026-11-07T19:39:01`; its static source-count descriptions are still stale. It was not edited.
- **Both source versions**: precisely **90** cards in the same order, **90** distinct titles and HTTPS destinations, **60** cards in the first `core/html` block and **30** in the supplemental block; categories `12/24/21/25/8`. Both have three top-level `wp:html` blocks.
- **89/90 card bodies byte-for-byte identical** between public and staging; the sole changed card is #89, **National Archives Record Group Explorer**, retaining its exact title, URL, source-institution / rights cue, category and link security attributes. Its description no longer freezes the June 2026 digitization percentage and now accurately explains the estimated nature of NARA's monthly scan-coverage figures. No historical document scan or photograph was copied.
- **Primary directory stylesheet byte-identical**. Staged supplemental styling switches a `display:none` category-count suppression to a 1px clipped, visually hidden accessible label. Staging has one search listener (public has two); explicit named filter group and `<noscript>` guidance; correct 90 static labels and JavaScript category count map.

## Exact change groups, against authentic Gutenberg markup
A line-oriented longest-common-subsequence comparison identified **five logical hunks**, not a wholesale replacement:
1. Intro `Sixty` and summary `60` → `Ninety` and `90`.
2. Static search, filtering, initial total and filter-group semantics repaired.
3. Redundant first controller removed; separate numeric-span stylesheet updated for accessible naming; scriptless fallback instruction added.
4. The single NARA Record Group Explorer description corrected without modifying title, link or existing rights metadata.
5. The supplementary script's category totals corrected from accountability **23 → 24** and archives **26 → 25**.

The original library landing page has **two separate text replacements** in the 15-anchor editorial proposal; these have **not** been applied. The above report audits the staging source itself, not the complete two-page live publish procedure.

## New reusable guard
[check-research-sources-draft-parity.mjs](../../../scripts/editorial/check-research-sources-draft-parity.mjs) is a **read-only Node tool** consuming two raw Gutenberg exports. Its output distinguishes `PASS_SOURCE_PARITY_ONLY` from actual browser approval. It fails on unexpected card, URL, ordering, date-caption, CSS, script-controller, category, no-JS guidance or accessible-label changes.

**Execution against actual authenticated WordPress raw content:** `PASS_SOURCE_PARITY_ONLY` with **zero parity errors**. Four deliberate negative controls, run against modified copies *in memory*, each correctly returned `FAIL`: (1) duplicate destination, (2) 60-source search regression, (3) newly hidden category count, and (4) unexpected card-description change. The tests did not write back to WordPress.

CLI (with two manually exported `content.raw` files, excluding passwords/cookies):
```sh
node scripts/editorial/check-research-sources-draft-parity.mjs public-1338.raw.txt staging-2354.raw.txt
```
Never commit site authentication tokens or editor preview parameters with exports. Source exports may include nonpublic editorial details and should be handled as internal QA material, not uploaded to the public repository.

## Evidence, provenance and rights — last checked 2026-11-17
- [Live Library](https://finalvestige.com/free-resources/): current public catalogue, resource sections and cross-links, viewed as an anonymous reader.
- [Research Sources](https://finalvestige.com/free-resources/research-sources/): anonymous landing page and authenticated #1338 raw source, separately checked.
- [Editorial Standards](https://finalvestige.com/editorial-standards/): published sourcing, dispute, reconstruction and image-rights policy.
- [Draft PR #2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816) and [issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788): active, overlapping Library correction; do not spawn a new duplicate.
- [NARA Record Group Explorer](https://www.archives.gov/findingaid/record-group-explorer): scan coverage against estimated pages is not a measure of record survival or individual access. Use evergreen wording.
- [Prior 90/90 source-and-rights audit](research-sources-90-of-90-link-audit-2026-11-16.md): dated per-destination attempt and rights/access qualifications. Its findings are *not* upgraded to current live download/rights validation by this source-diff audit.

**Media and use rights:** This run consists of original FV audit code, QA prose and comparisons of FV's own directory markup. No institutional photograph, third-party scan, licensed artwork, video or map was reproduced. Existing link-only rights notes are preserved byte-for-byte for 89 entries and unchanged for the NARA card except the explanatory caption.

## Release blockers: remain HOLD
1. **Genuine production theme** screenshot pixels and interactive keyboard checks at 320, 390, 768 and 1440; JavaScript on/off; filter behavior, focus styles, overflow, live announcements, keyboard order and NVDA/VoiceOver announcements. WordPress screenshot service returns `ready` URLs, but their pixels cannot be inspected from this container; container DNS cannot resolve the site. A synthetic/HTML-only pass is not a production pass.
2. **Enforceable subscriber and social notification suppression** for the exact published-page update. Newsletter currently enables subscriptions but `email_new_posts_by_default=false` (checked today); this is not proof of per-edit or social syndication suppression. The requested `_jetpack_dont_email_post_to_subs=true` field is not exposed by the available page connector. Do not alter global newsletter settings to work around this.
3. Reconcile current stage plus existing **15-anchor count and NARA plan** against *fresh* edit-context revisions for #1338 and #77; perform guarded, minimally scoped updates only after gates pass.
4. Independently read back published #1338 and #77, signed-out HTTP status, canonical/indexability, 90 unique links, category totals, alt/empty links and representative institutional destinations; verify no unintended send or publication side effect.

**Optional Grok educational handoff** (do not distribute): “Ninety sources, two layers: how thirty archival records stayed present while their directory labels said sixty.” Do not modify Grok's accounts or another editorial lane.

**Decision:** Keep original published Research Sources and Library landing intact; draft PR #2816 remains unmerged. No new spend, subscriber dispatch, social syndication, Preparedness, Investigations or homepage engineering edit.
