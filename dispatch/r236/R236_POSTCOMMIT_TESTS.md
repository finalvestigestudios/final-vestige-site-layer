# R236 — Exact-source postcommit verification (2026-11-09 16:xx UTC)

## Reproducibility / source identity
Parent: founder's original PR #175 HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`, **not** R235 and **not** frozen homepage PR #49. This new branch creates only `dispatch/r236/` files. Prior source content and original manuscripts are unchanged.

## Original native Python test (the first time this particular historical suite was actually run)
The original eight GitHub source files were read using the authenticated GitHub connector at PR #175's exact head and reconstructed locally. Each file matched its corresponding Git blob SHA-1 byte-for-byte (see `SOURCE_AND_CONVERSION_EVIDENCE.md` for all eight hashes). The unmodified `tests/test_campaign.py` was executed against the unmodified six Markdown files and original manifest, using native Python's built-in unittest runner:

```text
python -m unittest discover -s tests -p 'test_campaign.py' -v
... test_commercial_copy_has_disclosure ... ok
... test_legal_gate_requires_footer_verification ... ok
... test_links_not_activated ... ok
... test_no_invented_commercial_promise ... ok
... test_primarily_editorial ... ok
... test_six_issues_not_scheduled ... ok
Ran 6 tests in 0.002s
OK
```

This proves source-guard behavior on exact historical blobs and does **not** establish email readability in Jetpack, legal completeness, consent, final merchant permission, valid checkout or purchases. The private GitHub repo could not be cloned from the container due to DNS; Git blob-level equality, not a checkout, was used to guarantee original-source identity.

## New independent postcommit source-level safety execution
Fetched the five exact R236 GitHub-committed artifacts (`ISSUE05_TOTAL_FOCUS_ALTERNATIVE_UNSENT.md`, `ISSUE05_REVIEW_ONLY.txt`, `ISSUE05_REVIEW_ONLY.html`, `SOURCE_AND_CONVERSION_EVIDENCE.md`, `R236_GUARD.cjs`) then executed that same committed `R236_GUARD.cjs` in a detached V8 harness with immutable fetched inputs. **50/50 baseline assertions PASS.** This is source-level V8 execution, **not** a native Node CLI or real email rendering.

Initial adversarial review exposed four weaknesses: partial subject replacement retained a matching `<title>`, removed disclosure could pass the old order comparison because `-1 < index`, and a fabricated-revenue statement could pass a weak not-computable test. The check was fixed in a separate commit (`986821a88597f9ef9a90664481e82c6cb43cf274`).

**Final committed check:** 50 baseline assertions pass; **20 of 20 distinct unsafe mutations rejected**, including commercial/unsent marker removal, activating guide placeholders, changed visible email heading, subject/preheader drift, missing visible disclosure in both HTML and Markdown, missing postal/unsubscribe blockers, affiliate tracking/PII, fabricated efficacy, invented checkout price, tracking image, script or form, missing HTML lang, merchant source substitution, original head substitution, and fabricated positive revenue. No test attempted to send an email or exercise a recipient's unsubscribe mechanism.

## Review-only HTML accessibility/source safeguards
The HTML is dark-text-on-dark-background? **NO**: foreground `#f0eee8` on `#121411`/`#191c19`, high-contrast body, one H1, `lang=en`, 600px maximum width, semantic source list, inline styles, six direct official/editorial non-earning **citation** links, no images, pixels, scripts, forms, buttons or active offer destination. These are structural assertions only; no real mail-client screenshot or Jetpack/native preview exists. Full WCAG/email-client conformance is not claimed.

## Release state
**All original six = HOLD_UNSENT. Original commercial 03/05 = HOLD_MERCHANT. R236 alternative Issue 05 = NOT ADOPTED, NOT PUBLISHABLE.** No subscriber access/exports, email, test message, WordPress mutation, actual affiliate URL, analytics script, homepage change, sale or net-revenue claim.
