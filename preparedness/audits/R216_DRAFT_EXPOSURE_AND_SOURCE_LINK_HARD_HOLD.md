# R216 — Draft content exposure, link targets and citation bibliography order — DRAFT / HARD HOLD

**Scope:** Final Vestige Preparedness Archive source/citation safety and integration, issue #136. Commercial coordination #820 / charter #818. Exact parent R215 PR #1575 HEAD `5c2a984d3e6dc1a3d2219a54bb255eb1d3607375`. R216 is isolated in an independent draft. **Nothing in this artifact authorizes a merge, release, medical-safety classification, source approval or CMS write.**

## Identified gap and new safety boundary

R215 verifies a body-text/citation sequence against the authored bytes. It can still be possible for the intact visible-text sequence to appear under a concealed *ancestor*, or for entire source/disclosure scopes to be hidden, while text and original citation numbers remain structurally present. A separate outbound anchor or a bibliography target can introduce an unsafe/incorrect scheme without mutating one of the three held source URLs. This is a **DOM/source transport** concern, not a review of the underlying advice.

New `preparedness/tools/r216_draft_exposure_guard.py` checks BOTH WP-ready and preview transports for the two held articles (original #7 CDC x2 and #20 Ready.gov x1). It requires a prior R215 DRAFT_HARD_HOLD result for the identical four SHA-256 render receipts; no prior approval flags may be true. Rejects concealed ancestors or sections (.pa-body, .pa-sources, .pa-chips, .pa-review), native hidden/inert/aria-hidden and selected inline hiding CSS, closed details/dialog/template containers, empty or duplicate scopes, malformed HTML/unsafe active elements, event-handler attributes, unsafe links and redirect/base overrides. Bibliography entries must be contiguous numbered `src-N` anchors with HTTPS links, and active new-tab anchors require `noopener noreferrer`. Rejects false approval language in draft/review scopes. Emits only **DRAFT_HARD_HOLD (exit 2)** or **INVALID_HARD_HOLD (exit 3)** with draft SHA-256 receipts, no write path. This is stricter than the previous transport parity check and may expose formatting problems in authentic generated drafts; a failure must be investigated, not bypassed.

**Limits:** Source text and external URL truth are not re-verified; any incoming R215 report must itself be generated from the authentic R214 dossier and frozen source/article bytes, not hand-crafted. This R216 gate does not independently authenticate that earlier chain; a forged R215 report is outside this standalone parser's protection. Inline CSS/DOM analysis cannot prove computed CSS, loaded stylesheets, actual WordPress sanitizer behavior, JavaScript effects, focus behavior, screen-reader behavior, mobile rendering, print output, or editor/clinician safety. CSS-hidden claims not represented inline may evade the parser and require real-browser QA. WordPress output compatibility is not certified.

## Reproducible locally executed tests (synthetic; NOT authentic repository suite)

- Exact committed Python content of tool and test was mirrored to the local runner, checked with Git blob SHA-1 after commits, and run with `python -I -m unittest discover -s preparedness/tests -p 'test_r216*.py' -q`: **103/103 PASS**.
- `python -m py_compile` for tool and test: **PASS**.
- 52 concealed-wrapper permutations (4 scopes × 13 wrappers), 24 malicious/unsafe URL mutations (12 in body, 12 in bibliography), 15 other negative integrity tests and 12 HOLD/prerequisite tests. Each mutating test establishes a clean synthetic baseline HOLD, recomputes the synthetic upstream receipt after mutation, then requires R216 INVALID—so rejection is not caused by a stale digest. These counts refer to synthetic tests, not original articles.
- Direct CLI synthetic complete input returned **exit 2 / DRAFT_HARD_HOLD**; same data with a hidden inherited `aria-hidden` guide body and regenerated prior digest returned **exit 3 / INVALID_HARD_HOLD**.
- Protected source Git blob SHA-1: `preparedness/tools/r216_draft_exposure_guard.py` = `92ab85f9592bd5b8f9a3d0e3177bb13ea8e22970`; test `preparedness/tests/test_r216_draft_exposure_guard.py` = `7abd3d50cb74e60f491dc4334fa40b59e3db6aa2`.

**NOT executed:** native `preparedness/tools/validate.py`, `build.py`, original 35-article slate/41 WordPress targets, authentic R214→R215→R216 dossier on Article #7/#20, real WordPress/browser, original fixture/QA suite, qualified source/medical review, independent QD or founder signoff. A full trusted local checkout remains blocked by `git ls-remote`: **Could not resolve host github.com**. Connected GitHub API is available, local git transport is not.

## Exact upstream custody checked this run, 2026-11-08 PT

- Claude Start Here `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.

Independent draft QA PR #157 = `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture PR #169 = `e9cd7766dac59d47ab467d8945269b9146c2aef5`, stacked follow-up #973 = `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`, none merged into original sources. Homepage lead PR #1580 = `b1a6b8c4ebe0fca4ee9a4755ac4913b5063bc619`, separate and untouched. Existing 35 original canonical routes, seven Claude authored branches and safety classifications are not modified. Unresolved source adjudication: Article #7 two CDC claim occurrences; Article #20 one Ready.gov occurrence; seven historical source-identity conflicts remain under HOLD.

## Founder business priority — ONE proposed household records offer; no activation

Audience hypothesis: adults organizing family emergency contact paths and locations of insurance/financial documents. One authentic public free starting point is `https://finalvestige.com/preparedness/`, which presently links to official household planning sources; detailed unpublished FV guides and worksheet are NOT public campaign destinations. One publicly listed **provisional** commercial candidate: `https://payhip.com/b/n1RhV`, **Legacy Triage**, advertised $19 / printable PDF, seller Vested Wisdom. Listing existence/description does **not** prove FV seller rights, merchant acceptance, secure delivery, support/refunds or paid orders. Product includes account/access-related records; completed worksheets require a clear privacy/separate secure-storage caution. Do not put secrets in web forms, public PDFs or campaigns.

**Draft CTA copy (INACTIVE, not a live link):** “Start with the free emergency-planning resources. If an optional paper organizer for family contacts and records would be useful, a paid printable is under commercial review. The free Archive requires no purchase or signup. Keep completed financial and account records securely stored.”

| Offer → funnel step | Blocker | Change / experiment | Current evidence | Owner |
|---|---|---|---|---|
| Existing Grok household records social asset → public archive | Actual published asset_id, rights, hook, post URL and destination unverified in TASK-008 | Read-only reconcile actual creator asset and match visitor-intent; propose organic-social UTM only after ID confirmed | UNVERIFIED, no attribution | Grok / Praxxis |
| Public archive → free official family preparation source | No approved original long-form Article #1 destination | Keep existing official links free; stage destination/mobile source-link and disclosure checks, no paywall | Live public archive; original guide HOLD | Preparedness / QA |
| Free official guidance → optional Legacy Triage | Product seller authorization, intent match, sensitive-credential handling and disclosure unknown | Rights/terms check, exact product preview and mobile CTA copy test before enabling | Listing only, COMMERCIAL HOLD | Founder / Commerce |
| Product page → merchant confirmed PDF fulfillment | Payment, tax/currency, file delivery, refunds and support unverified | Founder-authorized test purchase and delivery/return evidence, no shadow checkout claims | UNVERIFIED | Founder / Commerce |
| Qualified campaign session → net paid revenue | No verified asset-linked human sessions, paid order ledger, fees/refunds | Use existing consent-compliant measurement, 7/30 day cohorts with low-sample warnings | Net revenue/1,000 qualified human sessions **NOT COMPUTABLE**, not $0 | Claude Analytics / Commerce |

For a future campaign landing acceptance check: actual content asset_id, hook/CTA match, valid official source link, zero 404/redirect loops, keyboard and screen-reader accessible disclosure, 360/390px mobile rendering, optional paid tool explicitly separated, no paid CTA until rights/merchant/privacy/release gates clear. Do not invent events or install duplicate measurement scripts. Creator queue untouched. Existing /focus/ email magnet unchanged.

## Hard hold
No article edits, source-register changes, public slug changes, CMS/navigation/homepage writes, emails, analytics activation, merchant or affiliate change, Grok posting, spending, merge or publication occurred. All source/safety/QD and founder releases remain pending.