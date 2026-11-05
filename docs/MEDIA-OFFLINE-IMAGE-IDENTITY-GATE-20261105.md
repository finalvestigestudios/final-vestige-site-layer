# Image recovery: offline visual identity gate — November 5, 2026

**Draft QA only; no homepage design, Site QA #154 collector, production WordPress writes, third-party media downloads, copying, caching or spend.** Media Recovery #183 retains provenance ownership.

## Current scope and accurate metrics

The latest read-only census in draft #1138 contains **66 published posts, 361 stored inline image slots, 294 offsite-origin references** (superseding the older #183 baseline 61/355/288). Oversized inventory #1160 identifies **13 WordPress originals >1.5 MiB totaling 43,522,829 stored bytes** — **not actual page-transfer weight**. Alleged **42 broken images remain visitor-browser UNVERIFIED**, claimed **76% wire reduction is UNMEASURED**, production images repaired **0**.

The [seven-row source/candidate ledger](../qa/media-recovery/visual_identity_priority_queue_20261105.json) preserves exact original URLs for Site QA's existing P0 285:5, 285:2, 287:5, 418:1, 418:2, 407:1 and the P1 Teton mismatch 291:2, mapping to CDC/NARA, Florida Memory, USCG and USGS catalog leads. Browser HTTP/decode/bytes remain null. Prior independent web-retriever wrapper 400/403/404/500 errors are **not** the origin HTTP status or logged-out visitor proof.

**Fresh primary-source recheck:** [USGS Hebgen scarp catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) names photographer **J. R. Stacy**, marks the item **Public Domain**, and its Original link resolves to the exact already published USGS S3 URL. The retrieval tool's unsupported binary/octet-stream 400 wrapper does **not** prove that this image is broken for site visitors. USCG/Florida Memory pages yielded retrieval-service 403, leaving item-specific provenance/rights/geometry unverified.

## Why this gate is new

Existing Site QA #154 owns real guest-browser/CDP evidence. Existing Media Recovery #183 owns original source/copyright mapping and cold-wire measurement. This additional **offline same-photograph visual-parity preflight** helps prevent an unrelated historical photo, silent crop, stretched 960px rendition or alpha loss from being falsely certified as a safe derivative.

The Python/Pillow script accepts **two already existing lawful local images only**, with explicit reviewer attestations that local processing rights PASS and both files were lawfully acquired. It rejects remote-file input, symlinks/traversal, excessive files/pixels, unsupported or animated formats, >960px width, upscaling, crop/stretch, gross grayscale/dHash mismatch and changed transparency. It computes SHA-256 for each local file, emits only machine-readable JSON to stdout and **never downloads, encodes, caches, uploads or publishes** any image. Even a positive VISUAL_SIMILARITY_REVIEW merely requests **manual review**; it does not establish that two historical photographs are identical, or grant copyright/rehost permission. The thresholds are heuristic, not archival identity proof.

Run the tests and the tool:

    python -m unittest discover -s qa/media-recovery -p 'test_offline_visual_identity_gate.py' -v
    python qa/media-recovery/offline_visual_identity_gate.py --root /approved/local/images --manifest /approved/local/manifest.json

Required JSON manifest fields: schema = fv-offline-visual-identity-gate-v1, image_key = 407:1, exact original_source_url and candidate_catalog_url, relative source_local_path and candidate_local_path, lawful_local_copies_attested = true, item_specific_rights_review = PASS, source_relationship = same_catalog_item or proposed_same_photo. These claims must be genuine, not inferred from example values. No currently audited P0 pair is approved for local processing; the ledger expressly records that all seven are on HOLD.

Results: exit 0 = VISUAL_SIMILARITY_REVIEW (NOT publication authorization), exit 1 = VISUAL_PARITY_FAILED, exit 2 = INPUT_REJECTED. All outputs preserve false release approval and null visitor status/transfer bytes. Subject-level substitutes (CDC aerial for Say Media aerial, Florida Memory bridge for Catalyst, unrelated NARA control room for UCS figure, or intentional Teton subject replacement) **must not be represented as the same photograph**.

## Release plan and measured savings

First Site QA #154 must establish an actual logged-out browser failure with full-scroll screenshot, currentSrc, natural dimensions, correct Image request and final HTTP/MIME. Then the archive owner reviews primary catalog item, ownership/attribution and processing/rehosting terms. Only after lawful local source and candidate exist, this preflight and human visual/ALT/caption checks may support a later *separately authorized* staged ≤960px derivative. Use a new cache-safe filename and reversible original-to-new media mapping; do not rewrite live Gutenberg blocks or WordPress settings here.

**A 76% improvement must be measured from matching, fully decoded, cold-CDP before/after image transfers:** 100 × [1 - SUM(candidate encodedDataLength)/SUM(baseline encodedDataLength)] for identical post/image/viewport coverage, no cache, no missing source failures. Stored originals do not measure transferred bytes. Until real complete traces exist, report the sitewide transfer reduction as NULL.

**Verification:** 20/20 native Python unittest cases passed locally against synthetic PNG/WebP, including wrong photo, crop/stretch, resizing, alpha, rights/symlinks/traversal and bad file guards. Full-repo CI and actual guest Chromium remain outstanding. Zero production images fixed; no image binaries or production media touched.
