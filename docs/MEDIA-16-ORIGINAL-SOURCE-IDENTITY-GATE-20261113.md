# Nov 13 media source-identity integrity correction (draft only)

**Scope:** The existing [16-oversized WordPress media ledger](../qa/media-recovery/wp_123_media_16_draft_20261113.json), not Site QA browser collector or homepage visuals.

## Reproduced defect

The original validator accepted a same-host substitute URL for media 39, accepted swapped stored-byte sizes for media 39/40 while the total stayed equal, and tolerated hidden permission metadata. These are offline evidence-tampering examples, **not observed live WordPress corruption or real broken images**.

## Correction

Each of the 16 media IDs now binds to its frozen exact source URL, timestamp, parent, MIME, original bytes, native geometry and declared WordPress derivative descriptors. All root, policy, inventory, row and dimension schemas reject unrecognized fields (including fake cache/rehost approvals). The original validator and 20 existing tests remain; an additional 73-case identity test suite covers all 16 rows and compensating swaps. [Machine-readable evidence](../qa/media-recovery/media_16_source_identity_integrity_20261113.json) retains exact original URLs and explicit null HTTP/guest transfer fields. The frozen values describe Nov 13 WP readback only and **must not be promoted to fresh CMS or visitor-browser evidence**.

## Release and measurement gates

Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) retains the P0 six-image guest-CDP queue and owns the collector. To verify alleged 42 failures, require true network Image responses after redirects, decoded pixels and screenshots; wrapper HTTP errors do not count. To measure claimed 76% benefit, use cold uncached, matched historical image slots with unchanged exact sources, per-image encoded transfer bytes, responsive widths and device pixel ratio; never substitute stored originals for wire bytes. Original 61/355 frozen and current 66/361 cohorts must remain distinct. Of 16 >1.5 decimal MB originals (49,107,665 stored B), attachment 2432 belongs to a draft, not verified as a published article transfer.

Any 960px/no-upscale derivative is **conditional** on item rights, accurate historical photograph/crop, caption/ALT fidelity, site QA and reversible staging. No image downloaded or cached; no public WordPress post/media write, homepage design change, merge, deployment or spend.
