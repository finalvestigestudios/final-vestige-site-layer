# Media Recovery — source-provenance discrepancy and duplicate historical-image integrity (2026-11-04)

**Scope:** Nonproduction, read-only source-corpus reconciliation. No homepage visual-design work, media binaries, WordPress writes or unlicensed caching. Media Recovery [draft #183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183) owns the ledger; Site QA [draft #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns guest-browser outcomes.

## Source data / repeatability

Pinned October 30 authenticated CMS inventory: eight `qa/media-recovery/parts/{01..08}.json` blobs, with SHA hashes embedded in [census_reconciliation_and_duplicate_src_20261104.json](../qa/media-recovery/census_reconciliation_and_duplicate_src_20261104.json). Independent cross-PR comparison: Site QA #154 `qa/media/cms_image_census_20261030.csv` Git blob `76aa63ffaa299a6e6878edc1b66e637fa6f058ab`. These are **stored HTML source**, NOT a new CMS pull or browser measurement.

**61 articles, 355 HTML image references; 353 distinct exact source URLs.** Media Recovery breakdown: **60 direct first-party + 7 first-party Jetpack paths + 170 other external + 118 Commons redirect** = 288 external-origin refs. QA #154's per-post CSV totals **286**. All 61 post image reference counts agree; the entire +2 external difference occurs at exactly two slots:

- **285:1**, Three Mile Island: `https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1`. Upstream is `www.squawkpoint.com`, NOT Final Vestige. QA CSV 5, Media 6 offsite refs for post 285.
- **291:0**, Teton Dam: `https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1`. Upstream is `text-message.blogs.archives.gov`, NOT Final Vestige. QA CSV 5, Media 6 offsite refs for post 291.

Seven other `i0.wp.com` URLs really are under `/finalvestige.com/`. The intermediary `i0.wp.com` host is therefore **not sufficient** to decide ownership, permitted caching, or performance attribution. The historical reason the older QA CSV excluded two refs has **not** been proven (the current Site QA classifier already handles this path distinction correctly); do not claim a current Site QA software defect or independently confirmed live regression. Next refresh the CSV side by side from identical frozen post revisions before updating the headline metric.

## High-value visual-integrity finding: post 291 is using the same photo twice for distinct phases

**291:2 and 291:5** both contain EXACTLY
`https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG`.

They use different ALT descriptions:
- `291:2`: “Growing breach in Teton Dam during the final hour before collapse.”
- `291:5`: “Aftermath of the Teton Dam failure and downstream cleanup in Idaho.”

The same exact source URL cannot, without a responsive/runtime source rewrite, depict both a growing breach **and** downstream cleanup. **P1 suspected contradictory visual narrative.** Confirm the decoded `currentSrc`, full photo content and each caption/placement in real guest-browser screenshots before choosing which, if either, is wrong. Do **not** rewrite Gutenberg blocks or merely swap URLs based on a photo name.

Two documented subject-level alternatives are now mapped, neither claimed to be a binary match:
1. National Archives at Denver, RG 115, **NAID 28894684** (“Hole in dam embankment grows larger”), archival context: https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/ . Historical prebreach candidate for 291:2.
2. National Archives / Bureau of Reclamation **NAID 28894688**, captioned “Looking into the break in Teton Dam” **June 6, 1976** in the DPLA archival record: https://dp.la/item/0998c6830bca790f010e6ba5552ec4ec . Postfailure candidate for 291:5.

These are **separate** archival objects, not approved replacements. NAID 28894684 is described in the National Archives blog; the original catalog asset, actual dimensions, photographer and reuse terms must be obtained from lawful primary archival access before any derivative. NAID 28894688's caption is from the DPLA catalog which identifies NARA Denver as its partner; item provenance/copyright still require review. Both have **conditional ≤960px max width, no enlargement**, with proportional height **unknown** until an authorized master is verified.

## P2 repeated map: Mann Gulch

**213:2** and **213:6** use one exact NWCG/Federal S3 image:
`https://fs-prod-nwcg.s3.us-gov-west-1.amazonaws.com/s3fs-public/2023-11/sr-mg-historical-map-race-pg5.jpg?VersionId=E03fTtNlZbsFr8cZyXxAMTHZfT8wEb4p`.

One ALT describes fire progression, tools and survivors; the other emphasizes Wag Dodge's escape fire. These may legitimately refer to different features of a single map. Verify map labels and readability at mobile width, **do not infer that reuse itself is wrong**. A separate USDA Forest Service/NWCG 1993 escape-fire map (Commons catalog 2113×1690) is a **subject-level alternative** with conditional 960×768 derivative if reuse and legibility are independently cleared. See https://www.nwcg.gov/page/staff-ride-to-the-mann-gulch-fire . No master was downloaded.

## Browser, licensing and release gates

All values for actual HTTP responses, redirect hops, broken-image state, decoded `naturalWidth`, CDP transfer bytes, lab LCP, CLS are still **NULL** in this batch. 355 HTML slots and 353 distinct original URLs are **neither** 355 nor 353 proven network transfers: responsive runtime rewriting, browser cache and duplicate requests must be measured. Do not extrapolate the duplicate-source count into 76% savings.

Priorities: keep existing Site QA P0 browser queue **285:5 → 285:2 → 287:5 → 418:1/2 → 407:1**, then add **291:2/5 visual integrity P1** and **213:2/6 P2**. Investigate former without taking ownership of QA's existing scripts.

No download/caching/resize/WordPress write licensed or authorized. Staging sequence only after verified browser defect, subject-provenance/rights check, authenticated binary dimensions, ≤960px proportional derivative/no upscale, visual proof, rollback original URL map, explicit separate publication approval. The 13 >1.5 MiB WordPress originals represent **43,522,829 stored bytes**, not transferred page weight.

## Tests and isolation

[Pure reconciler](../qa/media-recovery/validate_census_reconciliation_20261104.cjs) and [12-case regression suite](../qa/media-recovery/test_census_reconciliation_20261104.cjs) run against frozen 61/355 data; they fail closed for invented HTTP success, forged ALTs, wrong intermediary ownership, fake wire savings, false rights/cache clearance, WordPress publication, wrong counts and missing slots. **12/12 exact GitHub-file assertions passed in an isolated V8 Node-compatible harness.** Actual Node checkout/CI and guest Chrome remain unrun; test's in-repo QA CSV is synthetically reconstructed for hermetic regression, and a separate read checked the real #154 CSV blob. For the full cross-PR integration run:

```sh
node qa/media-recovery/validate_census_reconciliation_20261104.cjs /absolute/path/to/qa154/cms_image_census_20261030.csv
node qa/media-recovery/test_census_reconciliation_20261104.cjs
```

**No production repairs or measured 76% reduction are claimed.**
