# R432 — Original passage and citation-context custody (DRAFT / HARD HOLD)

**Owners:** Preparedness integration and source/citation safety only. **Coordination:** #136, #820, charter #818. **Parent:** R431 draft PR #2847 at `7b7893b058e734431913f58d0d7646778827d8a3`. No original manuscripts, source registries, canonical URLs, safety states, offer configurations, or WordPress production files are changed.

## Defect and fix

R431's reading-depth comparison counted words, headings, citations, and href changes but could not detect deletion of an entire safety-relevant paragraph when the alternative grew longer overall. Nor could it distinguish a citation's *claim context* moving while the count of that source ID remained the same.

R432 reads the same **original Git-pinned, unselected** source/fork dossier and exact candidate blob files. For each of the **four original body fork paths**, it builds ordered per-paragraph and per-heading text fingerprints, counts repeated paragraphs, records the citation IDs attached to each paragraph fingerprint, and identifies context reassignments. Synthetic mutation checks include changed medication guidance, generators, carbon monoxide, family contacts/reunification, fire evacuation and source reassignment. It classifies text by keywords for **review triage only**; keyword detection is not a medical, safety or source-validity judgment.

The other **five source disputes and five non-body fork paths remain unresolved and untouched**. All three original Shelter branch identities, including identical-blob variants, remain separately traceable. No editorial candidate is auto-selected. Paragraph hashes deliberately avoid storing full original passages in the review receipt.

## Locally executable evidence — synthetic fixtures ONLY

- `python -I -m unittest discover -s preparedness/tests -p 'test_r432_passage_citation_custody_gate.py' -q`: **63/63 PASS**, after correcting one test's expected four-word value.
- `python -I -m unittest discover -s preparedness/tests -p 'test_r43*.py' -q`: **188/188 PASS** (69 R430, 56 R431, 63 R432) in a single local Python process.
- `python -m py_compile preparedness/tools/r432_passage_citation_custody_gate.py preparedness/tests/test_r432_passage_citation_custody_gate.py`: PASS.
- Files in this PR require exact remote blob-to-tested-file comparison. Source and tests must match Git SHA before a test receipt can be used. Neither test scope is the native 35-article validate/build or a qualified safety review.

Reproduce against real originals only inside an authenticated full checkout using original `preparedness/reviews/r397_original_source_fork_docket.json` and all 25 Git objects named `<sha>.blob` in a private temporary folder:

```sh
python -I preparedness/tools/r432_passage_citation_custody_gate.py \
  preparedness/reviews/r397_original_source_fork_docket.json \
  /tmp/fv-original-git-blobs
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
```

**The R432 CLI always returns 2 (HARD HOLD)** even with structurally complete original evidence. A paragraph is a heuristic HTML/text grouping, not a browser-rendered reading-depth measure. Unanchored text triggers a hold. Source links, manuscript claims, qualified emergency/food/medical/child-privacy review, original 35 WordPress and 35 preview export pairs, actual mobile rendering, independent QD PR #157, fixture PR #169 and dependent PR #2205 are not approved by this gate.

## Commercial conversion-first contract

**One tentative matched-audience path:** verified already-published Grok video specifically about family emergency contacts/reunification → currently available **free official-source** `https://finalvestige.com/preparedness/` → optional **unpublished** Tool #104 only if qualified human safety/privacy/accessibility approval. Original Article #15/Tool #104 remain PRIVATE/HOLD; Tool #102 is different; retired water freebies excluded. Praxxis must independently match the true immutable video asset ID, actual post/permalink/date, hook, rights and permitted mobile destination; **none is authenticated here**. Grok retains creator/posting ownership; this PR does not change TASK-008 creator assignments.

**Paid offer → step → blocker → change/test → owner:** No authenticated existing rights-cleared, FV-owned/licensed, payable, deliverable Preparedness SKU → paid CTA/checkout **HOLD** → founder/Commerce verifies seller, checkout, delivery, refund and consent records before advertising. No speculative SKU or third-party misattributed Payhip product. Existing free Archive → trusted agency resources remains ungated and free. Campaign sessions/CTA clicks/confirmed leads are not purchases. **7/30-day qualified-human cohorts, merchant-confirmed orders, fees/refunds and realized net revenue per 1,000 sessions remain NOT COMPUTABLE** → Claude/Commerce measurement QA, no duplicate scripts or live deployment.

**Release:** no merge, CMS/navigation write, public post, creator queue edit, email, analytics deployment, merchant/affiliate activation or spending. Founder must separately authorize publication and commercial release. DRAFT / HARD HOLD always.