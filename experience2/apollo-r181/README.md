# Apollo R181 — installed-stage QA hardening (DRAFT / HOLD)

Independent Experience 2.0 Apollo scope, Issue #150, stacked on R180 draft PR #1342 (commit f675af4ef0071b08261a081b191fe7f35ce9fab5). Commercial governance: Issues #820 and #818. This does NOT alter homepage PR #49, Research Desk PR #158, live WordPress, Grok's production queue, analytics, merchants or email.

## What this actually fixes

R180's real-staging preflight accepted any existing file as axe-core; a staging URL could redirect to an unreviewed production host; and it required an image where the six-record source-ledger template contains NASA *links* rather than embedded photos. Its seven-context exact-head fixture sweep also stalled when Playwright add_style_tag was used with JavaScript disabled.

The additive R181 runner replaces that QA path for **future approved staging tests**. It pins a reviewer-supplied local axe-core file by SHA-256 and checks its runtime API, blocks all cross-origin *document* redirects, separates Research Desk links-only from optional gallery decoded images, sets per-context timeouts and writes partial HOLD reports. It also checks six records, the catalog uncertainty warning, NASA source destinations, the single original-investigation CTA, keyword search/reset, no-JS evidence, keyboard/touch, reduced motion and forced-colors. Eight browser contexts: 320/360/390/768/1440/1920 JS, 320 no-JS, 390 forced-colors. Screenshots and SHA-256 hashes, laboratory LCP/CLS observations, and machine-readable receipts are produced without analytics scripts.

## Run (lab only)

    python -m unittest discover -s experience2/apollo-r181/qa -p 'test_strict_gate.py' -v
    python experience2/apollo-r181/qa/strict_gate.py --fixture /absolute/path/to/R179-source-derived-fixture.html --output /tmp/apollo-r181-fixture

The fixture is an unpublished local sample. **Fixture verdict is always HOLD**, even with all checks passing. Real staging is untested in this change.

## Run (ONLY on separately authorized, installed WordPress staging)

    python experience2/apollo-r181/qa/strict_gate.py --url https://AUTHORIZED-STAGING.example.org/research/ --approved-host AUTHORIZED-STAGING.example.org --axe-js /absolute/path/to/verified-axe-core.min.js --axe-sha256 VERIFIED_64_HEX_SHA256 --image-policy links-only --output /tmp/apollo-r181-staging

Obtain the axe-core file from the official repository/package and independently verify the digest. We do not download, vendor or independently authenticate a particular axe release. Use --image-policy gallery --minimum-images N only after a rights-reviewed gallery is actually installed. Source-ledger links-only acceptance is NOT a gallery/media/CDN acceptance. The gate also cannot prove NASA commercial photo rights, deployment CSP, screen-reader usability, field Core Web Vitals, consent, or merchant attribution. The real staging result is at most a technical candidate needing independent QA and founder release approval; it is NOT a release token.

## Reviewed exact-source inputs

- R180 prior gate Git blob 112dfafee5fcd39d6a99e6b671b399ff733bbd3d.
- PR #158 original JS blob 32e757cc4dc8708397ff65ac21e89dd319781d78 and PHP adapter blob d1879a90101b5475990132369178f42743f4b57c.
- R179 fail-open JS blob 822ff332711d129de077463e3d33e58144f48467.

Offline local source-equivalent verification: 7/7 Python safety unit tests PASS; 8/8 Chromium fixture contexts complete; 96/96 per-context checks PASS; screenshot hashes stable in a prior two-run comparison (reconfirm on exact committed version). These are **not** genuine axe-core, WP staging, screen-reader or actual NASA media checks. No exact-head GitHub CI confirmation yet.

## One restrained conversion pathway

High-intent audience hypothesis: a history educator arriving from a Grok-produced Apollo 1 long-form video (published asset ID, campaign URL and attribution NOT VERIFIED). The Research Desk preserves ONE contextual "Read original investigation" action, sources/chronology, and explicit uncertainty. A future original educator evidence dossier is a *product hypothesis*, not a cleared available SKU. Do not insert paid-product links until Commerce/Claude and the founder verify rights, Payhip listing, working checkout and delivery.

Issue #820's measurement: qualified human sessions by verified asset_id/UTM -> source/CTA action -> optional confirmed lead -> merchant-confirmed purchase -> refunds/fees -> realized net revenue per 1,000 qualified sessions, with seven/thirty-day cohorts. None of those Apollo revenue values is verified in this QA lane; do not conflate visits/clicks with sales.

## Release and ownership HOLD

Needs actual installed isolated WP staging, source-bundled PHP/template/CSS/JS, genuine axe, real NASA media/image rights, CSP and assistive-technology acceptance, screen-reader signoff, exact-head CI and independent review. Claude owns core engineering; Grok owns scripts/distribution; Praxxis owns external creator QA; founder owns posting, spending and release approvals. Nothing here grants an unreviewed deployment or a WordPress write.
