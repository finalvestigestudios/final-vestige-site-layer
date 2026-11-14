# R367 — private WP/preview citation and provenance custody

2026-11-14 · Preparedness Archive #136 · conversion charter #820 / #818 · upstream draft #2476 HEAD `51fd79d8c915b735a12d242b74a07c54fd9f66b9`.

**DRAFT / HARD HOLD / NO PUBLICATION.** This change adds only a read-only validator, tests and this audit; it does not edit the original 35 articles, six authored tools, sources, taxonomy, URLs, WordPress, social or commerce.

## Integration verification

`preparedness/tools/r367_wp_preview_source_custody.py` checks **50 expected private WordPress HTML + 50 noindex preview HTML** exports: 35 article and six tool pairs, eight section hubs and one landing. It cross-checks the original 41 manuscript bodies, contributor-specific source origins, source-to-footnote URLs and occurrences, build report, export inventory and inner HTML equivalence. It rejects missing/extra exports, noindex loss, altered canonicals, suppressed pending-review notices, mismatched citation counts/footnotes, changed source destinations, unsupported release assertions and unresolved template tokens. Each result is a hard hold regardless of passing structural checks. It does not contact WordPress or make factual/medical safety claims.

**Isolated executable evidence:** 59/59 new R367 tests PASS, including 50-pair synthetic fixture and adversarial cases; 88/88 inherited R366, 58/58 R365, 66/66 R364 PASS (271/271 total). Python compilation PASS. The exact committed Python/test Git blob hashes were matched to locally executed bytes. Missing authentic checkout correctly exits 2 with INVALID_HARD_HOLD. Local GitHub clone/ls-remote fails DNS. Native `python -I preparedness/tools/validate.py`, `build.py`, full Python test discovery, genuine 50+50 private exports, browser/print and QD reviews **NOT EXECUTED**. Synthetic fixtures are not real WordPress artifacts, not publication readiness.

**Source holds:** original 15 unverified register placeholders; 32 unadjudicated shared-URL reading-scope groups and 15 duplicate ID groups. Tool #104 continues to require independent review of print-hidden paper privacy warning, child data use, no-JS behavior and emergency call wording. No source is treated as independently human verified.

**Contributor exact SHAs checked:** start `2122d856fce9f64887c16df3d52e64be9f59a55b`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; shelter continuation `ac8625faf30dd5538fadc31e06cb5a2cea1defae`; shelter followup `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`.

**Separate drafts not modified:** independent QA #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, dependent correction #2205 `bbcf1859768624c611df4abadc564c18247cf32a`, homepage #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`.

## OFFER → FUNNEL → BLOCKER → PRIVATE CHECK → EVIDENCE → OWNER

| One potential offer | Funnel | Blocker | Required private check | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| One existing FV-owned Preparedness pack, only if authentic | Paid order/delivery/refund | No rights-cleared actually purchasable SKU, merchant terms or delivery verified | Founder verifies live SKU, seller acceptance, fulfillment and refund/fees | **HOLD — no approved paid CTA or paid sale** | Founder/Commerce |
| Existing free agency household-planning guide → optional free Tool #104 | Relevant guide-to-card CTA | Source, print, child privacy, emergency-language, accessibility and no-JS holds | Qualified QD and actual mobile/print checks after source adjudication | **HARD HOLD** | Preparedness/QD |
| One real already-posted Grok family-reunification asset → free Archive | Authenticated `asset_id` / allowed UTM / qualified human visit | Matching published asset ID/URL and landing proof missing | Praxxis read-only content/CTA match; Grok retains posting ownership | **UNVERIFIED** | Grok/Praxxis |
| Qualified humans → confirmed lead → independently paid order → net per 1,000 | 7/30-day customer revenue | No consent-safe attribution or settled merchant orders/refunds/fees | Claude/Commerce reconcile existing approved analytics and merchant receipts | **NOT COMPUTABLE** | Claude/Commerce |

Draft free CTA **“Start With Trusted Preparedness Resources”** → existing ungated `https://finalvestige.com/preparedness/` (not deployed); no retired water freebie, unapproved paid product or affiliate. No site, CMS, navigation, analytics, social, email, merchant, affiliate, spend, merge or release operations.

**Next gates:** complete authenticated native checkout, genuine full build/validator/test run, 50+50 private output comparison, human source-claim/reading-scope adjudication, Tool #104 qualified review and founder-approved release. All publication, QD, safety, paid-order and revenue-verification booleans remain false.
