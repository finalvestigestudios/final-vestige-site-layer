# R175 — Original-to-rendered editorial link graph custody (DRAFT / HARD HOLD)

**Scope:** Preparedness Archive only, issue #136; revenue coordination issue #820 and charter #818. Isolated stacked draft on R174 PR #1295 at `2d784366168271afbef729aa2845cb86cb92da23`. No merge, public publishing, WordPress/CMS/nav/home, email, new analytics, affiliate, social posting, purchases, or spending.

## New independent integrity boundary

The original R161 roster protects 35 article bodies / 2,000 source citation occurrences / 385 article-specific source relationships. R174 checks citation numbers, source URLs, per-article reading scopes and draft WordPress export. R175 **additionally** derives the expected hyperlink graph from the pinned original `{{link:slug|label}}` tokens, literal original inline links and `related` metadata, then independently compares those with generated WordPress-ready article-body and related-reading anchors.

R175 rejects missing/extra/reordered editorial links, label changes, wrong section or canonical path, injected affiliate/checkout/UTM/query destinations, silently dropped links to missing targets, duplicate draft routes, duplicate HTML IDs and local `#fragment` targets that do not exist (including TOC, citations, skip links). It preserves legitimate generated citation footnote anchors without counting them as editorial links. Original authored **draft tools** may legitimately appear in the target map, but are not counted as part of the immutable 35-article slate or represented as live. It emits a deterministic SHA-256 of the link receipt and counts, not any real conversion event.

The gate imports the original R174 and R161 checks and requires their immutable draft/citation state. The CLI always exits **2**, even on structural success, and reports `DRAFT_HARD_HOLD` or `INVALID_HARD_HOLD`. This is **not** QD PASS, authoritative source checking, food/medical safety approval or a publish decision.

## Locally executed tests and limits

- `python -I -m unittest discover -s /mnt/data/prep_r175/preparedness/tests -p 'test_r175*.py' -q` → **78 tests PASSED, 0 failed, 0 skipped** on synthetic/adversarial fixtures, including **50 mutated link destinations**. The fixtures do not contain any real family data.
- `python -m py_compile` on source and tests → PASS.
- Tested local Git blob IDs: validator `794524902ebdc9bcc4c61d0070ed94634633577c`; tests `2d29cc10ac8a470a9ae7d05b7733cf9afb6163da`. Recheck GitHub at this PR head before using them as evidence.
- This environment's `git ls-remote` cannot resolve `github.com`; **authentic source checkout, full `validate.py`, `build.py`, repository-wide 36+ tests, native 35-body R174/R175 proof, 35 genuine WordPress drafts and real browser/mobile/printing/accessibility were NOT executed here**. Synthetic success must not be conflated with these absent checks.

### Trusted full-checkout runbook (no publication)

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r174_rendered_citation_gate.py --repo . --check-export
python -I preparedness/tools/r175_link_custody_gate.py --repo . --check-export
```

**Do not use shell `|| true` to disguise the last two expected exit-2 hard holds**; read their JSON receipts and preserve any `INVALID_HARD_HOLD` failure as a blocker. Original articles and generated drafts remain unpublished. A staged rendered WordPress site must receive independent guest-browser and mobile checks before any release decision.

## Seven-cluster / independent-QA custody

At 2026-11-06 12:xx PT, exact pin→branch comparisons returned **identical 0 ahead / 0 behind** for: Start `2122d856fce9f64887c16df3d52e64be9f59a55b`, Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`, Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`, Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`, Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`, Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.

Independent QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` improves safety-gate tests and removes a dangerous live-breaker rehearsal; fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` isolates synthetic sources, extended by #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. **None is silently merged into R175.** Homepage #49/#604 remain separate. Human checks of 75 source decisions, 32 shared-URL scope groups and 10 jerky claim-locality selections, 11 Family Card review decisions and NCHFP/FSIS dispute remain unresolved (some groups overlap; do not add totals together).

## Conversion-first handoff: ONE audience, ONE authentic free draft, NO invented checkout

**High-intent subject:** school pickup and family contact/reunification during an emergency; caregivers wanting a printable household contact plan. **Authentic guide:** the original source-linked Household Emergency Plan (proposed `/preparedness/start-here/household-emergency-plan/`), `DRAFT/HOLD`; **optional practical free tool:** Family Reunification Card, `DRAFT/HOLD`, privacy, print and source checks outstanding. **Paid practical pack:** no currently purchasable, rights-cleared, matching Preparedness SKU has been authenticated; therefore there is **no enabled purchase link or implied commercial product**. The already-approved Focus Fieldbook remains the sole free subscriber offer, **not** a replacement for un-gated safety instructions. Never resurface the retired water freebie.

Proposed unpublished CTA (only after safety review): “Make a plan for how your household will reconnect. Read the free Household Emergency Plan.” Later optional card only after privacy/print/safety clearance. No unapproved urgency, health guarantee or claims of secure personal-data handling.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing paid Preparedness pack → verified paid order | No authenticated matching SKU, rights, purchase/fulfillment or refund proof | Commerce confirms actual Payhip listing, genuine downloadable deliverable and refunds **before** any purchase CTA | **HOLD, no SKU or paid sales authenticated** | Commerce / Claude |
| Household Emergency Plan → ungated free reader | Human source/safety/QD and native build outstanding | Run independent verification and draft WP/browser acceptance, keep public-service steps free | **DRAFT/HOLD; 78 synthetic R175 tests are not article approval** | Preparedness / Site QA |
| Free guide → optional Family Card | Source decisions and authentic print/privacy/mobile checks unresolved | Staged 360/390/768/1440 inspection with synthetic data | **HARD HOLD** | Preparedness / independent QA |
| Grok caregiver asset → correct guide | No published asset ID / permitted CTA placement / matching destination confirmed in shared TASK-008 v4 | Grok/Praxxis crosswalk actual `asset_id`, post URL, campaign, source rights, destination under existing creator queue; Mini Museum-first priority remains unchanged | **UNVERIFIED** | Grok / Praxxis |
| Qualified-human source sessions → independently confirmed paid net revenue | Confirmed checkout/orders, unique human sessions, refunds/fees and consent-safe matching absent | #820 contract: asset_id/UTM → human landing → resource CTA → confirmed optional lead → merchant-paid order/refunds/fees; 7/30-day cohorts | **NOT COMPUTABLE** | Claude / Commerce / Analytics |

**Landing/checkout acceptance:** matching content promise and destination; guide available without email gate; stable route/accessible CTA/visible source warnings at 360/390/768/1440; nonproduction privacy/print test; optional lead only via already approved infrastructure; only authenticated existing merchant checkout, full-file delivery, fee/refund policy and settled payment; no click counted as sale; `net revenue / qualified human sessions * 1000` only when both are independently observed. Record sample sizes, exclusions and attribution uncertainty.

**Not LIVE or VERIFIED.** Human food safety, medical and family privacy checks, source review, WordPress release and commercial authorization remain founder/qualified reviewers' responsibility.