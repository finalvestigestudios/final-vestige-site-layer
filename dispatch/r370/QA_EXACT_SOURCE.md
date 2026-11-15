# R370 independent readback and exact-source QA

**Review artifact head before this record:** 7165a6ab998e0b0dfc50b08ef51a8c3664b8ca19 (stacked on parent PR #2564 at 18805745f7edb52ef5331a570cc393a4bf9bafda).

At that commit, all **7 source files** were separately fetched from GitHub by exact SHA and their Git blob IDs recorded:

| File | Git blob SHA |
|---|---|
| ISSUE03_OPTIONAL.md | b3eae08610cc08f4acaa1cb8fde6d84c0a8b8f91 |
| ISSUE03_OPTIONAL.txt | 0cfa95cafe71e9fec7edfa0cbf86a1c4fe0529f9 |
| ISSUE03_OPTIONAL.html | 663ed09e93c2e867f8ddeda0d7f5fe85312458e9 |
| ZEN12_CLAIM_RIGHTS_PRICE_CROSSWALK.md | dccb26e93ef67403683439f1a53c5aac30b519d4 |
| ONE_OFFER_CONSENT_TO_NET_REVENUE.md | cb8eb2a5540c34c9a488877bc1bcbdd780ac1692 |
| R370_RELEASE_NOTE.md | 615f9ff3d5a006645c82065dc9f140d2259a8044 |
| R370_EVIDENCE_REGISTER.json | 509474c4b3e5d8dae7ae3324e472720f04dec12a |

**Executed against those exact GitHub-returned bytes:** 31/31 independent V8 assertions passed. Coverage: subject/preheader parity across three formats, merchant CTA deliberately inactive (seller citations remain valid source links), remaining legal placeholders, one CTA token, honest advertising disclosure, primary historical and research links, no fabricated price in issue copy, accessible semantic basics (lang/viewport/H1), table-based static HTML without scripts/forms/images/remote pixels, no secrets or subscriber identities, publisher/partner/send flags false, and consent/paid-only revenue definitions.

A separate **4/4 adversarial mutation check** correctly rejected removal of postal placeholder, removal of unsubscribe placeholder, removal of NOT ADOPTED marker, and insertion of executable script. These are **static checks**, not real native Jetpack output, inbox receipt, working unsubscribe, browser WCAG screen-reader inspection or email-client testing.

The original PR #175 was separately revalidated against its nine GitHub blob identities at exact SHA d57ccdba3aee8f065e143e101c2945f4f3d01647 using locally preserved byte-identical source. Its six original native Python unittest cases were actually executed here: **6/6 PASS**.

**Observed live provider read-only:** 2026-11-15 04:31 UTC, newsletter true, send technically available, automatic posts-to-email OFF, full format, welcome configured; total3/confirmed3/unconfirmed2, last five post notifications NEVER SENT. No unique eligible inbox count, live receive/footer proof or merchant rights. WordPress support says pending/unconfirmed not counted in total.

**Release:** all six originals HOLD_UNSENT, 03/05 HOLD_MERCHANT; new alternate 03 NOT_ADOPTED. No emails or test emails sent, no WP changes, no affiliate activations, no social content, no merges, no paid expenses or real sales claimed. Actual net revenue per 1,000 qualified human sessions remains NOT COMPUTABLE. Next true blockers are named EMAIL SKU rights, live approved guide, recipient status, real welcome/PDF, genuine native render, publisher mailing address and unsubscribe.
