# Apollo R337 — Research Desk documentary/source-custody correction (staging only)

This small PR is stacked **directly on Research Desk PR #158** (head at baseline `250d7f05a4de037e73826dcf0cfaef0ec4c29383`) rather than on Apollo's separate component chain. It leaves PR #158, homepage PR #49, live WordPress and Grok untouched. It is **not approved for merge or deployment**.

## Source and editorial changes
- All 6 cards now lead with a textual NASA record (the original 1967 Apollo 204 Review Board report for records 02–06; a later NASA retrospective for record 01).
- Their existing NASA photograph accessions remain as **separate, explicitly contextual links**, not independent fire-cause proof or commercial media permission.
- A visible note explains that source links do not convey reuse rights or NASA endorsement.
- Record 06 no longer asserts an exact count of **102 fire-ignition tests** in the search index or detail body: its linked 1967 report predates those alleged later tests; this number requires an independently verified source before reintroduction.
- No new NASA URLs, downloaded photos, geolocation, paid offer, tracking, or other sale claim.

## Test contract
`python3 experience2/apollo-r337/qa/desk_source_custody_contract.py experience2/research-desk/templates/ledger.html`

The deterministic pure-Python gate checks roles and destinations for every card and five negative mutation cases. It is not an axe-core, screen-reader, authenticated WordPress or HTTPS delivery test. Those remain release blockers.

## Rights and release boundary
NASA generally permits linking and informative use of NASA materials but use of agency marks, astronaut likenesses, potential third-party copyright and commercial endorsements requires separate review. See https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . A NASA photo detail page is metadata, not a rights certificate.

## Conversion pathway, gated
Grok approved Apollo long-form asset [unverified] → Apollo Evidence Atlas [staging] → one existing free investigation [editorial] → only a separately authenticated, rights-cleared Apollo-relevant paid product [not yet verified]. No commercial CTA is authorized in this PR. Outcome KPI is **net realized revenue per 1,000 qualified-human sessions**; there are no authenticated inputs to calculate it.

## Outstanding release gates
Original photo accessions, source wording and NASA reuse review by editorial owner; hosted exact-HEAD CI; genuine axe-core; manual screen reader; Firefox/WebKit; installed WordPress/Assembler/CDN; HTTP/CSP; full responsive QA and real performance; merchant inventory and checkout; founder/QD approval. No live changes.
