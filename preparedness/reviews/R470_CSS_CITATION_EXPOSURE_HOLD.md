# R470 — conditional stylesheet citation-exposure custody

**DRAFT / HARD HOLD / NO PUBLICATION** · Preparedness integration Issue #136 · conversion governance #820 / #818.

R469 protects literal citation tokens in authored HTML. CSS can still hide an intact source citation, its reading-scope note, or the independent safety-review warning on mobile/print views. R470 adds a separate fail-closed *read-only* authored-CSS guard for the pinned Preparedness stylesheet across base, `@media`, `@container`, `@supports`, and `@layer` branches, including print.

Original Git blobs pinned by code:
- `assets/preparedness.css`: `e354395cdb7985eb2fe16b99ca9fd66c9885557e`
- inherited `tools/r469_citation_visibility_custody.py`: `55b2a41afcb6f37a0df467b77406ec1a49f07409`

## Machine boundary

- Detect unbalanced or ambiguous stylesheets; unsupported at-rules, external CSS imports, hidden citation/source/review selector declarations, zero sizes/opacity, clipping/masking, offscreen displacement, deceptive animation, and unsafe nonliteral style expressions.
- Allow *exact pinned* legitimate opaque palette variables, ordinary source text, original visible citation-superscript line box, existing skip links and print controls. Unknown changed palette values must HOLD.
- Reject missing/changed original blobs and chain into R469's genuine 35-article, 2,000-citation audit when the full authenticated checkout exists.
- Never certify browser computed styles, WordPress theme overrides, printed PDFs, assistive technology, manuscript facts, source accuracy, medical/food/emergency safety, QD approval, or a production release.
- Even structural success emits `DRAFT_HARD_HOLD`; process exit 2 is intentional. A failure must be distinguished by the JSON `state` and `error` fields.

## Exactly executed local tests

- **104/104** new R470 synthetic Python tests PASS; Python compilation PASS.
- **881/881** combined isolated local regressions PASS across R463/R464/R465/R466/R468/R469/R470.
- Exact executed-and-committed Git blobs: validator `9a34357c68463b1ab4cc60f1024711455bf23043`; tests `c29f78360dfa1e47922dc6237dc47e7dd9a88a9b`.
- Native probe exited **2 / hard hold** because the local runtime lacked `assets/preparedness.css` from the complete authenticated checkout. The 35-article native `validate.py` and `build.py`, WordPress exports, private preview exports, 2,000-citation genuine chain, and browser/print checks **were not executed**. A synthetic test result does not waive them.
- Previous R469 hosted Actions run `44400795876` failed with one job and zero reported steps; log endpoint returned 404. **Cause unknown; no hosted PASS.** Do not weaken gates to hide this.

## Outstanding provenance decisions

The seven Claude original cluster SHAs plus two Shelter descendants remain pinned; independent draft QA #157, fixture #169 and repair #2205 are unmerged. Five original semantic disputes, nine unselected manuscript/source forks, 17 divergent article manuscripts, and 32 distinct shared-URL reading-scope groups still require human adjudication. Structural citation visibility does not prove emergency advice is safe.

## Conversion-first acceptance — offer → funnel step → blocker → experiment → evidence → owner

| Offer and funnel | Blocker / acceptance check | Result / owner |
|---|---|---|
| Existing FV-owned Preparedness pack → paid order | Authenticate genuine payable SKU, rights, checkout, refund terms, working fulfillment and independently settled merchant order before a paid CTA; do not invent a pack | **HOLD** / Founder–Commerce |
| Published Grok family-contact/reunification topic → existing free Archive | Match real published asset_id, actual message/rights, permalink and signed-out mobile destination; never fabricate social posts or UTMs | **UNMATCHED** / Grok–Praxxis TASK-008 |
| Agency-backed *free* planning guide → optional free Tool #104 | Article #15 and tool require emergency/child-privacy/accessibility/print human review; protect public free ungated promise, no retired water offer | **HARD HOLD** / Preparedness–QD |
| Qualified-human sessions → CTA → confirmed lead where applicable → verified paid order → fees/refunds → net revenue | Merchant transaction, rights, attribution and 7/30-day cohorts unavailable; no new scripts or invented sales | **NOT COMPUTABLE** / Claude–Commerce |

Scope: research-only and WordPress-ready **drafts only**. No merge, public publication, CMS, navigation, analytics, merchant/affiliate activation, emails, spending, social content, or false QD PASS.
