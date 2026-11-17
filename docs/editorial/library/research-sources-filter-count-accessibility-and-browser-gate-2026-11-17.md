# Research Sources — accessible filter counts and real-browser release gate
**2026-11-17 Pacific · Library-only · STAGING MODIFIED / PUBLIC HOLD**

## Problem and staged fix
The real Research Sources directory has **90 distinct original source URLs**, organized as 60 cards in its primary Gutenberg HTML block and 30 in a separate fallback block. Staging #2354 already corrects static "60" text, category totals, search behavior and no-JS guidance. An independent CSS block still contained `.fv-rs-filters button span{display:none}`, which removed category numbers from **both the visual interface and the accessibility tree**.

At 02:43:03 site-local, the Library Studio used **WordPress single-section revision/content/block-hash guards** to replace only staging **block index 1**, from `display:none` to a standard visually-hidden treatment (absolute 1px box, clipped and inset). The intended effect is to keep numeric totals in accessible filter-button names without changing layout. WordPress saved with **zero warnings**.

**Independent authenticated readback**: #2354 remains `draft`, Library parent #77, `jetpack_seo_noindex=true`, modified `2026-11-17T02:43:03`. 90 cards, 90 unique URLs, exact categories **12/24/21/25/8**, 1 search controller, group semantics and no-script instruction all preserved.

**Published WordPress unchanged**: #1338 remains `publish`, modified `2026-11-03T22:12:43`, containing the original 90 sources but static 60-labels, hidden category totals and double controller; parent #77 remains published, modified `2026-11-07T19:39:01`. **Do not publish staging as a substitute for updating these existing pages.**

## Reusable browser gate produced
A new read-only **Python/Playwright browser-acceptance test** was built, packaged and attached in this Library Studio run: `qa_research_sources_live.py`, with original explanatory figure, dated rights/provenance report, strict JSON evidence and example screenshots.

Its checks cover 320/390/768/1440px × scripts on/off; uses Chromium ARIA snapshots to verify category numbers participate in button accessible names; 90 unique URLs/titles; 5 category totals; static search label; accessible group role/name and non-`display:none` filter counts; 30 fallback records without scripts; live result count, search for supplemental record **National Archives Donated Collection Explorer**, no-result and reset; focus, horizontal overflow, link security, metadata and JS errors. It does **not** submit forms, click external links, sign in, publish or spend.

**Local *fictional* fixture:** 8/8 test configurations PASS, 0 failures; 220 individual checks passed, with 12 illustrative screenshots and JSON. The fixture has invented cards, not WordPress or genuine archival images. Two negative-control variants (old CSS display:none and stale 60-search label) correctly returned nonzero failure in all 8 configurations. This is **not** production-theme, actual screen-reader or full keyboard traversal QA.

Networked reviewer command:
```sh
python qa_research_sources_live.py --url https://finalvestige.com/free-resources/research-sources/ --out ./evidence-public
```
For authenticated staging, use a private preview URL and optional **local-only** Playwright storage state; never commit cookies or preview tokens. The script redacts query strings in report URLs.

## Release blockers and obligations
1. **Still missing:** real WordPress theme screenshots at 320,390,768,1440, JavaScript on/off; actual editor-authenticated staging preview; keyboard tab order, visible focus, screen-reader group/count announcements and no overflowing content. WordPress screenshot URLs marked ready but did not provide inspectable pixels; browser navigation / container DNS restrictions remain.
2. `email_new_posts_by_default=false` was observed from Jetpack Newsletter settings, **not an enforceable guarantee** against email/social delivery for a published-page update. Verify suppression using a supported mechanism before release; do not modify global subscription settings casually.
3. Reconcile **all 15 existing editorial correction anchors** from [draft PR #2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816) with the staging accessibility repair. Refresh #1338/#77 optimistic locks; retain original 90 cards, destinations, categories, legal rights cues and slugs.
4. Only once passed, update the original published pages with minimal guarded edits, then verify authenticated readback, signed-out public URL and canonical/robots, 90 unique links, media/link health and absence of unintended sends. The cross-cutting real-browser blocker is [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589).

## Dated provenance / media rights
Checked 2026-11-17: [Library](https://finalvestige.com/free-resources/), [Research Sources](https://finalvestige.com/free-resources/research-sources/), [Editorial Standards](https://finalvestige.com/editorial-standards/), [NARA Record Group Explorer](https://www.archives.gov/findingaid/record-group-explorer) (October 2026 503,600,456 scans / estimated 12,473,570,637 textual pages), [NARA Still Picture rights](https://www.archives.gov/research/still-pictures/permissions), and [90-source source/rights inventory](research-sources-90-inventory-2026-11-16.json). The check is institution-page level, not blanket permission to reproduce archival material. **No external photograph, scan, PDF or video copied**. Original code, CSS, fictional fixture and accessible conceptual diagram only.

**Grok editorial concept (not distributed):** "Ninety records, two ways to browse — and why the missing thirty were never missing." No account access, outbound promotion, emails or spending.
