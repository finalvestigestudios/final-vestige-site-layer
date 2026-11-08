# Experience 2.0 — consolidated seven-chapter release admission (2026-11-07)

**Status: DRAFT / RELEASE HOLD.** This PR creates a reproducible decision ledger over prior offline evidence. It does not edit the seven-chapter candidate, frozen PR #49, WordPress Page 6, the Assembler theme, Focus signup, affiliate URLs, 72 Margins items, or any art. It cannot approve a release.

## Why this exists

PRs #1469, #1484 and #1493 established full-source offline Chromium, PHP callback execution under WordPress stubs, and synthetic-media-decoder safeguards. The scattered PASS counts can be mistaken for native WordPress acceptance. This PR binds the source hashes and refuses to promote offline or synthetic results into live evidence.

**Source custody:** private preflight ZIP SHA-256 9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d; candidate PHP SHA-256 91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04. Assembler source pin is 75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f. Candidate hashes are not WordPress-runtime proof. Never use production database exports, subscriber data or secrets.

## Reproduce

Install Python 3 (stdlib only). From experience2/home-flagship/playground/, run the following, replacing the four paths with the **existing** protected local receipt files from PR evidence bundles #1469, #1484 and #1493:

    python -m unittest -v test_ex2_consolidated_admission.py
    python verify_ex2_consolidated_admission.py --blueprint /local/private/fv-ex2-local-cli-preflight-guarded.zip --php /local/private/php_hook_RESULT.json --browser /local/private/browser_acceptance.json --media /local/private/media_gate.json --output /local/private/ex2_decision.json

Do not upload private previews/public URLs to make the tests work. The verifier writes a machine-readable JSON and human-readable Markdown report. A nonzero exit means offline evidence failed; HOLD with exit 0 means prior offline evidence passed but the release is NOT authorized. No network, plugin installs, WordPress writes, subscription requests or sales events.

## Actual local receipt admission

- 12/12 self-contained adversarial tests PASS (synthetic fixtures are for verifier regression only).
- 5/5 prior offline source-custody gates PASS; 9/9 release gates HOLD.
- Existing full-source Chromium receipt: 28/28 offline viewport/JS/zoom checks, 4 interactions and 3 rejected negative controls; this PR does NOT rerun Chromium or assert new visual/performance measurements.
- Existing PHP hook receipt uses stubs, NOT WordPress core. Image-receipt tests used generated images, NOT authentic archival transfer bytes.

## Outstanding release acceptance

1. Execute the actual candidate in isolated WordPress core with pinned Assembler. WordPress.com Personal cannot make a native clone; Playground is NOT equivalent to hosted WordPress.com Atomic/Jetpack.
2. Measure actual browser network transfers and decode Apollo media #473 and Franklin media #474, documenting selected srcset URLs, HTTP response headers, bytes, hash, dimensions. Exclude rights-pending NYPL media #1258.
3. Run integrated axe and manual keyboard/touch/no-JS/reduced-motion/200%-zoom WCAG 2.2 AA checks, including Assembler's full page landmarks.
4. Run Lighthouse and identify measured lab scores separately from any real field CWV. No invented scores.
5. Check public Focus form without submitting test addresses or changing subscribers absent authorization. PR #1451 URL-parameter guard is not production approved; legitimate Jetpack redirects may be involved.
6. Independently verify archival rights and founder art-direction selection (Black Dossier / Museum After Hours / Observatory), exact-head CI and independent QD.
7. Require founder exact release approval; no publishing, merging, deployment, or plugin activation.

## Conversion-first decision

**Offer:** existing free 52-page Focus Fieldbook. **Funnel:** historical evidence → legible, unobstructed, relevant CTA → accessible Focus form → independently confirmed subscriber → independently verified paid purchase.

**Blocker:** live confirmed lead, actual order, merchant fees/refunds, and Grok asset_id attribution not established. **Change:** prevent an offline PASS from being presented as a functioning conversion system. **Experiment:** read-only responsive Focus interface acceptance and later privately authorized end-to-end confirmation. **Evidence:** protected offline receipts accepted, all nine release conditions HOLD. **Owner:** Interim homepage and independent Site QA; Claude owns Jetpack/checkout/analytics; Grok and Praxxis own acquisition.

**Net revenue per 1,000 qualified human sessions:** UNKNOWN — no independently confirmed paid conversions or trustworthy denominator supplied. No new instrumentation, tracking, subscriber actions, affiliate links, merchant claims, live editing or spending. Coordinate with #150 and #820; Apollo R&D #158 stays separate.
