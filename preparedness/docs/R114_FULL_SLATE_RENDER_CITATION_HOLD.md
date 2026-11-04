# R114 — 35-article render/citation preflight; private source-review HOLD

**Scope:** Preparedness Archive Issue #136 only. Commercial coordination: #820, charter #818. Exact parent: R113 commit `ea3c72ba5a4fe6d53cefcd3979348ccbdc9fab41`. The new files do not alter any original article, safety state, source, canonical URL, 30 literal shared-source groups, contributor SHA, WordPress-ready inputs, CMS, public navigation, analytics, products, emails or homepage. This is add-only private review machinery. Do not merge/publish.

## Critical new coverage

Existing `build.resolve_tokens` substitutes citation/link tokens with regex over raw HTML. R113 examines one frozen original guide, but the full **35-article slate** may contain a token in a comment, HTML attribute, nonreading tag, hidden ancestor, concealed CSS class or malformed HTML. These can be counted by a renderer even when the reader cannot see the supporting citation. R114 scans every article **before rendering** using a conservative HTMLParser, compares its visible citations and link counts to raw renderer-matched token counts, verifies article-owned source IDs via `Library.source_for` rather than a global source union, and returns explicit per-article review flags.

Additional flags: malformed HTML, repeated HTML ids, unsafe linked schemes, undocumented article-slug/section/track drift, missing author source-use explanation, unresolved source identity/verification, lost reading depth, missing safety record, unbuilt/unknown internal link targets. Canonical article routes are independently reconstructed for 35 numbered items, requiring unique slug and URL, with the complete existing tool enumerated separately. Never convert pending / unverified / synthetic receipts to QD PASS, source truth or medical safety. Stronger hidden-link checks are a structural lint only; CSS and actual assistive-technology visibility still require browser testing.

CLI on a trusted exact checkout: `python -I preparedness/tools/r114_full_slate_rendered_citation_gate.py --repo-root .`. Output is a deterministic summary of article identities, SHA-256 body *fingerprints, not signatures*, counts and coded review flags; it contains no source URLs, article prose or customer data. Exit 0 means **audit executed**, not `PASS` or release authorization. Exit 2 means a broken census or execution failed closed.

## Testing contract and limitations

Synthetic test module: `python -I -m unittest discover -s preparedness/tests -p 'test_r114_*.py' -v`. There are 74 adversarial/unit tests, run in a local isolated scratch directory without source-tree test fixtures; both committed GitHub blobs must match the locally tested blobs. Synthetic success does not verify against actual article corpus. The separate private workflow must run focused tests, `validate.py`, offline `build.py`, 480-second complete Python suite, R113 guide check, R111 converged branch/collision crosswalk, and real R114 corpus audit on the **exact head**; blocked Actions dispatch must be disclosed as UNVERIFIED. Do not weaken existing mandatory 13-stage release controls.

## Founder conversion-first offer → funnel → blockers → evidence → owners

| Priority | Offer / funnel step | Blocker | Change or experiment | PASS/FAIL evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | Existing FV-owned Preparedness toolkit → verified paid order | No merchant-confirmed rights-cleared Preparedness Payhip SKU, price, downloadable deliverable, returns/fees or accepted checkout | Review actual existing FV seller products against household communication planning intent, stage one only if rights and functionality verified | **HOLD; no product, purchase CTA, merchant confirmation or revenue established** | Growth / Claude / founder |
| P0 | Original free household emergency guide → reader trust | 35-article source/citation/visibility/safety review incomplete; 23 contributor file deltas, 30 author-specific URL groups | Run R111 lineage + R114 complete article audit, adjudicate human source/qualified emergency advice review | 74 synthetic tests do **not** constitute source or safety verification | Preparedness / qualified reviewer / independent QD |
| P1 | Grok household planning post → proposed guide URL | No verified TASK-008 asset_id, post URL, destination continuity or confirmed live guide | Grok supplies actual source-linked asset inventory; Praxxis validates; Claude stage-tests 360/390/768/1440, keyboard, disclosure, captions/profile routing | **NOT VERIFIED; no attributed qualified visits** | Grok / Praxxis / Claude / Site QA |
| P1 | Optional download → usable delivery | Product absent and release unapproved | Only after real owner/rights and merchant fulfillment proof, stage optional clearly labeled practical download; keep core safety guidance free | **NO checkout, delivery or price claim** | Growth / Claude / founder |
| P1 | Qualified human sessions → confirmed orders → refunds/fees → net/1,000 | No live cohort data or merchant attributable receipts | Existing #820 privacy-safe measure, 7/30-day tiny sample flags, consent, no duplicate scripts | **N/A, not zero; social views/CTR/CTA/checkout are NOT paid sales** | Growth / Claude / Praxxis |

Free guide: `household-emergency-plan`; proposed but **not live-confirmed or safety-approved** `/preparedness/start-here/household-emergency-plan/`. No paid offer or active public CTA. No retired water giveaways, no replacement for functioning Focus Fieldbook subscriber pathway. Keep all emergency guidance free without signup or purchase gates. Grok retains content/posting; Praxxis coordinates TASK-008; Claude owns website/analytics; founder owns release and spending.

## Release blocking dependencies

Historical seven Claude contributor branches including five advanced SHAs and 23 changed paths, 30 shared-source URL groups, 15 safety exceptions, 22 editorial decisions, five unfinished tools, qualified safety/source review, independent QA PR #157, PR #169 fixture race (one shared-tree temporary write), staged browser/print QA, mandatory integrity and independent QD. Preserve R113 frozen original 35-article/slate and source evidence unchanged.

**Release state: HOLD. `may_merge=false`, `may_publish=false`, `independent_QD_PASS=false`.** No WordPress/CMS writes, product activation, live social posts, email, tracking deployment or site navigation changes.
