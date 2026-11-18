# The Ninety-Source Field Desk — provenance, QA and publication decision

**Date:** 2026-11-17 America/Los_Angeles  
**Owner:** Final Vestige Studios · Library Resource Studio  
**Artifact:** [Portable field desk HTML](research-sources-portable-field-desk-2026-11-17.html)  
**Status:** `HOLD — INTERNAL REVIEW / NO PUBLIC WORDPRESS PUBLICATION`  
**Related issue / draft PR:** [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) / [#2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816)

## Reader problem and non-duplication

The live Research Sources page currently contains ninety unique institution-linked records but still presents static sixty-record labels in some contexts. There is no need to copy another forty records or create a second, competing WordPress guide. This **portable companion** is an independent **offline-browseable, source-first snapshot** of the same ninety records, built from the already-verified canonical inventory. It adds an access-evidence filter, item-level-rights cautions, a no-JavaScript mode, original source numbering and two existing FV investigation cross-links. This version is a GitHub review artifact, **not** a newly published FV URL or a live page replacement.

## Source control and rights

- Canonical source of titles, categories, original links, institution/reuse cues, access outcomes, and last-check dates: [immutable WordPress #1338 inventory snapshot](research-sources-90-inventory-2026-11-16.json). Captured 2026-11-16; original published page modified 2026-11-03T22:12:43 site-local. This new desk **does not claim destinations were rechecked on 2026-11-17**.
- Live target: https://finalvestige.com/free-resources/research-sources/ ; parent https://finalvestige.com/free-resources/ ; source policy https://finalvestige.com/editorial-standards/.
- Two meaningful FV cross-references: [Apollo 1: The Evidence Atlas](https://finalvestige.com/apollo-1-evidence-atlas/) (distinguishes documented from interpretive material) and [Puységur's Animal Magnetism Files](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) (source-trail example).
- The directory links outward to **ninety original institutional destinations**. No remote page, scan, archive image, institution logo, video, PDF or photograph was copied. The four-gate SVG schematic, CSS and client-side filtering are original to FV (2026), visibly captioned as an illustration.
- **Rights stay item-specific.** A CC0 label is valid only for a specifically marked asset; broad-reuse site terms may contain exceptions; records with living-person identifiers require privacy review. Neither original destination availability nor this portable directory establishes permission for reproducing the source materials.
- All data remain entirely within the local HTML; the search/filter script makes no network calls, cookies, persistent storage or telemetry. Clicking external institutional links requires an internet connection.

## Independent review of GitHub saved-file bytes

The saved HTML was read back using the GitHub connector **after** its cross-links were committed (blob SHA `50d8ed8a512cb7a76d2082fa4208a8d650a18572`; 149,434 UTF-8 characters). Validation was applied to the *saved file*, not just the construction buffer.

| Test | Result |
|---|---|
| Distinct original record numbers and titles / 90-item crosswalk against canonical JSON | **90/90 PASS** |
| Original institutional destination URL retained for each numbered source | **90/90 PASS** |
| Categories | **12 declassified / 24 accountability / 21 engineering / 25 archives / 8 navigation PASS** |
| Retrieval groupings | **64 institutional pages retrieved; 18 automation restrictions; 3 JavaScript shells; 5 other unresolved PASS** |
| Search-token coverage of every original source title | **90/90 PASS (static index)** |
| Distinct supplemental example: National Archives Donated Collection Explorer | **1 intended result PASS (static search check)** |
| Static accessibility/security requirements (14 groups) | **14/14 PASS** |
| Group categories, escaping, rights statement, responsive CSS rules, keyboard-focus CSS, print CSS, skip link, labelled fields and live region | **Present; verified statically only** |
| No outside scripts/media; no telemetry or web fetch | **PASS by static inspection** |
| Live browser interaction at 320, 390, 768, 1440 pixels | **NOT RUN — required** |
| Screen-reader and keyboard reading order against real rendered page | **NOT RUN — required** |
| Destination-level institutional URLs | **Historical 2026-11-16 checks incorporated; not newly rechecked** |
| WordPress production-page or first-publish notification suppression | **NOT ESTABLISHED; no public change** |

**Important qualification:** The original WordPress order was preserved by each card's visible original index, but source cards are **grouped by category** in the portable desk; therefore their DOM order is not a byte-for-byte replica of the two original Gutenberg source blocks. This is intentional for scriptless browsing. Source mapping was checked by unique original `index`, not by naïvely assuming the DOM order matches the WordPress order.

## Publication gate and independent live readback

Authenticated WordPress readback on 2026-11-17:
- Published **Research Sources #1338**: `publish`, modified `2026-11-03T22:12:43`; page retained original URL, metadata, and noindex=false. Public signed-out rendered response HTTP 200, canonical `https://finalvestige.com/free-resources/research-sources/`, Jetpack SEO description claiming ninety sources. Its initial public HTML still contains stale sixty-source labels.
- Published **Library #77**: `publish`, modified `2026-11-07T19:39:01`; HTTP 200 and canonical `https://finalvestige.com/free-resources/`, unchanged.
- Existing Research Sources **staging #2354**: `draft`, modified `2026-11-17T02:43:03`, child of #77, `jetpack_seo_noindex=true`, untouched.
- Current GitHub PR #2816 remains **draft/unmerged**.

The screenshot service produces a ready mshots URL but the current container cannot resolve `s0.wp.com` or `finalvestige.com` to inspect pixels. CSS breakpoints and static rules are **not** substitutes for visual, keyboard or actual assistive-technology checks on the production theme. The WordPress pages connector does not provide an independently verified per-post `_jetpack_dont_email_post_to_subs=true` option, so do not assume a safe live publish or a muted subscriber/social blast.

**Release decision: HOLD.** No WordPress updates, public navigation, public downloads, new spending, social accounts, newsletter or third-party media changes. Obtain real screenshot/keyboard/screen-reader checks at 320/390/768/1440, confirm notification suppression and page-revision parity, and then decide whether to release the *existing* Research Sources correction. The portable desk is available for review in the draft PR now, without creating a competing page or preempting other editorial owners.

## Grok coordination (idea only)

A brief source-literate video could show why **a working catalog link is not proof that an underlying file was read**. One practical example would contrast a retrieved institutional landing page, a JavaScript-only interface, and an automated 403—not presenting any of the three as a vanished record. Script and distribution remain Grok-owned; no account action or scheduled publication was taken.
