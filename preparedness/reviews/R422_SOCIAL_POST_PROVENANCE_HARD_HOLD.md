# R422 — Preparedness social-post provenance boundary (DRAFT / HARD HOLD)

**Scope:** `finalvestigestudios/final-vestige-site-layer` Preparedness Issue #136, commerce coordination #820 and founder business charter #818. Additive reviewer-only extension of R421 PR #2794 at parent `9cde3345e46b60b0a9a7063abd25139b82c9040a`. No publishing, CMS/navigation, social, merchant, email, analytics, product, original manuscript, source register or canonical routing changes.

## Demonstrated flaw and fix
R421 validates a proposed social post URL only as generic HTTPS, allowing a supposedly verified `youtube` campaign to provide an arbitrary unrelated HTTPS post URL. The resulting receipt can be `structural_integrity_ok=true` despite the post being hosted elsewhere. This is **a synthetic validation defect**, not evidence that such an FV campaign was posted.

R422 binds the **declared** platform to a conservative publisher host and stable-post permalink family:
- YouTube watch/shorts/live and youtu.be video; TikTok creator/video; Instagram reel/post; Facebook reel/watch/video.
- Rejects unrelated and lookalike hosts, cross-platform URLs, opaque redirect/share/profile routes, missing/duplicate video identifiers, dot/percent path routing ambiguity, embedded credentials, plain HTTP, suspicious redirect parameters.
- The older R421 source/guide/offer/UTM/7- and 30-day cohort gate runs first. R422 does **not** infer publication, content accuracy, media rights, signups or genuine orders from a post-shaped URL. All successful shapes retain independent-proof HOLDS.
- All outcomes, including self-attested merchant hashes, remain `DRAFT_HARD_HOLD`; eligible=false; QD=false; paid activation=false; orders and net revenue/1,000 qualified humans remain null.

**Synthetic reproduction:** `PROPOSED_MATCH` YouTube + `https://example.com/unrelated-page`: R421 structural PASS, R422 structural FAIL (`R422_SOCIAL_POST_PLATFORM_OR_PERMALINK_INVALID`). Genuine existing mobile URL or actual posts were **not** independently authenticated.

## Local tests and execution, not hosted proof
- Source/test blobs confirmed against GitHub branch and locally executed bytes by git hash.
- New 79 adversarial Python tests **PASS** with `python -I -m unittest discover -s preparedness/tests -p 'test_r422_social_provenance_gate.py' -q`.
- R421 74 and R420 58 tests independently **PASS**. Earlier R409–R416 eight modules: 570 tests **PASS** individually; total **781 passed across eleven completed module processes**, **not one combined run**. R417–R419 current inherited suite was **not completed**; R417 long test process interrupted, no result.
- Python compileall PASS; held fixture CLI intentionally exits 2 with a structural receipt and release HOLD.
- Native original 35-article validation/build and real WordPress/private paired exports **NOT EXECUTED**: no authenticated full source checkout. Synthetic tests do not approve content, claims or citations.
- CI job for R421 failed before readable runner steps (run 43970618662, job 133661506910); log endpoint returned 404 BlobNotFound. Do not assign cause or claim hosted pass. Inspect new R422 CI independently.

## Original source and independent QA custody
Read-only current snapshot of seven Claude cluster heads: food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historic field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historic food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historic home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; start `2122d856fce9f64887c16df3d52e64be9f59a55b`. Shelter continuation `ac8625faf30dd5538fadc31e06cb5a2cea1defae`; follow-up `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`. Snapshot via exact branch self-comparison; no contributor mutation. Independent draft QA #157, fixture #169 and dependent #2205, and homepage #1689 remain independent open workstreams; no code pulled from or written to those PRs.

The inherited graph count (35 slate entries, 203 source IDs, 280 occurrences, 17 URL review groups, 5 source disputes, 9 manuscript forks) is not re-attested by a full original corpus build in R422. The Article #11 NCHFP / CDC / USDA / Extension applicability and Article #15 / Tool #104 emergency and child-privacy concerns require qualified human review. No QD PASS.

## Conversion-first priority matrix
| Offer | Funnel step | Blocker | Proposed acceptance / experiment | Evidence now | Owner |
|---|---|---|---|---|---|
| ONE existing FV Preparedness owned pack, if authentic | practical pack → verified paid order | No authenticated FV seller, rights-cleared live SKU, checkout, fulfillment, refund and merchant receipt | Founder/commerce verifies seller record, actual authorized checkout and accessible product fulfillment before any paid CTA | HOLD; no paid product authenticated | Founder/Commerce |
| Already-posted on-topic family-reunification Grok asset | posted asset → existing free `/preparedness/` | No actual immutable post ID, rights/hook evidence or permitted working mobile URL | Praxxis independently inspects a genuinely posted matching post and exact link/asset_id/UTM; do not create social content | UNMATCHED; R422 only validates candidate URL shape | Grok/Praxxis |
| Existing public agency-linked free Archive → optional wallet card Tool #104 | guide → optional download | Tool #104 unpublished; emergency accuracy, child privacy, accessible print, provenance unreviewed | Human QD source-to-claim and offline/mobile check; essential safety information stays free | HARD HOLD | Preparedness/QD |
| Qualified-human sessions → confirmed orders → realized net revenue | event attribution and cohort | No consent-backed session denominator or independently reported order/fee/refund events | Reconcile 7/30-day receipts and qualified sessions without duplicate analytics scripts; use small-sample caveats | NOT COMPUTABLE | Claude analytics / Commerce |

**Draft free-only CTA:** “Start With Trusted Preparedness Resources,” proposed destination the existing `https://finalvestige.com/preparedness/`, but not authorized for a social asset until genuine post-topic-link verification. No retired water freebie, fabricated product, price, paid CTA, discount, lead count, sale or net revenue figure.

Founder owns releases, posting approvals and spending; Grok retains creator/posting; Praxxis independent source+social QA; Claude site/analytics. No live action permitted by this PR.
