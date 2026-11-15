# R372 QA and reproducibility

- Parent: draft PR #2577 dac47473a98d4cecece0916b750c7af2ce103c18, inherited source-only. All files additive in dispatch/r372/.
- Original campaign PR #175 HEAD d57ccdba3aee8f065e143e101c2945f4f3d01647; eight relevant local archive files matched official GitHub blob hashes at current PR head. Executed python -m unittest discover -s master/dispatch/campaign-2026-mind/tests -v → **6/6 PASS**.
- Executed node --test dispatch/r372/test_focus_client_truth.cjs → **25/25 PASS** (Node v22, no external packages, 2026-11-15 UTC). Test covers arbitrary success strings, failed status, mixed status, class spoofing, no PII/event emission, frozen result. All synthetic; library never contacts subscriber/merchant.
- Executed python -m json.tool on CONVERSION_RELEASE_MATRIX.json → **PASS**. Executed BeautifulSoup semantic/static checks on FOCUS_REPAIR_REVIEW.html → **PASS**: en language, exactly one h1, valid link href, no form/script/img/iframe.
- Attempted local Chromium headless screenshot at four viewports and retried with single-process/no-zygote: **FAILED / timed out** (no screenshots produced). Do NOT claim browser/mobile/actual email client pass. Future QA must rerun in functioning browser environment.
- FOCUS_REPAIR_REVIEW.html is static offline visual proposal and explicitly **not Jetpack rendered**. Intended for 360/390/768/1440px pending real viewport evidence; no JS, forms, send controls, tracking pixel or merchant link.
- Source policy: Free PDF link is copied from configured Jetpack welcome message, not verified as delivered to a guest. Do not claim an opt-in from PDF access or is-subscriber CSS class.
- CONVERSION_RELEASE_MATRIX.json uses null for unknown recipients/sales/revenue, never zeros or invented A/B measurements.
- Pending: real provider authoritative email-eligibility filter, received welcome/guest PDF, native non-sending WordPress preview, publisher postal address and functional unsubscribe, offer-specific EMAIL rights, guides, issued referral URLs, final price/refund/checkout, independent paid sales.
- Evidence recording will include final PR HEAD and exact GitHub reread blob identities. No secrets, email addresses, telemetry or subscriber export included.
