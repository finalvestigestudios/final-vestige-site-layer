# Article-image transfer evidence gate — 2026-11-01

Draft [Media Recovery PR #183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183), independent of [Site QA PR #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154). **Source-only. No WordPress writes or image downloads.**

## Concrete failure mode addressed
Previously `scopeArticleImageWire()` accepted any slot possessing matching `current_src` and `request_url`, even an ALT-only DOM guess, a slot whose original archival source did not match the decoded `currentSrc`, or a page with additional unmapped images. It also returned a partial positive total after silently omitting unresolved article images. Those totals could be mistaken for complete article-image transfer and contaminate attempts to substantiate the **76% claim**.

## Corrected protocol
An article-only encoded-wire total is numeric only if **every stored image slot** is `loaded_in_probe_browser`, mapped by exact stored-source URL/unique ALT after URL matching, has currentSrc identity verified and final nonredirected CDP image identity verified, and carries separate successful decoded/network proof. Every verified slot must match a fresh CDP Image response with positive encoded transfer bytes, 200 status, image MIME and no cache/service worker/network failure. One unresolved/ALT-only/broken image or missing request makes `article_bytes:null`, never a fabricated zero or partial saving.

Distinct genuine CDP requests for the same visible URL still count separately; two DOM references sharing one real request still count once. Unrelated page chrome is excluded. New fields `unverified_slot_count` and `unmatched_verified_slot_count` expose incomplete evidence. The strict paired before/after comparator now rejects any slot lacking exact DOM or separate final-CDP proof.

## Evidence and limitations
The frozen current-CMS inventory still indicates **61 posts / 355 stored image references / 288 offsite references / 13 original files >1.5 MiB**; two offsite-reference-count discrepancies with Site QA remain understood as classification/input differences, not browser failures. Site-wide **42 broken images unverified; 76% weight reduction unmeasured; production images repaired 0**. Original storage bytes and estimated 960px target sizes are not visitor encoded transfers.

**Synthetic test replay:** 52/52 focused cases across `test_article_wire_scope_20261031.cjs` and `test_compare_wire.cjs` passed with V8 URL/Node-assert compatibility shims against exact proposed source. **After committing, all 114/114 cases across seven existing and new browser/scope/compare test suites passed against GitHub source readback.** One older 200-image-MIME test had a stale expectation from the immediately preceding decode-failure fix; its expectation was corrected with a separate test-only commit `5f3d3aa6c84277749432891e7fb50133c368b75a`, without relaxing the safety gate. **Native Node CI and logged-out Chrome are still required.** Tests use synthetic example.edu/example.gov fixtures, not visitor observation.

## Site QA handoff
Continue existing logged-out desktop/mobile queue **285:5, 287:5, 407:1, 418:1–2**. When collecting actual broken-image evidence, preserve uncached CDP Image request, currentSrc, status, MIME, image decode width, request IDs, response bytes and screenshot. For weight claims additionally require a complete all-slots scan, separate true article image requests from site furniture, and pair same post/same viewport/same browser BEFORE and AFTER. Do not extrapolate a sample 76% reduction to 61 posts.

**Safety gates:** no third-party mirroring, altered Gutenberg blocks, guessed rights or asset substitutions, homepage visual design changes, or subscription spend.