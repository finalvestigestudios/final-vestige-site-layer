# EX2 — Private Playground integration bridge / exact-source admission
**Status:** REVIEW ONLY — release HOLD. **No WordPress.com writes, merges, deployment, or new paid services.**

## Actual blocker closed in source
PR #1332's exact seven-chapter Blueprint is blob `137c74a476005684a28f5ff9a36e75c6b03268f7` (SHA256 `10af751569bf11a7fd18003e56cb7ccad9596f59606be9d5fb5d87d95784bb7c`), at commit `37bc943c08204867809a0b3c80540fa534fb005f`. Prior private launcher (#1312) was pinned to the now-older `455c6cccbf8a00e6ecc4c2524775010d7ee1762c` Blueprint. It could **not** review current HEAD. Existing isolated-URL runner (#1306) cannot directly inspect the virtual WordPress page opened inside the Playground web application from a large private Base64 URL fragment.

This branch **re-pins** the generator to exact source and adds a browser bridge that:
1. Verifies the ZIP entries, exact Git blob and SHA256, Assembler commit, HTML fragment roundtrip, review safety markers, all seven chapters, 72 Margins fragments and five Focus destinations; refuses older or modified source.
2. Opens the **official** Playground URL via the locally rendered read-only launcher (no external paste/public Github URL); rejects non-Playground top-level origins and production navigations or mutations.
3. Waits for the actual Assembler `.wp-site-blocks [data-fv-home-flagship]` frame, then reuses the source-controlled #1306 WordPress-semantic checks.
4. Scrolls and inspects real image HTTP responses, decodes **actual body bytes** and hashes them; refuses missing or HTML responses.
5. Refuses a passing WCAG claim unless a locally provided official `axe.min.js` runs with no violations/incomplete checks.
6. Records a structured **FAIL** or **PARTIAL** report rather than treating launcher URL integrity, PHP stubs or a static fixture as WordPress validation.

WordPress Playground requires JS to bootstrap. Its internal virtual pages therefore **cannot certify a JS-disabled HTTP origin**. No-JS, Safari, independent WCAG review, Lighthouse/CWV, Jetpack, production host parity, image rights, editorial QA and founder release approval **remain independent HOLD gates**. This bridge never reports RELEASE PASS.

## Local execution from the repository
```bash
cd experience2/home-flagship/playground
python -m unittest -v test_make_private_playground_launcher.py test_verify_private_playground_bridge.py
python make_private_playground_launcher.py --blueprint FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json --output /tmp/fv-ex2-current-private.zip
python verify_private_playground_bridge.py --bundle /tmp/fv-ex2-current-private.zip --report /tmp/fv-ex2-wordpress-browser-report.json --axe-js /absolute/path/to/official/axe.min.js
```
Requires an **Internet-connected** system able to open `https://playground.wordpress.net/`, Python Playwright, Chromium and Pillow, plus official local axe-core. No subscriptions or new paid infrastructure. Do not publish the launcher fragment (it includes unpublished research source); do not import accounts, customers, subscribers, credentials or the live database.

## This run: evidence, not certification
- Exact #1332 Blueprint: **pinned and packaged locally**; 7 chapters / 72 Margins / 5 Focus preserved in admission.
- Local negative-control suite: **10/10 PASS** for source and privacy integrity (the branch's source variant will still need independent CI on exact HEAD).
- Actual Chromium navigation attempt: **FAIL CLOSED** — the automated sandbox rejects outbound requests to Playground (`chrome-error://chromewebdata/`; Python HTTPS DNS also unavailable). Thus WordPress runtime **not exercised**, image bytes not transferred and axe not run.
- Prior production Page 6 remains published and unchanged; connected WordPress listing exposes only production site 256784396, with no native Personal-plan clone.
- External provider confirms Blueprint Base64 URL fragment and `git:directory` are supported patterns; this is **format research**, not an executed import.
- No new archival claims or rights changes. Existing NASA Apollo and Franklin source images remain awaiting transferred-byte and rights acceptance; NYPL remains excluded.

**Owner/handoff:** Homepage engineering owns this bridging QA; Site QA owns independent accessibility/performance; Claude owns attribution, Jetpack and checkout validation; founder owns deployment approval. Grok/Praxxis own acquisition. Next: run the exact bundle on a connected private machine/browser, inspect true Playground results, complete WCAG and no-JS/Safari/performance/rights gates, then founder visual release decision. No change to frozen PR #49, Issue #171, or Apollo #158.

## Conversion contract
**Offer:** existing 52-page Focus Fieldbook. **Funnel:** paid-intent/qualified visitor → visible contextual CTA → confirmed subscriber → separately verified order/affiliate payment. **Blocker:** flagship WordPress execution and trust/CTA parity not verified. **Change:** current-HEAD private staging bridge and fail-closed acceptance. **Evidence:** exact-source hashes/negative controls; real WP FAIL (network unavailable). **Owner:** homepage QA + Site QA, with Claude for actual tracking. **Revenue:** not measured; no claimed sales.