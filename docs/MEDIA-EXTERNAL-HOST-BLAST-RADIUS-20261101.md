# External image-host blast radius and P0 rights hold — 2026-11-01

**Scope:** read-only, deterministic regrouping of the eight authenticated 2026-10-30 WordPress source-snapshot parts. No guest-browser proof, HTTP requests from this code, downloads, WordPress changes, homepage design changes, permission grant, or new spend. This is **Media Recovery PR #183**, not Site QA PR #154's browser instrumentation or source-classifier implementation.

## Audit results and why the denominators matter

| Measure | Verified against the frozen source corpus |
|---|---:|
| Published article posts | **61** |
| Stored inline image references | **355** |
| Direct WordPress sources | **60** |
| First-party Jetpack proxy sources | **7** |
| Offsite references (including offsite-host Jetpack proxy origins) | **288** |
| **Distinct raw offsite URL strings** | **286** |
| **Distinct offsite source hostname strings** | **79** |
| Browser-verified failures / measured guest bytes | **unknown / unknown** |
| Founder-reported 42 broken / 76% savings | **both unverified** |

**Source-host concentration is a potential failure blast radius, not the list of broken hosts.** Top sources: `commons.wikimedia.org` **118 refs across 20 posts**; `upload.wikimedia.org` **18/10**; `www.history.navy.mil` **15/4**; `d9-wret.s3.us-west-2.amazonaws.com` **9/2**; `www.floridamemory.com` **7/1**; `tile.loc.gov` **7/4**; `cdn.loc.gov` **7/2**. Commons redirect + raw upload together expose **136 stored refs** to Wikimedia image delivery behavior. This does **not** prove 136 broken photos; Jetpack rewriting, cache, URL redirects, CSP and lazy loading can change what browsers actually request.

Two `i0.wp.com` references **are not first-party originals**: **291:0** proxies `text-message.blogs.archives.gov` and **285:1** proxies `www.squawkpoint.com`; the other seven `i0.wp.com` refs point back to Final Vestige originals. This explains part of the older QA 286-versus-288 *reference classification* discrepancy; it is separate from the coincidental **286 distinct offsite URL strings** in the current 288-ref snapshot.

Two URLs occur twice, each in one post: **291:2 and 291:5** are one Deseret News Teton aftermath photograph (the first ALT wrongly describes an active breach; see previous Teton audit); **213:2 and 213:6** reuse one National Wildfire Coordinating Group Mann Gulch map with different contextual descriptions. Count physical requests from actual browser network entries, **not two assumed byte transfers per reused URL**.

The complete **79-host / 288-key rollup, exact source URL samples and proxy exceptions** are in [machine-readable data](../qa/media-recovery/host_exposure_20261101.json). Inputs are pinned to eight source-part **Git blob SHA-1** values and validated by [fail-closed verifier](../qa/media-recovery/validate_host_exposure_20261101.cjs) and [30 native Node tests](../qa/media-recovery/test_host_exposure_20261101.cjs).

## P0 recovery queue — recent retriever evidence, *not* guest status

| Slot | Stored URL evidence | Primary/archive candidate | Release gate |
|---|---|---|---|
| **285:5** Three Mile Island | SayMedia original **retriever 404** | [Commons creator-original photo](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg), catalog **819×614**; no upscale, candidate **819×614** | Verify same photograph/crop and copyright; **HOLD** |
| **287:5** Sunshine Skyway | Old St Pete Catalyst URL **retriever 404**; [new publisher media URL](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg) displayed independently | [St Pete Catalyst original report](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/), credit **University Press of Florida** | New URL is **not a free-use license**; verify crop and correct misleading later-bridge ALT; **HOLD** |
| **407:1** Hebgen Lake | USGS S3 source was reported as unsupported octet-stream by retriever; the wrapper's 400 is **not origin HTTP 400** | [USGS image record](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959), alternate same-record JPG path, master dimensions unknown | Confirm visitor MIME/decode and exact derivative; **HOLD** |
| **418:1** Scotch Cap | media.defense.gov portrait **retriever 403** | [U.S. Coast Guard official archival record](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/), ID **210330-G-DE713-0002** | Confirm image-specific release and Anthony Petit/Pettit credit; **HOLD** |
| **418:2** Scotch Cap | history.uscg.mil debris photo **retriever 403** | [USCG historical article](https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/) | Individual accession/dimensions unknown; **HOLD** |

The source viewer was refreshed for **285:5, 287:5 and 418:2** on 2026-11-01. Those tools returned wrapper errors, **not measured guest network GETs or a proven production outage**. Missing source dimensions stay **null**; maximum proposed derivative width is **960px, preserving aspect ratio with no upscaling**. Read the [P0 ten-image queue](../qa/media-recovery/p0_restoration_release_queue_20261101.json) and [Skyway publisher migration ledger](../qa/media-recovery/skyway_287_source_relocation_20261101.json) for per-image ALT, provenance and rights notes. No media binaries were fetched or cached.

## Performance accounting (no invented 76% claim)

The CMS holds **13 WordPress originals >1.5 MiB totaling 43,522,829 original file bytes**. Five featured+inline 1672×941 PNG originals have no WordPress-generated subsize metadata and total **13,267,538 original bytes**; conditional crop-preserving derivatives are **960×540**. Do **not** assume that originals are what browsers download; Jetpack may already supply smaller variants. See [13-image metadata evidence](../qa/media-recovery/large_first_party_20261101.json).

For actual transfer comparison, Site QA should collect **cold-cache logged-out mobile and desktop** post-render `currentSrc`, image decode and final network status/MIME/redirect, encoded request bytes, screenshots, LCP and CLS. A claimed 76% reduction requires **same-page, same-viewport, same-asset** before/after transfer bytes, deduplicated by observed requests and matched by image identity. Distinguish **historical-image repairs** (replacement content) from **same-image compression** (which the current [wire comparator](../qa/media-recovery/compare_wire_core.cjs) strictly measures). A changed published source URL must pass a *separate* rights/crop/visual identity review; do not bypass the wire comparator to claim compression from swapped photographs.

## Controlled first-party migration pathway (no authorization implied)

1. Site QA logs confirmed guest failure or excessive measured transfer, including exact rendered `currentSrc`, final response, cache state and screenshot.
2. Media Recovery links the **same photograph**, correct original creator/custodian, individual reuse terms and attribution; reject subject-only lookalikes, artist-owned works without permission, or scene/crop mismatch.
3. Only with permission, create a derivative `width=min(originalWidth,960)`, maintain aspect ratio, no upscale; preserve master SHA-256, derivative SHA-256, color/crop and source credit.
4. Stage a **WordPress Media Library cache plan** with item ID, responsive sizes and reproducible before/after proof. Keep production uploads and Gutenberg block changes disabled absent explicit release approval.
5. Compare image integrity and visitor network after any approved change, log a reviewer-approved result and actual bytes; only then report broken-image repairs or savings.

**Verification:** 1 positive baseline and **28/28 deliberately falsified audit mutations** passed in isolated JS against the actual saved snapshot/validator; native Node suite contains **30 tests** including source Git blob checks, and awaits a native run. The content-only branch does not deploy or alter live media. Exact final commit SHA and QA handoff will be recorded in the PR conversation.
