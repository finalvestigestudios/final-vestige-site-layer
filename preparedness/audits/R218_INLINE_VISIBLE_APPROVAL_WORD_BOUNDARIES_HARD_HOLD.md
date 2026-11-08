# R218 — Rendering-adjacent release-language integrity, DRAFT / HARD HOLD

**Scope and ownership:** Preparedness Archive integration/safety gates, Issue #136. Commercial attribution coordination #820 and founder charter #818. This is an isolated child of R217 draft PR #1588 at `d357b2f51c279d6803b6acee344a2e4ade96eb63`. Neither original article/source/slug/safety fields nor other agents' assets were modified. No WordPress, CMS, menu, homepage, social, merchant, email, analytics or public publication action. Not qualified medical, clinical, QD, editorial or source approval.

## Concrete deficiency, repair, and limits

Independent Praxxis/Grok handoff review identified a missing text-node adjacency check: `App<span>roved</span> for publication` is displayed as “Approved for publication” yet R217 previously inserted a space between all HTMLParser `handle_data` fragments, producing “app roved for publication” and missing the assurance. A comment or inline emphasis node can split the same word. This is a source-code finding and was reproduced with isolated synthetic HTML, not evidence it appears in real source articles.

R218 repairs the **existing** R217 gate rather than appending another unintegrated new stage. The reader concatenates adjacent text nodes verbatim, inserts visible word boundaries only for block-level elements and `br`, normalizes Unicode NFKC, removes specified default-ignorable characters, collapses whitespace, and rejects prohibited approval assurances in both `pa-chips` and `pa-review`. It preserves the inherited duplicate-attribute, document-global fragment, receipt and safety-state checks. Its only states remain `DRAFT_HARD_HOLD` (exit 2) and `INVALID_HARD_HOLD` (exit 3); never QD PASS.

**Exact independently executed local code Git blob:** `abefe8954e6dcd8f609db4359586120360828acd` (the revised R217 guard). **New test blob:** `d7eb969e7f7f040d41a0a287f7c8cb76050510fd`. Base R217 guard blob: `8850b5fdc93ddbcec212c600e78c9d8ffdd32f1b`. These were compared to GitHub contents after writing. An intermediary transport-error commit occurred during GitHub source replacement, was immediately corrected to the byte-exact tested blob before this PR; full Git history shows both operations, and final branch tree is authoritative.

### Executed test evidence

```sh
python -I -m unittest discover -s preparedness/tests -p 'test_r218*.py' -q
# Ran 182 tests in 0.129s — OK
python -m py_compile preparedness/tools/r217_transport_semantics_guard.py preparedness/tests/test_r218_visible_assurances.py
# PASS
git hash-object preparedness/tools/r217_transport_semantics_guard.py
# abefe8954e6dcd8f609db4359586120360828acd
git hash-object preparedness/tests/test_r218_visible_assurances.py
# d7eb969e7f7f040d41a0a287f7c8cb76050510fd
```

176 adversarial cases are distinct combinations of **22 mutations** × **two disclosure sections** × **two held articles (#7/#20)** × **WordPress/preview**; six baseline tests. Each mutation recomputes the matching synthetic parent digest first, proving the error is content semantics rather than stale receipt. Positive drafts stay held, never approved. Missing checkout means inherited R217 107 cases, full native validation/build, 35 authentic articles/41 outputs, genuine theme/browser/CSS/AT, independent QD and human source checks **not executed in this environment**.

### Branch and independent QA identity check, 2026-11-08

Seven core frozen Claude source-of-truth heads: Start `2122d856fce9f64887c16df3d52e64be9f59a55b`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`. Auxiliary shelter continuation `ac8625faf30dd5538fadc31e06cb5a2cea1defae`; shelter follow-up `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`. All nine refs read live through GitHub branch API and match previously pinned identities.

Independent draft QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` retains older Start article bases; fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` and follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` remain separate. Their payloads were inspected; **do not blindly merge outdated article files or write synthetic tests into the shared source tree**. Latest independently checked home PR #1595 head `450d65f392f3a1f0587b2671dc1e3141b3f88577`, untouched.

### Release blockers (unchanged)

- Three specific original citation occurrences still need adjudication: two CDC in Article #7 *Homemade Water Filters*, one Ready.gov in Article #20 *Preparedness for Real Households*. Seven historical source-ID collisions still need deliberate source scope handling.
- Native checkout via local GitHub DNS fails; full `python -I preparedness/tools/validate.py`, `build.py`, and `python -I -m unittest discover -s preparedness/tests -v` against all original 35 articles and 41 WordPress-ready outputs are **NOT EXECUTED**. The new guard remains an existing separately invoked R217 stage, not yet wired into the authentic root validation release gate.
- No original article or 41 export has been independently declared QD/medical-safe; any historical founder editorial status does not satisfy qualified expert review. Human source-check flags, accurate claim context, WP sanitizer output, and assistive-technology acceptance remain open.

## Conversion-first single-offer, single-audience staged acceptance (NO ACTIVATION)

**Audience hypothesis:** household decision-makers who need an emergency contact, identity, insurance and family records-location plan; research-only creator topic “How will your family find essential records if you cannot answer the phone?” It is **not** a request to produce a Grok video.

**Authentic ungated free destination:** https://finalvestige.com/preparedness/ (existing source-backed agency links, not a newly cleared R218 article). **Only provisional paid offer:** https://payhip.com/b/n1RhV, Legacy Triage printable listed at $19 under Vested Wisdom. An observable listing is not verified FV seller rights, settlement, checkout, secure file delivery, refunds, suitable scope, or real demand; it may be a poor-intent match and **must not be promoted without founder/commerce acceptance**. Do not resurrect the retired water freebie or manufacture a new product.

| Offer → funnel step | Blocker | Draft-only experiment / acceptance change | Evidence / state | Owner |
|---|---|---|---|---|
| Grok published high-intent family-records media → free Archive | No real matching asset_id/post URL/hook/destination confirmed in TASK-008 | Praxxis independently match existing actual posts; preserve creator queue and allowed UTM | UNVERIFIED; no asset fabricated | Grok/Praxxis |
| Free source-backed Archive → optional planning resource | Unpublished FV authored guides/safety citations still on hold | Keep official links free; test heading/safety label, keyboard/360–1440px link usability on approved staging | Existing public Archive LIVE; guide HARD HOLD | Preparedness / independent QA |
| Archive → optional Legacy Triage | Seller authorization, scope/fit, credential/privacy instructions and disclosures not approved | Founder/Commerce inspect purchased PDF rights and consent; draft adjacent optional-fee disclosure | Candidate listing OBSERVED; NOT APPROVED | Founder / Commerce |
| Product link → payment → download | Merchant checkout, secure delivery, receipt/refund/tax/fees not tested | Authorized sandbox/merchant buyer-flow only, without unnecessary credential capture | NOT TESTED; no CTA | Commerce |
| Asset sessions → verified orders → net revenue | No qualified-human unique asset cohort or independently confirmed order/refund/fees | Only approved existing analytics and merchant exports; match 7/30-day cohorts; mark tiny samples | Net revenue per 1000 qualified human sessions NOT COMPUTABLE (not zero) | Commerce / Analytics |

**Disabled on-site CTA draft, for review only:** “Start with free official emergency-planning resources. A separate family-records organizer may be useful for some households, but the optional paid printable has not yet completed our commercial and privacy review. You do not need to sign up or buy anything to use these free sources. Keep any completed financial or access information private and securely stored.” **Do not render a merchant link until approved.** No claimed conversions, no dark patterns, no new tracking script.

**Campaign acceptance contract:** verified actual Grok post and `asset_id`, canonical public page and matching factual hook, consent/rights, UTM when permitted, lead confirmation separated from signup attempts, paid order receipt and seller-reconciled cleared payment separate from CTA click or checkout start, fees/refunds and net revenue, 7/30-day cohort qualification with low-n warning. No paid/social/email/affiliate/CMS changes authorized.

### Next exact-head executable integration milestone
```sh
git checkout <trusted integrator reviewed HEAD>
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/audit_integration.py --require-release-ready
# EXPECT HARD HOLD until source/citation/safety/independent QD gates are resolved
```
