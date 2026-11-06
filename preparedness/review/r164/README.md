# R164 Family Reunification Card static browser contract — DRAFT / HARD HOLD

**Scope:** Issue #136; commercial coordination #820 / charter #818. Parent R163 exact commit 42063b68fec2ed6bfe0af755a01df97ac415e5e5. This is an isolated stacked draft. No 35-article canonical content, source register, taxonomy, merchant, homepage, or public site changed.

## New structural pre-browser gate

The script preparedness/tools/r164_family_card_browser_contract.py calls existing R163 -> R162 -> R161 custody checks and pins staged R163 Family Card blob 1b8a340c69b28280ae485a667da4564d9e849d70. It checks one inert form, 13 bounded optional fields, 17 exact controls including checkbox/select/print/clear, labels, HTML IDs, no-JavaScript paper fallback, hidden initialization and live warning region, preserved source labels and card loss privacy caution. It rejects submit and endpoint drift, new data collection fields, external embeds, suspicious script/network/storage sinks, and overconfident privacy guarantees. It uses HTMLParser and a conservative lexical scan; this is **not** a full browser security audit.

Two template dependencies remain UNEXPANDED: shelter_common.js and reunion_card.js. They must be inspected in a genuine staged build; lexical scanning cannot establish that browser/page analytics, printing, extensions, form host, SDKs or obfuscated code do not transmit personal information.

The gate returns DRAFT_HARD_HOLD for a structural match and INVALID_HARD_HOLD otherwise; CLI always exits 2. It can never grant a safety review, source approval, QD PASS, browser privacy verification, commercial permission or release authorization.

## Test commands in trusted complete checkout

    python -I -m unittest discover -s preparedness/tests -p test_r164_family_card_browser_contract.py -v
    python -I -m py_compile preparedness/tools/r164_family_card_browser_contract.py preparedness/tests/test_r164_family_card_browser_contract.py
    python -I preparedness/tools/r164_family_card_browser_contract.py --repo .
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

**Actual local evidence:** 97/97 separate synthetic unittest cases PASSED; Python compilation PASSED, exact two committed code blob IDs compared to locally tested files. Full repo source/check/build and browser/WordPress acceptance NOT VERIFIED: local runner cannot resolve github.com DNS. No claims of 35-article integration execution or native QD.

## Real-browser acceptance (NOT PERFORMED)

1. Read the **expanded** inline scripts and inspect network traffic while typing household contacts, toggling minimal mode, clearing, choosing copies and printing. No new subscriber or merchant transaction.
2. At widths 360/390/768/1440px and keyboard/screen reader, test labels, 44px targets, alerts, no-JavaScript fallback, long names, international phone formats, text escaping, mobile clipping and print preview.
3. Print one to four fold-over cards on US Letter, 100% scale, common browser settings; verify no crop, sensitive-content retention or unexpected printed elements. Check reset clears form and preview; be explicit that OS spooler, third-party print/PDF handlers and browser extensions are outside static source.
4. Independently adjudicate the outstanding **75 source decisions** (11 Family Card relationships including Colorado/NCMEC scope and six HTTP-403 observations; eight Historical Food substitutions and 56 other decisions). A 403 is not a dead source. Recorded existing safety labels cannot act as independent safety/QD approval.
5. Require native build and independent source/safety/QD approval before any proposed release; founder controls public posting, production changes, spending.

## Conversion-first handoff

One high-intent hypothesis: parents/caregivers needing emergency school pickup and family contact planning. Grok/Praxxis retain TASK-008 creator asset IDs and distribution, not this lane. Proposed draft-only path: source-reviewed Household Emergency Plan (free without signup) → optionally printable Family Reunification Card (free, staged only) → a **verified existing rights-cleared purchasable Preparedness product**, if one is authenticated. At present none is verified here: **no paid CTA, merchant URL, or new product**. Retired water offers remain retired.

Draft-only copy: "Build your household contact and pickup plan — free guide."

| Offer → funnel step | Blocker | Change/experiment | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Existing paid Preparedness SKU → purchase | Matching rights-cleared current SKU, delivery/refunds and checkout unverified | Independently authenticate existing merchant listing and test staged path | HOLD, no paid sale evidence | Commerce/Claude |
| Free household plan → reader | Source/safety/QD pending | Complete qualified review and native validation | DRAFT/HOLD | Preparedness/QA |
| Free plan → practical card | Source scope, real browser privacy, print, accessibility untested | Apply R164 static gate, then independent browser matrix | 97 local synthetic tests only | Preparedness/Site QA |
| Grok social asset → landing | No authenticated Preparedness post ID or destination | Reconcile existing TASK-008, do not modify queue | UNVERIFIED | Grok/Praxxis |
| Paid order → realized net revenue | Attributed settled orders/refunds/fees and qualified-human session denominator missing | Source-linked 7/30-day merchant and session cohorts with small-sample warnings | NOT COMPUTABLE | Commerce/Analytics |

Essential free guidance may not be gated behind email or purchase. No analytic scripts, social posts, emails, checkout links or production changes authorized. All 35 instructional articles remain DRAFT / HARD HOLD.
