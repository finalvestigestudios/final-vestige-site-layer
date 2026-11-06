# Apollo R161 — published gallery source audit and isolated browser regression

**Status:** BUILT / OFFLINE FIXTURE-TESTED ONLY / **STAGING HOLD**. Tracks [Apollo Experience #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and commercial contract [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). This additive file does not change any WordPress, homepage #49, Research Desk #158, PR #1222 or merchant setting.

## A genuinely changed finding (2026-11-06 read-only)
WordPress **published Page ID 2017** (`/apollo-1-evidence-atlas/`) now reports modification at **2026-11-05T18:19:45**. Its **editor source** includes three `data-fvx-chrono-photo` figures and corrected `box.querySelectorAll('[data-fvx-chrono-photo]')`; the previous singular-selector defect is **not present in that inspected source**. A range-slider handler selects photographs 0/1/2 at t<6, 6<=t<11.3, t>=11.3 and explicitly says pictures **do not depict the marked seconds**. The actual page was *not* remotely browser-accessible from this execution environment; a source inspection is not live browser QA, CDN image verification, or a new deployment.

Photos are context only: S66-58038 (1966 astronaut training), S67-15717 (January 1967 spacecraft preparation), and KSC-20170124-PH_KLS01_0129 (2017 memorial exhibit). The Apollo 204 Review Board report establishes technical chronology, not these photographs. Image rights for commercial marketing/paid packaging are **NOT CLEARED**.

## Reproduce
`python experience2/apollo-r161/live_gallery_contract.py --out /tmp/r161-first`  
`python experience2/apollo-r161/live_gallery_contract.py --out /tmp/r161-second`  
`diff /tmp/r161-first/SHA256SUMS /tmp/r161-second/SHA256SUMS`

The self-contained local Chromium *excerpt* fixture checks six widths (320/360/390/768/1440/1920), slider input, keyboard Home/End, visible-image count, 3 NASA links, context disclaimer, no checkout, no-JS source visibility, mobile overflow, deterministic screenshots and an intentional mutation to the obsolete singular selector. No external images or HTTP requests. **Do not mistake the fixture for the actual page**. Chromium localhost/HTTP navigation was refused by this runtime (`net::ERR_BLOCKED_BY_ADMINISTRATOR`); npm registry access to axe-core also failed with `EAI_AGAIN`. No fake axe result or production LCP/CLS is permitted.

## Release checklist — HOLD
1. Claude/site owner independently confirms page 2017 current published editor source and confirms gallery image loads, CSS hidden behavior and browser console at 320–1920. Include keyboard/touch/200%-400% zoom, no-JS, reduced motion and screen readers.
2. Test *installed* WordPress + Assembler + CSP + 3 real image loads + responsive gallery; genuine axe-core WCAG 2.2 AA with **zero violations and zero incomplete**, plus human accessibility review.
3. Measure realistic staging LCP/CLS with network/media delivery; independently inspect screenshots and record exact deployed hashes/CI/QD. Do not claim good CWV from an offline fragment.
4. Existing truthful next action: **Read original investigation**. A hypothetical educator dossier is **NOT** a verified rights-cleared SKU; no paid CTA. An affiliate click is not a purchase.
5. Grok owns video; Praxxis owns independent creator review via TASK-008. No verified Apollo asset_id/UTM/qualified-human denominator/merchant paid order. Per #820, realized net revenue per 1,000 qualified humans **NOT COMPUTABLE**.

**Control:** do not merge, deploy, modify CMS, publish, activate affiliate offer, send email, change tracking or spend without the existing review and founder release gate.