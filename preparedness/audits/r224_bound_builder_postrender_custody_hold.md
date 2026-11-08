# R224 — Bound builder import and post-render source custody (DRAFT / HARD HOLD)

**Scope:** Issue #136 Preparedness integration and source/citation gates only. Coordination #820, commercial charter #818. **Parent:** exact R223 head `ffe213458282de9221da79e0d25ed84f58a6298a` (draft PR #1627). **Date:** 2026-11-08 PT. No production changes authorized.

## Independently identified risk and surgical engineering repair

R220's exporter preflight authenticated 20 input files through R222, then used `sys.path.insert(...); import build`. In a long-lived Python interpreter, a previously imported `sys.modules['build']` could be reused even though it was not the just-validated `preparedness/tools/build.py`. This broke the execution-time evidence binding. Additional risk: an input could change after preflight but before the rendered-output custody check.

R224 edits **only** `preparedness/tools/r220_full_slate_draft_custody.py` and introduces a Preparedness-only regression suite:

1. `load_frozen_builder` reads `tools/build.py` after the R222 preflight using R220's no-symlink path reader; requires the exact R222-pinned Git blob, compiles those exact bytes into a **new private module** with correct `__file__`, and validates required producer APIs. It never uses `import build`, the global module cache, or manipulates `sys.path`.
2. The builder is read and hashed **again after module initialization**; a producer file changed during binding fails closed.
3. After evaluating the 41 reported WordPress/preview drafts, R220 **re-runs** frozen producer/source bundle, frozen taxonomy/tool source, and original 35 article/meta checks. This narrows the interval where post-preflight mutation could invalidate custody while preserving all source exceptions and HOLD-only outcomes.
4. No changes to authored text, 35 original article bodies or metadata, 6 tools, taxonomy, source register/crosswalk, HTML exports, URL routing, Wordpress, CMS, navigation, analytics, affiliate products or social assets.

## Exact test/evidence boundaries

Local **isolated synthetic** Python test fixture contains the byte-equivalent R224 loader function; **60/60 Python unit tests PASS**, including 42 distinct unauthorized producer-byte mutations, a forged `sys.modules['build']`, symlinked module/file rejection, preflight drift, a during-import source swap, malformed receipts, invalid syntax/encoding, required API, and no global module/path pollution. Isolated Python compilation PASS.

The GitHub-committed source and new test file are reviewable on this draft PR. Local runtime **does not** have an authentic clone: `git ls-remote` fails `Could not resolve host: github.com`. The entire committed R220 module, committed test file *as a full unit*, authenticated R222 producer, all 35 real articles, all 41 target exports / 82 channel files, native validate/build and independent QD have **NOT** run. Do not represent 60 synthetic passes as complete repository QA or a publication pass.

The exact original producer Git identity remains `349173d1e1d735eade218d95c7a0a2649c8cccd9`; remote source review confirms no relative imports, `__spec__`, or `__loader__` dependencies in this producer, but that is static compatibility evidence only.

## Coordination identity check

All seven original Claude cluster heads compared **identical** to frozen receipts on 2026-11-08:

| Cluster | Original head |
|---|---|
| start | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| hist-field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| hist-food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| hist-home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independent QA draft #157 head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic-fixture draft #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` and follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` all remain separate/unmerged; no blind cherry-picks. Homepage lead #1620 head `d20027e1dbba058ae4f0008f8d9f1ce291c1f82d`, untouched. R224 is stacked on earlier Preparedness drafts, not ready for merge.

## Outstanding release blockers

- Article #7 has two CDC `cdc-find-clean-water` citation explanations outstanding; Article #20 has one Ready.gov `start-ready-plan` citation explanation outstanding. Seven shared-source IDs need independent reading-scope adjudication.
- Native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, full `python -I -m unittest discover -s preparedness/tests -v`, and `python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness` in an authentic exact checkout, plus first-party WordPress/preview inspection and qualified water/food/medical/CO reviews.
- R224 fixes runtime producer identity caching; it does **not** guarantee all future reads are atomic or deliver an independent medical/QD approval. Repeated custody checks are additional detection, not proof against an attacker with continuous write access.

## Conversion-first, **draft-only** acceptance (no CTA activation)

**ONE high-intent audience/topic:** A household managing emergency contacts and essential documents during an evacuation or caregiver absence. **Live free source-backed destination:** `https://finalvestige.com/preparedness/`, “Create a household emergency plan,” linking to an existing Ready.gov/FEMA checklist. Do **not** direct campaigns to unpublished /preparedness/start-here/ long-form articles.

**ONE provisional optional paid candidate:** Legacy Triage `https://payhip.com/b/n1RhV` publicly lists a $19 printable PDF records organizer. A live listing is NOT verified seller rights, secure credential handling, a successfully delivered purchase, merchant acceptance, refund handling, or actual revenue. Optional draft CTA, disabled: “Use the free FEMA planning checklist first. A separate printable document-and-contacts organizer may be available as an optional paid download after product review. Store completed records securely; do not put account passwords in publicly shared copies.” No created/re-enabled lead magnet or merchant button.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / ACCEPTANCE CHECK | EVIDENCE | OWNER |
|---|---|---|---|---|
| Published Grok asset → official checklist section | Actual asset ID, URL, factual hook and mobile destination unverified | Praxxis/Grok TASK-008 match real media URL/date/rights, `utm_campaign` and `utm_content=asset_id`; no queue edits | NOT VERIFIED | Grok / Praxxis |
| Free checklist → deeper article | Author safety/citations and native build incomplete | Keep free first-party source, execute genuine pipeline and qualified review | HOLD | Preparedness / QA |
| Free guide → optional Legacy Triage | Seller/rights, content fit, privacy and disclosures unverified | Founder/Commerce inspect entire PDF, credential-handling advice, claims and explicit optional-price disclosure | NOT APPROVED | Founder / Commerce |
| CTA → checkout/payment/fulfillment | Real mobile checkout, receipt, download, refunds unverified | Authorized mobile 360/390/768/1440px + keyboard checks; completed paid test with merchant evidence | NOT TESTED | Commerce |
| Qualified sessions → realized net | Verified human campaign denominator and settled transactions unavailable | 7/30-day cohort attribution: unique asset/session → CTA → confirmed lead if any → independent order → refunds/fees → realized net | NOT COMPUTABLE | Analytics / Commerce |

**Primary KPI:** 1000 × (confirmed settled gross paid revenue − refunds − processor/platform fees) / qualified human sessions, when the denominator is authentic and >0. Separate paid conversion, qualified human sessions, confirmed customers, revenue and lead-to-customer; small cohorts require caution. Outbound clicks, signup UI, affiliate links, followers and checkout starts are not sales.

**Release:** BUILT / SYNTHETICALLY TESTED / DRAFT_HARD_HOLD. No merge, production publishing, navigation, CMS, merchant, analytics, email, social content, paid service or spending.
