# Preparedness R206 — 35-route WordPress collision custody | DRAFT / HARD HOLD

Scope: issue #136 only; cross-reference business #820 and charter #818. This review-only branch stacks on R205 #1508, exact parent a0b38990d6922df460ab9ec7e05820ada29e5f33. No existing contributor articles, metadata, source registers, canonical routes, exports, site/CMS, homepage, tracking, commerce or social assets altered.

## Engineering delivered

The earlier source-custody gates protect the frozen 35 article routes and Git identities, but do not compare those planned paths to concurrent WordPress pages/posts. A separate, legitimate Preparedness draft is currently being edited by another agent. Added Python **tools/r206_wp_route_collision_gate.py**, a fail-closed offline preflight that consumes the exact R200 manifest (Git blob 5822f9dfde21d1f3bdfc26658769d852c639438c) and a separately acquired complete and dated read-only WordPress page/post snapshot. It reconstructs page parent paths, keeps WP draft preview links separate from public URLs, detects exact planned-route collisions and same-slug risks, rejects missing parents, cycles, duplicate published URLs, incomplete inventory, foreign host links, unsupported publication/safety approvals, altered 35-article census, incorrect branch ownership and malformed identities. It never generates release approval. A structural result remains DRAFT_HARD_HOLD/exit 2; corrupt/missing input returns INVALID_HARD_HOLD/exit 3. Claims of snapshot completeness in a submitted JSON file require independent API pagination inspection; the JSON alone is not authenticated evidence.

## Genuine WordPress observation, read-only, 2026-11-07 PT

Connected WordPress pages-list status=any returned **109 pages across two complete pages** (90 published, 19 draft). Posts-list status=any returned **81 posts across one page** (66 published, 15 draft). Independently reconstructed page paths from all 109 parent relationships and compared 81 post links against R200's 35 canonical routes: **0 exact route collisions; 0 same-slug matches; 0 missing page-parent references** at this observation. The live Archive is page **1868**, published at https://finalvestige.com/preparedness/ , modified 2026-11-04T17:32:05. The separate Household Records Map **2150** is still a draft, parent 1868, modified 2026-11-07T17:32:01, inferred prospective path /preparedness/household-records-map/ which does **not** overlap the frozen 35. Its ?page_id=2150 preview is **not** a verified public destination. Real observations are from a read-only connector inventory comparison; an authentic 190-row export was NOT run through the Python CLI. Route changes, plugin rewrites or redirects could invalidate the observation; re-fetch before release.

## Exact-code verification

**98/98 Python synthetic unittest PASS**, including 35 individual published-URL collision mutants, 35 manifest-route corruption mutants, nested WP draft collisions, missing parents/cycles, inconsistent archive status, incomplete pagination, foreign origins, unsafe preview links, duplicate published URLs, false QD/publishing flags, and invalid missing-checkout CLI exit 3. Python compilation PASS.

Executed code Git blob = committed GitHub blob: source **a737ce1716720cca3df95be6565ebf162f33bdca**; test **eb8c7020938e008ab2b1008d8b046ef484452d84**. This is **SYNTHETICALLY TESTED**, not native validation of the original full repo. Original git checkout via terminal still fails with "Could not resolve host: github.com". Therefore native preparedness/tools/validate.py, build.py, complete repository test suite, the authentic 35-article source crosswalk, 41 WordPress-ready exports, real-browser/print/keyboard accessibility, safety and independent QD remain NOT EXECUTED.

Once the trusted full checkout and reviewed complete fresh WordPress snapshot exist, run:
    python -I preparedness/tools/r206_wp_route_collision_gate.py --manifest preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json --snapshot /path/to/fresh-wp-snapshot.json --report /tmp/fv-r206.json
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
Exit 2 means structural hard hold, not approval; exit 3 means invalid hard hold.

## Exact ref coordination and remaining source blockers

Current original Claude branches, exact GitHub heads, still agree with R205: start 2122d856fce9f64887c16df3d52e64be9f59a55b; shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; food f911ff7a655de8d81535ea86ec3d65a49ee76648; health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; historical-field 4e5caf812727953aa45e3bda2d382f2c67b6a09c; historical-food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; historical-home 7504a5f099594d635e3dd7332a33a2e1346c43a2. Independent safety PR #157 = 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; synthetic-fixture PR #169 = e9cd7766dac59d47ab467d8945269b9146c2aef5; follow-up #973 = 4d40996a559b0124d74a9bb3bdcd481ad1992aa8; latest inspected home #1507 = afd41827b2e7a5f1139d0fc03a7ece0016c9d3d7. All untouched and separate.

R205 three original source-use explanation holes remain **unreviewed**: homemade-water-filters / cdc-find-clean-water twice; preparedness-real-households / start-ready-plan once. Seven historical multi-origin source collisions including jerky remain unadjudicated. PR #157 electrical drill and refrigerated medicine corrections are review requirements, not integrated/approved source or medical-safety judgments.

## OFFER → FUNNEL → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| OFFER / STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE / OWNER |
|---|---|---|---|
| Existing public Preparedness gateway → free orientation | Original Household Emergency Plan is unpublished and held | Preserve free no-signup guidance; stage source-reviewed article before any link | Page 1868 is live; original guide NOT live / Preparedness QA |
| Grok evacuation-records social asset → Archive | No matching approved published asset_id and destination in TASK-008 | Reconcile with Grok/Praxxis without touching queue | UNVERIFIED / Grok and Praxxis |
| Free guide → optional Family Reunification Card | Card safety, child privacy, keyboard, print, 360/390/768/1440 acceptance not established | Synthetic-only staged QA; avoid collection of personal data | HARD HOLD / QA |
| Free guide → optional Legacy Triage pack | Product rights, owned SKU, fit, real price, checkout, delivery and refunds not authenticated | Founder/Commerce confirm active purchasable rights-cleared product before drafting enabled paid CTA | NO APPROVED PAID OFFER / Founder-Commerce |
| Qualified sessions → CTA → confirmed lead → paid merchant order → fees/refunds → net revenue | No trustworthy relevant asset IDs, qualified denominator, confirmed orders or refunds | Use only approved existing attribution; 7/30 day cohorts with tiny-sample warnings | NOT COMPUTABLE / Analytics-Commerce |

Draft text only: **Explore the free Preparedness Archive. Essential guidance remains accessible without a signup.** Do not link Grok posts to unpublished original guides or private drafts, introduce retired water lead magnet, create product, add tracking or claim paid conversions. The Focus Fieldbook remains the separately approved lead magnet, not a new Preparedness freebie.

**BUILT / 98 SYNTHETIC TESTS / READ-ONLY WP INVENTORY OBSERVED / NATIVE BUILD NOT RUN / DRAFT HARD HOLD / NOTHING MERGED OR PUBLISHED.**
