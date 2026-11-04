# Apollo R121 — Self-contained photographic source custody in printed student worksheet

**Classification:** BUILT in isolated draft source; exact-source V8 checks TESTED; representative fixture Chromium TESTED; **actual-page acceptance NOT EXECUTED**; **RELEASE: STAGING HOLD**. No WordPress, homepage, merchant, tracking, social or mail writes.

## Specific integrity defect
R120's optional student-only print mode hides the main investigation/source table, but its printable text asserted the dated register was earlier in the printed packet. It was not. Question 3 asks students to analyze a photograph, yet the standalone handout included only two general NASA citations and no photograph-specific NASA links. A teacher distributing the independent student worksheet could leave students with no specific photo sources to examine.

## Implementation
- `landing-preview.html`: place a six-link photographic source directory **inside** `[data-fv-student-print]`, pairing record IDs 01–06 exactly with the same six NASA URLs in the normal register. Source roles, individual dates and 2017 retrospective status remain explicit.
- `S67-19766` portrait catalog assignment and exact January date remain **unconfirmed**; photo 04/06 credit NASA/Kim Shiflett. No photo binaries, maps, inferred pins, invented edges, sales claims, forms, cookies or additional CTA.
- Replace the misleading standalone printed-copy assertion with accurate on-page vs. print distinction.
- Add print-specific wrap/break avoidance for the index without altering ordinary source packet or no-JS fallback.
- `qa_r113_print.py`: strengthen **actual-page** Playwright acceptance requirements for all 14 viewport/JS combinations, screen/print boundaries, the six links, chronology warning, provisional ID, NASA credit and PDF utility. **These are authored assertions, not an actual-page test pass.**
- `test_r121_student_source_custody.cjs`: offline 1 canonical + 10 adversarial exact-source checks, including URL drift between main register and handout, record duplication, 2017 misdating, loss of credit/rights and unauthorized photograph embedding.

## Execution evidence
- Exact current GitHub HTML + source contract fetched and executed with a **Node-compatible V8 assertion shim:** 11/11 PASS (1 canonical + 10 adversarial mutations). **Native Node / GitHub CI not executed.**
- Actual Chromium 144.0.7559.96 on *representative fixture only*: 14/14 width (320,360,390,768,1024,1440,1920) × JS/no-JS passed; 2 print-mode screenshots; student PDF generated and checked via `pdftotext`, including six NASA record labels and 1966/1967/2017 dates; six fixture-only lab observations LCP 64–92ms, CLS 0.
- Fixture reproducibility: 8-file deterministic ZIP created twice with identical SHA-256 `5ef768a67b7e0c960348df75ecad72768d773401dc252555e22f9e02dfb7f9c3` (not a production asset; local evidence only).
- Actual R121 whole-page Playwright, approved local axe bundle, genuine LCP/CLS, WordPress/Assembler and published URL screenshot comparison: **NOT COMPLETED**.
- User-facing traffic, checkout, confirmed leads, paid orders, refunds, affiliate conversions, realized net revenue: **NOT OBSERVED**; qualified-human session denominator unknown.

## Conversion-first handoff (#820; #818)
**Offer:** teacher-ready Apollo evidence casefile = **unverified product hypothesis**, not a sellable SKU.  
**Audience:** grades 6–9 educators arriving from possible Grok Apollo long-form/Shorts asset (Grok retains content/distribution).  
**Pathway:** identified `asset_id` / `utm_content` → Apollo provenance landing → free worksheet utility → optional later contextual verified teacher-casefile offer, **only after merchant/rights, fulfillment, terms and founder activation**. Do not treat worksheet prints or CTA clicks as purchases. No new measurement script, signup, price or checkout on this branch.  
**Hypothesis:** a source-usable, self-contained free handout improves qualified educator trust and later purchase intent compared with a worksheet referring to hidden records. **Untested commercially.**

## Owner/blocker actions
| Priority | Offer → funnel step | Blocker | Change/experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | Casefile → paid purchase | No verified matching SKU/rights/price/fulfillment | Independent audit of existing Payhip product inventory or founder-approved B2B pilot, no live link yet | BLOCKED | Claude/Growth/founder |
| P1 | Grok Apollo content → landing → worksheet | Printed photo sources previously absent | R121 source directory/print wording | BUILT; source tested; fixture browser tested | Apollo engineering |
| P2 | Worksheet → relevant commercial offer | No product or release authorization | Keep worksheet freely usable; specify later contextual offer only after clearance | NOT APPROVED | Claude/founder |
| P3 | Confirmed purchase → net revenue/1k qualified sessions | No verified buyer/cohort/source-of-truth orders | Reuse #820 privacy-governed asset UTMs and merchant reconciliation; 7/30-day small-sample flags | NOT COMPUTABLE | Claude/Growth/Praxxis |

## Hard release gate
Resolve six photograph-specific rights reviews, provisional crew ID, six Research Desk PR #158 role discrepancies, real-page browser + axe QA and source-linked CWV, WordPress integration/release reconciliation, independent historical review, approved merchant inventory/terms if commercialization is proposed, and founder publication approval. No code merge/deploy, site analytics, social post, email or payment mutation under this branch. Protect homepage PR #49 and PR #158 unchanged.
