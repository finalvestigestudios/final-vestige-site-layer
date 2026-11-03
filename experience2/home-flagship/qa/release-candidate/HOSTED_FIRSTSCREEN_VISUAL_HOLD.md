# Founder first-screen A/B — actual hosted homepage, not staging (RELEASE HOLD)

**November 3, 2026.** Evidence continuation of the existing EX2 seven-chapter flagship and Margins remediation, stacked on draft PR #765 exact head `6693e63536cf7d3f7f8b618fe133c76b4f1cbd52`. This draft never changes the published WordPress homepage, frozen PR #49, Apollo R&D #158, or Mind #171.

## What this closes

PR #746 proved synthetic fixture screenshots; PR #765 proved a **browser-local candidate** achieves 12.678:1 measured contrast and 7/7 anonymous hosted margin tests at 320/390/768/1440/1920 including reduced-motion and no-JS. Neither supplied a founder-review **first-screen screenshot of the actual public WordPress HTML with the candidate applied**. This isolated companion captures paired public-host first-viewport screenshots (unchanged production, then in-memory CSS override) at 320, 390 and 1440 CSS pixels. It checks 72 original Margins fragments, seven chapter anchors, a Focus link, absence of horizontal overflow, candidate CSS application and immutable screenshot SHA-256 digests. Raw archival images are not written as separate files. It blocks the NYPL Malbone reproduction URL before image download.

**These screenshots are a founder visual *study*, not QD, an approval, or a true browser zoom test.** Browser animation phase is not synchronized between the two captures; the script makes no pixel-identity or causal performance claim. Safari, NVDA/VoiceOver, actual 200% browser zoom, measured Lighthouse/CWV, first-party image completion and hosted Jetpack behavior remain separate gates. A successful screenshot job alone does not prove WCAG 2.2 AA.

## Privacy, rights and publication safeguards

- Anonymous GET-only browser, no credentials, cookies preloaded, forms, emails, WordPress API writes, subscriptions, media installs or database exports.
- Rights-unresolved NYPL map reproduction URL is blocked. The rest of the already public site may appear in the screenshots; do **not** redistribute these as independent archive-image licenses.
- **Specific NYPL evidence:** current public page 6 points to item UUID `c745e730-d2a9-012f-5ecc-58d385a7bbd0`, image ID `5003296`, and includes a statement that NYPL believes the item is public domain in the US. This wording is from *the published page itself*, not independently verified capture-level permission. The exact NYPL item URL could not be directly fetched for a rights readback; therefore its image-specific rights gate stays HOLD. NYPL's general reuse guidelines alone cannot clear this image.
- Source material for Franklin 1847/48 is an **editorial typesetting**, not a facsimile. Apollo/Franklin hero assets are otherwise unchanged.
- Screenshots record a public **first viewport only**, not subscriber records or authentication screens. A SHA-256 manifest links each image to the result. No claim of full-frame archival rights clearance.
- The production WordPress.com Personal tier does **not** have an independent native staging clone. WordPress Playground is not equivalent to the hosted WordPress.com runtime.

## How to run

```bash
python -m pip install 'playwright==1.56.0'
python -m playwright install chromium
cd experience2/home-flagship/qa/release-candidate
python -m unittest -v test_capture_hosted_margins_visual.py
python capture_hosted_margins_visual.py --output-dir /tmp/ex2-visual
```

Expected source receipt: three widths, HTTP 200, 72 Margins, seven chapter anchors and `candidate_active: true`; paired image files and SHA-256 hashes in `VISUAL_GATE_HOLD.json`. Any marker drift, navigation failure, CSS rejection or missing PNG fails the hosted job. The GitHub workflow uploads evidence even when the job fails, so never treat a missing run as a pass.

## Release decision

**HOLD** regardless of automatic results. Before further WordPress publishing: reconcile the already-published revision's founder authorization, verify image-specific NYPL item rights, review actual screenshots with the founder and an independent QD reviewer, complete manual WCAG 2.2 AA and physical device tests, measure field/lab CWV honestly, and receive exact release authorization. Do not merge this validation PR as a substitute for production authorization.
