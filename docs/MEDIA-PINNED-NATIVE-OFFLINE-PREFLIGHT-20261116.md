# Media Recovery — SHA-pinned native Node release-preflight (2026-11-16)

**Status: REVIEW ONLY / no production repair.** This preflight closes an engineering evidence gap: prior source/rights/oversize/wire regressions were scattered across individual files and some were only tested in isolated V8, with no repository CI reported. It provides one explicitly bounded, **offline** command to execute five known Node suites and verify the *exact Git blob SHA-1* for every referenced test, validator and JSON fixture **before any suite runs**. No GitHub Actions workflow is installed, and no runner is scheduled, thereby avoiding unintended billable CI.

Run from a checkout of draft #183:

```sh
node --test qa/media-recovery/test_run_pinned_media_regressions_20261116.cjs
node qa/media-recovery/run_pinned_media_regressions_20261116.cjs
```

The first is the runner's own synthetic-only **13-case** native Node test; the second checks **14 pinned Git blobs** and executes **123 declared existing Node regression tests** across five suites. On missing/different blobs, misconfigured rights, unsafe paths, incomplete TAP output, skipped or failed tests it exits nonzero and reports `FAIL_CLOSED` or `HOLD`. It cannot download image binaries, modify WordPress, call subscriptions, deploy, inspect browser imagery or establish real HTTP statuses. The second command is a **future checkout gate**, not claimed to have executed during this automation run because a network-capable checkout of all 14 repository inputs is unavailable here.

## Test inventory and safety purpose

| Suite | Expected native tests | Item |
|---|---:|---|
| Twin USGS original URL reconciliation | 35 | 407:1: distinguish on-post -1959-0 old Original from sibling -1959 Original, and avoid wrapper-400 = server HTTP 400 |
| Coast Guard photo rights/conflicted surname | 21 | 418:1: exact `210330-G-DE713-0002.JPG`, USCG PD statement and Petit/Pettit caution |
| Official-source P0 candidate queue | 17 | P0 slot URLs and Florida Memory/USGS/USCG candidate fidelity and rights-HOLD |
| Oversize noninline surface inventory | 17 | Nine large originals: featured/page/drafts/unresolved, don't label as unused |
| Actual cold-wire savings acceptance | 33 | CDP per-request encoded bytes required; rejects unmeasured 76% savings |

**Expected 123** means the five existing individual test suites, not 123 browser observations. A native Node run of the runner's own **13 synthetic tests passed** in this run on the identical committed runner source blob `c7d23cda5094e0576eb10d1f7344e12961ef0309`; the committed test file has its own SHA and is to be re-run on a checkout.

## Current asset-release disposition

The exact candidate URL/source maps remain in [official nine-slot P0 ledger](../qa/media-recovery/official_p0_triage_20261115_2030pt.json), [Hebgen twin-catalog record](../qa/media-recovery/hebgen_catalog_alias_fidelity_20261116.json), [USCG item-rights record](../qa/media-recovery/uscg_scotch_cap_item_rights_conflict_20261115_2122pt.json), and [66-post oversized cross-surface ledger](../qa/media-recovery/wp66_oversize_noninline_cross_surface_20261115.json). Avoid copying them into a second, possibly drifting source-of-truth.

- **407:1 USGS** offers a different official Original URL for the same attributed J. R. Stacy scene, but no verified guest failure, identical frame/hash or native dimensions. Reversible WordPress substitution **HOLD**.
- **418:1 USCG** item-level public-domain evidence exists; guest delivery, required credit and frame/resize review remain **HOLD**, as does an unverified spelling change.
- **287:0/287:3 Florida Memory** RC09236 is an event-relevant car photograph but not proven the existing image's exact photographic frame or fully cleared for rehosting. **HOLD**.
- **285:5, 287:5, 418:2 and other suspected failures** still have retriever-level concerns, not Site QA browser 4xx/decode proof. Preserve editorial subject, ALT and caption; do not replace with a different scene.
- **960px rule:** only derive after a rights-cleared binary is reviewed and native dimensions are measured. Set width `min(960,nativeWidth)`, height `round(nativeHeight × width/nativeWidth)`; never upscale or silently crop. Store an attributable WordPress Media Library copy *only after* positive source identity, reuse rights, browser failure, visual acceptance and explicit staging permission. This run performs no such copy.

## Acceptance still blocked by real browser evidence

Site QA #154 already owns the guest-browser collector. It must produce actual `currentSrc`, GET request/response status, image MIME, decode/natural pixels, screenshots and CDP encoded bytes for its original six P0 images; this gate **does not duplicate** its collector. External web-reader 403/404/unsupported-content responses cannot be reported as visitor HTTP outcomes. The original **42 broken** remains an *unverified report* and **76% weight reduction remains an unmeasured hypothesis**. Historical 61 posts/355 source refs are separate from the newer 66/361 census. Twenty WordPress originals >1.5MB contain 64,385,752 **stored** bytes, not cold-image transfer bytes.

No image binary download, production WordPress write, published-block rewrite, homepage design edit, deployment, merge or subscription spend was performed.
