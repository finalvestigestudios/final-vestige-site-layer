# Article-image wire-byte attribution — October 31, 2026

**Scope:** Media Recovery draft PR #183 only. No homepage visual-design files, Site QA PR #154 classifier, WordPress production content, image originals, source archives or costs are changed.

## Reproduced measurement error (synthetic, not a live-site finding)

The previous `compare_wire_core.cjs` counted every CDP `Network` Image response as article image weight. That includes site chrome, logos and unrelated widgets, even when no stored article image references those requests. Consequently two valid browser reports could falsely show major “article image weight reduction” when an unrelated navigation image disappeared while the article's historical photographs remained unchanged.

A reproducible example has **two actual article images at 5,000 encoded bytes each in both runs**; before additionally downloads a 50,000-byte page-chrome PNG, while after does not. The previous method would compare 60,000 against 10,000 bytes and report **83.33%** “image savings.” The corrected **article-image metric is 10,000 versus 10,000: 0%**. These are synthetic fixture bytes, not FinalVestige.com transfers.

## Isolation and exact identity requirements

`browser_probe_core.cjs::scopeArticleImageWire` now attributes each network request **once**, regardless of how many historical image slots reuse the same URL, only when:

1. The request's final URL matches the browser-decoded `currentSrc` using the existing conservative image-identity rules; and
2. The request URL or an established redirect alias corresponds to that classified slot's request URL.

A redirect alias **by itself** cannot make a final URL depicting a different historical photograph pass. Wikimedia Commons hashed originals and same-photo Jetpack resizes remain eligible under existing identity rules. Two independently observed requests for the same photo count twice because two transfers actually occurred. Missing encoded-byte evidence for an article-linked request produces a **null** attributed total, never a guessed zero.

The browser JSON now records *separate* fields:

- `image_wire_bytes_total`: all network `Image` response bytes, including page chrome. Retained for diagnostic visibility and existing all-image consistency checks.
- `article_image_wire_bytes_total`: measured bytes of network requests attributable to image slots in published article content.
- `unattributed_image_wire_bytes_total`: measured network image bytes not conservatively attributable to stored article slots.
- `matched_article_network_requests` and `unmeasured_article_network_requests`: transparent attribution coverage.

The offline pair comparator **recalculates** attribution from each report's stored slots, rendered `currentSrc` and actual image network records. It rejects missing or inconsistent `article_image_wire_bytes_total` as `NOT_COMPARABLE` with reason `article_wire_scope_mismatch:POST`. Old reports lacking the new field must be re-captured with the updated runner; never fill the field manually to force a saving. The pair's `before_image_wire_bytes`, `after_image_wire_bytes` and reduction percentage now represent **article-attributed requests**, not all-page Image responses. Each per-post result additionally reports contextual all-image and unattributed totals.

The comparator's existing gates still require complete scroll coverage, exact photo-slot source and alt continuity, loaded images, valid requests, no cache/service-worker delivery, exact same page set/viewport/browser, and real network byte counts. Replacing a broken photograph is an **availability repair**, not automatically a compression saving.

## Verification and limits

Committed changes: `browser_probe_core.cjs`, `browser_probe_chrome.cjs`, `compare_wire_core.cjs`, `test_compare_wire.cjs`, new `test_article_wire_scope_20261031.cjs`.

**43/43 synthetic tests passed** against exact source read back from the draft GitHub branch in isolated JavaScript V8, using a minimal URL/URLSearchParams compatibility shim. Source syntax checks passed. Native Node CI and a real logged-out Chrome audit have **not** been run. New adversarial cases cover unrelated page-chrome savings, duplicate DOM photo usage, multiple distinct network requests, false redirect aliases, Commons/Jetpack identity, null bytes and fabricated article-only totals.

Network reachability checked independently on October 31: `https://finalvestige.com/`, `https://www.google.com/robots.txt`, `https://upload.wikimedia.org/wikipedia/commons/4/4a/Commons-logo.svg` all produced environment-level DNS-resolution errors `[Errno -3] Temporary failure in name resolution` from local Python urllib. **No actual HTTP statuses were obtained**; this is not an inference that the public website or sources are broken.

## Required next measurement

From an external network-enabled logged-out Chromium environment, run:

```sh
node --test qa/media-recovery/test_compare_wire.cjs qa/media-recovery/test_article_wire_scope_20261031.cjs
node qa/media-recovery/browser_probe_chrome.cjs --plan
node qa/media-recovery/browser_probe_chrome.cjs
# After an independently authorized, rights-cleared performance change, capture the same pages/viewport again:
node qa/media-recovery/compare_wire_runs.cjs before.json after.json
```

For the 36 offsite P0 slots, capture final URL, redirect chain, actual HTTP response/MIME, decoded image width, screenshot evidence and transferred bytes before concluding which of the alleged **42** are truly missing. The previously stated **76% reduction remains unverified**. All proposed archival replacements remain individual-asset, copyright, attribution, visual identity, ≤960px/no-upscale and explicit WordPress release gates. No articles, media binaries or production settings were modified.
