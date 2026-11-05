# R154 — Source-review triage and notes intake (DRAFT / HARD HOLD)

Parent R153 PR #1159 at `2fde3b24878407b71de2e1939b0b5c9b727c9abd`; Issue #136, coordination #820. Additive Preparedness review files only. No source edits, original article edits, citation substitutions, taxonomy, WordPress CMS, navigation, merchant, tracking or social changes.

## Function

`preparedness/tools/r154_review_triage_gate.py` checks frozen R153 Git blob `ba0d460f7d43df5cb9f7641694bfa8b223f1352f`, then invokes R153/R152 existing-source custody. Its immutable 75-task review queue sorts: 8 Historical Food source substitutions (qualified food safety review), 11 Family Reunification Card source uses (privacy and emergency logistics), 4 shadow interpretation changes, and 52 other tool-source relationships. The 67 tool-source relationships contain 173 citation occurrences; 58 lack current source-origin resolution.

Optional reviewer notes are external, keyed by exact R153 task fingerprint, and may ONLY indicate QUESTION, NEEDS_MORE_EVIDENCE or PROPOSED_CORRECTION. Notes and URLs are unverified; no source decision, safety certification, qualified reviewer, QD PASS or publication is granted. Exit code is **2** for valid DRAFT_HARD_HOLD or invalid input. Report JSON is written only to a new external file.

Run on a trusted disposable checkout: `python -I preparedness/tools/r154_review_triage_gate.py --repo . --report /tmp/fv-r154-report.json` (exit 2 expected). Then separately run `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and `python -I -m unittest discover -s preparedness/tests -v`. The native build can create local draft artifacts; never run on a public WordPress instance.

## Remaining blocks

Full authenticated 35-article native pipeline, qualified source/safety checks, independent QD and WordPress draft mobile/print/offline QA unverified. Existing `/preparedness/` overview is LIVE separately; all 35 article bodies remain DRAFT/HOLD. No verified Preparedness-specific Grok asset ID, rights-cleared purchasable matching SKU, merchant delivery or attributable paid order; no speculative paid CTA. Proposed free Household Emergency Plan → optional Family Reunification Card journey requires reviews and staging. Preserve retired-water-freebie exclusion, existing Focus fieldbook, and essential safety information without payment or signup gating.
