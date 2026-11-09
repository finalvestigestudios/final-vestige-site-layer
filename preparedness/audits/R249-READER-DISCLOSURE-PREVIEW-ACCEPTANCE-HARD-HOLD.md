# R249 — Article #15 / Tool #104 plain-language reader preview (UNAPPROVED)

**2026-11-09 PT · Preparedness Issue #136 · conversion Issue #820 · business charter #818. DRAFT / HARD HOLD; no production release.**

## Decision-neutral engineering scope

R248 proved that the *current*, not-yet-published Tool #104 prints six populated user fields in shorter mode (Household, household Phone, out-of-area Contact, out-of-area Phone, first Meeting place, Reviewed date), compared with thirteen in full mode. The original descriptions understate household identifiers. Its no-JavaScript notice contradicts the hidden interactive form; a separate blank printable fallback exists. Its unconditional written-plan statement and privacy/retention claims require independent review. These are reader-copy and print-handling concerns, **not observed exfiltration**.

Editorial E248 identified **Option A** (change JS model, then separately review the consequences of omitting identifiers) and **Option B** (retain six actual fields but describe them honestly as a *shorter* card). **R249 stages *only* an unsigned, offline Option B preview; it does not select A/B, patch original content, alter original JS, or resolve the 11 pending E247 decisions.** Original 35 article bodies, six tools, source records, citation counts, routes, states, and seven Claude branches remain untouched.

### Files and deterministic safety boundary

- `audits/r249_family_card_reader_disclosure_draft.html` — static WordPress-ready *candidate* fragment (Git blob `ce5c363786deb0296f78598818af1fd7abefae65`), one existing free `/preparedness/` destination, no form, script, merchant/affiliate CTA, tracking, input or paid product.
- `tools/r249_reader_disclosure_preview_hold.py` — read-only, fail-closed parser/visible-copy checker (blob `7952b897d26e2496b371d9f4fab517cef1c7011d`). Requires six-field, thirteen-field, seven-field, JavaScript-off, paper-loss and conditional-review disclosure; forbids unsafe HTML/resources/URLs, misleading guarantees and promotional checkout links. Returns HOLD and explicit false approvals.
- `tests/test_r249_reader_disclosure_preview_hold.py` (blob `f7874b42584aba009fcd617fd7511643eaf4020d`) — 76 committed-file exact-byte regression tests including omission, marketing/assertion, structural, HTML/script/links/hidden/external-resource negative controls.
- `tests/r249_browser_smoke.py` (blob `2894d90a10afee61cbf3e7ec839f71b93c6a0e62`) — optional isolated Chromium smoke, synthetic set_content; not the original Tool #104 browser.
- `tools/r220_full_slate_draft_custody.py` — adds independent Git-blob pins for R249 gate and preview, runs the preview audit after R248's original five-source check and **before** WordPress draft export, then rechecks both source identities at the end. Never converts HOLD to source/QD/medical/merchant or release approval.

### Execution evidence versus limits

- 76/76 isolated Python unittest regressions **PASS** on local copies whose Git-object identities **exactly equal** the committed PR's module, HTML preview and tests.
- Python `-I -m py_compile` **PASS** for all three Python artifacts.
- 20/20 isolated Chromium assertions **PASS**: the authored preview under JavaScript ON/OFF at 320/360/390/768/1440 px in screen and print media, one free internal link, zero scripts/forms, zero network requests, no horizontal overflow in those fixtures. These are **preview-only**, not real WordPress delivery or actual family-card JS/storage/print testing.
- Native complete repository checkout remains blocked by `Could not resolve host: github.com`. Therefore full native `preparedness/tools/validate.py`, `build.py`, inherited 36+ tests, actual 41 WordPress drafts and original Tool #104 browser/network/print verification **NOT EXECUTED**. The new R220 callsite was inspected statically, not tested in the full checkout; this is **NOT an independent QD PASS**.
- Seven original Claude cluster heads freshly compared against frozen R200: **7/7 identical** as of this review. Independent draft QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`; homepage lead #1689 HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`: all read-only/untouched.
- 32 shared-source claim groups and three original citation disputes (CDC twice in Article #7 and Ready.gov once in #20) remain unadjudicated, alongside Tool #104 privacy/no-JS/field-exposure claims and separate safety concerns for hazardous procedures.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Offer / funnel step | Blocker | Acceptance change/experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Existing free Archive: original Grok video → free landing | Authentic matching published asset_id, platform post, rights and mobile tap path absent | Read TASK-008 and verify *already-published* match, not a new creator assignment | **UNVERIFIED** | Grok / Praxxis |
| Free Archive → held Article #15 / Tool #104 | Misdescribed six-field shorter card; no-JS and privacy wording still inaccurate/untested | Review unsigned Option A/B, independently sign any changes, then test authentic WordPress/browser/printed card | **R249 preview 76 Python + 20 Chromium isolated PASS; source release HARD HOLD** | Preparedness Editorial / independent QA |
| Free guide → one optional owned practical pack (provisional Legacy Triage) | Product not yet judged appropriate or rights/secure handling/delivery cleared | Review full product, evidence provenance, buyer need and founder authorization before enabling ANY paid CTA | **NOT APPROVED** | Founder / Commerce |
| Optional paid pack → confirmed paid order | Merchant checkout, exact downloadable file delivery, refunds and fees unverified | Authorized seller-side acceptance / independently confirmed orders, no fake purchases | **NOT TESTED** | Commerce |
| Qualified Grok session → CTA → lead → settled purchase | Asset tagging, human-session integrity, buyer/lead consent, merchant settlement data missing | Reconcile 7/30-day cohorts (explicitly clicks ≠ orders; no extra scripts) | **Realized net revenue / 1,000 qualified humans NOT COMPUTABLE** | Praxxis / Claude analytics / Commerce |

**No activation:** No publishing, merging, WordPress/CMS/nav/homepage writes, source/metadata status changes, emails, social posts, Grok task-queue edits, analytics vendors, affiliate activation, product listing, spending or assertion of medical/retention safety. Next: obtain named editorial A/B choice, authentic Tool #104 browser-print/network verification, full native 35/6/41 validation, independent citation/safety signoff, and approved merchant conversion evidence.
