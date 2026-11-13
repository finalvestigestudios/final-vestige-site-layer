# Media recovery: 286 vs 288 frozen external-origin reconciliation (2026-11-13)

**Isolated draft, NOT a site change.** Read `docs/IMAGE-WEIGHT-WORKLIST.md` on PR #183 (blob `2acd06a4ca4317646006eb6591face3fe76fedec`) and reviewed Site QA #154. This finding concerns the **same frozen Oct. 30 cohort**, not the expanded 66-post census.

## Evidence and exact accounting

Cross-joined Site QA #154 `qa/media/cms_image_census_20261030.csv` (Git blob `76aa63ffaa299a6e6878edc1b66e637fa6f058ab`) with all eight JSON `qa/media-recovery/parts/01.json … 08.json` from PR #183. **All 61 post IDs and all 355 image counts agree. 59 of 61 per-post offsite counts agree.** Only these two rows differ:

| Post | Site QA external | Media Recovery external | Strong source-count divergence lead |
| --- | ---: | ---: | --- |
| 291 (Teton Dam) | 5/6 | 6/6 | `291:0` `https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1` |
| 285 (Three Mile Island) | 5/6 | 6/6 | `285:1` `https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1` |

Both use `i0.wp.com` as a **proxy for an external site's image**, not a proxy for `finalvestige.com`. All other five stored image URLs in each post are externally hosted. Consequently the 288 offsite ledger decomposes into **170 generic external + 118 Wikimedia redirects**, plus **60 first-party and seven Final Vestige-owned Jetpack proxy images = 355**. The site QA CSV's 286 is two lower. Site QA's committed classifier already correctly requires `i0.wp.com/finalvestige.com/...` for a **first-party** proxy, so **do not assert a code defect in that classifier**. The original unpublished source input / counting path is unavailable, so the reason for the CSV's two discrepancies is **strongly suggested, not conclusively proved**.

## Archival/rights distinctions

- Teton `291:0`: [National Archives' official Teton Dam post](https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/) is an authoritative research lead; it documents photographs from contractor Jerry Dursteller, not necessarily federal-employee-created works. Exact image/crop match, native resolution and permission to rehost this image remain unverified. A government website or CDN proxy does not automatically grant public-domain status.
- TMI `285:1`: `www.squawkpoint.com` is an external publisher, even though Jetpack proxies its file. No exact-photo public-domain alternate, license or rehosting rights were established. Do not substitute an unrelated DOE/NRC facility photograph for the control-center scene.

**All 12 original frozen URLs** are preserved verbatim in [the machine-readable reconciliation](../qa/media-recovery/siteqa_286_288_proxy_reconciliation_20261113.json). The [fail-closed validator](../qa/media-recovery/validate_siteqa_proxy_reconciliation_20261113.cjs) and [15 adversarial/control cases](../qa/media-recovery/test_siteqa_proxy_reconciliation_20261113.cjs) check host/tenant distinction, slot custody, archive counts, unknown guest statuses, no licensing bypass, and conditional 960px limit. Native Node v22.16.0: **15/15 PASS** on Git-blob-identical JSON/validator/tests; full CI/Chrome unrun.

## Browser restoration and performance release gates

**Site QA #154 exclusively owns its existing visitor Chrome queue**, `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. This reconciliation adds no collector and does not change that order. If `285:1` or `291:0` is later investigated, collect independently observed request ID, `currentSrc`, redirect chain, complete uncached request lifecycle, status, `naturalWidth`/`naturalHeight`, actual transfer bytes, CSS display width and DPR. Failed retriever wrappers or unknown cache provenance must remain **HOLD**, not counted as 404s.

For a source-identity-preserving 960px derivative, require editor and rights signoff, pixel/scene/crop comparison, no upscale, attribution, responsive CSS×DPR checks and a zoom path for maps. A 960px file reaches one source pixel per physical pixel only at CSS width ≤ 960px/DPR. Native source dimensions and candidate output dimensions for these two files are **unknown**; do not guess a 960×height value.

WordPress caching plan, **not an upload authorization**: after proven browser failure and item-level rights clearance, acquire an authorized master, record source/copyright/credit and cryptographic hash, generate ≤960px non-upscaled derivative with explicit dimensions and ALT/caption, preview in reversible staging, compare original and staged article visual integrity, and only then submit a narrowly scoped production approval. No automatic mirroring or Gutenberg block rewrite.

The requested 76% reduction is **not measured**. Calculate `100 × (1 - Σ(candidate cold actual image wire bytes) / Σ(baseline cold actual image wire bytes))` only for identical paired image slots under the same conditions and explicit cache-miss provenance; do not substitute stored-original byte counts or mix image changes with compression. Separate 15 WordPress originals above 1.5 decimal MB (47,096,779 stored bytes) and the 11 inline-matched originals (38,480,915 stored bytes) from actual visitor transfers.

No image binaries were downloaded, cached, or uploaded; no WordPress/public-page writes, homepage design modifications, merges, deployments or paid service calls. All real guest HTTP statuses for these rows remain **null**. The historical 42 reported failures remain **guest-unconfirmed**, not newly fixed.
