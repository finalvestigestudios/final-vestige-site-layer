# R148 — Preparedness tool-source origin and rendered evidence integrity

**DRAFT / HOLD** · Issue #136 · #820 / #818. Stacked on R147 PR #1117 at `094a9707fa4c342fa6e9720caaa253f00fa2e026`. No original article bodies, metadata, source fragments, crosswalk, taxonomy, publishing states, tool implementations, site routes, WordPress, analytics or merchant records changed.

## New authentic source-resolution blocker

The frozen crosswalk records 36 article origins: 35 articles plus `water-planner`. The remaining five implemented printable tools fall back to `base` in `Library.source_for()`, but their citation IDs occur in `start` or `shelter` source fragments, not the base register. Independent GitHub reads of the exact parent `build.py`, crosswalk, register/fragments and all six tool metadata files establish the unresolved tool-source-use counts:

| Implemented tool | Current origin | Unresolvable source IDs | Candidate origin, NOT APPLIED |
|---|---|---:|---|
| water-planner | base | 0 | base |
| home-fire-escape-worksheet | base fallback | 6 | shelter |
| power-outage-planner | base fallback | 16 | shelter |
| family-reunification-card | base fallback | 11 | shelter |
| reunification-plan | base fallback | 6 | start |
| kit-builder | base fallback | 19 | start |

**Total: five blocked tools, 58 tool-level source-use IDs.** This is a builder provenance/crosswalk defect, not proof that 58 separate emergency claims are unsafe. All referenced IDs exist in source fragments. The read-only tool-origin gate proposes candidate mappings but never applies them, merges reading scopes, grants approvals or changes immutable source records. Any correction requires qualified review and custody reconciliation.

## Independent draft-output custody

R147 verifies article citation tokens and draft-file existence, but a nonempty export can still truncate prose, omit visible citations or redirect an author-specific source URL. The new read-only `r148_rendered_evidence_gate.py` checks both WordPress and preview output against the original article/tool body, source-use metadata and literal author-scoped URL. It rejects missing/reordered citations, hidden sources and markers (for explicit DOM attributes/styles), changed reading text, duplicate evidence regions and forged publication states. It is not a rendered-browser or CSS-computed visibility test.

## Verified locally versus blocked

**BUILT:** Two new offline validators, two synthetic/adversarial test modules and candidate-only review manifest. **TESTED LOCALLY:** 102/102 isolated Python tests passing and Python compilation. Thirty-five source substitution probes plus thirty-five dropped-citation mutations are included. **NOT VERIFIED:** execution against the authentic complete 35-article/six-tool checkout; native `validate.py`, native `build.py`, full original tests, stage/browser/print/mobile accessibility, medical and source-review QD. Direct container GitHub DNS fails; hosted Actions have historically failed before any steps (do not infer a code test result or rerun automatically).

Trusted checkout order:

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r148_tool_origin_gate.py --preparedness preparedness
python -I preparedness/tools/r148_rendered_evidence_gate.py --preparedness preparedness
```

The provenance diagnostic deliberately exits 2 when source mappings are unresolved; native build may stop first. R133–R147 earlier custody/route gates should run before any release review. Only a separate qualified editorial/source decision may authorize applying a tool-origin crosswalk change, with full original-file evidence custody reestablished. A structural PASS never grants medical safety or independent QD. PR #157 safety wording should be reviewed without loss of richer existing article evidence; PRs #169/#973 remain separate for synthetic test isolation. Seven Claude contributor branch pins matched immutable recorded SHAs in this review; homepage #49/#604 remain untouched.

## One conversion-first journey, still gated

**Audience:** parents/caregivers seeking school-pickup and family reunification planning. **Free entry:** existing authentic *Household Emergency Plan*, DRAFT/HOLD. **Optional practical resource:** existing *Family Reunification Card*, DRAFT/HOLD, presently missing 11 tool-origin source IDs and not mobile/print/privacy tested. **Optional paid pack:** none authenticated as an owned, rights-cleared, currently purchasable matching Preparedness SKU. No paid CTA, pricing, unapproved products or retired water guide introduced.

**Unpublished draft CTA:** “Plan how your household reconnects after an emergency. Read the free Household Emergency Plan; when its reviews and download testing are complete, you can optionally prepare a private printable family reunification card.”

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Verified paid Preparedness pack → order | no authenticated matching SKU/rights/price/fulfillment/refunds | read-only merchant listing/checkout audit | HOLD, no attributable paid sale | Growth / Commerce |
| Free Household Plan → reader | qualified safety/source/QD and native build outstanding | source adjudication and full build | DRAFT/HOLD | Preparedness / QA |
| Guide → Family Reunification Card | 11 origin IDs; download, mobile/print, privacy untested | author-source mapping review and 360/390px independent QA | 102 synthetic tests; genuine draft NOT TESTED | Preparedness / Site QA |
| Grok asset → guide | TASK-008 no verified Preparedness asset_id/link/UTM destination | request inventory from Grok/Praxxis, without altering their queue | UNVERIFIED | Grok / Praxxis |
| Human session → confirmed customer → net | missing qualified session, merchant order, fees/refunds | consent-safe 7/30-day cohort reconciliation | NOT COMPUTABLE | Growth / Analytics |

KPI only when verifiable: **realized net revenue per 1,000 qualified human sessions**, with source-linked orders, refunds/fees and small-sample caveats. Do not equate video views, affiliate clicks, checkout starts or confirmed leads with paid sales. No public posting, production deployment, navigation, CMS or subscriber changes authorized. TASK-008 and dated Praxxis/Grok handoff read on 2026-11-05; Grok retains production/distribution; founder retains release and spending approval.
