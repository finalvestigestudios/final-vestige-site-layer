# Release HOLD: exact archival transfer identity + 72 Margins

Parent is draft #1017 at `0c76662d8a4e81028f7389f40765554174b86f83`. Changes affect the **published-homepage read-only browser gate only**; they do not change the live homepage, the frozen #49, design assets, Jetpack or affiliate offers.

**Source witness:** Connected WordPress Page 6 is published, last-modified `2026-11-04T14:39:24` per WordPress; seven chapter destinations and 72 sequential `.fv-margin-strip__item` records (indices 0–71) are present, with three `data-fv-archive-img` exhibits and 4 Focus links. Published exhibit filenames: Apollo `s67-19766.webp` (#473), Franklin `Franklinexpeditionnote.jpg` (#474), NYPL `edit-017-v02-nypl-5003296-original.jpg` (#1258). The exact markup includes descriptive alt and responsive CDN variants. Source presence does NOT establish visitor-rendering, rights clearance, successful media transfer, or paid conversion.

**Defect:** Parent #1017 could count positive HTTP bytes from a different same-filename image/derivative as proof that a decoded exhibit was transferred. It also lacked a preservation check for 72 Margins. This is a test false-pass risk, not evidence of a broken live image.

**Change:** SHA-256 fingerprint of normalized HTTPS `currentSrc` must match the actual image HTTP response's fingerprint; require three unique explicitly marked exhibits, meaningful alt, decoded positive bitmap and 200/positive body bytes. No query-bearing URLs retained in receipts. Reject external/untrusted/non-HTTPS paths. Require 72 sequential nonempty Margins in both JS/no-JS whole-page checks.

**Actual test status:** 11/11 transformed source-helper positive/adversarial checks passed in V8 with **hash and URL shims**, before upload. New Node tests are committed, NOT run in an exact checkout. Live Chromium, full axe, image bytes, Lighthouse, zoom, image rights, CI/QD remain **UNVERIFIED** due network restrictions and GitHub pre-runner failure. Do not treat this as full WCAG or production acceptance.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:** 52-page free Fieldbook → evidence/Focus click → image-match false-pass + untested 72 records → strict full-page gate → source check + V8 preflight, no sales → homepage QA; commercial attribution Claude; Grok/Praxxis acquisition. Net revenue unverified.

**Release HOLD.** No merge, publish, CMS writes, email, affiliate deployment, tracker installation, purchases or spending.
