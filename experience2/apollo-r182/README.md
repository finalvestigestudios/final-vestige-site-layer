# Apollo R182 — exact-source browser gate (STAGING HOLD)

Part of Apollo Experience 2.0 Issue #150; conversion governance #820 and charter #818. Stacked additively on R181 draft PR #1348; original Research Desk PR #158 and frozen homepage PR #49 untouched. No production changes, CMS/merchant/social/email writes, paid services or analytics scripts.

## Verified gap and correction

The R181 test for six nasa.gov source links can pass even if a URL points to the *wrong* NASA photograph. It also does not reject altered photo chronology or missing commercial-rights HOLD. R182 extends R181 with exact 14 ordered source destinations from original Research Desk PR #158 (template blob 403d128c57b9bc82dac7c619651689070edef86c) and six source-role records from R174 (manifest blob 6cd3347238603dc049160a5dc7c38fe99cb1813a).

It checks all six archive-photo/written-source pairs, date/catalog matches, original #01 ID uncertainty, #05 post-fire photo limitations, the fact that 2017 exhibit photos do not depict the 1967 fire, distinction between images and Review Board technical claims, explicit media not-cleared notices, sole investigation CTA, and absence of speculative map pins or unrelated commerce. A valid NASA URL is not a media-use permission or proof that a photograph establishes a technical finding.

## Reproduction

From a full repository checkout, run Python unittest discovery in experience2/apollo-r182/qa using pattern test_strict_custody_gate.py. Execute strict_custody_gate.py with --fixture PATH --output DEST for an unpublished fixture. For approved nonproduction WordPress only: --url https://APPROVED_HOST/research-desk/ --approved-host APPROVED_HOST --axe-js PATH_TO_VERIFIED_AXE --axe-sha256 VERIFIED_SHA256 --output DEST. Production domains and cross-origin document redirects are rejected. Live WordPress testing must include real axe-core and manually verified screen readers; a fixture cannot approve release.

## Local verification (not release acceptance)

8/8 local Python tests PASS, including seven negative-control mutations: false NASA same-domain image route, wrong per-card photo, unsanctioned rights clearance, ID certainty misstatement, wrong fire aftermath date, speculative geo marker and unrelated merchant link. Two full genuine Chromium *fixture* runs: eight contexts each (320/360/390/768/1440/1920; 320 no-JS; 390 forced-colors); 336/336 assertions in each; 8/8 screenshot SHA-256 matches. Fixture result always HOLD. Laboratory fixture LCP ~72–136 milliseconds and CLS zero in one observed sweep; NOT WordPress or field p75 metrics. Exact GitHub-head CI, genuine axe, installed WP/Gutenberg/Assembler, NASA media/CDN live delivery, CSP, screen readers and rights remain UNTESTED.

## Conversion hypothesis / ownership

Target is a hypothetical educator arriving from a Grok-owned Apollo long-form asset, which is not yet verified as published. One appropriate action is Read original investigation. A future original educator case dossier is *not* an authenticated sellable SKU; no sale or paid affiliation is asserted. #820 requires unique asset_id/UTM -> qualified-human sessions -> investigation CTA -> confirmed lead where applicable -> merchant-confirmed paid order -> fees/refunds -> realized net revenue per 1,000 sessions in 7/30-day cohorts. Current attribution and orders are unverified, so commercial KPI NOT COMPUTABLE. Grok owns publication, Praxxis external QA/TASK-008, Claude production/analytics, founder approval.

**Release: HOLD.** Do not merge/deploy without exact-head CI, installed WordPress staging with axe and manual assistive tech, rights review and founder/Claude approval.