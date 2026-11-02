# Flagship release package (2026-11-02)

**Verdict: HOLD.** Not yet ready to request go-live authorization: QD acceptance, the authenticated WordPress.com render of the exact block, and NASA item sign-off are outstanding. See `ACCEPTANCE_MATRIX.md`.

| File | Contents |
|---|---|
| `CONSOLIDATION_MATRIX.md` | What came from PR #550, #565, #580/#573 and what was excluded |
| `WORDPRESS_STAGING_DIAGNOSIS.md` | The real cause of the 302/502 behaviour and the working local WordPress |
| `ACCEPTANCE_MATRIX.md` | PASS / FAIL / BLOCKED / NOT TESTED, Lighthouse, blockers P0-P2, recommendation |
| `RELEASE_AND_ROLLBACK.md` | Exact proposed production change, verification and rollback |
| `IMAGE_RIGHTS_REGISTER.md` | Attribution and rights register for the three archival images |
| `PAGE_LENGTH_DECISION.md` | Decision record on page length and the preserved-content destination ledger |
| `dry-run/` | WordPress.com private-draft verification and the probe block |
| `production-change/` | Replacement blocks (1 and optional 2), originals (hash-verified), apply/rollback parameters |
| `evidence/` | Raw measured results and compressed screenshots |

## Reproduce

```bash
# 1. official Assembler (public download), kept outside the repo
curl -L -o assembler.zip https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip
# 2. isolated WordPress with the composed page (inline delivery = proposed production mechanism)
python experience2/home-flagship/wp-candidate/run_stage.py --work <dir outside repo> --assembler-zip assembler.zip --delivery inline --launch
# 3. real-browser QA, images, preservation, production-change artifacts
python experience2/home-flagship/wp-candidate/qa/run_wp_qa.py --url http://127.0.0.1:9400/ --axe <axe.min.js> --out <dir>
python experience2/home-flagship/wp-candidate/qa/measure_images.py --out <dir>
python experience2/home-flagship/wp-candidate/qa/verify_preservation.py --stage <work>/stage --live
python experience2/home-flagship/wp-candidate/qa/make_production_change.py --stage <work>/stage
```

Needs Node >= 20 (free `@wp-playground/cli`), Python 3 with Playwright and Pillow, Chrome. On Windows from Git Bash set `MSYS_NO_PATHCONV=1` and `MSYS2_ARG_CONV_EXCL='*'`. Nothing is sent to, or imported from, WordPress.com beyond public GETs.

All measurements are lab results on a local WordPress, not field Core Web Vitals and not production behaviour.
