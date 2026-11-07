# Scotch Cap source recovery: two image slots (2026-11-06)

**Scope:** Existing site media recovery draft PR #1228, not homepage visual design, the Site QA #154 collector, or WordPress production. The requested `docs/IMAGE-WEIGHT-WORKLIST.md` is absent on `main` and this branch (404 when fetched on 2026-11-06). Source inventory: original 61 posts/355 inline images; working 66 posts/361. The historical 42 broken and claimed 76% image transfer reduction **remain unverified**.

## Verified source details and precise roles

- **Post 418 image 1 — Anthony L. Pettit portrait**, currently `https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG`. The [official Coast Guard catalog](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) identifies VIRIN **210330-G-DE713-0002.JPG** as the service portrait of the chief petty officer and calls the photograph public domain, cleared for release. The gallery lists a 0.04 MB download; actual native pixel dimensions and exact original binary are not verified. A web-text retrieval of the stored URL produced a **wrapper 403**, not a browser HTTP status. Do not replace this portrait with a lighthouse debris image.
- **Post 418 image 2 — 1946 Scotch Cap debris from bluff**, currently `https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg`. A web-text retrieval returned **wrapper 403**, not evidence that browsers fail. The [National Coast Guard Museum's historical article](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) credits U.S. Coast Guard and labels the matching **debris2** photograph. Its *actual link on the article* [renders at 600×463](https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg). This is a same-filename-family visual candidate, **not established binary-identical** or reproduction-cleared. Do not artificially enlarge to 960px; the observed available preview is 600×463. Preserve 'taken from bluff after 1946 tsunami' attribution and do not substitute 1912/1940 pre-disaster lighthouse photos or separate 1946 debris views.
- The [Coast Guard's original 2021 history](https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/) identifies these as distinct subjects. Use **photograph dates/events**, not the 2021 article publication or 2023 Museum upload date, as image chronology.

## Evidence strength and rights

`wrapper_403` is **retriever-only**; live origin response, visitor HTTP, `complete`, `naturalWidth`, `currentSrc`, redirect chain, CORS behavior, and cold transfer bytes are **null**. Index/catalog text describes images but is not binary proof. Item-level Coast Guard gallery notice supports U.S.-government public domain of portrait, subject to DoD display/credit/no-endorsement guidance. A Museum-curated derivative credited to USCG is **not automatically cleared for mirroring**; verify underlying original and Museum-specific rights before any copying. Neither source should be hotlinked as an untested replacement.

## Staged, approval-only restoration path

1. Site QA #154 runs its **existing** logged-out guest-browser collector on article 418. Capture network request URL, redirect chain, status, `currentSrc`, `complete`, natural pixel size, content type and byte transfer, plus desktop/mobile screenshots and crop.
2. If **and only if** an image fails in the visitor browser, reconcile exact photo identity (portrait vs debris), rights/attribution, and original master quality. Try official publisher source first; treat Museum 600×463 only as a candidate. Do not substitute a different subject.
3. If rights and binaries clear, propose a **local WordPress Media Library asset staged outside production** with source record, creator/credit, descriptive ALT, caption and preserved full-resolution source link. Make an optimized responsive JPEG/WebP/AVIF preview of **min(960, native width)** with native aspect ratio, no upscaling; do not blur map/archival details. Respect original full-res access.
4. After explicit review and isolated backup, stage exactly one image slot at a time. Compare identical cold-cache viewport/network conditions, visual parity and document load/crop/CLS. Do **not** rewrite Gutenberg blocks wholesale.
5. No 76% saving assertion until the complete 61/66-post cohort passes the separately committed offline cold-wire comparison gate.

## Safe release state

**No WordPress production writes, image downloads, caching, image repairs, Site QA collector duplicate, homepage changes or subscription spend.** All candidate binaries, rights gates and browser fields remain held pending actual verification.

**GitHub implementation:** `qa/media-recovery/scotch_cap_two_primary_20261106.json`, `validate_scotch_cap_two_20261106.cjs`, `test_scotch_cap_two_20261106.cjs`. Test with `node --test qa/media-recovery/test_scotch_cap_two_20261106.cjs` and `node qa/media-recovery/validate_scotch_cap_two_20261106.cjs qa/media-recovery/scotch_cap_two_primary_20261106.json`.
