# P0 Image MIME evidence integrity correction — November 13, 2026

Draft PR #1703 only; no deployment, WordPress changes, image downloads, cache, third-party scraping, homepage visual work or spend. Site QA #154 owns the existing guest-Chrome collector.

## Defect proven on exact prior source
Previous code blob `70c1366fbdf423fab312d977d728d52865907a12` had an accidental embedded source declaration inside each MIME token character class. Thus a synthetic P0 404 record reporting `te xt/html`, `text/ht ml`, `te>xt/html` or `text/h=tml` was accepted as valid MIME, even though those are not valid media types. The validator could admit corrupted response metadata as a guest failure. This is an **offline intake defect**, not evidence of a production broken image.

## Safe correction and validation
The fixed type/subtype grammar rejects whitespace, operators, controls and MIME values longer than 256 characters. A valid HTML MIME for an HTTP 404 remains eligible for *failure review only*, and a valid decoded JPEG HTTP 200 remains a keep-original outcome. Eight new targeted synthetic decisions were executed in isolated V8: **8/8 PASS**. Existing regression suite is extended, but the complete revised suite, native Node, CI, browser capture and screenshot-byte review are **not** claimed as executed this sprint.

## Evidence and restoration boundaries
Machine audit: `qa/media-recovery/p0_mime_token_integrity_six_20261113.json`, six actual stored URLs plus candidate catalog links, external retriever wrapper codes and **null true guest statuses and transfer bytes**. The historical 61/355/288 inventory remains separate from newer 66/361 coverage. Forty-two reportedly broken URLs remain unconfirmed by visitor browser. Fifteen WordPress originals >1.5 decimal MB total 47,096,779 *stored* bytes, of which eleven inline-used originals total 38,480,915 stored bytes. The claimed 76% transfer reduction is still unmeasured.

The only appropriate path is Site QA #154's uncached browser provenance → exact-photo and source-master byte checks → item-specific rights and attribution review (Coast Guard public domain guidance requires credit and additional restrictions; commercial publisher relocation does not grant rehosting rights) → max 960px/no-upscale and actual-DPR screenshot parity → reversible staging proposal. No automatic rewrites or production writes.

Official primary-source check: https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/ identifies 418:1 subject, credit and public-domain/reuse conditions; this **does not confirm its source loads in a visitor browser**. The Coast Guard historical Scotch Cap article https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/ helps editorial scene comparison, not a blanket license.

Site QA handoff: do not duplicate collector or replace 407:1 merely because web retriever rejects binary. The USGS Original link points to the published 407:1 image. Preserve until actual guest failures.
