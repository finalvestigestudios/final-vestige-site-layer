# R307 · Preparedness source/citation custody, not release approval

**Status: DRAFT / HARD HOLD / NO PUBLICATION** · 2026-11-11 America/Los_Angeles (2026-11-12 UTC). Owner lane: Preparedness Archive integration safety gate only; Issues [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136) and [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

## Two bounded engineering corrections

1. **Real R305 bug, identified by independent Praxxis inspection:** Same-document `href="#family%2Dcontact"` was incorrectly checked against the literal HTML ID `family%2Dcontact`, falsely flagging a valid `id="family-contact"` link as missing. R307 adds strict UTF-8 URI-percent decoding for fragment targets *only* (not HTML IDs), fails closed on malformed %-escapes, invalid UTF-8 or decoded controls, and preserves literal ID case sensitivity. R306's immediate predecessor Git-blob SHA is re-pinned to the changed R305 implementation. The HTML5 non-void, unsafe URL and active-content gates are otherwise retained. This does **not** verify that external URLs or emergency guidance are safe.
2. **Real R306 provenance-flag gap, identified by independent Praxxis inspection:** The old validator required four `line_endings_only_observed` flags but did not bind each flag to the correct frozen/integrated byte pair. The R307 read-only validator now binds exactly four original article slugs to their frozen and integrated Git blob IDs, LF-normalized SHA-256 digests, normalized byte lengths, and independently observed frozen CRLF counts. Moving a flag between rows, changing an OID, mutating local content, substituting a symlink or asserting false publication/QD approval fails closed. The 35/70 source inventory and 14 body / 12 metadata differences remain a hard hold.

## Independently inspected exact GitHub blobs (UTC 2026-11-12)

The actual source contents were retrieved from GitHub by **both** frozen and integrated blob SHAs, and comparison after *only* `\r\n -> \n` returned exact equality for each:

| Article | Frozen Git blob | Integrated Git blob | Frozen CRLF | LF normalized bytes | SHA-256 of both normalized byte streams |
|---|---|---|---:|---:|---|
| root-cellars-cool-storage | `7f375c32d74f2828b4912f5692abc44483e4629a` | `2ff8d029769aa9a97de6b1e388d937899f3af38c` | 102 | 21,281 | `0f2d1992fc9915218fb64d14479fdc178cd18f47001dc5cad497e18dfaf3a45f` |
| navigation-before-gps | `49beb68339a6b85b07d686c0cfb9fe1d88b8de4f` | `3c02e58c30d1d608224944142f31fbead44a1252` | 100 | 21,752 | `1bb5f1b6213cc21d267731ac21a3a025e9bd0dde42c650d917b415606ddad2f4` |
| sanitation-before-germ-theory | `02090fc1b773fd79f08a7ba754b6125844c37eab` | `d56df76647d2598f35cfd4609f91649cef063f12` | 102 | 21,947 | `404e6fa663e0848fa78b059afeea6c8110d898a8f6aec32528d20458deb11d05` |
| pioneer-supply-chains-failed | `3643c50b43ca7ba6c1d9bc439e7c78730503b80f` | `ad158ee898f76d05bcb65c845b1e4a0e8103c660` | 113 | 24,803 | `d2131798ade5ae3250fe0e74fdf3d5af95368a3266f1315a927b8ee85a71b529` |

All four original and integrated text comparisons return identical after CRLF normalization. This does **not** adjudicate separate metadata changes (notably pioneer-supply-chains-failed).

## Scope and test evidence / limitations

- Local prototype test harness **1061/1061 PASS** (903 R295–R305 + 75 R306 + 83 exploratory R307); compilation PASS. This local build was reconstructed from prior downloadable test artifacts, not authenticated from the latest full repository. **Do not label that result the committed R307 branch's exact-blob suite.**
- The exact R307 GitHub branch now includes the bounded R305/R306 changes, the immutable-boundary validator and synthetic regression tests. **Full exact-branch Python suite, native validation/build and the actual 41 WordPress draft exports remain UNEXECUTED/UNVERIFIED** because the working container cannot resolve `github.com` for a complete trusted checkout. GitHub connector file/branch/blob reads are source evidence, not native runtime execution.
- Independent QA [PR #157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157) remains open/draft (HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`); synthetic-fixture [PR #169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) remains open/draft (HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`). #169 still writes `_dup_test.json` into the authentic source directory. Independently isolate it; do not edit another agent's PR.
- Latest inspected homepage lead [PR #1689](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1689) (HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`) is not modified.
- 7/7 Claude cluster branches independently compared **identical** to their respective authentic frozen R200 commits (0 ahead, 0 behind). The article-body changes are *integrated-lineage distinctions*, not contributor branch drift.
- **Ten substantive body revisions, twelve metadata differences, historical jerky citation scope, Article #7 hazardous-water guidance, Article #15 and Tool #104 emergency messaging, child privacy, printing, no-JS/accessibility all remain independent qualified-review HARD HOLDS.** No false QD PASS, no medical or emergency-safety approval.

## Conversion-first handoff, one audience only

**Audience:** households seeking a reliable family communication and reunification planning resource. **Existing free entry:** https://finalvestige.com/preparedness/ . Candidate draft CTA: *“Make a plan for how your household will reconnect. Start with free preparedness resources.”* This is not a published campaign.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE / OWNER |
|---|---|---|---|
| Existing social family-contact asset → free resource | No authenticated matching `asset_id` and verified mobile destination | Grok/Praxxis confirm existing posted asset, permitted destination, 360px/390px experience | **NOT VERIFIED** · Grok/Praxxis TASK-008 |
| Free guide → Tool #104 | Emergency-source, privacy, no-JS/print and child-data wording held | Independent qualified review; real browser no-JS/print checks | **HARD HOLD** · Preparedness QA |
| Free guide → optional **paid** pack | No verified FV-owned/licensed currently purchasable Preparedness SKU | Founder/Commerce establish rights, active merchant, refund/support, correct delivery; only then draft paid CTA and run test purchase with approval | **NO APPROVED SKU** · Founder/Commerce |
| Unique `asset_id` qualified sessions → relevant CTA → confirmed lead → verified paid order → refunds/fees → net revenue | Transactions/attribution not authenticated | Claude/Commerce reconcile 7/30-day cohorts; consent and existing measurement only | **NOT COMPUTABLE** · Claude/Commerce |

KPI: realized **net revenue per 1,000 qualified human sessions**. Never treat outbound affiliate clicks, checkout starts or unconfirmed subscribers as paid sales. Do not restore retired water freebies or sell Legacy Triage without rights/fit/delivery proof.

**Release state:** OPEN / DRAFT / HARD HOLD. No merge, public publishing, CMS, navigation, analytics script, merchant activation, email, social posting, paid API or spending change. Founder retains release approval.
