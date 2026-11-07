# R202 — Closed-world branch directory + article-scoped citation custody (DRAFT HARD HOLD)

**Governance:** Preparedness Issue #136; conversion attribution Issue #820; charter #818. **No approval to merge or publish.** R202 is isolated atop draft R201 (#1478, `9b7c24643b0b24a27eca23fb2bd203111815dcb0`).

## What changed, and why it matters

R201 authenticated 142 **declared** original/inherited paths across seven fixed Claude branch trees. That positive-list proof did not reject an undeclared eighth copy of a body or metadata file, an orphan/partial pair, or a nested shadow document elsewhere in `preparedness/content/articles/`. A blind merger could potentially ingest such unlisted files.

`preparedness/tools/r202_directory_and_source_closure.py` closes that omission: it enumerates the **whole** articles directory from each of seven pinned original commit objects with `git ls-tree -r -l -z`, compares **the complete set** to the immutable R200 35-article/71-witness roster, rejects unexpected and missing paths, compares regular-file Git mode, type, SHA and body/metadata sizes, then reads all **35 exact owner-branch metadata blobs** and rejects changed article identity, non-draft publishing states, non-pending/claimed safety reviews and altered provenance.

The crosswalk then verifies every metadata `source_use` identifier is in the original global source register OR in the article owner's cluster fragment; unrelated cluster-only sources are excluded. Each claimed source-use explanation is individually fingerprinted. Competing global/owner origins are **reported together for human review**, never silently aliased; `hist-food-nchfp-jerky` is not treated as `nchfp-jerky`. This is source-reference existence, **not** claim-truth, advice-safety or human URL verification.

`DRAFT_HARD_HOLD` (exit 2) means structural consistency only. `INVALID_HARD_HOLD` (exit 3) means missing evidence or a failed invariant. Neither is QD_PASS. Merchant purchases and revenue stay null.

## Independent read-only provider observation, 2026-11-07

Authenticated GitHub Git-tree API returned all seven article subtrees at the exact R201 tree IDs, and the seven live contributor ref SHAs matched the frozen source identities:

| Branch | Current commit | Directory files |
| --- | --- | ---: |
| start | `2122d856fce9f64887c16df3d52e64be9f59a55b` | 20 |
| shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | 20 |
| food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | 20 |
| health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | 18 |
| hist-field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | 18 |
| hist-food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | 24 |
| hist-home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | 22 |
| **Total** | **7/7 heads unchanged** | **142** |

Against all 35 original article rows and 36 identical inherited witnesses: **142/142 Git tree SHA, size, type and mode matches**; zero extras, zero missing, zero duplicate paths, zero truncated trees. This authentic remote inspection is narrower than full Python/native execution and does not prove HTML, sources or safety claims.

## Tested versus blocked

- **BUILT:** standalone Python gate plus 128 real unittest methods, including 105 per-article body/metadata/safety corruption cases; synthetic fixtures only.
- **LOCALLY TESTED:** `python -I -m unittest discover -s preparedness/tests -p 'test_r202*.py'` **128/128 PASS**; exact source Git blob `7d05d80277a7571e67ff3bf3228635fb734c767c`, exact unittest blob `2dc2e7c7d458d704450cf54b1a411ccccad819b6` match the GitHub-committed files. `python -I -m py_compile` PASS.
- **NOT EXECUTED:** whole-repository native `python -I preparedness/tools/validate.py`, `build.py`, full `unittest discover`, R202's authentic 35-metadata/source-crosswalk read, rendered 41 WordPress-ready outputs, browser/accessibility/print/privacy and independent QD. Local git clone attempt still errors: `Could not resolve host: github.com`. Do not imply that synthetic results validate editorial citations or medicine/food safety.
- **Independent QA:** draft #157 (start safety repair) and drafts #169 / #973 (isolated food test fixtures) remain distinct and unmerged; #157/#169/#973 all touch `preparedness/tests/test_preparedness.py` and require conflict-aware review. No changes were made to their branches.
- **Separate editorial lane:** a WordPress **draft** household-records-map page #2150 was reported in #136; do **not** confuse it with an approved source-controlled 35-article release or modify its CMS state.

## Authentic offline review commands (trusted checkout with all seven branch commits)

```sh
python -I preparedness/tools/r202_directory_and_source_closure.py --repo . --report /tmp/preparedness-r202.json
# exit 2 = structural DRAFT_HARD_HOLD, never publish approval
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Independently inspect every source collision, historic and modern food safety, medications, child privacy, accessibility and 41 WordPress drafts. Preserve all original body/citation bytes and routes; no source, safety or route rewrites in this PR.

## Conversion-first, single candidate; no commercial CTA now

**Audience:** households planning emergency continuity of essential identity, insurance, financial and out-of-area contact records. The only presently supportable free public destination is the existing `https://finalvestige.com/preparedness/` official-resource gateway. The Household Emergency Plan (unpublished) and optional free Family Reunification Card (unpublished) cannot be linked as live destinations until source, safety, child privacy and printing acceptance. The Focus Fieldbook remains the sole approved sitewide lead magnet and is untouched.

**Candidate optional paid pack:** Legacy Triage — **not authenticated as active/purchasable, rights-cleared, audience-fit, fulfilled or refundable**; no offer/price/checkout CTA in this branch. No retired water magnet, invented product or paid service.

**Offer → funnel → blocker → experiment → evidence → owner:**

| Offer/funnel step | Blocker | Required test/change | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Legacy Triage → paid order | No authenticated product rights/listing, fulfillment/returns or real merchant purchase | Seller-access-controlled SKU/terms review, rights manifest and *authorized* sandbox checkout/download/refund inspection before any paid link | HARD HOLD | Founder + Commerce |
| Grok records-themed video → public gateway | No verified posted preparedness `asset_id`, real post URL, CTA placement or approved UTMs in TASK-008 | Grok/Praxxis reconcile existing published asset and exact actual destination; do not change queue/post | UNVERIFIED | Grok / Praxxis |
| Free gateway → Household Emergency Plan | Article not safety/source/QD approved; no live article route | Complete claim citations, independent hazard review, source dates, keyboard/mobile link test, no email gate for essential guidance | DRAFT / HOLD | Preparedness + QA |
| Plan → optional printable free Reunification Card | Child location/privacy, in-browser retention, save/print and accessibility not approved | Synthetic-only mobile 360/390/768/1440, offline, print, focus, keyboard, zero-network and no-sensitive-storage checks | HARD HOLD | Site QA |
| CTA → merchant-confirmed purchase → realized net | No attributable qualified human sessions, order/fees/refund ledger | Validate explicit opt-in and existing nonduplicative measurement: `utm_content=asset_id`; keep CTA click, signup, checkout start, merchant sale and refund separate; 7/30-day cohorts | NOT COMPUTABLE | Commerce / Analytics |

**Draft on-site CTA, NOT live, only after guide release:** “Preparing to leave quickly? Start with official planning guidance, then use our independently reviewed household records checklist when it becomes available. The safety resources stay free.” No paid link until commercially authenticated.

**Landing acceptance contract, prior to any campaign:** verified actual Grok asset URL + unique asset_id, platform permitted link location, content-to-destination accuracy, 200/canonical and source notices, accessible mobile/keyboard CTA, no unsafe urgency, honest disclosures, un-gated safety resources; route/UTM preservation and privacy consent; merchant terms and verified delivery before sale. Track revenue only from merchant-confirmed transactions minus fees/refunds over qualified human session cohorts; insufficient numerator/denominator means **not computable**, not $0.

**Release gate:** independent source/medical-food safety/child-privacy/printing and browser review, original native validator+builder+full tests, separate QD, and founder approval. No CMS, homepage, navigation, social, merchant, analytics, email, live changes or spending.
