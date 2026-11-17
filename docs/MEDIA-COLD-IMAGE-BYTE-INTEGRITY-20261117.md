# Cold image-transfer accounting: reject no-body and zero-byte false savings

17 November 2026, 13:27 Pacific. Scope: isolated media QA only, not homepage visual design. Addendum to draft media recovery PR #2747; Site QA PR #154 remains the sole cold logged-out Chromium evidence collector. Worklist `docs/IMAGE-WEIGHT-WORKLIST.md` was read from historical media PR #183; it is not present on main or the current #2747 branch.

## Concrete bug and fix

Previously the offline 61-post parity checker accepted any 2xx status including HTTP 201 Created, 204 No Content and 206 Partial Content, and accepted `wire_bytes:0` as long as the collector set `decoded:true` and plausible dimensions. This could count a fabricated 100% bandwidth reduction even when no cold transfer was evidenced. It also could accept range requests with no complete range-byte ledger.

The corrected fail-closed assessor requires `http_status === 200` and positive safe-integer `wire_bytes` for each distinct cold image GET. This conservative gate is an *accounting eligibility rule*; it does not imply that all 206 responses are broken images. A legitimate image assembled from ranges must be assessed separately with a complete independently reviewed transfer ledger, not fed to this full-response gate. Existing same-URL/two-slot requests still count one actual GET, preserving two DOM slots. The shared-GET conflict test now uses a mismatching positive one-byte report to exercise its intended guard rather than the new zero-byte rejection.

Observed negative control: four new synthetic cases all incorrectly succeeded under the old assessor (**36 pass, 4 fail**); the patched code passed all **40 / 40** in isolated V8 with URL, crypto, Buffer, Node test/assert shims. **Native Node, full repository CI and real CDP replay not executed.** Fixture SHAs, screenshots and verified wire figures remain unknown. This patch neither deploys a release gate nor proves the claimed 76% site-wide reduction.

## Fresh direct-origin observations (public retriever, not guest browser)

- Scotch Cap portrait slot **418:1**: [Defense original](https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG) returned **403** to independent retriever. [USCG catalog](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) identifies a public-domain/cleared item; binary dimensions and exact crop still pending.
- Scotch Cap debris **418:2**: [old USCG Portals source](https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg) returned **403**; Museum's previously described preview is 600×463 and must not be upscaled; rights and frame still pending.
- Sunshine Skyway **287:5**: [old Catalyst origin](https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg) returned **404**; [new publisher media URL](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg) rendered in independent retriever, *not* a proven binary-identical image or cleared to reuse. Publisher credits University Press of Florida.
- Hebgen Lake **407:1**: [USGS S3 old source](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg) gave **public tool error 400: unsupported binary/octet-stream**; this is **not an origin HTTP 400**. USGS Public Domain / J. R. Stacy catalog candidate needs original/crop check.

Five public-retriever Jetpack proxy requests were inaccessible **without numeric HTTP**, so *all six* priority slots remain guest-browser-status unknown. Prior 285:2/285:5 source probes are kept in prior ledgers, not presented as fresh here. Exact URLs, outcomes and rights holds are in the adjacent machine audit. Other 42 alleged failures still need browser verification.

## Hold and restoration decision

No caching or WordPress media upload until Site QA #154 confirms guest breakage and request bytes, original/official candidate image is exact frame or editorially approved alternate, item-level reproduction rights/credit and SHA-256 are recorded, native dimensions are read, review derivatives have width ≤960px without upscaling, and a reversible nonproduction staging plan is approved. No media binaries were downloaded and no HTML catalog was passed as an image. The 20 >1.5 million byte stored WP originals total 64,385,752 **storage** bytes, not user transfer bytes. The historical 61/355 inventory must not be conflated with the later 66-post live set.
