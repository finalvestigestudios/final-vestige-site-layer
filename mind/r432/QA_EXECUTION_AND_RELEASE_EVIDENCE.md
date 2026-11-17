# Mind R432 — Exact source QA receipt and release hold
**2026-11-16 PT | SRC-only, unpublished | pre-receipt verified branch commit 5d710e83932bab5ee46d69f76c8a3e5494cfb0a7**

## Source fidelity and execution

**Eight substantive exact UTF-8 GitHub blobs** fetched from R432 branch on 2026-11-16, plus the committed verifier (nine files before this receipt):
- THE_SECOND_NUMBER_ARRIVED.md blob `a391d08a9792312a0d6caac864bf46d3c8a624cd`
- ZEN12_A_TEXT_BUYER_GUIDE.html blob `8c0a975d0e2de2d317d161099165112e9409704c`
- ZEN12_B_42S_FILM_CONCEPT.html blob `a92517ad86b08fb561c83ccf4c58f4cf04fd31fe`
- ZEN12_OPTIONAL_42S.vtt blob `f795d842e61dba62daa4d54b9c67768b68232cdb`
- ZEN12_OPTIONAL_POSTER.svg blob `1a166e37fe40989bb776cfad49fd540a97cf659e`
- MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html blob `3c813bb8ea306520a8c67f8bcbc57108293e1b9f`
- CLAIM_SOURCE_AND_RELEASE_MATRIX.json blob `654957a143f9dc7bb4623764b834ac0897777810`
- CONVERSION_ACCEPTANCE_AND_GROK_CROSSWALK.md blob `70c6e35af88919aea76f7a5a735709c274074eb5`
- verify.mjs blob `58c35b8dc8c75e7f3fe15df42017968162def4cc`

**Executed:** The EXACT committed `verify.mjs` verifier body was fetched and run with a read-only filesystem shim, path adapter, assertion and console adapter in an isolated JavaScript V8 executor. The shebang/imports/import.meta/path resolution and process exit were adapted; verifier **logic** was otherwise unchanged. **80/80 static assertions PASS** across A/B substantive copy equality, all 28 HOLD release gates, 30 claims/23 sources resolution, accessible semantic markup and no-JS/no-third-party-script source checks, proximate disclosure, disabled commercial control, caption completeness (6 cues, 0–42s), original poster safe source, approved existing Focus route, no merchant earning links, and revenue/attribution truthfulness. Initial verifier regex escaping defects and two overly broad forbidden-string checks were fixed *before* the passing run. They are not counted as initial passing tests.

**Adversarial negative tests:** 10/10 deliberately unsafe synthetic mutations were rejected by the exact verifier, each on its own fresh in-memory copy of the verified blobs: enabling earning link, opening approval gate, inserting seller link, deleting disclosure, enabling paid button, injecting third-party script, altering caption endpoint, removing noindex, inserting remote SVG image, and fabricating a revenue figure. Detection of these synthetic violations is not proof of full production safety.

**Reproduce in a checkout:** `node mind/r432/verify.mjs` with no dependencies, **not executed natively during this run**. Native Node v22 is present in a separate isolated container but connected GitHub repository bytes are not mountable there and GitHub DNS resolution failed; therefore native execution against the exact GitHub files is **NOT VERIFIED**. GitHub Actions status, CI checks and Node integration not claimed.

## NOT TESTED, not silently passed

- Browser at 360/390/768/1440/1920, Lighthouse/CWV, screen reader, keyboard focus, zoom, real responsive rendering, WCAG 2.2 AA; CSS/string assertions are not substitutes.
- WordPress block sanitization, theme integration, Jetpack provider-confirmed lead/welcome, original film encoding/caption timing, source image/rights review, actual video playback or performance impact.
- Exact Final Vestige Inspire3 publisher approval, issued permitted link, partner email/social/web scope, final referred checkout/price/refund, order, merchant settled commission, real qualified-human denominator, privacy-consent events.
- New /mind/ is *source-only* HTML, **not** a WordPress CMS draft. Existing Focus/Dispatch list unchanged. No paid CTA, merchant link or analytics script is live.

## Conversion gating and reason for hold

Independent source review: 1992 RSVP paper https://pubmed.ncbi.nlm.nih.gov/1500880/ ; Slagter intensive retreat https://pubmed.ncbi.nlm.nih.gov/17488185/ ; 2022 theoretical review https://doi.org/10.3758/s13423-021-01973-2 ; official https://inspire3.com/ , https://zen12.com/ , https://zen12.com/getstarted ; FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

Read-only authenticated WordPress verified live 66 published posts (historical Issue #171 baseline 61), /focus/ id 1579, Puységur id 1377, Mesmerism post id 1924, Change Blindness post id 1922. **No live CMS writes**. Read-only Gmail affiliate/partner/commission search found retail promotion but did not establish named FV partner approval. The published Focus Fieldbook is a *free* resource, not a payable owned Mind SKU.

**No actual social asset ID verified; no attribution published.** Net revenue per 1,000 qualified humans = **NOT COMPUTABLE**, not zero. No fake payables or commissions.

**Owners / next independent gates:** Founder + Commerce authenticate exact eligible merchant/sellable SKU and return terms. Praxxis independently match already-published Grok asset IDs and approved mobile destination via existing TASK-008. Claude/site QA validate source-only landing in real browser and existing first-party tracking without new scripts. Dispatch owns Issue #174 and existing Jetpack welcome. Homepage #150/PR #49 and Mind hub #172 protected. No live changes without founder release approval.
