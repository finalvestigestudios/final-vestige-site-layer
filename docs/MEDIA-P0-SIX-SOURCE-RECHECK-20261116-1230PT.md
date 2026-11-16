# FV Media Recovery — Six P0 Source Recheck (2026-11-16 ~12:30 PT)

## Evidence method, not a visitor outage claim
Rechecked all six highest-priority historical image **authored-origin** routes with an independent PUBLIC WEB RETRIEVER. All six generated *retriever-level* errors, **not authenticated origin HTTP responses or logged-out browser errors**. In particular 407:1's 400 is a content-type rejection, and 285:2's 500 is a redirect tool-access failure. None establishes a visitor-broken image on FinalVestige.com; the actual displayed URL is a Jetpack proxy for every slot. See the exact stored and proxy URLs in `p0_reader_matrix_20261116_1230pt.json`.

| P0 slot | Retriever source observation | Alternative independently displayed | Reuse disposition |
|---|---|---|---|
| 285:5 — Three Mile Island movie | 404 from retriever | None verified | Private publisher source; HOLD |
| 285:2 — TMI NRC figure at UCS | 500 redirect tool inaccessible | Related Commons derivative previously identified, NOT same annotated figure | HOLD |
| 287:5 — Skyway | 404 from retriever | same-publisher `media.stpetecatalyst.com` route | University Press of Florida/private rights; HOLD |
| 418:1 — Scotch Cap official portrait | 403 from retriever | No alternate binary verified | USCG gallery marks item public domain; exact URL, SHA/crop/review pending |
| 418:2 — Scotch Cap debris | 403 from retriever | Coast Guard Museum 600×463 *filename-indicated preview* | No upscale; master and rights HOLD |
| 407:1 — Hebgen scarp | 400 unsupported binary content-type from retriever | USGS separate official catalog Original | USGS PD/J. R. Stacy; binary/frame HOLD |

The only alternatives displayed **in this run** were 287:5, 418:2, and 407:1. The official USGS catalog identifies public-domain status. Public reader output is distinct from `response.status` in guest Chrome.

## Release and measurement gates
Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns existing browser collection; **do not build another browser collector**. For each image record `currentSrc`, redirect chain, logged-out browser network GET status, MIME, decode/naturalWidth, viewport screenshot, actual CDP `encodedDataLength`, cache mode and WP revision. The six-P0 existing staging gate in [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183) must remain HOLD until those facts plus frame/crop and item rights signoff exist.

Any approved derivative must be <=960px wide, retain aspect ratio, and never upscale a 600px or 604px preview. Require copyright/PD item record, author credit, source URL, pixel/frame comparison, binary SHA-256, isolated WordPress Media staging with stable URL/ALT/caption, screenshot checks and rollback. **No new rights to commercial imagery are inferred.** No caching, downloads, post rewrites, production writes or spending authorized.

Historical 61 posts/355 refs and later 66/361 are distinct. The reported 42 breaks remain unconfirmed by browser, the claimed 76% wire savings unmeasured. The 20 original media files above 1.5MB total 64,385,752 *stored* bytes, not transferred bytes.

## Offline test
```sh
node --test qa/media-recovery/test_verify_p0_reader_matrix_20261116.cjs
node qa/media-recovery/verify_p0_reader_matrix_20261116.cjs qa/media-recovery/p0_reader_matrix_20261116_1230pt.json qa/media-recovery/p0_source_pin_projection_20261116.json
```
The pin projection is a small exact-field copy of six rows from the existing #183 manifest (blob `93ed6631518dc0c06253719b61d1cf50b623f6f0`), crosschecked against the genuine upstream manifest when authored, *not* an independently collected browser snapshot. Tests reject false HTTP status, invented transfer bytes, pretend visual/rights clearance, unsupported source mutations, excessive sizing and production authorization.
