# Preparedness R305 — HTML5 non-void interpretation, link targets, and conversion acceptance

**Scope:** #136 / #820, 2026-11-11 PT. REVIEW ONLY / HARD HOLD. No public publishing, WordPress/CMS or navigation writes, no affiliate activation, emails, posting, new measurement, commercial checkout or spending. Claude retains website production, Grok social publishing, Praxxis independent social QA and founder release authority.

## Corrected semantic integrity defect

R304 repaired `<wbr/>`, but the inherited Python `HTMLParser` could still accept identical source/export `<strong/>`, `<span/>`, `<section/>` and other **non-void HTML** elements as if they self-closed. In HTML5, the slash on ordinary HTML non-void tags is ignored by browsers, so the resulting browser tree may swallow following warning language, change scope, and reassign citation context. R305 adds `HTML5_NONVOID_SELF_CLOSED:<tag>` and `HTML5_VOID_EXPLICIT_CLOSE:<tag>` fail-closed errors for authored/exported article contexts, while keeping ordinary `<br/>`, `<img/>`, `<wbr/>` and SVG self-closure legal. No source content is rewritten.

## Independent URL and fragment scanner

The new read-only validator, pinned to the exact corrected R303 validator and frozen R200 custody, scans **35 original articles and 35 matching WP-ready article draft HTML files**, not the six interactive tools. It checks event handlers, active embedded content, unwanted article scripts/forms, duplicate IDs/attributes, broken same-document fragment links, URL scheme and protocol-relative/encoded-traversal ambiguity, unsafe link/media/CTA targets, and `srcset` entries. It preserves source metadata and does not dereference external URLs, evaluate advice, run a browser or clear merchant rights. All six interactive tools remain subject to their separate privacy and safety gates.

The earlier R299–R304 chain still governs the intended 41 outputs, source pins, claims and citation placement. R305's new 35-document scanner is an *additional* condition, not a substitute for the authentic 41-export build.

## Current branch and independent QA

Seven Claude contributors were compared directly with the actual R200 pinned baseline on this run: **seven of seven identical, 0 ahead, 0 behind, 0 changed paths** (start `2122d856`, shelter `5daeaf2d`, food `f911ff7a`, health `d5ef5baf`, hist-field `4e5caf81`, hist-food `67e116e5`, hist-home `7504a5f0`). PR #157 remains draft `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. PR #169 remains draft `e9cd7766dac59d47ab467d8945269b9146c2aef5` with the independent duplicate-fixture source-directory write outstanding. Home lead PR #1689 is draft `f55c36b6598eec558dd8bb24e4c8988becc51be0` and untouched. Predecessor PR #2125 head `2ec5f75c37291773f49d57281aeb73e2a3886cc0`.

The 14 original body-lineage and 12 metadata-lineage differences remain **UNADJUDICATED**. Article #7 hazardous-water context and Article #15/Tool #104 emergency call thresholds, child privacy, printing, accessible no-JS usage and absolute no-storage promises remain **HARD HOLD**. Source-ID/history dispute remains open. No QD PASS.

## Verification boundary

Local source/test fixture only: **100 new adversarial Python tests plus 803 inherited = 903 PASS**; compilation PASS. This does **not** establish an authenticated real build or browser QA. Full 41-draft WordPress export validation is NOT EXECUTED because a complete authenticated source checkout is unavailable in this local environment; DNS resolution for github.com fails. A deliberate empty-root test returns `INVALID_HARD_HOLD`; no code path authorizes publication.

## Conversion-first plan — one audience/one provisional path

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (draft only) | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Family-contact/reunification social topic → free existing `https://finalvestige.com/preparedness/` agency-resource landing | Existing Grok published asset ID, actual destination, mobile source match unverified | Verify existing Grok `asset_id` + `utm_campaign`/`utm_content`, independently check destination without touching queue | **UNVERIFIED** | Grok / Praxxis TASK-008 |
| Free guide → optional Tool #104 printable family-contact card | Emergency-dispatch, child data/privacy, no-JS, print and accessibility gates unresolved | Review official sources, JS-free/print/browser behavior at 360/390px and screen-reader keyboard flow before any CTA | **HARD HOLD** | Preparedness QA |
| Free guide → one optional practical paid Preparedness pack | No owned/licensed, approved, actively purchasable, delivered audience-fit FV SKU verified | Founder/Commerce verify product provenance, rights, live price/checkout, delivery/refunds, disclosure and no safety dependency before drafting purchase CTA | **NOT APPROVED** | Founder / Commerce |
| Qualified human campaign visits → relevant click → confirmed lead → settled order → net revenue | No authenticated merchant events/fees/refunds, consent or asset-level qualified session evidence | Claude existing-approved analytics only; 7/30-day reconciliation; warn on tiny samples and report known unknowns | **NOT COMPUTABLE** | Claude / Commerce |

**Draft no-purchase CTA (review only):** “Make a plan for how your household will reconnect. Start with free official preparedness resources.” No signup gate to emergency safety information, false urgency or medical-safety claims. No paid CTA unless separately approved. Do not revive the retired water offer or treat Legacy Triage as licensed.
