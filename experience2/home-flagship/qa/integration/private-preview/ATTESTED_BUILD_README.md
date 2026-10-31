# Exact-HEAD private WordPress staging ZIP custody — Experience 2.0

**Unpublished / HOLD / no CMS writes.** Companion to PRs #225, #231 and #238. Frozen homepage PR #49 is unchanged. PR #224 remains an unmerged alternate staging renderer.

## Concrete defect closed

The provisional `build_private_preview.py --expected-head <SHA>` accepts a caller-provided 40-hex label without checking whether the checkout actually points to that commit, whether bundled files are tracked and clean, or whether ZIP hashes correspond to the committed bytes. A stale or modified staging ZIP can therefore be incorrectly labeled as an exact-HEAD build.

The new `attest_private_preview.py` is a strict entry point around the existing private staging builder. It verifies the *actual Git HEAD*, checks 17 source/security files against `git show HEAD:<path>` before importing local build Python, refuses symlinks/untracked or altered files, enforces the eleven runtime assets, and executes the canonical Node source/rights gate on the same checkout. It builds the sealed archive twice and requires byte-identical ZIP output, exact manifest source hashes, the guarded PHP-only four-file ZIP structure and an explicit RELEASE HOLD receipt.

## Reproduce

Run from the complete repository checkout, using Python 3.10+, Node and Git:

```bash
python -m unittest discover \
  -s experience2/home-flagship/qa/integration/private-preview \
  -p test_attest_private_preview.py -v

HEAD=$(git rev-parse HEAD)
python experience2/home-flagship/qa/integration/private-preview/attest_private_preview.py \
  --repo . --expected-head "$HEAD" \
  --out /tmp/fv-ex2-private-preview-attested.zip \
  --report /tmp/fv-ex2-private-preview-attestation.json
```

The receipt records the attested SHA, 17 file SHA-256 values, deterministic build assertion, ZIP hash and all outstanding release blockers. The ZIP is never installed automatically. Avoid importing or executing unreviewed checkout code: this gate verifies the source hash first, but it does not establish the trustworthiness of the authors of the Git commit.

## Executed local tests and scope

**12/12 tests passed** using synthetic local Git repositories and the actual PR #225 PHP/builder bytes. Positive coverage: clean checkout, deterministic ZIP, four intended ZIP entries, explicit HOLD. Negative coverage: wrong/malformed SHA, dirty homepage/PHP/builder/contract, dirty importer prevented before execution, untracked/symlinked assets, missing Git provenance, modified asset contract, failed Node source gate.

The tests do **not** demonstrate the canonical complete homepage renders in WordPress. They do not measure image requests, accessibility, security headers on an actual authenticated WP response, Lighthouse/CWV, archival reuse rights, or field performance. Hosted exact-head tests and independent QD are still outstanding.

## Independent staging requirement / STOP condition

Only production `finalvestige.com` (WordPress site 256784396, Assembler) was visible in the connected environment=all site listing. No separately authorized private staging connection was available. **Do not install this plugin, modify page 6, or publish anything on production.**

Before launch, an independent nonproduction WP/Assembler installation with authenticated editor and controlled plugin deployment must execute actual browser tests: authorization/nonce/cookie/CSP/frame headers; 320–1920px and 200%/400% reflow; keyboard/touch/reduced-motion/no-JS/axe/screen-reader/Safari; real first-party archival image requests and transfer sizes; media-by-media rights signoff; Lighthouse on exact URL and real p75 field CWV when available. Hosted CI, independent QD, founder visual signoff and separate release approval remain mandatory.

Historical investigations retain priority over the Mind & Perception bridge. Preserve the 52-page Focus Fieldbook, Jetpack signup and 72 Margins entries. Do not insert affiliate checkout links or unsupported claims in the staging preview.
