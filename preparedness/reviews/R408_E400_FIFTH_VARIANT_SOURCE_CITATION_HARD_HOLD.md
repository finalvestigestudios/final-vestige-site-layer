# R408 — E400 fifth-edition adjudication escrow (DRAFT / HARD HOLD)

Scope: **ONLY** Final Vestige Preparedness Archive Issue #136. Conversion governance #820, charter #818. This is an additive, read-only source/citation and reading-depth review gate; **not a publication plan or safety approval**.

## What changed

Editorial E400's 2026-11-15 #136 comment reports a *fifth*, unselected Article #11 `safe-jerky-dehydration` candidate, different from E395/E397/E398/E399. Original E399 HTML reported SHA-256: `75ed08831c138ad3057220df060897e1efe518f1156ea68bb2400c06db898661`; E400 candidate HTML reported SHA-256: `7bf191f816da04027ad440e77e0898345c63caabc0edfae733965cebd8f9a107`. **These are editorial-reported fingerprints, not receiver-authenticated original bytes.** E400 is not automatically a better or safe edition merely because it is newer, shorter, or locally renderable.

`tools/r408_editorial_variant_escrow.py` accepts the two private original HTML paths and performs guarded identity/byte-bound reads and fixed digest matching, source-host/URL/remote resource and unsafe-markup preflight, exact source URL set additions/removals, duplicate visible citation URLs, rendered-word-depth and heading-context comparison. It distinguishes source removal (requires adjudication) from additions and reading compression (warnings, not clearance). It never selects an edition; does not infer food safety from domain or phrase matches. Digest overrides are API-only for synthetic tests, never permitted via CLI. The CLI **always returns code 2** with `decision=DRAFT_HARD_HOLD`, `eligible=false`, `publication_approved=false`, no qualified food safety or privacy approval.

`tests/test_r408_editorial_variant_escrow.py` contains 57 discoverable synthetic/adversarial unittest methods for unsafe URLs/HTML, fingerprint mismatch, citation loss, duplicate source URLs, reading-depth caution, linked files, bound reads and missing artifacts. They are **synthetic only** and cannot replace authentic manuscript or WordPress QA.

## Independent evidence and unchanged original scope

Fresh original R397 docket: **35** article identities, **203** source IDs, **280** original source occurrences, **17** shared URL groups, **5** original source-reading disputes, and **9** unresolved Shelter manuscript forks. Nine original contributor branch refs compared to R397 pinned SHAs: **all 9 identical, zero ahead/behind**. The five original source disputes and nine forks remain unselected. Original Article #7, #11, #15 and Tool #104 need qualified safety/privacy adjudication.

Independent QA PR #157 exact head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; independent synthetic fixture #169 head `e9cd7766dac59d47ab467d8945269b9146c2aef5`; dependent correction #2205 head `bbcf1859768624c611df4abadc564c18247cf32a`. Inspected as separate draft patches, none merged or modified. Parent R407 PR #2708 at `2e6ad89a08f1c025ac62490e2a54b31dc1d1cab5`. Home #1689 at `f55c36b6598eec558dd8bb24e4c8988becc51be0`. Do not change their ownership.

## Test truth and blockers

- **BUILT:** R408 gate and adversarial test file committed in this isolated branch, plus this memo.
- **TESTED locally, PROTOTYPE ONLY:** related but *nonidentical* standalone R408 prototype ran 52/52 unittest methods and Python compilation successfully in a disposable sandbox; NOT proof of exact committed 57 tests.
- **EXACT COMMITTED TESTS:** not executed in the local environment. The complete GitHub checkout could not be retrieved locally due DNS resolution; do not mark PASS.
- **AUTHENTIC ORIGINALS:** E395/E397/E398/E399/E400 original private HTML/ZIP and original printable not receiver-side available. No authentic five-edition comparison.
- **NATIVE BUILD:** original full 35-article `validate.py`/`build.py`, WordPress-ready export parity and 360/390/768/1440px actual-preview/print acceptance not executed.
- **RELEASE:** human source/claim reconciliation, qualified food-safety/emergency/child privacy and QD clearance remain **NOT GRANTED**. No publication approval.

## Commercial acceptance ordered by value

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| One existing rights-cleared FV Preparedness owned pack (none authenticated) | Confirm paid order and delivery | SKU ownership/payability/license/delivery/refunds/fees not independently verified | Founder/Commerce authenticates one *existing* item before a paid CTA | HOLD; no merchant-confirmed purchase | Founder/Commerce |
| Existing free agency-linked /preparedness/ | Genuine already-published family-contact social asset to matching landing | `asset_id`, exact hook, rights, permitted route and mobile verification absent | Praxxis independently QA Grok published post and destination; Grok retains posting | UNVERIFIED; no attributable qualified-human cohort | Grok/Praxxis |
| Optional Tool #104 (private) | Free guide to useful printable | Child privacy, family reunification, emergency scope and accessible print checks incomplete | QD source and privacy audit; do not publish yet | HARD HOLD | Preparedness/QD |
| Merchant receipts minus refunds/fees | Net revenue per 1,000 qualified human sessions (7/30 day) | Campaign attribution, human-session denominator and actual settlements not independently available | Reuse Claude-approved existing measurement after founder release, no duplicate script | NOT COMPUTABLE; clicks/leads/checkout starts are NOT sales | Claude/Commerce |

Proposed **unpublished, free-only** CTA: “Start With Trusted Preparedness Resources,” existing public `https://finalvestige.com/preparedness/`. No retired water freebie; no unapproved product or merchant URL. No paid CTA absent authenticated SKU.

**Required next handoff:** authorized receiver-side transfer of exact private E399 and E400 HTML (and E395–E398 chain), rerun fixed-hash/URL/visible claims checks, then native full build/export with independent qualified source/safety adjudication. Do not merge, deploy, post, write WP/CMS/navigation/analytics, edit Grok queue, send email, activate sales or spend. **DRAFT/HARD HOLD.**
