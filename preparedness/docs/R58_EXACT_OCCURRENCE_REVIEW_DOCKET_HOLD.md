# R58 — Exact original citation-occurrence reviewer docket (PRIVATE / HOLD)

**Issue:** #136 only. **Stack:** R57 source/citation/action bridge at
`60f970cc673a3a597c15e55f0d94992287f2c5a9`. No article, tool, source
fragment, taxonomy, original contributor branch, site CSS, CI workflow, WordPress,
navigation or homepage file is modified. All work remains a separate draft PR.

## Concrete review gap closed

The R57 crosswalk covers all **367** article/source relationships and all
**1,959** repeated citation occurrences while preserving **224** original source
records / **186** exact URLs / **30** shared-URL groups / **43** fallback
relationships. But 367 relationship cards are not the same as a practical
one-item-per-citation work queue. A cited source can be used repeatedly in
different contexts in the same article, with different claims and risks.

R58 creates exactly **1,959 distinct, deterministic, NOT_REVIEWED citation
work orders**, one for every original visible citation occurrence:

- Exact article slug and contributor-specific source ID/origin.
- Original citation occurrence ordinal and **Unicode codepoint offset** in
  the unchanged source HTML.
- Exact original unabridged citation context and its SHA-256.
- Original frozen article and source-reading-use SHA-256 custody anchors.
- Original, unabridged full contributor-specific source record (URL, notes,
  support scope, and provenance), retaining same-URL variants separately.
- Original entire article/source relationship without losing repetition.
- Related high-consequence action **work-order IDs on the same
  article/source relationship only**. This is explicitly **not** a
  token-to-claim or claim-support inference.
- Three explicit **NOT_REVIEWED** states for retrieval, claim support, and
  qualified hazard-safety assessment.

The private packet additionally retains **all 779 original action work
orders** (including 237 same-block-uncited), their unmodified source rows,
all 30 shared-URL review cards, all 43 fallback cards, all **15 OPEN safety
exceptions**, and all **25 historical machine source-access holds**. It
does not silently identify historic holds as current link failures.

## Trust boundary and required commands

The CLI `preparedness/tools/r58_exact_citation_occurrence_docket.py`
first regenerates the entire upstream R53/R54/R56 evidence and R25 audit,
then runs the full R57 original-source/citation/action validation. Only then
does it derive and self-reverify the per-token R58 docket. Fingerprint
self-consistency is not a trusted external signer or a substitute for
independent reviewer identity.

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I preparedness/tools/r57_global_citation_action_bridge.py --summary
python -I preparedness/tools/r58_exact_citation_occurrence_docket.py --summary
python -I -m unittest discover -s preparedness/tests -v
```

Default execution is read-only and only prints HOLD summary JSON.
Optional `--write-private` exclusively creates a new directory under the
existing ignored, nonsymlink `preparedness/build/`, containing a complete
UTF-8 JSON docket. The directory must not already exist. The export is not
WordPress content and must never be uploaded to a public CMS or repository
release artifact. No external source URLs are visited automatically.

The adversarial suite includes 36+ independent explicit input and output
mutation cases, missing/reordered/duplicate citation offsets, false reviewer
approval, changed contributor reading depth, missing safety counts, repeated
citation tasks, original-source substitution, and a full 35-article + water
tool corpus smoke test. Only a final exact-HEAD hosted CI result can establish
that the native full Python suite and all required private stages pass.

## Coordination and unresolved release work

Before merging anything, recheck exact current SHAs for all seven Claude
contributor branches; independent safety QA PR #157 and synthetic fixture
PR #169; R48 review PR #483, shelter continuation PR #521, homepage
#49/#254 and Gutenberg #414. The original R57 issue worklog records
the current verified baseline SHAs. These branches are not rewritten
or cherry-picked by R58.

**Public release remains HOLD:** no independent completed checks for
206 tracked human source links; 30 shared-URL groups and 43 fallbacks
still require contextual human reconciliation; 15 OPEN safety
exceptions; 25 historical source-access holds; 779 flagged
high-consequence actions; qualified water/food/fire/medical/infant/evacuation
safety review; actual WordPress/Assembler mobile, keyboard, print and
accessibility testing; authenticated independent QD review of exact final
commit. This machine-made packet completes **none** of those approvals.

Never call a machine citation, URL, numeric match, or automated test proof
that an emergency/medical claim is correct or safe. No QD PASS, no CMS write,
no site navigation, no merge, no live publishing.
