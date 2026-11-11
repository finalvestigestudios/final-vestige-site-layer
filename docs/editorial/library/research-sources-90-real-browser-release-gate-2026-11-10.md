# Research Sources — actual-theme release gate

**Owner:** Final Vestige Library Studio · **Prepared:** 2026-11-10 Pacific (2026-11-11 UTC) · **Status:** HOLD — no public WordPress write.

## What is actually on the site

Re-read the [public Library](https://finalvestige.com/free-resources/), [Editorial Standards](https://finalvestige.com/editorial-standards/), and authenticated WordPress editable content for the [published directory #1338](https://finalvestige.com/free-resources/research-sources/) and staging **#2354**. Published #1338 is still `publish`, modified **2026-11-03 22:12:43** local, with 90 existing source cards and misleading static initial **60** labels. Staging #2354 remains `draft/noindex`, modified **2026-11-10 12:36:48** local. It contains **90 cards, 90 unique titles, 90 unique primary direct-child destinations**, with groups **12 / 24 / 21 / 25 / 8**. It refines 47 card bodies and five primary destinations. The old 30 supplemental cards are *not missing*; the published script moves them after loading. See [controlled change register](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/main/docs/editorial/library/research-sources-90-controlled-staging-diff-2026-11-10.md).

## New substantial release-tool package (attached to Library Studio run)

**A real-network, read-only Playwright release inspector** (`verify_research_sources_live.py`), a synthetic 90-card fixture/fault generator, regression run outputs, a source/rights ledger, an operator runbook, and an original three-page illustrated **90-Source Release Gate** checklist.

The inspector runs 320 / 390 / 768 / 1440 px × JavaScript on/off. It tests the actual page for 90 cards, 90 distinct titles and **direct-child primary** links (avoids the prior CIA inline-supporting-link false duplicate), category and button counts, live-region text, supplemental-card search, no-JS access, filter functionality, focus indication, page-wide overflow, console exceptions, duplicate IDs, and new-tab protections. It saves top/filters/last-group screenshots for **human** inspection. It never writes to WordPress, never sends email/social, and never calls paid sources.

**Privacy:** When testing an unpublished preview, accept private preview URL through an environment variable, optional local browser storage-state, and write images to a private folder; neither private preview URLs nor cookies are serialized to the machine-readable report. Hard-code no publication authority: `publish_authorized=false`.

**Verified regression testing here (synthetic HTML only):** full fictional 90-card fixture **192/192 automated checks PASS** across four widths and JS/no-JS; a deliberate 89-card mutation was correctly rejected with **44 failed checks**. This proves the inspector can detect representative regressions, **NOT** that WordPress's production theme passes. All fixture names/links are fictional. PDF 3 pages rendered/visually inspected and collision corrected. ZIP CRC PASS, SHA-256 `1f9c0845224b8e247a25de13e6ab3657d002bc0d1e06e2a5917074f1d0304a96`. Deliverables live in the corresponding ChatGPT Library Studio run's local conversation attachments, **not** publicly hosted media or this repository.

## New official-publisher clarification (not an unconditional release pass)

Jetpack's [Newsletter documentation](https://jetpack.com/support/newsletter/) (updated **Nov 4 2026**) and [WordPress support](https://wordpress.com/support/newsletter/send-newsletter-emails/) (reviewed **Nov 9 2026**) explicitly say **pages and updates to previously published posts do not send standard newsletter emails**; newsletter emails are for new posts. This narrows the ordinary Jetpack newsletter risk for an in-place *page* edit and Library child pages. **It does not verify FV-specific hooks**, the explicit founder suppression key `_jetpack_dont_email_post_to_subs=true`, or **Jetpack Social** sharing. [Jetpack Social docs](https://jetpack.com/support/jetpack-social/) (updated Nov 3) distinguish automatic new-post sharing controls; inspect this site's real configuration. Do not temporarily change newsletter settings or activate social.

## Required gate before changing public #1338

1. Network-capable browser with actual current FV WordPress theme, *inspectable pixels*, screenshots for **all four widths** with JS on/off, site header/signup overlay, filters/cards/footer; keyboard and print checks. Cached mshots links **without pixels** do not pass.
2. Authenticated preview of staging #2354 (private preview URL/nonce never published) and ordinary visitor baseline of #1338. Validate 90 primary destinations, 90 heading IDs, five category groups, search works for a card originally in the supplemental thirty, live counts 90 / 12 / 24 / 21 / 25 / 8, focus and no global overflow.
3. Ordinary-browser verification of the **26 inconclusive institutional destinations**, particularly those blocked for bots or rendered as app shells. Do not classify a 403/406 from automation as a broken reader link; an official help page is not proof the underlying content works.
4. Fresh WordPress readback and optimistic revision/hash comparison; confirm Jetpack email and Social/custom hooks will not distribute. Preserve source/item rights qualifications.
5. Apply *in-place only* to existing #1338, **never publish staging #2354 as a duplicate**. Re-read WordPress, guest URL, SEO/noindex/canonical, front-end screenshots, links, JS/no-JS; then separately make a guarded **#77 Library landing** 60→90 correction.
6. Grok may be given the honest angle *“The directory advertised sixty, but ninety cards were already there.”* No media account access or promotion until the corrected public URL is fully verified.

**No public WP, subscriber, social, homepage, Preparedness, Investigations, or paid services changed.** Shared Site QA dependency remains [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). All diagrams and scripts in this run are original FV material; external publisher documents are linked only. No archival photographs, protected source scans, or court/government seals reproduced.
