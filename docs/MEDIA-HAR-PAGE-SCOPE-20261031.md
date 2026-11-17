# HAR page-scope attribution guard — 2026-10-31

**Status:** isolated source-only change for Media Recovery PR #183; Site QA PR #154 and homepage visual-design lane untouched. **No visitor-browser run, WordPress write, image download, rights determination or measured compression claim.**

## Confirmed defect in offline triage

The earlier \`har_image_triage.cjs\` matched an image's URL anywhere in a supplied HAR without checking which **page/tab/navigation** originated that request. A HAR containing two article tabs requesting the same historical photograph could therefore associate a second tab's Image HTTP 404 with the article under investigation. A synthetic regression reproduces the wrong attribution, not an observed live-site failure.

This is different from the already fixed **Fetch/XHR masquerading as an Image** issue: here both requests can be genuine Image requests, but belong to different tabs. A URL match alone does not establish page ownership.

## New fail-closed CLI path

\`har_page_scope_core.cjs\` and \`reconcilePageScopedHar\` now require the supplied HAR to contain:

1. A valid \`log.pages\` array, unique nonempty page IDs, and **exactly one** page whose declared HTTPS title URL points to the audited FinalVestige.com article (query/fragment ignored).
2. A **GET Document** request tagged with that page's \`pageref\`, pointing to the article, reporting HTTP 2xx and \`text/html\` or \`application/xhtml+xml\`.
3. Image entries with the **same page's** \`pageref\`. Only these enter the pre-existing resource-type, exact-source-identity, status and MIME triage.

Requests belonging to other tabs/pages, or missing \`pageref\`, are excluded. Missing/ambiguous \`log.pages\`, duplicate IDs, a missing successful document load, or an unrelated document return zero attributable image statuses rather than an invented failure/success.

The command remains:

\`\`\`bash
node qa/media-recovery/har_image_triage.cjs \
  --har=/secure/local/logged-out-export.har \
  --post-id=268 \
  --out=/secure/local/archimedes-triage.json
\`\`\`

Review \`har_declared_article_scope_consistent\`, \`har_scope_status\`, \`scoped_har_entries\`, \`excluded_unscoped_har_entries\`, and \`findings[].har_observations\`. The HAR metadata is **self-reported**, so \`har_page_identity_verified\` deliberately remains \`false\`. HTTP codes are evidence only that the **supplied HAR** recorded a request; they are **not** independent logged-out Chrome verification, decoded pixels, or a confirmed broken image. Raw HAR files can contain cookies and authorization information; keep them local and private. A report does not include raw headers, cookies or response bodies.

A Chrome export without \`log.pages\` or image \`pageref\` is **not usable for page-scoped response conclusions**; capture an appropriate single-tab HAR or use the existing logged-out CDP browser probe. Avoid broadening this gate to guesses from referrer headers, filename matching, or copied screenshot pixels.

## Evidence and checks

- New pure module: \`qa/media-recovery/har_page_scope_core.cjs\`.
- New native Node tests: \`qa/media-recovery/test_har_page_scope_20261031.cjs\` — **14/14 passed locally** using Node v22.16.0, including mixed tabs, missing page metadata, duplicate IDs, unscoped requests, invalid documents and a verified article-path normalization.
- New integration regression definitions: \`qa/media-recovery/test_har_page_scoped_triage_20261031.cjs\` — full native suite **not executed** in this environment. An isolated V8 smoke test against the exact committed importer/core source passed: unrelated tab's HTTP 403 was excluded while the target tab's HTTP 200 survived; a HAR without page metadata produced zero observed image statuses.
- No live browser HAR, visitor-facing response status, screenshot, transferred bytes or decoded image dimensions were produced in this sprint.

**Still outstanding:** 61 published posts / 355 stored image references; 288 offsite references in the frozen snapshot (versus 286 in Site QA #154's older input); 13 Media Library originals >1.5 MiB. The reported **42 broken photographs** and **76% reduction** are not independently verified. Prioritize confirmed guest-visible breakage, same historical asset identity, individual Navy/USCG/Florida Memory/archive rights checks and ≤960px/no-upscale staged candidates. Never alter production Gutenberg blocks or third-party copyrights based on a HAR-only indication.

