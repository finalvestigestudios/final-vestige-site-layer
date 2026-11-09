# Preparedness R234 — Auxiliary Draft Card and Conversion Exposure Gate (2026-11-08 PT)

**Owners:** Issue #136, conversion issue #820, charter #818. **Release:** BUILT / 70 isolated synthetic tests PASS / native corpus and build NOT EXECUTED / DRAFT_HARD_HOLD. Not a QD PASS, human editorial review, source substantiation, medical/food/water safety approval, public release, checkout authorization, or proof of paid revenue.

## Why R232/R233 did not solve this

R232 verifies that landing and hub HTML exactly matches an authenticated producer; R233 freezes the optional editorial hub source bytes and directory membership. Neither independently asserts the user-visible semantics of a *generated card* on the auxiliary pages. In particular, a future reviewed generator/input change could introduce a route mismatch, concealed card, purported verified badge or outbound merchant/data-collection link while keeping renderer/source/output identities mutually consistent. R234 adds a **separate fail-closed behavioral contract**, not a claim that tampering was observed.

The authenticated producer currently generates all 41 article/tool cards on the landing and repeats each card once in its own populated section hub, in two draft channels. R234 requires:

1. Exactly 41 distinct canonical Preparedness routes, with source-controlled card title, section and track.
2. Exactly one card per expected route on landing, and exactly the section-specific cards on each populated hub, in WordPress and preview HTML. No duplicate/foreign routes, missing titles or altered card provenance.
3. Every card has one visible Draft badge, data-verify=pending and exactly one title link inside its h3. No hidden card, hidden title link, hidden Draft badge, purported QD verification or unintended published state.
4. Preview pages must carry robots=noindex. Auxiliary links remain internal or fragment-only; new outbound merchant/affiliate links and external scripts, embedded third-party frames, active forms and duplicate attributes fail until separately reviewed and deliberately reauthorized.
5. The already pinned R230 tokenizer-state validator runs before interpreting auxiliary markup. R234 itself is loaded from exact committed Git source bytes through the R220 loader, with a post-render pin check. R232 strict filename inventory and exact HTML replay remain required.

## Actual verification

Executed locally, with no repository or CMS writes:

python -I -m unittest discover -s /mnt/data/fv_r234/preparedness/tests -p 'test_r234*.py' -v → **70 tests PASS**.

python -m py_compile .../r234_auxiliary_draft_exposure_hold.py → **PASS**.

Matched executed files against committed Git blobs:
- Module: 316e5463cd41a067b6503fe7de115e1a1110d345
- Test: 5ea1fb913872f54b934bba47d86d6c825775b7e3

Tests include a synthetic 41-card/3-populated-hub × 2-channel replay (164 card instances over 8 surfaces), 41 independently mutated canonical hrefs, preview indexing, duplicate cards, invisible safety labeling, missing/false Draft badges, source title/track drift, off-site merchant and affiliate anchors, external scripts, embedded frames, unsafe forms and fail-closed status controls. Fixtures are synthetic, not authentic 35-article material.

**NOT EXECUTED:** trusted native repository checkout, real validate.py, real build.py, inherited full Python test suite, R220 native invocation, real WordPress and preview exports, actual browser/mobile accessibility or independent editorial/qualified safety/QD review. Container git ls-remote cannot resolve github.com. GitHub connector source reads/writes do **not** constitute native execution. Repository remains not production-ready.

## Coordination and immutable inputs

All seven Claude branch HEADs still match frozen R200 manifest — start 2122d856fce9f64887c16df3d52e64be9f59a55b, shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976, food f911ff7a655de8d81535ea86ec3d65a49ee76648, health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17, hist-field 4e5caf812727953aa45e3bda2d382f2c67b6a09c, hist-food 67e116e536c7410bed30f8f3b1bb8c166f3c223d, hist-home 7504a5f099594d635e3dd7332a33a2e1346c43a2.

Independent review #157 draft HEAD 7d1ae6b8ef93d10cfb6810987672360885e9c1aa and test-isolation #169 draft HEAD e9cd7766dac59d47ab467d8945269b9146c2aef5 remain unmerged. Homepage owner #1689 draft HEAD f55c36b6598eec558dd8bb24e4c8988becc51be0 untouched. This PR stacks only on R233.

Independent source review remains held: two CDC source-use occurrences in Article #7, one Ready.gov in Article #20, seven historical source-ID conflicts, and safety language involving powered medical devices and utility restoration. R234 does not alter articles, tools, taxonomy, citations, source register, source crosswalk or human-review statuses.

## ONE high-intent social-to-free-resource pathway (TASK-008, not a new Grok assignment)

**Audience:** households without a designated out-of-area emergency contact or documented location of essential papers. **Existing public free destination:** https://finalvestige.com/preparedness/ → Practical resources for households today → Create a household emergency plan, with linked official Ready.gov/FEMA checklist. Public page is separate from **unpublished** original 35 long-form guides.

**Optional currently listed candidate:** https://payhip.com/b/n1RhV (Legacy Triage, publicly listed at $19, 580 KB PDF, Vested Wisdom storefront). It focuses on estate/incapacity and account access, **not an authenticated disaster-preparedness product**. Listing does not establish owner authorization, audience fit, credentials privacy, transaction acceptance, delivery, refunds or confirmed orders. **No paid Preparedness CTA approved.** No unapproved substitute toolkit or retired water offer.

**Draft free CTA, held:** “Choose one out-of-area contact and write down where the household can find its essential documents. Use the free official emergency-planning checklist to start.” No email gate. No product pitch while suitability and checkout remain unverified.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Grok existing post → public free planning resource | No authenticated asset ID / post URL / published date / rights / mobile destination | TASK-008 crosswalk an **already published** video, exact hook and destination | UNVERIFIED; no traffic attribution | Grok / Praxxis |
| Public resource → original 35 guides and six tools | Native build, citations and qualified safety approvals absent | Full native validator, human review, preserve depth/routes | HARD HOLD; R234 synthetic only | Preparedness / Independent QA |
| Free planning → optional Legacy Triage | Audience mismatch risk; ownership/rights/privacy unverified | PDF audit, merchant authorization; optional disclosed placement only if accepted | NOT APPROVED | Founder / Commerce |
| Product → checkout → delivery | Authorized transaction, fulfillment/refunds unverified | Consent-based end-to-end merchant test only after authorization | NOT TESTED | Commerce |
| Qualified sessions → net paid sales | No matched creator asset, real sessions, orders, fees/refunds | 7/30-day cohort: session→CTA→lead→paid order→fees/refunds→net | NOT COMPUTABLE net/1,000 human sessions | Analytics / Commerce |

Nothing was merged, published, purchased, emailed, posted or changed in WordPress, navigation, homepage, merchant, affiliate, creator queue or analytics. Founder approval and independent source/safety review remain mandatory.

## Required complete-checkout commands and gates

python -I preparedness/tools/validate.py

python -I preparedness/tools/build.py

python -I -m unittest discover -s preparedness/tests -v

python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness

Then compare 35 bodies/metadata with contributor heads and integrated exceptions, all 41 routes and six tools, all 82 article/tool outputs plus landing/hubs across both modes, source-use conflicts, reader-visible warnings and mobile behavior. Independently review official-source claims/high-consequence advice before QD/release. **HARD HOLD regardless of machine test outcome.**
