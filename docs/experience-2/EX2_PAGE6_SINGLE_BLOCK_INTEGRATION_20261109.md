# EX2 — Single-block Page 6 Integration (REVIEW ONLY / RELEASE HOLD)

**Source:** read-only connected WordPress.com Page 6 (production site 256784396), checked November 9, 2026. Parent PR #1853 exact SHA 0c6530e8264edab92516de6119adc0495db3d714. Frozen PR #49 untouched.

## New live-source discovery
Production Page 6 ALREADY contains an earlier seven-chapter experience inside the SECOND of five Custom HTML Gutenberg blocks. This is not a blank landing page. Replacing all Page 6 source would destroy existing content; inserting a second flagship would duplicate chapter anchors. The scoped integration must replace exactly ONE existing Gutenberg HTML block and leave all other blocks unchanged.

Read-only real Page 6 in-memory splice: 5 Custom HTML blocks; unique flagship block length 107,978 characters; untouched prefix 15,503 characters; untouched suffix 27,229 characters. The untouched 42,732 characters include all 72 original Hidden in the Margins records (in the first block), one native serialized Jetpack subscriptions block, the existing separate Focus CTA, and all other page material. An in-memory sentinel substitution preserved those exact outside source slices and their contents. No WordPress write occurred. Production Page 6 modified timestamp returned: 2026-11-05T12:07:24.

In the view representation, Jetpack Subscribe renders a link pointing to Page 6 with query parameters. This is a genuine conversion-verification question, NOT proof of broken Jetpack, successful subscriptions or email delivery. Real confirmation and delivery behavior must be accepted separately without adding subscribers without authorization.

## New source-controlled engineering
tools/experience-2/compose_page6_flagship.py: Offline-only draft generator, takes public-only WordPress context=edit Gutenberg content and the 11 exact-source Experience 2.0 files under experience2/home-flagship. The source files have been independently pinned to GitHub blob hashes from exact parent #1853. It substitutes exactly one flagship wp:html Gutenberg block and asserts that all other byte sequences survive unchanged. It fails closed on missing/duplicate flagship, duplicate chapter IDs, missing 72 original Margins, missing native Jetpack or Focus CTA, Gutenberg delimiter injection, and source SHA drift. The isolated candidate's nested site-level header/main/footer landmarks are converted into scoped elements for the WordPress theme; original evidence, first-party destination URLs and three art directions are retained.

tests/experience-2/test_page6_scoped_composer.py: 14 synthetic regression cases.
tests/experience-2/verify_page6_scoped_composer_chromium.py: seven responsive widths, JS on/off, reduced-motion, synthetic integrated fixture. This test NEVER performs a real Jetpack signup.

## Reproduction (no CMS writes)
1. Capture public-only WordPress Page 6 context=edit content into a local UTF-8 file; verify the latest fingerprint and contents. Do not export users, subscribers, private database, passwords or secrets.
2. Run: python tools/experience-2/compose_page6_flagship.py --page6-raw /local/page6.blocks.html --expected-page-sha256 <freshly-reviewed-sha256> --source-dir experience2/home-flagship --out /tmp/flagship-offline.blocks.html --receipt /tmp/flagship-offline-receipt.json
3. Run: python -m unittest discover -s tests/experience-2 -p test_page6_scoped_composer.py -v
4. Run: python tests/experience-2/verify_page6_scoped_composer_chromium.py
5. Do not upload or activate the output in WordPress production. Run first in an explicitly authorized isolated WordPress Playground / developer site and independently inspect the actual native render.

## Observed tests (local equivalent source, NOT clean exact-GitHub-HEAD)
- 11/11 source blob SHA identities verified at parent #1853.
- 14/14 local Python synthetic unit tests passed including negative controls and repeatability.
- 14/14 local Chromium synthetic integrated tests passed across 320, 360, 390, 768, 1024, 1440, 1920 CSS pixels with JS enabled/disabled and reduced motion. No horizontal root overflow observed. Synthetic 72 records and a NONFUNCTIONAL Jetpack placeholder were used; not a genuine WordPress/Assembler or signup test.
- Offline mobile before/after fixture captures show the evidence and native-content placeholders in a scoped composition; fixture banner/strip changes first-fold geometry, not proof of increased conversions.

## Mandatory release blockers
Actual isolated WordPress + Assembler render and Gutenberg-parser acceptance; native Jetpack confirmed subscriber/delivery semantics; real archive asset bytes; independent rights and image credits (#1730); accessible tab/keyboard/touch/no-JS/reduced-motion/zoom and independent WCAG 2.2 AA with axe; Safari if available; measured Lighthouse/CWV; actual HTTP CSP; CI/QD at exact head; founder visual and production release approval. No WordPress.com native staging clone exists on the Personal plan. Playground does not certify WordPress.com host-specific behavior.

## Commercial contract
OFFER = free 52-page Seven Day Focus Fieldbook. FUNNEL = qualified Grok campaign entry → relevant historic evidence → unobstructed Focus CTA → verified lead → verified paid order/affiliate conversion → refunds/fees → realized net revenue.
BLOCKER = whole-page replacement could remove existing native Jetpack and 72 records; actual Jetpack self-link needs hosted verification.
CHANGE = safe, reproducible single-block offline draft composer.
EVIDENCE = live read-only Page 6 splice + passing local negative controls + synthetic Chromium.
OWNER = interim homepage engineer (this PR), Claude (production integration/attribution), Grok and Praxxis (TASK-008), founder (release).
BUSINESS RESULT = zero new verified subscribers/orders/revenue attributable to this engineering run.

**RELEASE HOLD. No merge, deployment, CMS/theme/settings/navigation write, plugin install, subscriber action, email, paid service, affiliate activation, tracking change or social post.**
