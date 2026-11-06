# Apollo R160 — source-pinned accessibility escalation (staging hold)

Scope: independent Apollo 1 / Research Desk acceptance. Parent [#150](../../issues/150), conversion gate [#820](../../issues/820). Follows draft [R159 #1216](../../pull/1216). **Do not merge, install, publish, or alter WordPress.** Homepage PR #49 and original Research Desk PR #158 are untouched.

## New verifiable implementation
`test_csp_accessibility_gate.py` extends the committed R159 PHP shortcode/Chromium test runner. It rejects a package unless its SHA-256 is `08e633bcc07f8d29cd2aebac5c7b9d945d9040da5a6e35a4f2bed60815defbc3`. It checks Chromium's actual accessibility tree, duplicate IDs, keyboard-targeted chronology, new-window rel safety, no invented geo pins, and absence of paid links. It preserves R159 no-JS, SRI tampering, keyboard/search, six responsive widths, reduced-motion, screenshot checksums and PHP fallback tests.

Optional `--axe /approved/axe.min.js` runs browser-executed axe-core WCAG checks; **zero violations AND zero incomplete** are necessary. Without an approved local axe-core build the receipt records `NOT_EXECUTED_LIBRARY_UNAVAILABLE`, never an accessibility pass. No remote library is fetched or installed by this script. The optional supplied library is a **test instrument**, not a production asset.

## Replay
1. Rebuild or supply the exact R159 staging ZIP, checking the SHA-256 above.
2. Run: `python -I experience2/apollo-r160/test_csp_accessibility_gate.py --package /path/to/fv-apollo-r159-wordpress-staging.zip --out /tmp/apollo-r160-qa`
3. Review `receipt.json` and `SHA256SUMS`; `--axe` is needed for a full automated accessibility audit. Do not certify production from this offline result.
4. Repeat in a fresh output directory and compare screenshots/JSON. Run any actual WordPress staging check only with appropriate release approval and isolated credentials; no authorization to change a site is implied.

## Offline evidence and limitations
In an independent local derivative replay of the R159 package, native Chromium completed **174/174 checks**, six viewport widths (320, 360, 390, 768, 1440, 1920), zero page exceptions, and six reproducible screenshots. Additional independent comprehensive audit of the same source completed **204/204 checks**. **Neither was an exact-head GitHub CI run**; hosted GitHub CI and real WordPress staging are not certified. Chromium outbound HTTP/file navigation is blocked in the execution environment, so data: URL substitution preserves asset bytes but does **not** verify same-origin CSP headers. Browser accessibility-tree checks are not axe or a manual screen-reader audit. Production LCP/CLS were not measured.

## Conversion-first decision (no commercial activation)
History educator / long-form Apollo viewer → source-rich Research Desk → **Read original investigation** (one contextual action). An Apollo educator dossier remains a proposed offer, **not a verified SKU, checkout or rights-cleared product**. Do not add an unrelated Mini Museum offer to the narrative or suggest NASA endorsement. Grok owns video production and asset IDs; Praxxis owns creator-source QA; Claude owns production instrumentation; founder owns release and spending. Qualified sessions, confirmed subscribers, merchant-confirmed paid orders, refunds, fees and realized net / 1,000 qualified sessions remain **unverified / not computable**, never inferred from clicks or views.

## Release gates
**HOLD** until (1) installed WordPress Assembler/reusable-block staging acceptance, (2) actual same-origin CSP/SRI, (3) trusted axe-core zero violations/zero incomplete plus manual keyboard/screen-reader/zoom, (4) networked actual-page LCP/CLS, (5) NASA rights review, (6) independent site QA and founder-controlled production release, (7) verified merchant product and attribution before purchase CTA activation. No CMS/settings/social/affiliate/email/merchant writes in R160.
