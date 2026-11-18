# R469 — literal citation visibility custody (DRAFT / HARD HOLD)

**Repository:** finalvestigestudios/final-vestige-site-layer · **Owner lane:** Preparedness Archive source/citation integration only (#136) · **Business charter:** #818/#820 · **Date:** 2026-11-18 PT.

## New engineering / scope

R468's context docket preserves citation IDs, 2,000 occurrences, reading scopes and paragraph SHA witnesses but does not independently reject citation tokens that have been moved inside explicitly hidden markup or HTML attributes. R469 adds a **read-only, fail-closed** literal-HTML inspection. It checks hidden/inert/aria-hidden nodes, inline display/visibility/content-visibility/opacity, nonvisible containers, citation-bearing attributes/comments/scripts, malformed/unbalanced markup, duplicate/conflicting attributes or CSS properties, forbidden base/meta/link, noncanonical citation tokens and citation order versus R468 witnesses. It separately counts *closed details* as human-review indicators rather than silently approving them.

Every gate output keeps `qualified_qd_pass=false`, `may_publish=false`, `claim_support_verified=false` and `DRAFT_HARD_HOLD`. No article, source register, WordPress export, public URL, product, content queue, live script, or CMS item was changed. This does **not** establish computed CSS visibility, JavaScript behavior, keyboard/screen-reader access, source authenticity, official source currency, or medically safe advice. No hidden-citation defect is asserted in any original article merely from the existence of this protection.

## Test and source evidence

- New source: `preparedness/tools/r469_citation_visibility_custody.py`, exact local and remote Git blob `55b2a41afcb6f37a0df467b77406ec1a49f07409`.
- New tests: `preparedness/tests/test_r469_citation_visibility_custody.py`, exact local and remote Git blob `b81fc2653b02a95fc2c662df0354eefcf8526e50`.
- `python -I -m unittest discover -s preparedness/tests -p 'test_r469*.py' -q`: **81/81 PASS**, local exact file.
- Isolated inherited local tests from R463/R464/R465/R466/R468 plus R469: `python -I -m unittest discover -s preparedness/tests -p 'test_r46*.py' -q`: **777/777 PASS**, local test assembly. No native original-article build claim.
- `python -I -m py_compile preparedness/tools/r46*.py`: **PASS**, local.
- Native R469 probe with incomplete local source checkout: **exit 2, VISIBLE_CITATION_FAILURE_HARD_HOLD** (missing pinned original R468 dependency), not PASS.
- This run fetched **all 35 integrated candidate authored body files** through the authenticated GitHub connector at R468 SHA `8663dea632eee8b4bda697944e9a3471ba78d703`, and independently compared their Git blobs against R460's frozen candidate list: **35/35 match**. They were not materialized as a complete runnable Python checkout, so no native full build or genuine WP/private-preview test is claimed.
- Nine frozen contributor HEADs were independently rechecked unchanged. QA #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, and repair #2205 `bbcf1859768624c611df4abadc564c18247cf32a` remain open draft, not merged. Apollo/home PR #3037 `415cd4e08c0cef472b77397a594331a325d5b3f6` and Article #11 editorial PR #2789 `40a134ba233785bc1f6c779705e49b19672e58fd` were read, not edited.
- Original unresolved decisions remain **five source disputes, nine original manuscript forks, 17 divergent articles and 32 reading-scope shared-URL review groups**. Independent qualified medical, emergency, food, child privacy, editorial/QD review has **NOT APPROVED** release.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE / STATUS | OWNER |
|---|---|---|---|---|---|
| One actual FV-owned/licensed, sellable Preparedness practical pack | Merchant-confirmed paid order → fulfillment | No authenticated **currently payable** SKU, rights, terms, delivery, refund/fee or settlement | Founder/Commerce read-only authenticated product and checkout receipt; only then propose optional differentiated pack | **HOLD**; no verified paid pack or sale | Founder/Commerce |
| Existing free ungated `https://finalvestige.com/preparedness/` agency-reference Archive | Published Grok family-contact/reunification asset → qualified visit | No independently matched genuine published asset_id, hook, rights or signed-out permissible mobile destination | Praxxis validate one actual posted asset in TASK-008, do not edit Grok's queue | **UNMATCHED**; no attributable human sessions | Grok/Praxxis |
| Original family-contact guide → optional free Tool #104 | Relevant guide reading → useful download | Article #15 accuracy, child privacy, printing/accessibility and independent qualified QD gates not cleared; distinct Tool #102 must remain distinct | Draft only: “Review official household emergency-planning resources”; do not link Tool #104 or gate free advice | **HARD HOLD**, no public CTA | Preparedness/QD |
| Optional cleared paid pack or verified affiliate → order | CTA → checkout → confirmed order → net revenue | Merchant attribution, order/refund/fees and 7/30-day qualified cohorts missing | Review consent-respecting attribution with Claude; no duplicate tracking scripts | **NOT COMPUTABLE** net revenue/1,000 qualified humans | Claude/Commerce |

### Next gate

Obtain **native original checkout** with full pinned branch source and actual WordPress/private outputs, run `validate.py`, `build.py`, R463→R469 and 36+ native tests. Human adjudicate author/source forks and qualified safety claims. Do not merge/publish/activate until founder authorization and independent review.

**No publishing, CMS/navigation writes, analytics deployment, social posts, emails, commerce activation, affiliate conversion claim, spending, or QD PASS.**
