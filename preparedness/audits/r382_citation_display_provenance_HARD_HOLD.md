# R382 — HTML citation display and claim-scope custody (DRAFT / HARD HOLD)

**Engineering scope:** Preparedness Archive only · Issues #136, #820 · founder charter #818 · 2026-11-14 PT. No permission to merge, publish, deploy, or edit WordPress.

## Why this matters

The 35-article original manuscript audit counted `{{cite:id}}` tokens. Counting a token does **not** demonstrate it is present in reader-facing content: an HTML comment, `script`, `template`, inaccessible `aria-hidden` region, a hidden style or an attribute can preserve the raw count while removing readable evidence. This independent R382 gate classifies those cases and reports original article-specific `source_use` gaps. It is deliberately stricter than token-count-only checks and remains fail-closed.

- New `preparedness/tools/r382_citation_visibility_gate.py`: static `HTMLParser` custody for visible text vs hidden/non-text citations, split/malformed tags, source-ID mismatch, absent article reading scopes, historic safety-state labels, repeated citations and limited-same-block claim context.
- The CLI uses the **original immutable nine-ref Git-object manifest** (35 body/meta pairs, 77 original object paths, nine unresolved object variants) and central BASE source register plus original fragments; it audits *all* original body/metadata branch variants and selects **none**. No original article/source/URL/metadata rewrite.
- New `preparedness/tests/test_r382_citation_visibility_gate.py`: synthetic matrix for original invisible/nontext/malformed cases, valid paragraphs/list/table/captions, historic status-label preservation and hard-hold invariants. Fixtures never write to source fragments.
- **Limits:** Static source parsing cannot prove output from WordPress transforms, CSS, 200% zoom, screen reader, no-JS, offline print, page load, live URLs or factual source sufficiency. Human review remains required even when static checks find no error.

## Exact code identities at review

- Source file Git blob `ce930b7d288ef702b5313ae81fbcc5c6a79d2e10`
- New test file Git blob `1208544c13f22cd7ef06b1201352fb8c6569e3fa`
- Branch base R381 commit `580e4514c326b4e9a1f74a17b918a59a003eee96`
- R382 new commits: `7af92fbb115b2b9a7a5834fd435e1a1fed7f2b3c`, `3a7614fbbf16a74004c3532518c60b08fabe08b0`; current HEAD finalized after this audit file.

## Execution categories

- **LOCAL PROTOTYPE TESTED:** A separately bundled equivalent offline R382 HTML custody prototype passed **59/59 new**, and **434/434 combined available isolated R374–R382 Python unit tests** with compilation under `-W error`. This is useful algorithm validation but **not byte-identical execution of the GitHub R382 tool/test files**.
- **COMMITTED / NOT YET EXECUTED:** Exact remote source and test Git blobs verified through GitHub readback. A native GitHub Python test run, repository `validate.py`/`build.py`, 35 real original variants in one authenticated checkout and authentic 50 WordPress/50 private-preview exports have **NOT** passed in this local environment. Local `github.com` DNS remains unavailable; Git-object-dependent CLI returns exit 2.
- **OPEN HUMAN HOLD:** Qualify Article #7 CDC water-source caveats and missing source-use scope; Article #11 wild-game food safety; the five original source payload discrepancies; nine Shelter Git forks; Article #15/Tool #104 child privacy, emergency wording and print geometry. R380 historical `approved` labels are founder labels, never independent QD PASS.

## Coordination at exact remote refs

- Nine original Claude/Shelter branch pins rechecked against the R374 manifest: **all nine identical, ahead=0, behind=0**.
- Independent QA #157: OPEN DRAFT `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`.
- Synthetic-fixture QA #169: OPEN DRAFT `e9cd7766dac59d47ab467d8945269b9146c2aef5`. The separate dependent temp-fixture correction #2205 remains OPEN DRAFT `bbcf1859768624c611df4abadc564c18247cf32a`.
- Homepage owner #1689 remains separate OPEN DRAFT `f55c36b6598eec558dd8bb24e4c8988becc51be0`.
- No QA/head branch was merged or modified.

## One conversion hypothesis and acceptance, NOT an offer launch

| OFFER → FUNNEL | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| One existing, genuinely purchasable FV Preparedness pack → paid order | No FV rights-cleared payable/deliverable SKU or tested refunds verified | Founder/Commerce authenticate rights, payment, delivery, fees and refund handling **before** any draft paid CTA can graduate | FAIL/UNKNOWN; zero authenticated merchant orders; **no paid CTA** | Founder/Commerce |
| Already-published Grok family-contact asset → existing free agency-backed /preparedness/ guide | No matching real published `asset_id`, hook, permissible UTM, rights and mobile link established | Praxxis independently check published permalink and intent; Grok retains creator/post role | UNKNOWN; do not invent attribution or repurpose unrelated asset | Grok/Praxxis |
| Existing free household guidance → optional practical Tool #104 | Card remains private with physical trim, privacy, emergency and QD holds | Print and accessibility checks with independent qualified review | FAIL/HOLD; not advertised as downloadable | Preparedness/QD |
| Qualified sessions → CTA → confirmed lead → merchant-confirmed orders → refunds/fees → realized net revenue | No confirmed sales or reliable unique-human 7/30-day denominator | Read-only event/data mapping per #820, no new tracking script | NOT COMPUTABLE; outbound clicks ≠ sales | Claude/Commerce |

Unposted free-only proposed CTA: **“Start With Trusted Preparedness Resources”** → `https://finalvestige.com/preparedness/`. This is a research draft, not a campaign, product SKU or promise of availability.

**HARD HOLD**: No publication, CMS/nav write, site script, email, social post, Grok task overwrite, affiliate/merchant activation, spend, merge or claim of medically safe advice.