# Apollo Experience 2.0 — R419 Evidence Concordance (STAGING ONLY)

**Boundary:** isolated, default-off PHP shortcode `[fv_ex2_apollo_concordance_r419]` on a **specified WordPress staging page only**. No deployment, homepage #49 editing, source-ledger PR #158 editing, WordPress writes, paid CTA, email, analytics script, Grok assignment or affiliate activation. Built on parent R418 draft PR #2807, but only files in `experience2/apollo-r419/` are new.

## What is different

A single public-facing concordance traces (a) **three independently dated NASA textual events**, each with historical/evidentiary limits, and (b) **six source-photo context records**, each with photo date/type, associated textual claim, NASA original research link and a prominent statement of *what the photograph cannot establish*. This explicitly repairs the misleading R415 later-event → 2017 museum-photo association **without editing R415**. Photo dates are never treated as dates of the claim. All photos/insignia omitted until asset-specific rights reviewed. Native `<details>` discloses separate links; all meaningful historical boundaries are visible without JS. A single nonintrusive CTA goes only to the existing free investigation.

### Runtime custody

The shortcode pins exact Git blobs for R411 source catalog (`efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1`), R418 chronology (`2936eaac30cfe8a1c9016ca9298d98cb78ce9f7d`) and R419 CSS (`42bcc4e606b035f0b52519fb97acb5d3fefd7352`). These files must be reviewed, unchanged and available; a failure **falls back** to the pre-existing free Apollo investigation. Source/caption values are escaped; no dynamic media, speculative maps, tracking, forms or purchase links. Enabling requires explicit `FV_R419_ENABLED=true`, exact `FV_R419_STAGING_PAGE_ID`, `wp_get_environment_type()==='staging'`, a singular page and matching ID.

## Primary sources and media boundaries

- Original [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): no conclusive ignition initiator; electrical arc most probable, not proved.
- [NASA history of 102 later deliberate Command Module ignitions](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/): **December 1967–February 1968**, not fire-day telemetry.
- [NASA history of March 14, 1968 mixed-gas decision](https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/): subsequent decision, not a 1967 fire image.
- [NASA images/media rights and non-endorsement policy](https://www.nasa.gov/nasa-brand-center/images-and-media/). Linking does not establish commercial reproduction rights. 1966 training, 1967 preparation/aftermath, and 2017 tribute photographs are labelled as contextual or retrospective, NOT primary claim proof.
- Six source image-catalog URLs and NASA research-text URLs derive *unchanged* from reviewed R411 catalog based on original PR #158 ledger (original `templates/ledger.html` Git blob `403d128c57b9bc82dac7c619651689070edef86c`). Original PR #158 not modified.

## Evidence and reproducibility

From `experience2/apollo-r419/`, after obtaining **the exact reviewed R411/R418 dependencies on the parent PR stack**:

```bash
python qa/test_contract.py
python qa/test_release_gate.py
python qa/browser_qa.py
python qa/navigation_probe.py  # actual loopback Chromium navigation probe; may be blocked
python qa/release_gate.py  # expected HOLD, exit 2
python qa/package_evidence.py
```

Tests exercise exact upstream Git blob pinning, six distinct claim/photo relationships, 3 chronology sources, valid `<time datetime>` boundaries, unsupported contexts, mutated CSS/upstream source rejection, one free CTA, no geo or tracking, multi-instance IDs, no-JS native disclosure and real Chromium on PHP-built offline markup. 320, 360, 390, 768, 1024, 1440, 1920 widths, touch, keyboard, no JS, 400% root font/forced colors/reduced motion, print and CDP accessibility names. Browser screenshots are reproducible and the ZIP packaging uses a fixed timestamp and sorted entries.

**NOT TESTED / NO CLAIM:** installed Assembler/WordPress staging, real browser HTTP navigation, actual axe-core, navigated LCP/CLS, real-world p75 CWV, independently operated screen reader, checkout, published Grok asset, campaign attribution or sales. CDP accessibility tree ≠ axe. Existing R417 *committed* PHP differs from its earlier locally tested PHP; this upstream exact-source acceptance defect is still open. Exact-head CI and founder/QD reviews remain required.

## One conversion hypothesis — no unsupported sales claim

Audience: grades 6–9 history educators reached by a **verified** Grok Apollo video (Grok retains publishing). `asset_id` / actual `utm_campaign` → qualified human landing → transparent source/photo concordance → exactly one free-investigation CTA → **proposed** educator evidence/lesson kit *only after* a rights-cleared payable SKU, fulfillment, merchant records and founder approval. The investigation itself remains free; this code cannot silently activate commerce. Commercial hypothesis: clearer visual-vs-primary-evidence distinction increases qualified trust and later educator purchase intent; no data validates it. Claude owns approved first-party measurement/checkout, Praxxis independent creator QA, founder release/pricing. Attributed gross/net sales and net revenue/1,000 qualified sessions are **not computable** without verified first-party sessions, actual transactions, fee/refund records and 7-/30-day cohorts.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Unverified original Apollo educator dossier | Paid purchase | No rights-cleared payable SKU/fulfillment | Withhold paid CTA | HOLD, no merchant proof | Founder / Claude |
| Grok Apollo long-form | Qualified visit | Published `asset_id`, approved link and human cohort missing | Use existing TASK-008 only, no queue edit | UNVERIFIED | Grok / Praxxis / Claude |
| Apollo evidence → existing free investigation | Trust & onward visit | R415 links a 1968 event to 2017 exhibit image | Six explicit photo/claim boundaries, one free CTA | Local offline PASS; installed staging HOLD | Apollo QA / QD |
| Validated paid orders | Net revenue | No verified payments/refunds/fees | Request independent commerce scorecard | KPI NOT COMPUTABLE | Claude / Commerce |

**Release: HARD HOLD.** No live WordPress, homepage, analytics, merchant, social, affiliate, or email actions authorized.
