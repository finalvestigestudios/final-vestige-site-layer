# Experience 2.0 — extracted staging mount/source custody
**Review-only, RELEASE HOLD | 2026-10-31**

## Motivation: three reproduced false-positive admissions
The existing **unified Assembler Playground** binder (PR #303, exact base `706eb9f0e4afa02c0b3c31fb4d9fdd21a276a034`) checked that the theme and private-preview entry points existed and were not symlinks. It did **not** verify that the bytes *mounted into WordPress* still matched the source-attested archives created by the upstream builder.

In disposable synthetic Git repositories and local staging directories, the **original** binder accepted (1) replacement preview PHP, (2) modified Assembler CSS, and (3) an unexpected additional executable theme PHP file. These are local verification bypasses, **not evidence of altered production WordPress or compromised real media**.

## Correction
The proposed binder now compares the entire extracted theme file tree to the separately supplied original Assembler ZIP. It requires a **64-character, independently obtained SHA-256 pin** and matches it both against the source ZIP bytes and the preparation receipt; a hash stored in the editable receipt alone is insufficient. It rejects changed, missing, unexpected, linked, special, duplicate/case-colliding, path-traversing and oversized archive entries.

It also checks the exact extracted private-preview file tree against its source ZIP and checks that ZIP against the source preparation receipt. The main private-preview PHP file must equal its **exact committed Git version**, the source manifest must name the correct Git HEAD and all **11 canonical source asset hashes** must match `git show <HEAD>:experience2/home-flagship/<asset>`.

Critically, it independently **reconstructs the deterministic PHP source payload from those 11 Git file bytes** and compares the full payload to the staged ZIP. This rejects even a manipulated archive where an attacker adjusts the embedded payload hash, staging manifest and editable receipt in tandem. No PHP in the archive is executed during validation.

**External trust boundary:** The Assembler ZIP origin and out-of-band checksum still need an independent, documented authentic source. A checksum alone does not prove origin. The Git checkout must be inspected/reviewed and the exact-head canonical source gate must pass. There is still a filesystem time-of-check/time-of-use boundary until Playground uses these files: run in an isolated developer environment, never production.

## How to run after full exact checkout and authenticated theme acquisition
First execute the already-existing exact-source private-preview builder and upstream isolated stage preparation on the **same exact Git commit**, following their respective scripts/docs. Retain the generated `private-preview-release-HOLD.zip`, three provenance-tracked images and local-only WordPress CLI configuration. Obtain official Assembler **0.0.126** ZIP independently, verify it and separately record its SHA-256.

Then run from repository root (without connecting to production):

```sh
python experience2/home-flagship/qa/playground/parity/prepare_unified_playground.py \
  --repo . --expected-head "<EXACT_40_DIGIT_HEAD>" \
  --prepared-stage "<LOCAL_KIT_OUTSIDE_REPO>" \
  --assembler-zip "<VERIFIED_ASSEMBLER_ZIP_OUTSIDE_KIT>" \
  --assembler-sha256 "<INDEPENDENT_64_HEX_SHA256>"
```

This preparation-only program never starts a WordPress server, installs a plugin, imports a production database or publishes a page. If a check fails, it refuses the parity mount write. The successful receipt records matching file counts and archive SHA-256 values, **not a release approval**.

## Reproducible QA and provenance
- Baseline: **21/21** tests passed from exact PR #303 Git blob files, confirmed locally before modification.
- Before: three synthetic mount substitutions were **accepted** by the existing binder.
- After: those same three substitutions were **rejected before parity mount writes**.
- Expanded tests: **31/31 passed** with Python 3.13 in a disposable synthetic Git/ZIP fixture, including missing/extra files, nested symlinks, out-of-band checksum mismatch, rehashed plugin PHP and rehashed payload alterations.
- New binder/test files were compared after GitHub commit with the locally tested Git blob SHA-1 values. PHP importer syntax and original source were preserved.
- Chromium launched but **localhost, file:// and data: navigation returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` in the available sandbox**. Consequently there is still **no genuine WordPress/Assembler stage screenshot, seven-width/four-interaction/three-negative browser pass, axe, Lighthouse, or real historical image transfer result**.

## Release boundary
This change is stacked on the **PR #303** engineering branch, not frozen homepage PR #49 (unchanged exact SHA `10495883299d53596992c26a8987f629b2904670`). Apollo 1 R&D PR #158, Mind/Perception #171, Franklin art PR #254 and the seven-chapter HTML/CSS/JS are unchanged. No WordPress production writes, no merges, no plugin installations, no staging server startup, no new subscriptions.

The founder-confirmed WordPress.com **Personal** plan does not have native staging clone. The bundled `vestigefinal-tezws.wpcomstaging.com` host is the **production site's included address**, not a second environment. The goal remains a free isolated WordPress Playground/Assembler development site, with public content only. Such an environment does **not** prove WordPress.com-specific Jetpack subscriptions, cookies, redirects or field CWV.

**HOLD until** an authentic source-pinned Assembler ZIP, complete exact checkout, actual local WordPress execution, browser screenshots at 320/390/768/1440/1920 plus zoom, reduced-motion/keyboard/touch/no-JS and axe WCAG 2.2 AA review, measured lab Lighthouse/CWV, verified image bytes and publication rights, founder visual review and independent CI/QD are supplied. No claim of award win or of deployment readiness.
