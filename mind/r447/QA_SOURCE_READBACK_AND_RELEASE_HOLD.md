# R447 — Source readback, V8 QA and release HOLD receipt

**Date:** 2026-11-17 PT. **Status:** UNPUBLISHED SOURCE-ONLY / DRAFT / COMMERCIAL HARD HOLD. 
**Branch:** `mind-r447-rubber-hand-ownership-conversion-20261117`.
**Native command after checkout:** `node mind/r447/verify_r447.cjs` — committed, **NOT executed natively** during this run.

## What was actually run

Using the connected GitHub API, nine exact source blobs on this branch were fetched independently and read into a read-only V8 harness. The harness loaded the **committed** `verify_r447.cjs` verifier function; no website, merchant account or WordPress site was mutated. The first run passed 97/101 and exposed four false-positive assertions: an over-specific unused vocabulary word, a warning about autoplay matching the word “autoplay,” and disallowed urgency matching the sentence that denies a countdown. The actual buyer copy also initially had an invalid nested <main> landmark; both A and B were corrected by dedicated source-control commits. The verifier predicates were corrected; re-read the committed files and exact final verifier blob, **101/101 static/source assertions passed**.

**Mutation challenge:** 12/12 deliberately unsafe changes were independently detected: native disabled button removed; active merchant href injected; disclosure removed; new email form; third-party script; keyboard focus removed; reduced-motion protection removed; noindex removed; invented sale price; forced video autoplay; extra nested main; free Focus link replaced by a fake anchor. These were **synthetic in-memory alterations only**; they were not committed to the branch.

## Exact audited Git blob SHA (2026-11-17)

| Artifact | Blob SHA |
| --- | --- |
| Original body ownership investigation | `6c0f76e78e22ded1f5a557d86970b4fb1cbca583` |
| Zen12 A text-only guide | `8f31e738d15b0dc4e5d85a3cb00b8dddd0cae189` |
| Zen12 B optional-film concept | `9e4d4d6baf32a41b61eab4af7132cab74ba2308e` |
| Original static SVG poster | `f87a33c50b572e8f0950bb0eb607839eec4a9b1f` |
| Timed 42-second WebVTT captions | `75a309699936a52ef92106d8bfb94efd02c79a8a` |
| Source-only responsive Mind hub | `99ec954f42a4d3416bd292582bde3d0a5df820d6` |
| 34-item claim/source matrix, 28 closed gates | `3219f4cf1a9050c876795d12491cc1cdeb1021aa` |
| Creator/offer/paid conversion measurement dossier | `55bd39a61326250e71f293fa1316494cdbbc839c` |
| Source validator after false-positive corrections | `7759eeadc99f0ff554dcf88d4520d074fe72882f` |

## QA scope and limitations

**Static/V8 PASS:** single main landmark in each HTML file, no-JS, no script/iframe/tracking pixels, no extra email form, disabled merchant control, adjacent prospective FTC disclosure, no active merchant href, mobile responsive source, keyboard focus declarations, reduced-motion source, noindex, A/B complete substantive buyer-copy parity, original poster without executable code, six VTT cues ending at 42s, source-based product-feature qualifiers, 34 sourced claim entries, and all 28 commercial gates hard-held. The free Focus CTA is a legitimate **existing** page link, not merchant activation. “Source-level PASS” is not “WCAG 2.2 AA certified.”

**UNTESTED / required before release:** native Node runtime (only V8 was used), hosted CI, actual 360/390/768/1440/1920 browser screenshots, keyboard/VoiceOver/NVDA, contrast and responsive overflow with site fonts, WordPress CMS sanitization and block rendering, CSP/media restrictions, actual playable rights-cleared video decode and captions, web vital/Core Web Vitals, independent link-health across production routes, Jetpack opt-in confirmation/delivery, exact partner-approved referred buyer checkout and refund reconciliation, signed customer privacy approval and real paid merchant settlement.

**Video state:** original static SVG, transcript and WebVTT **only**. No encoded video was claimed, uploaded, played or served. No A/B visitor assignment or qualified human sample exists. **Zero new production scripts.**

**Commerce state:** Public affiliate portal is not named Final Vestige approval. No verified SKU, WEB/EMAIL rights, issued earning URL or authenticated referred price/return/settlement for Zen12; no existing paid rights-cleared FV Mind SKU authenticated. Focus Fieldbook remains free. Event names are only an analytics specification. There is no merchant-confirmed paid order or qualified-human session denominator. `net revenue / 1000 qualified human sessions` = **NOT COMPUTABLE**, not a numerical zero.

## Primary and official source custody

- Botvinick & Cohen (1998): https://doi.org/10.1038/35784 (**publisher abstract and figures listing; full text paywalled**)
- Rohde et al. (2011): https://doi.org/10.1371/journal.pone.0021659 (open full text)
- Tosi et al. (2023): https://doi.org/10.1177/17470218231156849 (**abstract only**)
- Roseboom & Lush (2022): https://doi.org/10.1525/Collabra.32274
- Slater & Ehrsson (2022): https://doi.org/10.3389/fnhum.2022.834492
- Direct cortical evidence (2019): https://pmc.ncbi.nlm.nih.gov/articles/PMC6373693/
- Seller specific: https://inspire3.com/ ; https://zen12.com/about ; https://zen12.com/ ; https://zen12.com/secret/ ; https://hypnosislive.com/mental-skills/total-focus ; https://brainwaveshots.com/focus-shot ; https://affiliates.inspire3.com/
- FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Existing owned live routes: https://finalvestige.com/focus/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/2026/11/02/change-blindness/ ; https://finalvestige.com/2026/11/02/mesmerism/

## Owners and zero-live-change boundary

Founder/Commerce must authenticate partner or paid-owned offer and confirm release; Claude owns CMS and analytics integration; Mind owns buyer/editorial/claim test; Site QA owns independent browser and WordPress review; Dispatch owns newsletter and existing welcome; Praxxis/Grok own social handoff and production respectively; homepage artist owns Issue #150, and PR #49 and prior Mind PR #172 remain untouched.

**NO CMS write, navigation, release, newsletter change, live affiliate link, Grok queue edit, payment test, merge, deploy, spending or new service.**
