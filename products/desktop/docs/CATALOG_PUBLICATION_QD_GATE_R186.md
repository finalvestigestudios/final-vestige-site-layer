# R186 — six-app static catalog publication preflight (DRAFT / HARD HOLD)

Tracks issue #73, stacked on R185 draft PR #941, **not production/main**. All Windows x64 executables are **UNRELEASED**.

## Scope and protection

A source-only Gutenberg catalog can prematurely expose unsigned builds or unrestricted premium downloads even if the executable gate is working. The new offline standard-library preflight validates the tracked static draft before independent WordPress/QD review. It requires:
- Four free and two premium product H3s in the expected accessible H1/H2/H3 heading order, with exact **IN DEVELOPMENT** and **PRIVATE DEVELOPMENT PREVIEW** labels respectively.
- Exactly one approved contact-pilot hyperlink, at https://finalvestige.com/contact/. Reject unknown links, download attributes, external resources, scripts, iframes, forms, images, embed tags, event/data attributes and duplicate attributes.
- No-download status, sensitive-production-data warning, professional/human-approval disclaimer; bounded UTF-8, actual Gutenberg comments only, correct markup nesting, no dangling raw tags or BiDi/control overrides.
- Privacy-safe generic failure output without raw source content, file paths, financial inputs or premium URLs.

A passing check returns PASS_STATIC_DRAFT_ONLY with downloads_verified=false, premium_access_verified=false, site_publication_authorized=false, qd_approved=false. This checks only source draft—not served WordPress, build artifacts, malware scanning, payments, entitlement, code signing, or legal conclusions.

## Exact local evidence — November 4, 2026

Isolated Linux Python 3.13.5, PYTHONPATH=. from products/desktop:
- python -m unittest discover -s tests -p test_catalog_preflight_r186.py -q: **36/36 PASS**.
- python -OO -m unittest discover -s tests -p test_catalog_preflight_r186.py -q: **36/36 PASS**.
- **72/72 focused method executions**, zero skips/errors/failures; *not* a full-repository or native Windows test.
- Checker exact Git blob: **1b5130ccd44f4ab60c1ea9b9e455e44f60e04653**.
- 36-method test source exact Git blob: **09183fec931c1140e5cb0a05499c241cbf3cc3aa**.
- The unchanged original six-card Gutenberg source was recreated byte-for-byte locally, Git blob **6ab8fc98223330caae28a9964f36ee8a0c9ce6af**, matching R185. Exact catalog CLI: **PASS_STATIC_DRAFT_ONLY**, one pilot CTA, all six unreleased, QD/launch HOLD.
- Found and corrected a real first-read st_atime false-reject: verifier compares stable device/inode/mode/nlink/size/mtime/ctime, not access time. Added a regression that deliberately ages atime before reading.
- Both Ubuntu and Windows jobs now run 36 tests normal and -OO, plus exact real-draft preflight; they remain unexecuted while GitHub Actions runner allocation is broken.

## QD handoff and remaining gates

No GitHub Actions success, six Windows builds, physical Windows 11 accessibility witness, Defender/EDR, signing, actual premium entitlement controls, live WordPress readback, or founder approval has been established. **Do not merge to production or publish binaries, premium links, or the catalog from this evidence.**

**Next highest-impact action:** repo owner check Actions run error banner, billing/usage allowances and hosted-runner allocation, restore runners, rerun the unchanged R186 commit, and execute inherited suites including fourteen pending R178/R180 real-file integration tests. After that, build/smoke the six candidates privately and complete independent QD + founder signoff.