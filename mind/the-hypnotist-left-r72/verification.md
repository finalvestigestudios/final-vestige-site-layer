# R72 proof and release ledger — 2026-11-02

**Scope:** isolated source only; no site or paid merchant activation.

## Source code and test provenance
- Compared against main base `77a87635eb613ce6de268aee11350fa8242efa0f`, base tree `761f15981ac8304dd456ac4f07eeb557a23dea26`.
- Final new-directory-only diff after this proof file: 12 ADDED, 0 MODIFIED, 0 DELETED.
- Re-fetched exact new-branch GitHub source for guide A, B, core, matrix, investigation, caption, attribution, test file and renderer; **35/35 source-scoped V8 assertions passed**. These were independent source checks, not native Node suite execution or host-run GitHub Actions.
- **8/8 dynamic synthetic privacy tests passed** using the exact fetched attribution implementation with ESM export syntax adapted to a function evaluator. Rejected email, UID and unknown channels; suppressed cohorts of 19; surfaced a cohort of 20; rejected min cohort below 20; no network/storage API. **Prototype never loaded on site; no actual people measured.**
- **5/5 adversarial alterations detected**, including removing a true HTML disabled property, injecting seller checkout href, injecting a subscriber form, removing disclosure, and introducing an active video tag.
- Source `tests.test.mjs` includes native Node `node:test` assertions; an early self-check found that shared CSS class names could cause a false positive for “A has film” and corrected the test to inspect `<figure>` markup. **Do not claim native Node tests passed** until executed in actual Node on the committed tree.

## Actual offline original film
- *The Hypnotist Left* — original six-scene silent animated educational short, not an original historical recording, licensed merchant creative, or Zen12 endorsement.
- **40.000 seconds**, **540×960**, **H.264**, **12 fps**, **480 frames**, **298,268 bytes**.
- Locally rendered using `render_film.py`, Python/Pillow and installed FFmpeg; source `git hash-object` **`3148f8a3eb1633511f419e78c0a857bebd684705`**, exactly matching GitHub committed blob SHA.
- MP4 SHA-256 **`8ac30c56ce63900ab3f5699f99bca1bfd9309af20896a43b4d17c173f255d5c8`**.
- Six frames visually inspected via contact sheet. Original poster PNG, six timed WEBVTT captions, offline HTML5 player, source renderer and contact sheet bundled in `offline-review.zip`; native local FFprobe/caption/HTML/archive checks **10/10 PASS**; ZIP CRC integrity PASS.
- Offline ZIP **454,528 bytes**; SHA-256 **`1888b32033e21786012f177fd8750a81446d49140532a1700079ad4c5ef246e7`**. MP4 and ZIP are generated review artifacts and **not uploaded to WordPress or committed in GitHub**. HTML candidate B accurately withholds website playback until first-party hosting and caption-sync QA.
- Local review player uses native controls, `playsinline`, `preload="none"`, full transcript and matching VTT; never autoplay or send network requests.

## Actual existing WordPress source checks (read-only)
- On 2026-11-02, WordPress authenticated list showed **61 published posts** and **79 published pages**.
- Read existing published Puységur page (WordPress page ID **1377**) and existing Focus Fieldbook landing page (ID **1579**); both live destinations used in noncanonical new source. No 7th category, changed navigation, duplicate signup or WordPress write.
- Focus page has one existing Jetpack-linked funnel; no other form introduced in this PR.

## What passing checks do NOT prove
No WordPress staging sanitizer test, native Node GitHub-hosted test, real browser responsive screenshots at 360/390/768/1440/1920, actual NVDA/VoiceOver and WCAG 2.2 AA audit, Lighthouse/CWV numbers, live first-party MP4/VTT synchronization, server production validation, legitimate controlled A/B assignment, conversion advantage, affiliate acceptance, approved URL or real purchases.

## Release hold
Written named Final Vestige partner approval and channel-specific rights; exact earning URL and legal promotion/creative terms; final offer/checkout/refund and privacy review; independent claims and accessibility audits; first-party media/caption verification; explicit founder release approval; Dispatch-specific EMAIL consent/source/received-mail scrutiny. **No merge, deployment, CMS, menus, Jetpack, newsletter, analytics, affiliate CTA activation or merchant outreach.**
