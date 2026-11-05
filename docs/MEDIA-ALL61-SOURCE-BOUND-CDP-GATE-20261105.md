# All-61 image evidence reconciliation — isolated media sprint (2026-11-05)

**Ownership:** Media Recovery, independent of interim homepage art direction and Site QA's browser-collection code. **Status:** review-only, zero production changes, no third-party image downloads, no rights clearance, no spend.

## Major engineering deliverable

This branch adds a **read-only, standalone, all-post inventory-to-browser reconciliation gate**. It consumes the *existing* Site QA/#154 guest Chrome/CDP probe (no competing collector) and the eight already-pinned WordPress source parts from #183. It binds each browser image to its **specific frozen WordPress post, image slot, original URL and unique CDP request ID**. It refuses a sitewide broken-image total if even one of the 61 posts/355 slots lacks complete validated guest evidence.

- `qa/media-recovery/reconcile_all61_guest_inventory_v1.cjs`: offline CLI, strict source census, full-scroll/uncached CDP identity+decoded pixels, one-to-one source binding and request-level byte de-duplication. Requires exact screenshot evidence to confirm a broken slot. An individual validated loaded/broken result does **not** authorize rehosting or WordPress editing.
- `qa/media-recovery/all61_source_bound_pending_20261105.json`: **355 actual original image source URLs** from 61 frozen published articles, the six P0 slots and their null *actual browser HTTP statuses*, per-slot rights and 960px HOLD. Includes exact Git blob SHAs of the eight frozen input parts. No invented 404s or transferred bytes.
- `qa/media-recovery/test_reconcile_all61_guest_inventory_v1.cjs`: **29 deliberately independent source-level cases** for source/host/count tampering, URL/post drift, missing scroll, contradictory HTTP and MIME, missing cache flags, wrong request IDs, decode failure, unverified broken screenshots, unauthorized caching and deduplicated repeated image references. **29/29 verified against exact committed source/test blobs in isolated V8**. Native Node/GitHub CI and actual logged-out Chromium execution remain pending.

Source script blob: `69a9060766e7e48f6accffe5d612ec12fa975aac`. Test blob: `53a97e5a5ad49e91e04af9866649473563677f4d`.

## Scope of the audited baseline

| Measure | Frozen source / actual status |
| --- | --- |
| Published articles | 61, WordPress 2026-10-30 source snapshot; not a fresh count |
| Stored inline image references | 355 |
| Distinct exact original image URLs | 353 (two repeated-source pairs) |
| Direct offsite references | 288 in media inventory; #154's 286 is a historical origin-classification discrepancy |
| Source img tags missing width or height | 305; **not proof of real CLS** |
| Images with **actual visitor browser HTTP/decode proof** in this batch | **0** |
| P0 original URLs/source slots | **6** (285:5, 285:2, 287:5, 418:1, 418:2, 407:1) |
| Claimed 42 broken in a browser | **Unverified**; sitewide proven count = `null`, not zero |
| Claimed 76% transferred-byte improvement | **Unmeasured**; no paired real cold-client traces |
| Oversized WordPress originals >1.5 MiB | 13 / 43,522,829 **stored** bytes (existing baseline, not visitor traffic) |
| Five first-party full-size PNG heroes in posts 34–38 | 13,267,538 stored bytes; no existing subsize in prior WP inspection |
| Production repairs, new caches, WordPress changes | **0** |

## Priority restoration / source-candidate handoff

Keep **Site QA #154's existing** guest browser P0 queue unchanged. Do not add duplicate browser collectors or substitute different historical scenes merely to avoid a failed third-party URL.

1. **285:5 (Say Media / Three Mile Island), 285:2 (UCS panel)** — the publisher-source failures are only third-party retrieval-wrapper results; 285:2 has a separate archival same-scene Commission-report candidate in #1084. Rights, crop fidelity and guest browser status remain HOLD.
2. **287:5 (Sunshine Skyway)** — old Catalyst path returned retrieval-tool 404 on Nov 5. The publisher's **new own-media path** `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` displayed the collision-wreckage scene. This is **not** a license for copying; publisher/University Press of Florida reuse permission needs review. The ALT description should not assert the later replacement bridge is pictured.
3. **418:1/2 (Scotch Cap)** — old Coast Guard photo paths have retrieval-tool 403s. Museum source `https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg` displays a 600×463 historic debris scene. Rehost authorization and photographic identity remain HOLD; never enlarge it to 960.
4. **407:1 (Hebgen Lake)** — exact original URL is a USGS catalog Original download, with an image-level public-domain designation. Prior retrieval wrapper could not handle its octet-stream response, which is **not** proof of browser failure. Preserve the image unless guest Chrome shows an actual problem.

These are existing source-level findings (see PR #183 and isolated #1077/#1084), **not new release approval**. For Navy, Coast Guard, Florida Memory and USGS primary archives, retain item IDs, date, photographer, attribution and item-specific rights, checking each before derivatives. A commercial website must not silently assume a photograph is freely reusable because it appears on a government page.

## Reproducibility and release safety

Use the existing eight JSON parts on PR #183 in a local read-only checkout; they are intentionally **not duplicated onto this small PR**:

```bash
node qa/media-recovery/reconcile_all61_guest_inventory_v1.cjs \
  --inventory-dir /path/to/PR-183/qa/media-recovery \
  --output /tmp/fv-media-pending.json

node qa/media-recovery/reconcile_all61_guest_inventory_v1.cjs \
  --inventory-dir /path/to/PR-183/qa/media-recovery \
  --guest /path/to/existing-site-qa-full-61-guest-CDP-run.json \
  --output /tmp/fv-media-browser-verdicts.json

node --test qa/media-recovery/test_reconcile_all61_guest_inventory_v1.cjs
```

The CLI exits nonzero if a supplied browser run **does not completely substantiate all 61 posts**. Unverified per-slot statuses remain visible in the JSON; a partial capture can never masquerade as a 42-failure sitewide census. No external network is required.

**76% measurement gate:** capture real *before and after* logged-out, same-viewport, same-full-scroll, cold-CDP runs with all relevant images decoded, record actual CDP encoded-data bytes by distinct network request ID (not stored CMS originals), ensure identical editorial image scenes/alt and no material crop/legibility regression. The present script reports an article-wire total only for a fully loaded run; the existing paired comparator in #183 must verify actual before/after. There is no justified sitewide 76% claim without both captures.

For any proposed fix, create **staging-only** ≤960px-width, no-upscale derivative from an authorized master, preserve aspect ratio/color/scene, record source catalog link, copyright, original and new SHA-256, credit, exact image slot and reversible rollback. Do **not** mirror third-party photos without reuse rights; do **not** blindly rewrite Gutenberg image blocks. QD editorial, rights and independent visual QA remain mandatory before any WordPress publication.

**Evidence scope:** committed static audit is a read-back of the eight GitHub inventory source blobs at PR #183, not direct new HTTP/CDP evidence. Actual visitor status remains `null` throughout. The new collector-binding safeguard adds no production effect until deployed and run against real QA evidence.
