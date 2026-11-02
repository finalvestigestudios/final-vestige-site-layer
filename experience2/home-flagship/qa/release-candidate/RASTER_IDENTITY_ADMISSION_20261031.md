# Archival raster identity gate — October 31, 2026
**Status: DRAFT / RELEASE HOLD.** Stacked on PR #278 at `beec9d17decf6cef32681f6ea3f0ca18fbddf9d3`. No production or WordPress changes.

## Reproduced defect
The prior `audit_image_payloads()` accepted HTTP 200 + `Content-Type: image/jpeg` + any nonempty body. An adversarial response containing `<html>not a historical image</html>`, served as `image/jpeg`, was reported PASS for all three archival sources. This is a defect in the *media payload audit*, not evidence that production imagery is corrupted. The separate browser naturalWidth check offers some protection but must not be confused with a trustworthy independent payload receipt.

## Exact scope
- Require plausible JPEG, PNG, RIFF/WebP or ISO-BMFF AVIF byte signatures, with matching allowed raster MIME. CDN-optimized encodings are recognized from response bytes, not by the original image URL's suffix.
- Reject mislabeled HTML, unsupported image formats (including SVG), truncated JPEG, damaged WebP RIFF sizes, and duplicate decoded payload digests appearing under different historical-source URLs. Retain existing HTTP status, URL-identity, byte limits and body-hash checks.
- Report the observed raster format next to each SHA-256. These remain **decoded response-body bytes**, not encoded network transfer size, original upload hashes, or proof of historical authenticity.
- Replace the old `not-a-real-image-fixture` success mock with embedded, distinct, genuine 2×2 WebP/JPEG/JPEG raster fixtures. The regression suite uses only the standard library at execution time; Pillow was used solely to generate fixture bytes.

## Verification
- Before patch: forged HTML-as-JPEG responses `PASS` (reproduced).
- After patch: `python -m unittest discover -v` in `experience2/home-flagship/qa/release-candidate`: **29/29 PASS** (18 media checks + 11 existing staging source checks), synthetic/offline only.
- GitHub new source blobs must equal locally tested `3dc09ea4e1990e8a508bd67f2a51fa1d69d298cd` (module) and `21540721e90b08f38ddc52d406bee537c8ea2691` (tests). Verify the exact PR HEAD before review.
- Unchanged: canonical 7-chapter markup and original archival-image paths, three art directions, Focus Fieldbook/Jetpack, 72 Margins, frozen PR #49, Apollo PR #158, editorial Mind/affiliate separation.

## Release gates remaining (all HOLD)
1. Start the actual complete seven-chapter page in a **free isolated WordPress Playground or local WordPress environment with Assembler** using the source-attested staging tools. WordPress.com Personal has no native staging clone; `vestigefinal-tezws.wpcomstaging.com` is not a separate stage. No Business-plan upgrade requested.
2. Re-run PR #252's exact-source Chromium gate at 7 widths / 4 interactions / 3 negative controls; #254 folio first-screen captures at 320/390/768/1440/1920 and 200% zoom. The current tool environment cannot retrieve the full Git checkout or run browser navigation, so neither is claimed.
3. Execute the private WordPress renderer, HTTP image-response audit, real bytes and browser decode, axe WCAG 2.2 AA, reduced-motion, keyboard, no-JS, Safari if available, and Lighthouse. No fabricated lab or field CWV results.
4. Review NASA Apollo, Franklin museum/Commons, and NYPL individual-item reproduction conditions and source authenticity independently. Raster magic and unique hashes **do not** constitute image-fingerprint or licensing signoff.
5. Get founder visual selection, hosted CI, independent exact-SHA QD and explicit release authorization. **No merge, deploy, publishing, production plugin upload, theme edit, or subscriber/database copy.**
