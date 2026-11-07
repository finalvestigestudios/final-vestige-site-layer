# R191 — Preparedness six-tool CSS/resource and false-offer admission

**2026-11-07 PT | ISSUE #136 | DRAFT / HARD HOLD | NEVER A RELEASE APPROVAL**

## Inherited admission chain

R190 draft #1401 (head `0db83115dbd5bbecd9c45982492b6e7151b15f0d`) composes native validation/build/12 source-citation-safety stages with R189 HTML/JS export inspection. Independent QD draft #157 (`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`), synthetic-source draft #169 (`e9cd7766dac59d47ab467d8945269b9146c2aef5`) and stacked #973 (`4d40996a559b0124d74a9bb3bdcd481ad1992aa8`) remain separate. Original seven Claude heads, 35 article bodies, six tools and historical source-review decisions remain unmodified.

**R191 identifies a further, independently blockable gap:** R189 checks network-capable JavaScript, unsafe HTML tags/links and merchant domains, but did not expressly inspect CSS `@import`, `url(...)`, external SVG presentation-attribute resources or hidden Product/Offer/BuyAction JSON-LD in unpublished printable tools. A third-party CSS/SVG load could defeat the intended private family-data boundary, while false commerce schema could advertise an unapproved paid product despite inactive CTAs.

## Draft implementation

- `r191_static_resource_offer_gate.py`: read-only scan of all six original tool HTML bodies and **six generated WordPress HTML exports**. Reject CSS external loaders, CSS escapes/entities, malformed or non-fragment URL references, SVG fill/stroke/filter/clip-path/mask remote resource loads, HTML media/foreignObject/animation resources, JSON-LD Product/Offer/commercial actions or price claims, source/export path drift and symlinks.
- Legitimate **same-document SVG fragment** references (notably `fill="url(#fw-pat)"`) remain permitted. Body and export inputs are explicitly accounted for; source-only diagnostic never claims structural completion.
- `r191_full_integrated_preflight.py`: new preferred **trusted-checkout diagnostic only**. Pins the **exact Git blobs** of unchanged R190 wrapper and R191 scanner. Requires successful R190 12-stage structural receipt first; copies original sources into another disposable directory for the existing builder, then validates six authentic WordPress exports and original source byte-inventory parity. Any false merchant/sale/QD/publication flag returns INVALID_HARD_HOLD. Even structural success is DRAFT_HARD_HOLD with nonzero CLI exit, not a green release.
- Original articles, tools, source registers, 2,000 article and 173 companion-tool citations, 385+67 source-use mappings, 41 routes, WordPress/CMS, nav, measurement vendors and public website **not changed**.

## Executed verification — strictly local synthetic fixtures

`python -I -m unittest discover -s preparedness/tests -p 'test_r191*.py' -q` → **122/122 PASS, zero skips** in a reproduced `preparedness/tools` and `preparedness/tests` layout. Includes deliberate CSS external-load, hidden JSON-LD commerce, SVG resource, path/symlink, altered-code-identity and false release/paid-order attack cases. `python -I -m py_compile` of all four new files PASSED. Connected GitHub readback must match the same local Git blob SHAs.

**NOT executed:** authentic complete repo build, original suite, browser/WebKit/WordPress rendering, keyboard/print QA, full safety or source adjudication, merchant checkout verification. GitHub DNS resolution in the Python container still fails; the 35+6 native command cannot be honestly marked PASS. Static detection cannot prove full browser privacy. This PR is **DRAFT/HARD HOLD**, not publication authorization.

## Conversion-first proposal for TASK-008 (research-only; never a Grok production assignment)

**Audience / one high-intent question:** households safeguarding identity, insurance, medication/contact documentation before an emergency departure: “Could your household find its essential records if you had to leave tonight?”

**Current legitimate entry:** already-live, free `https://finalvestige.com/preparedness/` gateway linking current official sources. The original Household Emergency Plan is a long-form **unpublished** safety/source-held draft and may not be used as a public CTA destination yet.

**Practical optional tool:** existing Family Reunification Card is **free, unreleased and held** until its 11 source decisions plus child/family privacy, device, print and accessibility acceptance. Label it a printable family planning worksheet, not a professionally validated medical safety tool; never require an email for emergency guidance.

**ONE candidate paid offer to authenticate:** existing public-facing `Legacy Triage` records/household-continuity PDF. It is **not yet verified as rights-cleared, merchant-owned, consistently deliverable or appropriate**; no paid CTA, Product/Offer JSON-LD, checkout, speculative upsell or affiliate redirect. Its records/financial-continuity scope is potentially adjacent to the household plan's paper/insurance section, **not** emergency child reunification. Founder/Commerce must verify owned SKU/rights, exact artifact, price/terms, checkout, fulfillment, refunds/fees, and signed-out mobile acceptance before consideration.

**Draft editorial CTAs (NOT public):** free gateway: “Start with current official emergency-planning resources”; future independently approved full guide: “Build a household emergency plan”; optional future practical free tool: “Print a family reunification card (contains private information—store it securely)”. Any eventual commerce CTA must truthfully name and disclose the approved SKU and destination, with accessible focus states and no false urgency.

**Grok/Praxxis:** TASK-008 and dated handoff have not established a published matching Preparedness `asset_id`, exact platform post URL, rights, destination or approved UTM string. Do not seize or overwrite Grok's production queue. Only after IDs and page approval: `utm_source=<actual platform>`, `utm_medium=organic_social`, `utm_campaign=preparedness_pilot_2026_11`, `utm_content=<immutable published asset_id>`; profile-link limitations documented. No new analytics code.

### OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Required change or experiment | Current evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Legacy Triage (candidate only) | Relevant reader → paid order | Merchant rights, SKU, buyer fit, refund/fulfillment missing | Authenticate ownership and perform staged signed-out accessible checkout+delivery | **HARD HOLD**; zero confirmed purchases established | Founder / Commerce / Claude |
| Public Preparedness gateway / future held Household Emergency Plan | Grok post → qualified landing → relevant action | No approved matching asset ID, long-form guide is unpublished | TASK-008 asset/destination/rights mapping, no posting | **UNKNOWN ATTRIBUTION** | Grok / Praxxis |
| Free Family Reunification Card draft | Guide → optional usable download | 11 human source decisions; privacy, print, keyboard and mobile untested | Synthetic family data on 360/390/768/1440 px in isolated staging | **HARD HOLD** | Preparedness / Site QA |
| Existing approved Focus signup (separate lane) | Optional qualified lead | No Preparedness-specific consent/delivery proof | Reuse approved Focus flow only if genuinely relevant; do not gate emergency advice | **UNVERIFIED** | Claude / Dispatch |
| Verified merchant order | Revenue reconciliation | Qualified-human session denominator, sale, fees/refunds unavailable | Source-confirmed 7/30-day cohorts; report nulls not fake zeroes | **NET / 1K NOT COMPUTABLE** | Commerce / Analytics |

**Release dependencies:** independent primary-source adjudication (21 indexed article decisions, 58 tool relationships including 11 Family Card), qualified food/medical/electrical review where needed, accessible native WordPress preview, full authentic tests and signed independent QD. No production, emails, posts, spending, affiliate activation or navigation changes.

Cross references: [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818), home lead draft [#1407](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1407).
