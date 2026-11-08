# Apollo Experience 2.0 — R214 creator attribution provenance hold

**Draft/staging only — not installed or approved for production.** Governing [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [revenue/analytics #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), and [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stack solely on R213 PR #1577; never edit homepage PR #49, Research Desk PR #158 or Grok's Drive queue.

## Concrete risk eliminated in staged PHP

The inherited optional `campaign-handoff.js` accepts syntactically plausible `utm_content` values without checking whether the claimed Grok asset actually exists. That code can append unverified creator campaign context to the **only** free Apollo investigation CTA. Syntax validation is not source custody and can contaminate downstream attribution. **R214 disables enqueue of the optional JS in the PHP adapter**, regardless of parameters. JS bytes are retained unchanged as archived parent code, *not activated*. The link works normally without JavaScript; the reader's NASA evidence, chronology, gallery, print source analysis, single free investigation and source limits remain byte-identical to R213. This is a local staging change, not an assertion that the JS ever ran on the production site.

`attribution-release-gate.json` denies activation until Grok supplies verified immutable published asset ID, platform/post URL and intended destination under TASK-008, Praxxis independently reviews, Claude verifies attribution in installed staging and the founder authorizes release. This does **not** require a paid service, new tracker or user identity data. No publication or merchant purchase is claimed.

## Rebuild/QA

The parent R213 `dist/manifest.json` is pinned at SHA-256 `d7495c05522628e9483c161a8ac32020f1325f97b6437fd9e870c8036032fd4a`; all parent output digests and negative rights/release flags are checked. It must be supplied as a SHA-verified generated snapshot because the R198 canonical vs inherited builder source mismatch remains unresolved.

```sh
FV_APOLLO_R213_DIST=/absolute/path/to/r213/dist python experience2/apollo-r214/apply_r214.py
python experience2/apollo-r214/qa/gate_r214.py /tmp/apollo-r214-run-A
python experience2/apollo-r214/qa/gate_r214.py /tmp/apollo-r214-run-B
```

Generated R214 `dist/manifest.json` SHA-256 `f4fb5bcea55c222a25e46b173c4ce273d88c523ed6f0bb82178203f0786465b3` using the pinned parent.

**Actually executed locally:** PHP lint + normal/printed/late fail-open, `js=false` in all PHP render modes, sole free CTA intact; two runs of real Chromium 144 / Playwright, 11 contexts per run across widths 320/360/390/768/1440/1920, touch, keyboard anchor navigation, no-JS disclosures, reduced-motion, forced colors, simulated CSS zoom, print answer visibility, overflow and console checks. **11/11 screenshot hashes match across runs.** Six deliberately corrupted parent artifacts rejected by the executable builder per run. The current receipt logs local layout/context only; it does **not** claim measured p75 CWV, genuine axe-core, actual browser UI zoom or merchant conversion. No URL navigation or installed WordPress acceptance.

**Unpassed release gates:** exact GitHub R198 source chain reconstruction; genuine axe-core and NVDA/VoiceOver; installed WP/Assembler/Jetpack/CDN/CSP, external destination and *real* zoom; hosted CI on exact HEAD and independent QA; image/likeness commercial rights, genuinely purchasable educator SKU/price/fulfillment and founder approval. R214 does not activate a paid link or pretend any non-verified offer is sellable.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Change | Evidence | Owner |
|---|---|---|---|---|---|
| Future educator source-analysis dossier, **not sellable** | Original investigation → checkout | No approved SKU, rights, product validation, merchant order | Keep paid CTA absent; commerce verifies actual product before design | COMMERCIAL HOLD | Claude/Commerce/Founder |
| Grok Apollo documentary (publication not verified) | Social campaign → Atlas → article | Spoofable syntactic `asset_id` contaminates provenance | Disable optional UTM script pending source-linked allowlist and creator QA | LOCAL PHP + Chromium PASS; actual campaign unknown | Apollo; Grok/Praxxis/Claude |
| Free investigation | NASA findings → original article | Need reliable no-JS, accessible action | Preserve one source-adjacent CTA unchanged | 11×2 Chromium contexts PASS | Apollo |
| Paid customer | Qualified sessions → order/refund/net | No confirmed orders, fees, refunds or denominator | Reconcile only first-party/merchant 7/30 day records | NOT COMPUTABLE | Claude/Analytics |

**Proposed visitor pathway:** Grok documentary with later verified asset ID → source-led Apollo Atlas → one free original investigation → a future *original*, classroom-ready rights-cleared educator dossier only after demand, product, checkout and release approval. No unrelated affiliate offer in tragedy coverage. Revenue per 1,000 qualified sessions and paid conversion **NOT COMPUTABLE**.
