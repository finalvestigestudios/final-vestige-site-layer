# Media Recovery QA — image-slot parity versus shared network requests
Run: 2026-11-17 09:27 PT. Scope: **draft PR #2747 only**. No WordPress/production/homepage writes.

## Verified source-level failure mode

The preceding `slot_parity_61_20261117.cjs` required a unique `request_id` for *every* HTML image slot and added `wire_bytes` per slot. Two actual published posts contain two slots referencing an identical source and identical Jetpack VIEW URL, so one successful Chromium fetch can legitimately populate both DOM images. A duplicate network ID is not in itself evidence of lost images; separately recording the same network bytes against each slot would inflate the denominator of the proposed 76% saving.

Previously authenticated WordPress VIEW and historical census (Git blob `421a2c1d06694726339f4416673cfb6eea78f73d`) identify:
- Teton Dam post 291: slots **291:2, 291:5**, same Deseret `PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG`, same published Jetpack URL, different ALT; **291:2's growing-breach caption is not supported by its reused cleanup photograph**. Editorial correction needs separate review.
- Mann Gulch post 213: slots **213:2, 213:6**, same official NWCG `sr-mg-historical-map-race-pg5.jpg`, same published Jetpack URL, different descriptive contexts; **no automatic editorial correction**.

The historical 61-post inventory contains 355 image slots but **353 unique authored URLs**. This is source evidence, **not** a demonstration that Chrome in fact used one CDP request for either pair; all guest HTTP/decoding/bytes remain unknown.

## Isolated code correction and acceptance logic

Updated `qa/media-recovery/slot_parity_61_20261117.cjs` on media draft branch, without changing Site QA #154 or its browser collector:

1. Keep **every authored DOM slot** in the 61/355 parity check, and require its own decoded natural dimensions and visual evidence.
2. Within **one post and one before/after phase**, allow multiple slots to reference **the same CDP request ID** only if their `current_src`, request URL, HTTP response code, MIME, wire bytes, natural dimensions and cache/service-worker/prefetch flags agree exactly.
3. Count that shared request's transfer bytes **once**. If the same URL was fetched in two separate real network requests with different IDs, count both transfers.
4. Fail closed on one ID assigned to different URLs or contradictory status/bytes/MIME/dimensions; continue rejecting missing images, stale source revisions, failed decode, HTML responses, cache contamination, altered source identity and missing visual evidence.
5. Preserve `MEASURED_SUBSET_NOT_SITEWIDE` and `ALL_355_SELF_REPORTED_REVIEW_REQUIRED` results. Never certify 76% based on self-reported screenshot flags or historical stored-media bytes.

Four deterministic new Node `test` definitions cover legitimate request sharing, two independent GETs, mismatched bytes and divergent URL/MIME/native size. Existing 32 tests remain, including rejection of a duplicate request ID for **different** sources. **Test definitions committed; native Node and GitHub CI execution remain unverified** in this run. Command to execute from a checked-out branch:

```sh
node --check qa/media-recovery/slot_parity_61_20261117.cjs
node --test qa/media-recovery/test_slot_parity_61_20261117.cjs
```

## Rights, 960px, cache and rollback

This accounting fix never approves an image substitution or redistribution. The Deseret photo remains third-party and cannot be copied to WordPress without source-specific permission. For a *different-frame* Teton historical correction, the [National Archives NAID 28894684](https://catalog.archives.gov/id/28894684) record supports an editorial candidate; Commons/DPLA lists 2558×1728 before a conditional proportional 960×649 review rendition, with an altered crop/rotation in later Commons history. NARA custody is not equivalent to a binary-identical replacement. The NWCG government-hosted map also requires item-specific credit/rights and exact rendered-frame verification before any possible rehosting.

Proposed future caching workflow, **not executed**: Site QA first captures logged-out cold `currentSrc`, HTTP/MIME, decoded pixels, screenshot and transferred bytes; editorial owner checks visual identity/caption; rights officer reviews accession/credit; verify binary SHA-256 and native dimensions; create a <=960px *no-upscale* derivative only on a permitted isolated staging environment; compare cold screenshots and bytes with every slot preserved; require explicit authorization before a versioned WordPress Media Library swap; retain original URLs, revisions and rollback snapshots. No risky Gutenberg block rewrite.

## Boundaries / source provenance

Machine audit: [shared-request collision JSON](../qa/media-recovery/shared_request_collision_20261117_0927pt.json). Original source/collision report: Git blob `421a2c1d06694726339f4416673cfb6eea78f73d`, previous media draft HEAD `34637f79024ac0286fb6fea23de0ec682d54b8f9`. The primary `docs/IMAGE-WEIGHT-WORKLIST.md` resides on independent draft PR #183 (blob `71280920640a00551b4d2c2b54fa0f95e33030b8`), not this media branch or main. Site QA #154 remains the browser evidence owner.

The reported **42 broken images are still not independently guest-browser confirmed** and **76% transfer reduction remains unmeasured**. Twenty originals >1.5 decimal MB total **64,385,752 bytes of stored files**, not visitor network bytes. This sprint has made **zero** WordPress production writes, downloads, rehosting, caching, homepage edits, block rewrites, merges, deployments and subscription purchases.
