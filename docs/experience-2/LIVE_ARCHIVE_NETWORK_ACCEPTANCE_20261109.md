# EX2: real-image-network admission — 2026-11-09 (review only)

**DRAFT / RELEASE HOLD · no WordPress edits, subscriber interaction, merge, deployment, affiliate activation, or new service.**

## Why this is an actual release blocker

Issue #150 requires proof that the source-grounded seven-chapter WordPress homepage loads its first-party archival images in a real anonymous browser. Parent PR #1730 verified *editor attributes, media record metadata and rights references*, not downloaded bytes, selected responsive source, image decoding, or mobile behavior. This companion PR adds a **reusable, fail-closed anonymous hosted-browser admission probe** rather than another visual concept. **Do not read passing synthetic browser tests as passing the live homepage.**

Fresh authenticated read-only WordPress Page 6, modified **2026-11-05 12:07:24 site-local**, has the three corresponding \`[data-fv-case]\` / \`[data-fv-archive-img]\` pairs:

| Case | Live editor original / responsive location | Source rights caveat |
| --- | --- | --- |
| Apollo | \`s67-19766.webp\`, WordPress 473, original URL on finalvestige.com; srcset Jetpack CDN | NASA source attribution; don't imply NASA commercial endorsement. NASA source https://www.nasa.gov/image-detail/apollo-1-crew-honored/ |
| Franklin | \`Franklinexpeditionnote.jpg\`, WordPress 474, original URL on finalvestige.com; srcset Jetpack CDN | Commons https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg documents an 1869 print reproduction; the site's editorial folio is not an original artifact photograph. |
| Malbone | \`edit-017-v02-nypl-5003296-original.jpg\`, WordPress 1258, current default \`i0.wp.com\` transform fit=1024×692 | NYPL https://old-digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0 gives a U.S.-only public-domain belief; global rights not established. |

No original source image is rehosted or redistributable from this PR. Keep attribution, evidence boundaries, source notes and historical facts unchanged.

## Exact executable source and observations

\`tools/experience-2/verify_live_archive_delivery.py\` runs anonymous Chromium against **only https://finalvestige.com/**; it never logs in, submits a form, touches WordPress, or records subscriber data. It selects all three archival cases via existing UI controls when JavaScript is enabled, scrolls to each image and reads \`currentSrc\`, responsive attributes, decoded dimensions and document visibility. Only three allowlisted archive filenames on finalvestige.com / Jetpack i0–i2.wp.com are traced. Arbitrary query params, credentials, emails and tokens are excluded from receipts. Response fields distinguish:

- \`wire_body_bytes\`: Playwright \`request.sizes().responseBodySize\`, encoded HTTP **response body** as reported by Chromium; this excludes request/response headers and is NOT full network transfer or a Core Web Vital.
- \`decoded_body_bytes\`: length of Playwright \`response.body()\`; **not** encoded transfer bytes.
- Selected responsive URL, HTTP status, image MIME, image decode, alt text and visible nonzero geometry.

The checker FAILS CLOSED on missing image/response, stale or wrong selected source, 4xx/5xx, missing or invalid MIME/body/sizes, tiny/broken decode, hidden image or missing alt. It does not produce field LCP, INP, CLS, rights clearance, or Jetpack confirmation.

**Run in a network-enabled review environment with Playwright + Chromium (Python):**

\`\`\`bash
python -m pip install playwright pillow
# Chrome/Chromium installed locally; alternatively playwright install chromium
python tools/experience-2/verify_live_archive_delivery.py \
  --url https://finalvestige.com/ \
  --widths 320,360,390,768,1440,1920 --dprs 1,2 --nojs \
  --out /secure/local-home-image-network.json \
  --screenshots /secure/local-home-network-screens
python -m unittest discover -s tests/experience-2 \
  -p test_archive_delivery.py -v
\`\`\`

Only publish a sanitized receipt and rights-reviewed screenshot excerpts. Offline synthetic fixtures are explicitly marked \`synthetic_fixture: true\`; never pass them as live acceptance. Screenshots can contain actual public page imagery; no full editor exports, credentials, subscriber records or host-specific private data are to be committed.

## Evidence from this isolated run

- The **exact committed test files** ran locally with Python 3.13, Chromium and PIL: 3 unittest methods PASS, **10 positive real Chromium network-interception scenarios** at widths 320/390/768/1440/1920 × DPR 1/2, plus **6 negative network/alt/decode controls** correctly rejected. These are synthetic sources and bodies delivered by \`page.route\` inside Chromium.
- Additional synthetic reference screenshots captured at 390px JS, 1440px JS, and 390px no-JS DPR2. They show only locally generated images, **not the WordPress production website**.
- Actual anonymous browser navigation was attempted at 390px; this execution environment returned \`ERR_BLOCKED_BY_ADMINISTRATOR\` before the homepage loaded. Receipt: **0/1 live visits passed; all three DOM images absent**. Consequently **no real media transfer bytes, screenshots, Lighthouse or CWV were obtained here**. The probe correctly failed closed.
- Current site inventory, read-only: WordPress \`wpcom_user_sites(environment=all)\` returned only production site **256784396**. The WordPress Personal plan has no native staging clone. Do not use the default wpcomstaging.com production domain as a second site.

## Conversion and release governance

**OFFER:** existing free 52-page Seven Day Focus Fieldbook. **FUNNEL STEP:** credible evidence experience -> contextual Focus action -> provider-confirmed Jetpack subscriber -> independently verified paid conversion. **BLOCKER:** without genuine archived-image delivery we cannot certify trusted mobile evidence presentation; separately live Focus query-only false-success remains in production, addressed in draft PR #1681. **CHANGE:** add a deterministic image-delivery network gate under parent #1730. **PASS/FAIL:** synthetic transport checks pass; actual hosted visit **FAIL (environment blocked)**, release stays **HOLD**. **OWNER:** interim homepage QA; Claude owns Jetpack/attribution; Grok and Praxxis own creator asset reconciliation (TASK-008), not website copy; founder approves production release.

Do not release hero CTA proposal #1689 until Focus correction #1681 and paired gate #1726 receive real Jetpack acceptance. No additional tracking or UTM mechanism is introduced. Do not infer leads/sales from visits, links or simulated browsers. **Net revenue per 1,000 qualified human sessions remains not computable**.

## Remaining independent gates

Hosted anonymous Chrome at 320/360/390/768/1440/1920 (and DPR2), no-JS, reduced motion, 200% zoom, source/context boundaries, keyboard/touch, axe WCAG 2.2 AA (fail closed if axe missing), honest Lighthouse lab results, 7/30-day *field* CWV only where supported, Jetpack confirmed opt-in + welcome delivery (under separate approval), current image source rights/byte receipts, GitHub exact-SHA CI/QD PASS and founder-specific release authorization. A free isolated WordPress Playground/Assembler is useful for native-block previews but cannot certify WordPress.com Atomic hosting, Jetpack subscriber state, cookies/redirects or field traffic metrics.

Frozen PR #49 at \`10495883299d53596992c26a8987f629b2904670\` remains untouched. Apollo R&D PR #158 and Mind #171 remain separate lanes. Do not merge or deploy this PR.
