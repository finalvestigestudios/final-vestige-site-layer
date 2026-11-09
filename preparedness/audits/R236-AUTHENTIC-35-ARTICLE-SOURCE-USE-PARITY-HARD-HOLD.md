# Preparedness R236 — authenticated 35-article citation-source parity correction (2026-11-09 PT)

**Issues:** #136, #820, charter #818. **STATUS: DRAFT_HARD_HOLD**. No WordPress, public publishing, menu, navigation, CMS, product, email, affiliate, creator queue or spending changes. All 35 author manuscripts, 35 metadata documents, six tools, source registers, taxonomy, route authorities and HTML exports remain unchanged.

## Material defect independently reproduced from authenticated current GitHub files

R220's old \`EXPECTED_EXCEPTIONS\` asserted that three cited source IDs were **absent from author source-use metadata**: twice \`{{cite:cdc-find-clean-water}}\` in Article #7 and once \`{{cite:start-ready-plan}}\` in Article #20. This was once a meaningful *original-content review* list, but the currently frozen integration has already added **author-authored source-use explanations** to BOTH integrated metadata documents:

- #7 body blob \`67aa44e9a332f57fb70298a3867410d8f66c8c15\`, metadata blob \`91c730bd1c7a61fa3140a86245c9bc0c88160c29\`; two unchanged uses and a matching source_use key.
- #20 body blob \`68344cf6c4022285fffb2a01f42027bf6f9ee95d\`, metadata blob \`ba840917f34634ccd634c488eeca4a8a6b3a8fe2\`; one unchanged use and a matching source_use key.

Because R220 computed exceptions as *missing source_use keys* but required those old three entries, its \`verify_originals\` raised a false exception on otherwise frozen authentic inputs. Its prior synthetic originals fixture patched \`EXPECTED_EXCEPTIONS\` to empty and therefore missed the contradictory hard-coded production expectation. This is a **deterministic validation defect**, not proof of safety or source correctness. It also explains why a native originals-only test needed substantive audit rather than more cosmetic validators.

**Independent authentic census:** GitHub connector read all **35 original bodies and 35 current metadata documents** at R235 exact HEAD \`ac4a91921fc43ab490b1f215124edf5f728460c7\`. Counts: **2,000 authored citation occurrences**, with **0 cited IDs absent from their corresponding source_use metadata**; all 35 source_use entries used by the articles were non-empty strings. Author note presence **does not verify claim accuracy** or resolve the original three source-reading concerns. Editorial #7 and #20 proposals are still **REVIEW ONLY**; none applied.

## R236 fix and scope

- Update the *mechanical* R220 source-use mismatch expectation from three phantom omissions to **zero**. Do not remove or relabel the original risk.
- Add \`tools/r236_citation_source_parity_hold.py\` as an independently Git-blob-pinned read-only gate. It inventories exact 35 author bodies/meta, enforces n/slug identity, draft status, valid non-blank source-use explanations for **every cited ID**, rejects duplicate JSON keys/nonfinite JSON, and records a deterministic per-article SHA-256 evidence digest.
- Preserve the **two explicitly unadjudicated source review groups / three source occurrences** separately in an immutable \`UNREVIEWED\` review docket. Presence of a source-use explanation must never become an independent source, medical-safety or QD PASS.
- R220 runs the frozen R236 gate **before importing the renderer** in both originals-only and export mode; hard-asserts 35 article receipts, all three untouched editorial review occurrences, zero missing metadata notes and false approval flags; checks module Git identity again after audit.
- Existing R200–R235 original-body, crosswalk, source URL, publishing and 32-group review HOLDs persist. Do not merge or suppress source-reading disagreements, especially Article #7 CDC water safety and Article #20 emergency plan / medically dependent household advice.

## Test evidence / limitations

- **75/75 Python synthetic tests executed locally**, including **70 per-article** missing and blank explanation mutations and five controls for 35-source identity, still-unreviewed citations, forged duplicate JSON keys and nonfinite JSON. Python compilation passes.
- Tested module Git blob **\`78936188bcb636d638346348d51c5f44daf8e5e2\`** and test Git blob **\`4c35bca98c28d1ce8bf5ac15515155b77b32389f\`** match exact GitHub committed files. This is executable local source-level evidence, NOT a complete checkout pass.
- **Not executed:** full native \`python -I preparedness/tools/validate.py\`, \`python -I preparedness/tools/build.py\`, inherited suite, generated 41 article/tool and auxiliary page exports, independent browser/QD/qualified emergency-safety checks. Container GitHub DNS resolution failure remains. Do not claim native integration passed.
- The discrepancy is resolved in **draft R220 code**; it remains an unreviewed change and no public release is authorized.

## Conversion-first friction / owners (one provisional candidate only)

**High-intent topic:** household out-of-area emergency contact + essential document organization. **Authentic FREE destination:** the existing public official-resource index https://finalvestige.com/preparedness/ . Full 35 source-reviewed guides are NOT LIVE. One **provisional paid candidate:** Legacy Triage, an estate/incapacity-oriented $19 PDF; relevance to *general disaster preparedness*, merchant authorization, privacy/security, reliable checkout, delivery and refunds are NOT established. No existing true-fit, independently cleared Preparedness SKU has been demonstrated, so **no paid CTA or product promotion is approved**. A draft, noncommercial landing prompt only: *"Start with the free household planning resources. Official guidance remains available without signing up or buying."*

**OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER**
1. Free official guidance → creator landing: real published Grok asset_id, platform URL, rights, exact hook/UTM and phone destination missing → independent TASK-008 crosswalk → **UNVERIFIED** → Grok/Praxxis.
2. Free index → original article: 32 still-unreviewed shared-source groups, 3 original held citation occurrences, native build and qualified reviews incomplete → independent source reading and authentic validation → **HARD HOLD** → Preparedness/QA.
3. Free planning → optional Legacy Triage: buyer-intent mismatch, product rights/security/FTC/privacy/offer terms unresolved → inspect complete PDF, merchant ownership, consent and buyer-suitability before any proposed CTA → **NOT APPROVED** → Founder/Commerce.
4. Paid PDF → realized sale: checkout/receipt/fulfillment/refunds not validated → authorized merchant check with actual transaction settlement → **NOT TESTED** → Commerce.
5. Qualified sessions → net revenue: unique asset_id sessions and independently settled orders/fees/refunds unavailable → privacy-safe 7/30d matching and net-realized ledger → **NOT COMPUTABLE** → Claude Analytics/Commerce.

No claimed leads, orders, affiliate sales, revenue or synthetic conversion wins. Maintain existing analytics; do not add vendor scripts. No retired water guide, no speculative SKU, no unapproved paid product. Marketing and editorial remain isolated.
