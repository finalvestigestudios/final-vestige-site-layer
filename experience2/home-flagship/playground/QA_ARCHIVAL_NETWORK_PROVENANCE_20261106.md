# EX2 — archival network evidence hardening (review only)

**2026-11-06 PT · No production release or CMS writes**

- Stacked on draft #1339 exact parent `2ad4e35fc1239cdc1785279f0a66a63c005bd235`.
- Frozen #49, seven-chapter Blueprint, WordPress Page 6, #158 Apollo and #171 Mind were **not modified**.
- Source Blueprint blob `137c74a476005684a28f5ff9a36e75c6b03268f7`; SHA-256 `10af751569bf11a7fd18003e56cb7ccad9596f59606be9d5fb5d87d95784bb7c`.
- Actual WordPress/Assembler startup, hosted Jetpack, axe and Lighthouse still **NOT VERIFIED**. Release remains **HOLD**.

## Reproducible defect

Before this change, the private Playground bridge chose the expected format by looking for an Apollo filename in `currentSrc`, then checked only whether an HTTP response could decode as WebP/JPEG with dimensions >150px. `assert_semantics()` checks the HTML `src` attribute but not the **browser-selected `currentSrc`**, which often comes from responsive `srcset`. Thus a byte-decodable, unrelated or compromised origin could be recorded as accepted evidence.

Independent local negative control: an unrelated 400×400 WebP image (83,530 bytes) was **accepted by the former format-only decoder** but was **rejected** by `classify_source()` as not an approved original or allowed WordPress CDN derivative. This test is purely synthetic and **does not claim any real image was transferred**.

## Source-grounded media inventory

Read-only WordPress media API, 2026-11-06:

| ID | Source / provenance | WordPress metadata | Selected-URL restriction |
| --- | --- | --- | --- |
| **473** | Apollo 1 NASA S67-19766; credited in existing editorial caption | original WebP 1041×810, 78,346 metadata bytes | First-party original or approved 300×233 / 768×598 / 1024×797 WP CDN derivatives |
| **474** | Franklin Victory Point note; existing caption attributes public-domain Wikimedia scan of an **1869 printed reproduction**, original object RMG HSR/C/9/1 | original JPEG 960×1526, 466,043 metadata bytes | First-party original or approved 189×300 / 644×1024 / 768×1221 / 960×1526 WP CDN derivatives |

The rights-pending NYPL item #1258 remains excluded from the unpublished homepage candidate. These are **source metadata**, not successful HTTP transfer receipts. Do not overstate NASA endorsement or assume every reproduction of the Franklin object carries the same rights.

The candidate embeds **two original `src` URLs** on `finalvestige.com` but **seven responsive `srcset` URLs** on `i0.wp.com`. That is an expected Jetpack media CDN origin, **not a same-origin first-party request**. The new receipt labels the CDN selection accurately and keeps the first-party transfer release gate open; it does not silently certify it.

## Changes

1. `verify_archival_provenance.py` pins the two media IDs, allowed URL hosts/paths, expected WordPress size derivatives and permissible query fields.
2. `verify_private_playground_bridge.py` binds actual `img.src` + browser `currentSrc` + media index to real response status, content type, decoded pixel dimensions, byte length and SHA-256; it separately reports `first_party_image_transfers`.
3. `test_verify_archival_provenance.py` checks the actual committed Blueprint's two images and rejects cross-media substitution, deceptive hostnames, unknown CDN crops, extra query parameters, wrong MIME, HTTP failures, wrong dimensions and absent byte/hash proof.

## Local evidence and release controls

- **4/4** Python unittest methods passed on the exact extracted parent Blueprint, including multiple hostile URL and HTTP receipt cases.
- Negative control: old decoder accepts unrelated but valid 400×400 WebP; new provenance check rejects it.
- No network image transfer completed: runtime DNS cannot resolve WordPress/Playground hosts.
- No actual Playground/Assembler PHP/HTML render, WCAG 2.2 AA, measured Lighthouse/CWV, Jetpack signup or paid-sale conversion was established.
- Remaining gate: run the existing private Playground bundle in a genuinely networked browser, capture responsive currentSrc, actual response body hashes, full WordPress/Assembler DOM, axe, image-host decision, 320–1920px mobile/desktop, keyboard/no-JS (separate local WP), and measured lab performance. No release without founder approval.

### Conversion-first decision

**OFFER:** Free 52-page Focus Fieldbook. **STEP:** historical evidence trust → contextual CTA → confirmed lead → verified order. **BLOCKER:** an untrusted/undocumented image transfer could undermine evidence integrity or performance and yield a false passing review. **CHANGE:** bind image acceptance to actual approved media and response bytes while exposing CDN-vs-first-party status. **PASS:** offline source and negative controls. **FAIL/OPEN:** real hosted transfers, WordPress rendering, accessibility, net revenue attribution. **OWNERS:** interim homepage engineering/Site QA for UI; Claude for production attribution/checkout; Grok/Praxxis for acquisition.

No paid services, website edits, new claims, analytics scripts, affiliate URLs, emails, merges or deployments.
