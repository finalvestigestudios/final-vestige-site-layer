# Final Vestige Media Recovery — default browser P0 coverage defect corrected
**Evidence date: 2026-11-01. Scope: isolated draft Media Recovery PR #183, no production writes.**

## Why this is a high-priority repair to the verification process

The existing `qa/media-recovery/browser_probe_chrome.cjs` default run selected only article IDs `268,432,418,407,434,621`. It **omitted article 285 (Three Mile Island)** and **article 287 (Sunshine Skyway)** despite those two articles containing the leading independent-retriever 404 investigations. Consequently, the browser command recommended in the runbook could finish without checking either of the highest-priority missing-image reports. It was not legitimate to infer that Site QA had independently checked those sources from a successful default probe.

**The default `--plan` and actual Chrome runner are now tied to a strictly validated source queue, rather than a stale six-ID constant.** New default article order is **285, 287, 407, 418, 268, 432, 434, 621** (eight pages). These cover **55/355 stored inline image references**, including all **ten** existing P0 audited source slots plus **287:5**. The full `--all` mode still covers 61 articles / 355 stored slots.

The 11 specifically prioritized stored-image keys are `285:5`, `287:5`, `407:1`, `418:1`, `418:2`, `285:0`, `407:3`, `268:8`, `268:4`, `285:2`, `418:0`. The mapping includes exact original published URLs and ALT text, not invented image replacements. The P0 page plan retains legacy investigative articles 432, 434 and 621; other images on the eight pages are not dropped.

## New code and machine-readable handoff

- `qa/media-recovery/probe_p0_queue_core.cjs`: fail-closed offline queue builder that checks an eight-part frozen WordPress census against all ten precise `p0_restoration_release_queue_20261101.json` entries and the exact Skyway 287:5 source. A missing slot, changed URL or ALT, unexpected release row, renamed/offsite post URL, duplicate, HTTP-only URL or unauthorized publication/caching gate causes a hard error **before** starting a guest-browser audit.
- `qa/media-recovery/browser_probe_chrome.cjs`: default `plan()` uses that audited queue. Its `--plan` output lists the actual targeted source URLs and ALT; the eventual browser report carries the priority keys so that a site verifier can see what was intended to be inspected. No changes to Media Recovery's separate HTTP/decode/redirect classifiers or Site QA #154 files.
- `qa/media-recovery/p0_browser_probe_coverage_20261101.json`: 11-row machine-readable record preserving each published source URL and prior **independent web retriever** observation, authoritative candidate source lead, reproduction-rights HOLD, conditional ≤960-pixel no-upscale geometry and explicit **null guest HTTP/decoded/transfer data**. A retriever wrapper 403/404 is **not** a confirmed visitor GET status.
- `qa/media-recovery/test_probe_p0_queue.cjs`: **18/18 native Node v22 tests passed**, including 16 deliberately corrupted or prohibited inputs. The locally executed core and test files were byte-identical to their GitHub blobs: core `40bb916870442ca1c18f2a89803df274659ca625`, tests `644652a20447a8c1ea82f55878702b1ddbc11114`. Syntax checks passed.
- Independent *full actual frozen corpus* replay of exact committed launcher/core with isolated V8 Node/URL compatibility shims: default eight pages / **55** image slots / **11** mapped priority keys, and `--all` 61/355. Launcher blob `73f70590e3615eea896aa8e9e547012875db3184`. **This was not a live Chrome network test.**

Run the safe no-network preflight first:

```sh
node --test qa/media-recovery/test_probe_p0_queue.cjs
node qa/media-recovery/browser_probe_chrome.cjs --plan
```

On a network-enabled, logged-out Chrome environment, run mobile and desktop without editing WordPress:

```sh
node qa/media-recovery/browser_probe_chrome.cjs
node qa/media-recovery/browser_probe_chrome.cjs --desktop
```

Collect exact `currentSrc`, original/final CDP Image GET, response status/MIME, encoded bytes, natural pixel size, full-height scroll proof and screenshots. Source URL / browser network identity and actual photo composition must remain distinct. If a queue URL changes legitimately, first refresh and approve audited source evidence; **do not bypass the error**.

## Historical, rights and performance safety

The Sunshine Skyway **287:5** old St Pete Catalyst URL was retriever-404; the publisher's relocated image was displayed independently but credited to **University Press of Florida**. No permission exists to rehost it. The source ALT also possibly misstates the later bridge replacement; this requires editorial review, not a silent Gutenberg rewrite. The other ten audited sources likewise retain individual archival identity and rights checks.

The overall figures remain **61 posts / 355 source slots / 288 external references / 13 WordPress originals >1.5 MiB**. Five featured/inline historical-reconstruction PNG masters without WordPress registered subsizes account for **13,267,538 source-storage bytes**; this is **not** measured browser weight. The reported **42 broken images remain unverified**, claimed **76% savings remain unmeasured**, and **production images repaired remain zero**. Neither a failed source viewer nor a partially complete trace may be counted as a proven outage or a compression benefit.

**No third-party image downloads/copies, WordPress writes, archive copyright shortcuts, homepage design changes, Site QA #154 draft changes or spending.** Independent Site QA owns actual guest browser acceptance; Media Recovery owns the source/rights map, safe target plan and any future individually approved caching/staging proposal.
