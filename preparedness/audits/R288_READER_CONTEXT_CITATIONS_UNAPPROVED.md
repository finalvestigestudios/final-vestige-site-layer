# R288 — Preparedness Reader-Context Citation Safety (UNAPPROVED)

**2026-11-11 PT · Engineering #136 · Conversion #820 · Business charter #818**

**State: DRAFT / HARD HOLD.** This is a source-only review artifact; it is not authority to merge, publish, write to WordPress, edit navigation or analytics, activate checkout, send email, post social media or spend funds.

## Reproduced R287 mechanical weakness

R287's literal `{{cite:id}}` string search can count an exact tag inside HTML comments, attributes, `script`, `style`, `template`, `noscript` or concealed ancestors as a citation occurrence. An ID matching a source register and metadata mapping is **not** proof that a reader sees an actual source note. This affects citation audit confidence. No live publication bypass was observed.

R288 layers a conservative HTML-token context check over R287's source custody, without changing original content. It imports R287 by compiling its authenticated Git bytes (`b7bd7b2b65010df2aaef8875f717ee94cc70d553`) rather than resolving `__pycache__`. It demands the inherited audit return `DRAFT_HARD_HOLD` with all independent QD, medical, privacy and publication permissions false. It then reads the same 41 pinned bodies and rejects raw citation references missing from reader-text nodes, including markers in comments, attributes, nonreader elements and locally hidden markup. Malformed or tag-split markup is held for review. An invalid upstream gate always blocks R288.

**Scope limitation:** this is a Python HTML tokenizer, not the actual WordPress renderer, browser accessibility tree or computed CSS. CSS classes, external styles, JS and layout can still hide source notes; `render_visibility_verified` and `wordpress_drafts_verified` remain false even after a mechanical hold result. Human source-scope and qualified safety review remain mandatory.

## Local exact-source receipts

- 56/56 isolated synthetic Python tests **PASSED**, including 31 generated nonreader/malformed scenarios and fail-closed source-pinning/invalid-root tests.
- `python -m py_compile` of both new Python files **PASSED**.
- Exact local Git blobs: implementation `0924ead810a4df8c169a5e77f05bcf979eac3dc9`; tests `06aae950d19c18259cf8be4653da02c78b30ca10`. These match GitHub file object identities on this draft branch.
- Native `python -I preparedness/tools/validate.py`, `build.py`, all current-head inherited suites, and 41 authentic WordPress exports **NOT RUN** because complete repository checkout still fails local GitHub DNS. Do not claim a full-tree PASS.
- 7/7 Claude contributor branches compared directly with their R200 frozen SHAs; all ahead 0/behind 0/identical. Historical 21-article lineage review remains unresolved. Independent QA #157 inspected, independent fixture #169 inspected; #169's separate duplicate-ID fixture still writes `_dup_test.json` inside real `sources/fragments/` and remains QA-owned. Homepage #1689 inspected and unchanged.

## Source, safety and release holds

No original manuscript, metadata, source register, source use, route, CTA, offer, exporter or integration manifest modified. Preserve review of 32 shared source-URL groups, 15 duplicated source IDs, 3 disputed CDC/Ready.gov citation occurrences, Article #7 chemical-water advice, Article #15/Tool #104 child-information privacy/accessibility/printing, and the 21 historical lineage disparities. No medical-safety, privacy, print-usability or independent QD PASS.

## Conversion-first decision contract

**Audience:** households seeking emergency-contact/reunification plans. **Free guide:** existing, public `https://finalvestige.com/preparedness/` only (not held drafts, no retired water freebie). **Optional practical downloadable resource:** the held family contact resource needs child privacy, print and accessibility review; not distributable as a verified freebie. **Potential paid pack:** Legacy Triage is merely a provisional candidate; no evidence yet confirms rights, appropriate intent fit, merchant availability, delivery or refund conditions. No approved paid CTA.

| Offer → step | Blocker | Change/experiment | PASS/FAIL evidence | Owner |
| --- | --- | --- | --- | --- |
| Public free archive → reader's cited guidance | Literal string match can count hidden citations | R288 text-context gate; render-level follow-up | 56 synthetic PASS; full checkout UNRUN | Preparedness integration / independent QA |
| Already-published Grok family-contact asset → free archive | No independently authenticated asset_id, post URL/date/rights and signed-out mobile destination | Verify existing TASK-008 ledger entry, UTM and destination; do not create content | NO VERIFIED MATCH | Grok / Praxxis |
| Free archive → optional held family-contact download | Child privacy, accessibility and physical print review pending | Review human safety, 44px controls, print/no-JS and information minimization | HARD HOLD | Preparedness QA |
| Free guide → optional Legacy Triage product | Sellability, licensing, offer match, merchant settlement/refund proof unknown | Audit existing product and delivery before any proposed CTA | NOT APPROVED / NOT TESTED | Founder / Commerce |
| Qualified campaign traffic → confirmed net revenue | No authenticated purchase, fees, refunds or human-session/asset attribution | 7/30-day reconciled merchant/provider scorecard, no proxy sales | NOT COMPUTABLE | Analytics / Commerce |

**KPI** = realized net revenue / qualified human sessions × 1,000, calculated only if denominator, merchant-settled owned orders / independently confirmed FV affiliate commissions, refunds and fees can be reconciled. Distinguish CTA clicks, checkout starts, leads and purchases; never count one as another. Consent/disclosures required before implementation. All missing figures remain unknown, not zero.

**Release hold:** independent source-scope adjudication; true live renderer/WordPress drafts verification (41), semantic citation exposure, mobile 360/390/768/1440, keyboard, no-JS, 200% zoom, WCAG, prints, complete validate/build/test, independent QD and founder approval before any public changes.
