# Media Recovery — Offline acceptance gate for Site QA guest-browser P0 images

**2026-11-16 / Draft QA, not a production fix.** This addition is an offline consumer for Site QA #154's existing logged-out Chromium capture, **not another collector**. It makes no network calls, downloads, media copies, WordPress writes, homepage changes, Gutenberg block rewrites, or rights determinations.

## The six P0 subjects

The existing machine-readable \`qa/media-recovery/p0_reader_matrix_20261116_1230pt.json\` (Git blob \`60a23c53ea573e986f3b85ced134abfecbdc5fd9\`) is the sole source of authored and Jetpack exact URLs. Its rows document \`285:5\` SayMedia Three Mile Island movie still, \`285:2\` UCS Three Mile Island control panel, \`287:5\` St Pete Catalyst Sunshine Skyway, \`418:1\` Coast Guard portrait, \`418:2\` Coast Guard museum debris and \`407:1\` USGS Hebgen Lake. **Web-retriever tool response codes are NOT actual guest-Chromium HTTP statuses.** The previous 404/403/500/400 retriever outcomes must not be presented as browser failures.

Run from the repository root:

\`\`\`bash
node --check qa/media-recovery/evaluate_guest_image_evidence.cjs
node --test qa/media-recovery/test_evaluate_guest_image_evidence.cjs
node qa/media-recovery/evaluate_guest_image_evidence.cjs qa/media-recovery/p0_reader_matrix_20261116_1230pt.json
node qa/media-recovery/evaluate_guest_image_evidence.cjs qa/media-recovery/p0_reader_matrix_20261116_1230pt.json /private/site-qa-p0.json > /private/p0-assessed.json
\`\`\`

With no capture, every slot is \`UNOBSERVED\`; the evaluator asserts neither the reported 42 broken images nor any measured 76% savings.

## Existing collector data interface

Input is an exported, privacy-redacted local JSON object. The following schema is **illustrative only**, with deliberately null measurements and placeholders, and **must not be treated as a genuine observation**:

\`\`\`json
{
  "schema": "fv-siteqa-guest-image-evidence-v1",
  "environment": {
    "browser": "chromium",
    "session": "logged_out",
    "collector": "Site QA #154",
    "cache": "disabled",
    "captured_at_utc": "2026-11-16T23:31:33Z"
  },
  "slots": [{
    "key": "285:5",
    "post_url": "<exact pinned post_url>",
    "current_src": "<observed img.currentSrc>",
    "complete": null,
    "natural_width": null,
    "natural_height": null,
    "decode_succeeded": null,
    "request": {
      "url": "<matching observed network request URL>",
      "http_status": null,
      "mime_type": null,
      "wire_bytes": null,
      "from_cache": false,
      "network_error": null
    }
  }]
}
\`\`\`

Do not commit capture exports containing cookies, authentication headers, sensitive query strings, HAR response bodies, or identifying browsing data. The evaluator accepts only the six known keys and expected post/Jetpack-image identities, allows Jetpack i0/i1/i2/i3 and a limited set of resize options, and returns \`SOURCE_DRIFT_REVIEW\` for different images or mismatched network URLs. It rejects cache-unknown wire byte claims, out-of-range statuses, invalid natural dimensions, duplicate keys and unsupported provenance metadata.

\`CAPTURE_REPORTS_RENDERED\` requires observed 2xx, \`image/*\` MIME, completed load, positive natural dimensions and successful decode. \`CAPTURE_REPORTS_BROKEN\` requires a completed zero-dimension decode failure and a network failure or undecodable 2xx body. A bare 404 without image decode evidence remains \`CAPTURE_REPORTS_TRANSPORT_FAILURE_DECODE_UNKNOWN\`. Evaluator results are labelled \`COLLECTOR_SUPPLIED_UNINDEPENDENTLY_VERIFIED\`; JSON self-identification is not independent proof of browser origin.

## Performance and replacement controls

Transfer bytes are counted only when recorded as nonnegative, cache-disabled, actual request wire bytes. Partial sums are labelled partial; the full six-image sample appears only when all six contain valid bytes. Even a complete six-image sample **cannot** substantiate a site-wide 76% reduction. That claim requires paired representative full-page browser experiments at matched viewport, page set, cache policy, device and network conditions:

\`100 × (1 − Σ after image wire bytes / Σ before image wire bytes)\`

Never substitute WordPress storage metadata as if it were network transfer. Keep the historical 61-post/355-inline-image census distinct from later 66-post coverage, the unconfirmed 42-source-failure report and the 20 >1.5MB stored originals (64,385,752 stored bytes).

Any future replacement still needs visual same-frame/crop identification, authoritative catalog custody (Navy, Coast Guard, USGS, Florida Memory, archives), item-level publication rights and credit, original dimensions and proportional max width \`min(960, verified native width)\`. Do not upscale the Scotch Cap 600×463 preview or 604×590 TMI derivative. Only a separately approved, reversible WordPress-media proposal with tested responsive \`srcset\`/\`sizes\`, ALT, caption and rollback could proceed; **this script never authorizes a production write**.

Site QA #154 retains browser collection. Media QA #2747 owns this offline gate and all rights/replacement reviews; no collector or existing draft is duplicated.
