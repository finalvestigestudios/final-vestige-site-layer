# Media Recovery: Frozen-source census required before claiming a measured 76% image reduction

**Date:** November 2, 2026. **Branch/PR:** `qa/media-recovery-reviewed-20261030-1158` / #183. **Scope:** offline performance evidence validation only; independent of homepage design and Site QA PR #154.

## Verified failure mode
The existing `weight_claim_pair_gate_20261102.cjs` correctly checks CDP requestId-bound image bytes, complete 61-page scans, 355 slots, zero unresolved images and matching before/after URLs. However, it did **not** authenticate the 61 article IDs, article permalinks or 355 stored image source URLs against the real Final Vestige corpus. Its own successful simulated test uses invented 1000–1060 post IDs and invented image URLs. A user could therefore get `MEASURED` on a consistent but unrelated 61/355 pair. That is valid for code demonstrations but **not evidence of an actual FinalVestige.com site-wide reduction**.

## Safe engineering fix
Added `qa/media-recovery/frozen_census_claim_gate_20261102.cjs` and switched the **read-only CLI entrypoint** to `assessFrozenPair`. This first verifies the Git SHA-1 blob identities of all eight October 30 archived source parts, runs the existing inventory validator, then checks **all 61 baseline post IDs/permalinks and all 355 baseline image keys/exact source URLs** against the frozen WordPress source. It passes only an exact authentic baseline to the existing paired-CDP transfer evaluator. Candidate image changes are still subject to its explicit rights/visual/crop/960px/no-upscale/release approval checks. Any tampered archive, unrelated site, incomplete slot or changed baseline source produces **NOT_MEASURED**.

The actual eight GitHub source parts were re-read: **8/8 pinned blob IDs matched; 61 unique posts; 355 unique image keys; 61/61 source per-post image counts matched; zero image records with an unregistered post ID**. This is source-inventory integrity, **not a visitor image GET**.

## Test evidence
Executed native **Node v22.16.0: 13/13 new regression checks passed** on byte-for-byte locally authored source/test files. The suite rejects arbitrary article IDs, source swaps, changed permalinks, duplicate slots/IDs, absent images, wrong frozen counts and edited SHA-pinned parts. GitHub source/test blobs were checked against local `git hash-object` values. The existing 30 synthetic weight arithmetic tests remain useful as isolated arithmetic tests; use the new frozen CLI, not direct `assessPair`, to evaluate any real site-wide performance claim.

Run locally from a repository checkout with the eight frozen source parts:

```sh
node --test qa/media-recovery/test_frozen_census_claim_gate_20261102.cjs
node --test qa/media-recovery/test_weight_claim_pair_gate_20261102.cjs
node qa/media-recovery/cli_weight_claim_pair_gate_20261102.cjs --before /secure/guest-before.json --after /secure/guest-after.json --approvals /secure/approved-photo-changes.json
```

Never store authenticated CMS dumps or real guest browser logs containing tokens in Git. The CLI is offline/read-only and does not approve WordPress publication.

## Pending proof / priority
Site QA #154 retains browser-network ownership. Its highest-value guest Chrome queue remains **285:5, 287:5, 418:1, 418:2, 407:1**. For each, capture visitor `currentSrc`, CDP final image requestId, actual HTTP status/MIME, `naturalWidth`, transferred bytes and a visible screenshot. Archive reconstructions must keep exact historical identity/crop/caption; records from USGS, USCG, Navy, Florida Memory, NARA and Commons remain subject to item-level rights and attribution review before any first-party WordPress cache. Any derivative is **≤960px wide, never upscaled**.

**Status:** No guest Chrome responses collected in this sprint; the 42 alleged broken images remain unproven as a site-wide count; the previously cited 76% remains unmeasured; the 13 >1.5 MiB WordPress originals are storage sizes, not visitor network bytes. No production edits, asset copies, homepage changes or subscription spending.
