# Kosmos 954 post 279 — offsite media, exact archival scene, and rights release hold (2026-11-02)

## Scope and evidence

This is an **independent media-recovery source and visual-integrity sprint**, not a browser-health claim or a homepage redesign. Frozen authenticated WordPress census `qa/media-recovery/parts/03.json` (blob `49183f66f880f7c4dfd363acca906876877f2e5e`) contains six original published image URLs and six ALT values for [The Geologists Found the Spy Satellite](https://finalvestige.com/2026/08/19/the-geologists-found-the-spy-satellite/), post 279, modified 2026-09-08. No fresh CMS readback occurred this sprint.

Independent November 2 image-renderer probes **displayed exact URLs 279:0, 279:1, 279:2, 279:3 and 279:4**. The token-bearing LinkedIn URL **279:5 was inaccessible** to that retriever. These are **not** browser HTTP success/failure records. No numeric origin response, decoded natural dimensions, site visitor `currentSrc` or transferred byte totals were established; therefore **0 confirmed newly broken browser images** and **0 evidence of 76% image-weight savings**.

## High-value same-scene archival identification

Published **279:0** (Polish Spider's Web CDN) visibly shows four bundled searchers working over snow with radiation equipment. The **same composition** appears in [Wikimedia Commons: *Cosmos 954 - Recovery 001.jpg*](https://commons.wikimedia.org/wiki/File:Cosmos_954_-_Recovery_001.jpg), tracing to **U.S. Department of Energy Operation Morning Light Fact Sheet DOE/NV1198**. That catalog states original **576 × 452 pixels / 60 KiB-class**, with a U.S. DOE public-domain label and caveat that national laboratory rights may vary. The existing publisher rendition **is not SHA-matched or crop/retouch-verified**. Any conditional rights-cleared derivative must be **no larger than 576 × 452** (never scale to 960), preserve the composition, and carry truthful original credit. This is a *same-scene candidate*, not an approved download or replacement.

**279:4** is the current exact Commons-hosted LLNL-attributed [Cosmos-954 Reactor.png](https://commons.wikimedia.org/wiki/File:Cosmos-954_Reactor.png), a **640 × 958** vertical schematic; preserve its tall form and technical labels. Commons applies a PD-USGov rationale, but laboratory contractor authorship is not automatically federal-employee public domain. Item-level rights review and a legible mobile layout are required. Avoid squashing/cropping the vertical diagram. The graph marks several assumptions, unlike the current ALT's stronger “technical reconstruction” wording.

**279:2** is a diagram served from the Chinese Baidu CDN; it displayed in the independent renderer, but rights are unknown. A **different-scene illustration** with primary NNSA/DOE lineage, [*Cosmos-954 scheme.jpg*](https://commons.wikimedia.org/wiki/File:Cosmos-954_scheme.jpg), is cataloged at **868 × 608**. It is **not** a same-image match. Switching the depiction would require explicit editorial acceptance, source verification, licensing, and ALT/caption revision. Do not assume unlicensed mirror permission.

**279:3** is a composite currently displayed from Space Academy Australia. The visible four-panel collage depicts search teams/equipment, a snowy landscape and an Operation Morning Light insignia; **the ALT's aircraft reference is not supported by the pictured panels**. Proposed, unpublished ALT: “Four-panel Operation Morning Light collage showing teams at work in snow, a search landscape and the operation's emblem.” The DOE [Recovery 002 archival file](https://commons.wikimedia.org/wiki/File:Cosmos_954_-_Recovery_002.jpg) is a **different** image (562 × 453), not a same-scene replacement.

**279:1** is a displayed 1975 Short Skyvan aircraft photograph (illustrative type comparison, not footage of the 1978 operation). Original catalog dimensions and photographer/license still need item verification. **279:5** is an exact token-bearing LinkedIn image URL; the independent retriever could not access it, with no visitor HTTP conclusion. Its scene and reproduction rights cannot be approved without source and screenshot evidence.

## Important commercial-reuse blocker

Canada's [Ingenium Cosmos 954 object collection 1988.1334.001](https://collection.ingenium.ca/en/id/1988.1334.001/) is an authoritative historical reference, **but its own image terms are noncommercial and specifically require contacting the museum for commercial use**. Final Vestige's monetized site must **not** treat this museum image as an authorized free replacement or cache it. Its catalog information is not a license to reuse the photograph.

## Site QA coordination and conditional WordPress caching procedure

Site QA #154 retains its current P0 **285:5, 287:5, 418:1–2, 407:1** guest-browser image verification. Add **279:5** as a subsequent tokenized-CDN investigation, and preserve screenshots of **279:3/279:4** for editorial ALT review, without modifying Site QA's code/drafts. Gather Chromium source `currentSrc`, HTTP final response/redirect, MIME, `naturalWidth/Height`, loaded/failed state, CDP encoded transfer bytes, and mobile crop. A retriever fail is **not** a broken-image count.

Only after **actual guest failure + exact scene/crop confirmation + item copyright/credit approval** should editors stage a local WordPress Media Library derivative (max width **min(960, genuine original width)**; no upscaling; preserve aspect ratio and annotations), set descriptive ALT/caption, inspect logged-out desktop/mobile visually, compare transfer bytes under matching uncached profiles, and retain the original `src`/post revision for rollback. No automated Gutenberg block rewrites or blind mirroring.

**Decision:** all six slots remain **HOLD** for cache/upload/post-edit. No image binary downloaded, WordPress production changes, subscriptions, or homepage visual changes in this sprint. Existing **61 posts / 355 stored sources / 288 external-origin / 13 WP originals >1.5 MiB** remains the source census; reported **42 broken** unverified through visitor-browser evidence and **76% reduction** unmeasured.

Evidence: [six-source machine ledger](../qa/media-recovery/kosmos_279_hotlink_source_recovery_20261102.json), [defensive offline validator](../qa/media-recovery/validate_kosmos_279_20261102.cjs), and [16 regression cases](../qa/media-recovery/test_kosmos_279_20261102.cjs) (isolated V8 replay; native Node and visitor Chromium not completed).
