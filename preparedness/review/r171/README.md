# R171 — Source registry ⇄ article citation crosswalk admission (DRAFT / HARD HOLD)

**Scope:** Preparedness source/citation integrity only (#136). Conversion-first coordination #820 and charter #818. Stacked on R170 draft PR #1271 at `85fad995536d574b2d547d13974007b663b890f3`; do not merge or publish. This is not QD PASS, editorial approval, clinical approval, merchant admission or founder authorization.

## Fresh authenticated source finding (November 6, 2026)

The eight original source inventories contain **244 rows / 225 distinct source IDs / 202 distinct literal source URLs**, with **15 IDs repeated in multiple inventories and zero repeated IDs pointing to different literal URLs**. The original crosswalk records **32 shared-URL review groups, all pending human reading-scope review**. An exact source-by-source comparison against current pinned source files detects **one material shared-URL roster discrepancy**: `hist-food-nchfp-jerky` refers to `https://nchfp.uga.edu/how/dry/recipes/jerky/` (trailing slash), while the earlier group `https://nchfp.uga.edu/how/dry/recipes/jerky` includes that source ID under the slashless literal URL. The fragment notes both URLs returned HTTP 200 in a prior inspection; **do not equate these URLs without a qualified current check**. Four more group differences were merely source-variant order (CDC outage, LOC pioneer diaries, FEMA outage sheet, NWS winter during); the R171 validator treats row ordering within a shared-URL group as nonsignificant, while retaining exact identities, source records, indexes and citation state.

See `source-variance-quarantine.json` for the exact URL, identities, unresolved decisions and hold flags. **Do not auto-rewrite the historic crosswalk or source fragments.** A qualified reviewer must resolve the alias/redirect and source-scope relationship, preserve versioned original evidence and then approve a separately reviewed crosswalk update. A source URL redirect or successful automated scrape does not prove medical safety or source claim fit.

## Gate and tests

`r171_source_registry_claim_gate.py` crosschecks original 35 metadata interpretations against all eight source inventories, every duplicate URL/ID group, exact source-file Git blob pins and R151/R161 custody; it chains the R161 full HTML-depth, route, 2,000-citation and 385-edge gate for an authentic complete checkout. The 385 source-use relationships are never silently rewritten, and a missing source, URL conflict, synthetic approval, source variant mismatch, duplicate route, metadata or SHA drift is **INVALID_HARD_HOLD**. Local test suite `python -I -m unittest discover -s preparedness/tests -p 'test_r171*' -q`; CLI `python -I preparedness/tools/r171_source_registry_claim_gate.py --repo .` always exits **2**. In the current pre-review state the authentic gate is expected to reject the stale group relationship after a full checkout; locally this environment cannot clone GitHub because DNS fails. Synthetic tests only do not constitute authentic validation.

## Commercial intent, blocked

Target one high-intent **school pickup / reunification** audience: original ungated **Household Emergency Plan** (currently DRAFT) → optional free **Family Reunification Card** (quarantined, safety/privacy/print review pending) → *only after independent commerce authentication*, an existing rights-cleared genuinely purchasable relevant FV Preparedness pack. None has been verified; therefore **no paid CTA, merchant link or implied SKU**. Existing free `/focus/` lead magnet is unrelated and untouched. TASK-008/Grok must provide actual `asset_id`, published URL, legal destination and UTMs. No claim of lead, sale, paid affiliate conversion or realized net revenue. No new tracking scripts, production changes, social queue edits, messages, merchant actions or spending.

## Acceptance / blockers

1. Qualified source reviewer resolves the one literal-URL crosswalk discrepancy, the 32 shared-URL groups and the prior 75 outstanding source decisions without automatic approval. Preserve the 35 original body SHA pins, 35 routes and 2,000 citations.
2. Trusted full checkout executes native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete regression suite and R161→R171 gates. Independently review safety/claim wording and QD; inspect actual WordPress staged content, mobile 360/390/768/1440, print privacy and accessibility. No optimistic test-status promotion.
3. Commerce verifies ownership, SKU, rights, published merchant checkout, delivery, refund terms, verified receipts/settlements/fees; Grok/Praxxis reconciles actual audience asset IDs through TASK-008, without posting. Only then propose a founder-approved optional nonessential paid CTA and independently verifiable 7/30-day conversion measurements.

**Release state: DRAFT / HARD HOLD. No merges, WordPress, home, nav, analytics, CMS, paid offers, email, social actions, publishing or spending.**
