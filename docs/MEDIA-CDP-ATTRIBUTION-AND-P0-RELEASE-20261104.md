# Media Recovery — CDP byte-delta attribution gate and six P0 source decisions (2026-11-04)

**Owner:** Media Recovery PR #183 only; not homepage visual design or Site QA PR #154. **Status:** source-only draft. No WordPress production changes, image downloads/rehosting, post-block rewrites or purchase.

## Concrete measurement defect and repair

The existing `weight_claim_pair_gate_20261102.cjs` could return `claim_76_percent_supported: true` when 61 pages and 355 inline image slots showed an 80% difference in reported cold-CDP bytes **even if not one image source changed and no optimization release was evidenced**. Real transferred bytes may genuinely vary for unchanged URLs due to CDN quality/rendition, third-party response changes or server-side optimization; the difference alone cannot substantiate a *causal source-replacement optimization claim*.

This sprint adds `qa/media-recovery/approved_wire_attribution_20261104.cjs` and integrates it into the existing comparator. The result retains `status:'MEASURED'` and the raw byte-savings percentage after all its existing 61/355, request-ID, browser condition and frozen-inventory gates pass. **But the public claim flag now remains false unless approved before/after image-source rewrites account for all measured savings.** To attribute saved bytes, the code groups network requests by exact decoded DOM slot keys (rather than unstable CDP request IDs across runs), proves unchanged slot groups transferred unchanged byte counts, rejects an approved/unapproved mixed shared request and requires exact group topology. Only changed groups supported by existing approval manifests contribute to optimization attribution. A legitimate same-URL CDN/server optimization requires a separately documented, versioned deployment-and-measurement attestation, not this source-replacement gate.

This intentionally prioritizes avoiding false marketing claims over accepting otherwise genuine but causally unverified optimization. All rights and publication approvals in synthetic tests are **fixtures**, not permission to publish.

## Verification and remaining limitations

**40/40 synthetic checks passed** against exact GitHub blob contents using isolated V8 CommonJS execution (32 existing weight-claim tests plus two new end-to-end cases, 8 independent attribution assertions). Tests specifically distinguish an unchanged-URL 80% measured delta (**claim denied**), all 355 source swaps with approved manifests (**synthetic claim eligible**), one changed URL plus unrelated 354-image savings (**claim denied**), NaN/partial request mapping, shared/duplicated slot attribution, missing page and negative savings.

Native Node CI, actual guest Chrome/CDP network measurements, signed release evidence and image rights/visual checks are **not** available in this runner. Production visitor repairs remain **zero**. No image binaries were fetched, resized or cached. The reported **42 visitor-broken originals** remain unverified; the quoted **76% transfer-weight improvement** is not measured or achieved.

## Six high-priority original-source URLs and safe candidate custody

[Machine-readable six-image P0 decision packet](../qa/media-recovery/p0_attribution_release_gate_20261104.json) reconciles the exact published URL, independent-tool observation (404/500/403/unsupported are **retriever-wrapper observations, not origin or visitor HTTP status**), independent archival record, rights/crop caveat and conditional no-upscale geometry for:
- **285:5** SayMedia transformed 16:9 crop; upstream publisher links a 2010 Commons creator original 819×614. The 16:9 rendition and full photo are not binary-identical by assumption; item rights/crop on HOLD.
- **285:2** UCS original moved host (`blog.ucsusa.org` → `blog.ucs.org`), exact replacement image rendition unknown, copyright HOLD.
- **287:5** St. Pete Catalyst old `/wp-content/uploads/` path vs current `media.stpetecatalyst.com/uploads/` same filename. Publisher credits University Press of Florida; copying is NOT authorized. Florida Memory 1987 bridge K894127, 600×595, is a **different scene**, not an automatic substitute.
- **418:1/2** USC​G historic photos; 418:1 VIRIN 210330-G-DE713-0002 in official gallery (public-domain/public-release designation, credit and DoD restrictions review); 418:2 museum preview 600×463, no upscaling or assumed crop match.
- **407:1** USGS J. R. Stacy 1959 scarp source and alternate official `/thumbnails/image/img7535.jpg` path. Intrinsic pixels, decoded MIME and exact binary identity unverified.

Each asset **remains HOLD** until Site QA's *existing* logged-out Chrome queue verifies original rendered `src/currentSrc`, final Image GET HTTP/MIME, DOM `naturalWidth/Height` / `decode()`, lazy-load scroll, screenshot, CDP encoded transfer bytes and CLS on mobile and desktop. No browser-status fields were invented; no Site QA code/drafts were changed.

Once broken **and** rights-cleared: stage an approved same-scene archival master, SHA-256 and attribution/caption record, no-upscale derivative `width=min(960,intrinsicWidth)` with proportional height, WebP/AVIF + fallback where supported, WordPress Media Library ID and candidate URL, before/after visual and actual CDP wire/CLS test, explicit production-release decision, rollback to prior URL. **No bulk caching/mirroring or risky Gutenberg rewrites.**

## Weight and storage accounting

Frozen source census: **61 posts, 355 inline images, 288 upstream/offsite references**. Thirteen WordPress original files individually exceed 1.5MiB, together **43,522,829 bytes in original storage**; only ten are associated with frozen inline slots. Five first-party 1672×941 PNG historical reconstructions (media 39–43; posts 34–38) have no registered WordPress subsizes and total **13,267,538 original-storage bytes**. Their conditional ≤960×540 output is **not** a measured wire-size reduction. Image-wire benchmark must use a cold, uncached, matched browser/device profile and actual CDP `Network.loadingFinished.encodedDataLength`; count shared requests once, and compare the same 61/355 cohort, at least three repeats for the separate sitewide evaluator. Distinguish inline image-transfer bytes from total page weight, image hosting bandwidth and traffic-weighted business impact.

## Exact repository provenance

- New attribution module: commit `267ca35fb9677bfe54c835f7a1cb20d74b33f01d`, blob `721441a1cd733afdbe89b338a4d4e60c7ae8f9a8`.
- New module tests: commit `e6257988d1312dc1e38a688690f7e15e7fb05db5`, blob `ca33e96ad789bedd524c640c90d4b9e950963779`.
- Comparator integration: commit `3de730909e9492fd0e986cf164f6b27addfd2f56`, blob `ba6030357b49245ac2ae4fe553bfbd614a582a2d`.
- Comparator regression cases: commit `a2c3556107ef9dd31d0e8cad7e2b049dcc82ea34`, blob `034b5bfe538356d06e3190db9dcd8c28712129bb`.
- Six-source P0 machine packet: commit `0fd95ef7aaa70bbe9859c42d5d7b8d8caff7dd73`.

**Site QA #154 owns browser proof; Media Recovery #183 owns rights-safe historical source custody and release-gate correctness.**
