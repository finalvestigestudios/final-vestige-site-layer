# R440 — Original 35-article / nine-branch docket replay (review only)

**Authority: Issue #136, commercial governance #820, charter #818. DRAFT / HARD HOLD.** Stacked on the frozen R439 draft #2890 at `672d67a9783119821c2e599e853b607b9b3ac4fa`. Additive only. This does **not** reconcile editorial disagreements by selecting a winner.

## Scope and engineering
- New `preparedness/tools/r440_original_slate_evidence_replay.py`: replay the original R397 Git-pinned source/fork docket; reject missing/duplicated article identities, drift in exact frozen cardinalities, unsupported contributor identities, source-support/reading-scope loss, route and citation/source-use inconsistencies, lost shared-URL review groups, and premature human-approval or variant selection. Optionally inspect actual checkout pairs with protected non-symlink/hardlink bounded reads, Git blob SHA-1 calculation, citation tokens, metadata safety states, internal article links, and source-use mapping.
- New `preparedness/tests/test_r440_original_slate_evidence_replay.py`: 70 synthetic unittest methods, including adversarial path escapes and fake human approvals.
- **Reviewer-only hard hold regardless of structural test results.** `main()` always returns exit 2; it cannot publish, merge, activate a merchant, give qualified safety approval or mark QD PASS.
- Uses no network calls, scripts, CMS changes, tracking scripts, affiliate writes, shell Git invocations or data mutations.

## Exact original docket observed from GitHub
Original R397 JSON blob `86d22a1d504c93db7689b914e2202a7845b648e2`, branch R439: 35 distinct slugs, 77 original object paths, seven source fragments, 203 source IDs/280 appearances, 17 shared exact-URL groups, five scope disputes and nine unselected manuscript/source paths. All selected source and fork decisions remain NULL. Exact SHA-pinned branch set: seven Claude clusters and two Shelter descendants. Their nine current branches were individually compared against R397 pins: nine IDENTICAL, zero commits ahead/behind (2026-11-17 PT).

### Original five unresolved source disputes
`fsis-power-failure`, `loc-pioneer-diaries`, `loc-prairie-traveler`, `nchfp-home`, `nchfp-jerky`. Each retains two recorded variants and original supports and reading-scope notes. Original nine forks are four body/metadata pairs for family communication, fire escape, outage/CO generators, shelter-versus-evacuation, plus `sources/fragments/shelter.json`. **Do not select a longer text merely because it has more words.**

## Real local execution (assembled subset, not a complete original checkout)
- `python -I -m unittest discover -s preparedness/tests -p 'test_r440*.py' -q`: **70/70 PASS**.
- R430–R439 inherited synthetic subset: **637/637 PASS**.
- One combined Python TestSuite of exactly those files: **707/707 PASS**, 16.306 seconds, exit 0.
- Python compileall: PASS.
- Missing original docket/evidence CLI: **exit 2**, `DRAFT_HARD_HOLD`.
- New implementation and test Git blobs were independently fetched after upload and matched the locally executed files.
- This does NOT mean authentic full-repository `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, or full offline suite has been executed. **No authentic WordPress/private-preview export pairs; no independent safety/QD or real-browser run.**

## Authentic validation invocation on a trusted checkout (not executed here)
```bash
python -I preparedness/tools/r440_original_slate_evidence_replay.py \
  preparedness/reviews/r397_original_source_fork_docket.json \
  --repo-root . --branch-heads /absolute/path/independently-observed-branch-heads.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```
Pass an externally recorded exact nine-branch name→SHA map; self-reported pins in the docket do not establish a live branch read. A code-only structural report never certifies original claims as medically/operationally safe. If any originals differ from allowed Git blobs, **preserve the original and place the drift on the adjudication queue** instead of silently replacing it.

## Reviewer and conversion priorities
Independent QA #157, synthetic fixture #169, dependent draft repair #2205 and home lead #1689 were read and left unchanged. Editorial #2789 is separately active on Article #11; leave the underlying manuscripts and food safety state untouched.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER**
1. One *already-existing* FV Preparedness paid pack → paid order → seller rights, actually payable SKU, fulfillment, refunds and net proceeds **not independently authenticated** → Founder/Commerce validates read-only seller/checkout records → **HOLD; no paid CTA**.
2. Previously published Grok family emergency-contact asset → official free `/preparedness/` → authentic asset ID, rights, hook and mobile URL not matched → Praxxis/Grok TASK-008 researches a genuine published asset → **UNMATCHED**.
3. Free official checklist → optional Tool #104 → Article #15 emergency guidance, child privacy, print accessibility, Tool #102/#104 identity unapproved → qualified Preparedness/QD → **HARD HOLD**.
4. Qualified human sessions → CTA click → confirmed lead → merchant-confirmed paid order − refunds/fees → net revenue/1000 qualified humans over 7/30d → merchant and attribution evidence missing → Claude Commerce/analytics → **NOT COMPUTABLE**.

No claimed conversion lift, paid sales, source safety approval or product launch. No WordPress/CMS, public post, navigation, sitewide analytics, email, affiliate, merchant, finance or production changes.
