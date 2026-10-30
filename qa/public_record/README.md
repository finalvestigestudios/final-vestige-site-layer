# Public Record — published preview and indexing QA

This is an **isolated, read-only** editorial/indexability gate. It does not call WordPress, fetch web pages, write to GitHub at runtime, alter search settings, or deploy anything. Its fixture contains only public paths and status/metadata fields read through authenticated WordPress; no article bodies or privileged data.

## New source-verified finding (2026-10-30)

- The **published, indexable** `/accountability/` landing (WordPress ID **1304**, `jetpack_seo_noindex=false`) has **blank saved** `jetpack_seo_html_title` and `advanced_seo_description`. This is a CMS metadata-completeness review, **not evidence of empty rendered HTML metadata or a bad Google search snippet**; templates may supply defaults.
- That same published hub includes direct links to **four published pages expressly marked “Research Draft”**, each `jetpack_seo_noindex=true`: **1312** (Gabriel Fernandez), **1313** (Watergate), **1314** (Iraq WMD), **1315** (Maximus). The hub itself **labels these links as research previews**, which is good disclosure. The previews use cited sources and are not proven inaccurate. This is a release/editorial sign-off question, not a proven defect. **Noindex does not restrict direct visitor access.**
- The linked **Andrew Do** page **1316** is published, explicitly labeled established criminal accountability, and `noindex=false`; the checker correctly avoids treating it as a Research Draft.

## Run offline

```sh
node --test qa/public_record/test_public_preview_gate.cjs
node qa/public_record/public_preview_gate.cjs qa/public_record/sanitized_live_snapshot.json
```

The sanitizer fixture stores only five route/status/label records and anchor excerpts, not full page content. Its `observed_utc` is a collection-time approximation; page status and noindex values came from authenticated WordPress `pages.get?context=edit`. Refresh before future release decisions.

Interpretation: `REVIEW_PUBLIC_RESEARCH_PREVIEW` is **not a test failure**—an explicitly labeled, noindexed, published preview might be intentional. `HIGH_INDEXABLE_RESEARCH_DRAFT` flags an indexing-state regression; `HIGH_LINKED_UNPUBLISHED` flags a hub link to a nonpublished document; `REVIEW_INDEXABLE_HUB_METADATA` is a metadata-completeness reminder, not proof of an empty public meta tag. JSON always sets `production_browser_verified=false`. CLI exits 2 for `high` issues, 0 for review-only, 1 on malformed input.

## Claude and founder review gate

1. Decide whether the four short research previews should remain **publicly accessible, expressly labeled and noindexed**, or whether unfinished sensitive dossiers should be moved to draft **after** inspecting current traffic, source accuracy, routes, editorial sign-off and safe replacement links. Do not change status or noindex settings merely because this checker reports a review item.
2. If public previews remain intentional, keep the explicit hub labels, preserve their noindex until full editorial approval, review sources/factual nuance, and run logged-out/mobile verification.
3. Review the indexable Public Record hub's saved SEO title/description and rendered page HTML before touching metadata. Suggested title: **The Public Record | Investigations & Accountability | Final Vestige**. Suggested description: **Follow public decisions, audits, and official findings through the evidence, corrections, and promised changes that came afterward.** Any actual WordPress change requires explicit user approval and fresh revision checks.
4. Preserve the working Focus signup, retired-water drafts, editorial URLs, Claude's active WordPress design work, and QD/Decision Queue constraints. No production edits, merges, plugins, navigation updates or settings changes are part of this PR.

## Verification

The **12 native Node 22 tests passed**, both source files passed `node --check`; the exact GitHub blob SHA-1s were checked against locally tested bytes: guard `5a5b8c5db23cd790f607c528bf4d0bddea56426b`, tests `a0d58dcde94a430b050b867ba9e64e40fcf965fe`, fixture `fd1fb4ea56464fbf64775e1a89210636c72547f1`. The sanitized live snapshot yielded **five review findings**, **zero high findings**: four labeled/public research previews plus missing saved custom metadata on the hub.

No actual public HTTP, search index, native mobile DOM, screenshot, or legal/editorial completeness verification was performed. The initial exploratory page-source read is not enough to assert a visitor-visible defect.
