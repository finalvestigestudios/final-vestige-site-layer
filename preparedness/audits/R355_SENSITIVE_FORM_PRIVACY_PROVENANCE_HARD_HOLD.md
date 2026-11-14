# R355 — Sensitive-form privacy-claim provenance review (Issue #136)

**State: DRAFT / HARD HOLD / no release.** Read-only audit, not runtime privacy assurance, child-health authorization, qualified QD acceptance, WordPress publication or a commercial conversion claim. Source of truth: #136 and #820; charter #818.

## Exact source observations

Original Tool #104 \`family-reunification-card\` at \`preparedness/r203-all35-body-citation-link-20261107\`:

| File | Original Git blob |
| --- | --- |
| \`preparedness/content/tools/family-reunification-card.body.html\` | \`be8698ac5d020476ff649d85813810e2000c6f98\` |
| \`preparedness/content/tools/family-reunification-card.meta.json\` | \`47da1e7e20e39f0ea85e26d54a8d58301f6e0a15\` |
| \`preparedness/taxonomy.json\` | \`15c547bb3018ac182b12a51036389cfa39a59168\` |

The drafted form asserts that entered data stays on the page, is not sent or saved and is cleared by closing the tab. Metadata separately uses absolute "Nothing is stored", "local-only" and "Runs locally" language. The source contains the unresolved \`{{inline-js:shelter_common.js}}\` and \`{{inline-js:reunion_card.js}}\` dependencies plus interactive JavaScript and print behaviors. Neither the static source nor \`autocomplete="off"\` establishes the behavior of all host/theme scripts, browsers, extensions, session restore or print/PDF copies. **No evidence shows a real leak; no evidence establishes the advertised whole-system guarantee.**

The original print layout specifies \`7.5pt\` for wallet-card faces. The authored fields do not establish a complete CDC-style child emergency card. These are **qualified review obligations**, not automatic medical or print-safety findings.

## New audit boundary

- Inspect 35 articles and six drafted tools, plus nine planned tool identities and the field-tools taxonomy text.
- Produce deterministic redacted per-form dockets: hashes of source copy, count of fields, applicable absolute privacy-claim classes, runtime dependency names and review holds. Do not emit entered user data.
- Reject missing documents, missing citation declarations, changed source/copy fingerprints, altered draft/safety states, malformed form nesting and changed Tool #104 dependencies. Preserve 3 planned-only tools.
- Read only Git-pinned original Tool #104 and taxonomy; reject symlinked/missing corpus documents. Never claim the scan proves absence of network transmission, child-card completeness or true print accessibility.
- Existing 15 contributor editorial conflicts, 17 Article #15 / Tool #104 review obligations, 4 competing verified-source IDs and tool-number reuse remain hard holds. Never drop reading depth, disputed citations or existing warnings.

## Required manual acceptance (not completed)

1. Editorial/QD: replace unsupported **absolute** privacy wording with appropriately scoped, tested copy, and reconcile CDC-style child-card purpose and sensitive information handling with school/caregiver practices.
2. Claude/site privacy owner: browser-network test at supported mobile/desktop sizes including host/plugin scripts, tab/session restore, downloadable file/print behavior; separately assess security and data minimization. Obtain consent where applicable.
3. Accessibility owner: audit actual printed 7.5pt card on paper with an accessible alternative, including emergency legibility; no fabricated legal font threshold.
4. Integration owner: authenticate exact committed Python tests, original source inputs and complete repository before native validate/build/100 private artifact parity.
5. Founder/Commerce: verify genuine payable rights-cleared SKU, fulfillment, refund policy and merchant evidence **before** any paid Preparedness CTA. Never gate essential emergency instructions.

## Conversion acceptance / ownership

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Currently unverified owned Preparedness pack | paid purchase | rights, payable SKU and delivery not authenticated | private checkout/delivery/refund audit only | HOLD: no authenticated order | Founder/Commerce |
| Free public Archive | guide → optional free resource | Tool #104 privacy, source and print claims | private copy/runtime/accessibility review | HOLD: original tool unapproved | Preparedness/QD/Claude |
| Grok family emergency-contact asset | social → free Archive | published asset_id/topic-fit/clickable mobile path absent | owner-supplied real post and platform-permitted destination | UNVERIFIED: no public campaign activation | Grok/Praxxis |
| Verified sessions | lead → settled paid order → net revenue | no merchant attribution, fees/refund reconciliation | privacy-respecting 7/30-day ledger | NOT COMPUTABLE, clicks ≠ sales | Claude/Commerce |

**CTA copy (draft only):** "Start With Trusted Preparedness Resources" → \`https://finalvestige.com/preparedness/\`. This is a public free information destination, **not** a live new campaign, not Tool #104 and not a paid product.

No merge, publish, CMS/nav, analytics/vendor, social post, email, affiliate activation or spending was authorized or performed.
