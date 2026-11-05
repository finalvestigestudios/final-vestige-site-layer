# R136 — Custody-bound human-review notes: DRAFT / HOLD

Scope: Preparedness #136; business source-of-truth #820 and #818. Stacked on R135 PR #1037 at 072768f207847989c69b10770d83e4e533ce9ba3, above R134 #1031, R133 #1025, R132 #1012 and frozen 35-article RC #584. No releases, mergers, article changes, CMS writes, or public approval.

## Engineering delivered

New read-only Python tool: preparedness/tools/r136_human_review_ledger.py; adversarial tests: preparedness/tests/test_r136_human_review_ledger.py. The CLI first regenerates the R135 human queue through the R134 reviewer packet and R133 80-blob custody gate, then creates an unsigned local reviewer-note template. It checks exactly 35 draft articles, the 2,000-citation historical baseline, 32 pending shared-source groups, all passage witness IDs, and the exact SHA-256 digest of the parent queue. Review sheets cannot omit, duplicate, invent, or reassign tasks, or be reused on a changed queue.

Only OPEN, EVIDENCE_LOGGED_NOT_APPROVED, NEEDS_CORRECTION or INSUFFICIENT_EVIDENCE are accepted. Non-open records must include reviewer reference, UTC date, HTTPS evidence URL, source passage and reading-scope explanation. Medical or carbon monoxide/power/fire passages require a separate specialist-review reference; correction claims require a specific proposed correction. The script only validates presence and syntax; it does not verify a reviewer, confirm an authority, judge safety, or constitute qualified adjudication. Outputs ALWAYS HOLD, with may_publish, medical_safety_verified, qd_pass and merchant_offer_verified false.

## Commands (on complete authenticated repository checkout only)

python -I preparedness/tools/r133_snapshot_gate.py
python -I preparedness/tools/r134_reviewer_packet.py > /tmp/fv-r134-private.json
python -I preparedness/tools/r135_review_queue.py > /tmp/fv-r135-private.json
python -I preparedness/tools/r136_human_review_ledger.py > /tmp/fv-r136-private-blank-review.json
python -I preparedness/tools/r136_human_review_ledger.py --review-records /tmp/fv-r136-review-notes.json > /tmp/fv-r136-hold-audit.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -p 'test_*.py'

Feed only the template object from the blank review output as --review-records after private human editing. Do not commit review sheets or treat an unsigned note as source/medical/QD approval. All commands are read-only except the existing offline draft builder, which must remain off-production.

## Actual testing and blocked gates

86/86 locally executed synthetic/adversarial Python tests PASS under python -I; py_compile PASS. Local tests used a test-only stand-in for R135 fingerprint/ReviewHold imports; that stand-in is not committed. Both committed files are byte-for-byte identical to the locally tested files by Git blob SHA. This does NOT constitute a real archive run: full checkout DNS resolution fails, so complete R133-R136 35-article execution, native validator/build, entire regression suite, CI integrity, independent QD and browser QA remain NOT VERIFIED. There are no new human source or medical approvals.

## Unresolved evidence, exactly retained

Seven Claude heads checked via GitHub branch API on Nov 4 PT: Start 2122d856fce9f64887c16df3d52e64be9f59a55b; Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; Food f911ff7a655de8d81535ea86ec3d65a49ee76648 (diverged); Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; Historical Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; Historical Home 7504a5f099594d635e3dd7332a33a2e1346c43a2; Historical Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c.

QA #157 (7d1ae6b8ef93d10cfb6810987672360885e9c1aa) retains unresolved electrical-drill and refrigerated-medication wording; qualified reviewers must decide. QA #169 (e9cd7766dac59d47ab467d8945269b9146c2aef5) still has a shared-directory test fixture mutation, fixed only separately in draft #973. Historical Food eight NCHFP jerky citation ID retargets (S-7) remain excluded; three different author source interpretations remain under R132 pending review. Homepage #49 10495883299d53596992c26a8987f629b2904670 and flagship #604 bdf01b4a3e13fd6179ae9e847c9d4429bbe16176 untouched.

## ONE Preparedness topic and conversion-first staging plan

High-intent creator topic: family emergency communications, school pickup authority and reunification. Proposed existing free article: Household Emergency Plan, still DRAFT/HOLD, not a live approved destination. Proposed optional free printable: existing family-reunification tool, DRAFT/QA NOT TESTED. Proposed draft CTA: Make your family's contact and reunification plan. Read the free Household Emergency Plan, then use the optional printable to rehearse contacts and pickup arrangements. No promise of guaranteed safety, paywall, new lead magnet or retired water freebie.

ONE paid Preparedness toolkit must be an ALREADY purchasable rights-cleared SKU; no authentic matching product, merchant checkout, delivery, refund terms or price has been independently verified. Therefore NO paid button, new SKU, merchant URL, price or commercial claim is authorized. The #818 charter's Products 001-015 must be checked by Growth/Claude for audience fit without assuming a Preparedness pack exists.

Offer → step → blocker → change → evidence → owner:
1. Paid pack → confirmed paid order → rights/merchant/fulfillment unverified → inspect actual current product, checkout, refund and delivery → UNVERIFIED/HOLD → Growth/Claude.
2. Household Emergency Plan → guide reading → source/safety/QD incomplete → qualified R135/R136 adjudication plus 360/390/768/1440 accessibility QA → DRAFT/HOLD → Preparedness/QA.
3. Grok source asset → landing → actual Preparedness asset_id and destination absent in TASK-008 → obtain published post URL, destination, permitted bio/caption link mapping from Grok/Praxxis → UNVERIFIED → Grok/Praxxis.
4. Guide → optional printable → download, print, privacy and accessible link not tested → staged mobile/print QA → NOT TESTED → Site QA.
5. Purchase → net revenue/1000 qualified sessions → no merchant-confirmed orders/refunds/fees or attributed qualified-session denominator → reconcile only real first-party events with Grok asset_id and UTMs over 7/30 days → N/A → Growth/Claude.

Acceptance checks before any proposed release: actual social asset URL, authorized UTM destination, intent congruence, no duplicate analytics, existing confirmed-lead flow consent, meaningful CTA and disclosures, staged mobile click-path and printable delivery, verified merchant acceptance where relevant, independently confirmed paid orders minus fees/refunds. Never equate sessions, video views, outbound links, checkout starts or email signups with paid sales. Claude retains production engineering; Grok production/posting; Praxxis QA; founder release and spending approval. The full 35 instructional articles remain unpublished by this lane.