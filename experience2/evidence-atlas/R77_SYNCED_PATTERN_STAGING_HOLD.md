# Apollo R77 — native synced-pattern source and asset custody

**Release: DRAFT / STAGING_HOLD. Issue #150. Not installed, merged, published, or cleared for production.**

## Why this sprint exists

The original Research Desk PR #158 documents a real WordPress lifecycle risk: a shortcode embedded in a reusable Gutenberg block or template part can render after `wp_head`, so stylesheet enqueueing inside the shortcode is too late. The Apollo suite has an explicit private-staging page-ID opt-in, but did not automatically discover a source-verified suite inside two-level `core/block` synced-pattern references. Existing R68–R76 genuine WordPress testing inserted only a flat top-level shortcode, so it did **not** settle this gap.

## Isolated implementation

The *Apollo integration adapter alone* now follows `core/block` references from the queried post to **published `wp_block` posts** using `parse_blocks` and `get_post`, both read-only WordPress APIs. It discovers the existing `[fv_ex2_apollo_suite]` before `wp_head` and calls the existing fully pinned asset enqueue gate. This does not modify the original PR #158 plugin, immutable NASA records, Atlas HTML/JS, WordPress settings, or homepage lanes.

Traversal is deliberately bounded to six nested reference levels, 32 unique synced-pattern IDs, 256 parsed blocks per level and 200 KB per fragment. A missing ref, private/draft ref, wrong post type, circular ref, or over-budget path does not authorize a preload. Unrecognized dynamic template parts remain outside automatic discovery: the previously documented **private staging page-ID opt-in** remains the safe fallback rather than eagerly executing dynamic blocks.

## Real WordPress acceptance addition

R77 extends the established disposable WordPress Playground + official Assembler scenario with locally created Gutenberg **two-level synced patterns**, a private page containing only an outer `core/block` reference, and an unrelated published pattern/private page as a negative control. These fixture writes occur solely inside a freshly created local VM under a strict loopback/environment guard.

Five additional independent Chromium scenarios test 390 and 1440px with JS on/off, plus the unrelated-pattern negative control. The suite must appear from actual WordPress block rendering with 6 Research Desk and 6 Evidence Atlas records, **30 + 54 custody values**, no invented geographic markers or unreviewed NASA imagery. Stylesheet links for all three components must be in the document **head** (not late footer); the unrelated page must not enqueue Apollo CSS. JS-enhanced filters, native no-JS source visibility, true axe-core audit, local LCP/CLS, offline-only network policy, responsive overflow, screenshots and a source-preserving browser PDF are also tested. The previous 14 width/JS scenarios remain unchanged and separately counted.

Adversarial PHP fixture tests cover nested, grouped, top-level, unrelated, draft, wrong post type, missing refs, cycles, excessive source length and depth. The PHP stub is **not** substitute evidence for real WordPress. Browser results are only verified if exact-head CI completes successfully; do not claim success from tests merely committed.

## Promotion gates / exclusions

This does **not** demonstrate hosted WordPress.com parity, block-template-part discovery, human NVDA/VoiceOver, mobile Safari, field INP/LCP/CLS, or accessibility certification. All six NASA photo-use assessments are still `INDIVIDUAL_REVIEW_REQUIRED` and the S67-19766 catalog relationship is provisional. No NASA images, copyright clearance, speculative latitude/longitude, relationship edges, or paid services are introduced. The R76 native-print footer behavior still needs hosted editorial review to ensure a customized site footer does not lose meaningful print information.

Do not merge or deploy. Keep homepage PR #49 and the homepage lead's branches untouched. Request independent QD, editorial, rights, accessibility, and founder release approval after successful exact-head genuine WordPress evidence.
