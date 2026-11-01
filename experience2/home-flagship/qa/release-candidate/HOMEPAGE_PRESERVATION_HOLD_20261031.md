# Experience 2.0 — Homepage publication no-loss gate (October 31, 2026)

**DRAFT / HOLD.** Branch stacked directly on PR #395 exact head 5ce5672897d8d62ae84ca28a2834bda7a3bd05b1. Does not change frozen PR #49, WordPress production, page content, plugins, theme, navigation or settings. Apollo #158 and Mind/affiliate #171 remain separate.

## Material finding from actual live page 6

Read-only WordPress.com pages.get for published homepage ID 6 (modified 2026-10-30T09:14:14 according to site API) returned 47,021 characters of raw Gutenberg content. It contains exactly **72** historical Margins spans with unique indexes 0–71, **one original Jetpack subscriptions block** of the is-style-split variant, **two original /focus/ links** and the associated Fieldbook CTA copy, plus an existing H1 heading (Find what others miss).

The source-pinned seven-chapter fragment in PR #382 has another H1, but does NOT contain the native Jetpack block or the live 72 Margins records. **Replacing page 6 wholesale would erase both**. Simply concatenating the full old page with the new fragment creates at least **two H1 headings** before considering Assembler theme landmarks. Both are concrete release blockers.

## Source-controlled safeguard

The new verify_homepage_migration.cjs compares a reviewed WordPress Gutenberg candidate against the public page-6 raw source. It fails closed on missing or changed source SHA-256; any of 72 missing, altered, or duplicated record spans; altered/removed/duplicated Jetpack subscription block; loss of original Focus links; duplicate/missing H1, seven chapter anchors or three case panels; and leaked preview developer controls or remote executable script tags.

It emits a machine-readable receipt on success only and NEVER changes WordPress. No live content export or private visitor data is committed.

## Reproduction

With Node 22+ from an exact branch checkout:

~~~sh
node --test experience2/home-flagship/qa/release-candidate/test_homepage_preservation.cjs

node experience2/home-flagship/qa/release-candidate/verify_homepage_migration.cjs \
  --legacy /PRIVATE/public-page-6-gutenberg-raw.html \
  --candidate /PRIVATE/integrated-review-candidate.html \
  --expected-legacy-sha256 "$(sha256sum /PRIVATE/public-page-6-gutenberg-raw.html | cut -d' ' -f1)" \
  --receipt /PRIVATE/NEW-preservation-receipt.json
~~~

The full source content and receipt stay **private**; export only the public page blocks, never WP users, subscribers, settings, secrets or a production database. Independent source/digest review should use a separate extraction and the page modification timestamp, not just trust a digest computed by the same process.

## Execution evidence

**15/15 Node tests passed** using the actual PR #382 seven-chapter WordPress release fragment from the exact-source offline package alongside a controlled synthetic legacy-page fixture. Controls exercise record alteration/deletion/substitution, Jetpack mutation/duplication, Focus loss/deduplication, H1 collisions, chapter anchor and evidence inventory corruption, developer controls, remote JS, and baseline digest drift. This is not a genuine WordPress import or browser accessibility acceptance.

## Next release decision

**HOLD** pending a selective, reviewed Gutenberg migration that incorporates all 72 original record texts and the existing native Jetpack block/Fieldbook links without duplicating the old hero. Then run actual isolated WordPress/Assembler staging, seven viewport widths, keyboard/touch/no-JS, axe WCAG 2.2 AA, 200% zoom, real archival HTTP bytes and source provenance, Lighthouse lab metrics, independent QD/CI and founder release approval. WordPress.com Personal does not support a native staging clone, and standalone Playground admission will not certify hosted Atomic or Jetpack delivery. Existing Apollo/Franklin/NYPL image reproduction rights remain open; no license claim is made here. Frozen PR #49 stays untouched.
