# Apollo R106 — fail-closed WordPress browser evidence (STAGING HOLD)

Issue: #150. Stacked only on independent Apollo R105 draft #873 (commit `03cf8b67ac800343b0c3cf05fd2dce9a9f5f4dea`). Preserve PR #49, original Research Desk PR #158, homepage owner branches and production WordPress.

## Failure modes found by actual source review

R105's receipt was atomic, but its completion predicate allowed misleading success: ten duplicates of the same browser result; missing HTTP scope fields; two axe records without the required selected state or meaningful pass count; an unmeasured LCP trial so long as *one* trial per width was observed; non-finite numerical values such as NaN (comparisons to thresholds do not reject NaN); Boolean values counted as numerical measurements; arbitrary PNG/PDF filenames with valid digests, regardless of file type; and replacing a completed journal by a new checkpoint. The R104 harness also wrote the human-readable QA report *before* R105 final validation and re-raised raw Playwright exceptions that could contain login URLs, page HTML or form values in CI logs.

## Implemented corrective controls

- Verify the exact 10 unique (width, JavaScript) browser results at **320, 390, 768, 1440, 1920px**, with true pass, genuine WordPress HTTP, reduced-motion and expected forced-colors flag on each.
- Require two selected-comparison axe-core scans at 390/1440 with nonzero pass count, exactly empty violation arrays, and both widths represented.
- Require **all six** discrete LCP/CLS trials (390 and 1440px × three), finite non-Boolean measurements, unique trial numbers, LCP **>0 and <=2500ms** and CLS **0–0.1**. A missing measurement or variability-related LCP failure is **failure**, never a convenient omission.
- Require the exact four screenshots and one PDF by name, SHA-256 match and PNG/PDF header signature; reject substituted names or mismatched bytes.
- Validate the exact isolated-core release scope flags; never turn a local test receipt into hosted WordPress.com or production Core Web Vitals evidence.
- Refuse attempts to overwrite a completed receipt through another checkpoint or completion call.
- Only write the human-readable full QA report after the final journal acceptance. Replace raw exception traceback propagation in the CLI with a non-secret, type-only progress journal and a fixed failure message.

## Reproducible local test contract

```bash
python -m py_compile experience2/evidence-atlas/tests/qa_receipt_r105.py experience2/evidence-atlas/tests/test_qa_receipt_r105.py experience2/evidence-atlas/tests/browser_real_wp_gallery_r104.py
python -m unittest discover -s experience2/evidence-atlas/tests -p test_qa_receipt_r105.py -v
```

On the locally prepared functionally equivalent source, **27/27** hermetic unit cases passed (11 inherited, 16 additional adversarial tests). Local validation is **not** a green GitHub exact-head CI assertion. Genuine WordPress/Playwright/axe tests and repeat LCP/CLS must run at the final Git SHA. CI dispatch had failed with zero steps at R104/R105; do not reclassify pre-runner failure as test failure or success.

The strict matrix may surface additional genuine browser performance or missing-observation failures. Preserve them rather than relaxing the 2500ms LCP/0.1 CLS thresholds.

## Source, content, rights, and release guards

This change is only test/receipt infrastructure. No NASA photographic-use assessment is cleared (0/6), and the `S67-19766` portrait association remains provisional. No media added, geography invented, relationship edges inferred, WordPress content/settings written, paid service activated, homepage file touched, branch merged, plugin deployed or production changes made. Actual hosted WordPress.com/Assembler/browser acceptance, independent NASA source and rights review, manual NVDA/VoiceOver, real touch devices and zoom, independent QD/editorial review, field performance verification and founder approval are mandatory. **STAGING HOLD**.
