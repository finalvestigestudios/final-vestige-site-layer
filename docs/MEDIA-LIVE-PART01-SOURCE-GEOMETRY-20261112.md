# Media Recovery: 8-post live source + geometry readback (Nov 12, 2026)

Draft PR #1703 **only**. Freeze: `qa/media-recovery/parts/01.json` from PR #183, blob `948bc1b65b42799aa40cfdb810ddf6ffd80886b6`. Authority for historical source candidates: 288-slot register blob `4965a862f7de7de46c1f4a1e26f3ca70a8c38805`. PR #154 owns logged-out browser collection; no duplicate work.

## New read-only batch
WordPress `posts_get(context=edit)` read eight published posts 621, 434, 433, 432, 431, 428, 425, 418. **52/52 inline sources and 52/52 ALT strings equal the October 30 frozen inventory.** Zero missing image tags or source drift. **37/52 lack both HTML width/height**, 15/52 have both, zero partial dimension pairs, and 0/52 have literal `srcset` in stored Gutenberg source. **41/52 have archival candidate catalog records**, which are *not* image or reuse approvals. The five malformed/missing dimension risks are not isolated to any origin: perform image-specific native-size verification before proposing width/height changes; do not rewrite Gutenberg blocks in production.

Machine record `qa/media-recovery/live_part01_8posts_52_images_20261112.json` contains actual published source URLs, frozen URLs, ALT, dimensions, source-catalog leads and explicitly `null` origin / guest statuses, natural dimensions and encoded bytes. It does not supply browser status or measured CLS. Native size and item rights of each catalog candidate must be verified independently before a conditional <=960px derivative. Maps, diagrams and photographs require scene and label fidelity and full-resolution access.

## Release constraints
The historical cohort stays 61 posts / 355 inline positions / 288 offsite, rather than treating the later 66-post set as its baseline. Historically reported 42 broken remain **not confirmed in guest Chrome**; proposed 76% reduction remains **unmeasured**. P1 >1.5 decimal MB 15 originals = 47,096,779 **stored** bytes, not network bytes. Site QA's priority P0 queue stays 285:5 -> 285:2 -> 287:5 -> 418:1 -> 418:2 -> 407:1; this batch includes 418:1 and 418:2 with unchanged source URLs but no observed guest success/failure. Do not claim images repaired.

Staging plan: only after Site QA supplies uncached CDP evidence and genuine missing-image diagnosis, verify same-scene primary catalog, copyright/license attribution, exact native dimensions, no upscale, at least 960px only where DPR warrants, and reversible isolated staging pair; no caching or WP upload before independent item authorization.

**No binaries downloaded, images cached, WordPress production writes, risky block rewrites, homepage changes, deployments, merges or paid services.** Offline validation/tests cannot replace native CI or genuine guest-browser checks.
