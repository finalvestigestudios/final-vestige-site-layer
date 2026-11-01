# Apollo Experience 2.0 — R31: actual PHP HTTP response custody

**DRAFT / HOLD / NO WORDPRESS OR PRODUCTION INSTALL.** Stacked on R30 PR #371, isolated under `experience2/apollo-wp-bridge/sealed/qa/`. No edits to frozen homepage PR #49, homepage lead branches, Research Desk PR #158, evidence records, source media or WordPress.

## New security coverage

`http_response_gate_r31.py` verifies the unchanged, exact SHA-256-pinned R29 private staging ZIP and sealed plugin, loads the real PHP plugin under a deliberately minimal **mock WordPress** HTTP shim, and makes actual loopback HTTP requests to PHP's built-in server. It verifies: HTTP CSP/nonce binding to rendered style/script tags; different nonces on successive requests; CSP, no-store and source-head headers; six concordance records; six explicit image-rights holds; one unresolved catalog hold; zero Atlas geo coordinates; seven distinct denied-request conditions returning **empty HTTP 403 bodies**; and absence of direct PHP source disclosure. The direct PHP URL currently returns **HTTP 200 with an empty body** in this standalone harness, so this check does **not** claim direct-request status 403.

`test_http_response_gate_r31.py` adds eight adversarial test methods (missing headers, mismatched nonces, permissive CSP, fabricated geo, removed rights record, failed response, corrupted archive, valid control).

The nonce is random by design. The reproducible receipt substitutes a fixed-length placeholder before hashing response HTML/CSP, so two independent runs produce exactly the same audit bytes without exposing live nonces.

## Reproduce (local nonproduction only)

Requirements: Python 3.10+, PHP CLI (including PHP built-in server), no paid dependencies. This run used PHP 8.4.24. R29 exact ZIP is **not committed to GitHub**, but included in the founder-facing R31 evidence archive as `staging/PRIVATE_R29_SEALED_REVIEW_HOLD.zip`. Its SHA-256 must equal `d29ee02d629ae50716058b8ffa6cb3d9bac76a9cd72d9e3387504e2d22dab14f`.

```bash
python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p test_http_response_gate_r31.py -v
python experience2/apollo-wp-bridge/sealed/qa/http_response_gate_r31.py \
  --r29-zip /path/to/PRIVATE_R29_SEALED_REVIEW_HOLD.zip \
  --out /tmp/R31_HTTP_RESPONSE_RECEIPT.json
```

Locally observed: **8/8 adversarial tests PASS**; **7/7 empty HTTP 403 rejection cases PASS**; **two authorized responses** have independently rotating CSP nonces yet byte-identical normalized source custody; **two independent audit receipts byte-identical**. Independent Chromium rendering of the **actual HTTP response body** via `page.set_content` also passed at 320, 360, 390, 768, 1024, 1440 and 1920px, with keyboard, touch, no-JS and two deterministic source-review screenshots. Browser rendering is auxiliary evidence in the R31 archive; it does **not** enforce HTTP CSP because Chromium navigation is administratively blocked in this environment. Earlier R30 source-controlled Chromium gate remains the primary browser contract.

## Outstanding release gates

- An installed, authenticated, independent WordPress/Assembler staging environment (true WordPress permissions/cookies/nonces, theme and shortcode behavior) has not been tested.
- Browser-enforced HTTP CSP on actual staging cannot be claimed from PHP HTTP-header inspection or `set_content`.
- A verified upstream axe-core bundle was unavailable; axe certification remains **NOT RUN**. Safari, real device and screen-reader checks remain open.
- Hosted p75 Core Web Vitals, image-by-image NASA reuse clearance, the unresolved `S67-19766` identity, GitHub hosted CI, independent QD and explicit founder launch approval remain outstanding.
- **Do not merge, activate, deploy, or invent Atlas geographic coordinates or relationships.**
