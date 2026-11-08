# EX2 local Focus browser receipt — source-correctness repair (2026-11-08)

**Status: DRAFT / RELEASE HOLD. No production CMS edit, merge, install, subscriber event or tracking.** Stack parent: PR #1620, exact SHA `d20027e1dbba058ae4f0008f8d9f1ce291c1f82d`. Frozen PR #49 is untouched.

## Proven blocker

PR #1620 intentionally rewrites all five protected WordPress Playground homepage Focus links from `https://finalvestige.com/focus/` to a same-origin, visibly inert `/fv-ex2-focus-review/` destination, marking each `data-fv-ex2-isolated-focus="1"`. But its packaged `fv-ex2-private-browser-receipt.php` still counts only anchors whose host is `finalvestige.com`. Reproduced by actually executing the protected PHP preview shortcode, route filter and footer receipt with WordPress-function stubs, then clicking the receipt's capture control in Chromium: **0 Focus destinations, FOCUS_LINKS_NOT_5** despite five valid local links. This makes the prepared staging QA instrument misleading. It was not reported as genuine WordPress acceptance.

## Change

`repair_focus_receipt.py` accepts **only** the protected PR #1620 ZIP SHA-256 `e3a7f7ef73e7db6f7705b01fd3a0aa52452626dd1a1291f66c11248e7712e9dc`, validates the old receipt source SHA, applies exact-once replacements, updates private source-custody metadata and writes a deterministic ZIP. New receipt accepts only **exactly five** flagged, same-origin `/fv-ex2-focus-review/` anchors with **no query or fragment**; rejects production Focus leakage, unmarked local links, extra, missing, wrong-host or spoofed destinations. No changes to archival narrative, CSS, first-screen mobile fix, image elements, Blueprint import steps or actual Focus Page 1579.

Protected rebuilt ZIP SHA-256: `23c4073fb328ae6231380f68225af36645ab127b8df864e604aee1848f54b436`. Modified receipt SHA-256: `9d7ffe5cc4070aab3dac656cb039c44594e0249e1e762a0ad14f6418f2e7c89e`. **Protected ZIP intentionally not committed publicly**; attached to founder's private engineering artifact.

## Verified / not verified

- Actual protected PHP renderer + existing Focus route plugin + footer receipt executed via PHP 8.4 function stubs. Native WordPress Core, real Assembler and Jetpack **not executed**.
- Full Chromium 144 tested at 320×568, 390×667, 768×1024, 1440×900, 1920×1080 with JS enabled/disabled; expanded artifact verification **33/33 PASS**, including six deliberately malformed link cases rejected.
- Source-controlled smaller browser regression `test_focus_receipt_guard.py` **34/34 PASS** across four sizes + JS modes, reproducing the old false blocker and rejecting five negative controls.
- Seven chapters and 72 Margins preserved, no non-receipt PHP/Blueprint/JS/CSS changed; ZIP integrity and PHP lint pass.
- No genuine WordPress Core staging, host navigation, media network transfers, independent axe/manual WCAG, Lighthouse field CWV or real subscriber/purchase proof. Do not infer net revenue from this test.

## Conversion-first interpretation

**Offer:** existing 52-page Focus Fieldbook. **Funnel step:** seven-chapter evidence -> five contextual CTA links -> local inert review landing; live Jetpack signup and actual paid purchase remain separate. **Blocker:** local QA receipt falsely rejected the correct destination. **Change:** exact-scope fail-closed receipt correction. **Pass evidence:** verified 5/5 same-origin route receipts; original rejected; spoofed/production escape routes rejected. **Owner:** interim homepage engineering and QA. Claude retains Jetpack and attribution production engineering; Grok/Praxxis retain social acquisition. **Sales/subscribers/net revenue: unverified/unchanged.**

Source/rights: no new or revised archival imagery. NASA 473, Franklin 474, NYPL 1258 remain under existing metadata; bytes and NYPL derivative clearance not verified. WordPress.com Personal has no native staging clone.

## Reproduce (private local parent only)

```bash
python experience2/review/focus-local-route/repair_focus_receipt.py --parent fv-ex2-isolated-focus-review.zip --output repaired-review.zip
python experience2/review/focus-local-route/test_focus_receipt_guard.py --parent fv-ex2-isolated-focus-review.zip
```

**Release remains HOLD:** real isolated WordPress Core/Assembler import, native cross-page navigation, genuine image transfers/rights, axe/manual WCAG 2.2 AA, measured Lighthouse, actual Jetpack verification, CI green, QD PASS and explicit founder approval. Never install this MU plugin on production.
