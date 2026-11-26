# Nine-post external-image crosspost: safe triage, November 17, 2026

**Method:** offline re-projection of **nine existing authenticated WordPress EDIT/VIEW image audits**, not a fresh WordPress or guest-browser call. Site QA [PR #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns the existing Chromium/CDP collector; no competing collector.

**Verified crosspost result:** 56 externally sourced published image slots; **52 Jetpack-markup paths / 4 direct third-party routes**. **51/56** lack explicit paired width and height in the captured VIEW markup (not measured CLS). **47** have previous catalog *leads*, NOT an approved replacement binary or rights clearance. Browser `currentSrc`, GET HTTP status, MIME, decode, screenshot and transfer bytes **all unknown**. No independently verified visitor-broken images.

| Slot | Direct published external image URL | Status |
|---|---|---|
| 292:2 | [images.pubble.cloud](https://images.pubble.cloud/worker/jpg/quick/1920/3077598/96897487/content/2024/6/cf6d9b51-c16b-4938-800c-833b86ac5740) | Guest browser not measured; HOLD |
| 290:2 | [upload.wikimedia.org](https://upload.wikimedia.org/wikipedia/commons/3/32/Camp_Century_trench_deformation.png) | Guest browser not measured; HOLD |
| 291:3 | [brightspotcdn.byui.edu](https://brightspotcdn.byui.edu/dims4/default/37ddf06/2147483647/strip/true/crop/2048x1365+0+0/resize/1200x800!/quality/90/?url=https%3A%2F%2Fk3-prod-byuifulbrightspot.s3.us-west-2.amazonaws.com%2Fbrightspot%2F33%2F7d%2F67f04f174772ab1d35419706138c%2Fteton-dam-flooding-aerial.jpg) | Guest browser not measured; HOLD |
| 285:3 | [i.insider.com](https://i.insider.com/5d5eb5f754c75f23dc72ed4c?auto=webp&format=jpeg&width=800) | Guest browser not measured; HOLD |

Existing six P0 suspected failures **285:5, 285:2, 287:5, 418:1, 418:2, 407:1** come first. These four direct sources are second-tier checks. 290:2 is a directly served public-domain **Army Camp Century** diagram; direct delivery itself does not imply breakage. [The official 1964 Army report-derived catalog](https://commons.wikimedia.org/wiki/File:Camp_Century_trench_deformation.png) lists 1,573×1,132; a proportional optional 960×691 version is possible without upscaling, but no download/rehosting is approved.

**Reproducibility:** each row has exact authored and published markup URLs, pin to its source Git blob and original WordPress revision. An offline fail-closed validator and **21 Node-compatible tests** (baseline plus 20 adversarial cases) reject invented HTTP/bytes, 42/76% claims, SHA drift, proxy misclassification, rights clearance, upscaling and writes. The equivalent logic and mutations passed in isolated V8; **native Node/CI have not run**.

Historical **61 posts/355 inline image references** are distinct from this 9-post external subcohort and later 66-post reporting. Reported **42 broken** remain unconfirmed by guest browser, **76% visitor image-byte savings** remains unmeasured, and the **20 WordPress originals >1.5 MB total 64,385,752 stored bytes**, NOT browser transfers. After a real guest failure, stage only a same-scene/crop and rights/credit-reviewed primary-source candidate with verified SHA-256 and no-upscale max 960px; preserve source media URL and rollback. **No downloads, media rehosting, live WordPress writes, homepage design changes, Gutenberg rewrites, merges, deployments, or spending.**
