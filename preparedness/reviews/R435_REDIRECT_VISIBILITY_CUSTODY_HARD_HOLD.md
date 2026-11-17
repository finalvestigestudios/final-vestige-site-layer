# R435 — Preparedness full-document destination & visibility custody

**Status: DRAFT / HARD HOLD. Issue #136; conversion governance #820 / #818. Never publication/QD approval.**

## Controlled scope

Only new read-only validator and synthetic tests. Stacks on R434. Does **not** select among nine manuscript forks, adjudicate five source disputes, alter the 35 original articles/203 source IDs/280 occurrences/17 URL review groups, change their routes or safety labels, merge Claude branches, or modify WordPress, navigation, social, analytics, merchant, email or product listings.

## Reproducible findings

R434's whole-document parser can return zero errors for (a) an outside-main URL that points through an intermediary's `?next=` to an unapproved Payhip checkout, (b) a duplicated href where the first browser-interpreted value differs from the last value in its dictionary, (c) a CSS rule in `<style>` hiding a safety warning, or (d) a changed outside-main anchor across the WordPress/preview pair. These are synthetic test cases, **not observed live compromises**. R435 adds bounded decoding, nested-destination flags, duplicate-attribute reports, all-document anchor multiset fingerprints, inert/hidden/aria-hidden review flags, stylesheet and HTML-comment checks, robots-directive review, and structural closure checks. Review flags are conservative and may flag legitimate templates; a qualified human must adjudicate.

Execution contract: `python -I -m unittest discover -s preparedness/tests -p 'test_r435*' -q`; combined local subset `python -I -m unittest discover -s preparedness/tests -p 'test_r43*' -q`. `python -I preparedness/tools/r435_redirect_visibility_custody_gate.py <private_manifest> <evidence_lock> <paired_exports>` always exits **2 / HARD HOLD** even for structurally clean results. The gate never establishes source truth, modern medical/food safety, merchant settlement or a QD PASS.

## Open evidence and release blockers

The local synthetic subset is not the authenticated complete checkout, an original 35-article native validation/build, a real 35 WordPress + 35 private-preview export comparison, or human emergency/medical/food/privacy/source review. Hosted CI must be separately established at its exact commit; inherited R434 Actions failure has no usable diagnostic logs. No authenticated, rights-cleared, genuinely payable Preparedness pack, merchant-confirmed sale or qualified session denominator. None of these absent inputs can be transformed into a passing approval state.

## Conversion-first acceptance (review only)

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| One *existing* rights-cleared Preparedness toolkit or digital pack | Optional paid purchase after free official guide | No authenticated SKU, seller rights, live checkout, delivery, refunds, fees or settlement | Independently inspect existing inventory; draft only if product truly exists; do not invent an offer or revive retired water freebies | **HOLD** — none authenticated | Founder / Commerce |
| Existing official FEMA household emergency checklist on `/preparedness/` | Relevant social visitor → accessible free source | Genuine published family-contact Grok asset ID, rights, hook, exact destination & mobile link not independently matched | TASK-008 research-only crosswalk; do not direct visitors to unreviewed article #15 or to Tool #104 | **UNMATCHED** — public Archive source link exists; no verified social post match | Grok / Praxxis |
| Free official guide → optional practical Tool #104 | Intent-matched useful download | Tool #102 full plan builder versus #104 card identity conflict, no independent child/privacy/print/mobile/QD evidence; free information must remain ungated | Human adjudication and accessibility/safety tests; label optional; no draft-to-live transition | **HARD HOLD** — no approval | Preparedness / QD |
| Qualified human sessions → merchant-confirmed orders → realized net revenue | Measurement and financial settlement | No attributable real asset IDs, merchant orders, refunds, fees, or 7/30-day qualified-human denominator | Claude-owned existing/native event audit only; separate outbound clicks, confirmed leads, checkout starts, orders and settlement; no duplicate scripts | **NOT COMPUTABLE** | Claude / Commerce |

**Unpublished free-only CTA candidate:** “Review the official household emergency checklist” → the current open `/preparedness/` resource section, with the linked FEMA checklist available without signup. No paid upsell or tracking script. Draft landing acceptance: verified matching Grok post and asset_id; mobile 360/390 and desktop keyboard checks; visible emergency boundaries; working primary-source link; no email gate; canonical/domain consistency; actual CTA click distinguished from confirmed leads/orders; privacy/FTC disclosure adjacent to any future approved offer.

Cross-reference #136, #820, #818; TASK-008. Founder retains publishing, spending and production approvals. **No merge, publish, CMS/nav write, social post, paid service, affiliate activation, emails, or false QD PASS.**
