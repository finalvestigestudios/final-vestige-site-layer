# Media Recovery — falsifiable 76% weight-reduction measurement protocol
**Date:** 2026-11-02 · **Owner:** Media Recovery PR #183 · **Browser evidence owner:** independent Site QA PR #154

## What was actually accomplished
Added an offline, read-only **paired CDP wire-weight decision gate** and a five-image exact-source evidence packet. This is new analysis code only; it does **not** replace Site QA's established Chrome/CDP renderer, network classifier, image census, request-ID attribution, or screenshots. It consumes the existing `browser_probe_chrome.cjs --all` output after Site QA obtains two genuine, comparable full-site guest-browser captures.

Current evidence is **61 published posts / 355 stored image references / 288 offsite-origin references**, **13 WordPress originals >1.5 MiB**. A previously reported **42 broken image** count is still **not browser-verified**. A previously mentioned **76% reduction** is still **NOT MEASURED**. The newly committed source-only five-PNG packet records **13,267,538 bytes of original storage**: this is not a browser transfer baseline.

## Exact audited P1 PNG sources
The machine record `qa/media-recovery/weight_claim_protocol_20261102.json` captures media **39–43** on `34:0, 35:0, 36:0, 37:0, 38:0`. The current original URLs are first-party `https://finalvestige.com/wp-content/uploads/2026/08/…png`, each source **1672×941** and stored HTML **1024×576**. Original storage totals **13,267,538 bytes**. No registered WordPress subsizes in inventory, no actual guest-CDP response or `currentSrc`, and no confirmed visitor error. The independent retriever could not access the five binaries; **no numeric HTTP status was observed**. Conditional candidate geometry: **960×540 with no upscaling** after genuine binary, visual and creator-rights review. Never assume these five are page downloads of their original storage sizes.

## Strict measurement contract
1. Site QA captures two **actual**, logged-out `--all` Chromium runs of the **same 61 public article URLs**, once before and once after a reviewed change, not dry-run plans. Each must reach the bottom of each article, verify all **355** stored image slots and have zero unresolved image identities / CDP image requests. Keep raw evidence and screenshots. P0 external breakage remains the first QA priority: `285:5`, `287:5`, `418:1`, `418:2`, `407:1`. Do not displace that queue for weight work.
2. Identical Chrome build, viewport, uncached CDP configuration (cache disabled and service workers bypassed), scroll timings, URL/post/slot census. Never compare a mobile-before to a desktop-after or a priority-only scan to all-site.
3. Derive article-image bytes from **network `Image` request IDs** through existing `request_id_wire_core.cjs`. Verify identity against the exact DOM `currentSrc`, 200 image MIME, decoded positive width, positive CDP encoded bytes, no cache. Shared DOM source reuse is counted **once per real requestId**; unrelated logos/page chrome are excluded. Extra same-source preloads, redirects with image identity mismatch, unresolved cached resources or missing bytes invalidate the page's measurement. Recompute the attribution, never trust a supplied total field.
4. If a stored source URL changes between baselines, require an explicit one-to-one approval manifest for each image key, old/new URL, rights reviewed, same-scene crop review, no-upscale demonstrated, derivative width ≤960px and positive height, and separate publication authorization. This analyzer does **not** itself authorize publishing. A new stored WordPress snapshot is required for a changed live source; a stale pre-change source census cannot prove new image identities.
5. A comparable pair is measured with **100 × (Σ per-article uncached CDP encoded bytes BEFORE − Σ AFTER) / Σ BEFORE**, using one visit per article in each snapshot. Never calculate site savings from five large originals, a hypothetical compressed size, archives, MIME size hints, downloader 403/404 wrappers, unverified 42 failures or mismatched screenshots. There is no **76%** claim without qualifying measured output. Full-site equal-article-visit sampling is **not** traffic-weighted real-user analytics.
6. If baseline articles contain broken/unresolved images, conservatively return `NOT_MEASURED` rather than counting absent bytes as successful optimization. Recover and verify visual integrity first, then obtain two suitable baselines. Optimize only with approved rights and crop preservation.

## Invocation after Site QA provides real evidence
```bash
node --test qa/media-recovery/test_weight_claim_pair_gate_20261102.cjs
node qa/media-recovery/cli_weight_claim_pair_gate_20261102.cjs \
  --before qa/media-recovery/runs/real-before-all-mobile.json \
  --after qa/media-recovery/runs/real-after-all-mobile.json \
  --approvals qa/media-recovery/runs/rights-reviewed-change-manifest.json
```
The `--approvals` argument is optional **only when stored image source URLs are unchanged**. All three inputs are local JSON files; the command issues no network requests and makes no WordPress writes. Exit code **2** means `NOT_MEASURED`/invalid inputs, not **0%** savings. Exit code **0** means a *measured* result; it does not imply that the result meets 76%, that the page has passed aesthetic QA, or that any publication is approved.

## Verification / provenance
- Core `qa/media-recovery/weight_claim_pair_gate_20261102.cjs`
- CLI `qa/media-recovery/cli_weight_claim_pair_gate_20261102.cjs`
- Tests `qa/media-recovery/test_weight_claim_pair_gate_20261102.cjs`
- Machine source packet `qa/media-recovery/weight_claim_protocol_20261102.json`; source record originates in reconciled `oversized_inline_proxy_corrected_20261102.json` **Git blob `827f29907b20d8a2d41b0ead107850006b9575f1`**.
- **30/30 tests passed** in an isolated V8 replay of the exact GitHub-committed core, tests, and both current dependency blobs. The isolated environment lacks the native Node runtime, so native Node `--test` / CI and real-browser scan remain outstanding; do not misstate either as completed.
- No original images copied/downloaded, no third-party scrape, no rights/license inference, **no WordPress production write, no homepage design change, no spend**. The staging/caching plan remains *only* a review proposal until actual visitor failures, item-specific reuse clearance, source/crop match, true no-upscale dimensions, a before/after screenshot and rollback approval exist.

**Coordination:** Pass new weight output schema to Site QA #154 for review without changing its branch. Media Recovery PR #183 owns the analyzer and five-source packet. The immediate execution dependency is Site QA's genuine completed guest-Chrome evidence, not another speculative URL inventory.
