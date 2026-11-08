# R222 — Producer/source custody before WordPress build (DRAFT / HARD HOLD)

**Governing issues:** Preparedness #136; revenue/attribution #820 and business charter #818. **Parent:** R221 PR #1614 at `e5092c99ddcc8e2a73bdfb86514794c168c61a08`. All changes are Preparedness-only and unpublished. No WordPress/CMS, navigation, homepage, social, email, merchant, analytics, or spending writes.

## Independent finding and implementation
R221 freezes the taxonomy and six tool input pairs, but R220 subsequently imports `tools/build.py` and resolves citations with `sources/register.json`, `sources/fragments/*.json`, `sources/crosswalk.json`, scripts and CSS **without checking these producer/source Git blobs in the R220 entry point**. A forged or accidentally changed build engine/source bundle could yield internally consistent render reports and make frozen bodies insufficient to prove the rendered evidence's origins.

R222 adds a fail-closed, read-only gate pinning exactly **20 observed R221 Git blobs**: the original `build.py`, `preparedness.css`, base register, source crosswalk, seven author fragment JSON files, and nine inline JavaScript source files. It rejects altered/missing/truncated/symlinked inputs, and extra `*.json` fragments or `*.js` producer files. The R220 custody entry point now checks the **exact pinned Git identity of the R222 gate** and runs it **before** its builder import. R220/HOLD is unchanged: this does not approve any citation, medical/household-safety claim, or document for publishing. A legitimate future change requires independently reviewed pin refresh, not a silent build-output repair.

### Evidence / execution
- Fresh R221 root for engineering changes: `e5092c99ddcc8e2a73bdfb86514794c168c61a08`.
- New gate Git blob: `31ee5604ccff115ded6b856ec175fa82776e08eb`.
- Original R220 pre-edit blob: `ef4cf02b495f23a2456d6bfa07441802f4e8fa46`.
- New R220 with pre-import custody check: `fef3ff76f7c2906b2a072c76773d54db1fda6f22`.
- Python 3 local execution of exact committed new gate and tests: **89/89 PASS**, including **80 file mutation cases** (20 inputs x modification, truncation, deletion, symlink) plus directory-closure and fail-closed tests. Python `-I -m py_compile` passed.
- The 20 expected Git blobs were collected from the authenticated R221 GitHub contents directory metadata. Synthetic fixture results are **not** an authentic 35-body/41-output run.
- Local direct Git checkout: `fatal: Could not resolve host github.com`; native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py` and full repository regression suite **NOT EXECUTED**. The actual WordPress 82 draft/preview exports remain **UNVERIFIED**.
- R220/R221 prior independent synthetic tests: reported, but **not rerun here**; do not aggregate separate test counts into this round's execution.
- All article sources, body text, metadata, safety labels and WordPress drafts **unchanged**.

### Current exact seven contributor heads, read 2026-11-08
| Cluster | Head SHA |
|---|---|
| start | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| hist-field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| hist-food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| hist-home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independent QA PR #157 (safe drills, refrigerated medications, publisher classification, taxonomy) and synthetic fixture PR #169 + follow-up #973 (isolate synthetic fragments in temp copies) were inspected from their current patches; **not merged or adopted**. The independent homepage lead PR #1620 at `d20027e1dbba058ae4f0008f8d9f1ce291c1f82d` was inspected but untouched.

### Outstanding blockers
- **Three unexplained citation occurrences:** Article #7 CDC `cdc-find-clean-water` x2, Article #20 Ready.gov `start-ready-plan` x1. Seven historical conflicting shared source IDs await qualified source-scope adjudication.
- Full 35-article source/citation validation, 41 route/export reconciliation, 82 output-file custody, native build and independent source/safety/QD review required. Prior branch/OID reconciliation is *custody*, not qualitative approval.
- R222 preserves the existing R219/R220/R221 draft stack; contributor work must not be flattened or published.

## Conversion-first acceptance, **not** a live CTA
**One high-intent social angle:** households gathering contact, insurance and essential-document information before a power outage or evacuation. Grok owns creation/posting; Praxxis reconciles existing posted asset URL, `asset_id`, media rights, factual hook, actual mobile destination, permitted `utm_source/utm_medium/utm_campaign/utm_content` via existing TASK-008 (no new creator queue or invented IDs).

**Free:** original article #1 `household-emergency-plan` is source-backed but **unpublished and under safety/source review**; current public `/preparedness/` remains the available ungated destination, without representing the draft article as live.

**Optional candidate:** Legacy Triage printable is **not yet verified as seller-owned, rights-cleared, correctly disclosed, securely usable, delivered, refundable or successfully purchased**. Its convenience cannot gate free preparedness information; caution that completed household records may include sensitive financial/login details.

**Proposed on-site copy, staging-only, DISABLED as a commercial CTA:** “Make the household plan first. Start with the free Preparedness Archive; it never requires a purchase. An optional printable document organizer may be offered separately after we verify its contents, data-handling cautions, seller rights, checkout and delivery.” Do not publish or link a paid button now.

| Offer → step | Blocker | Change / acceptance check | PASS/FAIL evidence | Owner |
|---|---|---|---|---|
| Grok asset → free archive | Genuine asset ID, post URL and mobile link missing | Reconcile TASK-008 existing published items only | **UNVERIFIED** | Grok/Praxxis |
| Archive → original free guide | 3 citation occurrences; 7 source conflicts; independent QD missing | Run native 35/41/82 checks and qualified review | **HARD HOLD** | Preparedness/independent QA |
| Free guide → optional Legacy Triage | Rights, privacy, matching audience, seller disclosures unknown | Inspect owner authorization and redacted actual pack | **NOT APPROVED** | Founder/Commerce |
| Optional paid CTA → confirmed order | Merchant test, fulfillment and refund process unknown | Authorized mobile checkout/delivery verification (not a fictitious sale) | **NOT TESTED** | Founder/Commerce |
| Qualified sessions → net revenue | Asset attribution + merchant verified orders/fees/refunds missing | Reconcile 7/30-day privacy-safe cohorts; only true purchase is paid conversion | **NOT COMPUTABLE** | Analytics/Commerce |

**Metric contract:** verified net revenue / qualified human sessions × 1,000, only when audited denominator > 0 and attributable transaction/fees/refunds complete; zero/negative net revenue is valid if verified. No claim from pageviews, affiliate outbound clicks, checkout starts or unconfirmed lead states. No duplicate analytics scripts or spending.

**Release state remains DRAFT / HARD HOLD.** Founder retains release/payment approval. No creator posting, site, merchant or CMS writes here.
