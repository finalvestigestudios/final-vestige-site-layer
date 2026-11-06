# R167 — Family Reunification Card PDF-output privacy gate (DRAFT / HARD HOLD)

**Owner:** Preparedness Archive integration and source/citation safety, Issue #136; business coordination #820 / #818 / Grok-Praxxis TASK-008.  
**Exact parent:** R166 draft PR #1246, SHA bafbbf2ae0c4e06e3d44e32257abb8f5e41ddebe.  
**Scope:** Three additive draft review/tool/test files. No original articles, source registers, metadata, taxonomy, 35-article routing, staged Family Card, website, merchant, analytics or creator-queue changes.

## Why this work is nonredundant

R166 tests Chromium DOM print-media behavior but **never checks text in the actual PDF**. R167 renders real headless Chromium PDFs at 360, 390, 768 and 1440 pixels, then uses PyMuPDF to examine actual print output in memory:

1. Full card prints explicitly entered fictional contact and school information.
2. Four-copy minimal card keeps fictional emergency contact but omits school, caregiver, alternate meeting place and special-access sentinel values.
3. PDF generated after clearing all 13 original fields contains no fictional contact or private sentinel values.
4. External requests, WebSockets, page errors, fictional-input console logging, cookies, local/session storage, IndexedDB and CacheStorage cause a fail-closed result if detected.
5. Authentic execution first requires the R166 -> R165 -> R164 -> R163 -> R162 -> R161 -> R160 frozen source/citation chain, pinned JS and original draft HTML.

PDF bytes and synthetic input are not retained in the repository or report. Only aggregate test outcomes are recorded. This does not prove how WordPress plugins, extensions, user devices, physical printers, OS queues, or real user data behave.

## Full-checkout commands

Requires Python 3, Playwright, Chromium and PyMuPDF:

    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
    python -I preparedness/tools/r166_family_browser_probe.py --repo . --report /tmp/r166.json
    python -I preparedness/tools/r167_print_pdf_privacy_gate.py --repo . --report /tmp/r167.json

The last two commands intentionally return exit code 2 even for a structurally passing *draft hold*. Review their JSON states; **never** interpret a successful fixture preflight as publication permission.

**Local verification 2026-11-06 PT:** Python compilation PASS. R167 isolated tests **53/53 PASS**, including 42 named adversarial content/field mutations. Chromium actually generated and inspected **12 PDFs** on a fictional HTML fixture across the four viewport widths; negative tests demonstrated catches for minimal-card leak, print CSS, outbound fetch, and console input logging. Exact committed tool/test Git blob hashes match executed local bytes. Full private repository checkout unavailable because local GitHub DNS resolution fails: complete native validation/build, full 35-article suite, actual Family Card PDF probe, WordPress/device/OS spooler, independent source/safety/QD **NOT RUN / NOT VERIFIED**. Always DRAFT_HARD_HOLD or INVALID_HARD_HOLD; NEVER QD PASS.

## Seven current canonical Claude branch identities

A fresh 2026-11-06 GitHub compare against each previous verified SHA returned identical, 0 ahead/0 behind and no changed files.

| Cluster branch | Verified SHA |
|---|---|
| claude/prep-start-bbfeb8 | 2122d856fce9f64887c16df3d52e64be9f59a55b |
| claude/prep-food-ccdc55 | f911ff7a655de8d81535ea86ec3d65a49ee76648 |
| claude/prep-health-837444 | d5ef5bafd68361434dd1cc9209915b8e8a4eaf17 |
| claude/prep-shelter-5e1e0e | 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 |
| claude/prep-hist-food-b81f19 | 67e116e536c7410bed30f8f3b1bb8c166f3c223d |
| claude/prep-hist-home-0e0e38 | 7504a5f099594d635e3dd7332a33a2e1346c43a2 |
| claude/prep-hist-field-9db767 | 4e5caf812727953aa45e3bda2d382f2c67b6a09c |

Read-only inspected independent safety PR #157 at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa, synthetic test PR #169 at e9cd7766dac59d47ab467d8945269b9146c2aef5, correction PR #973 at 4d40996a559b0124d74a9bb3bdcd481ad1992aa8, home PR #49 at 10495883299d53596992c26a8987f629b2904670 and home PR #604 at bdf01b4a3e13fd6179ae9e847c9d4429bbe16176. Do not blindly replace later qualified draft safety wording with older patch text. Previously reported 75 outstanding source-review decisions, including 11 Family Card relationships and eight Historical Food substitutions, remain OPEN, not represented as adjudicated.

## Conversion-first — one audience, unverified paid step OFF

**Audience/intent:** family caregivers preparing school emergency pickup and reunification. **Free guide:** ungated Household Emergency Plan *after* independent source/safety review. **Optional free tool:** Family Reunification Card *after* privacy, citation and print approval. **Paid pack:** OFF until an existing Final Vestige-owned, rights-cleared, truly purchasable Preparedness SKU, merchant delivery/refund details, and mobile checkout acceptance are authenticated. Do not assume other public Payhip preparedness listings belong to FV; do not invent or publish a product, retire an offer, or resurrect water freebies.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing FV Preparedness pack → paid order | Current matching SKU, rights, fulfillment and refund proof missing | Read-only identify real existing product; merchant and staged checkout QA | HOLD, no authenticated paid purchase | Commerce / Claude |
| Household Emergency Plan → free guide reader | Qualified source, safety, QD and native build incomplete | Native validate/build, full regression, independent review | DRAFT/HOLD | Preparedness / QA |
| Free guide → free printable Card | Authentic PDF print, privacy, accessibility and sources unresolved | Execute R167 on trusted checkout; staged WordPress print/mobile review | 53 **fictional fixture** tests; real card NOT RUN | Preparedness / Site QA |
| Grok post → page | No authenticated Preparedness asset ID + destination | Confirm Grok/Praxxis TASK-008 inventory and platform-permitted link | UNVERIFIED, asset ID NULL | Grok / Praxxis |
| Qualified sessions → merchant-confirmed paid orders → net revenue | No verified sessions/order/fees/refunds | Existing consent-respecting measurement, 7/30-day cohorts, reconcile merchant | NOT COMPUTABLE | Commerce / Analytics |

**Draft CTA (not live):** “Build your household contact and school pickup plan — free guide, no signup required.” Landing acceptance: accurate creator-to-page topic; ungated safety steps, verified sources/review dates, accessible mobile CTA; optional clearly labeled practical card; no untested data storage assertions; working source-safe PDF; only verified existing offers with disclosed digital delivery/refunds, and founder release approval. Qualified-human sessions, CTA, confirmed leads, checkout and merchant-confirmed purchases must remain distinct. Never call outbound clicks sales, or claim net revenue per 1,000 sessions without both an actual numerator and denominator.

**Governance:** no merge, WordPress/CMS/navigation, publishing, social posts, email, merchant or affiliate activation, analytics scripts, paid tools, or spending; no independent QD PASS or claims that unreviewed emergency/medical advice is safe. All 35 articles remain DRAFT/HOLD.
