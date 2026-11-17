# Media Recovery — final-redirect false-positive and Skyway source verification
**Date:** 2026-11-01. **Scope:** isolated draft Media Recovery PR #183, not homepage design or Site QA PR #154.

## Actual engineering defect

The previous `classifyImages()` identified a network request using `url_aliases` as well as the final CDP URL. That is necessary to investigate redirects, **but the code then marked a stored image broken on 403/404, network error, or 200 HTML even if the final request URL had become a *different historical photograph*.** The independent `proofKind()` accepted those misattributed classifications. Unlike the stricter existing HTTP-200 undecodable-image branch, the other failure branches did not require `network_final_identity_verified:true`.

**Pre-fix synthetic reproduction:** source `https://www.history.uscg.mil/Portals/6/example.jpg`, `currentSrc` the same, CDP final URL `https://redirector.example.net/other-photograph.jpg`, `url_aliases=[source]`, `status:404`, `complete:true`, `naturalWidth:0` generated `confirmed_broken_in_probe_browser` and census `broken` even though the final image was identity-unverified. Equivalent false positives existed for network errors and 200 HTML error responses. These are **synthetic fixtures**, not actual Final Vestige visitor observations.

**Correction:** Require exact `currentSrc` ↔ final CDP network source identity and no unresolved redirected identity **for all browser failure kinds**. Independently enforce the same gate in the census instead of trusting a reported failure flag. This is deliberately fail-closed: a real failed visitor image redirected to an unrelated final URL becomes `redirected_image_identity_unverified` pending browser screenshot/source attribution. Direct source 403/404, network errors, 200 HTML bodies, and 200/undecodable images remain countable when exact CDP identity is established.

## Test evidence

- `78c3e5f3e509199b7bd463fc0b14d9122545e984`: `browser_probe_core.cjs` fix, blob `c994a70182340800ec4b9ae556dc257fb454a8e3`.
- `52982a358a0ecf4d92327383f3ce5caa6b97350b`: `image_census_coverage_core.cjs` fix, blob `e7e30a5baa7d78341aa827166e7e2be6d71adbd3`.
- `33e3b6964e3c45a49fa534589bf042cb9db684ae`: update pre-existing redirect test expectation.
- `a3871f0fe9e5f570b0f2788cec637e12f1402c78`: new `test_redirect_failure_identity_20261101.cjs` with **20** targeted synthetic regression cases.
- `ef7db7d4babb1aba4b819221740c69764a744b84`: machine-readable, method-qualified URL/source audit.

**Postcommit source readback:** **74/74** tests passed in isolated V8 with Node's URL/assert/test compatibility shims: 20 new redirect tests, 12 existing browser-core, 18 existing image-census, 24 existing decode-census cases. Replayed exact GitHub blobs, not local approximations. **Native Node CI and a real logged-out Chrome/CDP crawl were not run.**

## New independent source observations — method matters

Machine ledger: [redirect_failure_skyway_source_audit_20261101.json](../qa/media-recovery/redirect_failure_skyway_source_audit_20261101.json).

| Source and article image | Independent web retriever observation | Guest browser/origin status |
| --- | --- | --- |
| [287:5 old St Pete Catalyst Skyway photo](https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg) | Retriever **404** | **Unknown**, not confirmed visitor failure |
| [287:5 publisher-relocated photo](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg) | Image **displayed** | **Unknown**, no verified transfer bytes |
| [418:2 Coast Guard debris photo](https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg) | Retriever **403** | **Unknown**, not confirmed visitor failure |

Publisher's [April 10, 2020 article](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/) identifies the Skyway photograph as **May 9, 1980 collision aftermath** and credits **University Press of Florida**. The existing stored ALT says the image shows the old wreckage **and the later bridge replacement**. A photograph made at the 1980 wreckage scene does **not** establish the replacement bridge opened in 1987. This is an editorial/visual-identity review item; do **not** automatically replace the live image or rewrite its ALT without editor confirmation.

A new cataloged **alternative composition** better fitting the “old and new bridges” description exists: [Florida Memory item 131903](https://www.floridamemory.com/items/show/131903), H. Milo Stewart, **1987**. [Commons file record](https://commons.wikimedia.org/wiki/File:View_of_the_old_and_new_Sunshine_Skyway_bridges_from_St._Petersburg,_Florida,_1987.jpg) records **600×595** original JPEG, **46 KB** file size, tagged **CC0**. That is a **different historical photograph** and changing to it is an editorial decision, not a same-image file recovery. Florida Memory's primary page returned a retriever 403, so item-specific license validation is **HOLD**. No upscale; target **600×595** rather than 960 wide. Neither publisher photo nor archival alternative is authorized for caching/uploads yet.

## Safe release path

1. Site QA #154 independently captures logged-out desktop/mobile `currentSrc`, final CDP request URL + aliases, status/MIME/error, zero-width decode and screenshot for **285:5, 287:5, 407:1, 418:1–2**. An alias-only 404 is *unresolved*, not a proven same-source failure.
2. Match the exact historical photograph and framing; verify legal reproduction permission and required credits per item, plus binary SHA-256. The 1987 bridge alternative requires explicit editorial scene-change approval. Build at most 960px wide, no upscaling; cache only rights-cleared exact assets into WP media under a separately approved workflow.
3. Verify responsive variants and visual parity, then compare equivalent uncached browser transfer bytes/LCP/CLS. A source's original storage size does not measure visitor delivery. **42 claimed broken remain unverified; 76% claimed reduction unmeasured; 13 oversized WP originals are only stored-file evidence.**

No third-party binaries fetched or republished; no WordPress production write, unlicensed scraping, homepage design work, Site QA PR #154 code changes, or spend.
