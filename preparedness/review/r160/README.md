# R160 — Preparedness claim-context source crosswalk (REVIEW ONLY)

Issue #136; coordinated with #820, #818 and TASK-008. Parent R159 PR #1202 exact head 298d8414cf1ca6677ec1c8969036ac305e50d4e6.

**STATUS: DRAFT / HARD HOLD.** No production, CMS, navigation, analytics, merchant, publishing, affiliate, social, email or spending writes. No content or canonical sources modified. No independent safety/medical review or QD approval.

## Purpose

A citation count can stay constant while a citation moves away from the claim it purports to support. The new Python gate emits an inspectable, deterministic citation-context review docket for the authentic 35-article candidate. Every entry identifies article, citation ordinal, source ID, original author interpretation, normalized surrounding prose and SHA-256 context fingerprint. A changed claim context changes the fingerprint and requires human review. Evidence association does NOT establish that advice is accurate or medically safe.

The gate also authenticates the frozen R151 35-article metadata manifest and R159 quarantined Family Card snapshots by exact Git blob identities. It checks original article-body/metadata census, source-use/citation bijection, syntactic reference validity, unique routes, reading/citation depth, publication draft state, original metadata safety-state distribution (29 pending, 4 not-required, 2 recorded approved), and R159 privacy/print-unverified qualification. Recorded approval labels are not an independent QD PASS. The generated docket is stdout-only, no canonical file mutation.

The CLI always exits 2. It reports DRAFT_HARD_HOLD for structurally sound review evidence or INVALID_HARD_HOLD for validation errors. No path grants publication or merchant activation.

## Test evidence and trusted-checkout commands

72/72 isolated Python 3.13.5 unittest cases passed, including 64 individually named adversarial metadata, citation and source-use mutations. Python compilation passed. Synthetic unit tests are not authentic repository validation. All original 35 articles, canonical source registers, R159 snapshots, and seven contributor branches remain unchanged.

From an authenticated exact-head full repository clone run:

1. python -I -m unittest discover -s preparedness/tests -p 'test_r160_citation_context_gate.py' -v
2. python -I preparedness/tools/r160_citation_context_gate.py --repo .   (expected exit 2; inspect JSON status)
3. python -I preparedness/tools/r160_citation_context_gate.py --repo . --details > /tmp/preparedness-r160-context-review.json   (expected exit 2; reviewer-only dossier)
4. python -I preparedness/tools/validate.py
5. python -I preparedness/tools/build.py
6. python -I -m unittest discover -s preparedness/tests -v

Complete authenticated checkout, native build/validator/full suite, WordPress review rendering, browser privacy/print/mobile, source adjudication and independent QD are NOT VERIFIED. Local Git clone remains blocked by github.com DNS failure. Six source retrievals blocked by 403 must not be called dead links. Colorado and NCMEC source-scope disputes and the broader 75 PENDING citation/source decisions remain unresolved.

## Conversion-first admission

Proposed verified-intent audience: households with schoolchildren needing emergency pickup/reunification planning. Candidate FREE guide: Household Emergency Plan. Optional FREE practical draft: Family Reunification Card; privacy/print/source review pending. Grok asset_id and exact TASK-008 destination are unknown. Existing purchasable rights-cleared Preparedness SKU, checkout, fulfillment and refunds are NOT verified, so the optional paid step is DISABLED.

Draft-only CTA: Plan your household's emergency contacts and reunification steps — free guide. Do not gate essential safety instructions behind email or payment. No retired water offer and no newly invented SKU.

OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER:
- Verified rights-cleared Preparedness paid pack → paid order → no matching SKU authenticated → confirm existing merchant listing/rights/delivery/refunds, then stage checkout QA → HOLD → Commerce/Claude.
- Free Household Emergency Plan → reader → safety/source review pending → qualified review + native build → DRAFT → Preparedness/QA.
- Family Reunification Card → practical download → 11 source tasks and privacy/print unverified → independent source, device and print QA → HARD HOLD → Preparedness/Site QA.
- Grok topic → landing → asset ID/destination not verified → reconcile TASK-008 → UNVERIFIED → Grok/Praxxis.
- Confirmed order → realized revenue → missing settled orders and qualified-human sessions → reconcile privacy-safe 7/30-day cohorts, fees, refunds → NOT COMPUTABLE → Commerce/Analytics.

Conversion KPI (realized net revenue per 1,000 qualified human sessions) is NOT COMPUTABLE. Pageviews, CTAs, and leads are not paid orders; no claims of transactions, sales or conversion metrics are made.


## Authenticated read-only GitHub census — 2026-11-05 PT

Read each of the original 35 article bodies and 35 metadata files through the authenticated GitHub connector at exact R160 branch snapshot. Across these **70 repository files**: 35 article slugs and routes, **2,000 citation occurrences**, **385 article-specific source-use mappings**. Every observed citation ID appeared in its own article's source_use record and every listed article source appeared in its article body (**zero orphaned or unmapped relationships**). All 35 metadata records retained publish=draft and the original safety-state distribution of 29 pending, 4 not-required, 2 recorded approved. Readable text exceeded 1,500 words per article; the smallest observed citation count was 28. This was a static read/compare, not execution of R160 against a complete local checkout, not checking whether linked sources support the claims, not a safety/QD PASS, and not an authorized release. Exactly two recorded metadata approval labels must never be treated as independent release approval.
