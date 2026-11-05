# Final Vestige — Public Preparedness Gateway

**Current public location:** https://finalvestige.com/preparedness/  
**WordPress page:** 1868, one `core/html` Gutenberg block  
**Production state:** Published. Current source snapshot: `gateway-wordpress-1868.block.html`

## Scope and historical-safety distinction

This is a **public editorial landing page**. It contains 18 evidence-linked historical/technical explanations about food preservation, cold storage, heating, lighting and early electricity, and six cards pointing to current agency guidance from FEMA, CDC, NCHFP, USDA and California CDPH.

These explanations are **not recipes, medical guidance, wiring diagrams, fire-building instructions or endorsements of improvised household systems.** The page explicitly describes the difference between historic practice and contemporary safety standards.

The 35-article Preparedness release candidate in **PR #584** and later source/citation custody work remain under their existing publication holds. Publishing the gateway **does not change any manuscript's safety, source, custody or independent QD approval status**.

## Implementation

- The full Gutenberg source is stored as a single `core/html` block; CSS selectors are namespaced under `.pa.pa-landing`.
- Each of 24 curated entries has an explicit `data-section`, `data-track` and searchable `data-text` payload. The filter hides nonmatching cards and their empty groups, and restores them when filters clear.
- The public page includes one H1, five curated topical sections and the existing emergency caveat and editorial standards.
- The heading **“Old knowledge. Modern safeguards.”** and the supporting introduction replace the earlier unbalanced “Two tracks, kept apart on purpose” treatment.
- Historical methods are source-linked and never presented as validated modern procedures.
- External links open agency/museum sources; **no unreviewed draft-article URLs are present**.
- No new plugins, scripts from external hosts, tracking, personal data collection or newsletter changes were made.
- Keep the main site's existing Preparedness navigation entry at `/preparedness/`.

## Publication and rollback

The live block was edited using WordPress `page-sections.replace` with current `expected_modified`, `expected_content_hash`, `expected_block_hash`, and explicit founder publication authorization. **Never replace it without retrieving those fresh locks.**

To roll back, restore the preceding page-1868 WordPress revision (or this file's preceding Git commit) through the same guarded section replacement mechanism. Do not overwrite unrelated navigation/header content.

## Outstanding release checks

WordPress `context=view` readback verifies 24 cards (18 Lost Ways, 6 modern), unique HTML IDs, one H1, no references to unpublished guides, and saved/rendered inline-script identity with no `&#038;&#038;` corruption. These are **not** a substitute for signed-out Chromium/Safari screenshots, live filter interaction, NVDA/VoiceOver or real mobile device QA.

**The complete instructional Preparedness Archive remains HOLD pending the qualified safety and evidence review recorded in issue #136.**
