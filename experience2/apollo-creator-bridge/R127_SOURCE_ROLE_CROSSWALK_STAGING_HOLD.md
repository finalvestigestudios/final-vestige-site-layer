# R127 — Cross-branch Research Desk source-custody gate (STAGING HOLD)

Built against Apollo R126 `b9413ebb33b1fc45b96e9b33887ac1fac6fd3cd6`, and a **read-only** audit of Research Desk PR #158 at `250d7f05a4de037e73826dcf0cfaef0ec4c29383` (ledger blob `403d128c57b9bc82dac7c619651689070edef86c`). Nothing here modifies the Research Desk branch, PR #49, WordPress, Grok's queue, analytics, email, or merchant systems.

## Why this matters

Six NASA photograph URLs match across Apollo and the separate Research Desk, but **matching image URLs do not establish that a photograph proves the technical findings presented alongside it**. The Research Desk also treats the crew portrait's proposed `S67-19766` identification without the provisional qualifier used by Apollo. Two 2017 photographs must be visibly identified as retrospective exhibits, not contemporary photographs.

Apollo's photograph register now has six machine-readable `data-fv-source-kind="photograph"` labels and a visible text/no-JS/print evidence warning. This is not a claim that NASA photographs have commercial reuse approval; **individual rights 0/6**.

## Run locally (no extra dependencies or services)

```sh
node --test experience2/apollo-creator-bridge/test_r127_source_role_crosswalk.cjs
git fetch origin feature/experience-2-source-ledger-pilot-20261030
node experience2/apollo-creator-bridge/r127_source_role_crosswalk.cjs --research-ref origin/feature/experience-2-source-ledger-pilot-20261030 --output /tmp/apollo-r127-crosswalk.json
```

When Git PR #158 is unavailable locally, provide its exact `templates/ledger.html` with `--research-file /path/ledger.html`. The audit is **read-only**, emits deterministic SHA-256 source hashes and source-URL evidence, and exits 2 until photo-specific permissions and editorial reconciliation are complete. A no-run / missing source is a blocker, never an empty PASS. The unit tests use explicit synthetic ledger fixtures; they are NOT a native CI pass or an exact-head browser acceptance without execution.

## Scoped editorial flags expected from original PR #158

01: proposed crew portrait ID needs a visible provisional qualification. 02: photo of spacecraft preparation is not direct oxygen pressure evidence. 03: 1966 rehearsal image is not the instrument time series. 04: 2017 hatch exhibit is retrospective. 05: post-fire image does not establish a unique ignition source. 06: 2017 redesigned-hatch exhibit is retrospective. Each flag requests more precise labels and paired NASA Board attribution; **it is not a finding that the Review Board's technical conclusions are false**.

## Offer / funnel / blocker / change / evidence / owner

**Proposed offer:** Teacher-ready Apollo evidence casefile (NOT verified sellable or rights-cleared). **Funnel:** Grok-owned history video → Apollo evidence landing → one free, no-signup classroom worksheet → hypothetical paid casefile if independently approved and merchant-verified. **Blocker:** no verified SKU or confirmed orders; photographic source-role ambiguity; browser navigation administratively blocked. **Change:** R127 typed source custody and cross-branch release gate, not a checkout CTA. **Evidence:** exact NASA link identity (6/6 in read-only cross-branch inspection), editorial warnings (6), rights 0/6; executable test results must be reported separately. **Owner:** Apollo source QA for this PR; Research Desk PR #158 owner for editorial edits; Claude/Growth for merchant verification and #820 attribution; Grok/Praxxis for content/creator review; founder for release and commerce approval.

**Release gate remains closed:** actual canonical HTML `page.goto` Playwright 320–1920, axe-core, LCP/CLS, screenshots and PDFs, WP/Assembler staging acceptance, historical review, all six media permissions and approval. No injection fixture counts as browser release QA. No product sale, qualified visit, or revenue is claimed.
