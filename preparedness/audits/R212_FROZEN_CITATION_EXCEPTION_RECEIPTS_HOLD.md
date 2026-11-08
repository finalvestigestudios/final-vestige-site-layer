# R212 — frozen citation exception receipts (DRAFT / HARD HOLD)
**Issue:** #136 · **Revenue coordination:** #820 / charter #818 · **Date:** 2026-11-08 UTC  
**Scope:** authentic source/citation custody and an offline synthetic regression; no publication or CMS, navigation, homepage, merchant, email, analytics or social writes.

## Authenticated read-only observation
Direct GitHub file reads from Claude Start Here head `2122d856fce9f64887c16df3d52e64be9f59a55b` established:
- Article **#7**, `homemade-water-filters`: original body `67aa44e9a332f57fb70298a3867410d8f66c8c15`, metadata `33789d3db0ec06007deb50d0293361f07cea27ae`; **51** citation occurrences, **6** unique cited IDs; **2** occurrences of `cdc-find-clean-water` without article-level `source_use` explanation.
- Article **#20**, `preparedness-real-households`: original body `70d03c366e10db623929f118501becfa26c48bab`, metadata `a0c3a09143a825560b5a5ed79d857b7402bfa295`; **64** citation occurrences, **17** unique IDs; **1** occurrence of `start-ready-plan` without article-level explanation.
- Global source register blob `b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77` and Start Here fragment blob `29574c328cbab0548e6e5d4a026694857d56b6b4`. Both target IDs have a single record in the combined register/fragment; original `human_link_check=false` for both.
- **Total inspected here: 115 citation occurrences across TWO articles, not all 1,971 citations/35 articles.** Other existing gates and the seven historical source conflicts remain independent and unapproved.
- Other global/Start fragment ID collision `ready-are-you-ready` remains unadjudicated; the new tool NEVER treats it as an automatically equivalent citation.

## Live-source spot check — NOT qualified safety review
The CDC [How to Find Clean Water in an Emergency](https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html) page (dated **June 25, 2025**) distinguishes the **tap-water-heater tank** from a household *heating-system* tank, allows **melted ice only if made from uncontaminated water**, and prohibits drinking/using water contaminated by fuel or toxic chemicals. Article #7 uses a broad phrase about a "water heater tank, melted ice cubes and similar sources"; editorial review should assess whether it conveys the restrictions clearly enough. The second citation concerns suspected contamination upstream; the official page says fuel/chemical-contaminated water cannot be made safe. This inspection does not sign off on either claim, its full context, or the article's safety.

An independent direct fetch of `https://www.ready.gov/plan` yielded HTTP **403** in the current web retrieval context. Article #20 links household languages to this source, but its actual claim support and current page contents require a human check through an accessible trusted route. Do not change `human_link_check` to true merely because source metadata exists.

## R212 implementation
New `preparedness/tools/r212_citation_exception_receipts.py`:
1. Pins exact SIX Git blob identities and must read them with R211 no-symlink, descriptor-relative I/O from a trusted **Start Here contributor checkout**.
2. Rejects missing/extra files, drift, malformed/duplicate-key JSON, article identity/slug or approval changes, unexpected source-use explanations, malformed citation syntax, shifted held occurrence counts, duplicate target source records and substituted URLs.
3. Emits **three independent SHA-256 receipts** based on original article blob, citation source ID, exact UTF-8 byte offset and local claim-context window; statuses remain `PENDING` / `HUMAN_ADJUDICATION_REQUIRED`.
4. Has only `DRAFT_HARD_HOLD` (exit **2**) or `INVALID_HARD_HOLD` (exit **3**). **No PASSED state or approval flag exists.**
5. Is evidence custody, not claim-support adjudication or medical/water-safety approval. If a human changes an explanation or source, the frozen preflight rejects that change until a separate reviewed version is authored.

New `preparedness/tests/test_r212_citation_exception_receipts.py`:
- **63/63 PASS** in the local Python 3 isolated test directory; **35 individual mutation tests** inject new unexplained citation tokens; other cases check changed URLs, metadata approval, source identity, duplicate JSON keys, Unicode byte offsets, source status, deterministic receipts and stale Git pins.
- `python -m py_compile` **PASS**.
- **Exact-code proof:** GitHub refetched tool blob `5de67ebe4db2f7a77671d4916679dba2507657b2` and test blob `d1eea5ae4a54ef39ef6ba547c75afdd5d83d1570`, equal to the locally tested UTF-8 files' Git blob hashes.
- Full native checkout, `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, original complete unittest suite, authenticated CLI against all six original files and 41 WordPress-ready outputs **NOT EXECUTED**: local GitHub DNS cannot resolve. The six authentic originals were individually inspected via connected GitHub, not executed as a complete local checkout.

### Frozen cross-agent custody, no overwrite
Seven Claude heads observed unchanged at check: Start Here `2122d856`, Food `f911ff7a`, Shelter `5daeaf2d`, Health `d5ef5baf`, Historical Field `4e5caf81`, Historical Food `67e116e5`, Historical Home `7504a5f0`; full 40-character identities live in R210 receipt. QA #157 `7d1ae6b8`, fixture #169 `e9cd7766`, stacked #973 `4d40996a` remain **draft/unmerged**. Their older test/article bases must NOT overwrite newer content. Homepage EX2 draft #1555 `4b182ee5`, stacked over #1548 `cfcfd7fe`, inspected without modification.

### Release hold
Unresolved 3 citation occurrences, 7 historical conflicts, independent QA test equivalence and fixture isolation, qualified source/safety review, native validation/build, and WordPress preview acceptance. No false QD PASS, no publication. The next reviewer action is human claim-to-source adjudication with exact receipt IDs, followed by a reviewed superseding manifest; do NOT mutate originals to make the current gate green.

## Conversion-first review-only lane (#820)
**ONE audience:** households preparing document locations, insurance, financial contacts and fallback decision-makers. **Social:** only a topic hypothesis until Grok/Praxxis TASK-008 provides a *real published* asset ID, URL, hook and destination. **Free resource:** the existing ungated [Preparedness Archive](https://finalvestige.com/preparedness/) and its official-source links; the original Household Emergency Plan and printable Reunification Card are NOT published. **Optional candidate:** [Legacy Triage](https://payhip.com/b/n1RhV), a publicly listed $19 printable records/legacy organizer, NOT an emergency response plan. Seller rights, current checkout, purchased delivery, refunds and merchant-confirmed net sales remain unverified; **do not enable CTA**. Draft language (disabled): “Free planning information stays free. For separately organizing family records and contact locations, see optional Legacy Triage details when purchasing and delivery have been independently verified.”

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Grok topic → free archive | Real post and immutable asset ID absent | Reconcile TASK-008 hook, approved URL/UTM and creator rights | UNVERIFIED | Grok/Praxxis |
| Official free archive → reader | Long-form safety/citation approvals withheld | Keep actual official resources accessible; human-source review | Free gateway LIVE; original HOLD | Preparedness / independent QA |
| Separate optional organizer → buyer decision | Legacy/emergency fit, seller rights and accessible disclosure unapproved | Nonpublic mobile 360/390/768/1440, keyboard and no-purchase path | DRAFT / NOT TESTED | Preparedness + Commerce/QA |
| Merchant checkout → PDF fulfillment | No authorized paid-order/refund evidence | Founder-authorized checkout, delivered PDF, support and refund reconciliation | HARD HOLD | Founder / Commerce |
| Attributed session → net revenue | No human-session cohort and independently confirmed paid sales/fees/refunds | 7/30-day consent-safe existing measurement, no duplicate scripts | NOT COMPUTABLE | Claude/Analytics + Commerce |

**Grok retains all creator production/posting; Claude retains core site engineering; founder controls release and spending.** Nothing commercial, public, or analytics-related was activated by R212.
